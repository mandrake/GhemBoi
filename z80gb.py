import json
import struct

import gtk

w = gtk.Window()
w.set_default_size(200, 200)
w.connect('destroy', gtk.main_quit)

w.show()

class Z80sym(object):
    def __init__(self, cartridge, memsize = 0x10000):
        super(Z80sym, self).__setattr__('bind', super(Z80sym, self).__setattr__)
        self.bind('memory', [0x00] * 0x10000)
        self.bind('registers', {
            'A': 0x00,
            'B': 0x00,
            'C': 0x00,
            'D': 0x00,
            'E': 0x00,
            'F': 0x00,
            'H': 0x00,
            'L': 0x00,
            'PC': 0x0100,
            'IX': 0x0000,
            'IY': 0x0000,
            'SP': 0x0000,
            'I': 0x00,
            'R': 0x00
        })
        self.bind('running', True)
        self.bind('flags', {
            'zero': 0x80,
            'sign': 0x40,
            'half_carry': 0x20,
            'carry': 0x10
        })

        #self.memory = [0x00] * memsize
        self.memory[0x0000:0x4000] = cartridge[0x0000:0x4000]
        
        while self.running:
            try:
                self.decode()
            except Exception as e:
                #print self.memory
                print self.registers
                print e 
                self.running = False

    def __getattr__(self, n):     
        if n in ['A', 'B', 'C', 'D', 'E', 'F', 'H', 'L', 'PC', 'IX', 'IY', 'SP', 'I', 'R']:
            return self.registers[n]
        elif n == 'AF':
            return self.registers['A'] * 256 + self.registers['F']
        elif n == 'BC':
            return self.registers['B'] * 256 + self.registers['C']
        elif n == 'HL':
            return self.registers['H'] * 256 + self.registers['L']
        else:
            raise Exception('Roggan!')

    def __set__(self, x, y):
        pass

    def __setattr__(self, n, v):
        if n in ['A', 'B', 'C', 'D', 'E', 'F', 'H', 'L', 'PC', 'IX', 'IY', 'SP', 'I', 'R']:
            #XXX check ranges
            self.registers[n] = v
        elif n == 'AF':
            self.registers['A'] = v / 256
            self.registers['F'] = v % 256
        elif n == 'BC':
            self.registers['B'] = v / 256
            self.registers['C'] = v % 256
        elif n == 'HL':
            self.registers['H'] = v / 256
            self.registers['L'] = v % 256
        else:
            print n
            raise Exception('Roggan?')

    def read_inc_pc(self):
        x = self.memory[self.PC]
        self.PC += 0x0001
        return x

    def signedb(self, byte):
        if byte > 127:
            byte -= 256
        return byte

    def decode(self):
        b = self.read_inc_pc()

        if   b == 0x00:
            pass
        elif b == 0x01:
            self.C = self.read_inc_pc()
            self.B = self.read_inc_pc()
        elif b == 0x02:
            self.memory[self.BC] = self.A
        elif b == 0x03:
            self.inc('C')
            if self.registers['C'] == 0x100:
                self.registers['C'] = 0x00
                self.inc('B')
                if self.registers['B'] == 0x100:
                    self.registers['B'] = 0x00
        elif b == 0x04:
            self.inc('B')
        elif b == 0x0b:
            self.registers['C'] -= 1
            if self.registers['C'] == -1:
                self.registers['C'] = 0xff
                self.registers['B'] -= 1
                if self.registers['B'] == -1:
                    self.registers['B'] = 0xff
        elif b == 0x20:
            op = self.signedb(self.read_inc_pc())
            if not self.get_flag('zero'):
                self.jumprel(op)
                print self.registers['PC']
        elif b == 0x21:
            self.registers['L'] = self.read_inc_pc()
            self.registers['H'] = self.read_inc_pc()
        elif b == 0x23:
            self.registers['L'] += 1
            if self.registers['L'] == 0x100:
                self.registers['L'] = 0x00
                self.registers['H'] += 1
                if self.registers['H'] == 0x100:
                    self.registers['H'] = 0x00
        elif b == 0x28:
            op = self.signedb(self.read_inc_pc())
            self.jumprel(op)
        elif b == 0x31:
            self.registers['SP'] = self.read_inc_pc() + self.read_inc_pc() * 256
        elif b == 0x36:
            self.memory[self.registers['L'] + self.registers['H'] * 256] = self.read_inc_pc()
        elif b == 0x3e:
            self.registers['A'] = self.read_inc_pc()
        elif b == 0x78:
            self.registers['A'] = self.registers['B']
        elif b == 0xaf:
            self.registers['A'] = 0x00
            self.set_flag('zero')
        elif b == 0xb1:
            self.reset_flag('carry')
            self.reset_flag('sign')
            self.reset_flag('half_carry')
            if not (self.registers['A'] | self.registers['C']):
                self.set_flag('zero')
        elif b == 0xc3:
            op = self.read_inc_pc() + self.read_inc_pc() * 256
            self.jumpabs(op)
        elif b == 0xcd:
            op = self.read_inc_pc() + self.read_inc_pc() * 256
            self.push(self.registers['PC'])
            self.jumpabs(op)
        elif b == 0xe0:
            op = self.read_inc_pc()
            self.memory[op + 0xff00] = self.registers['A']
        elif b == 0xea:
            op = self.read_inc_pc() + self.read_inc_pc() * 256
            self.memory[op] = self.registers['A']
        elif b == 0xf0:
            self.registers['A'] = self.memory[self.read_inc_pc() + 0xff00]
        elif b == 0xf3:
            self.memory[0xffff] = 0x00
        elif b == 0xfe:
            op = self.read_inc_pc()
            a = self.registers['A']
            r = a-op
            if r < 0:
                self.set_flag('sign')
            elif r == 0:
                self.set_flag('zero')
        else:
            #raise Exception('OpCode %d not implemented yet' % b)
            print 'OpCode %x not implemented yet' % b
            print self.registers
            self.running = False

    def reset_flag(self, name):
        self.registers['F'] = self.registers['F'] | (255 - self.flags[name])

    def set_flag(self, name):
        self.registers['F'] = self.registers['F'] | self.flags[name]

    def get_flag(self, name):
        return (self.registers['F'] & self.flags[name]) != 0

    def push(self, op):
        self.memory[self.SP] = op
        self.SP += 1

    def inc(self, reg):
        self.setitem(self, reg, self.getitem(self, reg) + 1)

    def dec(self, reg):
        self.registers[reg] -= 1

    def sum(self, reg, op, optype):
        self.registers[reg] += op

    def jumprel(self, off):
        self.PC += off

    def jumpabs(self, addr):
        self.registers['PC'] = addr

class Z80instruction:
    def __init__(self, addr, instr, ops):
        self.addr = addr
        self.instr = instr
        self.ops = ops

    def __str__(self):
        #print self.instr, self.ops
        return "%08X: %s %s" % (self.addr, self.instr, ', '.join(map(str, self.ops)))

class Immb:
    def __init__(self, val):
        self.val = val

    def __int__(self):
        return self.val

    def __str__(self):
        return "%02Xh" % self.val

class Immw:
    def __init__(self, val):
        self.val = val

    def __int__(self):
        return self.val

    def __str__(self):
        return "%04Xh" % self.val

class Indb:
    def __init__(self, val):
        self.val = val

    def __int__(self):
        return self.val

    def __str__(self):
        return "(%02Xh)" % self.val

class Indw:
    def __init__(self, val):
        self.val = val

    def __int__(self):
        return self.val

    def __str__(self):
        return "(%04Xh)" % self.val

class Z80:
    ops = json.load(open('opcodes/z80gb.json'))

    @staticmethod
    def decodeStream(data, base):
        ret = []
        idx = 0
        base = int(base)
        while idx < len(data):
            tidx = idx
            key = ""
            ops = Z80.ops
            
            while (not ops.has_key(key)) and tidx < idx + 2 and tidx < len(data):
                key += "%02X" % data[tidx]
                tidx += 1

            if tidx == idx + 2 or (tidx == len(data) and not ops.has_key(key)):
                #print "Warning: this should never happen (%08X: %02Xh)" % (idx, data[idx])
                ret.append(Z80instruction(base+idx, 'nop', ["%02Xh" % data[idx]]))
                idx += 1
            else:
                instr = ops[key]['op']
                operands = list(ops[key]['operands'])
                params = []
                
                if ops[key].has_key('follows'):
                    for follow in ops[key]['follows']:
                        if follow == 'byte':
                            params.append(data[tidx])
                            tidx += 1
                        elif follow == 'word':
                            params.append(data[tidx] + data[tidx + 1] * 256)
                            tidx += 2
                        else:
                            raise Exception("Fuuuuuuuu")
                
                j = 0
                for i in range(0, len(operands)):
                    if operands[i] == 'byte':
                        operands[i] = Immb(params[j])
                    elif operands[i] == 'word':
                        operands[i] = Immw(params[j])
                    elif operands[i] == '(byte)':
                        operands[i] = Indb(params[j])
                    elif operands[i] == '(word)':
                        operands[i] = Indw(params[j])
                    else:
                        j -= 1
                    j += 1

                ret.append(Z80instruction(base+idx, instr, operands))
                found = True
                idx = tidx
            
        return ret

    @staticmethod
    def decodeStreamFile(data, path, base):
        f = open(path, 'w')
        r = Z80.decodeStream(data, base)
        for i in r:
            f.write(str(i) + "\n")
import json
import struct

import gtk

w = gtk.Window()
w.set_default_size(200, 200)
w.connect('destroy', gtk.main_quit)

w.show()

class Z80sym(object):
    x = open('opcodes/z80gb.json')
    def __init__(self, cartridge, memsize = 0x10000):
        super(Z80sym, self).__setattr__('bind', super(Z80sym, self).__setattr__)
        self.bind('ops', json.load(self.x))
        self.x.close()
        self.bind('cartridge', cartridge)
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
            'SP': 0x0000,
            'I': 0x00,
            'R': 0x00
        })
        self.bind('running', True)
        self.bind('flags', {
            'zero': 0x80,
            'subtraction': 0x40,
            'half_carry': 0x20,
            'carry': 0x10
        })

        self.memory[0x0000:0x4000] = cartridge[0x0000:0x4000]
        
        while self.running:
            try:
                o = 1
                s = ''
                
                b = '%02X' % self.memory[self.PC]
                s += self.ops[b]['op'] + ' '
                l = []
                for q in self.ops[b]['operands']:
                    if 'byte' in q:
                        l.append(q.replace('byte', '%02xh' % self.memory[self.PC + o]))
                        o += 1
                    elif 'word' in q:
                        l.append(q.replace('word', '%04xh' % (self.memory[self.PC + o] + self.memory[self.PC + o + 1] * 256)))
                        o += 2
                    else:
                        l.append(q)
                s += ', '.join(l)

                print '%20s (%s)\t' % (s, b),
                print self.registers
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
        elif n == 'DE':
            return self.registers['D'] * 256 + self.registers['E']
        elif n == 'HL':
            return self.registers['H'] * 256 + self.registers['L']
        else:
            print dir(super(Z80sym, self))
            return super(Z80sym, self).__getattribute__(n)

    def __setattr__(self, n, v):
        if n in ['A', 'B', 'C', 'D', 'E', 'F', 'H', 'L', 'PC', 'IX', 'IY', 'SP', 'I', 'R']:
            #XXX check ranges
            self.registers[n] = v
        elif n == 'AF':
            self.registers['A'] = v / 256
            self.registers['F'] = v % 256
        elif n == 'BC':
            print n, v
            self.registers['B'] = v / 256
            self.registers['C'] = v % 256
        elif n == 'DE':
            self.registers['D'] = v / 256
            self.registers['E'] = v % 256
        elif n == 'HL':
            self.registers['H'] = v / 256
            self.registers['L'] = v % 256
        else:
            print n
            super(Z80sym, self).__setattr__(n, v)

    def read_inc_pc(self, size = 0x0001):
        x = 0
        c = 0
        for i in range(0, size):
            x += self.memory[self.PC] * (256 ** c)
            c += 1
            self.PC += 1
        return x

    def signedb(self, byte):
        if byte > 127:
            byte -= 256
        return byte

    def decode(self):
        b = self.read_inc_pc()

        if   b == 0x00:         # nop
            pass
        elif b == 0x01:         # LD BC, d16
            self.BC = self.read_inc_pc(size=2)
        elif b == 0x02:         # LD (BC), A
            self.memory[self.BC] = self.A
        elif b == 0x03:         # INC BC
            self.inc('BC')
        elif b == 0x04:         # INC B
            self.inc('B')
        elif b == 0x05:         # DEC B
            self.dec('B')
        elif b == 0x06:         # LD B, d8
            self.B = self.read_inc_pc()
        elif b == 0x07:         # RLCA
            self.reset_flags('zero', 'half_carry', 'subtraction', 'carry')
            b7 = self.A & 0x80
            self.A &= 0x7f
            self.A *= 2
            if b7:
                self.A += 1
                self.set_flag('carry')
        elif b == 0x08:         # LD (a16), SP
            self.memory[self.read_inc_pc(2)] = self.SP
        elif b == 0x09:         # ADD HL, BC
            self.reset_flag('subtraction')
            if self.C == 0xff - self.L + 1:
                self.set_flag('half_carry')
            self.HL += self.BC
            if self.HL > 0x10000:
                self.HL -= 0x10000
                self.set_flag('carry')
        elif b == 0x0a:         # LD A, (BC)
            self.A = self.memory[self.BC]
        elif b == 0x0b:         # DEC BC
            self.dec('BC')
        elif b == 0x0c:         # INC C
            self.inc('C')
        elif b == 0x0d:         # DEC C
            self.dec('C')
        elif b == 0x0e:         # LD C, d8
            self.C = self.read_inc_pc()
        elif b == 0x0f:         # RRCA
            self.reset_flags('zero', 'half_carry', 'subtraction', 'carry')
            b0 = self.A & 0x01
            self.A /= 2
            if b0:
                self.A |= 0x80
                self.set_flag('carry')
        elif b == 0x10:         # STOP 0
            self.running = False
            if self.read_inc_pc() != 0:
                raise Exception('stoppewwronghe')
        elif b == 0x11:         # LD DE, b16
            self.DE = self.read_inc_pc(2)
        elif b == 0x12:         # LD (DE), A
            self.memory[self.DE] = self.A
        elif b == 0x13:         # INC DE
            self.inc('DE')
        elif b == 0x14:         # INC D
            self.inc('D')
        elif b == 0x15:         # DEC D
            self.dec('D')
        elif b == 0x16:         # LD D, d8
            self.D = self.read_inc_pc()
        elif b == 0x17:         # RLA
            self.reset_flags('zero', 'half_carry', 'subtraction', 'carry')
            b0 = self.A & 0x80
            self.A *= 2
            if self.get_flag('carry'):
                self.A += 1
            if b0:
                self.set_flag('carry')
        elif b == 0x18:         # JR d8
            #self.jumprel(self.signedb(self.read_inc_pc()))
            op = self.read_inc_pc()
            self.PC += op
        elif b == 0x19:         # ADD HL, DE
            self.reset_flag('subtraction')
            if self.E == 0xff - self.L + 1:
                self.set_flag('half_carry')
            self.HL += self.DE
            if self.HL > 0x100:
                self.HL -= 0x100
                self.set_flag('carry')
        elif b == 0x1a:         # LD A, (DE)
            self.A = self.memory[self.DE]
        elif b == 0x1b:         # DEC DE
            self.dec('DE')
        elif b == 0x1c:         # INC E
            self.inc('E')
        elif b == 0x1d:         # DEC E
            self.dec('E')
        elif b == 0x1e:         # LD E, d8
            self.E = self.read_inc_pc()
        elif b == 0x1f:         # RRA
            self.reset_flags('zero', 'half_carry', 'subtraction', 'carry')
            b0 = self.A & 0x01
            self.A /= 2
            if self.get_flag('carry'):
                self.A |= 0x80
            if b0:
                self.set_flag('carry')
        elif b == 0x20:         # JR NZ, r8
            #op = self.signedb(self.read_inc_pc())
            op = self.read_inc_pc()
            if not self.get_flag('zero'):
                self.jumprel(op)
                print self.registers['PC']
        elif b == 0x21:         # LD HL, d16
            self.HL = self.read_inc_pc(2)
        elif b == 0x22:         # LD (HL+), A
            self.HL = self.A
            self.inc('HL')
        elif b == 0x23:         # INC HL
            self.inc('HL')
        elif b == 0x24:         # INC H
            self.inc('H')
        elif b == 0x25:         # DEC H
            self.dec('H')
        elif b == 0x26:         # LD H, d8
            self.H = self.read_inc_pc()
        elif b == 0x27:         # DAA
            if self.A & 0x0f > 0x09 or self.get_flag('half_carry'):
                self.A += 0x06
            if self.A & 0xf0 > 0x90 or self.get_flag('carry'):
                self.A += 0x60
            if self.A > 0xff:
                self.set_flag('carry')
                self.A -= 0x100
            if self.A == 0x00:
                self.set_flag('zero')
            self.reset_flag('half_carry')
        elif b == 0x28:         # JR Z, r8
            #op = self.signedb(self.read_inc_pc())
            op = self.read_inc_pc()
            if self.get_flag('zero'):
                self.jumprel(op)
        elif b == 0x29:         # ADD HL, HL
            self.reset_flags('subtraction', 'half_carry', 'carry')
            if self.HL & 0x000f >= 0x0008:
                self.set_flag('half_carry')
            self.HL += self.HL
            if self.HL > 0xffff:
                self.HL -= 0x10000
                self.set_flag('carry')
        elif b == 0x2a:         # LD A, (HL+)
            self.A = self.memory[self.HL]
            self.inc('HL')
        elif b == 0x2b:         # DEC HL
            self.dec('HL')
        elif b == 0x2c:         # INC L
            self.inc('L')
        elif b == 0x2d:         # DEC L
            self.dec('L')
        elif b == 0x2e:         # LD L, d8
            self.L = self.read_inc_pc()
        elif b == 0x2f:         # CPL
            self.set_flag('subtraction')
            self.set_flag('half_carry')
            self.A = 0xff - self.A
        elif b == 0x30:         # JR NC, d8
            #op = self.signedb(self.read_inc_pc())
            op = self.read_inc_pc()
            if not self.get_flag('carry'):
                self.jumprel(op)
        elif b == 0x31:         # LD SP, d16
            self.SP = self.read_inc_pc(2)
        elif b == 0x32:         # LD (HL-), A
            self.memory[self.HL] = self.A
            self.dec('HL')
        elif b == 0x33:         # INC SP
            self.inc('SP')
        elif b == 0x34:         # INC (HL)
            self.reset_flag('subtraction')
            v = self.memory[self.HL]
            if v & 0x0f == 0x0f:
                self.set_flag('half_carry')
            if v == 0xff:
                self.set_flag('zero')
            v = (v + 1) % 0x100
            self.memory[self.HL] = v
        elif b == 0x35:         # DEC (HL)
            self.set_flag('subtraction')
            v = self.memory[self.HL]
            if v & 0x0f == 0x00:
                self.set_flag('half_carry')
            if v == 0x01:
                self.set_flag('zero')
            v -= 1
            if v == -1:
                v = 0xff
            self.memory[self.HL] = v
        elif b == 0x36:         # LD (HL), d8
            self.memory[self.HL] = self.read_inc_pc()
        elif b == 0x37:         # SCF
            self.reset_flags('half_carry', 'subtraction')
            self.set_flag('carry')
        elif b == 0x38:         # JR C, d8
            #op = self.signedb(self.read_inc_pc())
            op = self.read_inc_pc()
            if self.get_flag('carry'):
                self.jumprel(op)
        elif b == 0x39:         # ADD HL, SP
            self.reset_flag('subtraction')
            if self.L & 0x0f + self.SP & 0x000f > 0x0f:
                self.set_flag('half_carry')
            self.HL += self.SP
            if self.HL > 0xffff:
                self.HL -= 0x10000
                self.set_flag('carry')
        elif b == 0x3a:         # LD A, (HL-)
            self.A = self.memory[self.HL]
            self.dec('HL')
        elif b == 0x3b:         # DEC SP
            self.dec('SP')
        elif b == 0x3c:         # INC A
            self.inc('A')
        elif b == 0x3d:         # DEC A
            self.dec('A')
        elif b == 0x3e:         # LD A, d8
            self.A = self.read_inc_pc()
        elif b == 0x3f:         # CCF
            if self.get_flag('carry'):
                self.reset_flag('carry')
            else:
                self.set_flag('carry')
        elif b == 0x40:         # LD B, B
            pass
        elif b == 0x41:         # LD B, C
            self.B = self.C
        elif b == 0x42:         # LD B, D
            self.B = self.D
        elif b == 0x43:         # LD B, E
            self.B = self.E
        elif b == 0x44:         # LD B, H
            self.B = self.H
        elif b == 0x45:         # LD B, L
            self.B = self.L
        elif b == 0x46:         # LD B, (HL)
            self.B = self.memory[self.HL]
        elif b == 0x47:         # LD B, A
            self.B = self.A
        elif b == 0x48:         # LD C, B
            self.C = self.B
        elif b == 0x49:         # LD C, C
            pass
        elif b == 0x4a:         # LD C, D
            self.C = self.D
        elif b == 0x4b:         # LD C, E
            self.C = self.E
        elif b == 0x4c:         # LD C, H
            self.C = self.H
        elif b == 0x4d:         # LD C, L
            self.C = self.L
        elif b == 0x4e:         # LD C, (HL)
            self.C = self.memory[self.HL]
        elif b == 0x4f:         # LD C, A
            self.C = self.A
        elif b == 0x50:         # LD D, B
            self.D = self.B
        elif b == 0x51:         # LD D, C
            self.D = self.C
        elif b == 0x52:         # LD D, D
            pass
        elif b == 0x53:         # LD D, E
            self.D = self.E
        elif b == 0x54:         # LD D, H
            self.D = self.H
        elif b == 0x55:         # LD D, L
            self.D = self.L
        elif b == 0x56:         # LD D, (HL)
            self.D = self.memory[self.HL]
        elif b == 0x57:         # LD D, A
            self.D = self.A
        elif b == 0x58:         # LD E, B
            self.E = self.B
        elif b == 0x59:         # LD E, C
            self.E = self.C
        elif b == 0x5a:         # LD E, D
            self.E = self.D
        elif b == 0x5b:         # LD E, E
            pass
        elif b == 0x5c:         # LD E, H
            self.E = self.H
        elif b == 0x5d:         # LD E, L
            self.E = self.L
        elif b == 0x5e:         # LD E, (HL)
            self.E = self.memory[self.HL]
        elif b == 0x5f:         # LD E, A
            self.E = self.A
        elif b == 0x60:         # LD H, B
            self.H = self.B
        elif b == 0x61:         # LD H, C
            self.H = self.C
        elif b == 0x62:         # LD H, D
            self.H = self.D
        elif b == 0x63:         # LD H, E
            self.H = self.E
        elif b == 0x64:         # LD H, H
            pass
        elif b == 0x65:         # LD H, L
            self.H = self.L
        elif b == 0x66:         # LD H, (HL)
            self.H = self.memory[self.HL]
        elif b == 0x67:         # LD H, A
            self.H = self.A
        elif b == 0x68:         # LD L, B
            self.L = self.B
        elif b == 0x69:         # LD L, C
            self.L = self.C
        elif b == 0x6a:         # LD L, D
            self.L = self.D
        elif b == 0x6b:         # LD L, E
            self.L = self.E
        elif b == 0x6c:         # LD L, H
            self.L = self.H
        elif b == 0x6d:         # LD L, L
            pass
        elif b == 0x6e:         # LD L, (HL)
            self.L = self.memory[self.CHL]
        elif b == 0x6f:         # LD L, A
            self.L = self.A
        elif b == 0x70:         # LD (HL), B
            self.memory[self.HL] = self.B
        elif b == 0x71:         # LD (HL), C
            self.memory[self.HL] = self.C
        elif b == 0x72:         # LD (HL), D
            self.memory[self.HL] = self.D
        elif b == 0x73:         # LD (HL), E
            self.memory[self.HL] = self.E
        elif b == 0x74:         # LD (HL), H
            self.memory[self.HL] = self.H
        elif b == 0x75:         # LD (HL), L
            self.memory[self.HL] = self.L
        elif b == 0x76:         # HALT
            self.running = False
        elif b == 0x77:         # LD (HL), A
            self.memory[self.HL] = self.A
        elif b == 0x78:         # LD A, B
            self.A = self.B
        elif b == 0x79:         # LD A, C
            self.A = self.C
        elif b == 0x7a:         # LD A, D
            self.A = self.D
        elif b == 0x7b:         # LD A, E
            self.A = self.E
        elif b == 0x7c:         # LD A, H
            self.A = self.H
        elif b == 0x7d:         # LD A, L
            self.A = self.L
        elif b == 0x7e:         # LD A, (HL)
            self.A = self.memory[self.CHL]
        elif b == 0x7f:         # LD A, A
            pass
        elif b == 0x80:         # ADD A, B
            self.add('A', 'B')
        elif b == 0x81:         # ADD A, C
            self.add('A', 'C')
        elif b == 0x82:         # ADD A, D
            self.add('A', 'D')
        elif b == 0x83:         # ADD A, E
            self.add('A', 'E')
        elif b == 0x84:         # ADD A, H
            self.add('A', 'H')
        elif b == 0x85:         # ADD A, L
            self.add('A', 'L')
        elif b == 0x86:         # ADD A, (HL)
            self.add('A', self.memory[self.HL], rtype = 0x01)
        elif b == 0x87:         # ADC A, A
            self.add('A', 'A', carry = True)
        elif b == 0x88:         # ADC A, B
            self.add('A', 'B', carry = True)
        elif b == 0x89:         # ADC A, C
            self.add('A', 'C', carry = True)
        elif b == 0x8a:         # ADC A, D
            self.add('A', 'D', carry = True)
        elif b == 0x8b:         # ADC A, E
            self.add('A', 'E', carry = True)
        elif b == 0x8c:         # ADC A, H
            self.add('A', 'H', carry = True)
        elif b == 0x8d:         # ADC A, L
            self.add('A', 'L', carry = True)
        elif b == 0x8e:         # ADC A, (HL)
            self.add('A', self.memory[self.HL], rtype = 0x01, carry = True)
        elif b == 0x8f:         # ADC A, A
            self.add('A', 'A', carry = True)
        elif b == 0x90:         # SUB B
            self.sub('B')
        elif b == 0x91:         # SUB C
            self.sub('C')
        elif b == 0x92:         # SUB D
            self.sub('D')
        elif b == 0x93:         # SUB E
            self.sub('E')
        elif b == 0x94:         # SUB H
            self.sub('H')
        elif b == 0x95:         # SUB L
            self.sub('L')
        elif b == 0x96:         # SUB (HL)
            self.sub(self.memory[self.HL])
        elif b == 0x97:         # SUB A
            self.sub('A')
        elif b == 0x98:         # SBC B
            self.sub('B', carry = True)
        elif b == 0x99:         # SBC C
            self.sub('C', carry = True)
        elif b == 0x9a:         # SBC D
            self.sub('D', carry = True)
        elif b == 0x9b:         # SBC E
            self.sub('E', carry = True)
        elif b == 0x9c:         # SBC H
            self.sub('H', carry = True)
        elif b == 0x9d:         # SBC L
            self.sub('L', carry = True)
        elif b == 0x9e:         # SBC (HL)
            self.sub(self.memory[self.HL], carry = True)
        elif b == 0x9f:         # SBC A
            self.sub('A', carry = True)
        elif b == 0xa0:         # AND B
            self.and_('B')
        elif b == 0xa1:         # AND C
            self.and_('C')
        elif b == 0xa2:         # AND D
            self.and_('D')
        elif b == 0xa3:         # AND E
            self.and_('E')
        elif b == 0xa4:         # AND H
            self.and_('H')
        elif b == 0xa5:         # AND L
            self.and_('L')
        elif b == 0xa6:         # AND (HL)
            self.and_(self.memory[self.HL])
        elif b == 0xa7:         # AND A
            self.and_('A')
        elif b == 0xa8:         # XOR B
            self.xor('B')
        elif b == 0xa8:         # XOR C
            self.xor('C')
        elif b == 0xa8:         # XOR D
            self.xor('D')
        elif b == 0xa8:         # XOR E
            self.xor('E')
        elif b == 0xa8:         # XOR H
            self.xor('H')
        elif b == 0xa8:         # XOR L
            self.xor('L')
        elif b == 0xa8:         # XOR (HL)
            self.xor(self.memory[self.HL])
        elif b == 0xa8:         # XOR A
            self.xor('A')
        elif b == 0xa0:         # AND B
            self.and_('B')
        elif b == 0xa1:         # AND C
            self.and_('C')
        elif b == 0xa2:         # AND D
            self.and_('D')
        elif b == 0xa3:         # AND E
            self.and_('E')
        elif b == 0xa4:         # AND H
            self.and_('H')
        elif b == 0xa5:         # AND L
            self.and_('L')
        elif b == 0xa6:         # AND (HL)
            self.and_(self.memory[self.HL])
        elif b == 0xa7:         # AND A
            self.and_('A')
        elif b == 0xa8:         # XOR B
            self.xor('B')
        elif b == 0xa9:         # XOR C
            self.xor('C')
        elif b == 0xaa:         # XOR D
            self.xor('D')
        elif b == 0xab:         # XOR E
            self.xor('E')
        elif b == 0xac:         # XOR H
            self.xor('H')
        elif b == 0xad:         # XOR L
            self.xor('L')
        elif b == 0xae:         # XOR (HL)
            self.xor(self.memory[self.HL])
        elif b == 0xaf:         # XOR A
            self.xor('A')
        elif b == 0xb0:         # OR B
            self.or_('B')
        elif b == 0xb1:         # OR C
            self.or_('C')
        elif b == 0xb2:         # OR D
            self.or_('D')
        elif b == 0xb3:         # OR E
            self.or_('E')
        elif b == 0xb4:         # OR H
            self.or_('H')
        elif b == 0xb5:         # OR L
            self.or_('L')
        elif b == 0xb6:         # OR (HL)
            self.or_(self.memory[self.HL])
        elif b == 0xb7:         # OR A
            self.or_('A')
        elif b == 0xb8:         # CP B
            self.cp('B')
        elif b == 0xb9:         # CP C
            self.cp('C')
        elif b == 0xba:         # CP D
            self.cp('D')
        elif b == 0xbb:         # CP E
            self.cp('E')
        elif b == 0xbc:         # CP H
            self.cp('H')
        elif b == 0xbd:         # CP L
            self.cp('L')
        elif b == 0xbe:         # CP (HL)
            self.cp(self.memory[self.HL])
        elif b == 0xbf:         # CP A
            self.cp('A')
        elif b == 0xc0:         # RET NZ
            if not self.get_flag('zero'):
                self.PC = self.pop()
        elif b == 0xc1:         # POP BC
            self.BC = self.pop()
        elif b == 0xc2:         # JP NZ, a16
            op = self.read_inc_pc(2)
            if not self.get_flag('zero'):
                self.jumpabs(op)
        elif b == 0xc3:         # JP a16
            self.jumpabs(self.read_inc_pc(2))
        elif b == 0xc4:         # CALL NZ, a16
            op = self.read_inc_pc(2)
            if not self.get_flag('zero'):
                self.push(self.PC)
                self.jumpabs(op)
        elif b == 0xc5:         # PUSH BC
            self.push(self.BC)
        elif b == 0xc6:         # ADD A, d8
            op = self.read_inc_pc()
            self.add('A', op)
        elif b == 0xc7:         # RST 00h
            self.push(self.PC)
            self.PC = 0x0000
        elif b == 0xc8:         # RET Z
            if self.get_flag('zero'):
                self.PC = self.pop()
        elif b == 0xc9:         # RET
            self.PC = self.pop()
        elif b == 0xca:         # JP Z, a16
            op = self.read_inc_pc(2)
            if not self.get_flag('zero'):
                self.jumpabs(op)
        elif b == 0xcb:         # TODO: bit operations
            pass
        elif b == 0xcc:         # CALL Z, a16
            op = self.read_inc_pc(2)
            if self.get_flag('zero'):
                self.push(self.PC)
                self.jumpabs(op)
        elif b == 0xcd:         # CALL a16
            op = self.read_inc_pc(2)
            self.push(self.PC)
            self.jumpabs(op)
        elif b == 0xce:         # ADC A, d8
            self.add('A', self.read_inc_pc(), carry = True)
        elif b == 0xcf:         # RST 08h
            self.push(self.PC)
            self.PC = 0x0008
        elif b == 0xd0:         # RET NC
            if not self.get_flag('carry'):
                self.PC = self.pop()
        elif b == 0xd1:         # POP HL
            self.HL = self.pop()
        elif b == 0xd2:         # JP NC, a16
            op = self.read_inc_pc(2)
            if not self.get_flag('carry'):
                self.jumpabs(op)
        elif b == 0xd4:         # CALL NC, a16
            op = self.read_inc_pc(2)
            if not self.get_flag('carry'):
                self.push(self.PC)
                self.jumpabs(op)
        elif b == 0xd5:         # PUSH DE
            self.push(self.DE)
        elif b == 0xd6:         # SUB d8
            self.sub(self.read_inc_pc())
        elif b == 0xd7:         # RST 10h
            self.push(self.PC)
            self.PC = 0x0010
        elif b == 0xd8:         # RET C
            if self.get_flag('carry'):
                self.PC = self.pop()
        elif b == 0xd9:         # RETI
            self.PC = self.pop()
        elif b == 0xda:         # JP C, a16
            op = self.read_inc_pc(2)
            if self.get_flag('carry'):
                self.jumpabs(op)
        elif b == 0xdc:         # CALL C, a16
            op = self.read_inc_pc(2)
            if self.get_flag('carry'):
                self.push(self.PC)
                self.jumpabs(op)
        elif b == 0xde:         # SBC A, d8
            self.sub(self.read_inc_pc(1), carry = True)
        elif b == 0xdf:         # RST 18h
            self.push(self.PC)
            self.PC = 0x0018
        elif b == 0xe0:         # LDH (a8), A
            op = self.read_inc_pc()
            self.memory[op + 0xff00] = self.A
        elif b == 0xe1:         # POP HL
            self.HL = self.pop()
        elif b == 0xe2:         # LD (C), A
            self.memory[0xff00 + self.C] = self.A
        elif b == 0xe5:         # PUSH HL
            self.push(self.HL)
        elif b == 0xe6:         # AND d8
            self.and_(self.read_inc_pc())
        elif b == 0xe7:         # RST 20h
            self.push(self.PC)
            self.PC = 0x0020
        elif b == 0xe8:         # ADD SP, r8
            #o = self.signedb(self.read_inc_pc())
            o = self.read_inc_pc()
            self.reset_flags('zero', 'subtraction', 'half_carry', 'carry')
            if self.SP & 0x000f + o & 0x0f > 0x0f:
                self.set_flag('half_carry')
            self.SP += o
            if self.SP > 0xffff:
                self.set_flag('carry')
                self.SP -= 0x10000
            elif self.SP < 0:
                self.SP += 0x10000
                self.set_flag('carry')
        elif b == 0xe9:         # JP (HL)
            self.jumpabs(self.memory[self.HL] + self.memory[self.HL + 1] * 256)
        elif b == 0xea:         # LD (a16), A
            op = self.read_inc_pc(2)
            self.memory[op] = self.A
            if op >= 0x2000 and op < 0x4000:
                self.memory[0x4000:0x8000] = self.cartridge[self.A * 0x4000 + 0x0000:self.A * 0x4000 + 0x4000]
        elif b == 0xee:         # XOR d8
            self.xor(self.read_inc_pc())
        elif b == 0xef:         # RST 28h
            self.push(self.PC)
            self.PC = 0x0028
        elif b == 0xf0:         # LDH A, (a8)
            self.A = self.memory[self.read_inc_pc() + 0xff00]
        elif b == 0xf1:         # POP AF
            self.AF = self.pop()
        elif b == 0xf2:         # LD A, (C)
            self.A = self.memory[self.C + 0xff00]
        elif b == 0xf3:         # DI
            self.memory[0xffff] = 0x00
        elif b == 0xf5:         # PUSH AF
            self.push(self.AF)
        elif b == 0xf6:         # OR d8
            self.or_(self.read_inc_pc())
        elif b == 0xf7:         # RST 30h
            self.push(self.PC)
            self.PC = 0x0030
        elif b == 0xf8:         # LD HL, SP + r8
            self.reset_flags('subtraction', 'zero', 'half_carry', 'carry')
            o = self.read_inc_pc()
            if self.SP & 0x000f + o & 0x0f > 0x0f:
                self.set_flag('half_carry')
            self.HL = self.SP + o
            if self.HL > 0xffff:
                self.HL -= 0x10000
                self.set_flag('carry')
        elif b == 0xf9:         # LD SP, HL
            self.SP = self.HL
        elif b == 0xfa:         # LD A, (a16)
            self.A = self.memory[self.read_inc_pc(2)]
        elif b == 0xfb:         # EI
            self.memory[0xffff] = 0xff
        elif b == 0xfe:         # CP d8
            self.cp(self.read_inc_pc())
            #op = self.read_inc_pc()
        elif b == 0xff:         # RST 38h
            self.push(self.PC)
            self.PC = 0x0038
        else:
            #raise Exception('OpCode %d not implemented yet' % b)
            print 'OpCode %x not implemented yet' % b
            print self.registers
            self.running = False

    def reset_flags(self, *flags):
        for flag in flags:
            self.reset_flag(flag)

    def reset_flag(self, name):
        self.registers['F'] = self.registers['F'] | (255 - self.flags[name])

    def set_flags(self, *flags):
        for flag in flags:
            self.set_flag(flag)

    def set_flag(self, name):
        self.registers['F'] = self.registers['F'] | self.flags[name]

    def get_flag(self, name):
        return (self.registers['F'] & self.flags[name]) != 0

    def push(self, op):
        self.SP -= 2
        self.memory[self.SP + 1] = op % 256
        self.memory[self.SP + 2] = op / 256

    def pop(self):
        ret = self.memory[self.SP + 1] + self.memory[self.SP + 2] * 256
        self.SP += 2
        return ret

    def and_(self, r):
        self.reset_flags('subtraction', 'carry', 'zero')
        self.set_flag('half_carry')
        o = r
        if r in ['A', 'B', 'C', 'D', 'E', 'H', 'L']:
            o = self.registers[r]

        self.A &= o
        if self.A == 0x00:
            self.set_flag('zero')

    def xor(self, r):
        self.reset_flags('subtraction', 'carry', 'zero', 'half_carry')
        o = r
        if r in ['A', 'B', 'C', 'D', 'E', 'H', 'L']:
            o = self.registers[r]

        self.A ^= o
        if self.A == 0x00:
            self.set_flag('zero')

    def or_(self, r):
        self.reset_flags('subtraction', 'carry', 'zero', 'half_carry')
        o = r
        if r in ['A', 'B', 'C', 'D', 'E', 'H', 'L']:
            o = self.registers[r]

        self.A |= o
        if self.A == 0x00:
            self.set_flag('zero')

    def cp(self, r):
        self.set_flag('subtraction')
        o = r
        if r in ['A', 'B', 'C', 'D', 'E', 'H', 'L']:
            o = self.registers[r]
        
        if self.A & 0x0f + o & 0x0f > 0x0f:
            self.set_flag('half_carry')
        s = self.A + o
        if s > 0xff: 
            self.set_flag('carry')
            s -= 0x100
        if s == 0x00:
            self.set_flag('zero')

    def sub(self, r, carry = False):
        if r in ['A', 'B', 'C', 'D', 'E', 'H', 'L']:
            o = self.registers[r]
        else:
            o = r
        if carry:
            o += 1

        self.reset_flags('zero', 'carry', 'half_carry')
        self.set_flag('subtraction')

        if self.A & 0x0f + o & 0x0f > 0x0f:
            self.set_flag('half_carry')

        self.A += o
        if self.A > 0xff:
            self.set_flag('carry')
            self.A -= 0x100
        if self.A == 0x00:
            self.set_flag('zero')


    def add(self, r1, r2, carry = False):
        o2 = r2
        if r2 in ['A', 'B', 'C', 'D', 'E', 'H', 'L']:
            o2 = self.registers[r2]
        if carry:
            o2 += 1

        self.reset_flags('zero', 'carry', 'half_carry', 'subtraction')
        if self.registers[r1] & 0x0f + o2 & 0x0f > 0x0f:
            self.set_flag('half_carry')
        self.registers[r1] += o2
        if self.registers[r1] > 0xff:
            self.registers[r1] -= 0x100
            self.set_flag('carry')
        if self.registers[r1] == 0x00:
            self.set_flag('zero')

    def inc(self, reg):
        if len(reg) == 1:
            self.reset_flag('subtraction')
            if self.registers[reg] & 0x0f == 0x0f:
                self.set_flag('half_carry')
            self.registers[reg] += 1
            if self.registers[reg] == 0x100:
                self.registers[reg] = 0x00
                self.set_flag('zero')
        elif len(reg) == 2:
            self.registers[reg[1]] += 1
            if self.registers[reg[1]] == 0x100:
                self.registers[reg[1]] = 0x00
                self.registers[reg[0]] += 1
                if self.registers[reg[0]] == 0x100:
                    self.registers[reg[0]] = 0x00

    def dec(self, reg):
        if reg in ['A', 'B', 'C', 'D', 'E', 'F', 'H', 'L']:
            self.set_flag('subtraction')
            if self.registers[reg] & 0x0f == 0x00:
                self.set_flag('half_carry')
            self.registers[reg] -= 1
            if self.registers[reg] == -1:
                self.registers[reg] = 0x00
                self.set_flag('zero')
        elif reg in ['AF', 'BC', 'DE', 'HL']:
            self.registers[reg[1]] -= 1
            if self.registers[reg[1]] == -1:
                self.registers[reg[1]] = 0xff
                self.registers[reg[0]] -= 1
                if self.registers[reg[0]] == -1:
                    self.registers[reg[0]] = 0xff
        elif reg in ['SP', 'PC']:
            self.registers[reg] += 1
            if self.registers[reg] == 0x10000:
                self.registers[reg] = 0x0000

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
    q = open('opcodes/z80gb.json')
    ops = json.load(q)
    q.close()

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
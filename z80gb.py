import json

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
import json

class Z80instruction:
    def __init__(self, addr, instr, ops):
        self.addr = addr
        self.instr = instr
        self.ops = ops

    def __str__(self):
        #print self.instr, self.ops
        return "%08X: %s %s" % (self.addr, self.instr, ', '.join(self.ops))

class Z80:
    ops = json.load(open('opcodes.json'))

    @staticmethod
    def decodeStream(data, base):
        ret = []
        idx = 0

        while idx < len(data):
            tidx = idx
            key = ""
            ops = Z80.ops
            
            while (not ops.has_key(key)) and tidx < idx + 3 and tidx < len(data):
                key += "%02X" % data[tidx]
                tidx += 1

            if tidx == idx + 3 or (tidx == len(data) and not ops.has_key(key)):
                ret.append(Z80instruction(base+idx, 'unk', ["0x%02X" % data[idx]]))
                idx += 1
            else:
                found = False
                i = 0
                while not found and i < len(ops[key]):
                    instr = ops[key][i]['op']
                    operands = ops[key][i]['operands']
                    params = []
                    invalid = False
                    
                    for follow in ops[key][i]['follows']:
                        if follow == 'byte':
                            params.append("0x%02X" % data[tidx])
                            tidx += 1
                        elif follow == 'word':
                            params.append("0x%02X%02X" % (data[tidx+1], data[tidx]))
                            tidx += 2
                        elif follow == 'dword':
                            params.append("0x%02X%02X%02X%02X" % \
                                (data[tidx+3], data[tidx+2], data[tidx+1], data[tidx]))
                            tidx += 4
                        else:
                            if (follow != "%02X" % data[tidx]):
                                invalid = True
                            tidx += 1
                    
                    if not invalid:
                        j = 0
                        for i in range(0, len(operands)):
                            if 'word' in operands[i]:
                                operands[i] = operands[i].replace('word', params[j])
                                j += 1
                            if 'byte' in operands[i]:
                                operands[i] = operands[i].replace('byte', params[j])
                                j += 1

                        ret.append(Z80instruction(base+idx, instr, operands))
                        found = True
                        idx = tidx

                    i += 1
                if not found:
                    idx += 1
        return ret


    @staticmethod
    def decodeStreamPP(data, base):
        r = Z80.decodeStream(data, base)
        for i in r:
            print i

    @staticmethod
    def decodeStreamFile(data, path, base):
        f = open(path, 'w')
        r = Z80.decodeStream(data, base)
        for i in r:
            f.write(str(i) + "\n")

    @staticmethod
    def decodeString(string, base):
        ret = []
        for c in string:
            ret.append(c)
        return Z80.decodeStream(map(ord, ret), base)

    @staticmethod
    def decodeStringPP(string, base):
        ret = []
        for c in string:
            ret.append(c)
        return Z80.decodeStreamPP(map(ord, ret), base)

    @staticmethod
    def decodeStringFile(string, path, base):
        ret = []
        for c in string:
            ret.append(c)
        Z80.decodeStreamFile(map(ord, ret), path, base)
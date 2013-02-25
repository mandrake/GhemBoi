import json

class Z80:
    ops = json.load(open('opcodes.json'))

    @staticmethod
    def decodeStream(data):
        idx = 0
        f = open('disasm.asm', 'w')
        while idx < len(data):
            tidx = idx
            key = ""
            ops = Z80.ops
            
            while (not ops.has_key(key)) and tidx < idx + 3:
                key += "%02X" % data[tidx]
                tidx += 1

            if tidx == idx + 3:
                f.write("unk\n")
                idx += 1
            else:
                instr = ops[key]['op']
                operands = ops[key]['operands']
                params = []
                invalid = False
                for follow in ops[key]['follows']:
                    if follow == 'byte':
                        params.append("%02X" % data[tidx])
                        tidx += 1
                    elif follow == 'word':
                        params.append("%02X%02X" % (data[tidx], data[tidx+1]))
                        tidx += 2
                    else:
                        if (follow != "%02X" % data[tidx]):
                            invalid = True
                        tidx += 1
                if invalid:
                    idx += 1
                    f.write("unk\n")
                else:
                    j = 0
                    for i in range(0, len(operands)):
                        if 'word' in operands[i]:
                            operands[i] = operands[i].replace('word', params[j])
                            j += 1
                        if 'byte' in operands[i]:
                            operands[i] = operands[i].replace('word', params[j])
                            j += 1
                    #print instr,
                    #print operands
                    f.write(instr)
                    f.write(str(operands))
                    f.write('\n')

                    idx = tidx


    @staticmethod
    def decodeStreamPP(data):
        return None

    @staticmethod
    def decodeString(string):
        ret = []
        for c in string:
            ret.append(c)
        print len(string)
        x = map(ord, ret)
        Z80.decodeStream(x)

    @staticmethod
    def decodeStringPP(string):
        ret = []
        for c in string:
            ret.append(c)
        x = map(ord, ret)
        return Z80.decodeStreamPP(x)
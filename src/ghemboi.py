from cartridge import *
from mbc import *
from z80gb import *
from display import *

"""
class GhemBoi:
    offsets = {
        'header':   slice(0x0100, 0x0150)
    }

    memory_map = {}

    def chunk(self, name):
        return self.data[self.offsets[name]]

    def __init__(self, path):
        #self.data = map(ord, open(path, 'rb').read())
        f = open(path, 'rb')

        self.data = bytearray(f.read())
        self.header = GhemBoiHeader(self.chunk('header'))

        print str(self.header)
        print "%04Xh" % self.header.entry
        z = Z80sym(self.data)
    #    Z80.decodeStreamFile(self.data[int(self.header.entry):], 'disasm.asm', self.header.entry)
""" 

f = open('Pokemon Argento (ITA).gb', 'rb')
c = Cartridge(bytearray(f.read()))
f.close()

mbc_dict = {
    'MBC1': MemoryBlockController1,
    'MBC': MemoryBlockController1,
    'MBC2': MemoryBlockController2,
    'MBC3': MemoryBlockController3
}

cartridge_features = c.header.info['cartridge_type'].split('+')
f = open('DMG_ROM.bin', 'rb')
rom = bytearray(f.read())
f.close()
for m in mbc_dict.keys():
    if m in cartridge_features:
        mbc = mbc_dict[m](c, rom)

d = Display(mbc)
d.start()

z = z80gb.Z80sym(mbc)
z.run()
import json
import os
from z80gb import *

class GhemBoi:
    d = []

    @staticmethod
    def dataOffsetLength(o, l):
        return GhemBoi.d[o:o+l]

    def __init__(self, path):

        self.base = 0x0134
        self.data = GhemBoi.d = open(path, 'rb').read()

        def _d(o, l):
            return GhemBoi.dataOffsetLength(self.base + o, l)

        def _hb(o):
            return "%02X" % ord(GhemBoi.dataOffsetLength(self.base + o, 1))

        def _hw(o):
            return "%02X%02X" % \
                (ord(GhemBoi.dataOffsetLength(self.base + o, 1)), \
                 ord(GhemBoi.dataOffsetLength(self.base + o + 1, 1)))

        def _hd(o):
            return "%02X%02X%02X%02X" % \
                (ord(GhemBoi.dataOffsetLength(self.base + o, 1)), \
                 ord(GhemBoi.dataOffsetLength(self.base + o + 1, 1)), \
                 ord(GhemBoi.dataOffsetLength(self.base + o + 2, 1)), \
                 ord(GhemBoi.dataOffsetLength(self.base + o + 3, 1)))

        meta = json.load(open('meta.json'))
        
        self.info = {}

        self.info['name'] = _d(0, 16)
        self.info['licensee'] = meta['licensee'][_d(16, 2)]
        # self.info['SGB features'] = meta['SGB features'][_h(18, 1)]
        # self.info['Cartridge type'] = meta['cartridge'][_h(19, 1)]
        self.info['SGB features'] = _hb(18)
        self.info['Cartridge type'] = _hb(19)
        self.info['size'] = meta['size'][_hb(20)]
        self.info['savesize'] = meta['savesize'][_hb(21)]
        self.info['country'] = meta['country'][_hb(22)]
        self.info['licensee'] = _hb(23)
        self.info['hdrcheck'] = _hb(24)
        self.info['gblcheck'] = _hw(25)

        print len(self.data)
        Z80.decodeStringFile(self.data[0x05c6:], 'disasm.asm', 0x05c6)

    def __str__(self):
        return str(self.info)

g = GhemBoi('Pokemon Argento (ITA).gb')
print g
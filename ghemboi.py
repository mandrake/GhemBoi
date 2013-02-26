import json
import os
from z80gb import *

class Endianness:
    Little = 0
    Big = 1

class DataParser:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def s(self, size):
        r = self.data[self.index:self.index+size]
        self.index += size
        return ''.join(map(chr, r))

    def ston(self):
        return int(self.s(1), 16)

    # Parses 2 bytes as characters, and evaluates
    # them as a hex string, returning the int value associated
    def stob(self):
        return self.ston() * 16 + self.ston()

    # Parses 4 bytes as characters, and evaluates
    # them as a hex string, returning the int value associated
    def stow(self, end=Endianness.Little):
        if end == Endianness.Little:
            return self.stob() + self.stob()*256
        elif end == Endianness.Big:
            return self.stob()*256 + self.stob()
        else:
            raise Exception("AAAAAH")

    def stod(self, end=Endianness.Little):
        if end == Endianness.Little:
            return self.stob() + self.stob()*256 + self.stob()*256*256 + self.stob()*256*256*256
        elif end == Endianness.Big:
            return self.stob()*256*256*256 + self.stob()*256*256 + self.stob()*256 + self.stob()
        else:
            raise Exception("AAAAAAAH")

    def b(self):
        self.index += 1
        return int(self.data[self.index-1])

    def w(self, end=Endianness.Little):
        if end == Endianness.Little:
            return self.b() + self.b()*256
        elif end == Endianness.Big:
            return self.b()*256 + self.b()
        else:
            raise Exception("NOOOOOO")

    def raw(self, off):
        self.index += off
        return self.data[self.index-off:self.index]

class GhemBoiHeader:
    def __init__(self, data):
        self.data = data

        p = DataParser(self.data)
        meta = json.load(open('header_data.json'))

        self.info = {}
        intrl = Z80.decodeStream(p.raw(0x04), 0x0100)

        self.info['logo'] = p.raw(0x30)
        self.info['title'] = p.s(0x0f)
        self.info['colour_compatibility'] = p.b()
        self.info['licensee'] = meta['licensee']["%02X" % p.stob()]
        self.info['gb_sgb_function'] = p.b()
        self.info['cartridge_type'] = meta['rom_type']["%02X" % p.b()]
        self.info['rom_size'] = meta['size']["%02X" % p.b()]
        self.info['ram_size'] = meta['size']["%02X" % p.b()]
        self.info['destination_code'] = meta['country']["%02X" % p.b()]
        self.info['old_licensee'] = p.b()
        self.info['mask_rom_version'] = p.b()
        self.info['compl_checksum'] = p.b()
        self.info['checksum'] = p.w(end=Endianness.Big)

        self.entry = intrl[1].ops[0]

    def __str__(self):
        r = 'GameBoy Cartridge\n'
        r = r + '=================\n'
        r = r + '\n'
        for k in self.info:
            if type(self.info[k]) == int:
                r = r + k + ": " + "%Xh" % self.info[k] + '\n'
            else:
                r = r + k + ": " + str(self.info[k]) + '\n'
        return r

class GhemBoi:
    def __init__(self, path):
        self.data = map(ord, open(path, 'rb').read())

        self.header = GhemBoiHeader(self.data[0x0100:0x0150])

        print str(self.header)
        print "%04Xh" % self.header.entry
        Z80.decodeStreamFile(self.data[int(self.header.entry):], 'disasm.asm', self.header.entry)

g = GhemBoi('Pokemon Argento (ITA).gb')
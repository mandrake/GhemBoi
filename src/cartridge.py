from binparse import * 
import json
import z80gb

class Cartridge(object):

    def __init__(self, data):
        self.data = data
        self.ram_banks = [0x2000 * [0x00]] * 4
        self.header = CartridgeHeader(data[0x0100:0x0150])

    def get_rom_bank(self, n):
        return self.data[0x4000 * bank:0x4000 * bank + 0x4000]

    def get_ram_bank(self, n):
        return self.ram_banks[n]

class CartridgeHeader:
    def __init__(self, data):
        self.data = data

        p = DataParser(self.data)
        meta = json.load(open('header_data.json'))

        self.info = {}
        intrl = z80gb.Z80.decodeStream(p.raw(0x04), 0x0100)
        
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
        self.info['checksum'] = p.w(end = Endianness.Big)

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
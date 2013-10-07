from cartridge import *

class MemoryBlockController1(object):

    def __init__(self, cartridge):
        self.ram_enable = 0x00
        self.cartridge = cartridge

        self.rom_bank_no = None
        self.ram_bank = None

    def update_rom_bank(self):
        v = self.rom_bank_no
        if v in [0x00, 0x20, 0x40, 0x60]:
            v += 1
        self.memory[0x4000:0x8000] = self.cartridge[0x4000 * v:0x4000 * (v + 1)]

    def set_ram_bank(self, value):
        self.ram_bank = self.cartridge.get_ram_bank(value)

    def __setitem__(self, offset, value):
        if not (value >= 0x00 and value <= 0xff):
            raise Exception('Invalid write in memory')
        if offset >= 0x0000 and offset <= 0x1fff:           # RAM Enable
            print 'Write in interval 0x0000 - 0x1fff'
            if x == 0x00:
                self.ram_enable = False
            elif x == 0x0A:
                self.ram_enable = True
            else:
                raise Exception('Invalid write in interval 0x0000 - 0x1fff')
        elif offset >= 0x2000 and offset <= 0x3fff:         # ROM Bank Number
            print 'Write in interval 0x2000 - 0x3fff'
            self.rom_bank_no &= 0xe0
            self.rom_bank_no |= (value & 0x1f)
            self.update_rom_bank()
        elif offset >= 0x4000 and offset <= 0x5fff:         # RAM Bank Number - Upper Bits of ROM Bank Number
            print 'Write in interval 0x4000 - 0x5fff'
            if value <= 0b00000011:
                if self.ram_enable == 0x00:
                    self.rom_bank_no |= value * 32
                    self.update_rom_bank()
                else:
                    self.set_ram_bank(value)
            else:
                raise Exception('Invalid write in interval 0x4000 - 0x5fff')
        elif offset >= 0x6000 and offset <= 0x7fff:         # ROM/RAM mode select
            print 'Write in interval 0x6000 - 0x7fff'
            if value < 2:
                self.rom_ram_mode_select = value
            else:
                raise Exception('Invalid write in interval 0x6000 - 0x7fff')
        elif offset >= 0xa000 and offset <= 0xbfff:         # External RAM
            print 'Write in interval 0xa000 - 0xbfff (External RAM)'
            if value >= 0x00 and value <= 0xff:
                self.ram_bank[offset - 0xa000] = value
            else:
                raise Exception('Invalid write in interval 0xa000 - 0xbfff (%d)' % value)
        else:
            if value >= 0x00 and value <= 0xff:
                self.memory[offset] = value
            else:
                raise Exception("Invalid write in memory")

    def __getitem__(self, offset):
        # TODO: external RAM
        return self.memory[offset]

class MemoryBlockController2(object):

    def __init__(self, cartridge):
        self.ram_enable = False
        self.cartridge = cartridge

        self.mbc_ram  = [0x00] * 512

    def set_rom_bank(self, value):
        self.memory[0x4000:0x8000] = self.cartridge[0x4000 * value:0x4000 * (value + 1)]

    def __setitem__(self, offset, value):
        if not (value >= 0x00 and value <= 0xff):
            raise Exception('Invalid write in memory')

        if offset >= 0x0000 and offset <= 0x1fff:           # RAM Enable
            print 'Write in interval 0x0000 - 0x1fff'
            if offset & 0x0100 == 0x0000:
                if x == 0x00:
                    self.ram_enable = False
                elif x == 0x0A:
                    self.ram_enable = True
                else:
                    raise Exception('Invalid value for ram_clock_write_protect')
            else:
                print 'Dummy write in interval 0x0000 - 0x1fff (%04h)' % offset
        elif offset >= 0x2000 and offset <= 0x3fff:         # ROM Bank Number
            print 'Write in interval 0x2000 - 0x3fff'
            if value % 16 == 0x00:
                value += 0x01

            if offset & 0x0100 == 0x0100:
                self.set_rom_bank(value % 32)
            else:
                print 'Dummy write in interval 0x2000 - 0x3fff (%04h)' % offset
        elif offset >= 0xa000 and offset <= 0xafff:
            self.mbc_ram[offset - 0xa000] = value & 0x0f
        else:
            self.memory[offset] = value

    def __getitem__(self, offset):
        # TODO: external RAM
        return self.memory[offset]

class MemoryBlockController3(object):
    RAM_TIMER_RAM    = 0x00
    RAM_TIMER_RTC_S  = 0x08
    RAM_TIMER_RTC_M  = 0x09
    RAM_TIMER_RTC_H  = 0x0a
    RAM_TIMER_RTC_DL = 0x0b
    RAM_TIMER_RTC_DH = 0x0c

    def __init__(self, cartridge, boot_rom):
        self.ram_and_timer_enable = 0x00
        self.cartridge = cartridge
        self.boot_rom = boot_rom

        self.rom_bank_no = None
        self.ram_bank = None

        self.memory = [0x00] * 0x10000

        self.ram_and_timer_mode = None
        self.rtc = {
            'S': 0x00,
            'M': 0x00,
            'H': 0x00,
            'D': 0x0000
        }

    def update_rom_bank(self):
        v = self.rom_bank_no
        if v == 0x00:
            v += 1
        self.memory[0x4000:0x8000] = self.cartridge[0x4000 * v:0x4000 * (v + 1)]

    def set_ram_bank(self, value):
        self.ram_bank = self.cartridge.get_ram_bank(value)

    def __setitem__(self, offset, value):
        if not (value >= 0x00 and value <= 0xff):
            raise Exception('Invalid write in memory')
        if offset >= 0x0000 and offset <= 0x1fff:           # RAM and Timer Enable
            print 'Write in interval 0x0000 - 0x1fff (RAM and Timer Enable)'
            if value == 0x00:
                self.ram_and_timer_enable = False
            elif value == 0x0A:
                self.ram_and_timer_enable = True
            else:
                raise Exception('Invalid value for ram_clock_write_protect')
        elif offset >= 0x2000 and offset <= 0x3fff:         # ROM Bank Number
            print 'Write in interval 0x2000 - 0x3fff'
            self.rom_bank_no = value & 0x7f
            self.update_rom_bank()
        elif offset >= 0x4000 and offset <= 0x5fff:         # RAM Bank Number - Upper Bits of ROM Bank Number
            print 'Write in interval 0x4000 - 0x5fff (RAM Bank Number)'
            if value <= 0b00000011:
                self.set_ram_bank(value)
                self.ram_and_timer_mode = self.RAM_TIMER_RAM
            elif value in [self.RAM_TIMER_RTC_S, self.RAM_TIMER_RTC_M, self.RAM_TIMER_RTC_H, self.RAM_TIMER_RTC_DL, self.RAM_TIMER_RTC_DH]:
                self.ram_and_timer_mode = value
            else:
                raise Exception('Invalid write in interval 0x4000 - 0x5fff')
        elif offset >= 0x6000 and offset <= 0x7fff:         # ROM/RAM mode select
            print 'Write in interval 0x6000 - 0x7fff (ROM/RAM mode select)'
            if value < 2:
                self.rom_ram_mode_select = value
            else:
                raise Exception('Invalid write in interval 0x6000 - 0x7fff')
        elif offset >= 0xa000 and offset <= 0xbfff:         # External RAM / RTC registers
            print 'Write in interval 0xa000 - 0xbfff (External RAM)'
            if not self.ram_and_timer_enable:
                raise Exception('Cannot write in external RAM (RAM disabled)')

            if self.ram_and_timer_mode == self.RAM_TIMER_RAM:
                self.ram_bank[offset - 0xa000] = value
            elif self.ram_and_timer_mode == self.RAM_TIMER_RTC_S:
                self.rtc['S'] = value
            elif self.ram_and_timer_mode == self.RAM_TIMER_RTC_M:
                self.rtc['M'] = value
            elif self.ram_and_timer_mode == self.RAM_TIMER_RTC_H:
                self.rtc['H'] = value
            elif self.ram_and_timer_mode == self.RAM_TIMER_RTC_DL:
                self.rtc['D'] = (self.rtc['D'] & 0xff00) + value
            elif self.ram_and_timer_mode == self.RAM_TIMER_RTC_DH:
                self.rtc['D'] = (self.rtc['D'] & 0x00ff) + (value * 0x100)
        else:
            if value >= 0x00 and value <= 0xff:
                #print 'Scrivo in %04x' % offset
                self.memory[offset] = value
            else:
                raise Exception("Invalid write in memory")

    def __getitem__(self, offset):
        if offset >= 0x0000 and offset <= 0x3fff:
            if offset >= 0x00 and offset <= 0xff:
                return self.boot_rom[offset]
            return self.cartridge.data[offset]
        elif offset >= 0xa000 and offset <= 0xbfff:
            if self.ram_and_timer_mode == self.RAM_TIMER_RAM:
                return self.ram_bank[offset - 0xa000]
            elif self.ram_and_timer_mode == self.RAM_TIMER_RTC_S:
                return self.rtc['S']
            elif self.ram_and_timer_mode == self.RAM_TIMER_RTC_M:
                return self.rtc['M'] 
            elif self.ram_and_timer_mode == self.RAM_TIMER_RTC_H:
                return self.rtc['H']
            elif self.ram_and_timer_mode == self.RAM_TIMER_RTC_DL:
                return self.rtc['D'] & 0x00ff
            elif self.ram_and_timer_mode == self.RAM_TIMER_RTC_DH:
                return (self.rtc['D'] & 0xff00) >> 8
        else:
            return self.memory[offset]
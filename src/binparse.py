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
    def stow(self, end = Endianness.Little):
        if end == Endianness.Little:
            return self.stob() + self.stob()*256
        elif end == Endianness.Big:
            return self.stob()*256 + self.stob()
        else:
            raise Exception("AAAAAH")

    def stod(self, end = Endianness.Little):
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
class Header(object):
    def __init__(self, header):
        if header[:4] != b'NES\x1a':
            exit()
        self.prg_rom_size = header[4] * 0x4000
        self.chr_rom_size = header[5] * 0x2000
        self.mapper_number = header[6] >> 4 | header[7] & 0xf0
        self.has_trainer = header[6] >> 3 & 1


class NesFile(object):
    def __init__(self, prg_rom, chr_rom):
        self.prg_rom = prg_rom
        self.chr_rom = chr_rom

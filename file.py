class Header(object):
    def __init__(self, header):
        if header[:4] != b'NES\x1a':
            exit()
        self.prg_rom_size = header[4] * 0x4000
        self.chr_rom_size = header[5] * 0x2000
        self.mapper_number = header[6] >> 4 | header[7] & 0xf0
        self.vmirroring = header[6] & 1
        self.save_ram = header[6] >> 1 & 1
        self.has_trainer = header[6] >> 2 & 1
        self.four_screen = header[6] >> 3 & 1



class NesFile(object):
    def __init__(self, header, trainer, prg_rom, chr_rom):
        self.header = header
        self.trainer = trainer
        self.prg_rom = prg_rom
        self.chr_rom = chr_rom

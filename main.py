from cpu import Cpu
from file import Header, NesFile
from memory import Memory


class Emulator(object):
    def __init__(self, file_name):
        self.file_name = file_name
        self.nes_file = self.read_nes_file()
        self.save_memory = Memory(0x2000)
        self.main_memory = Memory(0x800)
        self.cpu = Cpu(self.nes_file, self.main_memory, self. save_memory)


    def read_nes_file(self):
        with open(self.file_name, 'rb') as f:
            nes_header = Header(f.read(16))
            if nes_header.has_trainer:
                nes_trainer = f.read(512)
            nes_prg_rom = f.read(nes_header.prg_rom_size)
            nes_chr_rom = f.read(nes_header.chr_rom_size)
            return NesFile(nes_prg_rom, nes_chr_rom)

    def run(self):
        self.cpu.run()


nes = Emulator('nes_files/nestest.nes')
nes.run()

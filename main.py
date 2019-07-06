import pygame
from pygame.locals import *
from sys import exit

from cpu import CPU
from file import Header, NesFile
from memory import Memory
from ppu import PPU
from display import get_pixel


class Emulator(object):
    def __init__(self, file_name):
        self.nes_file = self.read_nes_file(file_name)
        self.main_memory = Memory(0x800)
        self.save_memory = Memory(0x2000)
        self.ppu = PPU(self.nes_file)
        self.cpu = CPU(self.nes_file, self.main_memory, self.save_memory, self.ppu)

    def read_nes_file(self, file_name):
        with open(file_name, 'rb') as f:
            header = Header(f.read(16))
            trainer = f.read(512) if header.has_trainer else 0
            nes_prg_rom = f.read(header.prg_rom_size)
            nes_chr_rom = f.read(header.chr_rom_size)
            return NesFile(header, trainer, nes_prg_rom, nes_chr_rom)

    def run(self):
        self.cpu.run()

    def exec(self):
        self.cpu.exec()

    def disassemble(self):
        self.cpu.disassemble()


pygame.init()
screen = pygame.display.set_mode([256, 240])
nes = Emulator('nes_files/color_test.nes')

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                nes.cpu.input_status[0] = 1
            if event.key == pygame.K_i:
                nes.cpu.input_status[1] = 1
            if event.key == pygame.K_j:
                nes.cpu.input_status[2] = 1
            if event.key == pygame.K_k:
                nes.cpu.input_status[3] = 1
            if event.key == pygame.K_w:
                nes.cpu.input_status[4] = 1
            if event.key == pygame.K_s:
                nes.cpu.input_status[5] = 1
            if event.key == pygame.K_a:
                nes.cpu.input_status[6] = 1
            if event.key == pygame.K_d:
                nes.cpu.input_status[7] = 1
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_u:
                nes.cpu.input_status[0] = 0
            if event.key == pygame.K_i:
                nes.cpu.input_status[1] = 0
            if event.key == pygame.K_j:
                nes.cpu.input_status[2] = 0
            if event.key == pygame.K_k:
                nes.cpu.input_status[3] = 0
            if event.key == pygame.K_w:
                nes.cpu.input_status[4] = 0
            if event.key == pygame.K_s:
                nes.cpu.input_status[5] = 0
            if event.key == pygame.K_a:
                nes.cpu.input_status[6] = 0
            if event.key == pygame.K_d:
                nes.cpu.input_status[7] = 0
    for line in range(4000):
        # print(line+1, ' ', end='')
        # nes.disassemble()
        # nes.ppu.print()
        nes.exec()
    nes.cpu.nmi()
    for i in range(256):
        for j in range(240):
            screen.set_at((i, j), get_pixel(i, j, nes.ppu))
    pygame.display.update()

# nes = Emulator('nes_files/nestest.nes')
# nes.run()

import pygame
from pygame.locals import *
from sys import exit

import numpy as np

from c_cpu import CPU
from file import Header, NesFile
from ppu import PPU
from display import palette_data


class Emulator(object):
    def __init__(self, file_name):
        pygame.init()
        self.screen = pygame.display.set_mode([256, 240])

        self.nes_file = self.read_nes_file(file_name)
        self.main_memory = [0 for _ in range(0x800)]
        self.save_memory = [0 for _ in range(0x2000)]
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
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if event.key == pygame.K_u:
                    self.cpu.input_status[0] = event.type == pygame.KEYDOWN
                if event.key == pygame.K_i:
                    self.cpu.input_status[1] = event.type == pygame.KEYDOWN
                if event.key == pygame.K_j:
                    self.cpu.input_status[2] = event.type == pygame.KEYDOWN
                if event.key == pygame.K_k:
                    self.cpu.input_status[3] = event.type == pygame.KEYDOWN
                if event.key == pygame.K_w:
                    self.cpu.input_status[4] = event.type == pygame.KEYDOWN
                if event.key == pygame.K_s:
                    self.cpu.input_status[5] = event.type == pygame.KEYDOWN
                if event.key == pygame.K_a:
                    self.cpu.input_status[6] = event.type == pygame.KEYDOWN
                if event.key == pygame.K_d:
                    self.cpu.input_status[7] = event.type == pygame.KEYDOWN

        cycles_per_scanline = 341 / 3
        end_of_render = self.cpu.cpu_cycle + (240 + 1) * cycles_per_scanline
        end_of_vblank = end_of_render + 20 * cycles_per_scanline
        end_of_flame = self.cpu.cpu_cycle + 29780.5

        is_8x16_mode = self.ppu.ppu_ctrl.bit5
        sprites_number_per_lines = [0 for _ in range(256 + 16)]
        for index in range(64):
            for y in range(16 if is_8x16_mode else 8):
                # print(self.ppu.oam[index * 4], y)
                sprites_number_per_lines[self.ppu.oam[index * 4] + y] += 1

        # ppu render flame
        for line in range(241):
            end_of_scanline = self.cpu.cpu_cycle + cycles_per_scanline

            # ppu render one scanline
            while self.cpu.cpu_cycle < end_of_scanline:
                self.cpu.exec_op()

            # hblank
            if line == self.ppu.oam[0]:
                self.ppu.ppu_status.bit6 = 1
            if sprites_number_per_lines[line] > 8:
                self.ppu.ppu_status.bit5 = 1
        while self.cpu.cpu_cycle < end_of_render:
            self.cpu.exec_op()

        # vblank
        self.ppu.ppu_status.value |= 0x80
        self.cpu.nmi()
        while self.cpu.cpu_cycle < end_of_vblank:
            self.cpu.exec_op()
        while self.cpu.cpu_cycle < end_of_flame:
            self.cpu.exec_op()

        # end of flame, render and show
        if self.ppu.ppu_mask.bit3:
            self.ppu.render_background_1()
        if self.ppu.ppu_mask.bit4:
            self.ppu.render_sprites()

        pygame.surfarray.blit_array(self.screen, self.ppu.pixels)
        pygame.display.update()

        self.ppu.ppu_status.bit6 = 0
        self.ppu.ppu_status.bit5 = 0


class Debugger(Emulator):
    def __init__(self, file_name):
        super().__init__(file_name)

        self.debugger_screen = pygame.display.set_mode([256 * 2, 240 * 2])
        self.screen = self.debugger_screen.subsurface((0, 0), (256, 240))
        self.palette = self.debugger_screen.subsurface((256, 128), (256, 112))
        self.pattern_tables = self.debugger_screen.subsurface((256, 0), (256, 128))
        self.name_tables = self.debugger_screen.subsurface((0, 240), (256 * 2, 240))

        self.pattern_tables_pixels = np.array([[0 for _ in range(128)] for _ in range(256)])
        self.name_tables_pixels = np.array([[0 for _ in range(240)] for _ in range(256*2)])

    def run(self):
        super().run()

        # pattern_table
        for y in range(128):
            for x in range(128):
                index = y // 8 * 16 + x // 8
                y_offset = y % 8
                p0 = self.ppu.pattern_tables[index * 16 + y_offset]
                p1 = self.ppu.pattern_tables[index * 16 + 8 + y_offset]
                shift = (~x) & 0x7
                mask = 1 << shift
                value = ((p0 & mask) >> shift) | ((p1 & mask) >> shift << 1)
                self.pattern_tables_pixels[x, y] = palette_data[self.ppu.palette[value]]
        for y in range(128):
            for x in range(128):
                index = y // 8 * 16 + x // 8
                y_offset = y % 8
                p0 = self.ppu.pattern_tables[index * 16 + y_offset + 0x1000]
                p1 = self.ppu.pattern_tables[index * 16 + 8 + y_offset + 0x1000]
                shift = (~x) & 0x7
                mask = 1 << shift
                value = ((p0 & mask) >> shift) | ((p1 & mask) >> shift << 1)
                self.pattern_tables_pixels[x + 128, y] = palette_data[self.ppu.palette[value]]

        # palette
        for i in range(32):
            left_top_x, left_top_y = i % 16 * 16, i // 16 * 56
            right_botton_x, right_botton_y = left_top_x + 16, left_top_y + 56
            pygame.draw.rect(self.palette, palette_data[self.ppu.palette[i]],
                             (left_top_x, left_top_y, right_botton_x, right_botton_y))

        # name_tables
        pattern_table_base = 0x1000 if self.ppu.ppu_ctrl.bit4 else 0
        for y in range(240):
            for x in range(256):
                index = y // 8 * 32 + x // 8
                y_offset = y % 8
                pattern_tables_id = self.ppu.name_tables[index]
                p0 = self.ppu.pattern_tables[pattern_tables_id * 16 + y_offset + pattern_table_base]
                p1 = self.ppu.pattern_tables[pattern_tables_id * 16 + 8 + y_offset + pattern_table_base]
                shift = (~x) & 0x7
                mask = 1 << shift
                low = ((p0 & mask) >> shift) | ((p1 & mask) >> shift << 1)
                aid = (x >> 5) + (y >> 5) * 8
                attr = self.ppu.name_tables[aid + (32 * 30)]
                aoffset = ((x & 0x10) >> 3) | ((y & 0x10) >> 2)
                high = (attr & (3 << aoffset)) >> aoffset << 2
                index = high | low
                self.name_tables_pixels[x, y] = palette_data[self.ppu.palette[index]]
        for y in range(240):
            for x in range(256):
                index = y // 8 * 32 + x // 8
                y_offset = y % 8
                pattern_tables_id = self.ppu.name_tables[index + 0x400]
                p0 = self.ppu.pattern_tables[pattern_tables_id * 16 + y_offset + pattern_table_base]
                p1 = self.ppu.pattern_tables[pattern_tables_id * 16 + 8 + y_offset + pattern_table_base]
                shift = (~x) & 0x7
                mask = 1 << shift
                low = ((p0 & mask) >> shift) | ((p1 & mask) >> shift << 1)

                aid = x // 32 + y // 32 * 8
                attr = self.ppu.name_tables[aid + (32 * 30) + 0x400]
                aoffset = ((x & 0x10) >> 3) | ((y & 0x10) >> 2)
                high = (attr & (3 << aoffset)) >> aoffset << 2
                index = high | low
                self.name_tables_pixels[x + 256, y] = palette_data[self.ppu.palette[index]]

        pygame.surfarray.blit_array(self.pattern_tables, self.pattern_tables_pixels)
        pygame.surfarray.blit_array(self.name_tables, self.name_tables_pixels)
        pygame.display.update()



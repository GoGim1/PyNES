from memory import Memory
from register import Register
from display import palette_data
import c_render


class PPU(object):
    def __init__(self, file):
        self.pseudo = 0
        self._vram_addr_write_twice = 0
        self.vmirroring = file.header.vmirroring

        # self.pattern_tables = Memory(0x2000)
        self.pattern_tables = list(file.chr_rom)
        self.name_tables = Memory(0x800)
        self.palette = Memory(0x20)
        self.oam = Memory(256)

        self.ppu_ctrl = Register(0)         # $2000
        self.ppu_mask = Register(0)         # $2001
        self.ppu_status = Register(0)       # $2002
        self.oam_addr = 0                   # $2003
        self.oam_data = 0                   # $2004
        self.ppu_scroll = 0                 # $2005
        self.ppu_addr = 0                   # $2006
        self.ppu_data = 0                   # $2007
        self.oam_dma = 0                    # 4014

    def print(self):
        print(" P_CTRL:" + hex(self.ppu_ctrl.value),
              " P_MASK:" + hex(self.ppu_mask.value),
              " P_STATUS:" + hex(self.ppu_status.value),
              " OAM_ADDR:" + hex(self.oam_addr),
              " P_SCROLL:" + hex(self.ppu_scroll),
              " P_ADDR:" + hex(self.ppu_addr), end=''
              )

    def read_register(self, addr):
        if addr == 0x2002:
            ret = self.ppu_status.value
            self.ppu_status.bit7 = 0
            return ret
        elif addr == 0x2004:
            ret = self.oam[self.oam_addr]
            self.oam_addr += 1
            return ret
        elif addr == 0x2007:
            return self.read_vram()
        else:
            assert 0, "Error address! Can't read PPU register"

    def write_register(self, addr, data):
        if addr == 0x2000:
            self.ppu_ctrl.value = data
        elif addr == 0x2001:
            self.ppu_mask.value = data
        elif addr == 0x2003:
            self.oam_addr = data
        elif addr == 0x2004:
            self.oam[self.oam_addr] = data
            self.oam_addr += 1
        elif addr == 0x2005:
            if self._vram_addr_write_twice & 1:
                self.ppu_scroll = self.ppu_scroll & 0xff00 | data
            else:
                self.ppu_scroll = self.ppu_scroll & 0xff | data << 8
            self._vram_addr_write_twice += 1
        elif addr == 0x2006:
            if self._vram_addr_write_twice & 1:
                self.ppu_addr = self.ppu_addr & 0xff00 | data
            else:
                self.ppu_addr = self.ppu_addr & 0xff | data << 8
            self._vram_addr_write_twice += 1
        elif addr == 0x2007:
            self.write_vram(data)
        else:
            assert 0, "Error address! Can't write PPU register $2002"

    def read_vram(self):
        addr = self.ppu_addr
        self.ppu_addr += (32 if self.ppu_ctrl.bit2 else 1)
        if addr in range(0, 0x3f00):
            ret = self.pseudo
            if addr in range(0, 0x2000):
                self.pseudo = self.pattern_tables[addr]
            else:
                if self.vmirroring:
                    self.pseudo = self.name_tables[addr & 0x7ff]
                else:
                    self.pseudo = self.name_tables[addr & 0x3ff | (addr & 0x800) >> 1]
            return ret
        elif addr in range(0x3f00, 0x4000):
            index = (addr - 0x3f00) % 0x20
            return self.palette[index]
        else:
            assert 0, "Error PPU addr"

    def write_vram(self, data):
        addr = self.ppu_addr
        self.ppu_addr += (32 if self.ppu_ctrl.bit2 else 1)
        if addr in range(0, 0x2000):
            self.pattern_tables[addr] = data
        elif addr in range(0x2000, 0x3000):
            if self.vmirroring:
                self.name_tables[addr & 0x7ff] = data
            else:
                self.name_tables[addr & 0x3ff | (addr & 0x800) >> 1] = data
        elif addr in range(0x3f00, 0x4000):
            index = (addr - 0x3f00) % 0x20
            if index % 4:
                self.palette[index] = data
            elif index == 0 or index == 0x10:
                self.palette[::4] = [data for _ in range(8)]
            # print(self.palette.memory)
        else:
            assert 0, "Error PPU addr"

    def render_sprites(self, screen):
        pattern_base = 0x1000 if self.ppu_ctrl.bit3 else 0
        is_8x16_mode = self.ppu_ctrl.bit5
        for i in range(63, -1, -1):
            data = self.oam[i * 4: i * 4 + 4]
            x, y, attr, pattern_index = data[3], data[0] + 1, data[2], data[1]
            if y > 0xEF:
                continue
            if is_8x16_mode:
                pattern1 = pattern_index // 2 * 0x20 + (0 if x % 2 else 0x1000)
                pattern2 = pattern1 + 16
            else:
                pattern1 = pattern_base | pattern_index * 16
                pattern2 = pattern_base | pattern1 + 8

            high = (attr & 3) << 2
            for yy in range(16 if is_8x16_mode else 8):
                for xx in range(8):
                    p0 = self.pattern_tables[pattern1 + yy]
                    p1 = self.pattern_tables[pattern2 + yy]

                    shift = (~xx) & 0x7
                    mask = 1 << shift

                    low = ((p0 & mask) >> shift) | ((p1 & mask) >> shift << 1)
                    if low == 0:
                        continue
                    screen[x + xx, y + yy] = palette_data[self.palette[0x10 + high | low]]

    def render_background(self, pixels):
        name_table_index = 0  # TODO
        pattern_base = 0x1000 if self.ppu_ctrl.bit4 else 0

        for y in range(240):
            for x in range(256):
                tile_id = (x >> 3) + (y >> 3) * 32
                pattern_tables_id = self.name_tables[tile_id + name_table_index * 0x400]

                pattern1 = pattern_tables_id * 16 | pattern_base
                pattern2 = pattern1 + 8 | pattern_base

                offset = y & 0x7
                p0 = self.pattern_tables[pattern1 + offset]
                p1 = self.pattern_tables[pattern2 + offset]

                shift = (~x) & 0x7
                mask = 1 << shift

                low = ((p0 & mask) >> shift) | ((p1 & mask) >> shift << 1)

                aid = (x >> 5) + (y >> 5) * 8
                attr = self.name_tables[name_table_index * 0x400 + aid + (32 * 30)]

                aoffset = ((x & 0x10) >> 3) | ((y & 0x10) >> 2)
                high = (attr & (3 << aoffset)) >> aoffset << 2

                index = high | low

                pixels[x, y] = palette_data[self.palette[index]]

        # name_table_index = 0  # TODO
        # pattern_base = 0x1000 if self.ppu_ctrl.bit4 else 0

    def render_background_1(self, pixels):
        c_render.render_background_cython(self.pattern_tables, self.name_tables, self.palette, self.ppu_ctrl.bit4, pixels)

        # name_table_index = 0  # TODO
        # pattern_base = 0x1000 if self.ppu_ctrl.bit4 else 0

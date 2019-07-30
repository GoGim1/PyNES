from memory import Memory
from register import Register


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


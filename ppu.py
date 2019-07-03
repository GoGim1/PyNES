from memory import Memory

_0_bit_ = 0x1
_1_bit_ = 0x2
_2_bit_ = 0x4
_3_bit_ = 0x8
_4_bit_ = 0x10
_5_bit_ = 0x20
_6_bit_ = 0x40
_7_bit_ = 0x80



class Register(object):
    def __init__(self, data=0):
        self._value = data

    def value(self):
        return self._value

    def set(self, data):
        self._value = data

    def bit0(self):
        return self._value >> 0 & 0x1

    def bit1(self):
        return self._value >> 1 & 0x1

    def bit2(self):
        return self._value >> 2 & 0x1

    def bit3(self):
        return self._value >> 3 & 0x1

    def bit4(self):
        return self._value >> 4 & 0x1

    def bit5(self):
        return self._value >> 5 & 0x1

    def bit6(self):
        return self._value >> 6 & 0x1

    def bit7(self):
        return self._value >> 7 & 0x1


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
        self.ppu_status = Register(0x00)    # $2002
        self.oam_addr = 0                   # $2003
        self.oam_data = 0                   # $2004
        self.ppu_scroll = 0                 # $2005
        self.ppu_addr = 0                   # $2006
        self.ppu_data = 0                   # $2007
        self.oam_dma = 0                    # 4014

    def print(self):
        print(" P_CTRL:" + hex(self.ppu_ctrl.value()),
              " P_MASK:" + hex(self.ppu_mask.value()),
              " P_STATUS:" + hex(self.ppu_status.value()),
              " OAM_ADDR:" + hex(self.oam_addr),
              " P_SCROLL:" + hex(self.ppu_scroll),
              " P_ADDR:" + hex(self.ppu_addr),
              )

    def read_register(self, addr):
        if addr == 0x2002:
            ret = self.ppu_status.value()
            # self.ppu_status.set(ret & 0x7f)
            return ret
        elif addr == 0x2004:
            ret = self.oam.read(self.oam_addr)
            self.oam_addr += 1
            return ret
        elif addr == 0x2007:
            return self.read_vram()
        else:
            assert 0, "Error address! Can't read PPU register"

    def write_register(self, addr, data):
        if addr == 0x2000:
            self.ppu_ctrl.set(data)
        elif addr == 0x2001:
            self.ppu_mask.set(data)
        elif addr == 0x2003:
            self.oam_addr = data
        elif addr == 0x2004:
            self.oam.write(self.oam_addr, data)
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
        self.ppu_addr += (32 if (self.ppu_ctrl.bit2()) else 1)
        if addr in range(0, 0x3f00):
            ret = self.pseudo
            if addr in range(0, 0x2000):
                assert 0, "TODO"
                # TODO: self.pseudo = self.pattern_tables.read(addr)
            else:
                if self.vmirroring:
                    self.pseudo = self.name_tables.read(addr & 0x7ff)
                else:
                    self.pseudo = self.name_tables.read(addr & 0x3ff | (addr & 0x800) >> 1)
            return ret
        elif addr in range(0x3f00, 0x4000):
            return self.palette.read(addr & 0x1f)
        else:
            assert 0, "Error PPU addr"

    def write_vram(self, data):
        addr = self.ppu_addr
        self.ppu_addr += (32 if (self.ppu_ctrl.bit2()) else 1)
        if addr in range(0, 0x2000):
            self.pattern_tables[addr] = data
        elif addr in range(0x2000, 0x3000):
            if self.vmirroring:
                self.name_tables.write(addr & 0x7ff, data)
            else:
                self.name_tables.write(addr & 0x3ff | (addr & 0x800) >> 1, data)
        elif addr in range(0x3f00, 0x4000):
            if addr & 0x03:
                self.palette.write(addr & 0x1f, data)
            else:
                offset = addr & 0xf
                self.palette.write(offset, data)
                self.palette.write(offset | 0x10, data)
        else:
            assert 0, "Error PPU addr"


class Register(object):
    def __init__(self, data=0):
        self.data = data

    def __str__(self):
        return hex(self.data)

    @property
    def value(self):
        return self.data

    @value.setter
    def value(self, data):
        self.data = data

    @property
    def bit0(self):
        return self.data & 1

    @bit0.setter
    def bit0(self, data):
        if data:
            self.data |= 1
        else:
            self.data &= 0xfe

    @property
    def bit1(self):
        return self.data >> 1 & 1
    @bit1.setter
    def bit1(self, data):
        if data:
            self.data |= 2
        else:
            self.data &= 0xfd

    @property
    def bit2(self):
        return self.data >> 2 & 1

    @bit2.setter
    def bit2(self, data):
        if data:
            self.data |= 4
        else:
            self.data &= 0xfb

    @property
    def bit3(self):
        return self.data >> 3 & 1

    @bit3.setter
    def bit3(self, data):
        if data:
            self.data |= 8
        else:
            self.data &= 0xf7

    @property
    def bit4(self):
        return self.data >> 4 & 1

    @bit4.setter
    def bit4(self, data):
        if data:
            self.data |= 0x10
        else:
            self.data &= 0xef

    @property
    def bit5(self):
        return self.data >> 5 & 1

    @bit5.setter
    def bit5(self, data):
        if data:
            self.data |= 0x20
        else:
            self.data &= 0xdf

    @property
    def bit6(self):
        return self.data >> 6 & 1

    @bit6.setter
    def bit6(self, data):
        if data:
            self.data |= 0x40
        else:
            self.data &= 0xbf

    @property
    def bit7(self):
        return self.data >> 7 & 1

    @bit7.setter
    def bit7(self, data):
        if data:
            self.data |= 0x80
        else:
            self.data &= 0x7f

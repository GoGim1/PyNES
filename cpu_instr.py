def JMP(mode, cpu, addr):
    cpu.program_counter = addr


def LDX(mode, cpu, addr):
    cpu.x_index_register = cpu.read(addr)
    cpu.status_register.bit7 = 1 if (cpu.x_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.x_index_register == 0) else 0


def LAX(mode, cpu, addr):
    value = cpu.read(addr)
    cpu.accumulator = cpu.x_index_register = value
    cpu.status_register.bit7 = 1 if (value & 0x80) else 0
    cpu.status_register.bit1 = 1 if (value == 0) else 0


def LDY(mode, cpu, addr):
    addr = cpu.read(addr)
    cpu.y_index_register = addr
    cpu.status_register.bit7 = 1 if (cpu.y_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.y_index_register == 0) else 0

def LAY(mode, cpu, addr):
    value = cpu.read(addr)
    cpu.accumulator = cpu.y_index_register = value
    cpu.status_register.bit7 = 1 if (value & 0x80) else 0
    cpu.status_register.bit1 = 1 if (value == 0) else 0


def STX(mode, cpu, addr):
    cpu.write(addr, cpu.x_index_register)


def SAX(mode, cpu, addr):
    cpu.write(addr, cpu.x_index_register & cpu.accumulator)


def STY(mode, cpu, addr):
    cpu.write(addr, cpu.y_index_register)


def ADC(mode, cpu, addr):
    addr = cpu.read(addr)
    result = addr + cpu.accumulator + (1 if cpu.status_register.bit0 else 0)
    cpu.status_register.bit0 = 1 if (result >> 8) else 0
    result &= 0xff
    cpu.status_register.bit6 = 1 if (
            not ((cpu.accumulator ^ addr) & 0x80) and ((cpu.accumulator ^ result) & 0x80)) else 0
    cpu.accumulator = result
    cpu.status_register.bit7 = 1 if (result & 0x80) else 0
    cpu.status_register.bit1 = 1 if (result == 0) else 0


def SBC(mode, cpu, addr):
    addr = cpu.read(addr)
    result = cpu.accumulator - addr - (0 if cpu.status_register.bit0 else 1)
    cpu.status_register.bit0 = result >= 0
    result &= 0xff
    cpu.status_register.bit6 = 1 if (
            ((cpu.accumulator ^ addr) & 0x80) and ((cpu.accumulator ^ result) & 0x80)) else 0
    cpu.accumulator = result
    cpu.status_register.bit7 = 1 if (result & 0x80) else 0
    cpu.status_register.bit1 = 1 if (result == 0) else 0


def INC(mode, cpu, addr):
    value = cpu.read(addr)
    value += 1
    value &= 0xff
    cpu.write(addr, value)
    cpu.status_register.bit7 = 1 if (value & 0x80) else 0
    cpu.status_register.bit1 = 1 if (value == 0) else 0


def DEC(mode, cpu, addr):
    value = cpu.read(addr)
    value -= 1
    value &= 0xff
    cpu.write(addr, value)
    cpu.status_register.bit7 = 1 if (value & 0x80) else 0
    cpu.status_register.bit1 = 1 if (value == 0) else 0


def INX(mode, cpu, addr):
    cpu.x_index_register += 1
    cpu.x_index_register &= 0xff
    cpu.status_register.bit7 = 1 if (cpu.x_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.x_index_register == 0) else 0


def DEX(mode, cpu, addr):
    cpu.x_index_register -= 1
    cpu.x_index_register &= 0xff
    cpu.status_register.bit7 = 1 if (cpu.x_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.x_index_register == 0) else 0


def INY(mode, cpu, addr):
    cpu.y_index_register += 1
    cpu.y_index_register &= 0xff
    cpu.status_register.bit7 = 1 if (cpu.y_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.y_index_register == 0) else 0


def DEY(mode, cpu, addr):
    cpu.y_index_register -= 1
    cpu.y_index_register &= 0xff
    cpu.status_register.bit7 = 1 if (cpu.y_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.y_index_register == 0) else 0


def TAX(mode, cpu, addr):
    cpu.x_index_register = cpu.accumulator
    cpu.status_register.bit7 = 1 if (cpu.x_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.x_index_register == 0) else 0


def TAY(mode, cpu, addr):
    cpu.y_index_register = cpu.accumulator
    cpu.status_register.bit7 = 1 if (cpu.y_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.y_index_register == 0) else 0


def TXA(mode, cpu, addr):
    cpu.accumulator = cpu.x_index_register
    cpu.status_register.bit7 = 1 if (cpu.x_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.x_index_register == 0) else 0


def TYA(mode, cpu, addr):
    cpu.accumulator = cpu.y_index_register
    cpu.status_register.bit7 = 1 if (cpu.y_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.y_index_register == 0) else 0


def TSX(mode, cpu, addr):
    cpu.x_index_register = cpu.stack_pointer
    cpu.status_register.bit7 = 1 if (cpu.x_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.x_index_register == 0) else 0


def TXS(mode, cpu, addr):
    cpu.stack_pointer = cpu.x_index_register


def JSR(mode, cpu, addr):
    cpu.program_counter -= 1
    cpu.push(cpu.program_counter >> 8)
    cpu.push(cpu.program_counter & 0xff)
    cpu.program_counter = addr


def RTS(mode, cpu, addr):
    cpu.program_counter = cpu.pop()
    cpu.program_counter |= cpu.pop() << 8
    cpu.program_counter += 1


def RTI(mode, cpu, addr):
    cpu.status_register.value = cpu.pop() | 0x20
    cpu.status_register.bit4 = 0
    cpu.status_register.bit5 = 1
    cpu.program_counter = cpu.pop()
    cpu.program_counter |= cpu.pop() << 8


def SEC(mode, cpu, addr):
    cpu.status_register.bit0 = 1


def SEI(mode, cpu, addr):
    cpu.status_register.bit2 = 1


def SED(mode, cpu, addr):
    cpu.status_register.bit3 = 1


def CLD(mode, cpu, addr):
    cpu.status_register.bit3 = 0


def CLV(mode, cpu, addr):
    cpu.status_register.bit6 = 0


def BCS(mode, cpu, addr):
    if cpu.status_register.bit0:
        cpu.program_counter = addr


def CLC(mode, cpu, addr):
    cpu.status_register.bit0 = 0


def NOP(mode, cpu, addr):
    pass


def BCC(mode, cpu, addr):
    if not cpu.status_register.bit0:
        cpu.program_counter = addr


def LDA(mode, cpu, addr):
    cpu.accumulator = cpu.read(addr)
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


def STA(mode, cpu, addr):
    cpu.write(addr, cpu.accumulator)


def BEQ(mode, cpu, addr):
    if cpu.status_register.bit1:
        cpu.program_counter = addr


def BNE(mode, cpu, addr):
    if not cpu.status_register.bit1:
        cpu.program_counter = addr


def BIT(mode, cpu, addr):
    value = cpu.read(addr)
    cpu.status_register.bit6 = (value >> 6) & 1
    cpu.status_register.bit7 = (value >> 7) & 1
    cpu.status_register.bit1 = 0 if (cpu.accumulator & value) else 1


def BVS(mode, cpu, addr):
    if cpu.status_register.bit6:
        cpu.program_counter = addr


def BVC(mode, cpu, addr):
    if not cpu.status_register.bit6:
        cpu.program_counter = addr


def BMI(mode, cpu, addr):
    if cpu.status_register.bit7:
        cpu.program_counter = addr


def BPL(mode, cpu, addr):
    if not cpu.status_register.bit7:
        cpu.program_counter = addr


def PHA(mode, cpu, addr):
    cpu.push(cpu.accumulator)


def PLA(mode, cpu, addr):
    cpu.accumulator = cpu.pop()
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


def PHP(mode, cpu, addr):
    cpu.push(cpu.status_register.value | 0x10)


def PLP(mode, cpu, addr):
    cpu.status_register.value = cpu.pop() | 0x20
    cpu.status_register.bit4 = 0


def AND(mode, cpu, addr):
    cpu.accumulator &= cpu.read(addr)
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


def ORA(mode, cpu, addr):
    cpu.accumulator |= cpu.read(addr)
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


def EOR(mode, cpu, addr):
    cpu.accumulator ^= cpu.read(addr)
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


def CMP(mode, cpu, addr):
    result = cpu.accumulator - cpu.read(addr)
    cpu.status_register.bit0 = result >= 0
    cpu.status_register.bit7 = 1 if (result & 0x80) else 0
    cpu.status_register.bit1 = 1 if (result == 0) else 0


def CPX(mode, cpu, addr):
    addr = cpu.read(addr)
    result = cpu.x_index_register - addr
    cpu.status_register.bit0 = result >= 0
    cpu.status_register.bit7 = 1 if (result & 0x80) else 0
    cpu.status_register.bit1 = 1 if (result == 0) else 0


def CPY(mode, cpu, addr):
    addr = cpu.read(addr)
    result = cpu.y_index_register - addr
    cpu.status_register.bit0 = result >= 0
    cpu.status_register.bit7 = 1 if (result & 0x80) else 0
    cpu.status_register.bit1 = 1 if (result == 0) else 0


def LSR(mode, cpu, addr):
    if mode == 1:
        cpu.status_register.bit0 = 1 if (cpu.accumulator & 1) else 0
        cpu.accumulator >>= 1
        cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
        cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0
    else:
        value = cpu.read(addr)
        cpu.status_register.bit0 = 1 if (value & 1) else 0
        value >>= 1
        cpu.write(addr, value)
        cpu.status_register.bit7 = 1 if (value & 0x80) else 0
        cpu.status_register.bit1 = 1 if (value == 0) else 0


def ROR(mode, cpu, addr):
    value = cpu.accumulator
    if mode != 1:
        value = cpu.read(addr)
    if cpu.status_register.bit0:
        value |= 0x100
    cpu.status_register.bit0 = value & 1
    value >>= 1
    value &= 0xff
    cpu.status_register.bit7 = 1 if (value & 0x80) else 0
    cpu.status_register.bit1 = 1 if (value == 0) else 0
    if mode == 1:
        cpu.accumulator = value
    else:
        cpu.write(addr, value)


def ROL(mode, cpu, addr):
    value = cpu.accumulator
    if 1 != mode:
        value = cpu.read(addr)
    value <<= 1
    if cpu.status_register.bit0:
        value |= 0x1
    cpu.status_register.bit0 = value > 0xff
    value &= 0xff
    cpu.status_register.bit7 = 1 if (value & 0x80) else 0
    cpu.status_register.bit1 = 1 if (value == 0) else 0
    if mode == 1:
        cpu.accumulator = value
    else:
        cpu.write(addr, value)


def ASL(mode, cpu, addr):
    if mode == 1:
        cpu.status_register.bit0 = 1 if (cpu.accumulator >> 7) else 0
        cpu.accumulator <<= 1
        cpu.accumulator &= 0xff
        cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
        cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0
    else:
        value = cpu.read(addr)
        cpu.status_register.bit0 = 1 if (value >> 7) else 0
        value <<= 1
        value &= 0xff
        cpu.write(addr, value)
        cpu.status_register.bit7 = 1 if (value & 0x80) else 0
        cpu.status_register.bit1 = 1 if (value == 0) else 0


def DCP(mode, cpu, addr):
    value = (cpu.read(addr) - 1) & 0xff
    cpu.write(addr, value)
    result = cpu.accumulator - value
    cpu.status_register.bit0 = result >= 0
    cpu.status_register.bit7 = 1 if (result & 0x80) else 0
    cpu.status_register.bit1 = 1 if (result == 0) else 0


def ISC(mode, cpu, addr):
    value = (cpu.read(addr) + 1) & 0xff
    cpu.write(addr, value)
    result = cpu.accumulator - value - (0 if cpu.status_register.bit0 else 1)

    cpu.status_register.bit0 = result >= 0
    result &= 0xff
    cpu.status_register.bit6 = 1 if (
            ((cpu.accumulator ^ addr) & 0x80) and ((cpu.accumulator ^ result) & 0x80)) else 0
    cpu.accumulator = result
    cpu.status_register.bit7 = 1 if (result & 0x80) else 0
    cpu.status_register.bit1 = 1 if (result == 0) else 0


def SLO(mode, cpu, addr):
    value = cpu.read(addr)
    cpu.status_register.bit0 = 1 if (value >> 7) else 0
    value <<= 1
    value &= 0xff
    cpu.write(addr, value)
    cpu.accumulator |= value
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


def SRE(mode, cpu, addr):
    value = cpu.read(addr)
    cpu.status_register.bit0 = 1 if (value & 1) else 0
    value >>= 1
    cpu.write(addr, value)
    cpu.accumulator ^= value
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


def RLA(mode, cpu, addr):
    value = cpu.read(addr)
    value <<= 1
    if cpu.status_register.bit0:
        value |= 0x1
    cpu.status_register.bit0 = 1 if (value > 0xff) else 0
    cpu.write(addr, value & 0xff)
    cpu.accumulator &= (value & 0xff)
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


def RRA(mode, cpu, addr):
    value = cpu.read(addr)
    if cpu.status_register.bit0:
        value |= 0x100
    cpu.status_register.bit0 = value & 1
    value >>= 1
    value &= 0xff
    cpu.write(addr, value)

    value2 = cpu.accumulator + value + (1 if cpu.status_register.bit0 else 0)
    cpu.status_register.bit0 = 1 if (value2 >> 8) else 0
    value2 &= 0xff
    cpu.status_register.bit6 = 1 if (
            not ((cpu.accumulator ^ value) & 0x80) and ((cpu.accumulator ^ value2) & 0x80)) else 0
    cpu.accumulator = value2
    cpu.status_register.bit7 = 1 if (value2 & 0x80) else 0
    cpu.status_register.bit1 = 1 if (value2 == 0) else 0


def BRK(mode, cpu, addr):
    cpu.program_counter += 1
    cpu.push(cpu.program_counter >> 8)
    cpu.push(cpu.program_counter & 0xFF)
    cpu.push(cpu.status_register.value)
    cpu.program_counter |= cpu.read(cpu._IRQ + 1) << 8

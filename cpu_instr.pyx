cpdef void JMP(int mode, cpu, int addr):
    cpu.program_counter = addr


cpdef void LDX(int mode, cpu, int addr):
    cpu.x_index_register = cpu.read(addr)
    cpu.status_register.bit7 = 1 if (cpu.x_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.x_index_register == 0) else 0


cpdef void LAX(int mode, cpu, int addr):
    value = cpu.read(addr)
    cpu.accumulator = cpu.x_index_register = value
    cpu.status_register.bit7 = 1 if (value & 0x80) else 0
    cpu.status_register.bit1 = 1 if (value == 0) else 0


cpdef void LDY(int mode, cpu, int addr):
    addr = cpu.read(addr)
    cpu.y_index_register = addr
    cpu.status_register.bit7 = 1 if (cpu.y_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.y_index_register == 0) else 0


cpdef void LAY(int mode, cpu, int addr):
    value = cpu.read(addr)
    cpu.accumulator = cpu.y_index_register = value
    cpu.status_register.bit7 = 1 if (value & 0x80) else 0
    cpu.status_register.bit1 = 1 if (value == 0) else 0


cpdef void STX(int mode, cpu, int addr):
    cpu.write(addr, cpu.x_index_register)


cpdef void SAX(int mode, cpu, int addr):
    cpu.write(addr, cpu.x_index_register & cpu.accumulator)


cpdef void STY(int mode, cpu, int addr):
    cpu.write(addr, cpu.y_index_register)


cpdef void ADC(int mode, cpu, int addr):
    addr = cpu.read(addr)
    result = addr + cpu.accumulator + (1 if cpu.status_register.bit0 else 0)
    cpu.status_register.bit0 = 1 if (result >> 8) else 0
    result &= 0xff
    cpu.status_register.bit6 = 1 if (
            not ((cpu.accumulator ^ addr) & 0x80) and ((cpu.accumulator ^ result) & 0x80)) else 0
    cpu.accumulator = result
    cpu.status_register.bit7 = 1 if (result & 0x80) else 0
    cpu.status_register.bit1 = 1 if (result == 0) else 0


cpdef void SBC(int mode, cpu, int addr):
    addr = cpu.read(addr)
    result = cpu.accumulator - addr - (0 if cpu.status_register.bit0 else 1)
    cpu.status_register.bit0 = result >= 0
    result &= 0xff
    cpu.status_register.bit6 = 1 if (
            ((cpu.accumulator ^ addr) & 0x80) and ((cpu.accumulator ^ result) & 0x80)) else 0
    cpu.accumulator = result
    cpu.status_register.bit7 = 1 if (result & 0x80) else 0
    cpu.status_register.bit1 = 1 if (result == 0) else 0


cpdef void INC(int mode, cpu, int addr):
    value = cpu.read(addr)
    value += 1
    value &= 0xff
    cpu.write(addr, value)
    cpu.status_register.bit7 = 1 if (value & 0x80) else 0
    cpu.status_register.bit1 = 1 if (value == 0) else 0


cpdef void DEC(int mode, cpu, int addr):
    value = cpu.read(addr)
    value -= 1
    value &= 0xff
    cpu.write(addr, value)
    cpu.status_register.bit7 = 1 if (value & 0x80) else 0
    cpu.status_register.bit1 = 1 if (value == 0) else 0


cpdef void INX(int mode, cpu, int addr):
    cpu.x_index_register += 1
    cpu.x_index_register &= 0xff
    cpu.status_register.bit7 = 1 if (cpu.x_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.x_index_register == 0) else 0


cpdef void DEX(int mode, cpu, int addr):
    cpu.x_index_register -= 1
    cpu.x_index_register &= 0xff
    cpu.status_register.bit7 = 1 if (cpu.x_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.x_index_register == 0) else 0


cpdef void INY(int mode, cpu, int addr):
    cpu.y_index_register += 1
    cpu.y_index_register &= 0xff
    cpu.status_register.bit7 = 1 if (cpu.y_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.y_index_register == 0) else 0


cpdef void DEY(int mode, cpu, int addr):
    cpu.y_index_register -= 1
    cpu.y_index_register &= 0xff
    cpu.status_register.bit7 = 1 if (cpu.y_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.y_index_register == 0) else 0


cpdef void TAX(int mode, cpu, int addr):
    cpu.x_index_register = cpu.accumulator
    cpu.status_register.bit7 = 1 if (cpu.x_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.x_index_register == 0) else 0


cpdef void TAY(int mode, cpu, int addr):
    cpu.y_index_register = cpu.accumulator
    cpu.status_register.bit7 = 1 if (cpu.y_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.y_index_register == 0) else 0


cpdef void TXA(int mode, cpu, int addr):
    cpu.accumulator = cpu.x_index_register
    cpu.status_register.bit7 = 1 if (cpu.x_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.x_index_register == 0) else 0


cpdef void TYA(int mode, cpu, int addr):
    cpu.accumulator = cpu.y_index_register
    cpu.status_register.bit7 = 1 if (cpu.y_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.y_index_register == 0) else 0


cpdef void TSX(int mode, cpu, int addr):
    cpu.x_index_register = cpu.stack_pointer
    cpu.status_register.bit7 = 1 if (cpu.x_index_register & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.x_index_register == 0) else 0


cpdef void TXS(int mode, cpu, int addr):
    cpu.stack_pointer = cpu.x_index_register


cpdef void JSR(int mode, cpu, int addr):
    cpu.program_counter -= 1
    cpu.push(cpu.program_counter >> 8)
    cpu.push(cpu.program_counter & 0xff)
    cpu.program_counter = addr


cpdef void RTS(int mode, cpu, int addr):
    cpu.program_counter = cpu.pop()
    cpu.program_counter |= cpu.pop() << 8
    cpu.program_counter += 1


cpdef void RTI(int mode, cpu, int addr):
    cpu.status_register.value = cpu.pop() | 0x20
    cpu.status_register.bit4 = 0
    cpu.status_register.bit5 = 1
    cpu.program_counter = cpu.pop()
    cpu.program_counter |= cpu.pop() << 8


cpdef void SEC(int mode, cpu, int addr):
    cpu.status_register.bit0 = 1


cpdef void SEI(int mode, cpu, int addr):
    cpu.status_register.bit2 = 1


cpdef void SED(int mode, cpu, int addr):
    cpu.status_register.bit3 = 1


cpdef void CLD(int mode, cpu, int addr):
    cpu.status_register.bit3 = 0


cpdef void CLV(int mode, cpu, int addr):
    cpu.status_register.bit6 = 0


cpdef void BCS(int mode, cpu, int addr):
    if cpu.status_register.bit0:
        cpu.cpu_cycle += 2 if cpu.program_counter >> 8 != addr >> 8 else 1
        cpu.program_counter = addr


cpdef void CLC(int mode, cpu, int addr):
    cpu.status_register.bit0 = 0


cpdef void NOP(int mode, cpu, int addr):
    pass


cpdef void BCC(int mode, cpu, int addr):
    if not cpu.status_register.bit0:
        cpu.cpu_cycle += 2 if cpu.program_counter >> 8 != addr >> 8 else 1
        cpu.program_counter = addr


cpdef void LDA(int mode, cpu, int addr):
    cpu.accumulator = cpu.read(addr)
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0

cpdef void STA(int mode, cpu, int addr):
    cpu.write(addr, cpu.accumulator)


cpdef void BEQ(int mode, cpu, int addr):
    if cpu.status_register.bit1:
        cpu.cpu_cycle += 2 if cpu.program_counter >> 8 != addr >> 8 else 1
        cpu.program_counter = addr


cpdef void BNE(int mode, cpu, int addr):
    if not cpu.status_register.bit1:
        cpu.cpu_cycle += 2 if cpu.program_counter >> 8 != addr >> 8 else 1
        cpu.program_counter = addr


cpdef void BIT(int mode, cpu, int addr):
    value = cpu.read(addr)
    cpu.status_register.bit6 = (value >> 6) & 1
    cpu.status_register.bit7 = (value >> 7) & 1
    cpu.status_register.bit1 = 0 if (cpu.accumulator & value) else 1


cpdef void BVS(int mode, cpu, int addr):
    if cpu.status_register.bit6:
        cpu.cpu_cycle += 2 if cpu.program_counter >> 8 != addr >> 8 else 1
        cpu.program_counter = addr


cpdef void BVC(int mode, cpu, int addr):
    if not cpu.status_register.bit6:
        cpu.cpu_cycle += 2 if cpu.program_counter >> 8 != addr >> 8 else 1
        cpu.program_counter = addr


cpdef void BMI(int mode, cpu, int addr):
    if cpu.status_register.bit7:
        cpu.cpu_cycle += 2 if cpu.program_counter >> 8 != addr >> 8 else 1
        cpu.program_counter = addr


cpdef void BPL(int mode, cpu, int addr):
    if not cpu.status_register.bit7:
        cpu.cpu_cycle += 2 if cpu.program_counter >> 8 != addr >> 8 else 1
        cpu.program_counter = addr


cpdef void PHA(int mode, cpu, int addr):
    cpu.push(cpu.accumulator)


cpdef void PLA(int mode, cpu, int addr):
    cpu.accumulator = cpu.pop()
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


cpdef void PHP(int mode, cpu, int addr):
    cpu.push(cpu.status_register.value | 0x10)


cpdef void PLP(int mode, cpu, int addr):
    cpu.status_register.value = cpu.pop() | 0x20
    cpu.status_register.bit4 = 0


cpdef void AND(int mode, cpu, int addr):
    cpu.accumulator &= cpu.read(addr)
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


cpdef void ORA(int mode, cpu, int addr):
    cpu.accumulator |= cpu.read(addr)
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


cpdef void EOR(int mode, cpu, int addr):
    cpu.accumulator ^= cpu.read(addr)
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


cpdef void CMP(int mode, cpu, int addr):
    result = cpu.accumulator - cpu.read(addr)
    cpu.status_register.bit0 = result >= 0
    cpu.status_register.bit7 = 1 if (result & 0x80) else 0
    cpu.status_register.bit1 = 1 if (result == 0) else 0


cpdef void CPX(int mode, cpu, int addr):
    addr = cpu.read(addr)
    result = cpu.x_index_register - addr
    cpu.status_register.bit0 = result >= 0
    cpu.status_register.bit7 = 1 if (result & 0x80) else 0
    cpu.status_register.bit1 = 1 if (result == 0) else 0


cpdef void CPY(int mode, cpu, int addr):
    addr = cpu.read(addr)
    result = cpu.y_index_register - addr
    cpu.status_register.bit0 = result >= 0
    cpu.status_register.bit7 = 1 if (result & 0x80) else 0
    cpu.status_register.bit1 = 1 if (result == 0) else 0


cpdef void LSR(int mode, cpu, int addr):
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


cpdef void ROR(int mode, cpu, int addr):
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


cpdef void ROL(int mode, cpu, int addr):
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


cpdef void ASL(int mode, cpu, int addr):
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


cpdef void DCP(int mode, cpu, int addr):
    value = (cpu.read(addr) - 1) & 0xff
    cpu.write(addr, value)
    result = cpu.accumulator - value
    cpu.status_register.bit0 = result >= 0
    cpu.status_register.bit7 = 1 if (result & 0x80) else 0
    cpu.status_register.bit1 = 1 if (result == 0) else 0


cpdef void ISC(int mode, cpu, int addr):
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


cpdef void SLO(int mode, cpu, int addr):
    value = cpu.read(addr)
    cpu.status_register.bit0 = 1 if (value >> 7) else 0
    value <<= 1
    value &= 0xff
    cpu.write(addr, value)
    cpu.accumulator |= value
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


cpdef void SRE(int mode, cpu, int addr):
    value = cpu.read(addr)
    cpu.status_register.bit0 = 1 if (value & 1) else 0
    value >>= 1
    cpu.write(addr, value)
    cpu.accumulator ^= value
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


cpdef void RLA(int mode, cpu, int addr):
    value = cpu.read(addr)
    value <<= 1
    if cpu.status_register.bit0:
        value |= 0x1
    cpu.status_register.bit0 = 1 if (value > 0xff) else 0
    cpu.write(addr, value & 0xff)
    cpu.accumulator &= (value & 0xff)
    cpu.status_register.bit7 = 1 if (cpu.accumulator & 0x80) else 0
    cpu.status_register.bit1 = 1 if (cpu.accumulator == 0) else 0


cpdef void RRA(int mode, cpu, int addr):
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


cpdef void BRK(int mode, cpu, int addr):
    cpu.program_counter += 1
    cpu.push(cpu.program_counter >> 8)
    cpu.push(cpu.program_counter & 0xFF)
    cpu.push(cpu.status_register.value)
    cpu.program_counter |= cpu.read(cpu._IRQ + 1) << 8

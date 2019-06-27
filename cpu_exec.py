def JMP(mode, cpu, addr):
    cpu.program_counter = addr


def LDX(mode, cpu, addr):
    cpu.x_index_register = cpu.read(addr)
    cpu.status_register.check_zs_flag(cpu.x_index_register)


def LAX(mode, cpu, addr):
    value = cpu.read(addr)
    cpu.accumulator = cpu.x_index_register = value
    cpu.status_register.check_zs_flag(value)


def LDY(mode, cpu, addr):
    addr = cpu.read(addr)
    cpu.y_index_register = addr
    cpu.status_register.check_zs_flag(cpu.y_index_register)


def LAY(mode, cpu, addr):
    value = cpu.read(addr)
    cpu.accumulator = cpu.y_index_register = value
    cpu.status_register.check_zs_flag(value)


def STX(mode, cpu, addr):
    cpu.write(addr, cpu.x_index_register)


def SAX(mode, cpu, addr):
    cpu.write(addr, cpu.x_index_register & cpu.accumulator)


def STY(mode, cpu, addr):
    cpu.write(addr, cpu.y_index_register)


def ADC(mode, cpu, addr):
    addr = cpu.read(addr)
    result = addr + cpu.accumulator + (1 if cpu.status_register.carry_flag else 0)
    cpu.status_register.carry_flag = 1 if (result >> 8) else 0
    result &= 0xff
    cpu.status_register.overflow_flag = 1 if (
            not ((cpu.accumulator ^ addr) & 0x80) and ((cpu.accumulator ^ result) & 0x80)) else 0
    cpu.accumulator = result
    cpu.status_register.check_zs_flag(result)


def SBC(mode, cpu, addr):
    addr = cpu.read(addr)
    result = cpu.accumulator - addr - (0 if cpu.status_register.carry_flag else 1)
    cpu.status_register.carry_flag = result >= 0
    result &= 0xff
    cpu.status_register.overflow_flag = 1 if (
            ((cpu.accumulator ^ addr) & 0x80) and ((cpu.accumulator ^ result) & 0x80)) else 0
    cpu.accumulator = result
    cpu.status_register.check_zs_flag(result)


def INC(mode, cpu, addr):
    value = cpu.read(addr)
    value += 1
    value &= 0xff
    cpu.write(addr, value)
    cpu.status_register.check_zs_flag(value)


def DEC(mode, cpu, addr):
    value = cpu.read(addr)
    value -= 1
    value &= 0xff
    cpu.write(addr, value)
    cpu.status_register.check_zs_flag(value)


def INX(mode, cpu, addr):
    cpu.x_index_register += 1
    cpu.x_index_register &= 0xff
    cpu.status_register.check_zs_flag(cpu.x_index_register)


def DEX(mode, cpu, addr):
    cpu.x_index_register -= 1
    cpu.x_index_register &= 0xff
    cpu.status_register.check_zs_flag(cpu.x_index_register)


def INY(mode, cpu, addr):
    cpu.y_index_register += 1
    cpu.y_index_register &= 0xff
    cpu.status_register.check_zs_flag(cpu.y_index_register)


def DEY(mode, cpu, addr):
    cpu.y_index_register -= 1
    cpu.y_index_register &= 0xff
    cpu.status_register.check_zs_flag(cpu.y_index_register)


def TAX(mode, cpu, addr):
    cpu.x_index_register = cpu.accumulator
    cpu.status_register.check_zs_flag(cpu.x_index_register)


def TAY(mode, cpu, addr):
    cpu.y_index_register = cpu.accumulator
    cpu.status_register.check_zs_flag(cpu.y_index_register)


def TXA(mode, cpu, addr):
    cpu.accumulator = cpu.x_index_register
    cpu.status_register.check_zs_flag(cpu.x_index_register)


def TYA(mode, cpu, addr):
    cpu.accumulator = cpu.y_index_register
    cpu.status_register.check_zs_flag(cpu.y_index_register)


def TSX(mode, cpu, addr):
    cpu.x_index_register = cpu.stack_pointer
    cpu.status_register.check_zs_flag(cpu.x_index_register)


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
    cpu.status_register.set(cpu.pop())
    cpu.b_flag = 0
    cpu.irq_disabled_flag = 1
    cpu.program_counter = cpu.pop()
    cpu.program_counter |= cpu.pop() << 8


def SEC(mode, cpu, addr):
    cpu.status_register.carry_flag = 1


def SEI(mode, cpu, addr):
    cpu.status_register.irq_disabled_flag = 1


def SED(mode, cpu, addr):
    cpu.status_register.decimal_mode_flag = 1


def CLD(mode, cpu, addr):
    cpu.status_register.decimal_mode_flag = 0


def CLV(mode, cpu, addr):
    cpu.status_register.overflow_flag = 0


def BCS(mode, cpu, addr):
    if cpu.status_register.carry_flag:
        cpu.program_counter = addr


def CLC(mode, cpu, addr):
    cpu.status_register.carry_flag = 0


def NOP(mode, cpu, addr):
    pass


def BCC(mode, cpu, addr):
    if (not cpu.status_register.carry_flag):
        cpu.program_counter = addr


def LDA(mode, cpu, addr):
    cpu.accumulator = cpu.read(addr)
    cpu.status_register.check_zs_flag(cpu.accumulator)


def STA(mode, cpu, addr):
    cpu.write(addr, cpu.accumulator)


def BEQ(mode, cpu, addr):
    if cpu.status_register.zero_flag:
        cpu.program_counter = addr


def BNE(mode, cpu, addr):
    if not cpu.status_register.zero_flag:
        cpu.program_counter = addr


def BIT(mode, cpu, addr):
    value = cpu.read(addr)
    cpu.status_register.overflow_flag = (value >> 6) & 1
    cpu.status_register.sign_flag = (value >> 7) & 1
    cpu.status_register.zero_flag = 0 if (cpu.accumulator & value) else 1


def BVS(mode, cpu, addr):
    if cpu.status_register.overflow_flag:
        cpu.program_counter = addr


def BVC(mode, cpu, addr):
    if not cpu.status_register.overflow_flag:
        cpu.program_counter = addr


def BMI(mode, cpu, addr):
    if cpu.status_register.sign_flag:
        cpu.program_counter = addr


def BPL(mode, cpu, addr):
    if not cpu.status_register.sign_flag:
        cpu.program_counter = addr


def PHA(mode, cpu, addr):
    cpu.push(cpu.accumulator)


def PLA(mode, cpu, addr):
    cpu.accumulator = cpu.pop()
    cpu.status_register.check_zs_flag(cpu.accumulator)


def PHP(mode, cpu, addr):
    cpu.push(cpu.status_register.show() | 0x10)


def PLP(mode, cpu, addr):
    cpu.status_register.set(cpu.pop())
    cpu.status_register.b_flag = 0


def AND(mode, cpu, addr):
    cpu.accumulator &= cpu.read(addr)
    cpu.status_register.check_zs_flag(cpu.accumulator)


def ORA(mode, cpu, addr):
    cpu.accumulator |= cpu.read(addr)
    cpu.status_register.check_zs_flag(cpu.accumulator)


def EOR(mode, cpu, addr):
    cpu.accumulator ^= cpu.read(addr)
    cpu.status_register.check_zs_flag(cpu.accumulator)


def CMP(mode, cpu, addr):
    result = cpu.accumulator - cpu.read(addr)
    cpu.status_register.carry_flag = result >= 0
    cpu.status_register.check_zs_flag(result)


def CPX(mode, cpu, addr):
    addr = cpu.read(addr)
    result = cpu.x_index_register - addr
    cpu.status_register.carry_flag = result >= 0
    cpu.status_register.check_zs_flag(result)


def CPY(mode, cpu, addr):
    addr = cpu.read(addr)
    result = cpu.y_index_register - addr
    cpu.status_register.carry_flag = result >= 0
    cpu.status_register.check_zs_flag(result)


def LSR(mode, cpu, addr):
    if mode == 1:
        cpu.status_register.carry_flag = 1 if (cpu.accumulator & 1) else 0
        cpu.accumulator >>= 1
        cpu.status_register.check_zs_flag(cpu.accumulator)
    else:
        value = cpu.read(addr)
        cpu.status_register.carry_flag = 1 if (value & 1) else 0
        value >>= 1
        cpu.write(addr, value)
        cpu.status_register.check_zs_flag(value)


def ROR(mode, cpu, addr):
    value = cpu.accumulator
    if mode != 1:
        value = cpu.read(addr)
    if cpu.status_register.carry_flag:
        value |= 0x100
    cpu.status_register.carry_flag = value & 1
    value >>= 1
    value &= 0xff
    cpu.status_register.check_zs_flag(value)
    if mode == 1:
        cpu.accumulator = value
    else:
        cpu.write(addr, value)


def ROL(mode, cpu, addr):
    value = cpu.accumulator
    if 1 != mode:
        value = cpu.read(addr)
    value <<= 1
    if cpu.status_register.carry_flag:
        value |= 0x1
    cpu.status_register.carry_flag = value > 0xff
    value &= 0xff
    cpu.status_register.check_zs_flag(value)
    if mode == 1:
        cpu.accumulator = value
    else:
        cpu.write(addr, value)


def ASL(mode, cpu, addr):
    if mode == 1:
        cpu.status_register.carry_flag = 1 if (cpu.accumulator >> 7) else 0
        cpu.accumulator <<= 1
        cpu.accumulator &= 0xff
        cpu.status_register.check_zs_flag(cpu.accumulator)
    else:
        value = cpu.read(addr)
        cpu.status_register.carry_flag = 1 if (value >> 7) else 0
        value <<= 1
        value &= 0xff
        cpu.write(addr, value)
        cpu.status_register.check_zs_flag(value)


def DCP(mode, cpu, addr):
    value = (cpu.read(addr) - 1) & 0xff
    cpu.write(addr, value)
    result = cpu.accumulator - value
    cpu.status_register.carry_flag = result >= 0
    cpu.status_register.check_zs_flag(result)


def ISC(mode, cpu, addr):
    value = (cpu.read(addr) + 1) & 0xff
    cpu.write(addr, value)
    result = cpu.accumulator - value - (0 if cpu.status_register.carry_flag else 1)

    cpu.status_register.carry_flag = result >= 0
    result &= 0xff
    cpu.status_register.overflow_flag = 1 if (
            ((cpu.accumulator ^ addr) & 0x80) and ((cpu.accumulator ^ result) & 0x80)) else 0
    cpu.accumulator = result
    cpu.status_register.check_zs_flag(result)


def SLO(mode, cpu, addr):
    value = cpu.read(addr)
    cpu.status_register.carry_flag = 1 if (value >> 7) else 0
    value <<= 1
    value &= 0xff
    cpu.write(addr, value)
    cpu.accumulator |= value
    cpu.status_register.check_zs_flag(cpu.accumulator)


def SRE(mode, cpu, addr):
    value = cpu.read(addr)
    cpu.status_register.carry_flag = 1 if (value & 1) else 0
    value >>= 1
    cpu.write(addr, value)
    cpu.accumulator ^= value
    cpu.status_register.check_zs_flag(cpu.accumulator)


def RLA(mode, cpu, addr):
    value = cpu.read(addr)
    value <<= 1
    if cpu.status_register.carry_flag: value |= 0x1
    cpu.status_register.carry_flag = 1 if (value > 0xff) else 0
    cpu.write(addr, value & 0xff)
    cpu.accumulator &= (value & 0xff)
    cpu.status_register.check_zs_flag(cpu.accumulator)


def RRA(mode, cpu, addr):
    value = cpu.read(addr)
    if cpu.status_register.carry_flag: value |= 0x100
    cpu.status_register.carry_flag = value & 1
    value >>= 1
    value &= 0xff
    cpu.write(addr, value)

    value2 = cpu.accumulator + value + (1 if cpu.status_register.carry_flag else 0)
    cpu.status_register.carry_flag = 1 if (value2 >> 8) else 0
    value2 &= 0xff
    cpu.status_register.overflow_flag = 1 if (
            not ((cpu.accumulator ^ value) & 0x80) and ((cpu.accumulator ^ value2) & 0x80)) else 0
    cpu.accumulator = value2
    cpu.status_register.check_zs_flag(value2)

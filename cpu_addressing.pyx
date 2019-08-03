_accumulator = 1
_implied_addressing = 2
_immediate_addressing = 3
_absolute_addressing = 4
_zero_page_absolute_addressing = 5
_absolute_x_indexed_addressing = 6
_absolute_y_indexed_addressing = 7
_zero_page_x_indexed_addressing = 8
_zero_page_y_indexed_addressing = 9
_indirect_addressing = 10
_pre_indexed_indirect_addressing = 11
_post_indexed_indirect_addressing = 12
_relative_addressing = 13

_absolute_x_indexed_addressing_check_oops = 14
_absolute_y_indexed_addressing_check_oops = 15
_post_indexed_indirect_addressing_check_oops = 16

def addressing(mode, cpu):
    if mode == _accumulator or mode == _implied_addressing:
        return
    elif mode == _immediate_addressing:
        return cpu.program_counter + 1
    elif mode == _absolute_addressing:
        return cpu.read(cpu.program_counter + 1) | cpu.read(cpu.program_counter + 2) << 8
    elif mode == _zero_page_absolute_addressing:
        return cpu.read(cpu.program_counter + 1)
    elif mode == _absolute_x_indexed_addressing:
        return (cpu.x_index_register + (cpu.read(cpu.program_counter + 1) | cpu.read(cpu.program_counter + 2) << 8)) & 0xffff
    elif mode == _absolute_y_indexed_addressing:
        return (cpu.y_index_register + (cpu.read(cpu.program_counter + 1) | cpu.read(cpu.program_counter + 2) << 8)) & 0xffff
    elif mode == _zero_page_x_indexed_addressing:
        return (cpu.x_index_register + cpu.read(cpu.program_counter + 1)) & 0xff
    elif mode == _zero_page_y_indexed_addressing:
        return (cpu.y_index_register + cpu.read(cpu.program_counter + 1)) & 0xff
    elif mode == _indirect_addressing:
        addr = cpu.read(cpu.program_counter + 1) | cpu.read(cpu.program_counter + 2) << 8
        bug_addr = (addr & 0xff00) | ((addr + 1) & 0x00ff)
        return cpu.read(addr) | cpu.read(bug_addr) << 8
    elif mode == _pre_indexed_indirect_addressing:
        addr = (cpu.read(cpu.program_counter + 1) + cpu.x_index_register) & 0xff
        return cpu.read(addr) | cpu.read((addr + 1) & 0xff) << 8  # addr == FF, addr+1 == 00
    elif mode == _post_indexed_indirect_addressing:
        operand = cpu.read(cpu.program_counter + 1)
        addr = cpu.read(operand) | cpu.read((operand + 1) & 0xff) << 8
        return (addr + cpu.y_index_register) & 0xffff
    elif mode == _relative_addressing:
        operand = cpu.read(cpu.program_counter + 1)
        return cpu.program_counter + (operand - 256 if (operand & 0x80) else operand) + 2

    elif mode == _absolute_x_indexed_addressing_check_oops:
        addr = cpu.read(cpu.program_counter + 1) | cpu.read(cpu.program_counter + 2) << 8
        ret = (cpu.x_index_register + addr) & 0xffff
        cpu.cpu_cycle += 1 if addr >> 8 != ret >> 8 else 0
        return ret
    elif mode == _absolute_y_indexed_addressing_check_oops:
        addr = cpu.read(cpu.program_counter + 1) | cpu.read(cpu.program_counter + 2) << 8
        ret = (cpu.y_index_register + addr) & 0xffff
        cpu.cpu_cycle += 1 if addr >> 8 != ret >> 8 else 0
        return ret
    elif mode == _post_indexed_indirect_addressing_check_oops:
        operand = cpu.read(cpu.program_counter + 1)
        addr = cpu.read(operand) | cpu.read((operand + 1) & 0xff) << 8
        ret = (addr + cpu.y_index_register) & 0xffff
        cpu.cpu_cycle += 1 if addr >> 8 != ret >> 8 else 0
        return ret

    else:
        assert 0, 'Error addressing mode!'

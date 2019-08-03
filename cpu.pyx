# cython: language_level=3

from tools.tool import fromat
#from c_cpu_addressing import addressing
# from c_cpu_instr import *
from register import Register
from libcpp.vector cimport vector


cdef class CPU:
    cdef public object file
    cdef public int mmc_type
    cdef public vector[int] main_memory
    cdef public vector[int] save_memory
    cdef public object ppu

    cdef public object input_status
    cdef public int input_mask
    cdef public int input_index

    cdef public int _NMI
    cdef public int _RESET
    cdef public int _IRQ

    cdef public int program_counter
    cdef public int accumulator
    cdef public int x_index_register
    cdef public int y_index_register
    cdef public int stack_pointer
    cdef public object status_register

    cdef public long cpu_cycle

    cdef public list op_detail


    def __init__(self, file, main_memory, save_memory, ppu):
        self.file = file
        self.mmc_type = 0
        self.main_memory = main_memory
        self.save_memory = save_memory
        self.ppu = ppu

        self.input_status = [0 for _ in range(8)]
        self.input_mask = 0
        self.input_index = 0

        self._NMI = 0xfffa
        self._RESET = 0xfffc
        self._IRQ = 0xfffe

        self.program_counter = self.read(self._RESET) | self.read(self._RESET + 1) << 8
        self.accumulator = 0
        self.x_index_register = 0
        self.y_index_register = 0
        self.stack_pointer = 0xff
        self.status_register = Register(0x20)

        self.cpu_cycle = 0

        # (op_name, addressing_mode, instr_bytes, instr_cycles)
        #  1:accumulator, 2:implied_addressing, 3:immediate_addressing, 4:absolute_addressing, 5:zero_page_absolute_addressing
        # 6:absolute_x_indexed_addressing, 7:absolute_y_indexed_addressing 8:zero_page_x_indexed_addressing,
        # 9:zero_page_y_indexed_addressing, 10:indirect_addressing  11:pre_indexed_indirect_addressing
        # 12:post_indexed_indirect_addressing, 13:relative_addressing
        #                          0           1              2              3            4              5              6             7             8              9              A            B           C                D                E             F
        self.op_detail = [('BRK',2, 1,7),('ORA',11,2,6),'STP',        ('SLO',11,2,8),('NOP',5,2,3),('ORA',5,2,3),('ASL',5,2,5),('SLO',5,2,5),('PHP',2,1,3),('ORA',3, 2,2),('ASL',1,1,2),('ANC',3, 2,2),('NOP',4, 3,4),('ORA',4, 3,4),('ASL',4, 3,6),('SLO',4, 3,6),  # 0
                          ('BPL',13,2,2),('ORA',16,2,5),'STP',        ('SLO',12,2,8),('NOP',8,2,4),('ORA',8,2,4),('ASL',8,2,6),('SLO',8,2,6),('CLC',2,1,2),('ORA',15,3,4),('NOP',2,1,2),('SLO',7, 3,7),('NOP',14,3,4),('ORA',14,3,4),('ASL',6, 3,7),('SLO',6, 3,7),  # 1
                          ('JSR',4, 3,6),('AND',11,2,6),'STP',        ('RLA',11,2,8),('BIT',5,2,3),('AND',5,2,3),('ROL',5,2,5),('RLA',5,2,5),('PLP',2,1,4),('AND',3, 2,2),('ROL',1,1,2),'ANC',         ('BIT',4, 3,4),('AND',4, 3,4),('ROL',4, 3,6),('RLA',4, 3,6),  # 2
                          ('BMI',13,2,2),('AND',16,2,5),'STP',        ('RLA',12,2,8),('NOP',8,2,4),('AND',8,2,4),('ROL',8,2,6),('RLA',8,2,6),('SEC',2,1,2),('AND',15,3,4),('NOP',2,1,2),('RLA',7, 3,7),('NOP',14,3,4),('AND',14,3,4),('ROL',6, 3,7),('RLA',6, 3,7),  # 3
                          ('RTI',2, 1,6),('EOR',11,2,6),'STP',        ('SRE',11,2,8),('NOP',5,2,3),('EOR',5,2,3),('LSR',5,2,5),('SRE',5,2,5),('PHA',2,1,3),('EOR',3, 2,2),('LSR',1,1,2),('ALR',3, 2,2),('JMP',4, 3,3),('EOR',4, 3,4),('LSR',4, 3,6),('SRE',4, 3,6),  # 4
                          ('BVC',13,2,2),('EOR',16,2,5),'STP',        ('SRE',12,2,8),('NOP',8,2,4),('EOR',8,2,4),('LSR',8,2,6),('SRE',8,2,6),('CLI',2,1,2),('EOR',15,3,4),('NOP',2,1,2),('SRE',7, 3,7),('NOP',14,3,4),('EOR',14,3,4),('LSR',6, 3,7),('SRE',6, 3,7),  # 5
                          ('RTS',2, 1,6),('ADC',11,2,6),'STP',        ('RRA',11,2,8),('NOP',5,2,3),('ADC',5,2,3),('ROR',5,2,5),('RRA',5,2,5),('PLA',2,1,4),('ADC',3, 2,2),('ROR',1,1,2),('ARR',3, 2,2),('JMP',10,3,5),('ADC',4, 3,4),('ROR',4, 3,6),('RRA',4, 3,6),  # 6
                          ('BVS',13,2,2),('ADC',16,2,5),'STP',        ('RRA',12,2,8),('NOP',8,2,4),('ADC',8,2,4),('ROR',8,2,6),('RRA',8,2,6),('SEI',2,1,2),('ADC',15,3,4),('NOP',2,1,2),('RRA',7, 3,7),('NOP',14,3,4),('ADC',14,3,4),('ROR',6, 3,7),('RRA',6, 3,7),  # 7
                          ('NOP',3, 2,2),('STA',11,2,6),('NOP',3,2,2),('SAX',11,2,6),('STY',5,2,3),('STA',5,2,3),('STX',5,2,3),('SAX',5,2,3),('DEY',2,1,2),('NOP',3, 2,2),('TXA',2,1,2),'XAA',         ('STY',4, 3,4),('STA',4, 3,4),('STX',4, 3,4),('SAX',4, 3,4),  # 8
                          ('BCC',13,2,2),('STA',12,2,6),'STP',        'AHX',         ('STY',8,2,4),('STA',8,2,4),('STX',9,2,4),('SAX',9,2,4),('TYA',2,1,2),('STA',7, 3,5),('TXS',2,1,2),'TAS',         'SHY',         ('STA',6, 3,5),'SHX',          'AHX',          # 9
                          ('LDY',3, 2,2),('LDA',11,2,6),('LDX',3,2,2),('LAX',11,2,6),('LDY',5,2,3),('LDA',5,2,3),('LDX',5,2,3),('LAX',5,2,3),('TAY',2,1,2),('LDA',3, 2,2),('TAX',2,1,2),'LAX',         ('LDY',4, 3,4),('LDA',4, 3,4),('LDX',4, 3,4),('LAX',4, 3,4),  # A
                          ('BCS',13,2,2),('LDA',16,2,5),'STP',        ('LAX',16,2,5),('LDY',8,2,4),('LDA',8,2,4),('LDX',9,2,4),('LAX',9,2,4),('CLV',2,1,2),('LDA',15,3,4),('TSX',2,1,2),'LAS',         ('LDY',14,3,4),('LDA',14,3,4),('LDX',15,3,4),('LAX',15,3,4),  # B
                          ('CPY',3, 2,2),('CMP',11,2,6),('NOP',3,2,2),('DCP',11,2,8),('CPY',5,2,3),('CMP',5,2,3),('DEC',5,2,5),('DCP',5,2,5),('INY',2,1,2),('CMP',3, 2,2),('DEX',2,1,2),('AXS',3, 2,2),('CPY',4, 3,4),('CMP',4, 3,4),('DEC',4, 3,6),('DCP',4, 3,6),  # C
                          ('BNE',13,2,2),('CMP',16,2,5),'STP',        ('DCP',12,2,8),('NOP',8,2,4),('CMP',8,2,4),('DEC',8,2,6),('DCP',8,2,6),('CLD',2,1,2),('CMP',15,3,4),('NOP',2,1,2),('DCP',7, 3,7),('NOP',14,3,4),('CMP',14,3,4),('DEC',6, 3,7),('DCP',6, 3,7),  # D
                          ('CPX',3, 2,2),('SBC',11,2,6),('NOP',3,2,2),('ISC',11,2,8),('CPX',5,2,3),('SBC',5,2,3),('INC',5,2,5),('ISC',5,2,5),('INX',2,1,2),('SBC',3, 2,2),('NOP',2,1,2),('SBC',3, 2,2),('CPX',4, 3,4),('SBC',4, 3,4),('INC',4, 3,6),('ISC',4, 3,6),  # E
                          ('BEQ',13,2,2),('SBC',16,2,5),'STP',        ('ISC',12,2,8),('NOP',8,2,4),('SBC',8,2,4),('INC',8,2,6),('ISC',8,2,6),('SED',2,1,2),('SBC',15,3,4),('NOP',2,1,2),('ISC',7, 3,7),('NOP',14,3,4),('SBC',14,3,4),('INC',6, 3,7),('ISC',6, 3,7),  # F
                          ]


    cdef void push(self, int data):
        self.write(0x100 | self.stack_pointer, data)
        self.stack_pointer = (self.stack_pointer - 1) & 0xff

    cdef int pop(self):
        self.stack_pointer = (self.stack_pointer + 1) & 0xff
        return self.read(0x100 | self.stack_pointer)

    cdef int read(self, int addr):
        if self.mmc_type == 0:
            if 0x8000 <= addr < 0xc000:
                return self.file.prg_rom[:0x4000][addr & 0x3fff]
            elif 0xc000 <= addr < 0x10000:
                return self.file.prg_rom[-0x4000:][addr & 0x3fff]
            elif 0 <= addr < 0x2000:
                return self.main_memory[addr & 0x7ff]
            elif 0x2000 <= addr < 0x4000:
                addr = addr & 0x7 + 0x2000
                return self.ppu.read_register(addr)
            elif addr == 0x4014:
                assert 0, "TODO"
            elif addr == 0x4016:
                ret = self.input_status[self.input_index & self.input_mask]
                self.input_index += 1
                return ret
            elif 0x4000 <= addr < 0x4020:
                return 0  # TODO
            elif 0x6000 <= addr < 0x8000:
                assert 0, "TODO: sram"  # return self.save_memory.read(addr & 0x1fff)
            else:
                assert 0, "TODO"
        else:
            assert 0, "TODO"

    cdef void write(self, int addr, int data):
        if self.mmc_type == 0:
            if 0 <= addr < 0x2000:
                self.main_memory[addr & 0x7ff] = data
            elif 0x2000 <= addr < 0x4000:
                addr = addr & 0x7 + 0x2000
                self.ppu.write_register(addr, data)
            elif addr == 0x4014:
                if data in range(0, 0x20):
                    self.ppu.oam = self.main_memory[(data << 8):(data << 8 | 0x100)]
                elif data in range(0x60, 0x80):
                    data -= 0x60
                    self.ppu.oam.set(self.save_memory[(data << 8):(data << 8 | 0x100)])
                elif data in range(0x80, 0x100):
                    data -= 0x80
                    self.ppu.oam.set(self.file.prg_rom[(data << 8):(data << 8 | 0x100)])
            elif addr == 0x4016:
                self.input_mask = 0x0 if data & 1 else 0x7
                if data & 1:
                    self.input_index = 0
            elif 0x4000 <= addr < 0x4020:
                pass
            elif 0x6000 <= addr < 0x8000:
                assert 0, "TODO: sram"  # return self.save_memory.write(addr & 0x1fff, data)
            elif 0x8000 <= addr < 0x10000:
                assert 0, "Can't write to ROM"
            else:
                assert 0, "TODO"
        else:
            assert 0, "TODO"

    def exec_op(self):
        self._exec_op()

    cdef void _exec_op(self):
        cdef int index, addressing_mode, instr_bytes, operand, cycles
        cdef str instruction

        index = self.read(self.program_counter)
        op_detail = self.op_detail[index]
        instruction, addressing_mode, instr_bytes, cycles = op_detail[0], op_detail[1], op_detail[2], op_detail[3]

        operand = self.addressing(addressing_mode)
        self.program_counter += instr_bytes

        # self.op_function[instruction](addressing_mode, self, operand)
        self.exec_instr(instruction, operand, addressing_mode)

        self.cpu_cycle += cycles

    cpdef void nmi(self):
        if self.ppu.ppu_ctrl.value & 0x80:
            self.push(self.program_counter >> 8)
            self.push(self.program_counter)
            self.push(self.status_register.value)
            self.status_register.bit2 = 1
            laddr = self.read(self._NMI)
            haddr = self.read(self._NMI + 1)
            self.program_counter = laddr | haddr << 8

    cdef _get_operands(self, mode, param):
            if mode == 1:
                return 'A'
            elif mode == 2:
                return ''
            elif mode == 3:
                return '#$' + fromat(param[0])
            elif mode == 4:
                return '$' + fromat(param[0] | param[1] << 8)
            elif mode == 5:
                return '$' + fromat(param[0])
            elif mode == 6 or mode == 14:
                return '$' + fromat(param[0] | param[1] << 8) + ',X'
            elif mode == 7 or mode == 15:
                return '$' + fromat(param[0] | param[1] << 8) + ',Y'
            elif mode == 8:
                return '$' + fromat(param[0]) + ',X'
            elif mode == 9:
                return '$' + fromat(param[0]) + ',Y'
            elif mode == 10:
                return '($' + fromat(param[0] | param[1] << 8) + ')'
            elif mode == 11:
                return '($' + fromat(param[0]) + ',X)'
            elif mode == 12 or mode == 16:
                return '($' + fromat(param[0]) + '),Y'
            elif mode == 13:
                return '$' + fromat(self.program_counter + 2 + (param[0] if not param[0] & 0x80 else param[0] - 256))
            else:
                assert 0, 'Error addressing mode!'

    cdef disassemble(self):
        addr = self.program_counter
        op_index = self.read(addr)
        instruction, addressing_mode, instr_bytes = self.op_detail[op_index][0], self.op_detail[op_index][1], self.op_detail[op_index][2]

        operand_bytes = []
        for i in range(instr_bytes - 1):
            operand_bytes += [self.read(addr + i + 1)]
        # print('%s  %s %-7s ' % (fromat(addr), fromat(op_index), list_to_hex_str(operand_bytes)), end='')
        # print('%s  ' % (fromat(addr)), end='')

        operands = self._get_operands(addressing_mode, operand_bytes)
        #print('%s %-7s ' % (instruction, operands), end='')

        # print('A:%s X:%s Y:%s P:%s SP:%s' % (
        #     fromat(self.accumulator), fromat(self.x_index_register), fromat(self.y_index_register),
        #     fromat(self.status_register.value), fromat(self.stack_pointer)), end='')

        # print(self.cpu_cycle)

    cdef int addressing(self, int mode):
        cdef int addr, bug_addr, operand, ret

        if mode == 1 or mode == 2:
            return 0
        elif mode == 3:
            return self.program_counter + 1
        elif mode == 4:
            return self.read(self.program_counter + 1) | self.read(self.program_counter + 2) << 8
        elif mode == 5:
            return self.read(self.program_counter + 1)
        elif mode == 6:
            return (self.x_index_register + (self.read(self.program_counter + 1) | self.read(self.program_counter + 2) << 8)) & 0xffff
        elif mode == 7:
            return (self.y_index_register + (self.read(self.program_counter + 1) | self.read(self.program_counter + 2) << 8)) & 0xffff
        elif mode == 8:
            return (self.x_index_register + self.read(self.program_counter + 1)) & 0xff
        elif mode == 9:
            return (self.y_index_register + self.read(self.program_counter + 1)) & 0xff
        elif mode == 10:
            addr = self.read(self.program_counter + 1) | self.read(self.program_counter + 2) << 8
            bug_addr = (addr & 0xff00) | ((addr + 1) & 0x00ff)
            return self.read(addr) | self.read(bug_addr) << 8
        elif mode == 11:
            addr = (self.read(self.program_counter + 1) + self.x_index_register) & 0xff
            return self.read(addr) | self.read((addr + 1) & 0xff) << 8  # addr == FF, addr+1 == 00
        elif mode == 12:
            operand = self.read(self.program_counter + 1)
            addr = self.read(operand) | self.read((operand + 1) & 0xff) << 8
            return (addr + self.y_index_register) & 0xffff
        elif mode == 13:
            operand = self.read(self.program_counter + 1)
            return self.program_counter + (operand - 256 if (operand & 0x80) else operand) + 2

        elif mode == 14:
            addr = self.read(self.program_counter + 1) | self.read(self.program_counter + 2) << 8
            ret = (self.x_index_register + addr) & 0xffff
            self.cpu_cycle += 1 if addr >> 8 != ret >> 8 else 0
            return ret
        elif mode == 15:
            addr = self.read(self.program_counter + 1) | self.read(self.program_counter + 2) << 8
            ret = (self.y_index_register + addr) & 0xffff
            self.cpu_cycle += 1 if addr >> 8 != ret >> 8 else 0
            return ret
        elif mode == 16:
            operand = self.read(self.program_counter + 1)
            addr = self.read(operand) | self.read((operand + 1) & 0xff) << 8
            ret = (addr + self.y_index_register) & 0xffff
            self.cpu_cycle += 1 if addr >> 8 != ret >> 8 else 0
            return ret

        else:
            assert 0, 'Error addressing mode!'

    cdef void exec_instr(self, str instruction, int operand, int addressing_mode):
        cdef int result, value

        if instruction == 'JMP':
            self.program_counter = operand
        elif instruction == 'LDX':
            self.x_index_register = self.read(operand)
            self.status_register.bit7 = 1 if (self.x_index_register & 0x80) else 0
            self.status_register.bit1 = 1 if (self.x_index_register == 0) else 0
        elif instruction == 'LAX':
            value = self.read(operand)
            self.accumulator = self.x_index_register = value
            self.status_register.bit7 = 1 if (value & 0x80) else 0
            self.status_register.bit1 = 1 if (value == 0) else 0
        elif instruction == 'LDY':
            operand = self.read(operand)
            self.y_index_register = operand
            self.status_register.bit7 = 1 if (self.y_index_register & 0x80) else 0
            self.status_register.bit1 = 1 if (self.y_index_register == 0) else 0
        elif instruction == 'LAY':
            value = self.read(operand)
            self.accumulator = self.y_index_register = value
            self.status_register.bit7 = 1 if (value & 0x80) else 0
            self.status_register.bit1 = 1 if (value == 0) else 0
        elif instruction == 'STX':
            self.write(operand, self.x_index_register)
        elif instruction == 'SAX':
            self.write(operand, self.x_index_register & self.accumulator)
        elif instruction == 'STY':
            self.write(operand, self.y_index_register)
        elif instruction == 'ADC':
            operand = self.read(operand)
            result = operand + self.accumulator + (1 if self.status_register.bit0 else 0)
            self.status_register.bit0 = 1 if (result >> 8) else 0
            result &= 0xff
            self.status_register.bit6 = 1 if (
                    not ((self.accumulator ^ operand) & 0x80) and ((self.accumulator ^ result) & 0x80)) else 0
            self.accumulator = result
            self.status_register.bit7 = 1 if (result & 0x80) else 0
            self.status_register.bit1 = 1 if (result == 0) else 0
        elif instruction == 'SBC':
            operand = self.read(operand)
            result = self.accumulator - operand - (0 if self.status_register.bit0 else 1)
            self.status_register.bit0 = result >= 0
            result &= 0xff
            self.status_register.bit6 = 1 if (
                    ((self.accumulator ^ operand) & 0x80) and ((self.accumulator ^ result) & 0x80)) else 0
            self.accumulator = result
            self.status_register.bit7 = 1 if (result & 0x80) else 0
            self.status_register.bit1 = 1 if (result == 0) else 0
        elif instruction == 'INC':
            value = self.read(operand)
            value += 1
            value &= 0xff
            self.write(operand, value)
            self.status_register.bit7 = 1 if (value & 0x80) else 0
            self.status_register.bit1 = 1 if (value == 0) else 0
        elif instruction == 'DEC':
            value = self.read(operand)
            value -= 1
            value &= 0xff
            self.write(operand, value)
            self.status_register.bit7 = 1 if (value & 0x80) else 0
            self.status_register.bit1 = 1 if (value == 0) else 0
        elif instruction == 'INX':
            self.x_index_register += 1
            self.x_index_register &= 0xff
            self.status_register.bit7 = 1 if (self.x_index_register & 0x80) else 0
            self.status_register.bit1 = 1 if (self.x_index_register == 0) else 0
        elif instruction == 'DEX':
            self.x_index_register -= 1
            self.x_index_register &= 0xff
            self.status_register.bit7 = 1 if (self.x_index_register & 0x80) else 0
            self.status_register.bit1 = 1 if (self.x_index_register == 0) else 0
        elif instruction == 'INY':
            self.y_index_register += 1
            self.y_index_register &= 0xff
            self.status_register.bit7 = 1 if (self.y_index_register & 0x80) else 0
            self.status_register.bit1 = 1 if (self.y_index_register == 0) else 0
        elif instruction == 'DEY':
            self.y_index_register -= 1
            self.y_index_register &= 0xff
            self.status_register.bit7 = 1 if (self.y_index_register & 0x80) else 0
            self.status_register.bit1 = 1 if (self.y_index_register == 0) else 0
        elif instruction == 'TAX':
            self.x_index_register = self.accumulator
            self.status_register.bit7 = 1 if (self.x_index_register & 0x80) else 0
            self.status_register.bit1 = 1 if (self.x_index_register == 0) else 0
        elif instruction == 'TAY':
            self.y_index_register = self.accumulator
            self.status_register.bit7 = 1 if (self.y_index_register & 0x80) else 0
            self.status_register.bit1 = 1 if (self.y_index_register == 0) else 0
        elif instruction == 'TXA':
            self.accumulator = self.x_index_register
            self.status_register.bit7 = 1 if (self.x_index_register & 0x80) else 0
            self.status_register.bit1 = 1 if (self.x_index_register == 0) else 0
        elif instruction == 'TYA':
            self.accumulator = self.y_index_register
            self.status_register.bit7 = 1 if (self.y_index_register & 0x80) else 0
            self.status_register.bit1 = 1 if (self.y_index_register == 0) else 0
        elif instruction == 'TSX':
            self.x_index_register = self.stack_pointer
            self.status_register.bit7 = 1 if (self.x_index_register & 0x80) else 0
            self.status_register.bit1 = 1 if (self.x_index_register == 0) else 0
        elif instruction == 'TXS':
            self.stack_pointer = self.x_index_register
        elif instruction == 'JSR':
            self.program_counter -= 1
            self.push(self.program_counter >> 8)
            self.push(self.program_counter & 0xff)
            self.program_counter = operand
        elif instruction == 'RTS':
            self.program_counter = self.pop()
            self.program_counter |= self.pop() << 8
            self.program_counter += 1
        elif instruction == 'RTI':
            self.status_register.value = self.pop() | 0x20
            self.status_register.bit4 = 0
            self.status_register.bit5 = 1
            self.program_counter = self.pop()
            self.program_counter |= self.pop() << 8
        elif instruction == 'SEC':
            self.status_register.bit0 = 1
        elif instruction == 'SEI':
            self.status_register.bit2 = 1
        elif instruction == 'SED':
            self.status_register.bit3 = 1
        elif instruction == 'CLD':
            self.status_register.bit3 = 0
        elif instruction == 'CLV':
            self.status_register.bit6 = 0
        elif instruction == 'BCS':
            if self.status_register.bit0:
                self.cpu_cycle += 2 if self.program_counter >> 8 != operand >> 8 else 1
                self.program_counter = operand
        elif instruction == 'CLC':
            self.status_register.bit0 = 0
        elif instruction == 'NOP':
            pass
        elif instruction == 'BCC':
            if not self.status_register.bit0:
                self.cpu_cycle += 2 if self.program_counter >> 8 != operand >> 8 else 1
                self.program_counter = operand
        elif instruction == 'LDA':
            self.accumulator = self.read(operand)
            self.status_register.bit7 = 1 if (self.accumulator & 0x80) else 0
            self.status_register.bit1 = 1 if (self.accumulator == 0) else 0
        elif instruction == 'STA':
            self.write(operand, self.accumulator)
        elif instruction == 'BEQ':
            if self.status_register.bit1:
                self.cpu_cycle += 2 if self.program_counter >> 8 != operand >> 8 else 1
                self.program_counter = operand
        elif instruction == 'BNE':
            if not self.status_register.bit1:
                self.cpu_cycle += 2 if self.program_counter >> 8 != operand >> 8 else 1
                self.program_counter = operand
        elif instruction == 'BIT':
            value = self.read(operand)
            self.status_register.bit6 = (value >> 6) & 1
            self.status_register.bit7 = (value >> 7) & 1
            self.status_register.bit1 = 0 if (self.accumulator & value) else 1
        elif instruction == 'BVS':
            if self.status_register.bit6:
                self.cpu_cycle += 2 if self.program_counter >> 8 != operand >> 8 else 1
                self.program_counter = operand
        elif instruction == 'BVC':
            if not self.status_register.bit6:
                self.cpu_cycle += 2 if self.program_counter >> 8 != operand >> 8 else 1
                self.program_counter = operand
        elif instruction == 'BMI':
            if self.status_register.bit7:
                self.cpu_cycle += 2 if self.program_counter >> 8 != operand >> 8 else 1
                self.program_counter = operand
        elif instruction == 'BPL':
            if not self.status_register.bit7:
                self.cpu_cycle += 2 if self.program_counter >> 8 != operand >> 8 else 1
                self.program_counter = operand
        elif instruction == 'PHA':
            self.push(self.accumulator)
        elif instruction == 'PLA':
            self.accumulator = self.pop()
            self.status_register.bit7 = 1 if (self.accumulator & 0x80) else 0
            self.status_register.bit1 = 1 if (self.accumulator == 0) else 0
        elif instruction == 'PHP':
            self.push(self.status_register.value | 0x10)
        elif instruction == 'PLP':
            self.status_register.value = self.pop() | 0x20
            self.status_register.bit4 = 0
        elif instruction == 'AND':
            self.accumulator &= self.read(operand)
            self.status_register.bit7 = 1 if (self.accumulator & 0x80) else 0
            self.status_register.bit1 = 1 if (self.accumulator == 0) else 0
        elif instruction == 'ORA':
            self.accumulator |= self.read(operand)
            self.status_register.bit7 = 1 if (self.accumulator & 0x80) else 0
            self.status_register.bit1 = 1 if (self.accumulator == 0) else 0
        elif instruction == 'EOR':
            self.accumulator ^= self.read(operand)
            self.status_register.bit7 = 1 if (self.accumulator & 0x80) else 0
            self.status_register.bit1 = 1 if (self.accumulator == 0) else 0
        elif instruction == 'CMP':
            result = self.accumulator - self.read(operand)
            self.status_register.bit0 = result >= 0
            self.status_register.bit7 = 1 if (result & 0x80) else 0
            self.status_register.bit1 = 1 if (result == 0) else 0
        elif instruction == 'CPX':
            operand = self.read(operand)
            result = self.x_index_register - operand
            self.status_register.bit0 = result >= 0
            self.status_register.bit7 = 1 if (result & 0x80) else 0
            self.status_register.bit1 = 1 if (result == 0) else 0
        elif instruction == 'CPY':
            operand = self.read(operand)
            result = self.y_index_register - operand
            self.status_register.bit0 = result >= 0
            self.status_register.bit7 = 1 if (result & 0x80) else 0
            self.status_register.bit1 = 1 if (result == 0) else 0
        elif instruction == 'LSR':
            if addressing_mode == 1:
                self.status_register.bit0 = 1 if (self.accumulator & 1) else 0
                self.accumulator >>= 1
                self.status_register.bit7 = 1 if (self.accumulator & 0x80) else 0
                self.status_register.bit1 = 1 if (self.accumulator == 0) else 0
            else:
                value = self.read(operand)
                self.status_register.bit0 = 1 if (value & 1) else 0
                value >>= 1
                self.write(operand, value)
                self.status_register.bit7 = 1 if (value & 0x80) else 0
                self.status_register.bit1 = 1 if (value == 0) else 0
        elif instruction == 'ROR':
            value = self.accumulator
            if addressing_mode != 1:
                value = self.read(operand)
            if self.status_register.bit0:
                value |= 0x100
            self.status_register.bit0 = value & 1
            value >>= 1
            value &= 0xff
            self.status_register.bit7 = 1 if (value & 0x80) else 0
            self.status_register.bit1 = 1 if (value == 0) else 0
            if addressing_mode == 1:
                self.accumulator = value
            else:
                self.write(operand, value)
        elif instruction == 'ROL':
            value = self.accumulator
            if 1 != addressing_mode:
                value = self.read(operand)
            value <<= 1
            if self.status_register.bit0:
                value |= 0x1
            self.status_register.bit0 = value > 0xff
            value &= 0xff
            self.status_register.bit7 = 1 if (value & 0x80) else 0
            self.status_register.bit1 = 1 if (value == 0) else 0
            if addressing_mode == 1:
                self.accumulator = value
            else:
                self.write(operand, value)
        elif instruction == 'ASL':
            if addressing_mode == 1:
                self.status_register.bit0 = 1 if (self.accumulator >> 7) else 0
                self.accumulator <<= 1
                self.accumulator &= 0xff
                self.status_register.bit7 = 1 if (self.accumulator & 0x80) else 0
                self.status_register.bit1 = 1 if (self.accumulator == 0) else 0
            else:
                value = self.read(operand)
                self.status_register.bit0 = 1 if (value >> 7) else 0
                value <<= 1
                value &= 0xff
                self.write(operand, value)
                self.status_register.bit7 = 1 if (value & 0x80) else 0
                self.status_register.bit1 = 1 if (value == 0) else 0


        elif instruction == 'DCP':
            value = (self.read(operand) - 1) & 0xff
            self.write(operand, value)
            result = self.accumulator - value
            self.status_register.bit0 = result >= 0
            self.status_register.bit7 = 1 if (result & 0x80) else 0
            self.status_register.bit1 = 1 if (result == 0) else 0
        elif instruction == 'ISC':
            value = (self.read(operand) + 1) & 0xff
            self.write(operand, value)
            result = self.accumulator - value - (0 if self.status_register.bit0 else 1)

            self.status_register.bit0 = result >= 0
            result &= 0xff
            self.status_register.bit6 = 1 if (
                    ((self.accumulator ^ operand) & 0x80) and ((self.accumulator ^ result) & 0x80)) else 0
            self.accumulator = result
            self.status_register.bit7 = 1 if (result & 0x80) else 0
            self.status_register.bit1 = 1 if (result == 0) else 0
        elif instruction == 'SLO':
            value = self.read(operand)
            self.status_register.bit0 = 1 if (value >> 7) else 0
            value <<= 1
            value &= 0xff
            self.write(operand, value)
            self.accumulator |= value
            self.status_register.bit7 = 1 if (self.accumulator & 0x80) else 0
            self.status_register.bit1 = 1 if (self.accumulator == 0) else 0
        elif instruction == 'SRE':
            value = self.read(operand)
            self.status_register.bit0 = 1 if (value & 1) else 0
            value >>= 1
            self.write(operand, value)
            self.accumulator ^= value
            self.status_register.bit7 = 1 if (self.accumulator & 0x80) else 0
            self.status_register.bit1 = 1 if (self.accumulator == 0) else 0
        elif instruction == 'RLA':
            value = self.read(operand)
            value <<= 1
            if self.status_register.bit0:
                value |= 0x1
            self.status_register.bit0 = 1 if (value > 0xff) else 0
            self.write(operand, value & 0xff)
            self.accumulator &= (value & 0xff)
            self.status_register.bit7 = 1 if (self.accumulator & 0x80) else 0
            self.status_register.bit1 = 1 if (self.accumulator == 0) else 0
        elif instruction == 'RRA':
            value = self.read(operand)
            if self.status_register.bit0:
                value |= 0x100
            self.status_register.bit0 = value & 1
            value >>= 1
            value &= 0xff
            self.write(operand, value)

            value2 = self.accumulator + value + (1 if self.status_register.bit0 else 0)
            self.status_register.bit0 = 1 if (value2 >> 8) else 0
            value2 &= 0xff
            self.status_register.bit6 = 1 if (
                    not ((self.accumulator ^ value) & 0x80) and ((self.accumulator ^ value2) & 0x80)) else 0
            self.accumulator = value2
            self.status_register.bit7 = 1 if (value2 & 0x80) else 0
            self.status_register.bit1 = 1 if (value2 == 0) else 0
        elif instruction == 'BRK':
            self.program_counter += 1
            self.push(self.program_counter >> 8)
            self.push(self.program_counter & 0xFF)
            self.push(self.status_register.value)
            self.program_counter |= self.read(self._IRQ + 1) << 8

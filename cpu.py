from tools.tool import fromat
from cpu_addressing import addressing
from cpu_instr import *


class StatusRegister(object):
    def __init__(self):
        self.carry_flag = 0
        self.zero_flag = 0
        self.irq_disabled_flag = 0
        self.decimal_mode_flag = 0
        self.b_flag = 0
        self.overflow_flag = 0
        self.sign_flag = 0

    def value(self):
        ret = 0
        ret |= self.carry_flag << 0
        ret |= self.zero_flag << 1
        ret |= self.irq_disabled_flag << 2
        ret |= self.decimal_mode_flag << 3
        ret |= self.b_flag << 4
        ret |= 0x20
        ret |= self.overflow_flag << 6
        ret |= self.sign_flag << 7
        return ret

    def set(self, data):
        self.carry_flag = data >> 0 & 0x1
        self.zero_flag = data >> 1 & 0x1
        self.irq_disabled_flag = data >> 2 & 0x1
        self.decimal_mode_flag = data >> 3 & 0x1
        self.b_flag = data >> 4 & 0x1
        self.overflow_flag = data >> 6 & 0x1
        self.sign_flag = data >> 7 & 0x1

    def check_zs_flag(self, data):
        self.sign_flag = 1 if (data & 0x80) else 0
        self.zero_flag = 1 if (data == 0) else 0


class CPU(object):
    def __init__(self, file, main_memory, save_memory, ppu):
        self.file = file
        self.mmc_type = 0
        self.save_memory = main_memory
        self.main_memory = save_memory
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
        self.status_register = StatusRegister()

        # (op_name, addressing_mode, instr_bytes, instr_cycles)
        #  1:accumulator, 2:implied_addressing, 3:immediate_addressing, 4:absolute_addressing, 5:zero_page_absolute_addressing
        # 6:absolute_x_indexed_addressing, 7:absolute_y_indexed_addressing 8:zero_page_x_indexed_addressing,
        # 9:zero_page_y_indexed_addressing, 10:indirect_addressing  11:pre_indexed_indirect_addressing
        # 12:post_indexed_indirect_addressing, 13:relative_addressing
        #                          0           1              2              3            4              5              6             7             8              9              A            B           C               D           E             F
        self.op_detail = [('BRK', 2, 1, 7), ('ORA', 11, 2, 6), 'STP', ('SLO', 11, 2, 8), ('NOP', 5, 2, 3),
                          ('ORA', 5, 2, 3), ('ASL', 5, 2, 5), ('SLO', 5, 2, 5), ('PHP', 2, 1, 3), ('ORA', 3, 2, 2),
                          ('ASL', 1, 1, 2), ('ANC', 3, 2, 2), ('NOP', 4, 3, 4), ('ORA', 4, 3, 4), ('ASL', 4, 3, 6),
                          ('SLO', 4, 3, 6),  # 0
                          ('BPL', 13, 2, 2), ('ORA', 12, 2, 5), 'STP', ('SLO', 12, 2, 8), ('NOP', 8, 2, 4),
                          ('ORA', 8, 2, 4), ('ASL', 8, 2, 6), ('SLO', 8, 2, 6), ('CLC', 2, 1, 2), ('ORA', 7, 3, 4),
                          ('NOP', 2, 1, 2), ('SLO', 7, 3, 7), ('NOP', 6, 3, 4), ('ORA', 6, 3, 4), ('ASL', 6, 3, 7),
                          ('SLO', 6, 3, 7),  # 1
                          ('JSR', 4, 3, 6), ('AND', 11, 2, 6), 'STP', ('RLA', 11, 2, 8), ('BIT', 5, 2, 3),
                          ('AND', 5, 2, 3), ('ROL', 5, 2, 5), ('RLA', 5, 2, 5), ('PLP', 2, 1, 4), ('AND', 3, 2, 2),
                          ('ROL', 1, 1, 2), 'ANC', ('BIT', 4, 3, 4), ('AND', 4, 3, 4), ('ROL', 4, 3, 6),
                          ('RLA', 4, 3, 6),  # 2
                          ('BMI', 13, 2, 2), ('AND', 12, 2, 5), 'STP', ('RLA', 12, 2, 8), ('NOP', 8, 2, 4),
                          ('AND', 8, 2, 4), ('ROL', 8, 2, 6), ('RLA', 8, 2, 6), ('SEC', 2, 1, 2), ('AND', 7, 3, 4),
                          ('NOP', 2, 1, 2), ('RLA', 7, 3, 7), ('NOP', 6, 3, 4), ('AND', 6, 3, 4), ('ROL', 6, 3, 7),
                          ('RLA', 6, 3, 7),  # 3
                          ('RTI', 2, 1, 6), ('EOR', 11, 2, 6), 'STP', ('SRE', 11, 2, 8), ('NOP', 5, 2, 3),
                          ('EOR', 5, 2, 3), ('LSR', 5, 2, 5), ('SRE', 5, 2, 5), ('PHA', 2, 1, 3), ('EOR', 3, 2, 2),
                          ('LSR', 1, 1, 2), ('ALR', 3, 2, 2), ('JMP', 4, 3, 3), ('EOR', 4, 3, 4), ('LSR', 4, 3, 6),
                          ('SRE', 4, 3, 6),  # 4
                          ('BVC', 13, 2, 2), ('EOR', 12, 2, 5), 'STP', ('SRE', 12, 2, 8), ('NOP', 8, 2, 4),
                          ('EOR', 8, 2, 4), ('LSR', 8, 2, 6), ('SRE', 8, 2, 6), ('CLI', 2, 1, 2), ('EOR', 7, 3, 4),
                          ('NOP', 2, 1, 2), ('SRE', 7, 3, 7), ('NOP', 6, 3, 4), ('EOR', 6, 3, 4), ('LSR', 6, 3, 7),
                          ('SRE', 6, 3, 7),  # 5
                          ('RTS', 2, 1, 6), ('ADC', 11, 2, 6), 'STP', ('RRA', 11, 2, 8), ('NOP', 5, 2, 3),
                          ('ADC', 5, 2, 3), ('ROR', 5, 2, 5), ('RRA', 5, 2, 5), ('PLA', 2, 1, 4), ('ADC', 3, 2, 2),
                          ('ROR', 1, 1, 2), ('ARR', 3, 2, 2), ('JMP', 10, 3, 5), ('ADC', 4, 3, 4), ('ROR', 4, 3, 6),
                          ('RRA', 4, 3, 6),  # 6
                          ('BVS', 13, 2, 2), ('ADC', 12, 2, 5), 'STP', ('RRA', 12, 2, 8), ('NOP', 8, 2, 4),
                          ('ADC', 8, 2, 4), ('ROR', 8, 2, 6), ('RRA', 8, 2, 6), ('SEI', 2, 1, 2), ('ADC', 7, 3, 4),
                          ('NOP', 2, 1, 2), ('RRA', 7, 3, 7), ('NOP', 6, 3, 4), ('ADC', 6, 3, 4), ('ROR', 6, 3, 7),
                          ('RRA', 6, 3, 7),  # 7
                          ('NOP', 3, 2, 2), ('STA', 11, 2, 6), ('NOP', 3, 2, 2), ('SAX', 11, 2, 6), ('STY', 5, 2, 3),
                          ('STA', 5, 2, 3), ('STX', 5, 2, 3), ('SAX', 5, 2, 3), ('DEY', 2, 1, 2), ('NOP', 3, 2, 2),
                          ('TXA', 2, 1, 2), 'XAA', ('STY', 4, 3, 4), ('STA', 4, 3, 4), ('STX', 4, 3, 4),
                          ('SAX', 4, 3, 4),  # 8
                          ('BCC', 13, 2, 2), ('STA', 12, 2, 6), 'STP', 'AHX', ('STY', 8, 2, 4), ('STA', 8, 2, 4),
                          ('STX', 9, 2, 4), ('SAX', 9, 2, 4), ('TYA', 2, 1, 2), ('STA', 7, 3, 5), ('TXS', 2, 1, 2),
                          'TAS', 'SHY', ('STA', 6, 3, 5), 'SHX', 'AHX',  # 9
                          ('LDY', 3, 2, 2), ('LDA', 11, 2, 6), ('LDX', 3, 2, 2), ('LAX', 11, 2, 6), ('LDY', 5, 2, 3),
                          ('LDA', 5, 2, 3), ('LDX', 5, 2, 3), ('LAX', 5, 2, 3), ('TAY', 2, 1, 2), ('LDA', 3, 2, 2),
                          ('TAX', 2, 1, 2), 'LAX', ('LDY', 4, 3, 4), ('LDA', 4, 3, 4), ('LDX', 4, 3, 4),
                          ('LAX', 4, 3, 4),  # A
                          ('BCS', 13, 2, 2), ('LDA', 12, 2, 5), 'STP', ('LAX', 12, 2, 5), ('LDY', 8, 2, 4),
                          ('LDA', 8, 2, 4), ('LDX', 9, 2, 4), ('LAX', 9, 2, 4), ('CLV', 2, 1, 2), ('LDA', 7, 3, 4),
                          ('TSX', 2, 1, 2), 'LAS', ('LDY', 6, 3, 4), ('LDA', 6, 3, 4), ('LDX', 7, 3, 4),
                          ('LAX', 7, 3, 4),  # B
                          ('CPY', 3, 2, 2), ('CMP', 11, 2, 6), ('NOP', 3, 2, 2), ('DCP', 11, 2, 8), ('CPY', 5, 2, 3),
                          ('CMP', 5, 2, 3), ('DEC', 5, 2, 5), ('DCP', 5, 2, 5), ('INY', 2, 1, 2), ('CMP', 3, 2, 2),
                          ('DEX', 2, 1, 2), ('AXS', 3, 2, 2), ('CPY', 4, 3, 4), ('CMP', 4, 3, 4), ('DEC', 4, 3, 6),
                          ('DCP', 4, 3, 6),  # C
                          ('BNE', 13, 2, 2), ('CMP', 12, 2, 5), 'STP', ('DCP', 12, 2, 8), ('NOP', 8, 2, 4),
                          ('CMP', 8, 2, 4), ('DEC', 8, 2, 6), ('DCP', 8, 2, 6), ('CLD', 2, 1, 2), ('CMP', 7, 3, 4),
                          ('NOP', 2, 1, 2), ('DCP', 7, 3, 7), ('NOP', 6, 3, 4), ('CMP', 6, 3, 4), ('DEC', 6, 3, 7),
                          ('DCP', 6, 3, 7),  # D
                          ('CPX', 3, 2, 2), ('SBC', 11, 2, 6), ('NOP', 3, 2, 2), ('ISC', 11, 2, 8), ('CPX', 5, 2, 3),
                          ('SBC', 5, 2, 3), ('INC', 5, 2, 5), ('ISC', 5, 2, 5), ('INX', 2, 1, 2), ('SBC', 3, 2, 2),
                          ('NOP', 2, 1, 2), ('SBC', 3, 2, 2), ('CPX', 4, 3, 4), ('SBC', 4, 3, 4), ('INC', 4, 3, 6),
                          ('ISC', 4, 3, 6),  # E
                          ('BEQ', 13, 2, 2), ('SBC', 12, 2, 5), 'STP', ('ISC', 12, 2, 8), ('NOP', 8, 2, 4),
                          ('SBC', 8, 2, 4), ('INC', 8, 2, 6), ('ISC', 8, 2, 6), ('SED', 2, 1, 2), ('SBC', 7, 3, 4),
                          ('NOP', 2, 1, 2), ('ISC', 7, 3, 7), ('NOP', 6, 3, 4), ('SBC', 6, 3, 4), ('INC', 6, 3, 7),
                          ('ISC', 6, 3, 7),  # F
                          ]

    def push(self, data):
        self.write(0x100 | self.stack_pointer, data)
        self.stack_pointer -= 1

    def pop(self):
        self.stack_pointer += 1
        return self.read(0x100 | self.stack_pointer)

    def read(self, addr):
        if self.mmc_type == 0:
            if addr in range(0, 0x2000):
                return self.main_memory.read(addr & 0x7ff)
            elif addr in range(0x2000, 0x4000):
                addr = addr & 0x7 + 0x2000
                return self.ppu.read_register(addr)
            elif addr == 0x4014:
                assert 0, "TODO"
            elif addr == 0x4016:
                ret = self.input_status[self.input_index & self.input_mask]
                self.input_index += 1
                return ret
            elif addr in range(0x4000, 0x4020):
                return 0  # TODO
            elif addr in range(0x6000, 0x8000):
                assert 0, "TODO: sram"  # return self.save_memory.read(addr & 0x1fff)
            elif addr in range(0x8000, 0x10000):
                return self.file.prg_rom[addr & 0x3fff]
            else:
                assert 0, "TODO"
        else:
            assert 0, "TODO"

    def write(self, addr, data):
        if self.mmc_type == 0:
            if addr in range(0, 0x2000):
                self.main_memory.write(addr & 0x7ff, data)
            elif addr in range(0x2000, 0x4000):
                addr = addr & 0x7 + 0x2000
                self.ppu.write_register(addr, data)
            elif addr == 0x4014:
                assert 0
            elif addr == 0x4016:
                self.input_mask = 0x0 if data & 1 else 0x7
                if data & 1:
                    self.input_index = 0
            elif addr in range(0x4000, 0x4020):
                pass
            elif addr in range(0x6000, 0x8000):
                assert 0, "TODO: sram"  # return self.save_memory.write(addr & 0x1fff, data)
            elif addr in range(0x8000, 0x10000):
                assert 0, "Can't write to ROM"
            else:
                assert 0, "TODO"
        else:
            assert 0, "TODO"

    def exec(self):
        addr = self.program_counter
        instruction, addressing_mode, instr_bytes = self.op_detail[self.read(addr)][0], self.op_detail[self.read(addr)][
            1], self.op_detail[self.read(addr)][2]

        operand = addressing(addressing_mode, self)
        self.program_counter += instr_bytes

        {
            'JMP': JMP, 'LDX': LDX, 'LAX': LAX, 'LDY': LDY, 'LAY': LAY, 'STX': STX, 'SAX': SAX,
            'STY': STY, 'ADC': ADC, 'SBC': SBC, 'INC': INC, 'DEC': DEC, 'INX': INX, 'DEX': DEX,
            'INY': INY, 'DEY': DEY, 'TAX': TAX, 'TAY': TAY, 'TXA': TXA, 'TYA': TYA, 'TSX': TSX,
            'TXS': TXS, 'JSR': JSR, 'RTS': RTS, 'RTI': RTI, 'SEC': SEC, 'SEI': SEI, 'SED': SED,
            'CLD': CLD, 'CLV': CLV, 'BCS': BCS, 'CLC': CLC, 'NOP': NOP, 'BCC': BCC, 'LDA': LDA,
            'STA': STA, 'BEQ': BEQ, 'BNE': BNE, 'BIT': BIT, 'BVS': BVS, 'BVC': BVC, 'BMI': BMI,
            'BPL': BPL, 'PHA': PHA, 'PLA': PLA, 'PHP': PHP, 'PLP': PLP, 'AND': AND, 'ORA': ORA,
            'EOR': EOR, 'CMP': CMP, 'CPX': CPX, 'CPY': CPY, 'LSR': LSR, 'ROR': ROR, 'ROL': ROL,
            'ASL': ASL, 'DCP': DCP, 'SLO': SLO, 'SRE': SRE, 'ISC': ISC, 'RLA': RLA, 'RRA': RRA,
            # 'BRK': BRK
        }[instruction](addressing_mode, self, operand)

    def nmi(self):
        self.ppu.ppu_status.set(self.ppu.ppu_status.value() | 0x80)
        if self.ppu.ppu_ctrl.value() & 0x80:
            self.push(self.program_counter >> 8)
            self.push(self.program_counter)
            self.push(self.status_register.value())
            self.status_register.irq_disabled_flag = 1
            laddr = self.read(self._NMI)
            haddr = self.read(self._NMI + 1)
            self.program_counter = laddr | haddr << 8

    def disassemble(self):
        def _get_operands(mode, param):
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
            elif mode == 6:
                return '$' + fromat(param[0] | param[1] << 8) + ',X'
            elif mode == 7:
                return '$' + fromat(param[0] | param[1] << 8) + ',Y'
            elif mode == 8:
                return '$' + fromat(param[0]) + ',X'
            elif mode == 9:
                return '$' + fromat(param[0]) + ',Y'
            elif mode == 10:
                return '($' + fromat(param[0] | param[1] << 8) + ')'
            elif mode == 11:
                return '($' + fromat(param[0]) + ',X)'
            elif mode == 12:
                return '($' + fromat(param[0]) + '),Y'
            elif mode == 13:
                return '$' + fromat(self.program_counter + 2 + (param[0] if not param[0] & 0x80 else param[0] - 256))
            else:
                assert 0, 'Error addressing mode!'

        addr = self.program_counter
        op_index = self.read(addr)
        instruction, addressing_mode, instr_bytes = self.op_detail[op_index][0], self.op_detail[op_index][1], \
                                                    self.op_detail[op_index][2]

        operand_bytes = []
        for i in range(instr_bytes - 1):
            operand_bytes += [self.read(addr + i + 1)]
        # print('%s  %s %-7s ' % (fromat(addr), fromat(op_index), list_to_hex_str(operand_bytes)), end='')
        print('%s  ' % (fromat(addr)), end='')

        operands = _get_operands(addressing_mode, operand_bytes)
        print('%s %-7s ' % (instruction, operands), end='')

        print('A:%s X:%s Y:%s P:%s SP:%s' % (
            fromat(self.accumulator), fromat(self.x_index_register), fromat(self.y_index_register),
            fromat(self.status_register.value()), fromat(self.stack_pointer)), end='')

    def run(self):
        for _ in range(100000):  # while True:
            self.disassemble()
            self.exec()

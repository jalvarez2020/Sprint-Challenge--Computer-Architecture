"""CPU functionality."""

import sys
LDI = 0b10000010
RN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
PRN = 0b01000111

class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.reg[7] = 255
        self.sp = self.reg[7]
        self.flag = 0b00000000

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        address = 0
        if len(sys.argv) != 2:
            print(f"usage: {sys.argv[0]} filename")
            sys.exit(1)
        
        try:
            with open(sys.argv[1]) as file:
                for line in file:
                    if line[0].startswith('0') or line[0].startswith('1'):
                        num = line.split('#')[0]
                        num = num.strip()
                        self.ram[address] = int(num, 2)
                        address += 1
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} Not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            A = self.reg[reg_a]
            B = self.reg[reg_b]
            if A == B:
                self.flag = 0b00000001
            if A > B:
                self.flag = 0b00000010
            if A < B:
                self.flag = 0b00000100

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):

        running = True

        while running:
            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            number_of_operands = int(IR) >> 6
            
            self.pc += (1 + number_of_operands)

            if IR == HLT:
                running = False
            
            elif IR == LDI:
                self.reg[operand_a] = operand_b
            
            elif IR == PRN:
                print(self.reg[operand_a])
            
            elif IR == MUL:
                self.alu("MUL", operand_a, operand_b)
            
            elif IR == PUSH:
                self.sp = (self.sp % 257) - 1
                self.ram[self.sp] = self.reg[operand_a]

            elif IR == POP:
                self.reg[operand_a] = self.ram[self.sp]
                self.sp = (self.sp % 257) + 1
            
            elif IR == CALL:
                self.sp -= 1
                self.ram[self.sp] = self.pc + 2

            elif IR == CMP:
                self.alu("CMP", operand_a, operand_b)
            
            elif IR == JMP:
                self.pc = self.reg[operand_a]
            
            elif IR == JEQ:
                if IR == self.flag:
                    self.pc = self.reg[operand_a]
            
            elif IR == JNE:
                if self.flag & 0b00000001 == 0b00000000:
                    self.pc = self.reg[operand_a]
            
            elif IR == RET:
                self.pc = self.ram[self.sp]

            else:
                print('Error')
                sys.exit()
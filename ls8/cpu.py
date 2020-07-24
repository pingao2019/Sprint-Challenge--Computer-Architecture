"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
POP = 0b01000110
PUSH= 0b01000101 
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """""You’ll have to convert the binary strings to integer values to store in RAM. The built-in int() function can do that when you specify a number base as the second argument:x = int("1010101", 2)  # Convert binary string to integer."""
         
    def __init__(self):
        self.ram = [0]*256  
        self.register = [0] * 8   
        self.pc = 0 #(program count)        
        self.sp = 7 

        self.branch= {
            HLT: self.hlt,
            LDI: self.ldi,
            PRN: self.prn,            
            PUSH: self.push,
            POP: self.pop,
            CALL: self.call,
            RET: self.ret,            
            CMP: self.cmp,
            JMP: self.jmp,
            JEQ: self.jeq,
            JNE: self.jne

        }

        self.flag = 0b00000000
        self.running = True


    #access the RAM inside the CPU object. ram_read() accept the address to read and return the value stored there.
    def ram_read(self, index):        
        return self.ram[index]

    #should accept a value to write, and the address to write it to
    def ram_write(self, index, value):        
        self.ram[index] = value

    def load(self, filename):
        """Load a program into memory. open a file, read in its contents   and save appropriate data into RAM.You’ll have to convert the binary strings to integer values to store in RAM.""" 

        address = 0        
        with open(filename) as f:            
            for line in f:
                line = line.split("#")
                try:
                    line = int(line[0], 2)
                except ValueError:
                    continue
                self.ram_write(address, line)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations(Arithmetic logic unit). MUL is the responsiblity of the ALU,`MUL registerA registerB` Multiply the values in two registers together and store the result in registerA."""
        """The flags register `FL` holds the current flags status. These flags can change based on the operands given to the `CMP` opcode. The register is made up of 8 bits. If a particular bit is set, that flag is "true"."""
        """ `CMP registerA registerB`.Compare the values in two registers. If they are equal, set the Equal `E` flag to 1, otherwise set it to 0. If registerA is less than registerB, set the Less-than `L` flag to 1, otherwise set it to 0. If registerA is greater than gisterB, set the Greater-than `G` flag  to 1, otherwise set it to 0. """
        
        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
         
        if op == "CMP":  
            if self.register[reg_a] == self.register[reg_b]:
                self.flag = 0b00000001
            elif self.register[reg_a] < self.register[reg_b]:
                self.flag = 0b00000100
            elif self.register[reg_a] > self.register[reg_b]:
                self.flag = 0b00000010
            else:
                self.flag = 0b00000000

        else:
            raise Exception("Unsupported ALU operation")
            # sys.exit(1)

    def trace(self):
        """Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.Some instructions requires up to the next two bytes of data after the PC in memory to perform operations on. Sometimes the byte value is a register number.  Using ram_read(), read the bytes at PC+1 and PC+2 from RAM into variables operand_a and operand_b in case the instruction needs them.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()

    def run(self):
        """Run the CPU. Read the memory address that’s stored in register PC, and store that result in IR, the Instruction Register"""
        while self.running:
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            ir = self.ram_read(self.pc)
            if ir in self.branch:
                self.branch[ir](operand_a, operand_b)
            else:
                print(f"Uknown instructions {ir} at address {self.pc}")
                sys.exit(1)

    def hlt(self, operand_a, operand_b):
        self.running = False

    def ldi(self, operand_a, operand_b):
        """load "immediate".The byte value of some instruction is a constant value for LDI."""
        self.register[operand_a] = operand_b
        self.pc += 3

    def prn(self, operand_a, operand_b):
        """ PRN register` pseudo-instruction, Print numeric value stored in the given register.print to the console the decimal integer value that is stored in the given register."""
        print(self.register[operand_a])
        self.pc += 2

    

    def push(self, operand_a, operand_b):
        """PUSH a value in a register onto the stack, decrement stack pointer.Store in memory/Store the value in the register into RAM at the address stored in SP."""
        value = self.register[operand_a]   
        self.register[self.sp] -= 1  
        self.ram_write(self.register[self.sp], value)
        self.pc += 2

    def pop(self, operand_a, operand_b):
        """`POP register`,pop value at the top of the stack into the given register.Copy the value from the address pointed to by `SP` to the given egister. Increment `SP`. `PUSH register`Push the value in the given register on the stack.1. Decrement the `SP`.2. Copy the value in the given register to the address pointed to by`SP`"""
        value = self.ram[self.register[self.sp]]
        self.register[operand_a] = value
         
        self.sp += 1 # Increment SP
        self.pc += 2

    def call(self, operand_a, operand_b):
        """CALL register,calls a subroutine (function) at the address stored in the register. 1. The address of the instruction _directly after_ `CALL` is  pushed onto the stack. This allows us to return to where we left off when the subroutine finishes executing. 2. The PC is set to the address stored in the given register. We jump to that location in RAM and execute the first instruction in the subroutine. The PC can move forward or backwards from its current location."""

        value = self.pc + 2  # Get address of the next instruction   
         
        subroutine_addr = self.register[operand_a]
        self.register[self.sp] -= 1
        self.ram[self.register[self.sp]] = value
        self.pc = subroutine_addr

    def ret(self, operand_a, operand_b):
        """ Get return address from the top of the stack ,pop value from top of the stack and store it in the PC.""" 

        return_addr = self.register[self.sp]   
        self.pc = self.ram_read(return_addr)
        self.register[self.sp] += 1    

    def cmp(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)
        self.pc += 3

    def jeq(self, operand_a, operand_b):
        """If `equal` flag is set (true), jump to the address stored in the given register. """
        if self.flag == 0b00000001:
            #self.flag == [1]
            self.pc = self.register[operand_a]
        else:
            self.pc += 2

    def jne(self, operand_a, operand_b):
        """`JNE register` if `E` flag is clear (false, 0), jump to the address stored in the given register."""
        
        if self.flag != 0b00000001:            
            self.pc = self.register[operand_a]
        else:
            self.pc += 2

    def jmp(self, operand_a, operand_b):
        """`JMP register`Jump to the address stored in the given register.Set the `PC` to the address stored in the given register."""

        self.pc = self.register[operand_a]
        print(f'pc instruction stored in {self.pc}')




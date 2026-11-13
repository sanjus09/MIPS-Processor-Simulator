#hard coding the memory address values..!
TEXT_BASE = 0x00400000
DATA_BASE = 0x10010000

FUNC_CODES = {
    "100000": "add",
    "100010": "sub",
    "100100": "and",
    "100101": "or",
    "101010": "slt",
    "000010": "srl",
    "000000": "sll",
    "001000": "jr",
    "001100": "syscall"
}

OP_CODES = {
    "001000": "addi",
    "001101": "ori",
    "001100": "andi",
    "001111": "lui",
    "100011": "lw",
    "101011": "sw",
    "100000": "lb",
    "000100": "beq",
    "000101": "bne", 
    "000010": "j",
    "000011": "jal"
}

REG_NAME_TO_INDEX = {
    "$zero": 0, "$at": 1, "$v0": 2, "$v1": 3,
    "$a0": 4, "$a1": 5, "$a2": 6, "$a3": 7,
    "$t0": 8, "$t1": 9, "$t2": 10, "$t3": 11,
    "$t4": 12, "$t5": 13, "$t6": 14, "$t7": 15,
    "$s0": 16, "$s1": 17, "$s2": 18, "$s3": 19,
    "$s4": 20, "$s5": 21, "$s6": 22, "$s7": 23,
    "$t8": 24, "$t9": 25, "$k0": 26, "$k1": 27,
    "$gp": 28, "$sp": 29, "$fp": 30, "$ra": 31
}

label_to_address = {
    "rows":    DATA_BASE + 0,
    "cols":    DATA_BASE + 4,
    "matrix1": DATA_BASE + 8,
    "matrix2": DATA_BASE + 8 + 256,
    "matrix3": DATA_BASE + 8 + 256 + 256,
    "deltas":  DATA_BASE + 8 + 256 + 256 + 256
}

jump_count = 0
r_count = 0
i_count = 0


register_file = [0] * 32
#word addressable data memory (1KB / 4B per word = 256 words) enough..?
data_memory = [0] * (1024 // 4)
#byte addressable memory for ".byte" directives (gave a lot of trouble)
byte_memory = {}


def bin16_to_signed_int(bstr):
    #if negative number... 2's complement..!
    if bstr[0] == '1':
        return int(bstr, 2) - (1 << 16)
    return int(bstr, 2)

def addr_to_data_index(addr):
    return (addr - DATA_BASE) // 4

#rows = 8, cols = 8
data_memory[addr_to_data_index(label_to_address["rows"])] = 8
data_memory[addr_to_data_index(label_to_address["cols"])] = 8

#deltas => 16 bytes
delta_vals = [-1, -1, -1, 0, -1, 1, 0, -1, 0, 1, 1, -1, 1, 0, 1, 1]
for i, b in enumerate(delta_vals):
    byte_memory[label_to_address["deltas"] + i] = b

def execute_r_format(funct, rs, rt, rd, shamt, pc):
    global r_count
    r_count += 1
    
    #add
    if funct == "100000":
        register_file[rd] = register_file[rs] + register_file[rt]
        
    #sub
    elif funct == "100010": 
        register_file[rd] = register_file[rs] - register_file[rt]
    
    #and
    elif funct == "100100":  
        register_file[rd] = register_file[rs] & register_file[rt]
        
    #or
    elif funct == "100101": 
        register_file[rd] = register_file[rs] | register_file[rt]
        
    #slt
    elif funct == "101010":  
        register_file[rd] = int(register_file[rs] < register_file[rt])
        
    #srl
    elif funct == "000010":  
        register_file[rd] = (register_file[rt] & 0xFFFFFFFF) >> shamt

    #sll
    elif funct == "000000":  
        register_file[rd] = (register_file[rt] & 0xFFFFFFFF) << shamt

    #jr
    elif funct == "001000":  
        #convert byte address to word index
        next_pc = (register_file[31])  
        register_file[0] = 0
        return next_pc
    
    # syscall
    elif funct == "001100":
        #exit the program..!
        if register_file[2] == 10: 
            print("Program requested exit")
            return -1 
        
    
    #maintaint this register as zero..??
    register_file[0] = 0  
    return None


def execute_i_and_j_format(opcode, rs, rt, imm, pc):
    global jump_count
    global i_count

    #J-type
    if opcode in ("000010", "000011"):  
        jump_count += 1
    #I-type
    else:  
        i_count += 1

    next_pc = pc + 1

    #addi
    if opcode == "001000":  
        register_file[rt] = register_file[rs] + imm

    #ori
    elif opcode == "001101":  
        register_file[rt] = register_file[rs] | (imm & 0xFFFF)
    
    #andi
    elif opcode == "001100":  
        register_file[rt] = register_file[rs] & (imm & 0xFFFF)

    #lui
    elif opcode == "001111":  
        register_file[rt] = (imm & 0xFFFF) << 16
    
    #memory loads / stores

    #lw
    elif opcode == "100011":  
        addr = register_file[rs] + imm
        idx = addr_to_data_index(addr)
        if idx < 0 or idx >= len(data_memory):
            raise IndexError(f"LW out of range at PC {pc}: addr {hex(addr)} idx {idx}")
        register_file[rt] = data_memory[idx]

    #sw
    elif opcode == "101011":  
        addr = register_file[rs] + imm
        idx = addr_to_data_index(addr)

        if idx < 0 or idx >= len(data_memory):
            raise IndexError(f"SW out of range at PC {pc}: addr {hex(addr)} idx {idx}")
        
        data_memory[idx] = register_file[rt]

    #lb (this is weird and caused a lot of trouble..!)
    elif opcode == "100000":  
        addr = register_file[rs] + imm
        value = byte_memory.get(addr, 0)

        if value & 0x80:
            value = value | 0xFFFFFF00
        register_file[rt] = value

    
    #branche instructions

    #beq
    elif opcode == "000100":  
        if register_file[rs] == register_file[rt]:
            next_pc = pc + 1 + (imm)

    #bne
    elif opcode == "000101":  
        if register_file[rs] != register_file[rt]:
            next_pc = pc + 1 + (imm)
    
    #jump statements

    #j
    elif opcode == "000010":  
        target_addr = imm << 2
        next_pc = (target_addr - TEXT_BASE) // 4

    #jal
    elif opcode == "000011":  
        #save to $ra
        register_file[31] = pc + 1

        #the lower 26 bits from the instruction 
        target_offset = imm << 2

        #get the upper 4 bits from the current PC
        pc_addr = TEXT_BASE + pc * 4
        pc_plus4 = pc_addr + 4
        upper_bits = pc_plus4 & 0xF0000000

        #combine to form target address
        target_addr = upper_bits | target_offset

        #convert to word index
        next_pc = (target_addr - TEXT_BASE) // 4
    
    register_file[0] = 0
    return next_pc


def instruction_decode(instruction, pc):
    opcode = instruction[:6]
    
    #R format
    if opcode == "000000":
        rs = int(instruction[6:11], 2)
        rt = int(instruction[11:16], 2)
        rd = int(instruction[16:21], 2)
        shamt = int(instruction[21:26], 2)
        funct = instruction[26:]
        return execute_r_format(funct, rs, rt, rd, shamt, pc)
    
    #I/J formats
    rs = int(instruction[6:11], 2)
    rt = int(instruction[11:16], 2)
    imm_field = instruction[16:]
    
    #for jumps, immediate is the raw value (not offset..!)
    #j and jal
    if opcode in ("000010", "000011"):
        rs= None 
        rt = None
        imm = int(instruction[6:], 2)

    #lui
    elif opcode == "001111":
        #unsigned for lui
        imm = int(imm_field, 2)  
    else:
        imm = bin16_to_signed_int(imm_field)
    
    return execute_i_and_j_format(opcode, rs, rt, imm, pc)


def print_matrix_from_memory(matrix_label, rows=8, cols=8):
    base_addr = label_to_address[matrix_label]
    print(f"\n{matrix_label.upper()} ({hex(base_addr)}):")
    for i in range(rows):
        row_vals = []
        for j in range(cols):
            addr = base_addr + (i * cols + j) * 4
            idx = addr_to_data_index(addr)
            row_vals.append(str(data_memory[idx]))
        print(" ".join(row_vals))


def main():
    #read machine code
    with open("machine_code.txt") as f:
        instr_mem = [line.strip() for line in f if line.strip()]
    
    print(f"Loaded {len(instr_mem)} instructions")
    
    #initialize all the needed values..!
    pc = 0
    clock = 0
    executed_pcs = set()
    instruction_count = 0
    
    
    while 0 <= pc < len(instr_mem):
        instr = instr_mem[pc]
        executed_pcs.add(pc)
        instruction_count += 1
        
        try:
            next_pc = instruction_decode(instr, pc)
            #exit-ed via syscall
            if next_pc == -1:  
                break
            pc = next_pc if next_pc is not None else pc + 1
            clock += 5
        except Exception as e:
            print(f"Error at PC={pc} (instruction: {instr}): {e}")
            break
    
    
    #final statistics
    #clock + 5 cuz the last instruction gets terminated before the clock for it gets counted..!
    print(f"\nTotal clock cycles: {clock + 5}")
    print(f"Total instructions in file: {len(instr_mem)}")
    print(f"Instructions executed: {instruction_count}")
    print(f"Unique PCs executed: {len(executed_pcs)}")

    print_matrix_from_memory("matrix1")
    print_matrix_from_memory("matrix2")
    print_matrix_from_memory("matrix3")

    print(f"\nR instructions => {r_count}")
    print(f"I instructions => {i_count}")
    print(f"J instructions => {jump_count}")


if __name__ == "__main__":
    main()

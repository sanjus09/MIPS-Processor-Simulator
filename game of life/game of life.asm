.data
rows:     .word 8
cols:     .word 8
matrix1:  .space 256    # 8x8 matrix (4 bytes per element)
matrix2:  .space 256    #          ,,
matrix3:  .space 256    #          ,,
deltas: 
    .byte -1, -1   # Up-left
    .byte -1, 0    # Up
    .byte -1, 1    # Up-right
    .byte 0, -1    # Left
    .byte 0, 1     # Right
    .byte 1, -1    # Down-left
    .byte 1, 0     # Down
    .byte 1, 1     # Down-right
message0: .asciiz "The parent generation is: "
message1: .asciiz "The 1st generation is: "
message2: .asciiz "The 2nd generation is: "

.text
main:
    # Load matrix dimensions
    lw $s0, rows        # $s0 = 8 (rows)
    lw $s1, cols        # $s1 = 8 (cols)
    
    ####### GENERATE MATRIX 1 #######

    la $t6, matrix1     # Base address of matrix1
    addi $t2, $0, 0           # Row counter (i)
outer_loop1:
    beq $t2, $s0, generate_next_generations  # Proceed after matrix1
    addi $t3, $0, 0           # Column counter (j)
inner_loop1:
    beq $t3, $s1, next_row1
    # Generate value: (i + j) % 2
    add $t4, $t2, $t3
    andi $t5, $t4, 1
    # Calculate address for matrix1[i][j]
    sll $t7, $t2, 5    # row_offset = i * 32
    sll $t8, $t3, 2     # col_offset = j * 4
    add $t9, $t7, $t8
    add $t9, $t9, $t6
    sw $t5, 0($t9)
    addi $t3, $t3, 1
    j inner_loop1
next_row1:
    addi $t2, $t2, 1
    j outer_loop1

generate_next_generations:
    # Generate Matrix 2
    la $a0, matrix1
    la $a1, matrix2
    jal generate_next_generation
    
    # Generate Matrix 3
    la $a0, matrix2
    la $a1, matrix3
    jal generate_next_generation
    
    j print_all_matrices

# Function to generate next generation where $a0 = source matrix and $a1 = destination matrix #

generate_next_generation:    
    addi $t2, $0, 0           # Row counter (i)
row_loop:
    beq $t2, $s0, done_rows
    addi $t3, $0, 0           # Column counter (j)
col_loop:
    beq $t3, $s1, next_row
    # Compute neighbor sum
    addi $t5, $0, 0           # sum = 0
    la $s2, deltas      # Load deltas array
    addi $t0, $0, 0           # Neighbor counter
sum_loop:
    beq $t0, 8, apply_rules
    # Load delta values
    lb $t8, 0($s2)      # delta_row
    lb $t9, 1($s2)      # delta_col
    # Calculate neighbor coordinates
    add $t4, $t2, $t8   # neighbor_row
    add $t1, $t3, $t9   # neighbor_col
    # Check boundaries
    slt $a3, $t4, $zero              # pseudo instruction of blt $t4, $zero, skip_neighbor
    bne $a3, $zero, skip_neighbor

    slt $a3, $t4, $s0              # pseudo instruction of bge $t4, $s0, skip_neighbor
    beq $a3, $zero, skip_neighbor

    slt $a3, $t1, $zero            # pseudo instruction of blt $t1, $zero, skip_neighbor
    bne $a3, $zero, skip_neighbor

    slt $a3, $t1, $s1              # pseudo instruction of bge $t1, $s1, skip_neighbor
    beq $a3, $zero, skip_neighbor

    # Calculate source address
    sll $t7, $t4, 5    # row_offset
    sll $t8, $t1, 2     # col_offset
    add $t7, $t7, $t8
    add $t7, $t7, $a0   # source address
    lw $t8, 0($t7)      # Load neighbor value
    add $t5, $t5, $t8   # Add to sum
skip_neighbor:
    addi $t0, $t0, 1    # Next neighbor
    addi $s2, $s2, 2    # Next delta pair
    j sum_loop
apply_rules:
    # Load current cell state from source
    sll $t7, $t2, 5    # row_offset
    sll $t8, $t3, 2     # col_offset
    add $t9, $t7, $t8
    add $t9, $t9, $a0   # source address
    lw $t4, 0($t9)      # current_state
    # Apply Game of Life rules
    addi $t7, $0, 2           # Underpopulation threshold
    addi $t8, $0, 3           # Overpopulation/reproduction threshold
    beq $t4, $zero, check_dead
    # Ave cell rules
    slt $a3, $t5, $t7              # psuedo instruction of blt $t5, $t7, set_dead
    bne $a3, $zero, set_dead
    slt $a3, $t8, $t5              # psuedo instruction of bgt $t5, $t8, set_dead
    bne $a3, $zero, set_dead

    addi $t4, $0, 1
    j store_state
check_dead:
    bne $t5, $t8, set_dead
    addi $t4, $0, 1
    j store_state
set_dead:
    addi $t4, $zero, 0
store_state:
    # Store new state in destination
    sll $t7, $t2, 5    # row_offset
    sll $t8, $t3, 2     # col_offset
    add $t9, $t7, $t8
    add $t9, $t9, $a1   # destination address
    sw $t4, 0($t9)
    # Next column
    addi $t3, $t3, 1
    j col_loop
next_row:
    addi $t2, $t2, 1
    j row_loop
done_rows:
    jr $ra

###### PRINT ALL MATRICES ######

print_all_matrices:
   addi $v0, $0, 4          # syscall code for print_string
    la $a0, message0    # load address of the message
    syscall

    addi $v0, $0, 11
    addi $a0, $0, 10
    syscall

    # Print Matrix 1
    la $a0, matrix1
    jal print_matrix

    addi $v0, $0, 11
    addi $a0, $0, 10
    syscall

    addi $v0, $0, 4          # syscall code for print_string
    la $a0, message1    # load address of the message
    syscall

    addi $v0, $0, 11
    addi $a0, $0, 10
    syscall

    # Print Matrix 2
    la $a0, matrix2
    jal print_matrix

    addi $v0, $0, 11
    addi $a0, $0, 10
    syscall

    addi $v0, $0, 4          # syscall code for print_string
    la $a0, message2    # load address of the message
    syscall

    addi $v0, $0, 11
    addi $a0, $0, 10
    syscall

    # Print Matrix 3
    la $a0, matrix3
    jal print_matrix

    j exit


# Function to print a matrix where $a0 = base address of matrix #

print_matrix:
    add $t6, $a0, $0        # $t6 = matrix base address
    addi $t2, $0, 0           # Row counter (i)
print_row:
    beq $t2, $s0, print_done
    addi $t3, $0, 0           # Column counter (j)
print_col:
    beq $t3, $s1, print_newline
    # Calculate address
    sll $t7, $t2, 5    # row_offset = i * 32
    sll $t8, $t3, 2     # col_offset = j * 4
    add $t9, $t7, $t8
    add $t9, $t9, $t6   # final address
    lw $a0, 0($t9)
    addi $v0, $0, 1
    syscall
    # Print space (unless last column)
    addi $t3, $t3, 1
    beq $t3, $s1, print_col
    addi $v0, $0, 11
    addi $a0, $0, 32
    syscall
    j print_col
print_newline:
    addi $v0, $0, 11
    addi $a0, $0, 10
    syscall
    addi $t2, $t2, 1
    j print_row
print_done:
    jr $ra

exit:
    addi $v0, $0, 10
    syscall

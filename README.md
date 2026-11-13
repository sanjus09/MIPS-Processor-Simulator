# MIPS Processor Simulator & Game of Life

A Computer Architecture project featuring a custom non-pipelined MIPS processor simulator written in Python alongside a native MIPS assembly implementation of Conway's Game of Life[cite: 8, 9].

## Key Components

* **Non-Pipelined MIPS Simulator ()**: Executes binary machine code across sequential Instruction Fetch (IF), Decode (ID), Execute (EX), Memory (MEM), and Write-Back (WB) stages[cite: 9, 10, 11]. Supports R, I, and J-format instructions (including , , , , , , , , and ) with byte- and word-addressable memory mapping[cite: 9, 10, 11].
* **Conway's Game of Life ()**: Simulates cellular evolution across an 8x8 memory-mapped grid over multiple generations, written entirely without pseudo-instructions to run directly on the custom simulator[cite: 8, 9].

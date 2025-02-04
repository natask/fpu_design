# Parameterized Floating Point Unit (FPU)

This project implements a parameterized floating point unit in SystemVerilog with both cocotb (Python) and SystemVerilog testbenches.

## Project Structure

```
fpu_design/
├── rtl/
│   └── fpu.sv           # Main FPU implementation
├── tb/
│   └── test_fpu.py      # cocotb testbench
├── tb_sv/
│   └── fpu_tb.sv        # SystemVerilog testbench
├── sim/                 # Simulation outputs
└── requirements.txt     # Python dependencies
```

## Features

- Parameterized exponent and mantissa widths
- Supported operations:
  - Addition (000)
  - Subtraction (001)
  - Multiplication (010)
  - Division (011)
- Pipeline stages for improved performance
- Exception handling

## Requirements

- Python 3.6+
- cocotb
- SystemVerilog compatible simulator (e.g., Verilator, ModelSim)

## Running Tests

### Python (cocotb) Tests:
```bash
pip install -r requirements.txt
make -C tb
```

### SystemVerilog Tests:
Use your preferred SystemVerilog simulator to run the testbench in `tb_sv/fpu_tb.sv`

## Implementation Details

The FPU implementation follows IEEE-754 floating-point standard with configurable precision. The design is pipelined for better performance and includes comprehensive error checking.

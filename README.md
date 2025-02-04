# Parameterized Floating Point Unit (FPU)

This project implements a parameterized floating point unit in SystemVerilog with both cocotb (Python) and SystemVerilog testbenches. The verification framework leverages multiple reference models including NumPy's floating-point implementation, direct x86 FPU instructions, and a pure Python model for comprehensive verification.

## Project Structure

```
fpu_design/                    # Project root
├── rtl/
│   └── fpu.sv                # Main FPU RTL implementation
├── tb/
│   ├── fpu_operations.py     # Python FP operations and verification models
│   ├── test_fpu.py          # Basic cocotb testbench
│   └── test_fpu_comprehensive.py  # Comprehensive cocotb testbench
├── tb_sv/
│   └── fpu_tb.sv            # SystemVerilog testbench
├── sim/
│   └── run_tests.py         # Legacy test runner
├── fpu_verification/         # Python verification package
│   ├── __init__.py
│   └── sim/
│       ├── __init__.py
│       └── run_tests.py     # Main test runner with simulator configuration
├── requirements.txt          # Python package dependencies
└── pyproject.toml           # Python package configuration
```

## RTL Implementation Features

### Core FPU Features
- IEEE-754 compliant floating-point operations
- Parameterized design:
  - Configurable exponent width (default: 8 bits)
  - Configurable mantissa width (default: 23 bits)
- Supported operations:
  - Addition (000)
  - Subtraction (001)
  - Multiplication (010)
  - Division (011)

### Performance Optimizations
- Pipelined architecture for higher throughput
- Clock gating for dynamic power reduction
- Operand isolation for static power optimization
- Leading zero detection with priority encoder
- Carry-save adder for efficient addition/subtraction

### Exception Handling
- Overflow/Underflow detection
- NaN handling
- Infinity arithmetic
- Denormal number support

## Verification Framework

### Multi-Model Verification
The verification framework employs three different reference models for comprehensive testing:

1. **NumPy Reference Model**
   - Uses NumPy's highly optimized floating-point implementation
   - Provides IEEE-754 compliant results
   - Handles special cases (NaN, Infinity, denormals)

2. **x86 FPU Instructions**
   - Direct access to x86 hardware FPU via ctypes
   - Hardware-accelerated floating-point operations
   - Provides real hardware reference results

3. **Pure Python Model**
   - Bit-exact floating-point implementation
   - Full visibility into internal operations
   - Useful for debugging and edge cases

### Verification Features
- Automatic test vector generation
- Special case testing (NaN, Infinity, denormals)
- Comprehensive coverage collection
- Waveform generation for debugging
- Performance benchmarking against reference models

## Prerequisites

1. Install UV (Python package installer):
```bash
pip install uv
```

2. Install Icarus Verilog (or your preferred simulator):
```bash
# For Ubuntu/Debian
sudo apt-get install iverilog

# For macOS
brew install icarus-verilog

# For other systems, visit: http://iverilog.icarus.com/
```

## Setting Up Development Environment with UV

1. Create a new virtual environment:
```bash
uv venv
```

2. Activate the virtual environment:
```bash
# On Linux/macOS
source .venv/bin/activate

# On Windows
.venv\Scripts\activate
```

3. Install the project in development mode:
```bash
uv pip install -e .
```

## Running Tests

### Using UV and Entry Points

1. Run all tests using the package entry point:
```bash
uv pip run run-fpu-tests
```

2. Run with specific simulator:
```bash
SIM=icarus uv pip run run-fpu-tests
```

3. Run with SystemVerilog support:
```bash
HDL_TOPLEVEL_LANG=systemverilog SIM=icarus uv pip run run-fpu-tests
```

### Development Workflow

1. Install development dependencies:
```bash
uv pip install -e ".[dev]"
```

2. Run tests with coverage:
```bash
uv pip run pytest --cov=fpu_verification
```

3. Format code:
```bash
uv pip run black .
uv pip run isort .
```

## Configuration Options

### Simulator Options
- `SIM`: Choose simulator (default: icarus)
  - Supported: icarus, verilator
- `HDL_TOPLEVEL_LANG`: HDL language (default: verilog)
  - Supported: verilog, systemverilog

### FPU Parameters
- `EXPONENT_WIDTH`: Width of exponent field (default: 8)
- `MANTISSA_WIDTH`: Width of mantissa field (default: 23)
- `CLOCK_GATING_EN`: Enable clock gating (default: 1)
- `OPERAND_ISOLATION_EN`: Enable operand isolation (default: 1)

## Viewing Waveforms

Waveform files (.vcd) are generated in the sim_build directory. You can view them using:

1. GTKWave:
```bash
gtkwave sim_build/wave.vcd
```

## Contributing

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make changes and ensure tests pass:
```bash
uv pip run pytest
```

3. Format code before committing:
```bash
uv pip run black .
uv pip run isort .
```

## Troubleshooting

1. If you encounter import errors:
```bash
# Reinstall the package
uv pip install -e .
```

2. If simulator is not found:
```bash
# Verify simulator installation
which iverilog  # for Icarus Verilog
```

3. For waveform viewing issues:
```bash
# Install GTKWave
sudo apt-get install gtkwave  # Ubuntu/Debian
brew install gtkwave         # macOS
```

## Author
- Natnael Kahssay

## License
MIT License

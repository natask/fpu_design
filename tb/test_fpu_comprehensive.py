import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
from cocotb.binary import BinaryValue
import numpy as np
from fpu_operations import FPUVerification, FPOperation, FPFormat, FloatingPoint

@cocotb.test()
async def test_fpu_operations_comprehensive(dut):
    """Test FPU operations against Python implementations"""
    
    # Initialize verification
    fpu_verify = FPUVerification()
    
    # Create clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset system
    dut.rst_n.value = 0
    await Timer(20, units="ns")
    dut.rst_n.value = 1
    
    # Test vectors
    test_values = [
        # Normal numbers
        (1.0, 1.0),
        (2.5, 1.5),
        (-1.0, 1.0),
        # Subnormal numbers
        (1e-38, 1e-38),
        # Large numbers
        (1e38, 1.0),
        # Zero
        (0.0, 1.0),
        # Mixed signs
        (-2.5, 1.5)
    ]
    
    # Test all operations with different test vectors
    for op_a, op_b in test_values:
        for operation in FPOperation:
            # Skip division by zero
            if operation == FPOperation.DIV and op_b == 0.0:
                continue
                
            # Convert to FP32 format
            fp_a = FloatingPoint(op_a, FPFormat.FLOAT32)
            fp_b = FloatingPoint(op_b, FPFormat.FLOAT32)
            
            # Get results from Python implementations
            numpy_result, x86_result = fpu_verify.verify_operation(
                op_a, op_b, operation, FPFormat.FLOAT32
            )
            
            # Set inputs to DUT
            dut.valid_in.value = 1
            dut.operand_a.value = int(fp_a.bits.bin, 2)
            dut.operand_b.value = int(fp_b.bits.bin, 2)
            dut.operation.value = operation.value
            
            # Wait for result
            await RisingEdge(dut.clk)
            while not dut.valid_out.value:
                await RisingEdge(dut.clk)
                
            # Convert DUT result to float
            rtl_result_bits = dut.result.value.integer
            rtl_fp = FloatingPoint(
                struct.unpack('!f', struct.pack('!I', rtl_result_bits))[0],
                FPFormat.FLOAT32
            )
            
            # Compare results
            comparison = fpu_verify.compare_results(
                numpy_result, x86_result, rtl_fp.value
            )
            
            # Log results
            dut._log.info(f"Operation: {operation.name}")
            dut._log.info(f"Operands: {op_a} {op_b}")
            dut._log.info(f"Results - NumPy: {numpy_result}, X86: {x86_result}, RTL: {rtl_fp.value}")
            dut._log.info(f"Max difference: {comparison['max_diff']}")
            
            # Assert results match within tolerance
            assert comparison['numpy_x86_match'], "NumPy and x86 results differ"
            assert comparison['numpy_rtl_match'], "NumPy and RTL results differ"
            assert comparison['x86_rtl_match'], "x86 and RTL results differ"
            
        # Reset inputs
        dut.valid_in.value = 0
        await RisingEdge(dut.clk)

@cocotb.test()
async def test_special_cases(dut):
    """Test special floating point cases"""
    
    # Create clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset system
    dut.rst_n.value = 0
    await Timer(20, units="ns")
    dut.rst_n.value = 1
    
    special_cases = [
        # Infinity
        (float('inf'), 1.0),
        # NaN
        (float('nan'), 1.0),
        # Zero
        (0.0, 0.0),
        # Subnormal numbers
        (np.nextafter(0, 1), np.nextafter(0, 1))
    ]
    
    fpu_verify = FPUVerification()
    
    for op_a, op_b in special_cases:
        for operation in FPOperation:
            # Skip invalid operations
            if operation == FPOperation.DIV and op_b == 0.0:
                continue
                
            fp_a = FloatingPoint(op_a, FPFormat.FLOAT32)
            fp_b = FloatingPoint(op_b, FPFormat.FLOAT32)
            
            # Set inputs to DUT
            dut.valid_in.value = 1
            dut.operand_a.value = int(fp_a.bits.bin, 2)
            dut.operand_b.value = int(fp_b.bits.bin, 2)
            dut.operation.value = operation.value
            
            await RisingEdge(dut.clk)
            while not dut.valid_out.value:
                await RisingEdge(dut.clk)
                
            # Check exception flag for special cases
            if np.isnan(op_a) or np.isnan(op_b) or np.isinf(op_a) or np.isinf(op_b):
                assert dut.exception.value == 1, f"Exception not raised for special case: {op_a}, {op_b}"
                
        dut.valid_in.value = 0
        await RisingEdge(dut.clk)

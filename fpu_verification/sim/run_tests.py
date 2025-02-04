"""Test runner for FPU design verification."""
import argparse
import os
import sys
from pathlib import Path
from cocotb.runner import get_runner

def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent

def run_sv_testbench(proj_path, sim="icarus"):
    """Run SystemVerilog testbench."""
    print("Running SystemVerilog testbench...")
    
    sources = [
        proj_path / "rtl" / "fpu.sv",
        proj_path / "tb_sv" / "fpu_tb.sv"
    ]
    
    # Build arguments specific to SystemVerilog testbench
    build_args = [
        "-Wall",
        "-g2012",  # SystemVerilog-2012 support
        "-P", "fpu.EXPONENT_WIDTH=8",
        "-P", "fpu.MANTISSA_WIDTH=23"
    ] if sim == "icarus" else []
    
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="fpu_tb",  # SystemVerilog testbench top module
        build_dir=str(proj_path / "sim_build_sv"),
        always=True,
        build_args=build_args,
        parameters={
            "EXPONENT_WIDTH": 8,
            "MANTISSA_WIDTH": 23,
            "CLOCK_GATING_EN": 1,
            "OPERAND_ISOLATION_EN": 1
        },
        timescale=("1ns", "1ps"),
        waves=True
    )
    
    # Run SystemVerilog simulation
    runner.test(
        hdl_toplevel="fpu_tb",
        test_args=[],
        waves=True
    )

def run_cocotb_tests(proj_path, sim="icarus"):
    """Run cocotb Python testbench."""
    print("Running cocotb Python testbench...")
    
    sources = [
        proj_path / "rtl" / "fpu.sv"
    ]
    
    # Build arguments for cocotb tests
    build_args = [
        "-Wall",
        "-g2012",
        "-P", "fpu.EXPONENT_WIDTH=8",
        "-P", "fpu.MANTISSA_WIDTH=23"
    ] if sim == "icarus" else []
    
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="fpu",
        build_dir=str(proj_path / "sim_build_cocotb"),
        always=True,
        build_args=build_args,
        parameters={
            "EXPONENT_WIDTH": 8,
            "MANTISSA_WIDTH": 23,
            "CLOCK_GATING_EN": 1,
            "OPERAND_ISOLATION_EN": 1
        },
        timescale=("1ns", "1ps"),
        defines={"COCOTB_SIM": 1},
        waves=True
    )
    
    # Run cocotb tests
    runner.test(
        hdl_toplevel="fpu",
        test_module="test_fpu_comprehensive",
        test_dir=str(proj_path / "tb"),
        waves=True,
        extra_env={
            "PYTHONPATH": str(proj_path),
            "TOPLEVEL": "fpu"
        }
    )

def main():
    """Main entry point for running tests."""
    parser = argparse.ArgumentParser(description="FPU Verification Test Runner")
    parser.add_argument("--testbench", choices=["sv", "cocotb", "all"], 
                      default="all", help="Select testbench to run")
    parser.add_argument("--sim", default=os.getenv("SIM", "icarus"),
                      help="Simulator to use (default: icarus)")
    args = parser.parse_args()
    
    proj_path = get_project_root()
    
    try:
        if args.testbench in ["sv", "all"]:
            run_sv_testbench(proj_path, args.sim)
        
        if args.testbench in ["cocotb", "all"]:
            run_cocotb_tests(proj_path, args.sim)
            
    except Exception as e:
        print(f"Error running tests: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

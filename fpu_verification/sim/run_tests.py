"""Test runner for FPU verification framework."""
import os
import sys
from pathlib import Path
from cocotb.runner import get_runner

def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent

def main():
    """Main entry point for running tests."""
    # Configuration
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "icarus")
    proj_path = get_project_root()
    
    # Get main module name
    main_name = "fpu"
    print(f"Testing module: {main_name}")
    
    # Setup paths
    rtl_path = proj_path / "rtl"
    tb_path = proj_path / "tb"
    
    # Source files
    sources = [
        rtl_path / f"{main_name}.sv",
        proj_path / "tb_sv" / "fpu_tb.sv"
    ]
    
    # Build arguments
    build_test_args = [
        "-Wall",
        "-g2012",  # SystemVerilog-2012 support
        "-P", f"{main_name}.EXPONENT_WIDTH=8",
        "-P", f"{main_name}.MANTISSA_WIDTH=23"
    ] if sim == "icarus" else []
    
    # Parameters
    parameters = {
        "EXPONENT_WIDTH": 8,
        "MANTISSA_WIDTH": 23,
        "CLOCK_GATING_EN": 1,
        "OPERAND_ISOLATION_EN": 1
    }
    
    # Get runner and build
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel=main_name,
        build_dir=str(proj_path / "sim_build"),
        always=True,
        build_args=build_test_args,
        parameters=parameters,
        timescale=("1ns", "1ps"),
        defines={"COCOTB_SIM": 1},
        waves=True
    )
    
    # Run tests
    runner.test(
        hdl_toplevel=main_name,
        test_module="test_fpu_comprehensive",
        test_dir=str(tb_path),
        waves=True,
        extra_env={
            "PYTHONPATH": str(proj_path),
            "TOPLEVEL": main_name
        }
    )

if __name__ == "__main__":
    main()

import os
import sys
from pathlib import Path
from cocotb.runner import get_runner

def test_runner():
    # Configuration
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "icarus")
    path_file = Path(__file__).resolve()
    proj_path = path_file.parent.parent  # Project root
    
    # Get main module name from test file
    main_name = "fpu"  # Directly use FPU module name
    print(f"Testing module: {main_name}")
    
    # Setup paths
    sys.path.append(str(proj_path / "tb"))
    sys.path.append(str(proj_path / "rtl"))
    
    # Source files
    sources = [
        proj_path / "rtl" / f"{main_name}.sv",
        proj_path / "tb_sv" / "fpu_tb.sv"
    ]
    
    # Build arguments
    build_test_args = [
        "-Wall",
        "-g2012",  # SystemVerilog-2012 support
        "-P", f"{main_name}.EXPONENT_WIDTH=8",
        "-P", f"{main_name}.MANTISSA_WIDTH=23"
    ] if sim == "icarus" else []
    
    # Parameters to pass to simulation
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
        test_module="test_fpu_comprehensive",  # Our main test module
        test_dir=str(proj_path / "tb"),
        waves=True,
        extra_env={
            "PYTHONPATH": str(proj_path / "tb"),
            "TOPLEVEL": main_name
        }
    )

if __name__ == "__main__":
    test_runner()
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.binary import BinaryValue
import random
import struct

class FPUTransaction:
    def __init__(self, op_a, op_b, operation):
        self.op_a = op_a
        self.op_b = op_b
        self.operation = operation

class FPUDriver:
    def __init__(self, dut):
        self.dut = dut
        self.transactions = []

    async def send_transaction(self, transaction):
        await RisingEdge(self.dut.clk)
        self.dut.valid_in.value = 1
        self.dut.operand_a.value = transaction.op_a
        self.dut.operand_b.value = transaction.op_b
        self.dut.operation.value = transaction.operation
        await RisingEdge(self.dut.clk)
        self.dut.valid_in.value = 0

class FPUMonitor:
    def __init__(self, dut):
        self.dut = dut
        self.results = []

    async def monitor_output(self):
        while True:
            await RisingEdge(self.dut.clk)
            if self.dut.valid_out.value == 1:
                result = {
                    'result': self.dut.result.value,
                    'exception': self.dut.exception.value
                }
                self.results.append(result)

@cocotb.test()
async def test_fpu_basic(dut):
    """Test basic FPU operations"""
    
    # Create a 10ns period clock
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    
    # Initialize objects
    driver = FPUDriver(dut)
    monitor = FPUMonitor(dut)
    
    # Reset system
    dut.rst_n.value = 0
    await Timer(20, units="ns")
    dut.rst_n.value = 1
    
    # Start monitoring
    monitor_task = cocotb.start_soon(monitor.monitor_output())
    
    # Create test vectors
    test_cases = [
        FPUTransaction(0x3F800000, 0x3F800000, 0),  # 1.0 + 1.0
        FPUTransaction(0x40000000, 0x3F800000, 1),  # 2.0 - 1.0
        FPUTransaction(0x40000000, 0x40000000, 2),  # 2.0 * 2.0
        FPUTransaction(0x40800000, 0x3F800000, 3)   # 4.0 / 1.0
    ]
    
    # Send transactions
    for test in test_cases:
        await driver.send_transaction(test)
        await Timer(20, units="ns")
    
    await Timer(100, units="ns")
    
    # Verify results (simplified)
    assert len(monitor.results) == len(test_cases), "Not all results received"

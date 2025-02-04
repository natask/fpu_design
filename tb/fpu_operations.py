import numpy as np
import struct
import ctypes
from bitstring import BitArray
from enum import Enum

class FPOperation(Enum):
    ADD = 0
    SUB = 1
    MUL = 2
    DIV = 3

class FPFormat(Enum):
    FLOAT32 = 1
    FLOAT64 = 2

class FloatingPoint:
    def __init__(self, value, fp_format=FPFormat.FLOAT32):
        self.value = value
        self.fp_format = fp_format
        
    @property
    def bits(self):
        if self.fp_format == FPFormat.FLOAT32:
            return BitArray(float=self.value, length=32)
        else:
            return BitArray(float=self.value, length=64)
            
    @property
    def hex(self):
        return self.bits.hex
        
    @property
    def sign(self):
        return self.bits[0]
        
    @property
    def exponent(self):
        if self.fp_format == FPFormat.FLOAT32:
            return self.bits[1:9]
        else:
            return self.bits[1:12]
            
    @property
    def mantissa(self):
        if self.fp_format == FPFormat.FLOAT32:
            return self.bits[9:]
        else:
            return self.bits[12:]

class X86FloatingPoint:
    """Direct x86 floating-point operations using ctypes"""
    
    def __init__(self):
        # Load libc for direct FPU operations
        self.libc = ctypes.CDLL(None)
        
    def _float_to_bits(self, value, fp_format):
        if fp_format == FPFormat.FLOAT32:
            return struct.unpack('!I', struct.pack('!f', value))[0]
        else:
            return struct.unpack('!Q', struct.pack('!d', value))[0]
            
    def _bits_to_float(self, bits, fp_format):
        if fp_format == FPFormat.FLOAT32:
            return struct.unpack('!f', struct.pack('!I', bits))[0]
        else:
            return struct.unpack('!d', struct.pack('!Q', bits))[0]
    
    def add(self, a, b, fp_format=FPFormat.FLOAT32):
        if fp_format == FPFormat.FLOAT32:
            result = ctypes.c_float(a).value + ctypes.c_float(b).value
        else:
            result = ctypes.c_double(a).value + ctypes.c_double(b).value
        return result
        
    def subtract(self, a, b, fp_format=FPFormat.FLOAT32):
        if fp_format == FPFormat.FLOAT32:
            result = ctypes.c_float(a).value - ctypes.c_float(b).value
        else:
            result = ctypes.c_double(a).value - ctypes.c_double(b).value
        return result

class FPUVerification:
    def __init__(self):
        self.numpy_fp = np
        self.x86_fp = X86FloatingPoint()
        
    def verify_operation(self, op_a, op_b, operation, fp_format=FPFormat.FLOAT32):
        """
        Verify FPU operation against NumPy and x86 implementations
        Returns tuple (numpy_result, x86_result, rtl_result)
        """
        # NumPy implementation
        if operation == FPOperation.ADD:
            numpy_result = self.numpy_fp.float32(op_a) + self.numpy_fp.float32(op_b)
        elif operation == FPOperation.SUB:
            numpy_result = self.numpy_fp.float32(op_a) - self.numpy_fp.float32(op_b)
        elif operation == FPOperation.MUL:
            numpy_result = self.numpy_fp.float32(op_a) * self.numpy_fp.float32(op_b)
        elif operation == FPOperation.DIV:
            numpy_result = self.numpy_fp.float32(op_a) / self.numpy_fp.float32(op_b)
            
        # X86 implementation
        if operation == FPOperation.ADD:
            x86_result = self.x86_fp.add(op_a, op_b, fp_format)
        elif operation == FPOperation.SUB:
            x86_result = self.x86_fp.subtract(op_a, op_b, fp_format)
            
        return numpy_result, x86_result

    def compare_results(self, numpy_result, x86_result, rtl_result, tolerance=1e-6):
        """Compare results from different implementations"""
        numpy_x86_match = abs(numpy_result - x86_result) < tolerance
        numpy_rtl_match = abs(numpy_result - rtl_result) < tolerance
        x86_rtl_match = abs(x86_result - rtl_result) < tolerance
        
        return {
            'numpy_x86_match': numpy_x86_match,
            'numpy_rtl_match': numpy_rtl_match,
            'x86_rtl_match': x86_rtl_match,
            'max_diff': max(abs(numpy_result - x86_result),
                          abs(numpy_result - rtl_result),
                          abs(x86_result - rtl_result))
        }

#!/usr/bin/env python3
"""
GPU load generator using PyTorch
Usage: python gpu_load.py [duration_seconds] [gpu_id]

Requirements: pip install torch
"""

import sys
import time
import os

try:
    import torch
except ImportError:
    print("ERROR: PyTorch not installed")
    print("Install with: pip install torch")
    sys.exit(1)

def gpu_burn(duration, gpu_id=0):
    """
    Perform continuous GPU matrix operations
    """
    if not torch.cuda.is_available():
        print("ERROR: No CUDA-capable GPU found")
        print(f"PyTorch version: {torch.__version__}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        sys.exit(1)
    
    # Set GPU device
    device = torch.device(f'cuda:{gpu_id}')
    
    # Print GPU info
    print(f"Using GPU: {torch.cuda.get_device_name(gpu_id)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(gpu_id).total_memory / 1e9:.2f} GB")
    print(f"CUDA Version: {torch.version.cuda}")
    print("-" * 60)
    
    # Matrix size for good GPU utilization
    size = 8192
    
    print(f"Starting GPU load (matrix size: {size}x{size})")
    print(f"Duration: {duration}s" if duration > 0 else "Duration: indefinite (Ctrl+C to stop)")
    print("-" * 60)
    
    end_time = time.time() + duration if duration > 0 else float('inf')
    iteration = 0
    start_time = time.time()
    
    try:
        while time.time() < end_time:
            # Create random matrices on GPU
            a = torch.randn(size, size, device=device)
            b = torch.randn(size, size, device=device)
            
            # Matrix multiplication (GPU intensive)
            c = torch.matmul(a, b)
            
            # Additional operations to increase load
            d = torch.sin(c)
            e = torch.exp(d * 0.01)  # Scale to avoid overflow
            
            # Force computation to complete
            torch.cuda.synchronize()
            
            iteration += 1
            
            # Print status every 10 seconds
            if iteration % 10 == 0:
                elapsed = time.time() - start_time
                gpu_util = torch.cuda.memory_allocated(gpu_id) / torch.cuda.max_memory_allocated(gpu_id) * 100
                print(f"Iteration {iteration} | Elapsed: {elapsed:.1f}s | GPU Mem: {torch.cuda.memory_allocated(gpu_id)/1e9:.2f} GB")
    
    except KeyboardInterrupt:
        print("\n\nStopping GPU load...")
    
    finally:
        elapsed = time.time() - start_time
        print("-" * 60)
        print(f"Completed {iteration} iterations in {elapsed:.2f}s")
        print(f"Average: {iteration/elapsed:.2f} iterations/sec")
        print(f"Peak GPU memory: {torch.cuda.max_memory_allocated(gpu_id)/1e9:.2f} GB")

if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    gpu_id = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    print(f"GPU Load Generator")
    print(f"PID: {os.getpid()}")
    print("=" * 60)
    
    gpu_burn(duration, gpu_id)

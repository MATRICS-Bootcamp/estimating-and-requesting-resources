#!/usr/bin/env python3
"""
CPU load with actual computation (matrix operations)
Requires: pip install numpy
"""

import multiprocessing as mp
import sys
import time
import numpy as np

def matrix_multiply(cpu_id, duration):
    """Perform continuous matrix multiplications"""
    print(f"CPU {cpu_id} started (matrix operations)")
    end_time = time.time() + duration if duration > 0 else float('inf')
    
    while time.time() < end_time:
        # Create random matrices and multiply
        a = np.random.rand(500, 500)
        b = np.random.rand(500, 500)
        c = np.dot(a, b)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cpu_load_numpy.py <num_cpus> [duration_seconds]")
        sys.exit(1)
    
    num_cpus = int(sys.argv[1])
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    print(f"Starting {num_cpus} workers with matrix operations...")
    
    processes = []
    for i in range(num_cpus):
        p = mp.Process(target=matrix_multiply, args=(i, duration))
        p.start()
        processes.append(p)
    
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\nStopping...")
        for p in processes:
            p.terminate()
            p.join()

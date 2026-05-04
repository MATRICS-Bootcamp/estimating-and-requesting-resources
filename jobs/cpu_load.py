#!/usr/bin/env python3
"""
CPU load generator - GUARANTEED single-threaded
Usage: python cpu_load_single_thread.py <num_cpus> [duration_seconds]
"""

# CRITICAL: Must be at the very top, before ANY other imports
import os
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'

import multiprocessing as mp
import sys
import time

def cpu_burn(cpu_id, duration):
    """Pure CPU burner - single threaded"""
    # Set again in child process to be absolutely sure
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    
    pid = os.getpid()
    print(f"Worker {cpu_id} started: PID={pid}")
    
    end_time = time.time() + duration if duration > 0 else float('inf')
    
    # Pure Python loop - no libraries
    count = 0
    while time.time() < end_time:
        # Simple computation
        result = 0
        for i in range(10000):
            result += i * i
        count += 1
    
    print(f"Worker {cpu_id} (PID {pid}) completed {count} iterations")

if __name__ == "__main__":
    # Force fork method
    mp.set_start_method('fork', force=True)
    
    if len(sys.argv) < 2:
        print("Usage: python cpu_load_single_thread.py <num_cpus> [duration_seconds]")
        sys.exit(1)
    
    num_cpus = int(sys.argv[1])
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    print(f"CPU Load Generator (Single-Threaded)")
    print(f"Parent PID: {os.getpid()}")
    print(f"Starting {num_cpus} workers")
    print("-" * 60)
    
    processes = []
    for i in range(num_cpus):
        p = mp.Process(target=cpu_burn, args=(i, duration))
        p.start()
        processes.append(p)
    
    # Give processes time to start
    time.sleep(1)
    
    print("\nWorker PIDs:")
    for i, p in enumerate(processes):
        print(f"  Worker {i}: PID {p.pid}")
    
    print("-" * 60)
    print(f"Expected: {num_cpus} single-threaded processes")
    print("\nVerify with:")
    print(f"  for pid in $(pgrep -P {os.getpid()}); do ps -T -p $pid --no-headers | wc -l; done")
    print("-" * 60)
    
    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print("\n\nStopping workers...")
        for p in processes:
            p.terminate()
            p.join()
        print("Done")

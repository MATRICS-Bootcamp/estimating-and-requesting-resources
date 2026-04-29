# What resources might you request in HPC?

## CPUs

For any HPC job, you'll need some number of CPUs.  These are the central processing units that do operations on a computer!

## Memory

For any HPC job, you'll also need some amount of memory.  This is a data storage location closer to the CPUs that is used for near-term processing.

## Time

You will need to specify an amount of time for your job to run

## GPUs

You may or may not need GPUs (graphical processing units).  These chips can accelerate scientific computation if your code is setup to use them

## Nodes

A node is a physical machine, like your laptop.  By default, most jobs only need and request 1 node.  It's possible to request multiple nodes, and setup your code to distribute tasks across multiple machines.


# How do I request resources?

## OnDemand

## SBATCH

```bash
#!/bin/bash
#SBATCH --job-name=my_job             # Job name
#SBATCH --output=my_job_%j.out        # Output file name (%j expands to jobId)
#SBATCH --error=my_job_%j.err         # Error file name
#SBATCH --cpus=4                       # Total number of CPUs requested
#SBATCH --mem=16G                      # Total memory limit
#SBATCH --time=02:00:00                # Time limit hrs:min:sec
#SBATCH --gpus=2                       # Number of GPUs requested
#SBATCH --nodes=1                      # Number of nodes requested

# Load any necessary modules (if applicable)
module load your_module_name

# Execute your application
srun your_application_executable
```

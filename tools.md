# Tools for Tracking Resource Utilization

## Tools for tracking while the job is running

### Top / htop

We're going to start by submitting the following job:

```bash
sbatch cpu_hog.submit
```

When this job starts, let's login to the node and run `htop` to view utilization.  You'll see something like this:

![htop](assets/htop.png)

If you see many more threads, press Shift+H to switch from threads to processes.

### nvidia-smi / nvtop

For GPUs, were going to submit the following job:

```bash
sbatch gpu_hog.submit
```
When this job starts, let's login to the node and run `nvidia-smi` to view utilization.  You'll see something like this:

From this, you can see that you have a process on the GPU, and that GPU memory is being used.

You might also find `nvtop` useful.  You can load `nvtop` on Sherlock with `ml system nvtop`, and then run with `nvtop` to see something like this:

![nvidia-smi](assets/nvidia-smi.png)

There's another good tool for watching your GPU usage called `nvtop`.  Here's what that looks like:

![nvtop](assets/nvtop.png)

## Tools for tracking after the job is done

### seff

 `seff` stands for Slurm Efficiency, and will give you a report of your jobs efficiency like this:

 ```bash
seff 23801862
```

![seff](assets/seff.png)


 ### sacct

 `sacct` stands for Slurm Accounting.  This is the database of job information that Sherlock holds for 6 months.  Here's an example query where I request information about my job:

 ```bash
sacct -u bchivers -S2026-05-01 -E2026-06-01 -ojobid,jobname%40,user,start,end,state,alloctres%50,MaxRSS
```

![sacct](assets/sacct.png)

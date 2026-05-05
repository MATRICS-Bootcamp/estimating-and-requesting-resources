# sbatch Tips and Tricks on Sherlock

## Introduction to Sbatch Files
In Slurm, you submit jobs using the `sbatch ...` command, which reads a job script (often called an sbatch file) and queues it to run via the scheduler.

At minimum, an `sbatch` file needs three components:
1. A [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)): The shebang line can call any shell or scripting language available on the cluster. For example `#!/bin/bash`, `#!/bin/env python`, or `#!/bin/env julia`.
2. [SBATCH](https://slurm.schedmd.com/sbatch.html#SECTION_OPTIONS) constraints: Resource requests (for example: `ntasks`, `mem`, `nodes`, `time`) that specify the constraining limits of your job's resources.
3. Executable commands: These can follow what you might write in any script file to run your code. In shell, as an example, this would be where you would load modules (`module load ...`) followed by running a script (`python3 my_script.py`).

---

## Getting Started with Sbatch Basics

### Should I ask for a number of CPUs or for a certain amount of memory?

Two common needs in any resource request are CPUs and memory. The key insight is that if you ask for either, they will both reserve CPUs. Slurm will not schedule your job until it can find a node with enough free CPUs *and* enough free RAM to satisfy your request. You do not need to know both to submit your job. You just need to know which constraint is the right one to choose to get the resources that you need.

Before writing your `#SBATCH` lines, ask yourself:

1. Do I know how many parallel tasks my job will run at once? If you know this, constrain CPUs.
2. Do I know how much data my job needs to hold in memory at once? If you know this constrain memory.

### When to constrain on CPUs

Use `--cpus-per-task` when you know your software runs a fixed number of parallel workers. This can be achieved with MPI, a parallel Python loop with `multiprocessing`, or an R script using `parallel`. You are telling Slurm: "I need exactly N cores to parallelize my code; give me however much memory the node has to spare."

Brian's `cpu_load.py` is a perfect example: it spawns exactly as many worker processes as you tell it, each using one core.

```bash
#!/bin/bash
#!/bin/bash
#SBATCH --job-name=cpu_parallilized_load
#SBATCH --cpus-per-task=8        # reserve 8 cores; memory uses node default of >=4GB/CPU
#SBATCH --time=00:05:00
#SBATCH --partition=normal

# Use the $SLURM_CPUS_PER_TASK variable so your script always matches what Slurm allocated,
# even if you change --cpus-per-task later
python cpu_load.py $SLURM_CPUS_PER_TASK 60    # 8 workers, 60 seconds
```

> **Key variable:** `$SLURM_CPUS_PER_TASK` is automatically set by Slurm to match your `--cpus-per-task` value. You can pass it to your script as a keyword argument rather than hard-coding a number, and this keeps your script correct even if you change the resource request later.

> **Common mistake:** Make sure that you are multi-threading when you request more than one CPU. If you request 8 cpus, like this does, Slurm will reserve 8 cores but your job will use only 1 if you don't thread through all 8, which will leave 7 of your allocated CPUs idle. Ultimately, this makes your job wait longer in the queue without the speed-up that proper threading would provide. You can check actual CPU usage after the fact with `seff <jobid>`.

---

### When to constrain on minimum memory

Use `--mem` when you know your job needs a certain amount of RAM to complete its run. This is useful when loading a large reference genome, a big matrix, or a whole-dataset object. You are telling Slurm: "I need X GB of RAM; give me however many CPUs are available on that node."

```bash
#!/bin/bash
#SBATCH --job-name=cpu_mem_load
#SBATCH --mem=12G                # reserve 12GB RAM; nCPUs use node default
#SBATCH --time=00:05:00
#SBATCH --partition=normal

python cpu_load.py $SLURM_CPUS_PER_TASK 60
```

> **A guide:** Start by estimating the size of the data you need to hold in memory simultaneously (i.e. how many copies), then request ~30% more than that amount as a buffer for overhead. If your job reads a 4 GB file and builds a data structure from it, 12 GB is a reasonable starting point.

Note that `cpu_load.py` and `gpu_load.py` are compute-bound rather than memory-bound, so they don't show optimal performance in this pathway but the concept applies any time your bottleneck is RAM rather than number of CPU cores.

---

### When to request both

Many real jobs are both compute- and memory-intensive. It can be necessary, and, when needed, good practice to specify both at once. Here `cpu_load.py` stands in for any tool where you know the required parallelism *and* the data size:


```bash
#!/bin/bash
#SBATCH --job-name=cpu_constrained_load
#SBATCH --cpus-per-task=8
#SBATCH --mem=12G
#SBATCH --time=00:05:00
#SBATCH --partition=normal

python cpu_load.py $SLURM_CPUS_PER_TASK 60
```

> **Check your efficiency after the job runs.** Use `seff <jobid>` to see how much CPU and memory you actually used. If, for example, you used 5% of your requested memory, request less next time and your job will wait less in the queue because it's cheaper to schedule. It is good practice to aim for ~85% efficiency.

---

## How do I monitor that my job script is running properly?

By default, Slurm writes all job output (i.e. anything that would typically print out to the command line if you were running from an interactive shell) to a file named `slurm-<jobid>.out` in whatever directory you submitted your job from. This works fine for one job, but gets confusing fast if your job has a lot of printouts, warnings, or your running more than one job. You can monitor your job with several `sbatch` constraints.

### Separating `.out` files and `.err` files

```bash
#!/bin/bash
#SBATCH --job-name=cpu_logged_load
#SBATCH --output=logs/cpu_load_%j.out    # %j expands to the job ID
#SBATCH --error=logs/cpu_load_%j.err     # stderr goes to a separate file
#SBATCH --cpus-per-task=4
#SBATCH --time=00:05:00
#SBATCH --partition=normal

mkdir -p logs    # Make sure the log directory exists before the job runs
python cpu_load.py $SLURM_CPUS_PER_TASK 60
```

> **Why separate stdout and stderr?** When something goes wrong, you want to be able to `cat logs/my_analysis_12345.err` and see only the error messages, not a mix of normal output and error messages together. By seperating these into seperate files, you can see the command line printouts in the `.out` file, and any errors in the `.err` file.

### Useful filename patterns for log files

Slurm supports several special variables you can embed in your `--output` and `--error` file paths:

| Variable | Expands to |
|---|---|
| `%j` | Job ID |
| `%x` | Job name (from `--job-name`) |
| `%a` | Array task ID (useful in Day 2!) |
| `%N` | Name of the first node assigned |

A common naming convention that works for most use cases:

```bash
#SBATCH --output=logs/%x_%j.out               # records to logs/job-name_jobID.out
#SBATCH --error=logs/%x_%j.err                # records to logs/job-name_jobID.err
```

> **Common mistake:** If the `logs/` directory does not exist when your job starts, Slurm won't be able to write the log file and your job output won't be recorded, but this won't make your job fail. It's a good idea to add `mkdir -p logs` into your `sbatch` file before you run your script.

---

### Email notification setup

You can use the `squeue` command to see if your job is still waiting in the queue or if it's running, but when wait times are long, this can take a while. You can set Slurm to email you instead.

### Basic notification setup

```bash
#!/bin/bash
#SBATCH --job-name=cpu_email_load
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --cpus-per-task=8
#SBATCH --time=00:05:00
#SBATCH --partition=normal
#SBATCH --mail-type=BEGIN,END,FAIL     # Email on job start, completion, and failure
#SBATCH --mail-user=yourname@stanford.edu

mkdir -p logs
python cpu_load.py $SLURM_CPUS_PER_TASK 60
```

### mail-type options

| Value | When you get an email |
|---|---|
| `BEGIN` | Job starts running (left the queue) |
| `END` | Job finishes successfully |
| `FAIL` | Job fails or is cancelled |
| `TIME_LIMIT` | Job hits its time limit |
| `ALL` | All of the above |
| `BEGIN,END,FAIL` | The most common practical combination |

> **Common mistake:** On Sherlock, use your `@stanford.edu` address. Emails are sent from the Slurm daemon and may end up in your spam folder the first time you receive them. Add the sender to your allowed email senders so you don't miss them.

---

### Putting all the basics together

Here is a reusable `sbatch` template that combines all the practices for a basic `sbatch` request.

```bash
#!/bin/bash
#SBATCH --job-name=cpu_load
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --cpus-per-task=8
#SBATCH --mem=12G
#SBATCH --time=00:05:00
#SBATCH --partition=normal
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=yourname@stanford.edu

mkdir -p logs
module load python/3.12.0

echo "Job $SLURM_JOB_ID started on $(hostname) at $(date)"

python cpu_load.py $SLURM_CPUS_PER_TASK 60

echo "Job $SLURM_JOB_ID finished at $(date)"
```

> **Leveling Up:** The `echo` lines with timestamps give you a record of wall-clock time inside your `.out` file, which is useful for benchmarking how long each step takes even if you're already getting emails.

---

## Intermediate Tips and Tricks

### Preview for MATRICS Day 2 — Parallelization using Slurm job arrays 

If you ever find yourself copy-pasting a batch script and changing only keyword arguments or hyperparameters, that is an ideal time to use a Slurm **job array**. Arrays let you submit a whole family of jobs with a single `sbatch` command, each getting a unique index (`$SLURM_ARRAY_TASK_ID`) to iterate over for input. Christina will show us how to build arrays from scratch in Day 2.

---

### Which partition should you select?

On Sherlock, different partitions are useful for different tasks. Choosing the right one affects both how long your job waits and what resources it can access.

```bash
#SBATCH --partition=normal        # General-purpose CPU jobs
#SBATCH --partition=gpu           # Jobs requiring GPU nodes
#SBATCH --partition=bigmem        # Jobs needing >256 GB RAM
#SBATCH --partition=serc          # If you're in SDSS you get priority access to CPUs and GPUs through this queue
#SBATCH --partition=owners        # If you're in SDSS or an owner group, this queue has a shorter wait but is pre-emptible
```

> **Check available partitions with `sh_part`.** 

```bash
#SBATCH --partition=normal,owners
```
Slurm will schedule your job on whichever has resources available first.


> **Check available partitions with `sh_part`.** Your group may have dedicated owner nodes with shorter queue times for larger resources. Check `sh_part"` to list the partitions that you can access, and available resources there.

If you want your job to run on the `normal` partition but also use `owners` if slots open up there, you can specify multiple partitions:

```bash
#SBATCH --partition=normal,owners
```

Slurm will schedule your job on whichever has resources available first.

---

### Selecting specific nodes

Within a partition, nodes vary in CPU or GPU generation, memory size, and local storage. You can request specific node types with `--constraint`:

```bash
#SBATCH --constraint=CLASS:SH3_CBASE               # Sherlock 3 CBASE nodes
#SBATCH --constraint="GPU_SKU:A100_SXM4"           # A100 GPUs
```

On Sherlock, node features are listed in `sinfo -o "%N %f"`. This is especially useful when your script requires certain hardware to run, or when you are benchmarking and need to use the same SKUs for comparison purposes.

---

### What if you want jobs to run sequentially?

If you have jobs that need to run in sequence, you can automate Slurm to wait for one job to finish before submitting the next, using the `--dependency` flag:

```bash
# Submit the first job and capture its ID
JOB1=$(sbatch --parsable first_job.sh)

# Submit the second job, which only starts if the first succeeds
JOB2=$(sbatch --parsable --dependency=afterok:$JOB1 second_job.sh)

# Submit the third job after the second
sbatch --dependency=afterok:$JOB2 summarize.sh
```

Common dependency types:

| Type | Meaning |
|---|---|
| `afterok:<jobid>` | Start only if the dependency finished succesfully |
| `afternotok:<jobid>` | Start only if the dependency failed (useful for cleanup jobs) |
| `afterany:<jobid>` | Start regardless of how the dependency ended |
| `after:<jobid>` | Start after the dependency has begun running |

> **Quick Tip:** The `--parsable` argument makes `sbatch` print only the job ID to stdout, which is what makes the `--dependency` pattern above run properly.

This is the right tool for sequential multi-step pipelines that rely on the previous process before running the next process (for example: preprocess --> process --> postprocess --> cleanup). 
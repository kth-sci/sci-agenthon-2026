#!/usr/bin/env bash
# =============================================================================
# EXAMPLE SLURM job script — TEMPLATE ONLY. Do NOT submit this as-is.
#
# This file is here to be inspected and hardened, not run. It contains placeholder
# values (account, partition, paths) that must be replaced for a real site, and it has
# not been validated against a real cluster. Treat every #SBATCH value below as an
# example to confirm against your site's documentation.
# =============================================================================

#SBATCH --job-name=oscillator_sweep
#SBATCH --account=naiss-example-account        # EXAMPLE — replace with your allocation
#SBATCH --partition=main                       # EXAMPLE — replace with your partition
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:05:00                         # EXAMPLE walltime
#SBATCH --output=slurm-%j.out

set -euo pipefail

# Load the software environment (example module names live in modules.sh).
# source modules.sh

# Work from the directory the job was submitted from.
cd "$SLURM_SUBMIT_DIR"

# Run the parameter sweep.
python run_sweep_local.py --config configs/sweep_parameters.csv

echo "Sweep finished with exit code $?"

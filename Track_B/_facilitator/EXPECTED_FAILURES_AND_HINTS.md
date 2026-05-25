# Expected Starter-state Failures and Hints

This is an answer key for the facilitator, not for participants at the start.

## 01 HPC Workflow Preparation

Starter state:

- `Track_B/01_hpc_simulation_workflow/scripts/validate_package.py` should not exist.
- Participants create `scripts/validate_package.py` in Task 3.

Run from `Track_B/01_hpc_simulation_workflow`:

```bash
python scripts/run_sweep_local.py --dry-run
```

Expected behavior:

- The dry-run should print 10 planned runs.
- The dry-run should not write output files.

Expected participant-created validator behavior in Task 3:

- It should check required files, required sweep columns, numeric parseability, unique `run_id` values, job-script Python paths, and output-directory handling.
- It should expose the job-script path issue because `hpc/job_sweep.slurm` refers to `python run_sweep_local.py`, while the script lives under `scripts/` relative to the package root.
- It should warn or fail that `run_sweep_local.py` does not create the output directory before writing.
- After the output-directory issue is fixed, participants may discover `run_07` has a negative `n_steps`. That is a good prompt for Task 5 hardening.

Expected full-sweep behavior before repair:

- `python scripts/run_sweep_local.py` should fail before producing trusted output because the output directory is not created.

Facilitator hints:

- What would you want to know before submitting this workflow to a cluster?
- Which failure can be caught statically, before running a sweep?
- Which check did your participant-created validator add?
- Which issue remains a cluster assumption?

## 02 Research-code Debugging

Run from `Track_B/02_research_code_debugging`:

```bash
python -m pytest -q
python scripts/run_simulation.py
python scripts/plot_simulation.py
```

Expected behavior:

- Tests should fail around the sign of the restoring force and bounded motion.
- The key bug is in `src/oscillator.py`: acceleration has the wrong sign.
- The plot and `run_simulation.py` should show large unphysical growth.
- After fixing acceleration, tests should pass or mostly pass depending on extensions.

Facilitator hints:

- Which test is closest to the physical law?
- Does the proposed fix change the model or the numerical method?
- What physical invariant could become a new test?

## 03 Scientific Post-processing

Run from `Track_B/03_scientific_postprocessing`:

```bash
python -m pytest -q
python scripts/quicklook.py --dataset reference
python scripts/quicklook.py --dataset challenge
```

Expected behavior:

- Dataset-integrity tests should pass.
- Quicklook should produce output for both datasets.
- The challenge dataset contains a suspicious Verlet run around `r011` with unusually high error compared with neighboring Verlet runs. Participants should discover this through comparison and checks, not by being told in the participant guide.

Facilitator hints:

- Which claim do you want to make, and where is the number?
- Does the challenge dataset support the same conclusion as the reference dataset?
- How do you make a suspicious visual observation reproducible?
- Show the same summary with and without flagged runs.

## Cross-cutting Hint Ladder

Use only as much help as needed.

1. Ask the team to rerun the command and read the exact output.
2. Ask which file the output implicates.
3. Ask the agent for hypotheses without edits.
4. Ask for the smallest check that would distinguish two hypotheses.
5. Ask for a minimal patch.
6. Ask for re-verification.
7. Ask for a limitation statement.

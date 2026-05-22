# Sub-team 01 — Agentic HPC workflow preparation

## Story

You have received a small simulation workflow from a collaborator. It is intended to run
a parameter sweep on an HPC cluster, but it has not been hardened for submission. Your
job is to use an agent to inspect the package, reproduce a local smoke test, interpret
sample failure logs, repair the workflow, and add pre-submission checks. You will not
submit anything to a real cluster. The goal is to make the package locally reproducible
and submission-ready in principle.

This is not primarily about harmonic-oscillator physics. The oscillator is a safe
stand-in for a real scientific simulation code. The real topic is: how do we turn a
messy research-computing workflow into something reproducible, checkable, and
submission-ready?

## Scientific background (very short)

Each run simulates the undamped 1D harmonic oscillator `m x'' = -k x` with a chosen time
integrator and time step. You do not need to study the physics in depth — treat each run
as "a simulation that takes parameters and produces an output file".

## Repo layout

This folder is self-contained after Task 1.

- `README.md` — this file
- `VERIFY.md` — exact setup and verification commands for Windows PowerShell and Linux/macOS
- `DEMO_REPORT_TEMPLATE.md` — fill this in for your readout
- `configs/` — `sweep_parameters.csv` (the sweep table) and `environment_example.txt`
- `scripts/` — `simulate_oscillator.py` (one run), `run_sweep_local.py` (local driver),
  `validate_package.py` (pre-submission checks)
- `hpc/` — `job_sweep.slurm` and `modules.sh` (example templates; not for real submission)
- `logs/` — sample logs from previous failed attempts, for you to interpret
- `outputs/` — created by your scripts at runtime; gitignored, do not commit

The agent role document lives outside this folder, in
`../00_start_here/agent_role_templates/`, and is copied in during Task 1.

## Task 1 — Set up the HPC workflow agent

**Goal:** Establish the agent's role, scope, and guardrails before inspecting or
modifying any workflow files.

1. From this folder, copy
   `../00_start_here/agent_role_templates/01_hpc_simulation_workflow_AGENT_ROLE_TEMPLATE.md`
   into this folder and **rename** the copy:
   - to `CLAUDE.md` if you are using Claude Code, OR
   - to `AGENT_ROLE.md` for any other agent tool, OR
   - paste the file contents directly into your tool if it expects rules or role
     instructions in the interface.
2. Configure your tool so the agent has access **only to
   `Track_B/01_hpc_simulation_workflow/`**.
3. Ask the agent to read the role file first and summarise back, in its own words, its
   **role, scope, restrictions, and workflow**. Check that the summary is faithful.
4. Do **not** edit anything yet.

Before moving on, update the **Task 1** section of `DEMO_REPORT_TEMPLATE.md`.

## Task 2 — Inspect the workflow manually

**Goal:** Understand what the package is supposed to do before asking the agent to repair
it.

Inspect, with your own eyes, `configs/sweep_parameters.csv`,
`scripts/simulate_oscillator.py`, `scripts/run_sweep_local.py`,
`scripts/validate_package.py`, `hpc/job_sweep.slurm`, `hpc/modules.sh`, and the files in
`logs/`.

Then run **only these two commands** (do not run the full local sweep yet — that is
Task 3):

```bash
python scripts/validate_package.py
python scripts/run_sweep_local.py --dry-run
```

Write down:

- what parameters are swept;
- what command would run a single simulation;
- what command would run the local sweep;
- what the job script is trying to do;
- what the sample logs suggest;
- which issues are local workflow issues and which would only be verifiable on a real
  cluster.

You may ask the agent to explain what `validate_package.py` checks and what
`run_sweep_local.py` does, but start with your own inspection.

Before moving on, update the **Task 2** section of `DEMO_REPORT_TEMPLATE.md`.

## Task 3 — Make the local sweep reproducible

**Goal:** Use the agent to repair the package enough that it runs locally and produces
reproducible output.

1. Ask the agent to inspect the workflow and explain the main files.
2. Paste the validation report and the dry-run output, and now run the full local sweep
   (`python scripts/run_sweep_local.py`) and paste what happens.
3. Ask the agent to propose the smallest reasonable fixes for what you observe.
4. Approve edits only after the agent explains the intended change.
5. Re-run `python scripts/validate_package.py` and `python scripts/run_sweep_local.py`,
   and confirm the expected outputs are produced.

Expected participant-created outputs include `outputs/local_sweep_summary.csv` and
`outputs/local_sweep_diagnostics.png`, plus a local run command you trust.

Before moving on, update the **Task 3** section of `DEMO_REPORT_TEMPLATE.md`.

## Task 4 — Add pre-submission guardrails

**Goal:** Improve the workflow so common submission failures are caught before a human
sends the job to a cluster.

This must be **check-first**. Before editing `validate_package.py`, ask the agent:

> What checks should this package pass before a human submits the job script? For each
> check, explain what it catches or rules out, and what output it should produce.

Then extend `validate_package.py` (or add a small helper) so it checks things such as:

- required files exist;
- parameter rows are valid (for example sensible `dt` and `n_steps`);
- `run_id` values are unique;
- output names are unique;
- output and log directories are created or documented;
- job-script paths point to files that exist;
- a dry-run command is available;
- cluster-specific assumptions are clearly marked as unverified.

The validator should produce a clear report: a PASS / WARN / FAIL status per check, what
was checked, the evidence, and a suggested next action. Re-run the validator and confirm
it now catches (or rules out) the problems you found in Task 3.

Before moving on, update the **Task 4** section of `DEMO_REPORT_TEMPLATE.md`.

## Task 5 — Make the workflow submission-ready or easier to diagnose

**Goal:** Turn the repaired workflow into something another researcher could understand,
reuse, or debug.

This is the creative final task, but it should produce a concrete product. Some
directions you could take (examples only):

- generate `outputs/pre_submission_report.md`;
- write a submission runbook with exact local and cluster-side steps;
- draw a small workflow diagram in Markdown;
- add a CLI option that validates, dry-runs, and prints the `sbatch` command **without
  submitting**;
- create `scripts/diagnose_log.py` that classifies the sample logs by likely failure
  category;
- generate a Markdown or HTML report summarising the sweep design;
- add a comparison plot of the local sweep outputs;
- add checks that state which parts are locally verified and which remain cluster
  assumptions.

Work check-first: define what the product should communicate, ask the agent for a small
plan, define at least one check or command that verifies the product, implement,
regenerate the outputs, and confirm your check.

Before moving on, update the **Task 5** section of `DEMO_REPORT_TEMPLATE.md`.

## Deliverable

A filled `DEMO_REPORT_TEMPLATE.md` saved inside this folder. Use it to build your final
5-minute presentation: what the package was, what you repaired, how you made it locally
reproducible, what guardrails you added, and what remains an unverified cluster
assumption.

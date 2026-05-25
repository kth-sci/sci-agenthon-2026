# Sub-team 01: Agentic HPC Workflow Preparation

## Story

You have received a folder from a collaborator. It contains a job script, a parameter-sweep table, a few Python scripts, and logs from previous attempts. This is a very common research/HPC situation: the workflow looks close to runnable, but it is not yet clear whether it is safe to send to a cluster.

Before a researcher submits this kind of package, they should verify that the local workflow is reproducible and that obvious submission failures are caught early. In this version, that guardrail does not exist yet. You will first understand the handoff, then build the validation script, then use it to guide the smallest fixes needed for a trustworthy local sweep.

You will not submit anything to a real cluster. The goal is to make the package locally reproducible and submission-ready in principle.

This is not primarily about harmonic-oscillator physics. The oscillator is a safe stand-in for a real scientific simulation code. The real topic is: how do we turn a messy research-computing workflow into something reproducible, checkable, and easier for a human to trust?

## Scientific Background

Each run simulates the undamped 1D harmonic oscillator `m x'' = -k x` with a chosen time integrator and time step. You do not need to study the physics in depth. Treat each run as a simulation that takes parameters and produces an output file.

## What You Are Building

A good target is a locally verified workflow with a participant-created validation script and one additional hardening or diagnosis artifact, such as:

- a repaired local sweep;
- a new `scripts/validate_package.py` report;
- a log-diagnosis helper;
- a pre-submission checklist or report.

Use <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a> as a working notebook. It is not only for the end of the day.

## Files to Know

- `00_SUBTEAM_GUIDE.md` - this guide.
- `01_VERIFY.md` - local verification commands for this sub-team.
- `DEMO_REPORT_TEMPLATE.md` - fill this in as you work.
- `configs/sweep_parameters.csv` - the sweep table.
- `configs/environment_example.txt` - example environment notes.
- `scripts/simulate_oscillator.py` - one simulation run.
- `scripts/run_sweep_local.py` - local sweep driver.
- `hpc/job_sweep.slurm` and `hpc/modules.sh` - example cluster templates, not for real submission during the exercise.
- `logs/` - sample logs from previous failed attempts.
- `outputs/` - created by scripts at runtime; do not commit generated files.

There is no starter `scripts/validate_package.py`. You will create it in Task 3.

Shared commands: <a href="../02_COMMANDS_AND_VERIFY.md" target="_blank" rel="noopener noreferrer">../02_COMMANDS_AND_VERIFY.md</a>  
Local verification notes: <a href="01_VERIFY.md" target="_blank" rel="noopener noreferrer">01_VERIFY.md</a>

## Task 1: Set Up the HPC Workflow Agent

**Goal:** Establish the agent's role, scope, and guardrails before inspecting or modifying any workflow files.

Do both parts of this setup before asking the agent to inspect files.

### Step 1: Copy the role file into the sub-team folder

Run from the repository root, `Track_B/`, or copy the file manually in your file browser:

```bash
cp agent_role_templates/01_hpc_simulation_workflow_AGENT_ROLE_TEMPLATE.md 01_hpc_simulation_workflow/CLAUDE.md
```

On Windows PowerShell, run from the repository root, `Track_B/`:

```powershell
Copy-Item agent_role_templates\01_hpc_simulation_workflow_AGENT_ROLE_TEMPLATE.md 01_hpc_simulation_workflow\CLAUDE.md
```

If you are not using Claude Code, rename the copy to `AGENT_ROLE.md` instead, or paste the template contents into your tool's rules/system-prompt field.

### Step 2: Scope the agent to the sub-team folder

Configure your tool so the agent can access only:

```text
Track_B/01_hpc_simulation_workflow
```

If your agent tool asks for a working directory, project folder, allowed folder, or workspace root, set it to `Track_B/01_hpc_simulation_workflow`. Do not give the agent access to the whole Track B repository for this sub-team task.

### Step 3: Ask the agent to confirm its role

Ask the agent:

```text
Please read Track_B/01_hpc_simulation_workflow/CLAUDE.md and Track_B/01_hpc_simulation_workflow/00_SUBTEAM_GUIDE.md. Summarize your role, scope, restrictions, and workflow before doing anything else. Do not edit files until we approve a plan.
```

Check that the summary is faithful. In particular, the agent should not submit jobs, invent cluster details, or claim anything works on Dardel or NAISS without real verification.

Before moving on, update the **Task 1** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Task 2: Explore the Workflow Manually

**Goal:** Understand what the package is supposed to do before asking the agent to repair or validate it.

Imagine this is a real handoff from a colleague who says, "I think this should run on the cluster." Before trusting that claim, inspect the local evidence yourself. You want to know what would be submitted, which commands are implied, what files connect to each other, and what a sensible pre-submission check would need to verify.

Inspect, with your own eyes:

- `configs/sweep_parameters.csv`
- `scripts/simulate_oscillator.py`
- `scripts/run_sweep_local.py`
- `hpc/job_sweep.slurm`
- `hpc/modules.sh`
- the files in `logs/`

Write down:

- what parameters are swept;
- what command would run a single simulation;
- what command would run the local sweep;
- what the job script is trying to do;
- what the sample logs suggest;
- which issues are local workflow issues and which would only be verifiable on a real cluster;
- what checks you would want before sending this package to a real queue.

After your own exploration, you may ask the agent to clarify how the scripts, sweep table, job template, and logs fit together. Ask it to explain, not edit.

Before moving on, update the **Task 2** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Task 3: Build the Pre-submission Validator

**Goal:** Create `scripts/validate_package.py` from scratch so the workflow has explicit pre-submission checks before you try to repair it.

This task is intentionally concrete. A common research handoff lacks exactly this kind of guardrail, so you are building the safety net that should have existed.

Ask the agent to propose a small implementation plan before editing. The validator should run from `Track_B/01_hpc_simulation_workflow`:

```bash
python scripts/validate_package.py
```

Ask the agent to create `scripts/validate_package.py` with checks for:

- required files exist:
  - `configs/sweep_parameters.csv`
  - `configs/environment_example.txt`
  - `scripts/simulate_oscillator.py`
  - `scripts/run_sweep_local.py`
  - `hpc/job_sweep.slurm`
  - `hpc/modules.sh`
- `configs/sweep_parameters.csv` has the required columns: `run_id`, `mass`, `spring_constant`, `x0`, `v0`, `dt`, `n_steps`, `solver`;
- numeric parameter columns parse as numbers: `mass`, `spring_constant`, `x0`, `v0`, `dt`, `n_steps`;
- `run_id` values are unique;
- Python script paths referenced by `hpc/job_sweep.slurm` resolve relative to `Track_B/01_hpc_simulation_workflow`;
- `scripts/run_sweep_local.py` creates or handles the output directory before writing files.

The report should show a status per check, what was checked, the evidence, and a suggested next action for each warning or failure. PASS/WARN/FAIL is a good format.

After the validator exists, run from `Track_B/01_hpc_simulation_workflow`:

```bash
python scripts/validate_package.py
```

Record the output literally. A useful result in this task is not "everything passes"; it is that the validator exposes concrete workflow issues before any cluster submission.

Before moving on, update the **Task 3** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Task 4: Make the Local Sweep Reproducible

**Goal:** Use the participant-created validator and the local sweep commands to repair the package enough that it runs locally and produces reproducible output.

At this point, treat the local sweep as the closest safe rehearsal for the cluster workflow. If the local driver cannot run cleanly and regenerate outputs, the HPC submission script is not ready to trust.

Ask the agent to inspect the validator output and the workflow files, then propose the smallest reasonable fixes. Approve edits only after the agent explains the intended change.

Run from `Track_B/01_hpc_simulation_workflow`:

```bash
python scripts/validate_package.py
python scripts/run_sweep_local.py --dry-run
python scripts/run_sweep_local.py
```

Expected participant-created outputs include `outputs/local_sweep_summary.csv` and `outputs/local_sweep_diagnostics.png`, plus a local run command you trust.

After the edit, rerun the same commands and record what changed. Be explicit about which claims are verified locally and which would still require a real cluster.

Before moving on, update the **Task 4** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Task 5: Harden, Diagnose, or Package the Workflow

**Goal:** Turn the repaired workflow into something another researcher could understand, reuse, or debug.

This is the creative final task, but it should still produce a concrete product. Some directions you could take:

- extend `scripts/validate_package.py` with additional checks, such as sensible `dt`, positive `n_steps`, unique output names, documented output/log directories, or clearly marked cluster assumptions;
- generate `outputs/pre_submission_report.md`;
- write a submission runbook with exact local and cluster-side steps;
- draw a small workflow diagram in Markdown;
- add a CLI option that validates, dry-runs, and prints the `sbatch` command without submitting;
- create `scripts/diagnose_log.py` that classifies the sample logs by likely failure category;
- generate a Markdown or HTML report summarizing the sweep design;
- add a comparison plot of the local sweep outputs;
- add checks that state which parts are locally verified and which remain cluster assumptions.

Work check-first: define what the product should communicate, ask the agent for a small plan, define at least one check or command that verifies the product, implement, regenerate the outputs, and confirm your check.

Before moving on, update the **Task 5** section of <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">DEMO_REPORT_TEMPLATE.md</a>.

## Deliverable

A filled `DEMO_REPORT_TEMPLATE.md` saved inside `Track_B/01_hpc_simulation_workflow`. Use it to build your final 3-5 minute presentation: what the package was, what validator you built, what you repaired, how you made it locally reproducible, what hardening or diagnosis artifact you added, and what remains an unverified cluster assumption.

Next: <a href="01_VERIFY.md" target="_blank" rel="noopener noreferrer">open 01_VERIFY.md</a>.

# Commands and Verification

Every command below states the directory where it should be run.

## Environment Setup

Run from the repository root, `Track_B/`:

```bash
python -m pip install -r requirements.txt
```

Optional virtual environment setup, also from the repository root, `Track_B/`:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the virtual environment from the repository root, `Track_B/`:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

On Linux or macOS, activate the virtual environment from the repository root, `Track_B/`:

```bash
source .venv/bin/activate
```

## Shared Verification Prompt

After running a command, paste the exact output to the agent and ask:

```text
Interpret this output literally. Which checks passed, which failed, and what is the smallest next change? Distinguish verified facts from assumptions.
```

## Agent Role Templates

Task 1 in each sub-team guide asks you to copy a role template into the sub-team folder and then scope the agent to that sub-team folder only.

Run from the repository root, `Track_B/`, for sub-team 01:

```bash
cp agent_role_templates/01_hpc_simulation_workflow_AGENT_ROLE_TEMPLATE.md 01_hpc_simulation_workflow/CLAUDE.md
```

Run from the repository root, `Track_B/`, for sub-team 02:

```bash
cp agent_role_templates/02_research_code_debugging_AGENT_ROLE_TEMPLATE.md 02_research_code_debugging/CLAUDE.md
```

Run from the repository root, `Track_B/`, for sub-team 03:

```bash
cp agent_role_templates/03_scientific_postprocessing_AGENT_ROLE_TEMPLATE.md 03_scientific_postprocessing/CLAUDE.md
```

On Windows PowerShell, use `Copy-Item` with the same source and destination paths. If your tool is not Claude Code, copy to `AGENT_ROLE.md` instead or paste the template contents into the tool's rules/system-prompt field.

After copying the role file, set your agent tool's working directory, project folder, allowed folder, or workspace root to the matching sub-team folder:

- `Track_B/01_hpc_simulation_workflow`
- `Track_B/02_research_code_debugging`
- `Track_B/03_scientific_postprocessing`

## Sub-team 01: HPC Simulation Workflow

There is no starter `scripts/validate_package.py` for sub-team 01. Participants create it in Task 3.

For early exploration, run from `Track_B/01_hpc_simulation_workflow`:

```bash
python scripts/run_sweep_local.py --dry-run
```

After Task 3, when the participant-created validator exists, run from `Track_B/01_hpc_simulation_workflow`:

```bash
python scripts/validate_package.py
```

Later, when Task 4 asks for the full local sweep, run from `Track_B/01_hpc_simulation_workflow`:

```bash
python scripts/run_sweep_local.py
```

Expected starter state: no validator exists yet, and the dry-run prints the planned sweep. The full sweep should not be trusted until the group has inspected the workflow, built the validator, and repaired the issues it exposes.

Sub-team guide: <a href="01_hpc_simulation_workflow/00_SUBTEAM_GUIDE.md" target="_blank" rel="noopener noreferrer">01_hpc_simulation_workflow/00_SUBTEAM_GUIDE.md</a>

## Sub-team 02: Research-code Debugging

Run from `Track_B/02_research_code_debugging`:

```bash
python -m pytest -q
python scripts/run_simulation.py
python scripts/plot_simulation.py
```

Expected starter state: some tests should fail in a meaningful way, and the diagnostic output should invite a physical interpretation.

Sub-team guide: <a href="02_research_code_debugging/00_SUBTEAM_GUIDE.md" target="_blank" rel="noopener noreferrer">02_research_code_debugging/00_SUBTEAM_GUIDE.md</a>

## Sub-team 03: Scientific Post-processing

Run from `Track_B/03_scientific_postprocessing`:

```bash
python -m pytest -q
python scripts/quicklook.py --dataset reference
python scripts/quicklook.py --dataset challenge
```

Expected starter state: dataset-integrity tests should pass, and the quicklook figures should give the group evidence to inspect before making claims.

Sub-team guide: <a href="03_scientific_postprocessing/00_SUBTEAM_GUIDE.md" target="_blank" rel="noopener noreferrer">03_scientific_postprocessing/00_SUBTEAM_GUIDE.md</a>

Next: choose a sub-team and open its `00_SUBTEAM_GUIDE.md`:
<a href="01_hpc_simulation_workflow/00_SUBTEAM_GUIDE.md" target="_blank" rel="noopener noreferrer">01</a>,
<a href="02_research_code_debugging/00_SUBTEAM_GUIDE.md" target="_blank" rel="noopener noreferrer">02</a>, or
<a href="03_scientific_postprocessing/00_SUBTEAM_GUIDE.md" target="_blank" rel="noopener noreferrer">03</a>.

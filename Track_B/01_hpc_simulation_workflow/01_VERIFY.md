# Verify Sub-team 01

Use these commands for the HPC simulation workflow.

## Setup

Run dependency setup from the repository root, `Track_B/`:

```bash
python -m pip install -r requirements.txt
```

Shared setup notes are in <a href="../02_COMMANDS_AND_VERIFY.md" target="_blank" rel="noopener noreferrer">../02_COMMANDS_AND_VERIFY.md</a>.

## Early Exploration Command

There is no starter `scripts/validate_package.py`. You create it in Task 3.

Before Task 3, the safe runnable command is the dry-run. Run from `Track_B/01_hpc_simulation_workflow`:

```bash
python scripts/run_sweep_local.py --dry-run
```

The dry-run should print planned runs without writing output files.

## After Task 3: Validator Command

After you create `scripts/validate_package.py`, run from `Track_B/01_hpc_simulation_workflow`:

```bash
python scripts/validate_package.py
```

The validator should report PASS/WARN/FAIL evidence and point to issues that should be fixed before a human trusts the workflow.

## Task 4: Full Local Sweep

Run from `Track_B/01_hpc_simulation_workflow`:

```bash
python scripts/validate_package.py
python scripts/run_sweep_local.py --dry-run
python scripts/run_sweep_local.py
```

Expected participant-created outputs include:

- `outputs/local_sweep_summary.csv`
- `outputs/local_sweep_diagnostics.png`

Do not commit files under `outputs/`.

## Verification Question

After each command, ask the agent:

```text
Which facts are verified locally by this output, and which claims would still require real cluster access?
```

Next: <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">update DEMO_REPORT_TEMPLATE.md</a>.

# Verify Sub-team 02

Use these commands for research-code debugging.

## Setup

Run dependency setup from the repository root, `Track_B/`:

```bash
python -m pip install -r requirements.txt
```

Shared setup notes are in <a href="../02_COMMANDS_AND_VERIFY.md" target="_blank" rel="noopener noreferrer">../02_COMMANDS_AND_VERIFY.md</a>.

## Starter Checks

Run from `Track_B/02_research_code_debugging`:

```bash
python -m pytest -q
python scripts/run_simulation.py
python scripts/plot_simulation.py
```

`python scripts/plot_simulation.py` writes `outputs/oscillator_diagnostics.png`.

On Linux or macOS, `./run_tests.sh` is a convenience wrapper for the pytest command. On Windows PowerShell, run `python -m pytest -q` directly from `Track_B/02_research_code_debugging`.

## After a Fix or Extension

Run from `Track_B/02_research_code_debugging`:

```bash
python -m pytest -q
python scripts/run_simulation.py
python scripts/plot_simulation.py
```

Ask whether the output supports the physical expectation, not only whether the code runs.

Next: <a href="DEMO_REPORT_TEMPLATE.md" target="_blank" rel="noopener noreferrer">update DEMO_REPORT_TEMPLATE.md</a>.

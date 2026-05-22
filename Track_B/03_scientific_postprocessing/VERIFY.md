# Setup and verification commands

This file lists the exact commands for setting up a virtual environment and running the
verification steps the README asks for. Where the command differs between Windows
PowerShell and Linux/macOS, both are shown.

## 1. One-time environment setup

### Windows (PowerShell)

```
cd C:\agentathon-track-b\Track_B
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Linux / macOS

```
cd Track_B
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Quick dependency check (both platforms)

```
python -c "import numpy, pandas, matplotlib, pytest"
```

If this exits silently, you are set. If it raises `ModuleNotFoundError`, repeat the
setup step above with the environment active.

## 2. Run the verification commands

With the environment active, move into this sub-team folder and run the checks.

### Windows (PowerShell)

```
cd .\03_scientific_postprocessing
python -m pytest -v tests
python scripts/quicklook.py --dataset reference
python scripts/quicklook.py --dataset challenge
```

### Linux / macOS

```
cd 03_scientific_postprocessing
python -m pytest -v tests
python scripts/quicklook.py --dataset reference
python scripts/quicklook.py --dataset challenge
```

`quicklook.py` writes `outputs/<dataset>/quicklook.png`. The `outputs/` folder is
gitignored — do not commit anything in it.

The datasets are already provided under `data/reference/` and `data/challenge/`. You do
not need to regenerate them, but for transparency you can:
`python scripts/generate_dataset.py` rewrites all six files deterministically.

## Adding your own checks

From Task 3 onward you will create your own analysis scripts, guardrails, and a visual
product. Treat every new artefact as something that must be **regenerable and verified**:

- each new analysis or visual product should have at least one command, test, or check
  that confirms it can be regenerated from the data;
- prefer defining the expected output and the check **before** you implement;
- a figure, table, or written summary is not "done" unless a single command reproduces
  it.

Add your checks under `tests/` or as a `scripts/check_*.py` you can rerun.

## What to expect

- **Initial state (as shipped):** the dataset-integrity tests pass for both datasets, and
  `quicklook.py` prints a structure summary and writes `outputs/reference/quicklook.png`
  and `outputs/challenge/quicklook.png`. Open the figures and decide for yourself whether
  anything needs follow-up.
- **Task 3:** you create a reproducible analysis script and generate figures, a table,
  and a short summary under `outputs/reference/`, plus at least one check that the
  outputs were produced.
- **Task 4:** you apply the analysis to `data/challenge`, add data-quality checks, and
  report which run(s) or group(s) you flagged, with the evidence behind them.
- **Task 5:** your visual product is verified by a command, test, or check that
  regenerates it.

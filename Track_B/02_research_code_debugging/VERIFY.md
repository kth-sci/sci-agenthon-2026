# Setup and verification commands

This file lists the exact commands for setting up a virtual environment and running
the verification steps the README asks for. Where the command differs between Windows
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
python -c "import numpy, matplotlib, pytest"
```

If this exits silently, you are set. If it raises `ModuleNotFoundError`, repeat the
setup step above with the environment active.

## 2. Run the verification commands

With the environment active, move into this sub-team folder and run the three
commands.

### Windows (PowerShell)

```
cd .\02_research_code_debugging
python -m pytest -v tests
python scripts/run_simulation.py
python scripts/plot_simulation.py
```

### Linux / macOS

```
cd 02_research_code_debugging
python -m pytest -v tests
python scripts/run_simulation.py
python scripts/plot_simulation.py
```

On Linux/macOS, `./run_tests.sh` is a convenience wrapper for the pytest command.
Windows PowerShell cannot execute the `.sh` wrapper directly; use
`python -m pytest -v tests`.

`python scripts/plot_simulation.py` writes `outputs/oscillator_diagnostics.png`. The
`outputs/` folder is gitignored — do not commit the PNG.

## What to expect

- **Initial state (as shipped):** several tests fail in a meaningful way — the
  failure messages describe physics and motion, not crashes or import errors — and
  the rest pass. The script output and the diagnostic plot show behaviour you should
  interpret against the analytical reference. Decide for yourself what looks wrong.
- **After a correct minimal fix:** the currently-failing tests should pass, and the
  diagnostic plot should change visibly. Look closely — some imperfection may still
  remain for you to interpret.
- **After Task 4:** the new tests you wrote should verify the extension you chose,
  and the existing tests should still pass.

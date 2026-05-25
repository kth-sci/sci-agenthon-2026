#!/usr/bin/env python3
"""Check that the Track B starter repository is in the expected pedagogical state.

This script is for the facilitator. It deliberately expects some commands to fail,
because those failures are the teaching material.

Run from the top-level Track_B folder:

    python _facilitator/check_starter_state.py
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Check:
    name: str
    cwd: Path
    command: list[str]
    expected_returncode: int | None
    must_contain: list[str]


def run_check(check: Check) -> bool:
    print(f"\n=== {check.name} ===")
    print("cwd:", check.cwd.relative_to(ROOT))
    print("cmd:", " ".join(check.command))
    proc = subprocess.run(
        check.command,
        cwd=check.cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=60,
    )
    output = proc.stdout
    print(output[-3000:] if len(output) > 3000 else output)

    ok = True
    if check.expected_returncode is not None and proc.returncode != check.expected_returncode:
        print(f"UNEXPECTED return code: got {proc.returncode}, expected {check.expected_returncode}")
        ok = False
    for needle in check.must_contain:
        if needle not in output:
            print(f"MISSING expected text: {needle!r}")
            ok = False
    print("STATUS:", "OK" if ok else "CHECK THIS")
    return ok


def check_absent(name: str, path: Path) -> bool:
    print(f"\n=== {name} ===")
    print("path:", path.relative_to(ROOT))
    ok = not path.exists()
    if ok:
        print("Expected absent file is absent.")
    else:
        print("Unexpected file exists.")
    print("STATUS:", "OK" if ok else "CHECK THIS")
    return ok


def main() -> int:
    checks = [
        Check(
            name="01 dry run succeeds",
            cwd=ROOT / "01_hpc_simulation_workflow",
            command=[sys.executable, "scripts/run_sweep_local.py", "--dry-run"],
            expected_returncode=0,
            must_contain=["Dry run complete: 10 runs planned"],
        ),
        Check(
            name="02 tests have expected failures",
            cwd=ROOT / "02_research_code_debugging",
            command=[sys.executable, "-m", "pytest", "-q", "tests"],
            expected_returncode=1,
            must_contain=["test_acceleration_is_restoring_force"],
        ),
        Check(
            name="03 dataset integrity tests pass",
            cwd=ROOT / "03_scientific_postprocessing",
            command=[sys.executable, "-m", "pytest", "-q", "tests"],
            expected_returncode=0,
            must_contain=["passed"],
        ),
        Check(
            name="03 challenge quicklook succeeds",
            cwd=ROOT / "03_scientific_postprocessing",
            command=[sys.executable, "scripts/quicklook.py", "--dataset", "challenge"],
            expected_returncode=0,
            must_contain=["Saved first-look figure"],
        ),
    ]
    results = [
        check_absent(
            "01 validator is absent at starter state",
            ROOT / "01_hpc_simulation_workflow" / "scripts" / "validate_package.py",
        )
    ]
    results.extend(run_check(c) for c in checks)
    print("\n=== Summary ===")
    print(f"{sum(results)}/{len(results)} checks are in the expected starter state")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

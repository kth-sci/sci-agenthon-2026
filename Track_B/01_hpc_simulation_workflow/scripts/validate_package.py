"""Pre-submission validation for the HPC oscillator-sweep package.

Runs a set of static checks over the package and prints a PASS / WARN / FAIL report.
It does NOT submit anything and does NOT require a cluster. This is the package's main
guardrail: the initial version covers some useful checks, and you are expected to extend
it in Task 4 so that common pre-submission problems are caught before a human ever sends
the job script to a cluster.

Run it with:
    python scripts/validate_package.py
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PACKAGE_ROOT / "configs" / "sweep_parameters.csv"
JOB_SCRIPT = PACKAGE_ROOT / "hpc" / "job_sweep.slurm"
RUN_SWEEP = PACKAGE_ROOT / "scripts" / "run_sweep_local.py"

REQUIRED_FILES = [
    "configs/sweep_parameters.csv",
    "configs/environment_example.txt",
    "scripts/simulate_oscillator.py",
    "scripts/run_sweep_local.py",
    "scripts/validate_package.py",
    "hpc/job_sweep.slurm",
    "hpc/modules.sh",
]

REQUIRED_COLUMNS = ["run_id", "mass", "spring_constant", "x0", "v0", "dt", "n_steps", "solver"]
NUMERIC_COLUMNS = ["mass", "spring_constant", "x0", "v0", "dt", "n_steps"]


@dataclass
class Result:
    status: str  # "PASS", "WARN", or "FAIL"
    name: str
    evidence: str
    action: str = ""


def check_required_files() -> Result:
    missing = [rel for rel in REQUIRED_FILES if not (PACKAGE_ROOT / rel).is_file()]
    if missing:
        return Result("FAIL", "required files exist", f"missing: {', '.join(missing)}",
                      "restore the missing files before proceeding")
    return Result("PASS", "required files exist", f"all {len(REQUIRED_FILES)} present")


def check_required_columns() -> Result:
    if not CONFIG_PATH.is_file():
        return Result("FAIL", "sweep columns present", "sweep_parameters.csv not found", "")
    rows = pd.read_csv(CONFIG_PATH)
    missing = [c for c in REQUIRED_COLUMNS if c not in rows.columns]
    if missing:
        return Result("FAIL", "sweep columns present", f"missing columns: {', '.join(missing)}",
                      "add the missing columns to sweep_parameters.csv")
    return Result("PASS", "sweep columns present", f"all {len(REQUIRED_COLUMNS)} present")


def check_numeric_parseable() -> Result:
    if not CONFIG_PATH.is_file():
        return Result("FAIL", "numeric parameters parseable", "sweep_parameters.csv not found", "")
    rows = pd.read_csv(CONFIG_PATH)
    bad = []
    for col in NUMERIC_COLUMNS:
        if col in rows.columns:
            coerced = pd.to_numeric(rows[col], errors="coerce")
            if coerced.isna().any():
                bad.append(col)
    if bad:
        return Result("FAIL", "numeric parameters parseable",
                      f"non-numeric values in: {', '.join(bad)}",
                      "make every parameter column numeric")
    return Result("PASS", "numeric parameters parseable", "all numeric columns parse")


def check_run_id_unique() -> Result:
    if not CONFIG_PATH.is_file():
        return Result("FAIL", "run_id values unique", "sweep_parameters.csv not found", "")
    rows = pd.read_csv(CONFIG_PATH)
    dups = rows["run_id"][rows["run_id"].duplicated()].unique().tolist()
    if dups:
        return Result("FAIL", "run_id values unique", f"duplicates: {', '.join(map(str, dups))}",
                      "make every run_id unique")
    return Result("PASS", "run_id values unique", f"{rows['run_id'].nunique()} unique run_id values")


def check_job_script_paths() -> Result:
    if not JOB_SCRIPT.is_file():
        return Result("FAIL", "job-script paths resolve", "hpc/job_sweep.slurm not found", "")
    text = JOB_SCRIPT.read_text()
    referenced = re.findall(r"python\d?\s+([^\s]+\.py)", text)
    missing = [p for p in referenced if not (PACKAGE_ROOT / p).is_file()]
    if missing:
        return Result(
            "FAIL", "job-script paths resolve",
            f"job_sweep.slurm runs {', '.join(missing)}, which does not exist relative to the package root",
            "check the script path and the working directory the job assumes",
        )
    return Result("PASS", "job-script paths resolve",
                  f"referenced script(s) found: {', '.join(referenced) or 'none'}")


def check_output_dir_created() -> Result:
    if not RUN_SWEEP.is_file():
        return Result("FAIL", "output directory is created", "run_sweep_local.py not found", "")
    text = RUN_SWEEP.read_text()
    if "mkdir" not in text:
        return Result(
            "WARN", "output directory is created",
            "run_sweep_local.py does not appear to create its output directory before writing",
            "ensure the output directory is created or validated before files are written",
        )
    return Result("PASS", "output directory is created", "run_sweep_local.py creates its output directory")


# Checks run in order. Task 4: add new checks by writing a function above and listing it here.
CHECKS = [
    check_required_files,
    check_required_columns,
    check_numeric_parseable,
    check_run_id_unique,
    check_job_script_paths,
    check_output_dir_created,
]


def main() -> int:
    results = [check() for check in CHECKS]

    print("Pre-submission validation report")
    print("=" * 72)
    for r in results:
        print(f"[{r.status:<4}] {r.name}")
        print(f"        evidence: {r.evidence}")
        if r.action and r.status != "PASS":
            print(f"        next:     {r.action}")
    print("=" * 72)

    n_pass = sum(r.status == "PASS" for r in results)
    n_warn = sum(r.status == "WARN" for r in results)
    n_fail = sum(r.status == "FAIL" for r in results)
    print(f"summary: {n_pass} PASS, {n_warn} WARN, {n_fail} FAIL")
    if n_fail:
        print("Result: FAIL — resolve the failing checks before this package is submission-ready.")
    elif n_warn:
        print("Result: PASS with warnings — review the warnings above.")
    else:
        print("Result: PASS — all checks passed.")

    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())

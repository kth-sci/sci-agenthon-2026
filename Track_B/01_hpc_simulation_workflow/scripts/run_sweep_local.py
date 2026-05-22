"""Run the harmonic-oscillator parameter sweep locally (a stand-in for the cluster run).

Reads configs/sweep_parameters.csv and, for each row, integrates one simulation using
the functions in simulate_oscillator.py. This is how you reproduce the sweep on your own
machine before it would ever be submitted to a cluster.

Examples:
    python scripts/run_sweep_local.py --dry-run     # print the plan, write nothing
    python scripts/run_sweep_local.py               # run the sweep locally
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Make the sibling simulate_oscillator.py importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from simulate_oscillator import integrate

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = PACKAGE_ROOT / "configs" / "sweep_parameters.csv"
DEFAULT_OUTPUT_DIR = PACKAGE_ROOT / "outputs"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the local parameter sweep (or print the plan with --dry-run).",
    )
    parser.add_argument("--config", default=str(DEFAULT_CONFIG), help="sweep configuration CSV")
    parser.add_argument(
        "--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="directory for run outputs"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the command that would run for each row and write nothing",
    )
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    config_path = Path(args.config)
    output_dir = Path(args.output_dir)

    rows = pd.read_csv(config_path)
    print(f"Loaded {len(rows)} runs from {config_path}")

    if args.dry_run:
        print("Dry run — the following simulations would be executed:\n")
        for _, row in rows.iterrows():
            out = output_dir / f"{row['run_id']}.csv"
            print(
                "python scripts/simulate_oscillator.py "
                f"--run-id {row['run_id']} --mass {row['mass']} "
                f"--spring-constant {row['spring_constant']} --x0 {row['x0']} "
                f"--v0 {row['v0']} --dt {row['dt']} --n-steps {row['n_steps']} "
                f"--solver {row['solver']} --output {out}"
            )
        print(f"\nDry run complete: {len(rows)} runs planned. Nothing was written.")
        return

    summary = []
    for _, row in rows.iterrows():
        print(
            f"[{row['run_id']}] solver={row['solver']} dt={row['dt']} "
            f"n_steps={row['n_steps']} mass={row['mass']} k={row['spring_constant']}"
        )
        time, positions, velocities, energy = integrate(
            mass=float(row["mass"]),
            spring_constant=float(row["spring_constant"]),
            x0=float(row["x0"]),
            v0=float(row["v0"]),
            dt=float(row["dt"]),
            n_steps=int(row["n_steps"]),
            solver=str(row["solver"]),
        )

        run_csv = output_dir / f"{row['run_id']}.csv"
        with open(run_csv, "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["time", "x", "v", "energy"])
            for record in zip(time, positions, velocities, energy):
                writer.writerow([f"{value:.10g}" for value in record])

        e0 = energy[0]
        summary.append(
            {
                "run_id": row["run_id"],
                "solver": row["solver"],
                "dt": row["dt"],
                "n_steps": row["n_steps"],
                "n_points": len(time),
                "max_abs_x": float(np.max(np.abs(positions))),
                "final_energy": float(energy[-1]),
                "energy_drift": float(np.max(np.abs(energy - e0)) / abs(e0)) if e0 else float("nan"),
                "output": str(run_csv.relative_to(PACKAGE_ROOT)),
            }
        )

    summary_df = pd.DataFrame(summary)
    summary_path = output_dir / "local_sweep_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(summary_df["run_id"].astype(str), summary_df["max_abs_x"])
    ax.set_ylabel("max |x(t)|")
    ax.set_xlabel("run_id")
    ax.set_title("Local sweep: peak amplitude per run")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    diagnostics_path = output_dir / "local_sweep_diagnostics.png"
    fig.savefig(diagnostics_path, dpi=120)
    plt.close(fig)

    print(f"\nWrote summary to {summary_path}")
    print(f"Wrote diagnostics figure to {diagnostics_path}")


if __name__ == "__main__":
    main()

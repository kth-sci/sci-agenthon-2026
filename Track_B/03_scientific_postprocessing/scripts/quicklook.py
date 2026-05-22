"""First-look summary of a harmonic-oscillator post-processing dataset.

Prints a neutral description of the data structure and writes a first-look figure to
outputs/<dataset>/quicklook.png. This is a starting point for your own analysis, not a
finished result.

Usage:
    python scripts/quicklook.py --dataset reference
    python scripts/quicklook.py --dataset challenge
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"


def load_data(dataset: str):
    data_dir = DATA_DIR / dataset
    raw_runs = pd.read_csv(data_dir / "raw_runs.csv")
    trajectories = pd.read_csv(data_dir / "trajectories_sample.csv")
    with open(data_dir / "metadata.json", encoding="utf-8") as fh:
        metadata = json.load(fh)
    return raw_runs, trajectories, metadata


def print_structure(dataset: str, raw_runs, trajectories):
    data_dir = DATA_DIR / dataset
    print(f"dataset: {dataset}")
    print("data files:")
    print(f"  - {data_dir / 'raw_runs.csv'}")
    print(f"  - {data_dir / 'trajectories_sample.csv'}")
    print(f"  - {data_dir / 'metadata.json'}")
    print()
    print(f"raw_runs.csv: {len(raw_runs)} rows")
    print(f"  columns: {list(raw_runs.columns)}")
    print(f"trajectories_sample.csv: {len(trajectories)} rows")
    print(f"  columns: {list(trajectories.columns)}")
    print()
    print(f"solver labels: {sorted(raw_runs['solver'].unique())}")
    dt_values = sorted(round(float(v), 6) for v in raw_runs["dt"].unique())
    print(f"dt values: {dt_values}")
    print(f"unique run_id in raw_runs: {raw_runs['run_id'].nunique()}")
    print(f"sampled trajectories (unique run_id): {trajectories['run_id'].nunique()}")
    print()


def make_figure(dataset: str, raw_runs, trajectories):
    output_dir = OUTPUT_DIR / dataset
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "quicklook.png"

    solvers = sorted(raw_runs["solver"].unique())
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))

    for solver in solvers:
        sub = raw_runs[raw_runs["solver"] == solver].sort_values("dt")
        axes[0].plot(sub["dt"], sub["final_position_error"], marker="o", label=solver)
        axes[1].plot(sub["dt"], sub["max_energy_error"], marker="o", label=solver)
    for ax, ylabel, title in (
        (axes[0], "final_position_error", "Final position error vs time step"),
        (axes[1], "max_energy_error", "Max energy error vs time step"),
    ):
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("dt")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.grid(True, which="both", alpha=0.3)

    for run_id in sorted(trajectories["run_id"].unique()):
        sub = trajectories[trajectories["run_id"] == run_id].sort_values("time")
        axes[2].plot(sub["time"], sub["x_numeric"], marker=".", markersize=3, label=run_id)
    axes[2].set_xlabel("time")
    axes[2].set_ylabel("x_numeric")
    axes[2].set_title("Sampled position traces")
    axes[2].legend(fontsize=8)
    axes[2].grid(True, alpha=0.3)

    fig.suptitle(f"Quicklook — {dataset} dataset")
    fig.tight_layout()
    fig.savefig(output_path, dpi=120)
    plt.close(fig)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset",
        choices=["reference", "challenge"],
        default="reference",
        help="which dataset to summarise (default: reference)",
    )
    args = parser.parse_args()

    raw_runs, trajectories, _metadata = load_data(args.dataset)
    print_structure(args.dataset, raw_runs, trajectories)
    output_path = make_figure(args.dataset, raw_runs, trajectories)
    print(f"Saved first-look figure to: {output_path}")
    print("Inspect the figure and decide whether any runs, groups, or trends need follow-up.")


if __name__ == "__main__":
    main()

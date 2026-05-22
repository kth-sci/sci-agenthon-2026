"""Generate the synthetic harmonic-oscillator post-processing datasets.

Produces two batches with the same schema, under ../data/:
  - data/reference/{raw_runs.csv, trajectories_sample.csv, metadata.json}
  - data/challenge/{raw_runs.csv, trajectories_sample.csv, metadata.json}

The model is the undamped 1D harmonic oscillator m x'' = -k x. Several integrators are
run across a range of time steps so the data supports method comparison. The output is
deterministic for a fixed seed.

Usage:
    python scripts/generate_dataset.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20260522
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Fixed physical setup shared by every run.
MASS = 1.0
SPRING_CONSTANT = 1.0
X0 = 1.0
V0 = 0.0
N_PERIODS = 4
STEPS_PER_PERIOD = [50, 100, 200, 400, 800]
SOLVERS = ["euler", "semi_implicit_euler", "verlet", "rk4"]

# Relative per-step cost used to build a deterministic runtime proxy.
STEP_COST = {"euler": 1.0, "semi_implicit_euler": 1.0, "verlet": 2.0, "rk4": 4.0}

# Which time step is captured in the trajectory sample, and how many points per trace.
SAMPLE_STEPS_PER_PERIOD = 200
SAMPLE_POINTS = 80


def acceleration(x: float) -> float:
    return -SPRING_CONSTANT * x / MASS


def analytical_position(t, omega: float):
    return X0 * np.cos(omega * t) + (V0 / omega) * np.sin(omega * t)


def step(solver: str, x: float, v: float, dt: float):
    if solver == "euler":
        a = acceleration(x)
        return x + v * dt, v + a * dt
    if solver == "semi_implicit_euler":
        v_new = v + acceleration(x) * dt
        return x + v_new * dt, v_new
    if solver == "verlet":
        a = acceleration(x)
        x_new = x + v * dt + 0.5 * a * dt * dt
        v_new = v + 0.5 * (a + acceleration(x_new)) * dt
        return x_new, v_new
    if solver == "rk4":
        def deriv(x_, v_):
            return v_, acceleration(x_)

        k1x, k1v = deriv(x, v)
        k2x, k2v = deriv(x + 0.5 * dt * k1x, v + 0.5 * dt * k1v)
        k3x, k3v = deriv(x + 0.5 * dt * k2x, v + 0.5 * dt * k2v)
        k4x, k4v = deriv(x + dt * k3x, v + dt * k3v)
        x_new = x + (dt / 6.0) * (k1x + 2 * k2x + 2 * k3x + k4x)
        v_new = v + (dt / 6.0) * (k1v + 2 * k2v + 2 * k3v + k4v)
        return x_new, v_new
    raise ValueError(f"unknown solver: {solver}")


def integrate(solver: str, dt: float, n_steps: int):
    xs = np.empty(n_steps + 1)
    vs = np.empty(n_steps + 1)
    xs[0], vs[0] = X0, V0
    for i in range(n_steps):
        xs[i + 1], vs[i + 1] = step(solver, xs[i], vs[i], dt)
    return xs, vs


def estimate_period(t, x) -> float:
    """Estimate the period from interpolated upward zero-crossings of x(t)."""
    crossings = []
    for i in range(len(x) - 1):
        if x[i] <= 0.0 < x[i + 1]:
            frac = (0.0 - x[i]) / (x[i + 1] - x[i])
            crossings.append(t[i] + frac * (t[i + 1] - t[i]))
    if len(crossings) < 2:
        return float("nan")
    return float(np.mean(np.diff(crossings)))


def simulate_grid(rng):
    """Run every (solver, time step) combination once; return rows and full traces."""
    omega = float(np.sqrt(SPRING_CONSTANT / MASS))
    period = 2.0 * np.pi / omega

    rows = []
    full_traces = {}
    run_index = 0
    for solver in SOLVERS:
        for spp in STEPS_PER_PERIOD:
            run_id = f"r{run_index:03d}"
            run_index += 1
            dt = period / spp
            n_steps = N_PERIODS * spp
            t = np.arange(n_steps + 1) * dt
            xs, vs = integrate(solver, dt, n_steps)
            x_ref = analytical_position(t, omega)
            energy = 0.5 * MASS * vs ** 2 + 0.5 * SPRING_CONSTANT * xs ** 2
            e0 = energy[0]

            est_period = estimate_period(t, xs)
            period_error = (
                abs(est_period - period) / period if np.isfinite(est_period) else 0.0
            )
            runtime_proxy = (
                n_steps * STEP_COST[solver] * (1.0 + 0.02 * float(rng.standard_normal()))
            )

            rows.append(
                {
                    "run_id": run_id,
                    "solver": solver,
                    "dt": dt,
                    "n_steps": n_steps,
                    "mass": MASS,
                    "spring_constant": SPRING_CONSTANT,
                    "x0": X0,
                    "v0": V0,
                    "n_periods": N_PERIODS,
                    "final_position_error": float(abs(xs[-1] - x_ref[-1])),
                    "max_energy_error": float(np.max(np.abs(energy - e0) / abs(e0))),
                    "period_error": float(period_error),
                    "runtime_proxy": float(runtime_proxy),
                    "status": "ok",
                }
            )

            if spp == SAMPLE_STEPS_PER_PERIOD:
                full_traces[run_id] = {
                    "t": t,
                    "x_numeric": xs,
                    "v_numeric": vs,
                    "x_reference": x_ref,
                    "energy": energy,
                }

    return rows, full_traces


def build_trajectories(sample_ids, full_traces, points, fraction):
    rows = []
    for run_id in sample_ids:
        tr = full_traces[run_id]
        n = len(tr["t"])
        upper = max(2, int(round(n * fraction[run_id])))
        idx = np.unique(np.linspace(0, upper - 1, points[run_id]).astype(int))
        for j in idx:
            rows.append(
                {
                    "run_id": run_id,
                    "time": float(tr["t"][j]),
                    "x_numeric": float(tr["x_numeric"][j]),
                    "v_numeric": float(tr["v_numeric"][j]),
                    "x_reference": float(tr["x_reference"][j]),
                    "energy": float(tr["energy"][j]),
                }
            )
    return pd.DataFrame(rows)


def build_dataset(rng, adjust: bool):
    rows, full_traces = simulate_grid(rng)
    runs = pd.DataFrame(rows)
    sample_ids = list(full_traces)

    points = {rid: SAMPLE_POINTS for rid in sample_ids}
    fraction = {rid: 1.0 for rid in sample_ids}

    if adjust:
        # A small number of per-run adjustments to the generated values.
        emphasised = (runs["solver"] == "verlet") & (runs["n_steps"] == N_PERIODS * 100)
        runs.loc[emphasised, ["max_energy_error", "final_position_error"]] *= 500.0

        partial = runs.loc[
            runs["run_id"].isin(sample_ids)
            & (runs["solver"] == "semi_implicit_euler"),
            "run_id",
        ].iloc[0]
        points[partial] = 40
        fraction[partial] = 0.5

    trajectories = build_trajectories(sample_ids, full_traces, points, fraction)
    return runs, trajectories


def build_metadata(dataset_name: str):
    return {
        "dataset": dataset_name,
        "source": "Synthetic undamped harmonic-oscillator simulation outputs.",
        "generated_by": "scripts/generate_dataset.py (deterministic, fixed seed).",
        "note": (
            "These are synthetic simulation outputs. Inspect and validate data quality "
            "before drawing scientific conclusions; do not assume every row or trace is "
            "complete and consistent."
        ),
        "run_id_link": (
            "run_id is the key that connects the two data files: each summary row in "
            "raw_runs.csv has a unique run_id, and each time-series row in "
            "trajectories_sample.csv carries the run_id of the run it belongs to. Only a "
            "subset of runs is captured in trajectories_sample.csv."
        ),
        "files": {
            "raw_runs.csv": {
                "description": "One summary row per simulation run.",
                "columns": {
                    "run_id": {"meaning": "Unique run identifier.", "kind": "identifier"},
                    "solver": {"meaning": "Name of the time integrator used.", "kind": "parameter"},
                    "dt": {"meaning": "Integration time step.", "kind": "parameter"},
                    "n_steps": {"meaning": "Number of integration steps.", "kind": "parameter"},
                    "mass": {"meaning": "Oscillator mass m.", "kind": "parameter"},
                    "spring_constant": {"meaning": "Spring constant k.", "kind": "parameter"},
                    "x0": {"meaning": "Initial position.", "kind": "parameter"},
                    "v0": {"meaning": "Initial velocity.", "kind": "parameter"},
                    "n_periods": {"meaning": "Number of analytical periods requested.", "kind": "parameter"},
                    "final_position_error": {
                        "meaning": "Absolute error of the final position vs the analytical reference.",
                        "kind": "output",
                    },
                    "max_energy_error": {
                        "meaning": "Maximum relative deviation of total energy from its initial value over the run.",
                        "kind": "output",
                    },
                    "period_error": {
                        "meaning": "Relative error of the period estimated from the numerical trajectory vs the analytical period.",
                        "kind": "output",
                    },
                    "runtime_proxy": {
                        "meaning": "Relative cost proxy for the run (not a wall-clock measurement).",
                        "kind": "output",
                    },
                    "status": {"meaning": "Reported run status.", "kind": "output"},
                },
            },
            "trajectories_sample.csv": {
                "description": "Downsampled time-series traces for a subset of runs.",
                "columns": {
                    "run_id": {"meaning": "Run identifier (matches raw_runs.csv).", "kind": "identifier"},
                    "time": {"meaning": "Simulation time.", "kind": "parameter"},
                    "x_numeric": {"meaning": "Numerical position at this time.", "kind": "output"},
                    "v_numeric": {"meaning": "Numerical velocity at this time.", "kind": "output"},
                    "x_reference": {"meaning": "Analytical reference position at this time.", "kind": "output"},
                    "energy": {"meaning": "Total energy of the numerical state at this time.", "kind": "output"},
                },
            },
            "metadata.json": {
                "description": "This file: describes the dataset, the files, and the columns.",
            },
        },
    }


def write_dataset(target_dir: Path, dataset_name: str, runs, trajectories) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    runs.to_csv(target_dir / "raw_runs.csv", index=False)
    trajectories.to_csv(target_dir / "trajectories_sample.csv", index=False)
    with open(target_dir / "metadata.json", "w", encoding="utf-8") as fh:
        json.dump(build_metadata(dataset_name), fh, indent=2)
        fh.write("\n")
    print(
        f"[{dataset_name}] wrote {len(runs)} runs and {len(trajectories)} trajectory "
        f"rows to {target_dir}"
    )


def main() -> None:
    ref_runs, ref_traj = build_dataset(np.random.default_rng(SEED), adjust=False)
    ch_runs, ch_traj = build_dataset(np.random.default_rng(SEED + 1), adjust=True)

    write_dataset(DATA_DIR / "reference", "reference", ref_runs, ref_traj)
    write_dataset(DATA_DIR / "challenge", "challenge", ch_runs, ch_traj)


if __name__ == "__main__":
    main()

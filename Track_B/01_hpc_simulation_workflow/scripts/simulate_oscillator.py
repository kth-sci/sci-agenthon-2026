"""Run a single harmonic-oscillator simulation and write its trajectory to CSV.

This is a small stand-in for a real scientific simulation code. It integrates the
undamped 1D harmonic oscillator m x'' = -k x with a chosen time integrator and writes
one CSV (columns: time, x, v, energy) for one run.

Examples:
    python scripts/simulate_oscillator.py --help
    python scripts/simulate_oscillator.py --run-id demo --mass 1.0 --spring-constant 1.0 \\
        --x0 1.0 --v0 0.0 --dt 0.01 --n-steps 2000 --solver verlet --output demo.csv
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

SOLVERS = ("euler", "semi_implicit_euler", "verlet")


def acceleration(x: float, spring_constant: float, mass: float) -> float:
    return -spring_constant * x / mass


def integrate(mass, spring_constant, x0, v0, dt, n_steps, solver):
    """Return (time, x, v, energy) arrays for one run. Correct oscillator physics."""
    if solver not in SOLVERS:
        raise ValueError(f"unknown solver: {solver!r} (choose from {', '.join(SOLVERS)})")

    positions = np.empty(n_steps + 1)
    velocities = np.empty(n_steps + 1)
    positions[0], velocities[0] = float(x0), float(v0)

    for i in range(n_steps):
        x, v = positions[i], velocities[i]
        if solver == "euler":
            a = acceleration(x, spring_constant, mass)
            positions[i + 1] = x + v * dt
            velocities[i + 1] = v + a * dt
        elif solver == "semi_implicit_euler":
            v_new = v + acceleration(x, spring_constant, mass) * dt
            positions[i + 1] = x + v_new * dt
            velocities[i + 1] = v_new
        else:  # verlet
            a = acceleration(x, spring_constant, mass)
            x_new = x + v * dt + 0.5 * a * dt * dt
            a_new = acceleration(x_new, spring_constant, mass)
            positions[i + 1] = x_new
            velocities[i + 1] = v + 0.5 * (a + a_new) * dt

    time = np.arange(n_steps + 1) * dt
    energy = 0.5 * mass * velocities ** 2 + 0.5 * spring_constant * positions ** 2
    return time, positions, velocities, energy


def write_run_csv(output_path, time, positions, velocities, energy) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["time", "x", "v", "energy"])
        for row in zip(time, positions, velocities, energy):
            writer.writerow([f"{value:.10g}" for value in row])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one harmonic-oscillator simulation and write a CSV trajectory.",
    )
    parser.add_argument("--run-id", default="run", help="identifier for this run")
    parser.add_argument("--mass", type=float, default=1.0, help="oscillator mass m")
    parser.add_argument("--spring-constant", type=float, default=1.0, help="spring constant k")
    parser.add_argument("--x0", type=float, default=1.0, help="initial position")
    parser.add_argument("--v0", type=float, default=0.0, help="initial velocity")
    parser.add_argument("--dt", type=float, default=0.01, help="time step")
    parser.add_argument("--n-steps", type=int, default=2000, help="number of integration steps")
    parser.add_argument("--solver", choices=SOLVERS, default="verlet", help="time integrator")
    parser.add_argument("--output", default="run.csv", help="output CSV path")
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    time, positions, velocities, energy = integrate(
        args.mass, args.spring_constant, args.x0, args.v0, args.dt, args.n_steps, args.solver
    )
    write_run_csv(args.output, time, positions, velocities, energy)
    print(f"[{args.run_id}] wrote {len(time)} rows to {args.output}")


if __name__ == "__main__":
    main()

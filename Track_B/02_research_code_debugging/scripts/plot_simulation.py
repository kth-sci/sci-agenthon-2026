"""Plot the harmonic-oscillator simulation against its analytical reference."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.oscillator import HarmonicOscillator
from src.integrators import integrate
from src.diagnostics import total_energy, energy_drift


def main() -> None:
    osc = HarmonicOscillator(mass=1.0, spring_constant=1.0)
    x0, v0 = 1.0, 0.0
    n_periods = 2
    steps_per_period = 1000
    dt = osc.period / steps_per_period
    n_steps = n_periods * steps_per_period

    positions, velocities = integrate(x0, v0, osc.acceleration, dt, n_steps)
    t = np.arange(n_steps + 1) * dt
    analytical = osc.analytical_position(t, x0, v0)

    energies = total_energy(positions, velocities, osc.mass, osc.spring_constant)
    e0 = energies[0]
    relative_energy_error = np.abs(energies - e0) / np.abs(e0)
    drift = energy_drift(energies)

    output_dir = Path(__file__).resolve().parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "oscillator_diagnostics.png"

    fig, axes = plt.subplots(3, 1, figsize=(8, 9), sharex=True)

    axes[0].plot(t, positions, label="numerical", color="C0")
    axes[0].plot(t, analytical, label="analytical", color="C1", linestyle="--")
    axes[0].set_ylabel("x(t)")
    axes[0].set_ylim(-1.5, 1.5)
    axes[0].set_title("Position comparison, zoomed view")
    axes[0].legend(loc="best")
    axes[0].grid(True, alpha=0.3)

    axes[1].semilogy(t, np.abs(positions), label="numerical |x(t)|", color="C0")
    axes[1].semilogy(t, np.abs(analytical), label="analytical |x(t)|", color="C1", linestyle="--")
    axes[1].set_ylabel("|x(t)| (log)")
    axes[1].set_title("Position magnitude (log scale)")
    axes[1].legend(loc="best")
    axes[1].grid(True, which="both", alpha=0.3)

    axes[2].semilogy(t[1:], relative_energy_error[1:], color="C2")
    axes[2].set_xlabel("time")
    axes[2].set_ylabel("|E(t) - E0| / |E0| (log)")
    axes[2].set_title("Relative energy error")
    axes[2].grid(True, which="both", alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=120)
    plt.close(fig)

    print(f"Saved figure to: {output_path}")
    print(f"Initial position: {x0}")
    print(f"Final numerical position: {positions[-1]:.6e}")
    print(f"Analytical reference   : {analytical[-1]:.6e}")
    print(f"Max relative energy drift: {drift:.6e}")


if __name__ == "__main__":
    main()

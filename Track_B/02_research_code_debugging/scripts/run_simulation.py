"""Run a small undamped harmonic-oscillator simulation and print summary diagnostics."""
import sys
from pathlib import Path

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
    t_final = n_steps * dt

    positions, velocities = integrate(x0, v0, osc.acceleration, dt, n_steps)
    energies = total_energy(positions, velocities, osc.mass, osc.spring_constant)
    drift = energy_drift(energies)

    analytical_final = osc.analytical_position(t_final, x0, v0)

    print(f"Harmonic oscillator: m={osc.mass}, k={osc.spring_constant}")
    print(f"Initial state: x0={x0}, v0={v0}")
    print(f"Integration: {n_periods} periods, {steps_per_period} steps per period")
    print(f"Final numerical position: {positions[-1]:.6e}")
    print(f"Analytical reference   : {analytical_final:.6e}")
    print(f"Max relative energy drift over the run: {drift:.6e}")
    print(
        "Use the tests and the diagnostic plot to decide whether this numerical "
        "behaviour is acceptable."
    )


if __name__ == "__main__":
    main()

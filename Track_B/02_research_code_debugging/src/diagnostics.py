"""Diagnostics for harmonic-oscillator runs."""
import numpy as np


def total_energy(positions, velocities, mass: float, spring_constant: float) -> np.ndarray:
    positions = np.asarray(positions, dtype=float)
    velocities = np.asarray(velocities, dtype=float)
    kinetic = 0.5 * mass * velocities ** 2
    potential = 0.5 * spring_constant * positions ** 2
    return kinetic + potential


def energy_drift(energies) -> float:
    energies = np.asarray(energies, dtype=float)
    initial = energies[0]
    if initial == 0.0:
        raise ValueError(
            "relative energy drift is undefined for zero initial energy"
        )
    return float(np.max(np.abs(energies - initial) / np.abs(initial)))

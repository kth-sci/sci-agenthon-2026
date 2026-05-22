"""Undamped 1D harmonic oscillator: m x'' = -k x."""
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class HarmonicOscillator:
    mass: float
    spring_constant: float

    @property
    def angular_frequency(self) -> float:
        return float(np.sqrt(self.spring_constant / self.mass))

    @property
    def period(self) -> float:
        return float(2.0 * np.pi / self.angular_frequency)

    def acceleration(self, position):
        return self.spring_constant * position / self.mass

    def analytical_position(self, t, x0, v0):
        omega = self.angular_frequency
        return x0 * np.cos(omega * t) + (v0 / omega) * np.sin(omega * t)

    def analytical_velocity(self, t, x0, v0):
        omega = self.angular_frequency
        return -x0 * omega * np.sin(omega * t) + v0 * np.cos(omega * t)

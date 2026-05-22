"""End-to-end behavioural tests covering oscillator + integrator together."""
import numpy as np
import pytest

from src.oscillator import HarmonicOscillator
from src.integrators import integrate


def test_motion_is_bounded():
    osc = HarmonicOscillator(mass=1.0, spring_constant=1.0)
    x0, v0 = 1.0, 0.0
    n_periods = 2
    steps_per_period = 1000
    dt = osc.period / steps_per_period
    n_steps = n_periods * steps_per_period
    positions, _ = integrate(x0, v0, osc.acceleration, dt, n_steps)
    assert np.max(np.abs(positions)) < 2.0


def test_position_returns_near_start_after_one_period():
    osc = HarmonicOscillator(mass=1.0, spring_constant=1.0)
    x0, v0 = 1.0, 0.0
    steps_per_period = 1000
    dt = osc.period / steps_per_period
    positions, _ = integrate(x0, v0, osc.acceleration, dt, steps_per_period)
    assert positions[-1] == pytest.approx(x0, abs=0.1)


def test_numerical_matches_analytical_at_half_period():
    osc = HarmonicOscillator(mass=1.0, spring_constant=1.0)
    x0, v0 = 1.0, 0.0
    half_period = osc.period / 2.0
    n_steps = 500
    dt = half_period / n_steps
    positions, _ = integrate(x0, v0, osc.acceleration, dt, n_steps)
    analytical = osc.analytical_position(half_period, x0, v0)
    assert analytical == pytest.approx(-1.0)
    assert positions[-1] == pytest.approx(-1.0, abs=0.1)

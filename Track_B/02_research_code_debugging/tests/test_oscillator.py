import math

import pytest

from src.oscillator import HarmonicOscillator


def test_angular_frequency():
    osc = HarmonicOscillator(mass=4.0, spring_constant=9.0)
    assert osc.angular_frequency == pytest.approx(1.5)


def test_period():
    osc = HarmonicOscillator(mass=1.0, spring_constant=1.0)
    assert osc.period == pytest.approx(2.0 * math.pi)


def test_acceleration_is_restoring_force():
    osc = HarmonicOscillator(mass=1.0, spring_constant=4.0)
    assert osc.acceleration(1.0) == pytest.approx(-4.0)
    assert osc.acceleration(-2.0) == pytest.approx(8.0)


def test_analytical_position_at_t0():
    osc = HarmonicOscillator(mass=1.0, spring_constant=1.0)
    assert osc.analytical_position(0.0, x0=2.0, v0=0.0) == pytest.approx(2.0)


def test_analytical_velocity_at_t0():
    osc = HarmonicOscillator(mass=1.0, spring_constant=1.0)
    assert osc.analytical_velocity(0.0, x0=0.0, v0=3.0) == pytest.approx(3.0)

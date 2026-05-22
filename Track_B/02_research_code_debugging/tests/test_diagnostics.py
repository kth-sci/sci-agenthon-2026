import numpy as np
import pytest

from src.diagnostics import total_energy, energy_drift


def test_total_energy_at_rest_at_origin():
    e = total_energy([0.0], [0.0], mass=1.0, spring_constant=1.0)
    assert e[0] == pytest.approx(0.0)


def test_total_energy_max_displacement():
    e = total_energy([1.0], [0.0], mass=1.0, spring_constant=4.0)
    assert e[0] == pytest.approx(2.0)


def test_total_energy_max_velocity():
    e = total_energy([0.0], [3.0], mass=2.0, spring_constant=1.0)
    assert e[0] == pytest.approx(9.0)


def test_energy_drift_constant():
    assert energy_drift(np.array([1.0, 1.0, 1.0, 1.0])) == pytest.approx(0.0)


def test_energy_drift_relative():
    assert energy_drift(np.array([2.0, 2.0, 2.2, 2.0])) == pytest.approx(0.1)


def test_energy_drift_raises_for_zero_initial_energy():
    with pytest.raises(ValueError, match="zero initial energy"):
        energy_drift([0.0, 0.0, 0.0])

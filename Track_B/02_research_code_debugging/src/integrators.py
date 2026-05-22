"""Time integrators for second-order ODEs of the form x'' = a(x)."""
from typing import Callable, Tuple

import numpy as np


def euler_step(
    position: float,
    velocity: float,
    acceleration_fn: Callable[[float], float],
    dt: float,
) -> Tuple[float, float]:
    a = acceleration_fn(position)
    new_position = position + velocity * dt
    new_velocity = velocity + a * dt
    return new_position, new_velocity


def integrate(
    position0: float,
    velocity0: float,
    acceleration_fn: Callable[[float], float],
    dt: float,
    n_steps: int,
) -> Tuple[np.ndarray, np.ndarray]:
    positions = np.empty(n_steps + 1)
    velocities = np.empty(n_steps + 1)
    positions[0] = position0
    velocities[0] = velocity0
    for i in range(n_steps):
        positions[i + 1], velocities[i + 1] = euler_step(
            positions[i], velocities[i], acceleration_fn, dt
        )
    return positions, velocities

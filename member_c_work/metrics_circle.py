"""Geometric metrics for the true-circle study (Part C2)."""
from __future__ import annotations

import numpy as np


def _points(x: np.ndarray, name: str = "points") -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or x.shape[1] != 2 or x.shape[0] == 0:
        raise ValueError(f"{name} must be a non-empty array with shape (m, 2)")
    if not np.all(np.isfinite(x)):
        raise ValueError(f"{name} must contain only finite values")
    return x


def _circle(c: np.ndarray, radius: float) -> tuple[np.ndarray, float]:
    c = np.asarray(c, dtype=float)
    if c.shape != (2,) or not np.all(np.isfinite(c)):
        raise ValueError("c must be a finite vector of shape (2,)")
    radius = float(radius)
    if not np.isfinite(radius) or radius <= 0:
        raise ValueError("radius must be finite and positive")
    return c, radius


def circle_grid(c=(0.0, 0.0), radius: float = 1.0, length: int = 720) -> np.ndarray:
    c, radius = _circle(c, radius)
    if not isinstance(length, (int, np.integer)) or length < 3:
        raise ValueError("length must be an integer at least 3")
    theta = 2 * np.pi * np.arange(length) / length
    return c + radius * np.column_stack((np.cos(theta), np.sin(theta)))


def radial_error(outputs: np.ndarray, c=(0.0, 0.0), radius: float = 1.0) -> float:
    outputs = _points(outputs, "outputs")
    c, radius = _circle(c, radius)
    return float(np.mean((np.linalg.norm(outputs - c, axis=1) - radius) ** 2))


def coverage_error(outputs: np.ndarray, c=(0.0, 0.0), radius: float = 1.0,
                   length: int = 720, chunk_size: int = 2048) -> float:
    outputs = _points(outputs, "outputs")
    grid = circle_grid(c, radius, length)
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    total = 0.0
    for start in range(0, len(grid), chunk_size):
        diff = grid[start:start + chunk_size, None, :] - outputs[None, :, :]
        total += np.min(np.sum(diff * diff, axis=2), axis=1).sum()
    return float(total / len(grid))


def clean_test_coverage_error(clean_test_points: np.ndarray, c=(0.0, 0.0),
                              radius: float = 1.0, length: int = 720) -> float:
    """Finite-sample spacing baseline; it is not a universal lower bound."""
    return coverage_error(clean_test_points, c, radius, length)


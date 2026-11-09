"""Bidirectional dense-grid metrics for the Option-3 ellipse study."""
from __future__ import annotations

import numpy as np
from .metrics_circle import _points


def ellipse_grid(c=(0.0, 0.0), b: float = 1.0, length: int = 4096) -> np.ndarray:
    c = np.asarray(c, dtype=float)
    if c.shape != (2,) or not np.all(np.isfinite(c)):
        raise ValueError("c must be a finite vector of shape (2,)")
    b = float(b)
    if not np.isfinite(b) or b <= 0:
        raise ValueError("b must be finite and positive")
    if not isinstance(length, (int, np.integer)) or length < 3:
        raise ValueError("length must be an integer at least 3")
    theta = 2 * np.pi * np.arange(length) / length
    return c + np.column_stack((np.cos(theta), b * np.sin(theta)))


def _mean_nearest_squared(source: np.ndarray, target: np.ndarray,
                          chunk_size: int = 1024) -> float:
    source, target = _points(source, "source"), _points(target, "target")
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    total = 0.0
    for start in range(0, len(source), chunk_size):
        d = source[start:start + chunk_size, None, :] - target[None, :, :]
        total += np.min(np.sum(d * d, axis=2), axis=1).sum()
    return float(total / len(source))


def bidirectional_ellipse_errors(outputs: np.ndarray, c=(0.0, 0.0), b: float = 1.0,
                                 grid_length: int = 4096,
                                 chunk_size: int = 1024) -> dict[str, float]:
    outputs = _points(outputs, "outputs")
    grid = ellipse_grid(c, b, grid_length)
    return {
        "output_to_ellipse": _mean_nearest_squared(outputs, grid, chunk_size),
        "ellipse_to_output": _mean_nearest_squared(grid, outputs, chunk_size),
    }


def denoising_mse(outputs: np.ndarray, clean_points: np.ndarray) -> float:
    outputs, clean_points = _points(outputs, "outputs"), _points(clean_points, "clean_points")
    if outputs.shape != clean_points.shape:
        raise ValueError("outputs and clean_points must have the same shape")
    return float(np.mean(np.sum((outputs - clean_points) ** 2, axis=1)))


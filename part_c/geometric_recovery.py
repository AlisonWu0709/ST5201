"""Part C2 geometric recovery metrics for one simulation repetition."""

from __future__ import annotations

import numpy as np


COVERAGE_GRID_SIZE = 720


def geometric_recovery_metrics(Z, X_test_clean, c_true, R_true):
    """Compute C2 radial and coverage errors for one method and repetition.

    Parameters
    ----------
    Z : array-like, shape (m, 2)
        Denoised outputs from one method for the repetition's common test set.
    X_test_clean : array-like, shape (m, 2)
        Paired clean test points. Used only for the requested coverage reference.
    c_true : array-like, shape (2,)
        True circle center.
    R_true : float
        True circle radius, which must be positive.

    Returns
    -------
    dict
        Repetition-level radial error, output coverage error, and clean-test
        coverage reference. The coverage calculation uses exactly 720 equally
        spaced points on the true circle, as specified in the assignment.
    """
    Z = np.asarray(Z, dtype=float)
    X_test_clean = np.asarray(X_test_clean, dtype=float)
    c_true = np.asarray(c_true, dtype=float)
    if Z.ndim != 2 or Z.shape[1] != 2 or len(Z) == 0:
        raise ValueError("Z must have shape (m >= 1, 2)")
    if X_test_clean.shape != Z.shape:
        raise ValueError("X_test_clean must have the same (m, 2) shape as Z")
    if c_true.shape != (2,):
        raise ValueError("c_true must have shape (2,)")
    if not np.all(np.isfinite(Z)) or not np.all(np.isfinite(X_test_clean)):
        raise ValueError("Z and X_test_clean must be finite")
    if not np.all(np.isfinite(c_true)):
        raise ValueError("c_true must be finite")
    if np.ndim(R_true) != 0 or not np.isfinite(R_true) or R_true <= 0:
        raise ValueError("R_true must be finite and positive")

    R_true = float(R_true)
    radial_error = float(np.mean((np.linalg.norm(Z - c_true, axis=1) - R_true) ** 2))

    # Each grid point asks how close the available outputs come to covering it.
    theta = 2.0 * np.pi * np.arange(COVERAGE_GRID_SIZE) / COVERAGE_GRID_SIZE
    circle_grid = c_true + R_true * np.column_stack((np.cos(theta), np.sin(theta)))

    def mean_squared_distance_to_outputs(points):
        # Chunk the grid dimension to keep memory use modest for larger batches.
        nearest_sq = np.empty(len(circle_grid), dtype=float)
        chunk_size = 128
        for start in range(0, len(circle_grid), chunk_size):
            grid_chunk = circle_grid[start : start + chunk_size]
            delta = grid_chunk[:, None, :] - points[None, :, :]
            distances_sq = np.einsum("gmd,gmd->gm", delta, delta)
            nearest_sq[start : start + len(grid_chunk)] = distances_sq.min(axis=1)
        return float(nearest_sq.mean())

    return {
        "radial_error": radial_error,
        "coverage_error": mean_squared_distance_to_outputs(Z),
        "clean_test_coverage_error": mean_squared_distance_to_outputs(X_test_clean),
    }

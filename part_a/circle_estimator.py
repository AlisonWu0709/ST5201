"""Moment-based circle parameter estimation for Part A."""

from __future__ import annotations

import numpy as np


def estimate_circle(Y_train, sigma):
    """Estimate the center and radius from noisy training observations only.

    Parameters
    ----------
    Y_train : array-like, shape (n, 2)
        Noisy training observations, with n >= 2.
    sigma : float
        Known noise standard deviation per coordinate; must be nonnegative.

    Returns
    -------
    c_hat : ndarray, shape (2,)
        Estimated circle center.
    R_hat : float
        Square root of max(Q_hat, 0).
    Q_hat : float
        Untruncated estimate of the squared radius. Retain negative values
        when reporting the frequency of Q_hat < 0 in Part C.
    """
    Y_train = np.asarray(Y_train, dtype=float)
    if Y_train.ndim != 2 or Y_train.shape[1] != 2 or len(Y_train) < 2:
        raise ValueError("Y_train must have shape (n >= 2, 2)")
    if not np.all(np.isfinite(Y_train)):
        raise ValueError("Y_train must be finite")
    if np.ndim(sigma) != 0 or not np.isfinite(sigma) or sigma < 0:
        raise ValueError("sigma must be finite and nonnegative")

    c_hat = Y_train.mean(axis=0)
    centered = Y_train - c_hat
    second_moment = np.sum(centered * centered) / (len(Y_train) - 1)
    Q_hat = float(second_moment - 2.0 * float(sigma) ** 2)
    R_hat = float(np.sqrt(max(Q_hat, 0.0)))
    return c_hat, R_hat, Q_hat

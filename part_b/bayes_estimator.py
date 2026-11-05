"""Bayes posterior-mean estimators for the noisy circle model."""

from __future__ import annotations

import numpy as np


def bayes_posterior_mean(Y, c, R, sigma, K=512):
    """Numerically approximate E[X | Y] using K equally spaced angles.

    Parameters use Y.shape == (n, 2), c.shape == (2,); a single observation
    of shape (2,) is also accepted and returns a vector of shape (2,).
    """
    Y = np.asarray(Y, dtype=float)
    c = np.asarray(c, dtype=float)
    if Y.ndim not in (1, 2) or Y.shape[-1] != 2:
        raise ValueError("Y must have shape (n, 2) or (2,)")
    if c.shape != (2,):
        raise ValueError("c must have shape (2,)")
    if not np.all(np.isfinite(Y)) or not np.all(np.isfinite(c)):
        raise ValueError("Y and c must be finite")
    if not np.isfinite(R) or R < 0:
        raise ValueError("R must be finite and nonnegative")
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be finite and positive")
    if int(K) != K or K < 1:
        raise ValueError("K must be a positive integer")

    was_vector = Y.ndim == 1
    Y2 = Y[None, :] if was_vector else Y
    theta = 2.0 * np.pi * np.arange(int(K)) / int(K)
    circle = c + float(R) * np.column_stack((np.cos(theta), np.sin(theta)))
    # Process observations in batches; subtracting each row maximum stabilizes
    # exponentiation without changing the normalized posterior weights.
    result = np.empty_like(Y2)
    chunk_size = max(1, min(len(Y2), 4096))
    for start in range(0, len(Y2), chunk_size):
        y = Y2[start : start + chunk_size]
        delta = y[:, None, :] - circle[None, :, :]
        log_w = -np.einsum("nkd,nkd->nk", delta, delta) / (2.0 * sigma**2)
        log_w -= np.max(log_w, axis=1, keepdims=True)
        weights = np.exp(log_w)
        weights /= weights.sum(axis=1, keepdims=True)
        result[start : start + len(y)] = weights @ circle
    return result[0] if was_vector else result


def oracle_bayes(Y, c_true, R_true, sigma, K=512):
    """Oracle rule using the true center and radius."""
    return bayes_posterior_mean(Y, c_true, R_true, sigma, K)


def plugin_bayes(Y, c_hat, R_hat, sigma, K=512):
    """Plug-in rule; c_hat and R_hat are supplied by the caller (e.g. Part A)."""
    return bayes_posterior_mean(Y, c_hat, R_hat, sigma, K)

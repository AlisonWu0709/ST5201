"""Oracle and fitted circle projection estimators for Part B1."""

from __future__ import annotations

import numpy as np


def project_circle(Y, c, R):
    """Project observations onto the circle with center c and radius R.

    Parameters use Y.shape == (n, 2), c.shape == (2,); a single observation
    of shape (2,) is also accepted and returns a vector of shape (2,).

    If R == 0, every output equals c. If Y equals c and R > 0, return
    c + R * [1, 0], a fixed point on the circle. All noncentral observations
    retain their observed direction relative to c, including nearby points.
    """
    Y = np.asarray(Y, dtype=float)
    c = np.asarray(c, dtype=float)
    if Y.ndim not in (1, 2) or Y.shape[-1] != 2:
        raise ValueError("Y must have shape (n, 2) or (2,)")
    if c.shape != (2,):
        raise ValueError("c must have shape (2,)")
    if not np.all(np.isfinite(Y)) or not np.all(np.isfinite(c)):
        raise ValueError("Y and c must be finite")
    if np.ndim(R) != 0 or not np.isfinite(R) or R < 0:
        raise ValueError("R must be finite and nonnegative")

    was_vector = Y.ndim == 1
    Y2 = Y[None, :] if was_vector else Y
    if R == 0:
        result = np.broadcast_to(c, Y2.shape).copy()
        return result[0] if was_vector else result

    offset = Y2 - c
    # hypot avoids squaring very small or large coordinates when normalizing.
    distance = np.hypot(offset[:, 0], offset[:, 1])
    direction = np.zeros_like(Y2)
    noncentral = distance > 0.0
    direction[noncentral] = offset[noncentral] / distance[noncentral, None]
    direction[~noncentral, 0] = 1.0
    result = c + float(R) * direction
    return result[0] if was_vector else result


def oracle_projection(Y, c_true, R_true):
    """Oracle rule using the true center and radius."""
    return project_circle(Y, c_true, R_true)


def plugin_projection(Y, c_hat, R_hat):
    """Fitted projection using center and radius estimates supplied by Part A."""
    return project_circle(Y, c_hat, R_hat)

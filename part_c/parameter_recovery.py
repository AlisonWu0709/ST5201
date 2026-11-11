"""Part C1 parameter recovery metrics for one simulation repetition."""

import numpy as np


def parameter_recovery_metrics(c_hat, R_hat, Q_hat, c_true, R_true):
    """Score an existing circle fit against the simulation truth.

    Across repetitions, the means of the four fields give center MSE,
    radius bias, radius MSE, and the fraction of negative raw Q estimates.
    """
    center_error = np.subtract(c_hat, c_true)
    radius_error = float(R_hat - R_true)
    return {
        "center_sq_error": float(center_error @ center_error),
        "radius_error": radius_error,
        "radius_sq_error": radius_error**2,
        "q_negative": int(Q_hat < 0.0),
    }

"""Part C1 parameter recovery metrics for one simulation repetition."""

import numpy as np

from part_a.circle_estimator import estimate_circle


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


def main():
    """Check one setting before adding the metrics to the common simulation."""
    n = 100
    sigma = 0.15
    c_true = np.zeros(2)
    R_true = 1.0
    rng = np.random.default_rng(5201)

    theta = rng.uniform(0.0, 2.0 * np.pi, size=n)
    X_train = c_true + R_true * np.column_stack((np.cos(theta), np.sin(theta)))
    Y_train = X_train + rng.normal(0.0, sigma, size=X_train.shape)
    c_hat, R_hat, Q_hat = estimate_circle(Y_train, sigma)
    metrics = parameter_recovery_metrics(c_hat, R_hat, Q_hat, c_true, R_true)

    print(f"C1 check: n={n}, sigma={sigma}, seed=5201")
    print(f"c_hat = ({c_hat[0]:.8f}, {c_hat[1]:.8f})")
    print(f"R_hat = {R_hat:.8f}")
    print(f"Q_hat = {Q_hat:.8f}")
    for name, value in metrics.items():
        print(f"{name} = {value:.8g}")


if __name__ == "__main__":
    main()

"""Independent training/test generators for circle and ellipse experiments."""
from __future__ import annotations

import numpy as np


def generate_ellipse_sample(rng: np.random.Generator, size: int, b: float = 1.0,
                            sigma: float = 0.15, c=(0.0, 0.0)) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not isinstance(rng, np.random.Generator):
        raise TypeError("rng must be numpy.random.Generator")
    if not isinstance(size, (int, np.integer)) or size <= 0:
        raise ValueError("size must be a positive integer")
    c = np.asarray(c, dtype=float)
    if c.shape != (2,) or not np.all(np.isfinite(c)):
        raise ValueError("c must be a finite vector of shape (2,)")
    b, sigma = float(b), float(sigma)
    if not np.isfinite(b) or b <= 0 or not np.isfinite(sigma) or sigma < 0:
        raise ValueError("b must be positive and sigma must be nonnegative")
    theta = rng.uniform(0.0, 2 * np.pi, size=size)
    clean = c + np.column_stack((np.cos(theta), b * np.sin(theta)))
    noisy = clean + rng.normal(0.0, sigma, size=(size, 2))
    return clean, noisy, theta


def generate_train_test(rng: np.random.Generator, n: int, m: int, b: float = 1.0,
                        sigma: float = 0.15, c=(0.0, 0.0)) -> dict[str, np.ndarray]:
    train_clean, train_noisy, train_theta = generate_ellipse_sample(rng, n, b, sigma, c)
    test_clean, test_noisy, test_theta = generate_ellipse_sample(rng, m, b, sigma, c)
    return {"train_clean": train_clean, "train_noisy": train_noisy,
            "train_theta": train_theta, "test_clean": test_clean,
            "test_noisy": test_noisy, "test_theta": test_theta}

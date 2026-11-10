"""Assignment-settings wrapper around the supplied weighted MF implementation."""

from __future__ import annotations

import math
from pathlib import Path
import sys

import numpy as np

# mf_weighted.py remains the instructor-provided implementation at project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from mf_weighted import manifold_fit_weighted  # noqa: E402


def assignment_radii(n, sigma):
    """Return the B3 radii, using natural log in log(1/sigma)."""
    if n < 2 or not (0 < sigma < 1):
        raise ValueError("require n >= 2 and 0 < sigma < 1")
    denominator = math.log10(n)
    r0 = 5.0 * sigma / denominator
    r1 = r0
    r2 = (10.0* sigma* math.sqrt(math.log(1.0 / sigma))/ denominator)
    return r0, r1, r2


def manifold_fitting(Y_train, Y_query, sigma):
    """Fit query points using independent training observations.

    Returns (predictions, diagnostics); diagnostics is the MFDiagnostics object
    from mf_weighted.py and includes each fallback count and aggregate rate.
    """
    train = np.asarray(Y_train, dtype=float)
    query = np.asarray(Y_query, dtype=float)
    if train.ndim != 2 or train.shape[1] != 2 or len(train) < 2:
        raise ValueError("Y_train must have shape (n >= 2, 2)")
    if query.ndim != 2 or query.shape[1] != 2:
        raise ValueError("Y_query must have shape (m, 2)")
    if not np.all(np.isfinite(train)) or not np.all(np.isfinite(query)):
        raise ValueError("training observations and queries must be finite")
    radii = assignment_radii(len(train), sigma)
    # The reference supports explicit radii, k, and returns its diagnostics.
    return manifold_fit_weighted(
        train, query, sigma, k=3, r0=radii[0], r1=radii[1], r2=radii[2]
    )

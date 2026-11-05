from dataclasses import dataclass
import math
import numpy as np


@dataclass
class MFDiagnostics:
    n_query: int
    empty_sphere: int = 0
    zero_direction: int = 0
    empty_cylinder: int = 0

    @property
    def any_fallback(self):
        return self.empty_sphere + self.zero_direction + self.empty_cylinder

    def as_dict(self):
        n = max(self.n_query, 1)
        return {
            "n_query": self.n_query,
            "empty_sphere": self.empty_sphere,
            "zero_direction": self.zero_direction,
            "empty_cylinder": self.empty_cylinder,
            "fallback_total": self.any_fallback,
            "fallback_rate": self.any_fallback / n,
        }


def default_radii(n, sigma):
    if n < 2 or not (0 < sigma < 1):
        raise ValueError("require n >= 2 and 0 < sigma < 1")
    lg = math.log10(n)
    r0 = 5.0 * sigma / lg
    r1 = r0
    r2 = 10.0 * sigma * math.sqrt(math.log(1.0 / sigma)) / lg
    return r0, r1, r2


def _sphere_weights(diff, r0, k):
    d2 = np.sum(diff * diff, axis=1)
    w = np.zeros(len(diff))
    mask = d2 <= r0 * r0
    w[mask] = np.maximum(1.0 - d2[mask] / (r0 * r0), 0.0) ** k
    return w


def _cylinder_weights(diff, direction, r1, r2, k):
    u = diff @ direction
    abs_u = np.abs(u)
    v = diff - u[:, None] * direction[None, :]
    v2 = np.sum(v * v, axis=1)

    wu = np.zeros(len(diff))
    inner = abs_u <= r2 / 2.0
    taper = (abs_u > r2 / 2.0) & (abs_u < r2)
    wu[inner] = 1.0
    s = (2.0 * abs_u[taper] - r2) / r2
    wu[taper] = np.maximum(1.0 - s * s, 0.0) ** k

    wv = np.zeros(len(diff))
    mask = v2 <= r1 * r1
    wv[mask] = np.maximum(1.0 - v2[mask] / (r1 * r1), 0.0) ** k
    return wu * wv


def manifold_fit_weighted(train, query, sigma, k=3, r0=None, r1=None, r2=None, tol=1e-12):
    train = np.asarray(train, dtype=float)
    query = np.asarray(query, dtype=float)
    was_vector = query.ndim == 1
    if was_vector:
        query = query[None, :]

    if train.ndim != 2 or query.ndim != 2 or train.shape[1] != query.shape[1]:
        raise ValueError("train and query must have the same ambient dimension")
    if int(k) != k or k <= 2:
        raise ValueError("k must be an integer greater than 2")
    k = int(k)

    dr0, dr1, dr2 = default_radii(train.shape[0], sigma)
    r0 = dr0 if r0 is None else float(r0)
    r1 = dr1 if r1 is None else float(r1)
    r2 = dr2 if r2 is None else float(r2)

    out = np.empty_like(query)
    diag = MFDiagnostics(len(query))

    for j, z in enumerate(query):
        diff = train - z
        alpha = _sphere_weights(diff, r0, k)
        sa = alpha.sum()
        if not np.isfinite(sa) or sa <= tol:
            out[j] = z
            diag.empty_sphere += 1
            continue

        F = (alpha[:, None] * train).sum(axis=0) / sa
        direction = F - z
        norm_direction = np.linalg.norm(direction)
        if not np.isfinite(norm_direction) or norm_direction <= tol:
            out[j] = F
            diag.zero_direction += 1
            continue

        direction /= norm_direction
        beta = _cylinder_weights(diff, direction, r1, r2, k)
        sb = beta.sum()
        if not np.isfinite(sb) or sb <= tol:
            out[j] = F
            diag.empty_cylinder += 1
            continue

        out[j] = (beta[:, None] * train).sum(axis=0) / sb

    return (out[0] if was_vector else out), diag

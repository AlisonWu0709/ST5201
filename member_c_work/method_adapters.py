"""Small, explicit contract for algorithms supplied by members A/B."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
import numpy as np

ArrayMethod = Callable[[np.ndarray, np.ndarray, float], tuple[np.ndarray, dict]]


@dataclass(frozen=True)
class MethodAdapter:
    name: str
    apply: ArrayMethod

    def __call__(self, train_noisy, test_noisy, sigma):
        for points in (train_noisy, test_noisy):
            a = np.asarray(points, float)
            if a.ndim != 2 or a.shape[1] != 2 or not len(a) or not np.isfinite(a).all():
                raise ValueError('inputs must be finite nonempty (n,2) arrays')
        output, diagnostics = self.apply(np.asarray(train_noisy, float),
                                         np.asarray(test_noisy, float), float(sigma))
        output = np.asarray(output, float)
        if output.shape != np.asarray(test_noisy).shape or not np.all(np.isfinite(output)):
            raise ValueError(f"{self.name} returned invalid output")
        if not isinstance(diagnostics, dict):
            raise TypeError(f"{self.name} diagnostics must be a dict")
        return output, diagnostics


def raw_adapter() -> MethodAdapter:
    return MethodAdapter("raw", lambda train, test, sigma: (test.copy(), {}))


def mf_adapter() -> MethodAdapter:
    from part_b.manifold_fitting import manifold_fitting
    def apply(train, test, sigma):
        output, diagnostics = manifold_fitting(train, test, sigma)
        return output, diagnostics.as_dict()
    return MethodAdapter("mf", apply)


def all_adapters(part='C'):
    """Fitted rules see only noisy training/query data and known sigma."""
    from part_a.circle_estimator import estimate_circle
    from part_b.projection import oracle_projection, plugin_projection
    from part_b.bayes_estimator import oracle_bayes, plugin_bayes

    def fitted(rule):
        def apply(train, test, sigma):
            c, r, q = estimate_circle(train, sigma)
            output = rule(test, c, r, sigma) if rule is plugin_bayes else rule(test, c, r)
            return output, {'c_hat': c.tolist(), 'R_hat': r, 'Q_hat': q}
        return apply

    methods = [raw_adapter(),
        MethodAdapter('oracle_projection', lambda train, test, sigma: (oracle_projection(test, (0, 0), 1), {})),
        MethodAdapter('fitted_projection', fitted(plugin_projection)),
        MethodAdapter('oracle_posterior_mean', lambda train, test, sigma: (oracle_bayes(test, (0, 0), 1, sigma), {})),
        MethodAdapter('plugin_posterior_mean', fitted(plugin_bayes)), mf_adapter()]
    if part not in ('C', 'D'):
        raise ValueError('part must be C or D')
    return [m for m in methods if part == 'C' or not m.name.startswith('oracle_')]


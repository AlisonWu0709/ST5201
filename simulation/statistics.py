"""Monte Carlo summaries computed from repetition-level observations."""
from __future__ import annotations

import numpy as np
import pandas as pd


def monte_carlo_summary(values) -> dict[str, float | int]:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1:
        raise ValueError("values must be one-dimensional")
    x = x[np.isfinite(x)]
    if len(x) < 2:
        return {"mean": float(np.mean(x)) if len(x) else np.nan,
                "sample_sd": np.nan, "mcse": np.nan, "repetitions": int(len(x))}
    sd = float(np.std(x, ddof=1))
    return {"mean": float(np.mean(x)), "sample_sd": sd,
            "mcse": sd / np.sqrt(len(x)), "repetitions": int(len(x))}


def grouped_summary(data: pd.DataFrame, metrics: list[str],
                    group_by=("n", "sigma", "method")) -> pd.DataFrame:
    missing = set(group_by).union(metrics) - set(data.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    rows = []
    for key, group in data.groupby(list(group_by), dropna=False, sort=True):
        key = key if isinstance(key, tuple) else (key,)
        base = dict(zip(group_by, key))
        for metric in metrics:
            rows.append(base | {"metric": metric} | monte_carlo_summary(group[metric]))
    return pd.DataFrame(rows)

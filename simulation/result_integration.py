"""Schema validation and summaries for repetition-level results from all members."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

METHODS = ("raw", "oracle_projection", "fitted_projection", "oracle_posterior_mean",
           "plugin_posterior_mean", "mf")
KEYS = ["dataset_id", "repetition_id", "n", "sigma", "method"]
METRICS = ["centre_squared_error", "radius_error", "radius_squared_error", "negative_Q",
           "denoising_mse", "radial_error", "coverage_error", "mf_fallback_rate"]
REQUIRED = KEYS + METRICS


def read_results(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".csv":
        data = pd.read_csv(path)
    elif path.suffix.lower() in {".parquet", ".pq"}:
        data = pd.read_parquet(path)
    else:
        raise ValueError("results must be CSV or Parquet")
    return validate_results(data)


def validate_results(data: pd.DataFrame, expected_methods=METHODS,
                     expected_repetitions: int | None = 50) -> pd.DataFrame:
    data = data.copy()
    missing = set(REQUIRED) - set(data.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    if data.empty:
        raise ValueError("results may not be empty")
    if data[KEYS].isna().any().any():
        raise ValueError("identifying columns may not contain missing values")
    for col in ["repetition_id", "n"]:
        numeric = pd.to_numeric(data[col], errors="coerce")
        if numeric.isna().any() or (numeric % 1 != 0).any():
            raise ValueError(f"{col} must contain integers")
        data[col] = numeric.astype(int)
    data["sigma"] = pd.to_numeric(data["sigma"], errors="coerce")
    if not np.isfinite(data["sigma"]).all() or (data["n"] <= 0).any() or (data["sigma"] < 0).any():
        raise ValueError("n must be positive and sigma finite and nonnegative")
    for col in METRICS:
        original = data[col]
        data[col] = pd.to_numeric(original, errors="coerce")
        if (original.notna() & data[col].isna()).any():
            raise ValueError(f"{col} contains illegal values")
        if np.isinf(data[col]).any():
            raise ValueError(f"{col} contains infinite values")
    for col in ('denoising_mse', 'radial_error', 'coverage_error'):
        if data[col].isna().any() or (data[col] < 0).any():
            raise ValueError(f'{col} must be finite and nonnegative')
    for col in ('centre_squared_error', 'radius_squared_error'):
        if (data[col].dropna() < 0).any():
            raise ValueError(f'{col} must be nonnegative')
    if not data['negative_Q'].dropna().isin([0, 1]).all():
        raise ValueError('negative_Q must be Boolean')
    rate = data['mf_fallback_rate'].dropna()
    if ((rate < 0) | (rate > 1)).any():
        raise ValueError('fallback rate outside [0,1]')
    if (data['repetition_id'] < 0).any():
        raise ValueError('negative repetition_id')
    if data.duplicated(KEYS).any():
        raise ValueError("duplicate records found for dataset/repetition/setting/method")

    group = ["repetition_id", "n", "sigma"]
    for setting, block in data.groupby(group, sort=False):
        ids = block["dataset_id"].unique()
        if len(ids) != 1:
            raise ValueError(f"methods do not share one dataset_id at setting {setting}")
        methods = set(block["method"])
        if methods != set(expected_methods):
            raise ValueError(f"methods at {setting}: missing={set(expected_methods)-methods}, "
                             f"unexpected={methods-set(expected_methods)}")
    if expected_repetitions is not None:
        counts = data.groupby(["n", "sigma"])["repetition_id"].nunique()
        bad = counts[counts != expected_repetitions]
        if len(bad):
            raise ValueError(f"expected {expected_repetitions} repetitions; bad settings: {bad.to_dict()}")
    return data


def summarize_results(data: pd.DataFrame) -> pd.DataFrame:
    from .statistics import grouped_summary
    data = validate_results(data, expected_repetitions=None)
    return grouped_summary(data, METRICS)


def summarize_parameter_recovery(data: pd.DataFrame) -> pd.DataFrame:
    """Deduplicate circle estimates that are copied across denoising-method rows."""
    data = validate_results(data, expected_repetitions=None)
    cols = ["dataset_id", "repetition_id", "n", "sigma", "centre_squared_error",
            "radius_error", "radius_squared_error", "negative_Q"]
    unique = data[cols].dropna(subset=cols[-4:], how="all").drop_duplicates()
    if unique.duplicated(["dataset_id", "repetition_id", "n", "sigma"]).any():
        raise ValueError("inconsistent parameter estimates within a dataset")
    from .statistics import grouped_summary
    return grouped_summary(unique, cols[-4:], group_by=("n", "sigma"))


def write_results(data: pd.DataFrame, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(path, index=False)


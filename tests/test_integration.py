import numpy as np
import pandas as pd
import pytest

from member_c_work.result_integration import METHODS, METRICS, validate_results, summarize_parameter_recovery
from member_c_work.visualization import plot_geometric_outputs, plot_metric


def valid_frame(reps=2):
    rows = []
    for r in range(reps):
        for method in METHODS:
            row = {"dataset_id": f"data-{r}", "repetition_id": r, "n": 100,
                   "sigma": .15, "method": method}
            row.update({metric: float(r + 1) for metric in METRICS})
            row["negative_Q"] = 0
            row["mf_fallback_rate"] = 0.0
            rows.append(row)
    return pd.DataFrame(rows)


def test_validation_and_parameter_deduplication():
    data = validate_results(valid_frame(), expected_repetitions=2)
    summary = summarize_parameter_recovery(data)
    centre = summary[summary.metric == "centre_squared_error"].iloc[0]
    assert centre["repetitions"] == 2
    assert centre["mean"] == pytest.approx(1.5)


def test_dataset_mismatch_detected():
    data = valid_frame()
    data.loc[0, "dataset_id"] = "wrong"
    with pytest.raises(ValueError, match="dataset_id"):
        validate_results(data, expected_repetitions=2)


def test_plots_export(tmp_path):
    points = np.column_stack((np.cos(np.linspace(0, 6, 20)), np.sin(np.linspace(0, 6, 20))))
    p1 = tmp_path / "scatter.png"
    fig = plot_geometric_outputs({"demo": points}, output=p1)
    assert p1.exists(); fig.clf()
    summary = pd.DataFrame({"n": [100, 500], "sigma": [.15, .15], "method": ["raw", "raw"],
                            "metric": ["denoising_mse"] * 2, "mean": [.1, .09], "mcse": [.01, .01]})
    p2 = tmp_path / "metric.pdf"
    fig = plot_metric(summary, "denoising_mse", output=p2)
    assert p2.exists(); fig.clf()

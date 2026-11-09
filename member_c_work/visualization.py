"""Report-ready plotting functions; none embeds simulated conclusions."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _save(fig, output):
    if output is not None:
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output, bbox_inches="tight", dpi=200)
    return fig


def plot_geometric_outputs(series: dict[str, np.ndarray], c=(0, 0), radius=1.0,
                           output=None, columns=3):
    if not series:
        raise ValueError("series may not be empty")
    rows = int(np.ceil(len(series) / columns))
    fig, axes = plt.subplots(rows, columns, figsize=(4 * columns, 4 * rows), squeeze=False)
    theta = np.linspace(0, 2 * np.pi, 721)
    circle = np.asarray(c) + radius * np.column_stack((np.cos(theta), np.sin(theta)))
    for ax, (name, points) in zip(axes.flat, series.items()):
        points = np.asarray(points)
        ax.plot(circle[:, 0], circle[:, 1], "k-", lw=1.4, label="True circle")
        ax.scatter(points[:, 0], points[:, 1], s=8, alpha=.55, label=name)
        ax.set(title=name, xlabel="$x_1$", ylabel="$x_2$", aspect="equal")
        ax.legend(fontsize=8)
    for ax in axes.flat[len(series):]:
        ax.set_visible(False)
    fig.tight_layout()
    return _save(fig, output)


def plot_metric(data: pd.DataFrame, metric: str, x: str = "n", facet: str = "sigma",
                output=None):
    required = {x, facet, "method", "metric", "mean", "mcse"}
    if required - set(data.columns):
        raise ValueError(f"missing columns: {sorted(required-set(data.columns))}")
    d = data[data["metric"] == metric]
    levels = sorted(d[facet].dropna().unique())
    if not levels:
        raise ValueError(f"no rows for metric {metric}")
    fig, axes = plt.subplots(1, len(levels), figsize=(5 * len(levels), 4), squeeze=False)
    for ax, level in zip(axes.flat, levels):
        for method, g in d[d[facet] == level].groupby("method"):
            g = g.sort_values(x)
            ax.errorbar(g[x], g["mean"], yerr=g["mcse"], marker="o", capsize=3, label=method)
        ax.set(xlabel=x, ylabel=metric, title=f"{facet} = {level}")
        ax.legend(fontsize=8)
    fig.tight_layout()
    return _save(fig, output)


def plot_ellipse_outputs(outputs: dict[str, np.ndarray], b: float, output=None):
    theta = np.linspace(0, 2 * np.pi, 1000)
    truth = np.column_stack((np.cos(theta), b * np.sin(theta)))
    fig, axes = plt.subplots(1, len(outputs), figsize=(4 * len(outputs), 4), squeeze=False)
    for ax, (name, points) in zip(axes.flat, outputs.items()):
        ax.plot(truth[:, 0], truth[:, 1], "k-", label="True ellipse")
        ax.scatter(points[:, 0], points[:, 1], s=8, alpha=.55, label=name)
        ax.set(title=name, xlabel="$x_1$", ylabel="$x_2$", aspect="equal")
        ax.legend(fontsize=8)
    fig.tight_layout()
    return _save(fig, output)

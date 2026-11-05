"""Representative B2/B3 comparison figure generation."""

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "part_b") not in sys.path:
    sys.path.insert(0, str(ROOT / "part_b"))
from bayes_estimator import oracle_bayes
from manifold_fitting import manifold_fitting


def make_comparison_figure(output_path=None, seed=5201, sigma=0.15, n_train=500, n_query=120):
    """Save a plot from temporary known-parameter debugging data."""
    rng = np.random.default_rng(seed)
    c, radius = np.array([0.0, 0.0]), 1.0
    theta = rng.uniform(0, 2 * np.pi, n_train + n_query)
    clean = c + radius * np.column_stack((np.cos(theta), np.sin(theta)))
    noisy = clean + rng.normal(0, sigma, clean.shape)
    train, query = noisy[:n_train], noisy[n_train:]
    bayes = oracle_bayes(query, c, radius, sigma)
    mf, _ = manifold_fitting(train, query, sigma)
    if output_path is None:
        output_path = ROOT / "results" / "figures" / "b2_b3_debug_comparison.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    circle_t = np.linspace(0, 2 * np.pi, 500)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharex=True, sharey=True)
    panels = [("Noisy queries", query), ("Oracle Bayes posterior mean", bayes), ("MF output", mf)]
    for ax, (title, points) in zip(axes, panels):
        ax.plot(np.cos(circle_t), np.sin(circle_t), color="black", lw=1.4, label="true circle")
        ax.scatter(train[:, 0], train[:, 1], s=7, alpha=0.18, color="gray", label="training data")
        ax.scatter(points[:, 0], points[:, 1], s=16, alpha=0.72, color="#1676a3", label="query/output")
        ax.set_title(title)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(alpha=0.2)
    axes[0].legend(fontsize=8, loc="upper right")
    fig.suptitle(f"B2/B3 debugging illustration (c=[0,0], R=1, sigma={sigma}, n={n_train})")
    fig.tight_layout()
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    print(make_comparison_figure())

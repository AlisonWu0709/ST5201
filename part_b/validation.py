"""Reproducible implementation checks using temporary debugging parameters."""

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "part_b") not in sys.path:
    sys.path.insert(0, str(ROOT / "part_b"))
from bayes_estimator import oracle_bayes, plugin_bayes
from manifold_fitting import assignment_radii, manifold_fitting


def generate_noisy_circle(rng, n, sigma):
    """Generate one independent noisy sample for implementation checking."""
    theta = rng.uniform(0.0, 2.0 * np.pi, n)
    clean = np.column_stack((np.cos(theta), np.sin(theta)))
    return clean + rng.normal(0.0, sigma, size=(n, 2))


def run_validation():
    rng = np.random.default_rng(5201)
    c_debug = np.array([0.0, 0.0])
    R_debug = 1.0
    sigmas, sizes = (0.05, 0.15, 0.30), (100, 500, 2000)
    rows = []
    max_quad_difference = 0.0
    for sigma in sigmas:
        for n in sizes:
            # Separate random calls create independent training and query sets.
            train = generate_noisy_circle(rng, n, sigma)
            query = generate_noisy_circle(rng, 120, sigma)
            expected_radii = (
                5.0 * sigma / np.log10(n),
                5.0 * sigma / np.log10(n),
                10.0 * sigma * np.sqrt(np.log(1.0 / sigma)) / np.log10(n),
            )
            np.testing.assert_allclose(assignment_radii(n, sigma), expected_radii, rtol=1e-14)
            clean_query = query - rng.normal(0.0, sigma, size=query.shape)
            # Exercise the oracle and plug-in interfaces independently. For
            # this debugging check only, the plug-in arguments are known values.
            oracle = oracle_bayes(query, c_debug, R_debug, sigma)
            plugin = plugin_bayes(query, c_debug.copy(), float(R_debug), sigma)
            far_result = oracle_bayes(np.array([[1e6, -1e6]]), c_debug, R_debug, sigma)
            assert np.isfinite(far_result).all()
            fine = oracle_bayes(query[:25], c_debug, R_debug, sigma, K=1024)
            coarse = oracle_bayes(query[:25], c_debug, R_debug, sigma, K=512)
            quad_diff = float(np.max(np.linalg.norm(coarse - fine, axis=1)))
            max_quad_difference = max(max_quad_difference, quad_diff)
            mf, diag = manifold_fitting(train, query, sigma)
            assert oracle.shape == plugin.shape == mf.shape == query.shape
            assert np.isfinite(oracle).all() and np.isfinite(plugin).all() and np.isfinite(mf).all()
            assert np.isfinite(clean_query).all()
            assert diag.n_query == len(query)
            assert diag.any_fallback == diag.empty_sphere + diag.zero_direction + diag.empty_cylinder
            assert 0 <= diag.as_dict()["fallback_rate"] <= 1
            rows.append({
                "n": n, "sigma": sigma, "r0": assignment_radii(n, sigma)[0],
                "r1": assignment_radii(n, sigma)[1], "r2": assignment_radii(n, sigma)[2],
                "n_query": diag.n_query, "empty_sphere": diag.empty_sphere,
                "zero_direction": diag.zero_direction, "empty_cylinder": diag.empty_cylinder,
                "fallback_total": diag.any_fallback, "fallback_rate": diag.as_dict()["fallback_rate"],
                "max_K512_vs_K1024_norm": quad_diff,
            })
    out = ROOT / "results" / "numerical_checks"
    out.mkdir(parents=True, exist_ok=True)
    total_fallbacks = sum(row["fallback_total"] for row in rows)
    total_queries = sum(row["n_query"] for row in rows)
    overall_fallback_rate = total_fallbacks / total_queries
    import csv
    with (out / "validation_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    with (out / "validation_summary.txt").open("w", encoding="utf-8") as f:
        f.write("Debugging inputs only: c=[0,0], R=1; independently generated train/query samples.\n")
        f.write("Checks: output shapes, finite values, oracle/plugin entry points, K comparison, MF diagnostics.\n")
        f.write("A far-query posterior-mean probe at [1e6, -1e6] was also finite.\n")
        f.write(f"Maximum per-query norm difference between K=512 and K=1024 on 25-query subsets: {max_quad_difference:.8g}\n\n")
        f.write(f"Overall MF fallbacks across all settings: {total_fallbacks}/{total_queries} ({overall_fallback_rate:.4%}).\n")
        for row in rows:
            f.write(
                f"n={row['n']}, sigma={row['sigma']:.2f}: fallback counts "
                f"empty_sphere={row['empty_sphere']}, zero_direction={row['zero_direction']}, "
                f"empty_cylinder={row['empty_cylinder']}; overall={row['fallback_total']}/"
                f"{row['n_query']} ({row['fallback_rate']:.4%}); "
                f"K diff={row['max_K512_vs_K1024_norm']:.4g}\n"
            )
    return rows, max_quad_difference


if __name__ == "__main__":
    rows, difference = run_validation()
    print(f"Validated {len(rows)} settings; max K-grid difference={difference:.8g}")
    total = sum(row["fallback_total"] for row in rows)
    queries = sum(row["n_query"] for row in rows)
    print(f"Overall MF fallbacks: {total}/{queries} ({total / queries:.2%})")
    for row in rows:
        print(
            f"n={row['n']:4d}, sigma={row['sigma']:.2f}: "
            f"empty_sphere={row['empty_sphere']}, zero_direction={row['zero_direction']}, "
            f"empty_cylinder={row['empty_cylinder']}, total={row['fallback_total']}/"
            f"{row['n_query']} ({row['fallback_rate']:.2%})"
        )

"""Reproducible Part A/B1 checks and a plug-in Bayes interface check."""

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from part_a.circle_estimator import estimate_circle
from part_b.bayes_estimator import plugin_bayes
from part_b.projection import oracle_projection, plugin_projection, project_circle


def _expect_value_error(call):
    """Require rejection of an input outside the documented domain."""
    try:
        call()
    except ValueError:
        return
    raise AssertionError("Expected ValueError for an invalid input")


def _generate_sample(rng, n, c, R, sigma):
    """Keep each clean point paired with the observation generated from it."""
    theta = rng.uniform(0.0, 2.0 * np.pi, n)
    clean = c + R * np.column_stack((np.cos(theta), np.sin(theta)))
    noisy = clean + rng.normal(0.0, sigma, size=clean.shape)
    return clean, noisy


def run_validation():
    rng = np.random.default_rng(5201)
    rows = []

    def passed(name):
        rows.append({"check": name, "status": "passed"})

    # Four known points give second central moment 4/3 with denominator n-1.
    training = np.array([[-1.0, 0.0], [1.0, 0.0], [0.0, -1.0], [0.0, 1.0]])
    original_training = training.copy()
    sigma_known = np.sqrt(1.0 / 6.0)
    c_hat, R_hat, Q_hat = estimate_circle(training, sigma_known)
    np.testing.assert_allclose(c_hat, [0.0, 0.0], atol=1e-12)
    np.testing.assert_allclose([R_hat, Q_hat], [1.0, 1.0], atol=1e-12)
    passed("known sample and n-1 correction")

    _, radius_without_noise, Q_without_noise = estimate_circle(training, 0.0)
    np.testing.assert_allclose(Q_without_noise, 4.0 / 3.0, atol=1e-12)
    np.testing.assert_allclose(radius_without_noise, np.sqrt(4.0 / 3.0), atol=1e-12)
    passed("noise variance correction")

    shift = np.array([2.0, -3.0])
    shifted_c, shifted_R, shifted_Q = estimate_circle(training + shift, sigma_known)
    np.testing.assert_allclose(shifted_c, c_hat + shift, atol=1e-12)
    np.testing.assert_allclose([shifted_R, shifted_Q], [R_hat, Q_hat], atol=1e-12)
    passed("parameter translation equivariance")

    collapsed_train = np.tile(shift, (3, 1))
    collapsed_c, collapsed_R, collapsed_Q = estimate_circle(collapsed_train, 0.2)
    np.testing.assert_allclose(collapsed_c, shift, atol=1e-12)
    np.testing.assert_allclose(collapsed_Q, -0.08, atol=1e-12)
    assert collapsed_Q < 0 and collapsed_R == 0.0
    passed("negative Q retained and radius truncated")

    query = np.array([[3.0, 4.0], [0.3, 0.4], [-3.0, -4.0]])
    original_query = query.copy()
    expected = np.array([[0.6, 0.8], [0.6, 0.8], [-0.6, -0.8]])
    projected = project_circle(query, [0.0, 0.0], 1.0)
    np.testing.assert_allclose(projected, expected, atol=1e-12)
    np.testing.assert_allclose(np.linalg.norm(projected, axis=1), 1.0, atol=1e-12)
    passed("inside and outside observations retain direction")

    translated = project_circle(query + shift, shift, 2.0)
    np.testing.assert_allclose(translated, shift + 2.0 * expected, atol=1e-12)
    passed("projection translation and radius scaling")

    single = project_circle(query[0], [0.0, 0.0], 1.0)
    assert single.shape == (2,)
    np.testing.assert_allclose(single, expected[0], atol=1e-12)
    empty = project_circle(np.empty((0, 2)), shift, 1.0)
    assert empty.shape == (0, 2)
    passed("single observation and empty batch shapes")

    np.testing.assert_allclose(project_circle(shift, shift, 2.0), shift + [2.0, 0.0], atol=1e-12)
    mixed = np.vstack((shift, shift + [0.0, 1.0]))
    np.testing.assert_allclose(project_circle(mixed, shift, 2.0), shift + [[2.0, 0.0], [0.0, 2.0]], atol=1e-12)
    passed("center convention returns a fixed circle point")

    np.testing.assert_allclose(project_circle([0.0, 1e-200], [0.0, 0.0], 2.0), [0.0, 2.0], atol=1e-12)
    passed("nonzero points near the center retain direction")

    np.testing.assert_allclose(project_circle(mixed, shift, 0.0), np.tile(shift, (2, 1)), atol=1e-12)
    np.testing.assert_allclose(project_circle(shift, shift, 0.0), shift, atol=1e-12)
    np.testing.assert_allclose(plugin_projection(mixed, collapsed_c, collapsed_R), np.tile(shift, (2, 1)), atol=1e-12)
    np.testing.assert_allclose(plugin_bayes(mixed, collapsed_c, collapsed_R, 0.2), np.tile(shift, (2, 1)), atol=1e-12)
    passed("zero fitted radius is compatible with projection and Bayes")

    np.testing.assert_allclose(oracle_projection(query, [0.0, 0.0], 1.0), expected, atol=1e-12)
    np.testing.assert_allclose(plugin_projection(query, c_hat, R_hat), expected, atol=1e-12)
    passed("explicit oracle and fitted entry points")

    invalid_calls = [
        lambda: estimate_circle([[0.0, 0.0]], 0.1),
        lambda: estimate_circle(np.ones((3, 3)), 0.1),
        lambda: estimate_circle([[0.0, 0.0], [np.nan, 1.0]], 0.1),
        lambda: estimate_circle(training, -0.1),
        lambda: estimate_circle(training, np.inf),
        lambda: project_circle([1.0, 2.0, 3.0], [0.0, 0.0], 1.0),
        lambda: project_circle(query, [0.0], 1.0),
        lambda: project_circle(query, [0.0, 0.0], -1.0),
        lambda: project_circle(query, [0.0, 0.0], np.inf),
        lambda: project_circle([[np.nan, 0.0]], [0.0, 0.0], 1.0),
    ]
    for call in invalid_calls:
        _expect_value_error(call)
    passed("invalid inputs rejected")

    np.testing.assert_array_equal(training, original_training)
    np.testing.assert_array_equal(query, original_query)
    passed("input arrays are not modified")

    # One integration check, not the full Part C simulation study.
    n_train, n_test, sigma = 500, 500, 0.15
    c_true, R_true = shift, 1.5
    _, Y_train = _generate_sample(rng, n_train, c_true, R_true, sigma)
    X_test, Y_test = _generate_sample(rng, n_test, c_true, R_true, sigma)
    fitted_c, fitted_R, fitted_Q = estimate_circle(Y_train, sigma)
    oracle = oracle_projection(Y_test, c_true, R_true)
    fitted = plugin_projection(Y_test, fitted_c, fitted_R)
    bayes = plugin_bayes(Y_test, fitted_c, fitted_R, sigma)
    assert oracle.shape == fitted.shape == bayes.shape == X_test.shape == (n_test, 2)
    assert all(np.isfinite(Z).all() for Z in (oracle, fitted, bayes))
    oracle_error = float(np.max(np.abs(np.linalg.norm(oracle - c_true, axis=1) - R_true)))
    fitted_error = float(np.max(np.abs(np.linalg.norm(fitted - fitted_c, axis=1) - fitted_R)))
    assert oracle_error < 1e-12 and fitted_error < 1e-12
    assert np.all(np.linalg.norm(bayes - fitted_c, axis=1) <= fitted_R + 1e-12)
    passed("independent train/test integration with existing plug-in Bayes")

    out = ROOT / "results" / "numerical_checks"
    out.mkdir(parents=True, exist_ok=True)
    import csv
    with (out / "a_b1_validation_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["check", "status"])
        writer.writeheader()
        writer.writerows(rows)
    with (out / "a_b1_validation_summary.txt").open("w", encoding="utf-8") as f:
        f.write("Part A/B1 implementation checks; not the full Part C simulation study.\n")
        f.write(f"Python: {sys.version.split()[0]}; NumPy: {np.__version__}; seed: 5201.\n")
        f.write(f"Passed {len(rows)} checks.\n")
        f.write(f"Independent integration sample: n_train={n_train}, n_test={n_test}, sigma={sigma}.\n")
        f.write(f"Estimated center: {fitted_c.tolist()}; radius: {fitted_R:.12g}; raw Q: {fitted_Q:.12g}.\n")
        f.write(f"Maximum oracle-circle distance error: {oracle_error:.8g}.\n")
        f.write(f"Maximum fitted-circle distance error: {fitted_error:.8g}.\n\n")
        for row in rows:
            f.write(f"PASS: {row['check']}\n")
    return rows, oracle_error, fitted_error


if __name__ == "__main__":
    rows, oracle_error, fitted_error = run_validation()
    print(f"Passed {len(rows)} Part A/B1 checks.")
    print("Existing plug-in Bayes interface: passed.")
    print(f"Maximum circle-distance errors: oracle={oracle_error:.3g}, fitted={fitted_error:.3g}")
    print("Saved summaries to results/numerical_checks/a_b1_validation_summary.csv and .txt")

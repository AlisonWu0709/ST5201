import numpy as np
import pytest

from member_c_work.metrics_circle import radial_error, coverage_error, circle_grid
from member_c_work.metrics_ellipse import ellipse_grid, bidirectional_ellipse_errors, denoising_mse
from member_c_work.data_generation import generate_ellipse_sample, generate_train_test
from member_c_work.statistics import monte_carlo_summary


def test_circle_radial_known_answers():
    assert radial_error(circle_grid(length=720)) < 1e-28
    assert radial_error(np.zeros((5, 2)), radius=2) == pytest.approx(4.0)


def test_circle_coverage_properties():
    dense = circle_grid(length=720)
    assert coverage_error(dense, length=720) < 1e-28
    arc = dense[:40]
    assert coverage_error(arc, length=720) > 0.5
    assert coverage_error(circle_grid(length=100), length=720) < coverage_error(circle_grid(length=10), length=720)


def test_ellipse_grid_and_bidirectional_zero():
    grid = ellipse_grid(b=.75, length=128)
    assert np.allclose(grid[:, 0] ** 2 + (grid[:, 1] / .75) ** 2, 1)
    errors = bidirectional_ellipse_errors(grid, b=.75, grid_length=128)
    assert errors["output_to_ellipse"] < 1e-28
    assert errors["ellipse_to_output"] < 1e-28


def test_generator_circle_special_case_and_independence():
    rng = np.random.default_rng(5201)
    clean, noisy, theta = generate_ellipse_sample(rng, 500, b=1, sigma=0)
    assert np.allclose(np.linalg.norm(clean, axis=1), 1)
    assert np.array_equal(clean, noisy)
    sample = generate_train_test(np.random.default_rng(3), 5, 5)
    assert not np.array_equal(sample["train_noisy"], sample["test_noisy"])


def test_denoising_and_mcse_known_answers():
    x = np.array([[0., 0.], [1., 1.]])
    assert denoising_mse(x + 1, x) == pytest.approx(2)
    s = monte_carlo_summary([1, 2, 3, 4])
    # Mean 2.5; squared deviations sum to 5; sample variance = 5/3.
    expected_sd = np.sqrt(5 / 3)
    assert s["sample_sd"] == pytest.approx(expected_sd)
    assert s["mcse"] == pytest.approx(expected_sd / 2)


@pytest.mark.parametrize("bad", [np.zeros(2), np.empty((0, 2)), [[np.nan, 0]]])
def test_invalid_points_rejected(bad):
    with pytest.raises(ValueError):
        radial_error(bad)


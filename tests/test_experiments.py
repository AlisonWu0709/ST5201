import json
import numpy as np
import pandas as pd
import pytest
from member_c_work.experiment import run_experiment, SMOKE_DESIGN, C_DESIGN, D_DESIGN
from member_c_work.method_adapters import all_adapters, MethodAdapter
from member_c_work.metrics_circle import circle_grid
from member_c_work.metrics_ellipse import ellipse_grid, bidirectional_ellipse_errors
from member_c_work.result_integration import validate_results, summarize_parameter_recovery
from member_c_work.tests.test_integration import valid_frame


@pytest.mark.parametrize('part,count', [('C', 6), ('D', 4)])
def test_actual_adapters(part, count):
    rng = np.random.default_rng(12)
    train, test = rng.normal(size=(30, 2)), rng.normal(size=(8, 2))
    before = train.copy()
    methods = all_adapters(part)
    assert len(methods) == count
    for method in methods:
        output, diag = method(train, test, .15)
        assert output.shape == (8, 2) and np.isfinite(output).all()
        if method.name == 'mf':
            from part_b.manifold_fitting import manifold_fitting
            expected, diagnostics = manifold_fitting(train, test, .15)
            np.testing.assert_array_equal(output, expected)
            assert diag == diagnostics.as_dict()
        if method.name in ('fitted_projection', 'plugin_posterior_mean'):
            from part_a.circle_estimator import estimate_circle
            from part_b.projection import plugin_projection
            from part_b.bayes_estimator import plugin_bayes
            c, r, q = estimate_circle(train, .15)
            expected = (plugin_projection(test, c, r) if method.name == 'fitted_projection'
                        else plugin_bayes(test, c, r, .15))
            np.testing.assert_array_equal(output, expected)
            assert diag['Q_hat'] == q
    np.testing.assert_array_equal(before, train)


@pytest.mark.parametrize('part', ['C', 'D'])
def test_smoke_and_checkpoint_resume(tmp_path, part):
    design = SMOKE_DESIGN | dict(b=(1.,) if part == 'C' else (1., .75))
    checkpoint = tmp_path / 'SMOKE_TEST_ONLY.json'
    result = run_experiment(part, design, checkpoint, smoke=True)
    count = 6 if part == 'C' else 4
    assert len(result) == count * 2 * len(design['b'])
    assert set(result.run_type) == {'SMOKE_TEST_ONLY'}
    assert result.groupby(['b','n','sigma','repetition_id']).dataset_id.nunique().eq(1).all()
    assert result.dataset_id.nunique() == 2 * len(design['b'])
    assert np.isfinite(result.denoising_mse).all()
    fresh = run_experiment(part, design, smoke=True)
    pd.testing.assert_frame_equal(result.drop(columns='run_id'), fresh.drop(columns='run_id'))
    # Simulate interruption after the first complete repetition.
    saved = json.loads(checkpoint.read_text())
    saved['rows'] = saved['rows'][:count]
    checkpoint.write_text(json.dumps(saved))
    resumed = run_experiment(part, design, checkpoint, smoke=True)
    pd.testing.assert_frame_equal(result, resumed)
    # A complete resume must skip evaluation while replaying the data RNG.
    def fail(*args):
        raise AssertionError('completed method re-evaluated')
    methods = [MethodAdapter(m.name, fail) for m in all_adapters(part)]
    pd.testing.assert_frame_equal(result, run_experiment(part, design, checkpoint, True, methods))
    with pytest.raises(ValueError, match='configuration'):
        run_experiment(part, design | dict(seed=5), checkpoint, smoke=True)
    if part == 'C':
        assert result.loc[result.method == 'mf', 'centre_squared_error'].isna().all()
        assert len(summarize_parameter_recovery(result)) == 4
        assert result.groupby('dataset_id').clean_test_coverage_error.nunique().eq(1).all()
    else:
        assert np.isfinite(result[['output_to_ellipse','ellipse_to_output']]).all().all()
        assert not any(m.startswith('oracle') for m in result.method)


@pytest.mark.parametrize('kind', ['missing', 'duplicate', 'inf', 'nan', 'text', 'sigma_inf', 'negative', 'rate'])
def test_bad_result_records(kind):
    frame = valid_frame()
    if kind == 'missing': frame = frame.iloc[1:]
    elif kind == 'duplicate': frame = pd.concat([frame, frame.iloc[:1]])
    elif kind == 'inf': frame.loc[0, 'denoising_mse'] = np.inf
    elif kind == 'nan': frame.loc[0, 'radial_error'] = np.nan
    elif kind == 'text':
        frame['coverage_error'] = frame.coverage_error.astype(object)
        frame.loc[0, 'coverage_error'] = 'invalid'
    elif kind == 'sigma_inf': frame.loc[0, 'sigma'] = np.inf
    elif kind == 'negative': frame.loc[0, 'denoising_mse'] = -1
    elif kind == 'rate': frame.loc[0, 'mf_fallback_rate'] = 1.1
    with pytest.raises(ValueError): validate_results(frame, expected_repetitions=2)


def test_ellipse_circle_and_nonzero_known_answer():
    np.testing.assert_array_equal(ellipse_grid(b=1, length=64), circle_grid(length=64))
    errors = bidirectional_ellipse_errors(np.zeros((1,2)), b=.75, grid_length=4)
    assert errors['output_to_ellipse'] == pytest.approx(.75**2)
    assert errors['ellipse_to_output'] == pytest.approx((1 + .75**2)/2)


def test_smoke_limits_and_methods():
    with pytest.raises(ValueError, match='tiny'): run_experiment(smoke=True)
    with pytest.raises(ValueError, match='methods'):
        run_experiment(design=SMOKE_DESIGN, smoke=True, methods=all_adapters()[:-1])
    assert C_DESIGN['m'] == D_DESIGN['m'] == 500
    assert C_DESIGN['repetitions'] == D_DESIGN['repetitions'] == 50

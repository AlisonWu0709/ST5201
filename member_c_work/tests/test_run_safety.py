import json
import sys
from unittest.mock import Mock
import numpy as np
import pytest
from member_c_work import provenance
from member_c_work.experiment import run_experiment, main, SMOKE_DESIGN
from member_c_work.postprocess import summarize_run
from member_c_work.method_adapters import all_adapters


@pytest.mark.parametrize('field', ['schema_version', 'seed', 'methods', 'config_hash',
                                  'git_commit', 'git_dirty', 'environment', 'source_hashes'])
def test_resume_rejects_provenance_changes(tmp_path, field):
    checkpoint = tmp_path / 'checkpoint.json'
    run_experiment(design=SMOKE_DESIGN | dict(repetitions=1), checkpoint=checkpoint, smoke=True)
    saved = json.loads(checkpoint.read_text())
    if field == 'git_commit': saved['metadata']['git']['commit'] = 'different'
    elif field == 'git_dirty': saved['metadata']['git']['dirty'] = not saved['metadata']['git']['dirty']
    elif field == 'source_hashes': saved['metadata']['source_hashes']['mf_weighted.py'] = 'changed'
    else: saved['metadata'][field] = 'changed'
    checkpoint.write_text(json.dumps(saved))
    with pytest.raises(ValueError, match='Refusing resume'):
        run_experiment(design=SMOKE_DESIGN | dict(repetitions=1), checkpoint=checkpoint, smoke=True)


def test_source_fingerprint_includes_dependencies():
    hashes = provenance.source_hashes()
    for path in ['part_a/circle_estimator.py', 'part_b/projection.py', 'part_b/bayes_estimator.py',
                 'part_b/manifold_fitting.py', 'mf_weighted.py', 'member_c_work/experiment.py',
                 'member_c_work/method_adapters.py', 'member_c_work/metrics_circle.py',
                 'member_c_work/metrics_ellipse.py', 'member_c_work/data_generation.py']:
        assert len(hashes[path]) == 64


def test_changed_current_source_rejected(tmp_path, monkeypatch):
    path = tmp_path / 'checkpoint.json'
    run_experiment(design=SMOKE_DESIGN, checkpoint=path, smoke=True)
    changed = provenance.source_hashes() | {'part_b/projection.py': 'edited'}
    monkeypatch.setattr(provenance, 'source_hashes', lambda: changed)
    with pytest.raises(ValueError, match='changed source files: part_b/projection.py'):
        run_experiment(design=SMOKE_DESIGN, checkpoint=path, smoke=True)


def test_legacy_checkpoint_rejected(tmp_path):
    path = tmp_path / 'checkpoint.json'
    path.write_text(json.dumps({'metadata': {'part': 'C'}, 'rows': []}))
    with pytest.raises(ValueError, match='schema_version'):
        run_experiment(design=SMOKE_DESIGN, checkpoint=path, smoke=True)


def test_all_official_entry_points_called(monkeypatch):
    from part_a import circle_estimator
    from part_b import projection, bayes_estimator, manifold_fitting
    spies = []
    for module, names in [(circle_estimator, ['estimate_circle']),
                          (projection, ['oracle_projection', 'plugin_projection']),
                          (bayes_estimator, ['oracle_bayes', 'plugin_bayes']),
                          (manifold_fitting, ['manifold_fitting'])]:
        for name in names:
            spy = Mock(wraps=getattr(module, name))
            monkeypatch.setattr(module, name, spy)
            spies.append(spy)
    rng = np.random.default_rng(1)
    train, test = rng.normal(size=(20, 2)), rng.normal(size=(5, 2))
    for method in all_adapters():
        out, diag = method(train, test, .15)
        assert out.shape == (5, 2) and np.isfinite(out).all()
        if method.name == 'mf': assert 0 <= diag['fallback_rate'] <= 1
    assert all(spy.called for spy in spies)


def test_formal_cli_requires_isolated_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['runner', '--formal', '--output-dir', str(tmp_path / 'smoke')])
    with pytest.raises(SystemExit): main('C')
    monkeypatch.setattr(sys, 'argv', ['runner', '--formal', '--resume', '--output-dir', str(tmp_path / 'formal' / 'new')])
    with pytest.raises(SystemExit): main('D')


def test_postprocess_smoke_rejected_by_default_and_test_figures(tmp_path):
    frame = run_experiment(design=SMOKE_DESIGN, checkpoint=tmp_path / 'checkpoint.json', smoke=True)
    frame.to_csv(tmp_path / 'SMOKE_TEST_ONLY_repetitions.csv', index=False)
    with pytest.raises(ValueError, match='FORMAL input'): summarize_run(tmp_path)
    summary = summarize_run(tmp_path, test_only=True)
    assert len(summary) == 24
    assert (tmp_path / 'analysis/SMOKE_TEST_ONLY_summary.csv').exists()
    assert (tmp_path / 'analysis/SMOKE_TEST_ONLY_representative.pdf').exists()
    assert (tmp_path / 'analysis/SMOKE_TEST_ONLY_denoising_mse.png').exists()

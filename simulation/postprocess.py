"""Explicit-directory summaries/figures; rejects nonformal inputs by default."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .provenance import fingerprint, check_compatible
from .statistics import grouped_summary
from .result_integration import validate_results, summarize_parameter_recovery
from .visualization import plot_metric, plot_geometric_outputs, plot_ellipse_outputs


def summarize_run(run_dir, test_only=False):
    root = Path(run_dir)
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    config = manifest['configuration']
    expected_type = 'SMOKE_TEST_ONLY' if test_only else 'FORMAL'
    if config['run_type'] != expected_type:
        raise ValueError('formal summaries require FORMAL input; smoke cannot enter formal summaries')
    check_compatible(manifest, fingerprint(config['part'], config['design'],
                                          config['methods'], expected_type))
    prefix = 'SMOKE_TEST_ONLY_' if test_only else ''
    data = pd.read_csv(root / (prefix + 'repetitions.csv'))
    if (not data.run_type.eq(expected_type).all() or
        not data.run_id.eq(manifest['run_id']).all() or
        not data.config_hash.eq(manifest['config_hash']).all()):
        raise ValueError('CSV run identity mismatch')
    design = config['design']
    expected = {(b, n, s, rep, method) for b in design['b'] for n in design['n']
                for s in design['sigma'] for rep in range(design['repetitions']) for method in config['methods']}
    keys = ['b', 'n', 'sigma', 'repetition_id', 'method']
    actual = set(data[keys].itertuples(index=False, name=None))
    if len(data) != len(expected) or actual != expected:
        raise ValueError('incomplete or duplicate repetition-level results')
    if not data.groupby(keys[:-1]).dataset_id.nunique().eq(1).all():
        raise ValueError('dataset_id pairing mismatch')
    if config['part'] == 'C':
        validate_results(data, expected_repetitions=design['repetitions'])
        metrics = ['denoising_mse', 'radial_error', 'coverage_error', 'clean_test_coverage_error']
        groups, facet = ('n', 'sigma', 'method'), 'sigma'
    else:
        metrics = ['denoising_mse', 'output_to_ellipse', 'ellipse_to_output']
        groups, facet = ('n', 'b', 'method'), 'b'
    if not np.isfinite(data[metrics]).all().all() or (data[metrics] < 0).any().any():
        raise ValueError('invalid metrics')
    target = root / 'analysis'
    target.mkdir(exist_ok=True)
    summary = grouped_summary(data, metrics, group_by=groups)
    summary.to_csv(target / (prefix + 'summary.csv'), index=False)
    if config['part'] == 'C':
        summarize_parameter_recovery(data).to_csv(target / (prefix + 'parameter_summary.csv'), index=False)
    for metric in metrics:
        fig = plot_metric(summary, metric, facet=facet)
        if test_only:
            fig.suptitle('SMOKE_TEST_ONLY')
        for suffix in ('png', 'pdf'):
            fig.savefig(target / f'{prefix}{metric}.{suffix}', bbox_inches='tight')
        plt.close(fig)
    representative = root / 'representative.npz'
    if representative.exists():
        with np.load(representative, allow_pickle=False) as saved:
            if str(saved['dataset_id']) not in set(data.dataset_id):
                raise ValueError('representative data belongs to another run')
            outputs = {method: saved[method] for method in config['methods']}
            outputs = {'Clean test points': saved['test_clean'], **outputs}
            fig = (plot_geometric_outputs(outputs) if config['part'] == 'C'
                   else plot_ellipse_outputs(outputs, b=float(saved['b'])))
            if test_only:
                fig.suptitle('SMOKE_TEST_ONLY')
            for suffix in ('png', 'pdf'):
                fig.savefig(target / f'{prefix}representative.{suffix}', bbox_inches='tight')
            plt.close(fig)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--test-only', action='store_true')
    args = parser.parse_args()
    summary = summarize_run(args.run_dir, args.test_only)
    print(f'Summaries/figures saved under {args.run_dir / "analysis"}; {len(summary)} summary rows')


if __name__ == '__main__':
    main()

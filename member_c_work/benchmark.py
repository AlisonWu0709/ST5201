"""One n=100, m=100, sigma=.15 repetition, timing only; never a formal run."""
import argparse
import json
from pathlib import Path
from time import perf_counter
import uuid
import numpy as np
import pandas as pd
from .data_generation import generate_train_test
from .method_adapters import all_adapters
from .metrics_circle import radial_error, coverage_error
from .metrics_ellipse import denoising_mse, bidirectional_ellipse_errors
from .provenance import fingerprint, atomic_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    root = args.output_dir.resolve()
    if 'benchmark' not in [p.lower() for p in root.parts]:
        parser.error('output must be in a benchmark/ directory')
    if root.exists() and any(root.iterdir()):
        parser.error('choose an empty benchmark run directory')
    methods = all_adapters('C')
    design = dict(n=[100], sigma=[.15], b=[1.], m=100, repetitions=1,
                  grid_length=720, seed=5201)
    manifest = fingerprint('C', design, [m.name for m in methods], 'BENCHMARK_ONLY')
    manifest['run_id'] = str(uuid.uuid4())
    atomic_json(root / 'manifest.json', manifest)
    start = perf_counter()
    rng = np.random.default_rng(5201)
    sample = generate_train_test(rng, 100, 100, sigma=.15)
    generation = perf_counter() - start
    rows = []
    for method in methods:
        start = perf_counter()
        output, diagnostics = method(sample['train_noisy'], sample['test_noisy'], .15)
        seconds = perf_counter() - start
        start = perf_counter()
        denoising_mse(output, sample['test_clean'])
        radial_error(output)
        coverage_error(output, length=720)
        c_metrics = perf_counter() - start
        # Timing the D metric kernel on this SAME sample; no new D simulation.
        start = perf_counter()
        denoising_mse(output, sample['test_clean'])
        bidirectional_ellipse_errors(output, b=1., grid_length=4096)
        d_metrics = perf_counter() - start
        rows.append(dict(method=method.name, method_seconds=seconds,
                         c_metrics_seconds=c_metrics, d_metrics_seconds=d_metrics,
                         output_shape=str(output.shape), finite=bool(np.isfinite(output).all()),
                         mf_fallback_rate=diagnostics.get('fallback_rate'),
                         run_type='BENCHMARK_ONLY'))
    timing = pd.DataFrame(rows)
    timing.to_csv(root / 'BENCHMARK_ONLY_timings.csv', index=False)
    # n-average=(100+500+2000)/3, m multiplier=500/100. MF assumed O(n*m).
    # Other methods/geometry assumed O(m), with fixed K/grid. Only extrapolation.
    def estimate(part):
        selected = timing if part == 'C' else timing[~timing.method.str.startswith('oracle_')]
        methods_cost = sum(row.method_seconds * 5 * (26/3 if row.method == 'mf' else 1)
                           for row in selected.itertuples())
        metric_cost = selected[f'{part.lower()}_metrics_seconds'].sum() * 5
        baseline_cost = timing.c_metrics_seconds.mean() * 5 if part == 'C' else 0
        return 450 * (methods_cost + metric_cost + baseline_cost + generation * 16)
    estimates = {part: estimate(part) for part in ('C', 'D')}
    report = dict(run_type='BENCHMARK_ONLY', design=design, generation_seconds=generation,
                  estimates_seconds=estimates,
                  planning_range_seconds={k: [v * .5, v * 3] for k, v in estimates.items()},
                  assumptions='Single sample; MF linear in n*m, Bayes linear in m at fixed K, '
                  'geometry linear in grid*m. 450 repetitions per part. Range is a heuristic, '
                  'not a confidence interval. Excludes full-checkpoint I/O, plots, imports; '
                  'noise/shape, cache, BLAS and larger working sets can change runtime.')
    atomic_json(root / 'BENCHMARK_ONLY_estimates.json', report)
    print(timing[['method', 'method_seconds']].to_string(index=False))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()

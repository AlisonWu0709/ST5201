"""Shared runner with explicit smoke/formal CLI and strict resume provenance."""
from pathlib import Path
import argparse
import hashlib
import json
import uuid
from .provenance import fingerprint, check_compatible, atomic_json
import numpy as np
import pandas as pd
from part_a.circle_estimator import estimate_circle
from part_c.parameter_recovery import parameter_recovery_metrics
from .data_generation import generate_train_test
from .method_adapters import all_adapters
from .metrics_circle import radial_error, coverage_error
from .metrics_ellipse import bidirectional_ellipse_errors, denoising_mse

C_DESIGN = dict(n=(100, 500, 2000), sigma=(.05, .15, .30), b=(1.,),
                m=500, repetitions=50, seed=5201, grid_length=720)
D_DESIGN = dict(n=(100, 500, 2000), sigma=(.15,), b=(1., .9, .75),
                m=500, repetitions=50, seed=5201, grid_length=4096)
SMOKE_DESIGN = dict(n=(30,), sigma=(.15,), m=12, repetitions=2, grid_length=64)


def run_experiment(part='C', design=None, checkpoint=None, smoke=False, methods=None, run_type=None):
    if part not in ('C', 'D'):
        raise ValueError('part must be C or D')
    config = (C_DESIGN if part == 'C' else D_DESIGN) | (design or {})
    if part == 'C' and tuple(config['b']) != (1.,):
        raise ValueError('Part C requires the unit circle')
    for key, minimum in [('m', 1), ('repetitions', 1), ('grid_length', 3)]:
        if not isinstance(config[key], int) or config[key] < minimum:
            raise ValueError(f'invalid {key}')
    if not config['n'] or any(int(n) != n or n < 2 for n in config['n']):
        raise ValueError('invalid n')
    if not config['sigma'] or any(not 0 < s < 1 for s in config['sigma']):
        raise ValueError('invalid sigma')
    if not config['b'] or any(not np.isfinite(b) or b <= 0 for b in config['b']):
        raise ValueError('invalid b')
    if any(len(set(config[k])) != len(config[k]) for k in ('n', 'sigma', 'b')):
        raise ValueError('duplicate settings')
    if smoke and (len(config['n'])*len(config['sigma'])*len(config['b']) > 2
                  or config['repetitions'] > 2 or config['m'] > 40):
        raise ValueError('smoke must remain tiny')
    methods = all_adapters(part) if methods is None else methods
    if sorted(m.name for m in methods) != sorted(m.name for m in all_adapters(part)):
        raise ValueError('missing or duplicate methods')
    run_type = run_type or ('SMOKE_TEST_ONLY' if smoke else 'FORMAL')
    if run_type not in ('SMOKE_TEST_ONLY', 'BENCHMARK_ONLY', 'FORMAL'):
        raise ValueError('invalid run_type')
    if smoke and run_type != 'SMOKE_TEST_ONLY':
        raise ValueError('smoke run_type mismatch')
    identity = fingerprint(part, config, [m.name for m in methods], run_type)
    path = Path(checkpoint) if checkpoint else None
    rows = []
    metadata = dict(identity, run_id=str(uuid.uuid4()), run_type=run_type)
    manifest = path.parent / 'manifest.json' if path else None
    if path and path.exists():
        saved = json.loads(path.read_text(encoding='utf-8'))
        check_compatible(saved['metadata'], identity)
        metadata = saved['metadata']
        rows = saved['rows']
    if manifest and manifest.exists():
        existing = json.loads(manifest.read_text(encoding='utf-8'))
        check_compatible(existing, identity)
        if path.exists() and existing != metadata:
            raise ValueError('manifest/checkpoint mismatch; refusing resume')
        metadata = existing
    if manifest and not manifest.exists():
        atomic_json(manifest, metadata)
    completed = {}
    for row in rows:
        key = (row['b'], row['n'], row['sigma'], row['repetition_id'])
        completed.setdefault(key, []).append(row)
    rng = np.random.default_rng(config['seed'])  # exactly once, including resume
    visited = set()
    for b in config['b']:
        for n in config['n']:
            for sigma in config['sigma']:
                for rep in range(config['repetitions']):
                    # Regenerate skipped samples too, preserving the one RNG stream.
                    sample = generate_train_test(rng, n, config['m'], b, sigma)
                    h = hashlib.sha256(json.dumps([part, b, n, sigma, rep]).encode())
                    for name in ('train_noisy', 'test_noisy', 'test_clean'):
                        h.update(np.asarray(sample[name], dtype='<f8').tobytes())
                    did = h.hexdigest()
                    key = (b, n, sigma, rep)
                    visited.add(key)
                    if key in completed:
                        block = completed[key]
                        if (sorted(r['method'] for r in block) != sorted(m.name for m in methods)
                            or any(r['dataset_id'] != did for r in block)):
                            raise ValueError('invalid checkpoint pairing or methods')
                        continue
                    c, r, q = estimate_circle(sample['train_noisy'], sigma)
                    pm = parameter_recovery_metrics(c, r, q, (0, 0), 1)
                    baseline = coverage_error(sample['test_clean'], length=config['grid_length']) if part == 'C' else None
                    block = []
                    representative = {}
                    for method in methods:
                        out, diag = method(sample['train_noisy'].copy(), sample['test_noisy'].copy(), sigma)
                        representative[method.name] = out
                        row = dict(dataset_id=did, repetition_id=rep, n=n, sigma=sigma, b=b,
                                   m=config['m'], grid_length=config['grid_length'], seed=config['seed'],
                                   method=method.name, run_type=metadata['run_type'], run_id=metadata['run_id'],
                                   config_hash=metadata['config_hash'],
                                   denoising_mse=denoising_mse(out, sample['test_clean']),
                                   mf_fallback_rate=diag.get('fallback_rate'), diagnostics=json.dumps(diag))
                        if part == 'C':
                            # Parameter metrics describe the single Part A fit, not MF.
                            fitted = method.name in ('fitted_projection', 'plugin_posterior_mean')
                            row.update(centre_squared_error=pm['center_sq_error'] if fitted else None,
                                       radius_error=pm['radius_error'] if fitted else None,
                                       radius_squared_error=pm['radius_sq_error'] if fitted else None,
                                       negative_Q=pm['q_negative'] if fitted else None,
                                       radial_error=radial_error(out),
                                       coverage_error=coverage_error(out, length=config['grid_length']),
                                       clean_test_coverage_error=baseline)
                        else:
                            row.update(bidirectional_ellipse_errors(out, b=b, grid_length=config['grid_length']))
                        block.append(row)
                    if path and not rows:
                        np.savez_compressed(path.parent / 'representative.npz',
                                            test_clean=sample['test_clean'], test_noisy=sample['test_noisy'],
                                            n=n, sigma=sigma, b=b, dataset_id=did,
                                            **{name: value for name, value in representative.items()})
                    rows.extend(block)
                    if path:
                        atomic_json(path, dict(metadata=metadata, rows=rows))
    if set(completed) - visited:
        raise ValueError('checkpoint contains unexpected settings')
    result = pd.DataFrame(rows)
    metric_columns = ['denoising_mse'] + (['radial_error', 'coverage_error', 'clean_test_coverage_error']
                     if part == 'C' else ['output_to_ellipse', 'ellipse_to_output'])
    for column in metric_columns:
        values = pd.to_numeric(result[column], errors='coerce')
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError(f'invalid result metric: {column}')
    rates = pd.to_numeric(result.loc[result.method == 'mf', 'mf_fallback_rate'], errors='coerce')
    if not np.isfinite(rates).all() or ((rates < 0) | (rates > 1)).any():
        raise ValueError('invalid MF fallback rate')
    if not result.run_id.eq(metadata['run_id']).all() or not result.config_hash.eq(metadata['config_hash']).all():
        raise ValueError('checkpoint row identity mismatch')
    if not result.run_type.eq(metadata['run_type']).all():
        raise ValueError('checkpoint run_type mismatch')
    if part == 'C':
        from .result_integration import validate_results
        validate_results(result, expected_repetitions=config['repetitions'])
    result.attrs['manifest'] = metadata
    return result


def main(part):
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--smoke', action='store_true')
    mode.add_argument('--formal', action='store_true')
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    kind = 'smoke' if args.smoke else 'formal'
    output = args.output_dir.resolve()
    if kind not in [p.lower() for p in output.parts]:
        parser.error(f'output directory must be beneath a {kind}/ directory')
    if args.formal and any('smoke' in p.lower() or 'demo' in p.lower() or 'benchmark' in p.lower()
                           for p in output.parts):
        parser.error('formal output directory must not contain smoke/demo/benchmark')
    if output.exists() and any(output.iterdir()) and not args.resume:
        parser.error('run directory is nonempty; use --resume or a new directory')
    checkpoint = output / 'checkpoint.json'
    if args.resume and not checkpoint.exists():
        parser.error('--resume requires an existing checkpoint.json')
    design = SMOKE_DESIGN | dict(b=(1.,) if part == 'C' else (1., .75)) if args.smoke else None
    result = run_experiment(part, design, checkpoint=checkpoint, smoke=args.smoke)
    prefix = 'SMOKE_TEST_ONLY_' if args.smoke else ''
    result.to_csv(output / (prefix + 'repetitions.csv'), index=False)
    print(f"{result.attrs['manifest']['run_type']}: Part {part}, {len(result)} rows -> {output}")

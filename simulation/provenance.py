"""Strict, versioned run identity; only reads Git and source files."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 'st5201-repetition-v2'


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode('utf-8')).hexdigest()


def source_hashes():
    paths = [ROOT / p for p in ('part_a/circle_estimator.py', 'part_b/projection.py',
             'part_b/bayes_estimator.py', 'part_b/manifold_fitting.py',
             'mf_weighted.py', 'part_c/parameter_recovery.py')]
    paths += sorted((ROOT / 'member_c_work').glob('*.py'))
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths}


def git_state():
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=ROOT).decode('utf-8').strip()
    return {'commit': git('rev-parse', 'HEAD'),
            'dirty': bool(git('status', '--porcelain', '--untracked-files=normal'))}


def fingerprint(part, design, names, run_type):
    # Also record the fixed settings not exposed as configurable parameters.
    configuration = dict(part=part, design=design, methods=names, run_type=run_type,
                         c=[0., 0.], R=1., bayes_K=512, mf_k=3,
                         mf_radii='B3-corrected-995c669', angular_sampling='uniform-angle')
    return json.loads(json.dumps(dict(
        schema_version=SCHEMA_VERSION, configuration=configuration,
        config_hash=canonical_hash(configuration), seed=design['seed'],
        methods=names, git=git_state(), source_hashes=source_hashes(),
        environment={'python': platform.python_version(), 'numpy': np.__version__,
                     'pandas': pd.__version__})))


def check_compatible(saved, current):
    different = [key for key in current if saved.get(key) != current[key]]
    if different:
        detail = ''
        if 'source_hashes' in different:
            old, new = saved.get('source_hashes', {}), current['source_hashes']
            detail = '; changed source files: ' + ', '.join(
                p for p in sorted(set(old) | set(new)) if old.get(p) != new.get(p))
        raise ValueError('checkpoint configuration/provenance mismatch: ' +
                         ', '.join(different) + detail +
                         '. Refusing resume; use a new run directory.')


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')
    temp.replace(path)

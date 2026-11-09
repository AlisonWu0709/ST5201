# Final reproducibility notes

## Environment

The formal runs used Python 3.12.14, NumPy 2.5.4 and pandas 3.1.1. From the repository root, activate `.venv` and install `member_c_work/requirements.txt`. Record the complete final environment with `python -m pip freeze`.

## Separation of responsibilities

- Data generation: `member_c_work/data_generation.py`
- Method fitting: `member_c_work/method_adapters.py` and the Part A/B modules
- Evaluation: `metrics_circle.py`, `metrics_ellipse.py`, `statistics.py`
- Experiment orchestration: `experiment.py`, `part_c_experiment.py`, `part_d_experiment.py`
- Formal aggregation and figures: `postprocess.py`
- Provenance and safe resume: `provenance.py`

## Formal commands

```powershell
python -m member_c_work.part_c_experiment --formal --output-dir ../ST5201-formal-results/formal/part_c_run01
python -m member_c_work.part_d_experiment --formal --output-dir ../ST5201-formal-results/formal/part_d_run01
```

For an interrupted compatible run only, add `--resume`. Never resume after changing configuration, source, environment or Git state. Postprocess with:

```powershell
python -m member_c_work.postprocess --run-dir ../ST5201-formal-results/formal/part_c_run01
python -m member_c_work.postprocess --run-dir ../ST5201-formal-results/formal/part_d_run01
```

Do not overwrite the audited formal directories. Each contains a manifest, checkpoint, repetition-level CSV, representative data and analysis outputs. Formal postprocessing rejects smoke data.

## MF settings

Use `k=3`, `r0=r1=5*sigma/log10(n)` and `r2=10*sigma*sqrt(log(1/sigma))/log10(n)`, where the inner logarithm is natural. Empty-sphere, zero-direction and empty-cylinder fallbacks are returned and counted rather than discarded.

## Verification

```powershell
python -m compileall -q part_a part_b part_c member_c_work
python -m pytest -q
python part_b/validation_projection.py
python part_b/validation.py
git diff --check
git status --short
```

The archive should include code, the main README, these notes and numerical summaries underlying the main figures. Exclude `.venv`, caches, temporary logs, smoke/demo artefacts and unnecessary large checkpoint files.

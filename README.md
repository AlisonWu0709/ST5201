# ST5201 Circle Project — Code and Results

Code and numerical summaries for *Recovering a Circle from Noisy Data*. The report is submitted separately as a PDF.

The model is `X = c + R(cos Θ, sin Θ)`, `Y = X + ε`, `Θ ~ Uniform(0, 2π)`, `ε ~ N(0, σ²I₂)`, with `σ` known. All fitted methods use only the noisy training sample. True `c` and `R` are used only by the methods explicitly labelled *oracle*.

## Repository layout

```text
ST5201/
├── README.md
├── requirements.txt
├── mf_weighted.py                  Supplied MF reference implementation (unchanged)
│
├── part_a/circle_estimator.py      A   Moment estimator: c_hat, R_hat, Q_hat
├── part_b/
│   ├── projection.py               B1  Oracle and fitted circle projection
│   ├── bayes_estimator.py          B2  Oracle and plug-in posterior mean (K = 512 grid)
│   ├── manifold_fitting.py         B3  Wrapper around mf_weighted.py (k = 3, assignment radii)
│   ├── validation_projection.py        Numerical checks for A and B1
│   ├── validation.py                   Numerical checks for B2 (K = 512 vs 1024) and B3
│   └── visualization.py                B2/B3 output plot for several observations
├── part_c/parameter_recovery.py    C1  Centre error, radius bias/MSE, negative-Q indicator
│
├── simulation/                     C/D simulation study
│   ├── data_generation.py              Data generation (circle and ellipse, uniform angle)
│   ├── method_adapters.py              Fitting: common interface for all six methods
│   ├── metrics_circle.py               Evaluation: radial and coverage error (Part C)
│   ├── metrics_ellipse.py              Evaluation: denoising MSE, two-way ellipse distances (Part D)
│   ├── statistics.py                   Mean, sample SD, Monte Carlo SE over repetitions
│   ├── result_integration.py           Completeness and pairing checks on repetition-level results
│   ├── experiment.py                   Experiment engine (designs, seed, checkpoint/resume)
│   ├── part_c_experiment.py            Entry point: Part C
│   ├── part_d_experiment.py            Entry point: Part D (Option 3, ellipse)
│   ├── postprocess.py                  Aggregation, summary CSVs and figures for one run
│   ├── visualization.py                Plot helpers
│   └── provenance.py                   Records config, Git commit, source hashes, versions
├── tests/                          pytest suite (metrics, experiments, integration, run safety)
│
└── results/
    ├── tables/                     Summaries underlying the report's main tables and figures
    ├── figures/                    B2/B3 output figure; Part D representative scatterplot
    └── numerical_checks/           Outputs of the Part A/B validation scripts
```

The code separates data generation, fitting and evaluation as follows:

| Stage | Code |
|---|---|
| Data generation | `simulation/data_generation.py` |
| Fitting | `part_a/`, `part_b/`, `mf_weighted.py`, through `simulation/method_adapters.py` |
| Evaluation | `part_c/parameter_recovery.py`, `simulation/metrics_circle.py`, `simulation/metrics_ellipse.py`, `simulation/statistics.py` |

## Software

The formal results were produced with **Python 3.12.14, NumPy 2.5.4, pandas 3.1.1** and matplotlib. Install the dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
```

`requirements.txt` asks for NumPy ≥ 2.0, pandas ≥ 2.0, matplotlib ≥ 3.8 and pytest ≥ 8.0. Run every command below from the repository root.

## Reproducing the results

### 1. Implementation checks (Parts A and B)

```bash
python part_b/validation_projection.py   # -> results/numerical_checks/a_b1_validation_summary.*
python part_b/validation.py              # -> results/numerical_checks/validation_summary.*
python part_b/visualization.py           # -> results/figures/b2_b3_debug_comparison.png
python -m pytest -q
```

The validation scripts check the `n − 1` correction, noise subtraction, negative `Q_hat`, projection conventions and the K = 512 vs K = 1024 quadrature agreement. They also check the MF radii and fallback counts. They are implementation checks, not the 50-repetition study.

### 2. Parts C and D simulation

A quick smoke run checks that the pipeline works. Its output is labelled `SMOKE_TEST_ONLY` and is not evidence:

```bash
python -m simulation.part_c_experiment --smoke --output-dir simulation/artifacts/smoke/c
python -m simulation.part_d_experiment --smoke --output-dir simulation/artifacts/smoke/d
```

Formal runs. The output directory must be new and lie beneath a directory named `formal/`; keep it outside the repository and start from a clean Git state, because the commit is recorded:

```bash
python -m simulation.part_c_experiment --formal --output-dir ../ST5201-formal-results/formal/part_c_run01
python -m simulation.part_d_experiment --formal --output-dir ../ST5201-formal-results/formal/part_d_run01

python -m simulation.postprocess --run-dir ../ST5201-formal-results/formal/part_c_run01
python -m simulation.postprocess --run-dir ../ST5201-formal-results/formal/part_d_run01
```

Each run directory contains `manifest.json`, `checkpoint.json`, the repetition-level `repetitions.csv`, and `analysis/` with `summary.csv`, `parameter_summary.csv` (Part C only) and PNG/PDF figures. An interrupted run can be continued with `--resume`. The code refuses to resume if the configuration, source files, environment or Git state have changed.

## Experimental design

| | Part C (common study) | Part D (Option 3: ellipse) |
|---|---|---|
| Truth | Circle, `c = (0, 0)`, `R = 1` | Ellipse `(cos Θ, b sin Θ)`, `b ∈ {1, 0.9, 0.75}` |
| `n` | 100, 500, 2000 | 100, 500, 2000 |
| `σ` | 0.05, 0.15, 0.30 | 0.15 (fixed) |
| Repetitions / test size | 50 / `m = 500` | 50 / `m = 500` |
| Methods | raw, oracle projection, fitted projection, oracle posterior mean, plug-in posterior mean, MF | raw, fitted projection, plug-in posterior mean, MF |
| Geometry metrics | radial error; coverage error on `L = 720` circle grid; clean-test coverage as reference | squared nearest-neighbour distance in both directions against a 4096-point ellipse grid |

- **Seed:** 5201 is set once at the start of each run. It is never reset per method.
- **Fresh data:** each repetition draws a fresh training sample and an independent clean/noisy test sample. All methods are applied to the same test sample.
- **Uncertainty:** Monte Carlo SEs are computed from the 50 repetition-level values, not from pooled test points.

## Method settings

- **A.** `c_hat = mean(Y)` and `Q_hat = Σ‖Yᵢ − Ȳ‖²/(n − 1) − 2σ²`, with `R_hat = sqrt(max(Q_hat, 0))`. Negative `Q_hat` values are kept for reporting.
- **B1.** At `y = c` the output is `c + R(1, 0)`. If `R_hat = 0`, fitted projection returns `c_hat`.
- **B2.** The posterior mean uses an equally spaced grid with `K = 512`. The maximum log-weight is subtracted before exponentiating. The plug-in rule substitutes `(c_hat, R_hat)`.
- **B3 radii.** MF uses `k = 3`, `r0 = r1 = 5σ / log10(n)` and `r2 = 10σ·sqrt(ln(1/σ)) / log10(n)`.
- **B3 queries and fallbacks.** MF is evaluated only on independent test queries. Empty-sphere, zero-direction and empty-cylinder fallbacks follow the assignment conventions and are counted. In the formal Part C run, 1,438 of 225,000 queries (0.639%) used the empty-sphere fallback; the other two fallbacks never occurred.

## Results in this archive

| File | Content |
|---|---|
| `results/tables/part_c_method_metrics.csv` | Part C: mean, sample SD, MCSE of denoising MSE, radial error and coverage error, per `(n, σ, method)` |
| `results/tables/part_c_parameter_recovery.csv` | Part C1: centre MSE, radius bias, radius MSE, proportion of negative `Q_hat`, per `(n, σ)` |
| `results/tables/part_d_option3_metrics.csv` | Part D: mean, sample SD, MCSE of denoising MSE and the two ellipse distances, per `(n, b, method)` |
| `results/tables/REPORT_TABLES.md` | Readable version of the `n = 2000` rows used in the report |
| `results/figures/b2_b3_debug_comparison.png` | B2/B3 outputs for several observations |
| `results/figures/part_d_representative_b075.png`, `.json` | Equal-axis scatterplot for `b = 0.75, n = 2000`, repetition 0. The JSON records the dataset hash that matches the formal run |
| `results/numerical_checks/` | Part A/B validation summaries |

The tables come from the formal runs below. Every summary was independently recomputed from the repetition-level CSVs and matched exactly. All 2700 Part C rows and 1800 Part D rows are complete, with no duplicates.

| Run | Run ID | Commit |
|---|---|---|
| Part C | `5bd5f7b4-e142-4237-8b35-1a3598db8d67` | `84b3b22` (clean) |
| Part D | `0d19358e-e90e-49ee-83d6-9851c8c0d805` | `84b3b22` (clean) |

At commit `84b3b22` the `simulation/` package was named `member_c_work/`. It has since been renamed without changing any computation. To reproduce the recorded provenance exactly, check out that commit and use `python -m member_c_work.part_c_experiment ...`.

# ST5201 Circle Project: Parts B2 and B3

This project folder contains the implementation work for **B2 (Bayes posterior mean)** and **B3 (Manifold Fitting)** only. Part A, B1, C, and D are outside this contribution. The assignment PDF and instructor-provided `mf_weighted.py` remain unchanged.

## Files

- `part_b/bayes_estimator.py`: quadrature Bayes rule and oracle/plug-in interfaces.
- `part_b/manifold_fitting.py`: B3 settings wrapper around `mf_weighted.py`.
- `part_b/validation.py`: debugging checks and fallback summary outputs.
- `part_b/visualization.py`: representative debugging plot.
- `results/numerical_checks/`: generated fallback counts and quadrature checks.
- `results/figures/`: generated comparison figure.

## Running

From the project root, with Python 3, NumPy, and Matplotlib installed:

```powershell
python part_b/validation.py
python part_b/visualization.py
```

Validation uses the requested temporary debugging values `c=[0,0]`, `R=1`, `sigma in {0.05, 0.15, 0.30}`, and `n in {100, 500, 2000}`. These are not Part A fitted estimates and do not constitute the full Part C simulation study. Each setting has independently generated training and query observations.

## B2: posterior mean

`bayes_posterior_mean(Y, c, R, sigma, K=512)` accepts `Y` with shape `(n, 2)` and returns shape `(n, 2)`; a single `(2,)` observation is also supported. `oracle_bayes(Y, c_true, R_true, sigma, K=512)` and `plugin_bayes(Y, c_hat, R_hat, sigma, K=512)` are explicit aliases for the true and estimated parameter cases.

For each of K equally spaced angles, the implementation forms the circle point and its Gaussian log likelihood. It subtracts the largest log weight for each observation before exponentiation, normalizes the resulting weights, and takes their weighted mean. The common angular grid spacing cancels in the ratio of integrals.

Under squared Euclidean loss, conditional expected loss decomposes as `E[||a-X||^2 | Y] = ||a-E[X|Y]||^2 + E[||X-E[X|Y]||^2 | Y]`; hence the conditional mean minimizes it. The mean may be inside the circle because posterior mass can be spread across different angles and the weighted average of circle points need not itself have radius R. That is consistent with pointwise squared-error optimality.

## B3: manifold fitting

`manifold_fitting(Y_train, Y_query, sigma)` requires independent arrays shaped `(n,2)` and `(m,2)`. It returns `(predictions, diagnostics)`. The wrapper calls the reference function `mf_weighted.manifold_fit_weighted` with `k=3` and explicit assignment radii:

`r0 = r1 = 5*sigma/log10(n)` and `r2 = 10*sigma*sqrt(log(1/sigma))/log10(n)`.

The instructor function exposes `MFDiagnostics` with counts for `empty_sphere`, `zero_direction`, and `empty_cylinder`, and aggregate count/rate. Thus the wrapper reports the fallback conditions directly without instrumentation. 

Step 1 uses a local spherical neighborhood around a query and its weighted center to estimate a contraction direction. Step 2 weights observations in a cylinder aligned with that direction, with a transverse radius and an axial taper, and returns their weighted center. If the first neighborhood is empty the query is returned; if the direction is numerically zero the first weighted center is returned; if the cylinder is empty the first weighted center is returned.

## Plugging in Part A later

When Part A supplies estimates, pass them directly:

```python
from part_b.bayes_estimator import plugin_bayes

Z_plugin = plugin_bayes(Y_test, c_hat, R_hat, sigma)  # Y_test: (m, 2), Z_plugin: (m, 2)
```

No parameter estimator is implemented here. The same fitted `c_hat` and `R_hat` should be used for each relevant test set and be estimated from training data only.

## Validation and limitations

The generated `validation_summary.csv` contains all nine `(n,sigma)` settings, exact MF fallback counts and rates, radii, and maximum per-query K=512 vs K=1024 differences on 25-query subsets. `validation_summary.txt` summarizes the run and gives the aggregate fallback rate across settings. These are implementation checks on debugging inputs, not denoising performance claims. The plot likewise illustrates oracle B2 and B3 on one debugging dataset, not comparative evidence or a tuned result. Results vary if the validation code or random-number generation is changed. The MF estimator itself does not estimate circle parameters.

Report-ready B2/B3 method descriptions are given above; include the fallback counts from the generated summary and identify the parameters as debugging inputs when citing them. Python/package versions are environment-dependent and can be recorded with `python --version` and `python -m pip show numpy matplotlib` when archiving a run.

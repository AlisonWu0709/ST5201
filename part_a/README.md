# ST5201 Circle Project Parts A and B1

This contribution implements Part A circle parameter estimation and Part B1 projection, using the existing repository's NumPy conventions and Part B2 plug-in Bayes interface.

## Files

- `part_a/circle_estimator.py`: moment-based circle parameter estimation.
- `part_b/projection.py`: common circle projection and explicit oracle/fitted entry points.
- `part_b/validation_projection.py`: numerical checks and integration with the existing `plugin_bayes` function.
- `results/numerical_checks/a_b1_validation_summary.csv` and `.txt`: generated check summaries.

## Interfaces

```python
estimate_circle(Y_train, sigma) -> c_hat, R_hat, Q_hat
project_circle(Y, c, R) -> Z
oracle_projection(Y, c_true, R_true) -> Z
plugin_projection(Y, c_hat, R_hat) -> Z
```

`Y_train` has shape `(n, 2)`, with `n >= 2`. The center has shape `(2,)`; `R_hat` and `Q_hat` are Python floats. Projection accepts either `(m, 2)` observations or a single `(2,)` observation and preserves that shape. `sigma` is the known standard deviation of each noise coordinate.

`estimate_circle` computes the sample mean and the sum of the two unbiased sample variances, then subtracts `2*sigma**2`. Its return order is **center, radius, raw squared-radius estimate**. Negative `Q_hat` values are preserved for Part C reporting; only `R_hat` uses truncation at zero. The estimator accepts zero noise; the existing Bayes function requires positive noise.

## Projection conventions

Projection retains the observed direction relative to the supplied center and replaces the radial distance with the supplied radius. If `R == 0`, every output equals `c`. If an observation equals `c` and `R > 0`, its output is the fixed circle point `c + R*[1, 0]`. Noncentral points retain their direction without an arbitrary near-center threshold.

`plugin_projection` is the fitted projection method in the report. Both fitted projection and plug-in Bayes use the same parameter estimates obtained from noisy training data only. No method resets the random seed or estimates parameters from test points.

## Running

Merge the supplied folders into the existing repository. From the project root, with Python 3 and NumPy installed, run:

```powershell
python part_b/validation_projection.py
```

The check imports `part_b/bayes_estimator.py` from the existing repository. It checks the `n-1` correction, noise subtraction, translation/scaling properties, negative squared-radius estimates, inside/outside projection, single and empty inputs, the center convention, zero radius, invalid inputs, preservation of input arrays, and independent train/test integration with plug-in Bayes. The summaries identify Python and NumPy versions. These are implementation checks, not the 50-repetition Part C simulation study.

## Integration

Run the following from the project root, using independent noisy training and test arrays:

```python
from part_a.circle_estimator import estimate_circle
from part_b.projection import oracle_projection, plugin_projection
from part_b.bayes_estimator import plugin_bayes

c_hat, R_hat, Q_hat = estimate_circle(Y_train, sigma)
Z_projection_oracle = oracle_projection(Y_test, c_true, R_true)
Z_projection_fitted = plugin_projection(Y_test, c_hat, R_hat)
Z_bayes_fitted = plugin_bayes(Y_test, c_hat, R_hat, sigma)
```

True circle parameters are used only by the explicitly labelled oracle method. The Part C driver should set seed 5201 once, generate fresh training and paired clean/noisy test samples for each repetition, and apply every method to the same noisy test sample. The local data helper in the validation script is for debugging; shared Part C data generation can be integrated separately.

## AI assistance

AI assistance was used to draft these modules and their checks. Verification consists of exact examples, geometric invariance checks, boundary cases, and integration with the existing Bayes implementation, as documented in the validation script.

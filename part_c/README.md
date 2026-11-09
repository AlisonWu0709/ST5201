# Part C2: Geometric recovery metrics

`geometric_recovery.py` provides per-repetition metrics for one method's denoised outputs. It does not run the full Part C simulation or aggregate Monte Carlo uncertainty.

```python
from part_c.geometric_recovery import geometric_recovery_metrics

metrics = geometric_recovery_metrics(
    Z=Z_method,                  # (m, 2), method output for the common test set
    X_test_clean=X_test_clean,    # paired clean points, used only as reference
    c_true=c_true,                # (2,)
    R_true=R_true,
)
```

The returned `radial_error` is the mean squared difference between each output's distance to the true center and the true radius. `coverage_error` averages, over a fixed grid of 720 equally spaced true-circle points, each point's squared distance to its nearest method output. `clean_test_coverage_error` applies the same grid and formula to the paired clean test points as the assignment's reference baseline. The clean test points must not be used to fit or tune any method.

Call this function for each method within each repetition, always passing outputs and clean points from the same test sample. Save the three returned values as one repetition-level record per method and setting. For Part C3, calculate means and Monte Carlo standard errors across the 50 repetition-level records; do not pool individual test points across repetitions.

The coverage baseline is a reference, not a strict lower bound: it also depends on the finite number and angular spacing of test points. A small radial error alone does not establish recovery of the entire circle, since outputs can all lie close to the circle while covering only a small arc.

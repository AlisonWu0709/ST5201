> Stage 1 design note only. Formal experiments have not been run.

# Part D Option 3: Approximately Circular Shapes (Draft)

## Research Question

How does misspecifying an elliptical signal as circular affect pointwise denoising and geometric recovery, how does the effect change with ellipse deformation and training sample size, and does manifold fitting respond differently from circle-constrained rules?

## Pre-specified Conjectures

H1: As the minor-axis parameter `b` decreases, at least one of the two directional geometric errors of circle-model rules will increase, after holding `n`, noise, test size, and grid resolution fixed. H2: Because MF does not impose circular geometry, its relative geometric performance may improve under stronger deformation when local neighborhoods are sufficiently populated. H3: Increasing `n` may reduce estimation and local-fitting variability but will not necessarily remove systematic error caused by a circular model. H4: Method ordering may differ between pointwise denoising MSE and the two directional geometric errors. These are testable pre-experiment conjectures, not conclusions.

## Experimental Design

The PDF requires `b` in `{1, 0.9, 0.75}`, uniform angular sampling, and variation of both `b` and `n` at a fixed noise level. We choose `n` in `{100, 500, 2000}`, `sigma=0.15`, `m=500`, and 50 independent repetitions. The last four choices extend the PDF's open-investigation instruction using the common-study scale. A single NumPy generator is seeded once with 5201. Every repetition uses independent training and test draws, and every method receives the same realized samples.

## Data Generation

We generate `theta ~ Uniform(0,2*pi)`, `X=(cos(theta), b sin(theta))`, and `Y=X+epsilon`, with independent `epsilon ~ N(0,sigma^2 I_2)`. Uniform angle is retained exactly and is not replaced by uniform arc length.

## Methods

The required comparison comprises raw noisy observations, fitted-circle projection, the plug-in circle posterior mean, and MF. The circle posterior mean is misspecified when `b<1`. No ellipse parameters or clean test points are exposed to fitted methods. A true-ellipse posterior mean could be added as a clearly labelled optional oracle, but is not part of the required design and has not been implemented here.

## Evaluation Metrics

For a dense true-ellipse grid, output-to-ellipse error averages the nearest squared grid distance from each output and measures fidelity to the target set. Ellipse-to-output error averages the nearest squared output distance from each grid point and measures coverage. The two quantities are stored and reported separately. Pointwise denoising MSE is retained as an auxiliary correspondence-based loss. The formal run will include a grid-resolution sensitivity check.

## Planned Statistical Analysis

For every `(b,n,method,metric)` cell, we will report the mean and MCSE from 50 repetition-level values. Comparisons will use paired data realizations by construction. Plots will show changes with `b` and `n` with MCSE error bars. We will distinguish observed finite-design evidence from claims about other distributions or arbitrarily large samples.


# Recovering a Circle from Noisy Data

**Authors:** [STUDENT NAME], [GROUP MEMBER A], [GROUP MEMBER B]
**Module/date:** ST5201, [DATE]

## 1. Statistical targets

We distinguish three targets that need not favour the same estimator: recovery of the circle parameters, pointwise recovery of each latent clean point, and recovery of the support's geometry. Under the stated circle model, moment identities motivate estimators of the centre and noise-corrected radius. Projection enforces circular geometry, the posterior mean minimizes pointwise squared loss under the correct circle model and true parameters, and MF uses local training-sample geometry without imposing a circle.

## 2. Part A: circle estimation

Since `E(Y)=c` and `E||Y-c||^2=R^2+2 sigma^2`, the sample mean estimates the centre and the unbiased sample variance minus `2 sigma^2` estimates `R^2`. The divisor `n-1` corrects the sample-variance bias. Truncation at zero and the square root generally destroy unbiasedness, particularly for small samples or weak signal, although laws of large numbers give consistency. The naive radius that omits noise correction targets `sqrt(R^2+2 sigma^2)` rather than `R`.

## 3. Part B: recovery rules

Oracle projection uses the true circle; fitted projection substitutes the Part A estimates. Projection discards radial displacement while retaining direction from the centre. The posterior mean is approximated on a 512-point angular grid using stabilized Gaussian likelihood weights; a representative 1024-point check showed negligible quadrature differences. Oracle and plug-in rules are labelled separately. MF uses independent noisy training observations, `k=3`, `r0=r1=5 sigma/log10(n)` and `r2=10 sigma sqrt(log(1/sigma))/log10(n)`, with the prescribed fallback conventions.

## 4. Part C: common simulation study

We used `c=(0,0)`, `R=1`, `n in {100,500,2000}`, `sigma in {0.05,0.15,0.30}`, 50 repetitions and 500 independent test pairs per repetition. Seed 5201 was initialized once. All six methods shared each repetition's data. Means and MCSEs were calculated across the 50 repetition-level values.

Parameter error generally decreased with training size. Negative corrected squared-radius estimates were absent in this design. Pointwise and geometric rankings differed. For example, at `n=2000, sigma=0.30`, oracle posterior mean had denoising MSE 0.09560 (MCSE 0.00086), below oracle projection's 0.09851 (0.00095). Conversely, oracle projection had essentially zero radial error and lower coverage error, as it places outputs exactly on and around the true circle. Thus pointwise Bayes optimality does not imply optimal geometric recovery.

Across 225,000 MF queries, 1,438 fallbacks occurred (0.6391%), all from empty first-stage spherical neighbourhoods; no zero-direction or empty-cylinder fallbacks occurred. These events were concentrated in sparse, low-noise settings and are reported as implementation diagnostics rather than discarded queries.

Insert the compact C1 and C2/C3 tables from `report_tables`, plus the formal equal-axis representative plot and error-trend figures. Captions must state 50 repetitions and define MCSE.

## 5. Part D Option 3: approximate circles

### Question, target and conjecture

We ask how much is lost by imposing a circular shape when the clean support is the ellipse `(cos theta, b sin theta)`. We conjectured that decreasing `b` would increase the geometric error of fitted circle methods; increasing `n` might reduce estimation variability but need not remove structural misspecification. MF might adapt better geometrically without necessarily minimizing pointwise loss.

### Design and evidence

We varied `b in {1,0.9,0.75}` and `n in {100,500,2000}` at fixed `sigma=0.15`, with 50 repetitions and 500 test pairs. Angles remained uniform, which is not uniform arc-length sampling. Geometry was assessed in both directions against a 4096-point true-ellipse grid; the circle radial formula was not used.

At `n=2000`, the circle-based fitted methods performed well when `b=1` but their bidirectional geometric errors rose markedly at `b=0.75`. Fitted projection's output-to-ellipse error increased from 0.000271 (MCSE 0.000037) to 0.007846 (0.000053), and its ellipse-to-output error rose from 0.000355 (0.000038) to 0.008117 (0.000028). MF at `b=0.75` had substantially smaller corresponding geometric errors, 0.001477 (0.000053) and 0.000527 (0.000012), and also the lowest denoising MSE among the four methods at this setting (0.02618, MCSE 0.00022). These are finite-design observations rather than universal dominance claims.

The supplementary equal-axis `b=0.75` plot illustrates the misspecification but is not aggregate performance evidence. A limitation is that we considered one noise level and centred axis-aligned ellipses, and did not include the optional correctly specified true-ellipse posterior mean.

### Concise answer

More training data stabilized estimation, but it did not by itself remove the geometric cost of imposing a circle when the support was elliptical. The cost grew as `b` decreased and was visible in both directional geometry metrics. This was not apparent from Part C, where the circle model was correctly specified.

## 6. Final reflection (148 words)

Before choosing an estimator, one must clarify what “recover a circle” means. If the target is the centre and radius, parameter bias and MSE are primary, and noise correction matters. If the target is each latent clean point, the relevant loss may be pointwise squared error; under a correct circle model with known parameters, the posterior mean is optimal for that loss but need not lie on the circle. If the target is geometric support, distances to the shape and coverage are more informative, and projection may perform well despite a different pointwise ranking. One must also clarify which quantities are known, how training and query samples are separated, the noise level, sample size, angular sampling mechanism, and whether the circle assumption is credible. Our ellipse study shows that more data cannot automatically repair structural model misspecification. Therefore no estimator is uniformly “best”: the answer depends on the scientific target, loss function, available oracle information, and robustness required when the assumed geometry is only approximate.

## Contribution and AI disclosure

Insert the verified contribution statement and reviewed AI-use disclosure. Add references for the supplied MF method and any other cited sources.

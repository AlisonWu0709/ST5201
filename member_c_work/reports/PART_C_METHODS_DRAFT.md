> Stage 1 methods note only; no formal numerical evidence.

# Part C2–C3 Methods and Statistical Analysis (Draft)

For every repetition, all denoising rules will be evaluated on the same independent test sample, so differences between methods were not confounded by different test realizations. The radial error was the mean squared departure of each output's radius from the true radius. The coverage error was the average, over 720 equally spaced true-circle grid points, of the squared distance to the nearest output. These criteria measure different geometric properties: a point set concentrated on a short arc can have nearly zero radial error but poor coverage. We will also evaluate the clean test points with the coverage criterion to quantify finite-sample spacing. This reference is not a strict lower bound because an estimator could produce points that are more regularly spaced than a random clean sample.

Monte Carlo simulation approximates repeated-sampling performance under the specified model. For each metric and setting, we will report the mean across the 50 repetition-level values and the Monte Carlo standard error, \(s/\sqrt{50}\), where \(s\) is the sample standard deviation with divisor 49. Test points within one repetition are not treated as independent Monte Carlo replications. Reporting MCSE indicates the simulation uncertainty in each estimated performance mean. Pointwise denoising MSE measures correspondence to each latent clean point, whereas radial and coverage errors measure recovery of the underlying set; consequently, rankings under these losses need not agree.

All geometric scatterplots use equal scaling on both axes. Error plots will show means with MCSE error bars across sample sizes and noise levels. Numerical rankings and interpretations remain pending until the common result file passes the pairing and completeness checks.


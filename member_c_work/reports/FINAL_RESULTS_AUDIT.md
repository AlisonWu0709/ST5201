# Final Results Audit

## Scope and authority

The assignment PDF was treated as authoritative. This audit used the formal repetition-level CSV files rather than screenshots or prior chat summaries. No formal output was modified or rerun.

## Git and MF audit

- Working branch at audit start: `part-c2-c3-part-d`, clean at `84b3b22`.
- Formal runs record commit `84b3b226be0ad25060028115bcc2e867fc875062`, `dirty=false`.
- The teammate correction on `origin/main` is commit `4959577`.
- Its executable formula is `r2 = 10*sigma*sqrt(log(1/sigma))/log10(n)`, identical to commit `995c669` used by the formal runs. The only executable difference is whitespace.
- Interfaces, fallback conventions and `mf_weighted.py` are unchanged. Therefore the teammate correction does not invalidate or require rerunning the formal results.
- `origin/main` also contains `59588d6`, an independent C2 metric module. Its definitions agree with the integrated framework, but it was not merged during this audit.

## Part C formal run

- Directory: `E:\nus classes\st5201\ST5201-formal-results\formal\part_c_run01`
- Run ID: `5bd5f7b4-e142-4237-8b35-1a3598db8d67`
- Config hash: `6140166e467ebdef1203b565987abff60772d8823611cf2fccdc003d36f5af1b`
- Design: `n={100,500,2000}`, `sigma={0.05,0.15,0.30}`, `m=500`, 50 repetitions, seed 5201, circle grid 720.
- Methods: raw, oracle projection, fitted projection, oracle posterior mean, plug-in posterior mean and MF.
- Rows: 2700/2700; dataset-repetition blocks: 450/450; duplicates: 0.
- Every block contains all six methods and one shared dataset ID.
- Run identity, config hash and `FORMAL` labels are consistent.
- All required performance metrics are finite and nonnegative.
- Independently recomputed 216 summary rows match saved mean, sample SD and MCSE exactly (maximum absolute difference 0).
- Independently recomputed 36 parameter-summary rows also match exactly.
- MF diagnostics: 450 repetitions, 225,000 queries, 1,438 empty-sphere fallbacks, zero zero-direction and zero empty-cylinder fallbacks; overall rate 0.00639111 (0.6391%).

**Decision:** suitable for the report; no rerun indicated.

## Part D formal run

- Directory: `E:\nus classes\st5201\ST5201-formal-results\formal\part_d_run01`
- Run ID: `0d19358e-e90e-49ee-83d6-9851c8c0d805`
- Config hash: `111d684db94a2c57d9228e081f54045b8e6af655542495f6752d223ad6c50633`
- Design: `n={100,500,2000}`, `b={1,0.9,0.75}`, fixed `sigma=0.15`, `m=500`, 50 repetitions, seed 5201, ellipse grid 4096, uniform-angle sampling.
- Methods: raw, fitted projection, plug-in posterior mean and MF.
- Rows: 1800/1800; dataset-repetition blocks: 450/450; duplicates: 0.
- Every block contains all four methods and one shared dataset ID.
- Run identity, config hash and `FORMAL` labels are consistent.
- All three required metrics are finite and nonnegative.
- Independently recomputed 108 summary rows match saved mean, sample SD and MCSE exactly (maximum absolute difference 0).
- Code inspection confirms geometry is evaluated by squared nearest-neighbour distances in both directions against a dense true-ellipse grid; the circle radial formula is not used.

**Decision:** suitable for the report; no rerun indicated.

## Supplementary Part D figure

The target `(b,n,sigma,repetition)=(0.75,2000,0.15,0)` was reconstructed by replaying the formal single RNG stream. Its SHA-256 dataset ID exactly matched all four formal method rows: `da3b85dc108c9a5011d54f94602d5a4b4f004e6c746c7d8ad802089900b30fda`. The resulting equal-axis figure is a supplementary visualization, not a new experiment, and does not overwrite formal outputs.

## Remaining limitations

- Part D uses one noise level and axis-aligned centred ellipses only.
- A correctly specified true-ellipse posterior mean was optional and was not included.
- The supplementary scatterplot is one prespecified repetition and must not be treated as aggregate evidence.
- Final prose, page count and author/contribution details require student review.

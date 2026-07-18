# Held-out test of the one-round selection-response law on judge-ablation runs

**Figure:** `ablation-unit-law-heldout.svg`

The project's one-round law was fit on an earlier program and then tested,
with no refitting, on 14 supplier-removed em750 runs (3 judge conditions,
seeds 41-46) that postdate the fit. Every axis is in units of the
generated-candidate self-report score (the judge's 0-1 rating of a freshly
generated answer). **Panel A (factorization)** plots, for each round with a
defined selection pressure, the predicted per-round gap `rho x sigma`
(selection-response coefficient times candidate-score spread) against the
observed kept-minus-pool gap (mean score of kept answers minus the full
pool mean); 40 points. The dashed line is the *frozen* relationship
`gap = 0.96 * rho * sigma`, drawn as fixed, not refit. A pooled refit would
give slope 1.121 (Pearson r = 0.894, n = 40); per condition, candid-judge +
self-report 1.202 (r = 0.947), neutral-judge + self-report 0.994 (r = 0.850),
and candid-judge + base-model 0.710 (r = 0.522, n = 7). The base-judge points
are the weak spot: with only 7 rounds they scatter (r = 0.52) and drag the
refit slope down. **Panel B (movement)** plots the realized gap at round r
against the next-round change in the own-pool mean (the drift), 42
round-to-round steps including the zero-pressure rounds. The dashed line is
the frozen `drift = 0.833 * gap`. Held-out, the frozen constant gives mean
absolute error 0.019, versus 0.070 for a zero-drift (persistence) baseline
that assumes the pool just stays put -- nearly a 4x reduction; the pooled
refit slope is 0.946 (r = 0.965, n = 42).

**Data source:** `experiments/ablation_unit_law.json` -- `rho_trajectories`
holds the per-run round arrays (`rho`, `sigma`, `gap`, `pool_mean`); the
`factorization`, `movement`, and `frozen_constants` blocks supply the summary
stats and the frozen constants C = 0.96, K = 0.833, and every annotated number
is read from that file. Scorer/analysis conventions follow
`analysis_spread_util_unified.py`. The frozen constants themselves were
originally fit on `simple_model_rollout.json` / `spread_util_unified.json`.
Regenerate with `python3 ablation-unit-law-heldout.py` from this directory
(stdlib only).

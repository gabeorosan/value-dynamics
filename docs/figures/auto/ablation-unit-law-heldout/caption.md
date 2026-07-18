# Held-out test of the one-round selection-response law across the full judge factorial

**Figure:** `ablation-unit-law-heldout.svg`

The project's one-round law was fit on an earlier program and then tested, with
no refitting, on the **full 2x2 judge factorial**: 24 supplier-removed em750
self-loop runs spanning judge prompt (candid / neutral) x judge model (self /
base), seeds 41-46, all postdating the fit. Both panels plot the realized
quantity (y) against the *frozen prediction* (x), so the dashed reference line
is the identity `y = x` -- a point on the line means the frozen law hit exactly
with no free parameter left to tune. **Panel 1 (movement law)** plots the
frozen prediction `0.833 x (kept-minus-pool gap)` against the actual next-round
change in the own-pool mean (the drift), 72 round-to-round steps (18 in each of
the four cells). The kept-minus-pool gap is the mean judge score of the answers
kept at a round minus the full pool mean; the drift is next round's pool mean
minus this round's. Held-out, the frozen constant K = 0.833 gives pooled mean
absolute error 0.023, versus 0.070 for a zero-drift ("assume the pool stays
put") baseline -- about a 3x reduction; the pooled refit slope is 0.995 (Pearson
r = 0.953, n = 72). Critically, the fit is judge-configuration-independent:
per-cell correlation is r >= 0.92 in every cell (candid+self 0.988,
neutral+self 0.932, candid+base 0.923, neutral+base 0.922). **Panel 2
(factorization)** plots the frozen prediction `0.96 x rho x sigma`
(selection-response coefficient rho times candidate-score spread sigma) against
the observed kept-minus-pool gap, 77 rounds with a defined rho. The frozen
constant C = 0.96 stays unbiased on held-out data (pooled refit slope 1.005, r =
0.852, n = 77). The self-judge cells are tight (candid+self r = 0.947,
neutral+self r = 0.850) and the base-judge cells scatter more (candid+base r =
0.647, neutral+base r = 0.701), but the base-judge predictions stay centered on
the identity -- looser, not biased. Refit slopes are shown as diagnostics only
and are never used to draw the reference lines.

**Data source:** `experiments/ablation_unit_law.json` (produced by
`scripts/analysis_ablation_unit_law.py`) -- `rho_trajectories` holds the per-run
round arrays (`rho`, `sigma`, `gap`, `pool_mean`); the `factorization`,
`movement`, and `frozen_constants` blocks supply the summary stats and the
frozen constants C = 0.96, K = 0.833. Every annotated number is read from that
file at render time. Scorer/analysis conventions follow
`analysis_spread_util_unified.py`; the frozen constants were originally fit on
`simple_model_rollout.json` / `spread_util_unified.json`. Regenerate with
`python3 ablation-unit-law-heldout.py` from this directory (stdlib only).

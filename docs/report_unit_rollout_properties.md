# The unit-recurrence rollouts reproduce the same path properties as the fitted model

*2026-07-16. Analysis: `scripts/analysis_unit_rollout_properties.py` →
`experiments/unit_rollout_properties.json`. Inputs: the stored per-run unit
trajectories in `experiments/selection_response_predictor.json` and the fitted
frozen-mean-SD trajectories plus observed paths in
`experiments/spread_rollout_bakeoff.json`.*

## Why this analysis exists

The rollout property audit (`report_rollout_property_fidelity.md`) and the
trajectory noise bakeoff (`report_trajectory_adjustment_bakeoff.md`) scored
only the **fitted** cores. The selection-response audit then adopted a
**zero-fitted-parameter unit recurrence** (`m_next = clip((1−u)·m +
u·supplier + ρσ)`, next value = kept-mean identity) on endpoint evidence
(MAE 0.118 vs 0.127 on the 36 matched selection-driven runs). Its rolled
trajectories existed in the result JSON but had never been property-scored —
so "the paths behave like the fitted model's" was an assumption. This closes
that gap.

## Result: property-equivalent on the matched runs

Scored with exactly the fitted-core property recipes (endpoint class: low
rail ≤ 0.15, high rail ≥ 0.85, else interior; sign reversals among
round-to-round moves ≥ 0.025; direction on runs with |net change| ≥ 0.15), on
the 32 selection-driven runs where the stored unit rollout starts at round 1
(the four glued grid entries are excluded for sequential-rollout ambiguity;
judge-swap runs are excluded because the stored unit swap rollouts are
post-swap conditional forecasts, so their full-path shape is not comparable
from round 1):

| property | observed | fitted frozen SD | unit recurrence |
|---|---:|---:|---:|
| mean total variation | 0.586 | 0.460 | 0.489 |
| mean sign reversals | 0.69 | 0.03 | 0.03 |
| endpoint mean | 0.507 | 0.538 | 0.530 |
| endpoint SD | 0.354 | 0.384 | 0.406 |
| endpoint MAE | — | 0.126 | 0.130 |
| all-round MAE | — | 0.110 | 0.106 |
| all-round value R² | — | 0.800 | 0.796 |
| large-move directions | — | 27/27 | 27/27 |
| rail endpoint recall | — | 14/15 | 14/15 |
| endpoint class accuracy | — | 26/32 | 25/32 |

(The variation/reversal values differ from the published 45-run figures
(0.648/0.458, 1.20/0.16) because this matched set is 32 selection-driven runs
and paths here include the round-1 starting value; both models are scored on
identical runs and recipes, which is the comparison that matters.)

The two deterministic cores are interchangeable on every property: identical
direction hits and rail recall, all-round MAE within 0.004, trajectory R²
within 0.004, and both are conditional means that under-produce path
roughness by the same amount. Nothing in the fitted model's path behavior is
bought by its fitted constants.

## Endpoint-only comparison on the full matched 45

The path comparison above needs round-1-aligned trajectories, which excludes
the glued entries and the judge swaps. Endpoints need no alignment, so the
full matched set (36 selection-driven including the glued entries + 9 judge
swaps, where fitted = the refreshed-at-swap rollout endpoint and unit = the
stored post-swap conditional endpoint) can be compared directly:

| endpoint-only, 45 runs | fitted frozen SD | unit recurrence |
|---|---:|---:|
| endpoint MAE | 0.1373 | **0.1365** |
| rail endpoint recall | 19/24 | **21/24** |
| endpoint class accuracy | 35/45 | 35/45 |
| large-move direction (from round-1 value) | 36/38 | 36/38 |

The unit recurrence recovers two more of the 24 observed rail endpoints than
the fitted model, with everything else equal.

**Direction-convention reconciliation.** The selection-response JSON publishes
37/38 large directions for the unit model; the fitted model's published number
is 36/38. Those use different conventions: the fitted 36/38 (and this table)
measure every run from its round-1 value; the 37/38 measures judge-swap runs
from the swap boundary, where the stored unit rollout starts. Under the
matched round-1 convention **both models score 36/38**, and the unit model's
two misses are press_d1 seed 1 and press_d2 seed 1 — exactly the documented
post-refresh agreement-sign-reversal runs. Do not quote 37/38 next to the
fitted 36/38 as if computed the same way.

## What has and has not been run with the updated model

- **Run and endpoint-analyzed:** yes — the unit recurrence was rolled through
  all 70 per-run records (LOCO boundary states, boundary refresh at swaps) in
  `analysis_selection_response_predictor.py`, endpoint-scored there
  (0.118 / 0.210 / 0.1365, 37/38 directions), horizon-scored in
  `analysis_model_ladder_horizon.py` (flat in horizon: 0.100 → 0.130), and
  self-weak-scored (endpoint 0.211 vs no-change 0.215 — the same
  scope boundary as the fitted model).
- **Path-property-analyzed:** now yes (this analysis) — property-equivalent.
- **Not yet re-run on the unit core:** the staged stochastic layer. The
  quoted CRPS 0.095 / 84% coverage numbers were produced with the fitted
  deterministic core inside `analysis_trajectory_adjustments.py`. The noise
  innovations attach to stage residuals of the same update law, and the two
  cores' deterministic paths differ by ≤ 0.004 all-round MAE, so material
  change is unlikely — but that is an expectation, not a result. If the
  stochastic layer is ever quoted specifically for the unit model, re-run it
  with the unit core first.

No figure spawn: this is an equivalence check whose product is one table; it
supplies a caption line for the existing rollout figures rather than a new
relationship to draw.

# A simple model from the two gap factors, tested on the interventions

*2026-07-15, general (writeup) thread. Committed scorer:
`scripts/analysis_simple_model_rollout.py` →
`experiments/simple_model_rollout.json` (input:
`experiments/spread_util_unified.json`). 67 modelable runs (a run needs a
round-1 pool measurement and ≥2 rounds; random arms have no judge scores and
are excluded).*

The writeup's spine is: the selection gap predicts movement → the gap is
value spread × utilization → spread and utilization each follow simple
dynamics. This analysis asks the natural next question with fresh eyes: if
you take those three sentences literally as a model, measure each run's
**first round only**, and roll forward, what do you get — especially on the
intervention cells (injection, invasion, judging-format changes,
self-judging), which is where a model like this would earn its keep?

## The model

Inputs, all measured on the run's round-1 pool: starting value v₀, spread
σ₁, utilization ρ₁, and (mixed pools) the supplier level s = the mean value
of the co-generator's round-1 candidates. Dynamics:

- pool mean: pₜ = vₜ (self-only) or ½vₜ + ½s (mixed);
- kept mean: pₜ + 0.96·ρ₁·σₜ (the factorization, ρ held at its round-1
  value — utilization is ~a judge-cell property);
- movement: vₜ₊₁ = vₜ + K·(keptₜ − vₜ), clipped to [0, 1];
- spread: σₜ₊₁ = a + b·σₜ (self-only) or σₜ = g·|vₜ − s| + d (mixed —
  spread is the source separation).

K, (a, b), (g, d) are two-parameter fits on the unified per-round records,
refit **leave-one-run-out** so a predicted run never touches its own fit
(fitted values ≈ K 0.79, self-only spread 0.88·σ + 0.02, mixed spread
0.36·|v−s| + 0.20).

## Results — by regime, because this is a selection-force model

The model only has a mechanism where a judge selects on the value axis, so
the honest evaluation splits runs by regime (assigned from the judge and pool
alone, not from the outcome):

| regime | what it is | n | endpoint MAE | persistence MAE |
|---|---|---|---|---|
| **selection-driven** | intervention + a gripping self-judge | 36 | **0.106** | 0.431 |
| — intervention | mixed pools (injection / invasion / rescue / erosion) | 24 | 0.105 | 0.450 |
| — self-force | self-only oracle, cautious copy, candid-prompt self-judge | 12 | 0.109 | 0.393 |
| self-weak | self-only base / frozen-copy / self-reference (ρ ≈ 0) | 22 | 0.197 | 0.215 |
| judge-swap (EXCLUDED) | fan-then-press schedule — judge changes mid-run | 9 | 0.399 | 0.361 |

Where a judge selects on the axis, first-round measurement cuts endpoint
error to about a quarter of the no-change baseline (0.106 vs 0.431). Where it
does not — the self-weak runs, ρ ≈ 0 — the model correctly predicts almost no
selection-driven movement, and the value's observed wandering (the K1
self-judge fan, the base-judge runaways) is the training-instability
mechanism documented in `report_runaway_decomposition.md`, which no
selection-based model can forecast; there it barely beats persistence
(0.197 vs 0.215). The judge-schedule cells are excluded from every model
claim: the judge is swapped mid-run, so a model that fixes utilization at its
round-1 value cannot apply, and it is duly worse than persistence there
(0.399 vs 0.361).

Direction hit-rate on the 51 runs that moved ≥ 0.15: **40/51 (78%)**.

The intervention cells, by name (predicted → true endpoint):

- **invasions** (railed peer supplies half the pool): predicted 1.000 in all
  8; true 0.740–1.000 (6 of 8 within 0.06);
- **injection reopening** (Qwen 0.625 stall + base candidates, oracle):
  predicted 0.000, true 0.000, both seeds;
- **self-judge erosion** (insecure-code organism judging duels, base text
  present, ρ₁ = −0.24 measured on round 1): predicted 0.45 → 0.10, true
  0.45 → 0.00, both seeds — direction and most of the magnitude from one
  round of measurement;
- **rescues**: right shape, conservative magnitude — cautious-judge duels
  predicted 0.66/0.84 vs true 0.54/0.75; base-judge duels under-predict the
  descent (0.73/0.87 vs 0.54/0.55); oracle-on-mixed overshoots it
  (0.06/0.27 vs 0.34/0.48). Errors 0.09–0.32, against a persistence error
  of 0.34 on these cells.

## The misses are the interpretable ones

The worst endpoint misses are exactly the runs that violate the model's one
strong assumption — that utilization stays at its round-1 value:

1. **Judge-schedule cells** (press_d1/d2/d3, press_to_base; endpoint MAE
   0.399): the experimenter swaps the judge mid-run, so ρ₁ describes the
   wrong judge for later rounds. Predictable failure; re-measuring ρ at the
   swap would fix it by construction.
2. **The bloom run** (OLMo frozen-base seed 5, err 0.56): round-1 state
   (ρ₁ = 0.012) was indistinguishable from settled runs; its alignment rose
   mid-run and the run railed at 0.802 while the model predicted flat 0.24.
   One of two runaways in that grid; the other (seed 2) had visible round-1
   alignment and is predicted fine.
3. **Largest per-round residuals** of the raw movement association are big
   drifts at near-zero pull — Qwen self-aware-grid and one
   base-judge-opposition run — i.e. movement without selection force, the
   training-instability mechanism already documented in
   `report_runaway_decomposition.md`.

## Caveats

Descriptive model, post-hoc structure: the equations were chosen after
seeing the unified accounting (the same data these runs come from), and the
factorization constant 0.96 is a pooled estimate, so this is an internal
consistency demonstration with LORO scalar fits — not a preregistered
forecast. The round-1 measurement uses that round's logged judge scores
(exactly what a practitioner could compute before training on the round).
Supplier level uses round-1 co-generator candidates. ρ fixed within a run is
knowingly wrong for schedule cells and blooms — that is the point of
reporting them as named failures. 67 runs, 2–8 rounds each, two families,
three value coordinates.

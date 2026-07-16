# One selection-response model at three forecast times

*Updated 2026-07-16. Primary analysis:
`scripts/analysis_selection_response_predictor.py` →
`experiments/selection_response_predictor.json`. Supporting fitted bakeoffs:
`scripts/analysis_value_predictor_bakeoff.py` and
`scripts/analysis_spread_rollout_bakeoff.py`.*

## The model

The selector converts offered variation into a shifted training set:

`selector gap = spread × value-axis selection intensity`.

Once the retained set is known, this is exact: the realized intensity is
`(kept mean − pool mean)/spread`, and the gap is the Price selection
differential. Before selection, use judge/value agreement as its compact proxy:

`predicted kept mean = pool mean + agreement × spread`.

The empirical full-data calibration is
`gap = −0.002 + 0.958197·agreement·spread`; rounding the intercept to zero and
the slope to one has negligible predictive cost. The coefficient one is a
parsimonious approximation, not a top-2-of-6 normal-theory constant. The scale
audit and literature connections are in
`docs/report_predictive_model_literature.md`.

## After selection: use the kept mean

Once the training examples have been selected, use

`next value = kept candidate value mean`.

Equivalently, `Δvalue = kept mean − current value`. This parameter-free rule
has leave-one-condition-out MAE **0.081**, RMSE 0.116, and R² 0.613 over all
340 rounds, versus MAE 0.128 for no change. It automatically includes judge
selection, supplier shift, and generator/readout mismatch.

A fitted partial update,
`Δvalue = −0.007 + 0.833(kept mean − current value)`, slightly improves squared
error but not MAE. Keep it as a calibration check rather than the headline
equation.

## Before selection: use agreement × spread

Before the retained set is known:

`predicted kept mean = pool mean + ρσ`,

where `σ` is mean within-prompt population SD over the whole offered pool and
`ρ` is the Pearson correlation between logged judge score and candidate value
on that pool. On 290 agreement-scored rounds, this unit proxy has MAE **0.0902**,
RMSE 0.1190, and R² 0.631 for next-round value. The fitted two-stage LOCO model
scores MAE 0.0891, RMSE 0.1172, and R² 0.642.

For the selector gap alone, the unit proxy has R² **0.810** and MAE **0.0421**.
A more elaborate per-prompt formula using the realized distribution of logged
judge scores is worse (R² 0.650, MAE 0.0444), because those scalar scores do
not always fully specify the actual selection rule. If future logging makes the
retained set a deterministic function of scalar scores, compute that set and
its value mean directly instead of estimating it through `ρσ`.

## Endpoint: freeze the boundary gap and refresh at changes

At the first measured pool, record host mean `m`, offered spread `σ`, agreement
`ρ`, and, for mixed pools, supplier mean `s` and supplier fraction `a`. Set
`c=ρσ` and iterate

`m_next = clip((1−a)m + as + c, 0, 1)`.

Set predicted behavioral value to the same next mean. For a self-only pool,
`a=0`. For a mixed pool without clipping, the fixed point is `s+c/a`.

| slice | unit agreement×spread | fitted frozen-SD loop |
|---|---:|---:|
| matched selection-driven runs (36) | **0.118 MAE** | 0.127 |
| judge swaps, refreshed at swap (9) | 0.210 | **0.179** |
| combined matched set (45) | **0.1365** | 0.1373 |

The unit recurrence gets **37/38** large endpoint directions. Freezing the
observed first selector gap instead scores 0.112 on the ordinary selection
runs but 0.311 on swaps, for combined MAE 0.152; `ρσ` is the better shared
boundary estimate.

When judge, judging format, or pool-generation policy changes, remeasure the
complete boundary state and restart. Agreement is local to the candidate
distribution, not a permanent judge trait.

## Outside the mean equation

- Binary `q(1−q)` geometry predicts changes in later spread, but propagating it
  does not improve endpoints. Keep it as the explanation of how the next pool
  regenerates variation.
- Weak-selection Qwen fans and OLMo blooms move without a reliable selection
  differential. Treat them as training-instability processes rather than
  missing terms in this selection predictor.
- For probabilistic forecasts, use zero-mean innovations around the conditional
  mean. The point predictor should remain deterministic.

The unit simplification was chosen retrospectively. Its combined benchmark is
competitive, but prospective validation is still required.

# Figure brief: closed-loop spread rollout bakeoff

Claude: please make this a visible two-panel figure in the spread/model
section. Source values from `experiments/spread_rollout_bakeoff.json`,
`experiments/rollout_property_fidelity.json`, and
`experiments/trajectory_adjustment_bakeoff.json`; do not manually transcribe
from prose.

## Panel A — Does the closed loop predict unseen conditions?

Grouped bars, endpoint MAE, leave-one-condition-out:

- selection-driven: frozen mean SD 0.127; no-change 0.431;
- mixed interventions: 0.112; no-change 0.450;
- gripping self-only judges: 0.157; no-change 0.393;
- weak self-only selection: 0.205; no-change 0.215;
- judge swaps from original round 1: 0.392; no-change 0.361.

Use descriptive regime labels, not internal run codes. Caption should say the
model sees the held-out run's first pool only. Visually mark judge swaps as an
intervention-time state change rather than blending them into the headline
average.

**Make the judge-swap refresh visible in Panel A.** Add a third, distinct bar
or an adjacent inset for the nine swap runs. At the first pool scored by the
new judge, the simulator remeasures value, generated-pool mean, spread, and
agreement, then reads no later state. Under LOCO:

- frozen mean SD: 0.404 from original round 1 → **0.179 refreshed**;
- holding the observed swap-time value fixed: 0.309;
- refreshed frozen mean SD gets 6/7 post-swap directions for movements ≥0.15.

Source these from `judge_swap_refresh.leave_one_condition_out` in the JSON.
Label this “restart at judge change,” not an oracle forecast. A small footnote
should say that it observes one pool under the replacement judge.

## Panel B — What rollout properties are reproduced?

Do not show the spread-definition bakeoff in the main figure. Mean SD and mean
range produce effectively identical forecasts (mean endpoint difference
0.0066; same endpoint class 66/67), so the writeup now uses mean SD for both
decomposition and endpoint prediction.

Instead compare observed rollouts with:

1. frozen-SD conditional-mean paths;
2. staged stochastic paths: selector-gap and generator-mean residuals,
   zero-mean agreement innovation around persistence, and finite-battery
   observation noise that is not fed back.

For the 45 selection-driven + judge-swap runs, show:

| property | observed | deterministic SD | staged stochastic model |
|---|---:|---:|---:|
| mean total variation | 0.648 | 0.458 | 0.678 |
| mean sign reversals | 1.20 | 0.16 | 1.36 |
| endpoint CRPS | — | 0.137 | 0.095 |
| nominal 80% endpoint coverage | — | 0.02 | 0.84 |

Also annotate the coarse deterministic fidelity: 36/38 large-movement
directions, 19/24 observed rail endpoints, endpoint mean 0.572 predicted vs
0.541 observed, endpoint SD 0.360 vs 0.370. The visual message is: the simple
model predicts the coarse endpoint behavior, while separately located
innovations restore realistic measured paths and useful endpoint uncertainty.
Visibly label observation noise as “battery readout only — does not feed back.”
Do not draw a latent value-process kick; the ablation worsens mean accuracy and
overproduces variation.

Do not show the candidate risk-feedback equation. Although its coefficient is
positive across folds, it does not improve held-out one-step prediction of
next agreement and is rejected as post-hoc compensation.

## Required correction to the existing agreement figure

Revise `auto/two-clocks-spread-util` and any selection-loop subtitle that calls
agreement a “fixed property.” The supported wording is:

> Agreement is strongly organized by judge × format × pool (82% between-cell
> variance), but later within-run changes dominate the remaining endpoint
> forecast error.

Keep the descriptive cell means. Add the rollout diagnostic 0.139 closed →
0.115 with observed later agreement, versus 0.139 with observed later spread.
Do not depict spread as dynamic and agreement as literally stationary.

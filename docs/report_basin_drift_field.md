# No robust saddle signal; linear drift-field equilibria remain exploratory

Closes Lit&planning → Analysis item 1 (docs/plan_recovered_threads.md §1): refit
the 1-D drift field Δx = f(x) per judge condition on the pooled basin ensembles
and answer the saddle question. No GPU; the JSONs store the risk coordinate per
round. Data: `basin_anchor` + `_ext` + `lightning_23_31` + `lightning_15_23`
(24 self-judge, 16 frozen-judge Qwen rollouts, 6 rounds) and `basin_second_model`
(OLMo, 8 rollouts).

## Method

For each judge condition, pool all round transitions (x_t, Δx = x_{t+1} − x_t)
across seeds and fit Δx as a function of the current risk coordinate x. A linear
fit Δx = a·x + b gives a descriptive mean-reversion slope and zero crossing
x* = −b/a. A cubic fit tests for **bistability** —
the deterministic signature of true "basins" would be two stable roots with an
unstable saddle between them. CIs by cluster bootstrap over rollouts.

## Result 1: no robust bistability; a true single attractor is not identified

| condition | slope a [95% CI] | descriptive zero crossing x* | cubic fit |
|---|---|---|---|
| Qwen self-judge | −0.206 [−0.369, −0.094] | **0.352** | one fitted root; cubic R² 0.09 vs linear 0.05 |
| Qwen frozen-judge | −0.192 [−0.295, −0.131] | **0.118** | one fitted root |
| OLMo self-judge | −0.398 | 1.049 (rail) | extrapolated crossing above ceiling |
| OLMo frozen-judge | −0.414 | 1.035 (rail) | extrapolated crossing above ceiling |

The cubic fit barely improves on the linear one, and a bootstrap over rollouts
finds ≥2 stable interior roots (the bistability signature) in only **19%** of
resamples — i.e. no reliable saddle. So the headline "self-judge → divergent
basins" is not supported as deterministic bistability. But a negative pooled
slope on a bounded noisy coordinate can arise from measurement error and
regression to the mean; these fits reject a robust saddle more strongly than
they establish a real single attractor.

The fitted zero crossing differs by judge (about 0.35 self versus 0.12 frozen),
but it should be called a **descriptive AR(1) equilibrium**, not a demonstrated
attractor set by the judge. OLMo's extrapolated roots above 1 are boundary/
saturation diagnostics, not physical fixed points.

## Result 2: the divergence is stochastic, not structural — and that distinguishes the two judges

The restoring eigenvalues are statistically indistinguishable between judges
(CIs overlap heavily). What differs is the balance of noise against restoring:

| condition | per-step noise sd | AR(1) equilibrium spread | observed final spread |
|---|---|---|---|
| self-judge | 0.139 | 0.229 | **0.223** |
| frozen-judge | 0.116 | 0.198 | **0.119** |

The self-judge's final spread is numerically close to the fitted stationary
spread. That is consistency with a weak noisy process, not evidence that
stationarity was reached. Likewise, the frozen final spread being below the
stationary extrapolation does not prove active compression; finite horizon,
starting distribution, boundedness, and measurement noise remain alternatives.

Earlier rounds increasingly correlate with the final recorded state, but the
terminal correlation of 1.0 is tautological and the pattern alone does not
distinguish path dependence from accumulated measurement/process noise.

## Interpretation and caveats

The defensible conclusion is narrower: no robust saddle/bistability appears in
these pooled trajectories, and judge conditions have different descriptive
conditional drifts and spreads. Whether this is a genuine low-dimensional
restoring field, measurement-induced regression, or hidden-state dynamics is
not resolved.

Caveat worth a follow-up: a single well with *state-dependent* (multiplicative)
noise can also widen spread without a deterministic saddle, and R² of the drift
fits is low (~0.05–0.09) — round-to-round motion is mostly stochastic, so these
zero crossings are the faint mean of a noisy fit, not a stiff well. The data do
not support deterministic bistability; whether the residual noise
is state-dependent is the natural next cut, and it needs per-round logits the
current JSONs don't store — so it is a new-run question, not a re-analysis one.

For Lit&planning: the saddle hypothesis is **not supported**. If the dedicated
drift-mapping experiment is still wanted, its value is now measuring the *noise
structure* (is it multiplicative?), not locating a saddle that isn't there.

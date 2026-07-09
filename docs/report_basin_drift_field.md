# The divergent basins are not a saddle: a weak single attractor whose location the judge sets, plus judge-dependent noise

Closes Lit&planning → Analysis item 1 (docs/plan_recovered_threads.md §1): refit
the 1-D drift field Δx = f(x) per judge condition on the pooled basin ensembles
and answer the saddle question. No GPU; the JSONs store the risk coordinate per
round. Data: `basin_anchor` + `_ext` + `lightning_23_31` + `lightning_15_23`
(24 self-judge, 16 frozen-judge Qwen rollouts, 6 rounds) and `basin_second_model`
(OLMo, 8 rollouts).

## Method

For each judge condition, pool all round transitions (x_t, Δx = x_{t+1} − x_t)
across seeds and fit Δx as a function of the current risk coordinate x. A linear
fit Δx = a·x + b gives the restoring rate (eigenvalue a; a < 0 = stable
attractor) and fixed point x* = −b/a. A cubic fit tests for **bistability** —
the deterministic signature of true "basins" would be two stable roots with an
unstable saddle between them. CIs by cluster bootstrap over rollouts.

## Result 1: both judges are a single stable attractor — no saddle, no robust bistability

| condition | eigenvalue a [95% CI] | fixed point x* | cubic verdict |
|---|---|---|---|
| Qwen self-judge | −0.206 [−0.369, −0.094] | **0.352** | single stable root; cubic R² 0.09 vs linear 0.05 |
| Qwen frozen-judge | −0.192 [−0.295, −0.131] | **0.118** | single stable root |
| OLMo self-judge | −0.398 | 1.049 (rail) | single stable root at the ceiling |
| OLMo frozen-judge | −0.414 | 1.035 (rail) | single stable root at the ceiling |

The cubic fit barely improves on the linear one, and a bootstrap over rollouts
finds ≥2 stable interior roots (the bistability signature) in only **19%** of
resamples — i.e. no reliable saddle. So the headline "self-judge → divergent
basins" is **not** deterministic bistability. There is one weak attractor.

**What the judge sets is the attractor's location.** The self-judge's fixed
point sits mid-range (0.35), the frozen judge's sits low, toward caution (0.12),
and on OLMo both judges pin to the ceiling (~1.03). That is the
judge-preference-sets-the-attractor mechanism (report_basin_lightning_partial.md
§Mechanism) read directly off the drift field: same weak restoring dynamics,
different equilibrium.

## Result 2: the divergence is stochastic, not structural — and that distinguishes the two judges

The restoring eigenvalues are statistically indistinguishable between judges
(CIs overlap heavily). What differs is the balance of noise against restoring:

| condition | per-step noise sd | AR(1) equilibrium spread | observed final spread |
|---|---|---|---|
| self-judge | 0.139 | 0.229 | **0.223** |
| frozen-judge | 0.116 | 0.198 | **0.119** |

The self-judge's final cross-seed spread (0.223) is almost exactly the spread a
linear mean-reverting process with its noise would settle at (0.229). **The
"divergent basins" are a weak-center random walk that has reached its natural
stochastic equilibrium — not selection between two wells.** The frozen judge, by
contrast, is far *tighter* than its own AR(1) equilibrium (0.119 vs 0.198): its
cross-seed spread rises then actively contracts (0.157 → 0.137 → 0.119 over
rounds 3–5), so it is doing more than mean-reverting — it is compressing toward
the cautious fixed point.

The lock-in is real but stochastic: corr(round-k state, final) climbs
monotonically for the self-judge (0.29 → 0.61 → 0.77 → 1.0), so early position
increasingly predicts fate — but that is path dependence in one weak well, not a
choice between attractors.

## Interpretation and caveats

The refined mechanistic story: the loop is a weakly mean-reverting stochastic
process on the coordinate; **the judge sets where it reverts to** (self mid,
frozen low/cautious, OLMo ceiling), and **the self-judge additionally runs near
its noise-equilibrium spread while the frozen judge contracts below it**. That
reproduces "self diverges / frozen decays" without any saddle.

Caveat worth a follow-up: a single well with *state-dependent* (multiplicative)
noise can also widen spread without a deterministic saddle, and R² of the drift
fits is low (~0.05–0.09) — round-to-round motion is mostly stochastic, so these
fixed points are the faint mean of a noisy field, not a stiff well. The
deterministic-bistability question is answered (no); whether the residual noise
is state-dependent is the natural next cut, and it needs per-round logits the
current JSONs don't store — so it is a new-run question, not a re-analysis one.

For Lit&planning: the saddle hypothesis is **not supported**. If the dedicated
drift-mapping experiment is still wanted, its value is now measuring the *noise
structure* (is it multiplicative?), not locating a saddle that isn't there.

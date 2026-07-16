# Model ladder by forecast horizon: how error grows with rounds ahead

**Date:** 2026-07-15; extended 2026-07-16 with the unit selection-response
models after the selection-response audit
(`docs/report_predictive_model_literature.md`).
**Script:** `scripts/analysis_model_ladder_horizon.py`
**Result JSON:** `experiments/model_ladder_horizon.json`
**Inputs:** `experiments/spread_rollout_bakeoff.json`,
`experiments/spread_util_unified.json`,
`experiments/selection_response_predictor.json`

## What this analysis is

Published results on the same corpus of self-training runs answer different
questions at different information budgets. The one-round value predictor
(`docs/report_value_predictor_models.md`) says: given this round's measured
pool, the mean value score of the kept training answers predicts the next
behavioral value with pooled mean absolute error about 0.081. The closed-loop
rollout bakeoff (`docs/report_spread_rollout_bakeoff.md`) says: measuring a run
once, at its first modelable round, and rolling the fitted frozen-mean-SD model
forward gives an endpoint mean absolute error of about 0.127 on the
selection-driven runs under leave-one-condition-out validation. The
selection-response audit adds a **unit recurrence with no fitted parameters**
(`m_next = clip((1−u)·m + u·supplier + ρσ, 0, 1)`, next value = that mean),
scoring 0.118 on the same 36 selection-driven endpoints.

This analysis fills in the ladder between the one-round and endpoint numbers:
for each simple model, how does forecast error grow with **forecast horizon** —
the number of rounds ahead of the first measured pool? Horizon h means: the
prediction target is the observed behavioral value after round h's training
(`value_after_true` in the bakeoff per-run records, which equals `value +
drift` in the unified per-round records). A run contributes at horizon h only
if it has at least h rounds. All 67 modelable runs from the bakeoff are used
(56 four-round runs, 11 eight-round runs).

**LOCO** means leave-one-condition-out: the fitted closed-loop models were fit
with the run's entire experimental condition excluded, inherited unchanged from
the source bakeoff analysis. The one-step models and the unit recurrence are
not fit at all: kept-mean and the unit rule are parameter-free, and the
factorized 0.958 slope is a full-data descriptive calibration — **not**
design-derived (the 0.9545 top-2-of-6 order statistic is in units of the
underlying normal SD, not the realized six-candidate SD the project measures;
scale audit in `experiments/selection_response_predictor.json`).

## The models

- **No-change**: predict `v1` (the behavioral value at the run's first
  modelable round) at every horizon. The floor.
- **Closed-loop frozen mean SD (measure once, fitted)**: the bakeoff's LOCO
  frozen-mean-SD rollout, launched from round-1 state and never updated.
- **Closed-loop geometry (fitted, predicted-spread feedback)**: same, but the
  bakeoff's geometry variant, which feeds its own predicted spread back.
- **Closed-loop unit recurrence (measure once, zero fitted parameters)**:
  `m_next = clip((1−u)·m + u·supplier + ρσ, 0, 1)` with the boundary state
  measured once; per-run trajectories read from the selection-response JSON.
  For judge-swap runs its stored rollout starts at the swap boundary, so on
  that slice it is a conditional post-swap forecast. The four glued
  selfaware-grid entries are excluded (their two 2-round sub-runs make a
  sequential rollout ambiguous); 63 of 67 runs are covered.
- **One-step kept-mean (re-measure every round)**: at horizon h, predict that
  round's observed `kept_mean`. Parameter-free; observes the pool at round h,
  so it is the "re-measure every round" ceiling for the simple law.
- **One-step unit (re-measure, pre-selection)**: at horizon h, predict
  `pool_mean + ρ·spread` from that round's observed pool state. Parameter-free.
- **One-step factorized (re-measure, pre-selection, calibrated)**: same with
  the 0.958 full-data calibration slope. Rounds with null agreement are
  skipped by both pre-selection models (22 of 312 joined rounds).
- **Refresh at swap (judge-swap runs only, fitted)**: the closed-loop frozen
  model's predictions before the judge-swap round, then the fitted rollout
  re-launched from state remeasured on the first pool scored by the new judge.

Reading rule: the one-step models are conditioned on observations the
closed-loop models never receive (the actual pool at round h). Their advantage
is the **value of re-measuring**, not evidence of a better model.

## Anchors: do the published numbers reproduce?

All five reproduce.

| Anchor | Published | Computed here | Reproduces |
|---|---|---|---|
| Fitted frozen closed-loop endpoint MAE, selection-driven (36 runs) | 0.127 | 0.1268 | yes |
| No-change endpoint MAE, selection-driven (36 runs) | 0.431 | 0.4309 | yes |
| One-step kept-mean pooled MAE (all 340 unified records) | 0.081 | 0.0812 | yes |
| Unit-recurrence endpoint MAE, selection-driven matched (36 runs) | 0.118 | 0.1181 | yes |
| Unit-recurrence endpoint MAE, combined 45 runs | 0.1365 | 0.1365 | yes |

Two unplanned cross-checks also pass: the refresh-at-swap endpoint MAE
computed from per-round records (0.179) matches the bakeoff aggregate
(0.1794), and the unit recurrence's judge-swap endpoint computed here from
its per-round trajectories (0.2099, 9 runs) matches the selection-response
JSON's stored aggregate (0.210).

## Ladder summary: selection-driven runs (intervention + self-force)

Mean absolute error of the predicted behavioral value, by horizon. n = 40
predictions at h=1 and h=2, 32 at h=3 and h=4, 36 at endpoint for the fitted
and one-step models (four selfaware_loop_grid entries are glued pairs of
2-round sub-runs); the unit recurrence covers 32 runs at every horizon.

| Model | h=1 | h=2 | h=3 | h=4 | endpoint |
|---|---|---|---|---|---|
| No-change | 0.314 | 0.416 | 0.441 | 0.432 | 0.431 |
| Closed-loop frozen mean SD (measure once, fitted) | 0.135 | 0.110 | 0.104 | 0.126 | 0.127 |
| Closed-loop geometry (fitted) | 0.138 | 0.142 | 0.103 | 0.125 | 0.139 |
| Closed-loop unit recurrence (measure once, no parameters) | 0.100 | 0.099 | 0.097 | 0.130 | 0.130 |
| One-step kept-mean (re-measure) | 0.101 | 0.096 | 0.066 | 0.061 | 0.078 |
| One-step unit (re-measure) | 0.109 | 0.111 | 0.078 | 0.086 | 0.103 |
| One-step factorized (re-measure) | 0.110 | 0.111 | 0.077 | 0.085 | 0.103 |

(The unit-recurrence endpoint over its 32 covered runs is 0.130; over the full
matched 36, computed endpoint-only, it is 0.118 — the anchor above. The two
pre-selection one-step rows differ by less than 0.001 everywhere: the 0.958
calibration buys nothing over the unit coefficient.)

The striking feature is what does **not** happen: closed-loop error barely
grows with horizon on the selection-driven runs (fitted 0.135 → 0.127; unit
0.100 → 0.130 from h=1 to endpoint), because these trajectories saturate —
most movement happens in the first round or two, and a model that gets the
direction and rough magnitude of that first move right stays close thereafter.
The no-change model's error nearly triples over the same window (0.31 → 0.43):
the horizon cost is paid by models that ignore the dynamics, not by the
closed-loop rollouts. The one-step models improve at later horizons for the
same saturation reason — once the run has pinned near its endpoint, predicting
next round from the current pool is easy.

## Where re-measuring actually matters: judge-swap runs

For the 9 judge-swap runs (judge replaced mid-run), the closed-loop rollout
from round 1 cannot know the regime changed, and its error grows steadily with
horizon; remeasuring once, at the swap, cuts the endpoint error by more than
half:

| Model | h=1 | h=2 | h=3 | h=4 | h=5 | h=6 | h=7 | h=8 (endpoint) |
|---|---|---|---|---|---|---|---|---|
| No-change | 0.082 | 0.164 | 0.184 | 0.201 | 0.232 | 0.292 | 0.351 | 0.361 |
| Closed-loop frozen from round 1 | 0.098 | 0.110 | 0.143 | 0.175 | 0.232 | 0.322 | 0.354 | 0.404 |
| Refresh at swap (fitted) | 0.098 | 0.100 | 0.071 | 0.098 | 0.174 | 0.178 | 0.167 | 0.179 |
| One-step kept-mean | 0.069 | 0.083 | 0.071 | 0.072 | 0.111 | 0.074 | 0.107 | 0.041 |

The unit recurrence's stored swap rollouts start at each condition's swap
boundary (a conditional post-swap forecast); its endpoint MAE is 0.210 —
worse than the fitted refresh's 0.179. The swaps are the one slice where the
fitted model retains a real advantage over the parameter-free version.

This is the cleanest horizon-resolved statement of the bakeoff's judge-swap
finding: one extra measurement at the right moment (the regime change)
recovers most of the value of re-measuring every round.

For completeness, over everything except judge-swap (58 runs), the endpoint
MAEs are: no-change 0.349, closed-loop frozen 0.157, closed-loop geometry
0.164, one-step kept-mean 0.073, one-step factorized 0.086. On the self-weak
runs alone the closed-loop model is barely better than no-change at the
endpoint (0.205 vs 0.215) — those runs drift slowly and idiosyncratically, so
there is little first-round signal to extrapolate.

## The h=1 gap: predicting selection versus observing it

At horizon 1 the closed-loop models and the one-step models see exactly the
same information — the round-1 pool state. The only difference is that the
closed-loop models **predict** the selection gap from boundary ρ·σ, while
one-step kept-mean **observes** the realized kept set. On the matched
selection-driven runs (the 32 the unit recurrence covers, so all three models
score identical run sets):

- One-step kept-mean (observes selection): MAE **0.085**
- Closed-loop unit recurrence (predicts selection): **0.100** → cost 0.015
- Closed-loop fitted frozen SD (predicts selection): **0.108** → cost 0.023

So predicting which answers selection will keep, rather than watching it
happen, costs about 0.015–0.023 at h=1 — and the parameter-free unit rule is
the cheaper of the two. The pooled-set figure of 0.033 quoted in the first
version of this report was inflated by the four glued runs, which only the
fitted models cover; the matched-set numbers above supersede it. The remaining
growth from the one-step baseline at later horizons is state drift, which on
these saturating runs is small.

## Caveats and join diagnostics

- All 312 bakeoff per-run rounds joined to unified records with zero failures
  and zero round-index offset; `value_after_true` equals `value + drift`
  within 2e-3 everywhere.
- Four selfaware_loop_grid entries (seeds 11, 22, 33, 44) are "glued": each
  concatenates two 2-round sub-runs under one (cond, seed, source) key, with
  round indices running 1,1,2,2 in both input files. Duplicate join keys were
  disambiguated by matching `value_after_true` to `value + drift` per round.
  Each glued entry contributes two predictions at h=1 and h=2 and none beyond;
  its endpoint is the last listed round, matching how the published bakeoff
  endpoint (0.127) aggregates. This is why n = 40 rather than 36 at h=1 for
  the fitted and one-step models. The unit recurrence excludes these four runs
  per-round (its stored trajectory treats them as one sequential rollout) but
  its endpoint anchors include them, computed endpoint-only.
- Unit-recurrence swap trajectories were aligned by detecting their
  swap-boundary start (stored length = rounds remaining after the swap; start
  equals the observed value entering the first new-judge round); the alignment
  is validated per run against stored `start`/`actual`/`predicted` fields, and
  the resulting endpoint reproduces the published 0.210 aggregate.
- The pre-selection one-step models skip 22 null-agreement rounds; their n
  runs slightly below the other models at h ≥ 2.
- Horizons 5–8 outside the judge-swap group rest on only 2 runs — ignore them.
- The comparison between closed-loop and one-step models reads as "value of
  re-measuring", not model quality: the one-step models condition on the
  observed pool at horizon h, which the closed-loop models never see.

## What this shows

The gap between the one-round number (0.081) and the measure-once endpoint
numbers (0.118 unit / 0.127 fitted) is not a gradual accumulation of per-round
error. On selection-driven runs the closed-loop error is essentially flat in
horizon, and decomposes at h=1 into a 0.015–0.023 cost of predicting selection
rather than observing it, plus a first-round error that saturating dynamics
then preserve rather than amplify. The parameter-free unit recurrence matches
or beats the fitted model everywhere except the judge-swap slice (0.210 versus
0.179), and the 0.958 calibration slope is indistinguishable from the unit
coefficient at every horizon. Horizon only genuinely hurts when the regime
changes mid-run (judge swap), and there a single remeasurement at the change
point buys back most of the loss (endpoint 0.404 → 0.179, versus 0.041 for
re-measuring every round).

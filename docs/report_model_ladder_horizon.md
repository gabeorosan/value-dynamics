# Model ladder by forecast horizon: how error grows with rounds ahead

**Date:** 2026-07-15
**Script:** `scripts/analysis_model_ladder_horizon.py`
**Result JSON:** `experiments/model_ladder_horizon.json`
**Inputs:** `experiments/spread_rollout_bakeoff.json`, `experiments/spread_util_unified.json`

## What this analysis is

Two published results live on the same corpus of self-training runs but answer
different questions. The one-round value predictor
(`docs/report_value_predictor_models.md`) says: given this round's measured
pool, the mean value score of the kept training answers predicts the next
behavioral value with pooled mean absolute error about 0.081. The closed-loop
rollout bakeoff (`docs/report_spread_rollout_bakeoff.md`) says: measuring a run
only once, at its first modelable round, and rolling the frozen-mean-SD model
forward to the end of the run gives an endpoint mean absolute error of about
0.127 on the selection-driven runs under leave-one-condition-out validation.

This analysis fills in the ladder between those two numbers: for each simple
model, how does forecast error grow with **forecast horizon** — the number of
rounds ahead of the first measured pool? Horizon h means: the prediction
target is the observed behavioral value after round h's training
(`value_after_true` in the bakeoff per-run records, which equals `value +
drift` in the unified per-round records). A run contributes at horizon h only
if it has at least h rounds. All 67 modelable runs from the bakeoff are used
(56 four-round runs, 11 eight-round runs).

**LOCO** means leave-one-condition-out: the closed-loop models were fit with
the run's entire experimental condition excluded, inherited unchanged from the
source bakeoff analysis. The one-step models are not refit here at all:
kept-mean is parameter-free, and the factorized model uses the published
pooled constant (below).

## The models

- **No-change**: predict `v1` (the behavioral value at the run's first
  modelable round) at every horizon. The floor.
- **Closed-loop frozen mean SD (measure once)**: the bakeoff's LOCO
  frozen-mean-SD rollout, launched from round-1 state and never updated. Its
  per-round predictions (`value_after_pred`) are read directly from the
  committed bakeoff per-run records.
- **Closed-loop geometry (predicted-spread feedback)**: same, but the bakeoff's
  geometry variant, which feeds its own predicted spread back into the rollout.
- **One-step kept-mean (re-measure every round)**: at horizon h, predict that
  round's observed `kept_mean` — the mean value score of the answers actually
  kept for training. Parameter-free, but it observes the pool at round h, so
  it is the "re-measure every round" ceiling for the simple law.
- **One-step factorized (re-measure, pre-selection)**: at horizon h, predict
  `pool_mean + 0.958 × rho × spread` from that round's observed pool state
  (whole-pool mean, judge/value agreement rho, within-prompt spread). The
  constant 0.958 is the published pooled factorization slope — descriptive,
  pooled, not refit here. Rounds where rho is null are skipped (22 of 312
  joined rounds).
- **Refresh at swap (judge-swap runs only)**: the closed-loop frozen model's
  predictions before the judge-swap round, then the closed-loop rollout
  re-launched from state remeasured on the first pool scored by the new judge.
  Read from `judge_swap_refresh.leave_one_condition_out.mean_sd_frozen` in the
  bakeoff JSON, which does contain full per-round predictions for all 9
  judge-swap runs (so the model is included, not skipped).

An important reading rule: the two one-step models are conditioned on
observations the closed-loop models never receive (the actual pool at round
h). Their advantage is therefore the **value of re-measuring**, not evidence
of a better model.

## Anchors: do the published numbers reproduce?

All three reproduce.

| Anchor | Published | Computed here | Reproduces |
|---|---|---|---|
| Frozen closed-loop endpoint MAE, selection-driven (36 runs) | 0.127 | 0.1268 | yes |
| No-change endpoint MAE, selection-driven (36 runs) | 0.431 | 0.4309 | yes |
| One-step kept-mean pooled MAE (all 340 unified records) | 0.081 | 0.0812 | yes |

As a fourth, unplanned cross-check, the refresh-at-swap endpoint MAE computed
from the per-round records (0.179) matches the aggregate stored in the bakeoff
JSON (0.1794).

## Ladder summary: selection-driven runs (intervention + self-force)

Mean absolute error of the predicted behavioral value, by horizon. n = 40
predictions at h=1 and h=2, 32 at h=3 and h=4, 36 at endpoint (four
selfaware_loop_grid entries are glued pairs of 2-round sub-runs; see caveats).

| Model | h=1 | h=2 | h=3 | h=4 | endpoint |
|---|---|---|---|---|---|
| No-change | 0.314 | 0.416 | 0.441 | 0.432 | 0.431 |
| Closed-loop frozen (measure once) | 0.135 | 0.110 | 0.104 | 0.126 | 0.127 |
| Closed-loop geometry | 0.138 | 0.142 | 0.103 | 0.125 | 0.139 |
| One-step kept-mean (re-measure) | 0.101 | 0.096 | 0.066 | 0.061 | 0.078 |
| One-step factorized (re-measure) | 0.110 | 0.111 | 0.077 | 0.085 | 0.103 |

(The factorized row has slightly smaller n at h≥2 — 37, 27, 25, and 29 at
endpoint — because null-rho rounds are skipped.)

The striking feature is what does **not** happen: closed-loop error barely
grows with horizon on the selection-driven runs (0.135 → 0.127 from h=1 to
endpoint), because these trajectories saturate — most movement happens in the
first round or two, and a model that gets the direction and rough magnitude of
that first move right stays close thereafter. The no-change model's error
nearly triples over the same window (0.31 → 0.43): the horizon cost is paid by
models that ignore the dynamics, not by the closed-loop rollout. The one-step
models improve at later horizons for the same saturation reason — once the run
has pinned near its endpoint, predicting next round from the current pool is
easy.

## Where re-measuring actually matters: judge-swap runs

For the 9 judge-swap runs (judge replaced mid-run), the closed-loop rollout
from round 1 cannot know the regime changed, and its error grows steadily with
horizon; remeasuring once, at the swap, cuts the endpoint error by more than
half:

| Model | h=1 | h=2 | h=3 | h=4 | h=5 | h=6 | h=7 | h=8 (endpoint) |
|---|---|---|---|---|---|---|---|---|
| No-change | 0.082 | 0.164 | 0.184 | 0.201 | 0.232 | 0.292 | 0.351 | 0.361 |
| Closed-loop frozen from round 1 | 0.098 | 0.110 | 0.143 | 0.175 | 0.232 | 0.322 | 0.354 | 0.404 |
| Refresh at swap | 0.098 | 0.100 | 0.071 | 0.098 | 0.174 | 0.178 | 0.167 | 0.179 |
| One-step kept-mean | 0.069 | 0.083 | 0.071 | 0.072 | 0.111 | 0.074 | 0.107 | 0.041 |

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

At horizon 1 the closed-loop frozen model and the one-step models see exactly
the same information — the round-1 pool state. The only difference is that
the closed-loop model **predicts** the selection gap from frozen rho × spread,
while one-step kept-mean **observes** the realized kept set. On the
selection-driven runs:

- Closed-loop frozen h=1 MAE: **0.135**
- One-step kept-mean h=1 MAE: **0.101**
- Gap: **0.033** (n = 40)

So about 0.03 of the closed-loop model's error at every horizon is the
irreducible-without-observation cost of predicting which answers selection
will keep, rather than watching it happen. The remaining growth from 0.101 to
the one-step models' later-horizon numbers is state drift, which on these
saturating runs is small.

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
  endpoint (0.127) aggregates. This is why n = 40 rather than 36 at h=1.
- The one-step factorized model skips 22 null-rho rounds; its n therefore runs
  slightly below the other models at h ≥ 2.
- Horizons 5–8 outside the judge-swap group rest on only 2 runs — ignore them.
- The comparison between closed-loop and one-step models reads as "value of
  re-measuring", not model quality: the one-step models condition on the
  observed pool at horizon h, which the closed-loop models never see.

## What this shows

The gap between the two published numbers — 0.081 for one-round prediction and
0.127 for measure-once endpoint rollout — is not a gradual accumulation of
per-round error. On selection-driven runs the closed-loop model's error is
essentially flat in horizon, and decomposes at h=1 into a ~0.03 cost of
predicting selection rather than observing it, plus a first-round error that
saturating dynamics then preserve rather than amplify. Horizon only genuinely
hurts when the regime changes mid-run (judge swap), and there a single
remeasurement at the change point buys back most of the loss (endpoint 0.404 →
0.179, versus 0.041 for re-measuring every round).

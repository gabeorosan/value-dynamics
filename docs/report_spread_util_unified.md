# Unified spread × utilization accounting: one bookkeeping for every loop we ran

*2026-07-15, updated 2026-07-16. Committed scorer:
`scripts/analysis_spread_util_unified.py` → `experiments/spread_util_unified.json`.
Data: 340 selection rounds from 74 runs — the K1 Qwen risk grid, the K2 OLMo
grids, all modal K2 release cells (own-pool, base-mixed, peer-invasion,
head-to-head duels), and the Qwen insecure-code self-report cells
(self-aware grid, oracle opposition, mixed reopen + matched twin, self-judge
duels). Everything is descriptive accounting on logged pools; no causal claim.*

Motivation: the writeup is being refocused (user directive 07-15) onto three
claims — selection moves the generator toward the kept training targets; the
selector gap factorizes into value spread × judge agreement; and that movement
changes the variation the generator supplies next round. The own-pool halves existed
(`report_taste_alignment_predictor.md`, `state_space_explore.json`); this
analysis runs the SAME bookkeeping over the mixed-generator and injection
cells and adds the one quantity that unifies own-pool and mixed-pool movement.

## Definitions (per round, per run)

- **value** v — the measured coordinate before the round (risk share for the
  gamble organisms; insecure-code self-report for the EM organisms; both 0–1).
  The JSON now also records the known battery sample count and conditional
  generation SE for the current and next reads. Risk batteries use 24 or 96
  generated choices; self-report batteries use nine bounded generation scores.
  These fields support observation-noise forecasts without treating readout
  noise as latent model change.
- **within-prompt value spread** σ — for each prompt `j`, take the population
  SD of its candidate value scores,
  `σ_j = sqrt[(1/n_j)Σ_k(x_jk−x̄_j)²]`, then average `σ_j` equally over
  prompts. This uses `ddof=0`; it is not a pooled SD across prompts. Candidate
  count is six for every prompt in 336/340 rounds; the observed `n_j` is used
  in four rounds containing a five-candidate prompt.
- **selector gap** — kept mean minus the whole offered pool mean. This measures
  the judge's sorting inside the pool and is the quantity factorized below.
- **training displacement** — kept mean minus the model's own generated-pool
  mean. It equals selector gap + pool-supply shift and is the relevant update
  coordinate in mixed pools.
- **pull** — kept mean minus the separate behavioral value. It equals training
  displacement + the generator/behavior calibration residual and is therefore
  the best direct predictor of movement in that behavioral readout.
- **utilization** ρ — mean within-item Pearson correlation between the
  judge's candidate scores and the candidates' value scores (−1…1). This is
  the taste-alignment ρ, computed here for every cell with logged judge
  scores (reference `scores_arm`, duels `scores_h2h`, self-aware `scores`);
  the score oracle's ρ is computed from its decision rule (its score IS the
  negated value score). A secondary null-centred "extremeness" utilization
  (realized-vs-random kept-pair offset, per `analysis_own_pool_records.py`)
  is kept in the JSON as `util`.
- **source_sep** — |mean self candidate − mean co-generator candidate| in
  mixed pools.

## 1. Measuring against the model's own pool isolates the update

Each round, the value moves toward the mean of the kept answers, at ~80% of
the distance per round:

| slice | selector gap r | training displacement r | behavioral pull r |
|---|---:|---:|---:|
| pooled (340 rounds) | 0.58 | **0.68** | 0.80 |
| self-only (244) | 0.55 | 0.55 | 0.71 |
| base-mixed (64) | 0.43 | **0.64** | 0.80 |
| peer-mixed (32) | 0.90 | **0.95** | 0.99 |

In self-only rounds the two gaps coincide. In mixed pools, kept minus the
model's own generated mean is the better update coordinate because it includes
the displacement introduced by the supplier. Pull wins when predicting the
separate behavioral readout because the model's generated-pool mean and that
readout are close but not identical. The three quantities answer different
questions and are all retained.

The separate value-predictor bakeoff validates this one-round comparison while
holding out each complete condition. The parameter-free rule `next value =
kept mean` scores MAE 0.081 over all 340 rounds, versus 0.098 for fitted
training displacement, 0.112 for fitted selector gap, and 0.128 for no change.
A calibrated 0.833-gain pull model slightly improves squared error but not MAE.

## 2. The selector gap is spread × local selection intensity

Extending the own-pool factorization (`report_taste_alignment_predictor.md`:
gap ≈ 0.98·ρσ, r = 0.82, 100 rounds) to every cell with judge scores:

| slice | slope on ρσ | r | n | r² spread alone | r² ρ alone | r² product |
|---|---|---|---|---|---|---|
| pooled | 0.96 | **0.90** | 290 | 0.03 | 0.59 | 0.81 |
| self-only | 0.92 | 0.85 | 207 | 0.06 | 0.52 | 0.72 |
| base-mixed | 0.97 | 0.95 | 64 | 0.00 | 0.67 | 0.90 |
| peer-mixed | 1.14 | 0.91 | 19 | 0.48 | 0.48 | 0.83 |

Neither factor alone explains the gap; the product does. Prompt by prompt,
`kept_j−pool_j=Cov_i(value_ji,kept_ji)/mean_i(kept_ji)`, the Price selection
differential; the reported gap averages prompts equally. Standardizing the
aggregate gap by the measured spread defines the
realized value-axis selection intensity `a=(kept−pool)/spread`, so
`gap=spread×a` exactly after selection. Before selection, judge/value
correlation `ρ` is a compact proxy for `a`. The parameter-free rule `gap=ρσ`
has R² 0.810 and MAE 0.0421 over all 290 rounds; the descriptive calibration
is `−0.002+0.958ρσ`.

The empirical 0.958 slope is not a top-2-of-6 normal-theory constant. The
normal order-statistic value 0.9545 is expressed in units of the underlying
distribution SD, whereas this project uses the realized six-candidate
population SD. On the project scale a normal-pool simulation gives about
1.10, not 0.9545. This says where a gap can come from—material × a selector
that sorts on the axis—not whether that local alignment persists.

## 3. Selection changes the spread supplied next round

σ_{t+1} ~ σ_t within runs, plus mean spread by round:

| family / composition | persistence slope | r | mean σ by round |
|---|---|---|---|
| OLMo self-only (136 rds) | 0.88 | 0.79 | 0.30 → 0.31 → 0.28 → 0.26 |
| Qwen self-only (108 rds) | 0.97 | 0.93 | 0.36 → 0.29 → 0.30 → 0.28 |
| OLMo base-mixed (48 rds) | 0.12 | 0.15 | 0.35 → 0.39 → 0.40 → 0.38 |
| Qwen base-mixed (16 rds) | 0.22 | 0.46 | 0.32 → 0.14 → 0.10 → 0.10 |
| OLMo peer-mixed (32 rds) | 0.39 | 0.62 | 0.43 → 0.16 → 0.06 → 0.03 |

Persistence describes the trajectories but does not explain them. The
conversion analysis (`report_spread_conversion_model.md`) identifies the
changing state on the binary risk axis: the mean `q` and within-prompt spread
`s` of the model's own generated candidates. Training displacement predicts
`Δq` (`r = 0.84` over 221 risk-axis transitions, 0.90 mixed); the resulting
change in total binary variance `q(1−q)` predicts `Δs` (`r = 0.85` overall,
0.89 mixed). Leave-one-run-out, the headroom chain predicts next own-source
spread at R² 0.765 versus 0.581 persistence. The exact variance version also
subtracts variance across prompt means and scores 0.778; in mixed risk pools
it scores 0.653 versus 0.193 persistence.

Mixed-pool total within-prompt **variance** splits exactly into within-source
and between-source terms. The between-source term accounts for 34% of mean
variance in base-mixed pools and 57% in peer-mixed pools. Recomputing SD after
removing that term reduces mean spread by 23% and 42%, respectively. The
selector acts on whole-pool spread; the generator carries its own-source mean
and spread into the next round.

The matched pair is the cleanest single contrast (same seeds, same oracle,
random streams diverging only at injection): the self-only twin has spread
0.000 in every round and mean |drift| 0.0006; the injected run has spread
0.31 in the injected round and mean |drift| 0.157.

## 4. Agreement: organized by judge cell, but consequentially dynamic

Between-cell (organism × judge × format × composition) variance share of ρ:
**0.82** — i.e. most utilization variance is *which judge in which format on
which pool*, not round-to-round noise. (The extremeness-based `util` variant
is less stable, 0.53.) Selected cells (full table in the JSON):

This is a variance decomposition, not permission to hold ρ fixed indefinitely.
The closed-loop test in `report_spread_rollout_bakeoff.md` finds that later
agreement is the larger missing endpoint state: using observed later agreement
reduces LOCO selection-driven MAE from 0.139 to 0.115, while using observed
later spread alone leaves 0.139. The judge cell supplies a good initial level;
remeasure after the judge, format, or candidate distribution changes.

| cell | ρ mean | note |
|---|---|---|
| score oracle (any pool) | −1.00 | by decision rule; util 0.70–0.81 realized |
| OLMo base judge, reference, peer-mixed | +0.70 | contamination: keeps the railed peer's text |
| OLMo self judge, duels, peer-mixed | +0.52 | contamination survives duels |
| OLMo cautious judge, reference, base-mixed | +0.38 | positive ρ = keeps HIGH-risk own text → failed rescue |
| Qwen self judge, candid prompt, self-only | +0.35 | the sr-amplifying grid |
| OLMo cautious judge, duels, base-mixed | +0.10 | duels break the reference artifact |
| Qwen self judge, duels, base-mixed | −0.24 | the self-erosion cells |
| K1 Qwen model judges, reference, self-only | ≈ 0.0–0.11 | the fan without selection: drift there is training noise, not force |
| random | ≈ 0 (util +0.02) | validates the null-centring |

Two known results become single numbers in this table: the judging-format
result (same cautious judge: ρ +0.38 under reference scoring where it kept
the organism's own high-risk text, +0.10 under duels where it used the
rescue material) and the self-erosion result (self judge under duels with
base text present: ρ −0.24 — its judgment runs *against* its own installed
value).

## Caveats

- The factorization is near-tautological given order statistics; the movement
  comparisons are associations across heterogeneous cells
  (81 of 340 rounds share the OLMo K2 grid chassis). This descriptive scorer
  does not itself cross-validate; `report_value_predictor_models.md` adds
  leave-one-condition-out comparison of the one-round predictors. The
  frozen-predictor blind-set result,
  `report_loop_integrator_decomposition.md`, remains the out-of-sample
  prospective evidence that gap-type quantities predict. The separate
  spread-conversion report adds leave-one-run-out and leave-one-condition-out
  evaluation for next-round own-source spread. The closed-loop bakeoff adds complete-run LOCO
  endpoints and shows that the spread recurrence does not yet improve endpoints
  over holding first-round spread fixed.
- ρ for the oracle is definitional (−1), not measured from logged scores
  (logged oracle scores are near-ties; correlating them dilutes ρ
  artifactually).
- Schedule cells (fan-then-press) are included in movement/spread fits but
  excluded from the per-judge table (their judge changes mid-run).
- K3 (em-neutral grid) is excluded: its pools score a different axis
  (candor) and its battery lacks the sr trajectory.
- The `q(1−q)` spread dynamics apply only to the 280 binary risk-axis rounds.
  The 60 continuous self-report rounds retain the selector-gap accounting but
  fail the mean-to-within-spread conversion (LORO R² −0.029 versus 0.747 for
  persistence). See `report_spread_definition_audit.md`.
- Axes are pooled only where dimensionless (all coordinates 0–1); per-family
  fits are reported alongside every pooled fit.

# Unified spread × utilization accounting: one bookkeeping for every loop we ran

*2026-07-15, general (writeup) thread. Committed scorer:
`scripts/analysis_spread_util_unified.py` → `experiments/spread_util_unified.json`.
Data: 340 selection rounds from 74 runs — the K1 Qwen risk grid, the K2 OLMo
grids, all modal K2 release cells (own-pool, base-mixed, peer-invasion,
head-to-head duels), and the Qwen insecure-code self-report cells
(self-aware grid, oracle opposition, mixed reopen + matched twin, self-judge
duels). Everything is descriptive accounting on logged pools; no causal claim.*

Motivation: the writeup is being refocused (user directive 07-15) onto three
claims — the selection gap predicts movement; the gap factorizes into value
spread × judge utilization; and spread and utilization each follow simple,
separately-intervenable dynamics. The own-pool halves of this existed
(`report_taste_alignment_predictor.md`, `state_space_explore.json`); this
analysis runs the SAME bookkeeping over the mixed-generator and injection
cells and adds the one quantity that unifies own-pool and mixed-pool movement.

## Definitions (per round, per run)

- **value** v — the measured coordinate before the round (risk share for the
  gamble organisms; insecure-code self-report for the EM organisms; both 0–1).
- **spread** σ — mean within-item SD of the six candidates' value scores
  (the prereg formula).
- **gap** — kept mean minus pool mean on the value axis.
- **pull** — kept mean minus *current value*. In an own-pool round the pool
  mean sits at the current value, so pull ≈ gap. In a mixed pool the two come
  apart: pull = gap + (pool mean − value), and the second term carries the
  supplier.
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

## 1. One movement law covers own-pool, injection, and invasion rounds

Each round, the value moves toward the mean of the kept answers, at ~80% of
the distance per round:

| slice | drift ~ pull slope | r | n | drift ~ gap r |
|---|---|---|---|---|
| pooled (all rounds) | 0.83 | **0.80** | 340 | 0.58 |
| OLMo risk | 0.79 | 0.84 | 216 | 0.55 |
| Qwen risk | 0.98 | 0.72 | 64 | 0.42 |
| Qwen self-report | 0.91 | 0.76 | 60 | 0.78 |
| self-only rounds | 0.82 | 0.71 | 244 | 0.55 |
| base-mixed rounds | 0.71 | 0.80 | 64 | 0.43 |
| peer-mixed rounds | 0.95 | **0.99** | 32 | 0.90 |

In own-pool rounds pull and gap coincide, so this contains the known
gap→drift result. In mixed pools they separate, and pull wins everywhere —
which is the "runs end at the supplier's level" result restated as mechanics:
training moves the value toward whatever the judge kept, and when the judge
keeps supplier text, the kept mean sits at the supplier's level, so that is
where the run goes. No extra force is needed.

## 2. The gap factorizes: gap ≈ 0.96 · ρ · σ (r = 0.90, 290 rounds)

Extending the own-pool factorization (`report_taste_alignment_predictor.md`:
gap ≈ 0.98·ρσ, r = 0.82, 100 rounds) to every cell with judge scores:

| slice | slope on ρσ | r | n | r² spread alone | r² ρ alone | r² product |
|---|---|---|---|---|---|---|
| pooled | 0.96 | **0.90** | 290 | 0.03 | 0.59 | 0.81 |
| self-only | 0.92 | 0.85 | 207 | 0.06 | 0.52 | 0.72 |
| base-mixed | 0.97 | 0.95 | 64 | 0.00 | 0.67 | 0.90 |
| peer-mixed | 1.14 | 0.91 | 19 | 0.48 | 0.48 | 0.83 |

Neither factor alone explains the gap; the product does. The ~0.96 constant
matches the keep-2-of-6 order-statistics prediction (~0.95 under Gaussian
scores), as before. This is bookkeeping close to an order-statistic identity
— it says where a gap CAN come from (material × a judge that sorts on the
axis), not when one will persist.

## 3. Spread: a slow state under self-only pools; a supply floor under mixed

σ_{t+1} ~ σ_t within runs, plus mean spread by round:

| family / composition | persistence slope | r | mean σ by round |
|---|---|---|---|
| OLMo self-only (136 rds) | 0.88 | 0.79 | 0.30 → 0.31 → 0.28 → 0.26 |
| Qwen self-only (108 rds) | 0.97 | 0.93 | 0.36 → 0.29 → 0.30 → 0.28 |
| OLMo base-mixed (48 rds) | 0.12 | 0.15 | 0.35 → 0.39 → 0.40 → 0.38 |
| Qwen base-mixed (16 rds) | 0.22 | 0.46 | 0.32 → 0.14 → 0.10 → 0.10 |
| OLMo peer-mixed (32 rds) | 0.39 | 0.62 | 0.43 → 0.16 → 0.06 → 0.03 |

Reading: under self-only pools spread is a persistent, slowly-consumed state
(slope 0.88–0.97) — the intervention-window result in dynamical form. Under a
base co-generator, persistence disappears (slope 0.12) because the supplier
RESETS spread every round: the pool's spread is re-supplied by the source
difference, not inherited. In mixed pools spread tracks source separation
(σ ~ 0.36·source_sep + 0.20, r = 0.47, 96 rounds) — and source separation
itself shrinks as the host converges on the supplier, which is why Qwen
base-mixed spread decays toward ~0.10 (the host reached the supplier's level
in one round) and why peer-invasion spread collapses 0.43 → 0.03 (the host
inherits the railed peer's homogeneity).

The matched pair is the cleanest single contrast (same seeds, same oracle,
random streams diverging only at injection): the self-only twin has spread
0.000 in every round and mean |drift| 0.0006; the injected run has spread
0.31 in the injected round and mean |drift| 0.157.

## 4. Utilization: mostly a property of the judge cell, not of the round

Between-cell (organism × judge × format × composition) variance share of ρ:
**0.82** — i.e. most utilization variance is *which judge in which format on
which pool*, not round-to-round noise. (The extremeness-based `util` variant
is less stable, 0.53.) Selected cells (full table in the JSON):

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

- Descriptive throughout. The factorization is near-tautological given order
  statistics; the movement law is an association across heterogeneous cells
  (81 of 340 rounds share the OLMo K2 grid chassis); no leave-one-out
  validation is run here (the frozen-predictor blind-set result,
  `report_loop_integrator_decomposition.md`, remains the out-of-sample
  evidence that gap-type quantities predict).
- ρ for the oracle is definitional (−1), not measured from logged scores
  (logged oracle scores are near-ties; correlating them dilutes ρ
  artifactually).
- Schedule cells (fan-then-press) are included in movement/spread fits but
  excluded from the per-judge table (their judge changes mid-run).
- K3 (em-neutral grid) is excluded: its pools score a different axis
  (candor) and its battery lacks the sr trajectory.
- Axes are pooled only where dimensionless (all coordinates 0–1); per-family
  fits are reported alongside every pooled fit.

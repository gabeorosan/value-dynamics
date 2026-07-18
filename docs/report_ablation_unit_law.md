# The one-round law, held out: the judge-ablation runs test gap ≈ 0.96·ρ·σ and drift ≈ K·gap on data the law never saw

*2026-07-18, general thread. Scorer:
`scripts/analysis_ablation_unit_law.py` →
`experiments/ablation_unit_law.json`. Data: the 24 judge-ablation runs
(8 committed raw JSONs, the full 2×2 of judge prompt candid/neutral ×
judge model self/base, supplier-removed em750, seeds 41–46 in every cell;
ledger rows 07-17/07-18. First shipped 07-18 on the 14 then-landed runs;
extended the same day when the (e)/(f) Kaggle runs completed the
factorial). Frozen constants
from committed artifacts only: C = 0.96
(`experiments/simple_model_rollout.json` model.C; pooled fit 0.958,
r = 0.901, n = 290 in `experiments/spread_util_unified.json`) and K = 0.833
(same file, movement_law pooled drift~pull). Conventions copied from
`scripts/analysis_spread_util_unified.py` (per-item Pearson ρ, degenerate
items skipped, population SD).*

## Why this is a real held-out test

The one-round selection-response law was fit on the earlier program's logged
pools. The 14 judge-ablation runs were run AFTER those fits, for a different
question (mechanism decomposition), on a different condition family
(supplier-removed self-only across four judge configurations) — none of
their pools contributed to the constants. Every number below uses the frozen
constants first; refits are shown for comparison only.

## Movement law: passes, strongly, in every cell of the factorial

Next-round own-pool mean change (drift, candidate sr axis) vs the realized
kept-minus-pool gap, 72 transitions (18 per condition):

| group | n | frozen-K MAE | persistence MAE | refit slope (r) |
|---|---|---|---|---|
| pooled | 72 | **0.023** | 0.072 | 0.995 (r = 0.953) |
| candid+self | 18 | 0.014 | 0.082 | 0.937 (r = 0.988) |
| neutral+self | 18 | 0.018 | 0.049 | 0.753 (r = 0.932) |
| candid+base | 18 | 0.027 | 0.064 | 1.079 (r = 0.923) |
| neutral+base | 18 | 0.033 | 0.095 | 1.177 (r = 0.922) |

The frozen constant is 3.1× better than the zero-drift baseline pooled, the
pooled refit slope is 0.995 — essentially exactly the frozen K — and every
condition individually has r ≥ 0.92. The movement law is
judge-configuration-independent across the full factorial: whatever the
judge's taste does to the DIRECTION of selection, the pool moves the next
round by the same fixed fraction of the kept-minus-pool gap. The earlier
n = 6 base-judge slope of 1.41 regressed to 1.08 with the full 18
transitions.

## Factorization: strong for the self judge, looser but unbiased for the base judge

Observed per-round gap vs frozen 0.96·ρ·σ, 77 rounds with defined ρ:

| group | n | frozen-C MAE | refit slope (r) |
|---|---|---|---|
| pooled | 77 | 0.034 | **1.005** (r = 0.852) |
| candid+self | 17 | 0.029 | 1.202 (r = 0.947) |
| neutral+self | 16 | 0.031 | 0.994 (r = 0.850) |
| candid+base | 21 | 0.039 | 0.679 (r = 0.647) |
| neutral+base | 23 | 0.037 | 0.882 (r = 0.701) |

The pooled refit slope is 1.005 — the frozen constant is unbiased on held-out
data. Per condition: neutral+self lands almost exactly on the frozen
constant; candid+self runs ~20% hot (its judge converts agreement into gap
slightly more efficiently than the pooled historical fit); the base-judge
conditions are looser (r = 0.65/0.70) — the base judge's selection
concentrates on fewer, more extreme candidates, where a mean-ρ × mean-σ
summary is coarsest. The earlier 14-run version of this report had
candid+base at slope 0.710, r = 0.52, n = 7; tripling the data moved it to
0.679, r = 0.65 — genuinely weaker factorization for the base judge, not a
small-n artifact, but the direction and rough magnitude still track.

## The agreement trajectory — the writeup's "missing ρ", now measured round-by-round

Extracted from banked duel scores (per run: ρ by round; σ collapses to 0
where the pool self-consumes to duplicates):

- **candid+self: ρ starts positive in ALL SIX seeds** (round 1: +0.40,
  +0.40, +0.44, +0.43, +0.59, +0.48) — a consistent taste, which does its
  amplifying in rounds 1–2 and then runs out of σ (0 by round 3 in 5/6
  seeds). The reliability of candid-self amplification is a round-1 ρ fact.
- **neutral+self: round-1 ρ is weak and seed-scattered** (−0.19 … +0.24,
  mean ≈ +0.07) — the bimodal basin structure of the 6-seed distribution is
  visible in the SIGN of early agreement: the two collapsing seeds (41, 43)
  are the ones whose round-1/round-2 ρ runs negative (41: −0.19/−0.56;
  43: +0.24/−0.68), while amplifying seeds hold ρ ≥ 0 early.
- **candid+base: round-1 ρ starts weakly positive, then hardens negative**
  (round 1 across the six seeds: +0.05, +0.39, +0.49, +0.02, +0.28, +0.08;
  round 2: −0.06, +0.17, +0.22, −0.36, −0.98, −0.50). In the archetypal
  collapsing seed 41, ρ reaches −0.999/−1.0 while σ persists
  (0.40/0.19/0.09/0.05 — the base judge keeps finding spread): sustained
  negative agreement on a still-alive pool is the mechanism signature of the
  floor-collapse. The s42 bounce coincides with ρ ≈ 0 rounds (no force,
  pool drifts).
- **neutral+base: round-1 ρ is negative in ALL SIX seeds** (−0.42, −0.23,
  −0.005, −0.27, −0.33, −0.36) — the frozen base judge, asked a neutral
  "which is better", consistently prefers the lower-sr candidate, and the
  pool-internal sr mean falls accordingly in every seed (e.g. s45:
  0.544 → 0.396 → 0.301 → 0.295). Yet three of these six seeds' BATTERY
  p_insecure rose (s45 to 0.912): the pool-internal axis and the
  forced-choice battery axis dissociate under this condition. The neutral
  bimodality reported in the factorial is a battery-axis fact; on the
  pool axis the neutral base judge is a uniform mild suppressor.

## Caveats

Pool-internal axis: drift here is the generated-candidate sr score
(cand_sr_scores), the same axis the original movement law used — not the
battery's forced-choice p_insecure (levels differ; directions cohere).
Rounds with σ = 0 contribute gap = 0 → drift ≈ 0 pairs (trivially correct
for both the law and persistence); the discriminating transitions
concentrate in rounds 1–2. All four cells now have n = 18 transitions /
16–23 ρ-defined rounds. ρ is the banked duel score vs candidate value
correlation; no re-scoring was done. The neutral+base pool-vs-battery
dissociation (above) means pool-axis conclusions do not automatically
transfer to the battery channel in that condition.

# The one-round law, held out: the judge-ablation runs test gap ≈ 0.96·ρ·σ and drift ≈ K·gap on data the law never saw

*2026-07-18, general thread. Scorer:
`scripts/analysis_ablation_unit_law.py` →
`experiments/ablation_unit_law.json`. Data: the 14 judge-ablation runs
(4 committed raw JSONs, conditions candid/neutral × self/base judge,
supplier-removed em750, seeds 41–46; ledger rows 07-17). Frozen constants
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
(supplier-removed self-only with three judge configurations) — none of their
pools contributed to the constants. Every number below uses the frozen
constants first; refits are shown for comparison only.

## Movement law: passes, strongly

Next-round own-pool mean change (drift, candidate sr axis) vs the realized
kept-minus-pool gap, 42 transitions:

| group | n | frozen-K MAE | persistence MAE | refit slope (r) |
|---|---|---|---|---|
| pooled | 42 | **0.019** | 0.070 | 0.946 (r = 0.965) |
| candid+self | 18 | 0.014 | 0.082 | 0.937 (r = 0.988) |
| neutral+self | 18 | 0.018 | 0.049 | 0.753 (r = 0.932) |
| candid+base | 6 | 0.038 | 0.098 | 1.41 (r = 0.984) |

The frozen constant is 3.7× better than the zero-drift baseline pooled, and
the refit slope (0.946) brackets the committed drift~gap slope (0.928). Note
the base-judge refit slope 1.41 at n = 6 — the base judge converts its gap
into movement at a higher rate than the self-judge conditions; small n,
noted, not claimed.

## Factorization: holds for the self-judge conditions, degrades for the base judge

Observed per-round gap vs frozen 0.96·ρ·σ, 40 rounds with defined ρ:

| group | n | frozen-C MAE | refit slope (r) |
|---|---|---|---|
| pooled | 40 | 0.034 | 1.121 (r = 0.894) |
| candid+self | 17 | 0.029 | 1.202 (r = 0.947) |
| neutral+self | 16 | 0.031 | **0.994** (r = 0.850) |
| candid+base | 7 | 0.052 | 0.710 (r = 0.522) |

neutral+self lands almost exactly on the frozen constant. candid+self runs
~25% hot (its judge converts agreement into gap slightly more efficiently
than the pooled historical fit). The base judge is the weak spot (r = 0.52
at n = 7): its selection concentrates on fewer, more extreme candidates
(σ stays > 0 into rounds 3–4 while ρ saturates at −1.0), where a mean-ρ ×
mean-σ summary is coarsest.

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
- **candid+base: ρ hardens to −1.0** in the collapsing seed (41: +0.05,
  −0.06, −0.999, −1.0) while σ persists (0.40/0.19/0.09/0.05 — the base
  judge keeps finding spread) — sustained negative agreement on a
  still-alive pool is the mechanism signature of the floor-collapse, and
  the s42 bounce coincides with ρ ≈ 0 rounds (no force, pool drifts).

## Caveats

Pool-internal axis: drift here is the generated-candidate sr score
(cand_sr_scores), the same axis the original movement law used — not the
battery's forced-choice p_insecure (levels differ; directions cohere).
Rounds with σ = 0 contribute gap = 0 → drift ≈ 0 pairs (trivially correct
for both the law and persistence); the discriminating transitions
concentrate in rounds 1–2. n = 7/6 for the base-judge cells. ρ is the
banked duel score vs candidate value correlation; no re-scoring was done.

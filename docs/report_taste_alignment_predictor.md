# Taste alignment ρ and supply σ: descriptive selection accounting, not a validated runaway model

*2026-07-14, general thread; user proposal: "the degree to which the way the
judge decides among generator answers with value spread is correlated with
the value" as a runaway predictor. Committed scorer:
`scripts/analysis_taste_alignment_predictor.py` →
`experiments/taste_alignment_predictor.json`. Data: the 25 K1+K2 rollouts (13 OLMo + 12 Qwen)
with per-round judge score vectors (random arms have no scores and are
excluded).*

## Definitions

- **ρ (alignment)** = mean within-item Pearson correlation between the
  judge's candidate scores and the candidates' value scores — exactly the
  user's proposed quantity.
- **σ (supply)** = mean within-item candidate-value SD (the prereg spread).
- **gap** = realized kept-minus-pool value mean (what training sees).

## 1. Descriptive factorization: gap ≈ 0.98 · ρ · σ (r = 0.82, 100 rounds)

The fitted calibration is `gap = 0.981·ρ·σ` in this 100-round subset, so the
unit proxy `gap≈alignment×supply` is adequate. This is useful bookkeeping for
the realized selection step, not independent evidence for a causal runaway
model. The exact Price identity uses the retained-set indicator; judge-score
correlation is a predictive proxy. The previously drawn 0.95 normal-order-
statistic line was scale-mismatched because it uses the underlying normal SD,
not the realized six-candidate SD used here. The factorization says when a gap
can be expressed, not whether it will persist or create a runaway.

## 2. ρ is the stabler factor; σ is the slowest state variable

Lag-1 autocorrelation across rounds: σ **0.82**, ρ 0.39, gap 0.27. For
forecasting the next round's gap, ρ·σ edges the gap itself (corr 0.29 vs
0.27). Reading: supply is the slow state (it decays or survives over whole
runs — the intervention-window result in different clothes), alignment is
semi-stable, and the realized gap is their noisy product.

## 3. Exploratory round-1 association (not a validated warning signal)

Correlation of round-1 measures with the run's remaining pool drift:

| grid | ρ₁ | σ₁ | gap₁ | ρ₁·σ₁ |
|---|---|---|---|---|
| K2 OLMo (13 runs) | 0.48 | −0.39 | 0.39 | **0.55** |
| K1 Qwen (12 runs) | **0.51** | −0.08 | 0.38 | 0.50 |

The alignment product has the largest correlation in these two small grids.
These are in-sample correlations over 13 and 12 runs, with conditions pooled;
they are not a validated forecasting result and should not carry the mechanism
narrative. The negative σ₁ association also does not show that supply is
protective; wide early pools often settle in this sample.

## 4. The honest limit: alignment is endogenous — it can BLOOM mid-run

Ranking the six frozen_base runs by round-1 measures, gap₁ actually places
the two eventual runaways [1st, 2nd] while ρ₁ places them [1st, 3rd]:
runaway seed 5's alignment was ~0 in round 1 (ρ₁ = 0.012) and only emerged
as the run progressed (ρ: 0.01 → 0.21 → 0.27) — the generator drifted into
the judge-favored region, and no fixed early snapshot can see that coming.
(n = 2 runaways; treat all rankings as illustrative.) Crucially, settled seed
0 is a counterexample to the stronger story: its ρ rises 0.12→0.40→0.46 and
it has two late beyond-chance selection rounds, but it ends at 0.08. Thus a
rising running ρ_t·σ_t is neither a demonstrated runaway signature nor a
validated alarm. What the trace does establish is narrower: even with a
frozen judge, pool-relative score-value alignment can change as the generator
changes.

## Practical recommendation

For descriptive analysis, report (ρ_t, σ_t, gap_t) separately: σ_t describes
available value variation, ρ_t describes local score-value association, and
gap_t records the selection actually applied. Do not call ρ a detector of
generator-side exploitation or use it as the writeup's predictive spine on
the present sample. The more important untested hypothesis is cross-judge
transfer: whether agreement between the source judge and a recipient judge,
measured on the same pool in the same format and conditional on candidate
risk, predicts which source text the recipient keeps and how much it moves.

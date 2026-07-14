# Taste alignment ρ (and supply σ) as the gap's factors: a better early-warning signal, with one honest limit

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

## 1. The gap factorizes: gap ≈ 0.98 · ρ · σ (r = 0.82, 100 rounds)

Order statistics predicts E[gap] = c·ρ·σ with c ≈ 0.95 for keep-top-2-of-6
under Gaussian scores; the fitted c is 0.981. So the realized selection gap
IS alignment × supply plus round noise — ρ and σ are its factors, and the
runaway story splits cleanly into "alignment exists" (ρ>0) and "material
exists" (σ>0), which the loop must jointly sustain.

## 2. ρ is the stabler factor; σ is the slowest state variable

Lag-1 autocorrelation across rounds: σ **0.82**, ρ 0.39, gap 0.27. For
forecasting the next round's gap, ρ·σ edges the gap itself (corr 0.29 vs
0.27). Reading: supply is the slow state (it decays or survives over whole
runs — the intervention-window result in different clothes), alignment is
semi-stable, and the realized gap is their noisy product.

## 3. As a round-1 early-warning signal, the user's measure beats the raw gap

Correlation of round-1 measures with the run's remaining pool drift:

| grid | ρ₁ | σ₁ | gap₁ | ρ₁·σ₁ |
|---|---|---|---|---|
| K2 OLMo (13 runs) | 0.48 | −0.39 | 0.39 | **0.55** |
| K1 Qwen (12 runs) | **0.51** | −0.08 | 0.38 | 0.50 |

The alignment product is the best single round-1 forecaster in both grids
(and note σ₁ alone is *negatively* related to remaining drift — wide early
pools mostly settle; supply without alignment does nothing, which is the
random-arm result again).

## 4. The honest limit: alignment is endogenous — it can BLOOM mid-run

Ranking the six frozen_base runs by round-1 measures, gap₁ actually places
the two eventual runaways [1st, 2nd] while ρ₁ places them [1st, 3rd]:
runaway seed 5's alignment was ~0 in round 1 (ρ₁ = 0.012) and only emerged
as the run progressed (ρ: 0.01 → 0.21 → 0.27) — the generator drifted into
the judge-favored region, and no fixed early snapshot can see that coming.
(n = 2 runaways; treat all rankings as illustrative.) Consequence: the right
monitoring quantity is the **running** ρ_t·σ_t, not an initial screen — and
a rising ρ_t under a *frozen* judge is itself the runaway signature, visible
a round before the pool rails (seed 5: ρ jumps at r2, pool rails r3–r4).

## Practical recommendation

For loop monitoring, track (ρ_t, σ_t) as separate state variables instead of
the scalar gap: σ_t tells whether selection CAN act (window open/closed),
ρ_t tells whether it WILL act directionally, their product forecasts the
force, and ρ_t's trend under a frozen judge detects generator-side
exploitation. For duel-format judges (no score vectors), the analog of ρ is
the cross-pair win-versus-value correlation; not yet implemented — noted as
the missing piece for h2h cells.

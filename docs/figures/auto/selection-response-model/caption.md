# Spread, agreement, and the selector gap they forecast

**The two dials (top).** The forecast of what one round of selection does uses
only two per-round measurements, shown as marks rather than sentences. *Dial 1 —
spread σ*: how much variation the candidate pool offers, drawn as a narrow pool
(candidates clustered, small σ) versus a wide pool (candidates spread out, large
σ), where σ is the mean across prompts of the population standard deviation
(divide by n) of a prompt's candidate value scores — each prompt's pool
measured on its own, then averaged equally over the round's prompts.
*Dial 2 — agreement ρ*: how consistently the judge keeps one side of the same
wide pool, from keeping at random (ρ ≈ 0) to keeping the low side (ρ → −1);
ρ is the within-prompt correlation of the judge's scores with the candidates'
value scores, averaged over the round's prompts, and is in practice a property
of the judge × alternative-source × candidate-source condition (82% of its
variance is between conditions). Multiplying the two round-averaged dials
gives the forecast `ρσ`, the horizontal axis of the scatter.

**The evidence (bottom).** Scatter of the observed selector gap `g`
(kept mean − pool mean) against the forecast `ρσ` over the 290 agreement-scored
per-round records (x = `rho`·`spread`, y = `gap`, recomputed in the generator
and asserted against the stored aggregates). The **unit-slope line `gap = ρσ`
is the headline** — R² 0.810, mean absolute error 0.042. One-round-ahead value forecast
(not drawn): predicting the next value before selection with the unit rule
`ρσ` gives mean absolute value error 0.0902, versus 0.0854 when the kept set
is observed first (leave-one-condition-out).

Two honesty notes carried in words, not drawn: `ρσ` is a *forecast* of the
selector gap `g`, accurate here (R² 0.810) but not an identity — the exact gap
depends on which candidates the judge actually keeps, which ρ only predicts;
and the retracted **0.9545** "theoretical" coefficient is deliberately absent
because it is computed against the underlying normal SD rather than the realized
six-candidate population SD used throughout this project, making its closeness to
the 0.958 empirical slope a scale-mismatched coincidence (scale audit in the
predictor JSON). The loop mechanics (number-line view) and the frozen-boundary
endpoint recurrence are shown in separate figures.

## Source data
- `experiments/selection_response_predictor.json` — aggregates (selector-gap
  R²/MAE, one-round MAE for the unit rule and for the observed-kept-mean
  leave-one-condition-out comparator, scale audit), produced by
  `scripts/analysis_selection_response_predictor.py`.
- `experiments/spread_util_unified.json` — the 290 agreement-scored per-round
  records (`rho`, `spread`, `gap`) used for the scatter; `rho` is null on
  excluded rounds and those are dropped.
- Narrative and literature framing: `docs/report_predictive_model_literature.md`.

Regenerate: `python3 selection-response-model.py` (stdlib only; asserts every
plotted aggregate against the two JSONs).

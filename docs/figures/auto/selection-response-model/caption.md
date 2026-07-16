# Selection converts offered variation into movement — with no fitted constants

**The model (top).** One turn of the selection loop has three operations.
(1) *Generate a pool*: each prompt yields candidate value scores with mean `p`
and within-prompt spread `σ` (σ = the mean across prompts of the population SD,
ddof 0, of its candidate scores). (2) *Select a retained set*: a signed
value-axis selection intensity `a` converts variation into the selector gap
`g = σ·a` exactly, where `a` is the realized standardized selection differential
(kept mean − pool mean)/σ; before selection the forecast substitutes `â = ρ`,
the pre-selection judge/value agreement — a compact proxy for `a`, not an
identity. (3) *Refit*: the kept mean `k = p + g` is the next model's target, so
`v_next ≈ k`, and `k − host mean` is the training displacement (which also
carries any supplier shift). Mixed pools add a supplier inlet:
`pool mean = (1−u)·host mean + u·supplier mean`. Iterating with a frozen
selection boundary gives the endpoint recurrence
`m_next = clip((1−u)·m + u·supplier + ρσ, 0, 1)`. The cross-entropy method is
an *algorithmic analogue* (sample → keep elites → update mean and variance),
not the same algorithm: elite refitting narrows the candidate distribution and
an outside-supplier arrow reopens its support.

**The evidence (bottom).** Scatter of the observed selector gap `g`
(kept mean − pool mean) against the forecast `ρσ` over the 290 agreement-scored
per-round records (x = `rho`·`spread`, y = `gap`, recomputed in the generator
and asserted against the stored aggregates). The **unit-slope reference line
`gap = ρσ` is the main visual**: unit proxy R² 0.810, MAE 0.0421, with no fitted
constants. The full-data calibration fit `−0.002 + 0.958·ρσ` (faint dashed) is
plotted only for reference and nearly coincides with the unit line. One round
ahead, forecasting `v_next` gives value MAE 0.0902 with the unit proxy versus
0.0891 with the fitted line — the extra constant buys nothing. Endpoints under
the unit recurrence with boundary refresh: selection-driven endpoints MAE 0.118
(36 runs); judge swaps MAE 0.210 (9 runs), shown next to the fitted frozen-SD
comparator 0.179 so the remaining swap weakness stays visible; combined
MAE 0.1365 with 37/38 large moves pointed the right way (that count reads
judge-swap runs from the swap boundary where the rollout starts; under the
round-1 convention used for the fitted comparator, both models score 36/38 —
see `docs/report_unit_rollout_properties.md`). `ρ` is a proxy for the
realized intensity `a`, and the unit coefficient is a parsimonious empirical
choice rather than a derived constant. The retracted **0.9545** "theoretical"
coefficient is not drawn: it uses the underlying normal SD, not the realized
six-candidate population SD used throughout this project, so its match to the
0.958 empirical slope is a scale-mismatched coincidence (scale audit in the
predictor JSON).

## Source data
- `experiments/selection_response_predictor.json` — aggregates (selector-gap and
  one-round MAE/R², fitted equation, endpoint MAEs, scale audit), produced by
  `scripts/analysis_selection_response_predictor.py`.
- `experiments/spread_util_unified.json` — the 290 agreement-scored per-round
  records (`rho`, `spread`, `gap`) used for the scatter; `rho` is null on
  excluded rounds and those are dropped.
- Narrative and literature framing: `docs/report_predictive_model_literature.md`.

Regenerate: `python3 selection-response-model.py` (stdlib only; asserts every
printed aggregate against the two JSONs).

**The dial → direction forecast, split by model family.** This is the by-family
variant of `synthesis-dial-plane-horizon`. Both panels plot each 4-round run at
its round-1 dials — the horizontal axis is round-1 agreement ρ (the correlation
between the judge's scores and the candidates' behavioral-value scores, −1
disagree → +1 lockstep) and the vertical axis is round-1 spread σ (the
within-prompt standard deviation of value scores across the candidate pool). Each
dot is filled by the run's OBSERVED whole-run endpoint move of the behavioral
value (final measured value − round-1 value) on a continuous red-up / gray-none /
blue-down diverging scale saturating at ±0.6. The background of BOTH panels is the
identical painted FORECAST of the committed self-only recurrence's endpoint move,
`Δv_pred(4) = clip[−1,+1] of 4·ρ·σ` (one selection step ρσ compounded per round
over the modal 4-round horizon, capped at the value wall), drawn on the dots' own
color scale; a dot whose color matches the gradient behind it is the forecast
holding, a clash is it failing. The left panel is the 25 Qwen3-4B runs, the right
panel the 31 OLMo-3-7B runs (25 + 31 = 56), split on the `organism` field of each
run's round-1 record. **The split shows the sign story holds in both families but
much more tightly in Qwen: of the movers (|observed move| ≥ 0.15), Qwen3-4B is
unanimous at 17 of 17 (100%) concordant while OLMo-3-7B is 18 of 24 (75%) — OLMo
carries every one of the pooled corpus's 6 sign clashes, all 6 sitting in its own
panel.** Scope is 4-round runs only, so R = 4 is every plotted run's exact
horizon: the 11 eight-round judge-schedule runs are excluded and 7 runs are
skipped for undefined ρ (zero within-pool spread), leaving 56 of the 74 total
runs. Mixed-pool runs also feel the outside-source pull (p − q), so the 4·ρσ
background is the self-only force map — sign and relative magnitude are what
compare, not each run's exact per-run forecast.

Source data: `experiments/spread_util_unified.json` (records list; one run =
the (cond, seed, source) tuple; round-1 record supplies ρ, σ, value and the
`organism` label; last record supplies value + drift). All counts, the panel
split, and the per-family concordance are computed live in the generator with
assertions (74 total, 11 excluded, 7 skipped, 56 plotted = 25 Qwen + 31 OLMo;
Qwen 17/17, OLMo 18/24, pooled 35/41).

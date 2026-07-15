# movement-toward-kept-v2

Each selection-loop round, the measured value moves about 80% of the way toward
the mean of the answers the judge kept. One dot per score-logged round (340
rounds from 74 selection-loop runs: OLMo and Qwen organisms, risk and
self-report value axes, self and frozen judges). The x axis is the pull — the
kept answers' mean value-score minus the model's measured value at the start of
the round; the y axis is the drift — the measured value after the round's
fine-tune minus the value at the start of the round, both on the same 0-to-1
value axis. The solid line is the pooled least-squares fit, drift = 0.833 ×
pull − 0.007 (r = 0.801, n = 340); the dashed line is drift = pull, i.e.
moving the whole distance in one round. Dot color marks where the round's
candidate pool came from: self-only (the organism's own sampled answers),
base-mixed (base-injected runs where the base model supplies half the pool),
peer-mixed (head-to-head invasion runs where an extreme peer organism supplies
half). One relationship covers all three pool sources; this is a descriptive
association, not a mechanism claim.

Source data: `experiments/spread_util_unified.json` (`records` for the dots,
`movement_law.pooled.drift_vs_pull` for the fitted line; the generator
recomputes the fit from the raw records and asserts it matches before drawing).
Simplified single-panel replacement for
`docs/figures/auto/movement-toward-kept/`.

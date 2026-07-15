# Measure once and roll forward: forecast error stays flat until the judge changes

Forecast error, measured as the held-out-condition mean absolute error of the
predicted behavioral value (0–1 scale, one prediction per run at each horizon,
averaged over runs), plotted against forecast horizon — the number of rounds
ahead of the first measured answer pool — for simple models of self-training
selection loops (Qwen + OLMo). **Left panel, selection-driven runs (36 runs):**
predicting the starting value forever (no change, gray) gets steadily worse with
horizon (0.31 → 0.44), while measuring the run once at round 1 and rolling the
frozen selection model forward (blue) stays flat around 0.10–0.13 because the
trajectories saturate; re-measuring the kept-answer mean every round (green)
sits a little lower still. At one round ahead both models see the same pool, so
their gap (~0.03) is purely the cost of predicting the selection instead of
observing it. **Right panel, judge-swapped runs (9 runs, 8 rounds):** horizon
genuinely hurts — the frozen measure-once model (blue) climbs to ~0.40 as the
new judge pulls the run somewhere its round-1 state cannot anticipate, tracking
or exceeding no-change (gray) — but a single re-measurement at the swap (orange)
buys back most of that loss (endpoint ~0.18), and re-measuring every round
(green) stays low throughout. The swap happens somewhere in rounds 2–5 depending
on condition.

**Reading rule.** The re-measuring models (green, and orange after the swap)
condition on each round's *observed* answer pool, information the measure-once
model is not given; their advantage is therefore the value of monitoring, not a
better model.

**Source data.** `scripts/analysis_model_ladder_horizon.py` →
`experiments/model_ladder_horizon.json` (the `table` records, regime groups
`selection_driven` and `judge_swap`; models `no_change`, `closed_frozen`,
`one_step_kept_mean`, `refresh_at_swap`). Method and anchors in
`docs/report_model_ladder_horizon.md`. The generator
`model-ladder-horizon.py` reads the JSON and asserts every plotted value before
drawing.

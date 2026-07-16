# Forecast error by horizon, under three measurement schedules

Forecast error, measured as the held-out-condition mean absolute error of the
predicted behavioral value (0–1 scale, one prediction per run at each horizon,
averaged over runs), plotted against forecast horizon — the number of rounds
ahead of the first measured answer pool — for simple models of self-training
selection loops (Qwen + OLMo). Each model is given the run's state on one of three
measurement schedules: once at round 1 (the measure-once models "no change", the
unit recurrence, and the fitted comparator), at every round (the re-measured
models), or once plus once at the judge swap ("one refresh at swap"). The
in-figure end labels are shortened for legibility; their full identities are:
"no change" = predict the round-1 value forever; "measured once (unit recurrence)"
= the parameter-free unit recurrence launched once at round 1; "fitted comparator"
= the one-parameter frozen selection model measured once at round 1; "re-measured
every round" = predict each round's observed kept-answer mean; "measured once"
(right panel) = that same frozen selection model; "one refresh at swap" = the
frozen rollout re-launched once from the first pool the new judge scores.
**Left panel, selection-driven runs (36 runs):**
predicting the starting value forever (no change, gray) gets steadily worse with
horizon (0.31 → 0.44), while the **unit recurrence measured once at round 1**
(purple, the primary line) stays flat around 0.10–0.13. This unit recurrence has
**zero fitted parameters** — its update is `next mean = clip((1−u)·mean +
u·supplier + agreement×spread, 0, 1)` with the kept-mean identity for the next
value — yet it tracks, and slightly beats, the previously-drawn one-parameter
frozen selection model (blue dashed, "measured once, fitted comparator";
0.135/0.110/0.104/0.126). The unit recurrence covers 32 of the 36 runs — four
glued grid entries whose sequential-rollout alignment is ambiguous are excluded.
Re-measuring the kept-answer mean every round (green) sits a little lower still.
On the same runs (the 32 with the four glued entries removed), predicting the
selection instead of observing the realized kept set costs about **0.015** more
error for the unit recurrence and **0.023** for the fitted comparator (kept-mean
0.0849, unit 0.0999, fitted 0.1079); the pooled 0.033 figure quoted earlier was
inflated by the glued runs, which only the fitted models cover.
**Right panel, judge-swapped runs (9 runs, 8 rounds):** horizon genuinely hurts
— the frozen measure-once model (blue) climbs to ~0.40 as the new judge pulls the
run somewhere its round-1 state cannot anticipate, tracking or exceeding no-change
(gray) — but a single re-measurement at the swap (orange) buys back most of that
loss (endpoint ~0.18), and re-measuring every round (green) stays low throughout
(~0.04). The swap happens somewhere in rounds 2–5 depending on condition. The
unit recurrence is not drawn here (its post-swap conditional forecast covers
different rounds per condition), but it ends the judge-swap slice at 0.210 — so
the swaps are the one place where the fitted frozen-SD model keeps an advantage
over the parameter-free unit recurrence.

**Reading rule.** The re-measuring models (green, and orange after the swap)
condition on each round's *observed* answer pool, information the measure-once
models are not given; their advantage is therefore the value of monitoring, not a
better model.

**Reproduction.** All five published anchors reproduce off the regenerated file
(frozen endpoint 0.127, no-change endpoint 0.431, kept-mean pooled 0.081, unit
recurrence matched endpoint 0.118, unit recurrence combined-45 endpoint 0.1365).
The unit recurrence carries no fitted parameters; a descriptive calibrated variant
that scales the spread term by 0.958 differs by less than 0.001 at every horizon.

**Source data.** `scripts/analysis_model_ladder_horizon.py` →
`experiments/model_ladder_horizon.json` (the `table` records, regime groups
`selection_driven` and `judge_swap`; models `no_change`, `closed_unit`,
`closed_frozen`, `one_step_kept_mean`, `refresh_at_swap`; matched-set gap under
`h1_predicting_vs_observing_selection_gap.matched_set_excluding_glued`; anchors
under `anchors`). The unit-recurrence trajectories originate in
`experiments/selection_response_predictor.json`. Method and anchors in
`docs/report_model_ladder_horizon.md`. The generator `model-ladder-horizon.py`
reads the JSON and asserts every plotted value before drawing.

# A preregistered forecast called the supplier-removed arms flat — and they were

The program's first forward, out-of-time test of its simple selection model. A
forecast was committed mid-run — before the supplier-removed control arms
finished — from round-1 logged state alone: the kept-insecurity spread (0.060)
and the generator–judge agreement (−0.17), rolled forward with the bakeoff's
best unseen-condition configuration. It predicted the control arms would stay
roughly flat, about a fifth of the erosion seen in the matched supplier-present
run.

**Panel A (the forward call, seed 71, in-domain, live frozen-base insecurity
0–1):** the matched supplier-present run erodes 0.854 → 0.728 (red), while both
supplier-removed arms hold — reference-vs-secure 0.854 → 0.860 (green),
self-duels 0.854 → 0.848 (blue). The preregistered forecast for the reference
arm (dashed, 0.854 → 0.831) landed with the observed endpoint 0.860 inside its
±0.10 band; absolute endpoint error 0.029, per-round mean absolute error 0.025.
**Panel B (all eight supplier-removed cells):** each arm × seed × bank's absolute
move (endpoint − baseline) against its own threshold (half the matched run's move
on that cell); 7 of 8 pass, the one exception being the reference arm's seed-71
held-out bank at 0.070 vs a 0.069 threshold — over by 0.001. **Verdict strip:**
P-A (forecast band) pass · P-B (per-cell stability) 7 of 8 · P-C (self-pool
round-1 spread 0.060 / 0.051 < 0.15, as predicted for self-only pools) pass;
overall the forecast held.

Instrument caveat: the plotted coordinate is the declared live frozen-base
diagnostic (flagged, low-specificity). Blind manual severity agrees in-domain —
the control arms average about +0.02 vs the matched run's −0.15 / −0.29 — with
one discordant cell: the reference arm's seed-71 held-out bank fell −0.28 on
manual severity while its live coordinate moved only 0.07. n = 2 arms × 2 seeds,
one organism family — one passed forward test, not a forecasting record.

## Source data
- Forecast: `experiments/control_arm_prospective_predictions.json` (prereg:
  `docs/prereg_control_arm_prospective_forecast.md`)
- Scored outcome: `experiments/control_arm_forecast_score.json`, produced by
  `scripts/analysis_control_arm_forecast_score.py` (report:
  `docs/report_control_arm_forecast_score.md`)
- Observed trajectories (live `organism_baseline`/`organism_round_1..3`
  `live_llm_mean_FLAGGED`):
  `experiments/olmo_insecure/output/olmo_code_security_static_reference_v1_analysis.json`
  (reference-vs-secure arm),
  `olmo_code_security_self_pool_duels_v1_analysis.json` (self-duels arm),
  `olmo_code_security_duel_loop_v2_analysis.json` (matched supplier-present run).

Every quoted value is asserted against these files in the generator; regenerate
with `python3 control-arm-forecast.py` from this directory.

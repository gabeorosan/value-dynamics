**A frozen kept-gap → drift model predicts next round's pool drift on rollouts it never saw.**
Predictor M2 — a per-judge-condition intercept plus the pooled kept-gap slope (≈0.75, the same
coupling shown descriptively in fig17_loop_integrator, fit on 51 round-to-round transitions from the
K2 grid) — was frozen on 2026-07-12 and then scored, unrefit, against three later rollout sets. Panel A
compares its RMSE (root-mean-squared error of next-round pool-risk drift) to a separately and properly
refit no-gap comparator (same per-condition intercepts, gap term removed) on each set: kernel B
(n=35 transitions, fully blind — neither trajectory was inspected before freezing) −17.3%, Modal
branch A (n=35, partially blind — partial trajectories to round 7 were inspected pre-freeze, only
round 8 and final scoring were held out) −31.1%, and press-depth branch c (n=42, fully blind) −42.0%,
its strongest test to date. Panel B plots predicted vs. observed drift for all 42 press-depth
transitions against the y=x line. This validates prediction, not stability: no experiment has perturbed
a kept-gap and measured the closed-loop response, so no stability boundary or k-below/above-1 regime is
claimed. Data honesty note: the press-depth report (docs/report_press_depth_boundary.md) originally
quoted −45.0% for this same 42-transition test; that number was measured against an invalid,
joint-fit-derived "no-gap" ablation. −42.0%, recomputed here (and independently reproduced by
scripts/score_press_depth_prereg.py) against the properly-refit no-gap comparator
(experiments/release_predictor_nogap_frozen.json), supersedes it — consistent with the report's own
07-13 audit-correction section. The release-grid report's ~−42% figure quoted in this figure's prompt
does not appear in docs/report_release_grid_results.md itself, which instead reports the kernel B
(−17.3%) and Modal branch A (−31.1%) numbers shown here; this figure plots the three published,
file-verified numbers rather than the prompt's summary.

Source data (all RMSE numbers recomputed live by analysis-frozen-predictor.py, not copied from prose):
`experiments/release_predictor_frozen.json`, `experiments/release_predictor_nogap_frozen.json`,
`experiments/kaggle/kaggle_k2_release_relB/output/k2_release_kernelB.json`,
`experiments/modal_k2_release/output/k2rel_press_to_base_s{1,2,3}.json`,
`experiments/modal_k2_release/output/k2rel_base_hold_s{1,2}.json`,
`experiments/modal_k2_release/output/k2rel_press_d{1,2,3}_s{1,2}.json`. Cross-checked against
`docs/report_release_grid_results.md` and `docs/report_press_depth_boundary.md`
(including its 07-13 audit-correction section) and reproduced by `scripts/score_press_depth_prereg.py`.

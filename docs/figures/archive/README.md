# Retired figures

Figures moved here are no longer part of the active set and will not appear in
the main research write-up (owned by a separate thread). They are preserved for
git history and reference; their generators remain in `../make_figures.py` but
are no longer emitted by its `__main__` loop.

## Retired 2026-07-12 (Figures thread) — forward-looking planning/status figures superseded by results

These four were "what runs next" planning figures. The experiments they
previewed have since run, been cut, or been superseded, so the current planning
picture lives in the plan-figure set (`../plan/`) and the results live in
fig16/17/18.

| File | Was | Why retired |
|---|---|---|
| `fig12_experiment_map.svg` | "The experiment map: what runs next — status 2026-07-09 evening" | a dated status snapshot; superseded by `../plan/plan_program_map.svg` + `../plan/plan_final_sprint.svg` |
| `fig13_next_regime_grid.svg` | "Next on Modal: the regime grid" | the regime grid was CUT on the no-saddle result; Modal is retired (PLAN "Out of the sprint") |
| `fig14_next_round0_copy_judge.svg` | "Next on Kaggle: the round-0-copy judge" | ran as K1's `frozen_copy_r0` arm; superseded by the K1 results figure `../fig16_k1_anchor_fan.svg` |
| `fig15_next_content_arms.svg` | "Next on Colab: external-data content arms" | this is K4, deferred / not reached in the sprint; carries to a later window, so a "Next on Colab" framing is stale |

## Retired 2026-07-12 (Figures thread) — legacy result figures superseded by newer results or re-audit-retired framing

| File | Was | Why retired |
|---|---|---|
| `fig3_judge_determines_dynamics.svg` | "Same loop, same settings — the judge's identity decides whether the outcome is predictable" | states a determination on the legacy, partly position-confounded coordinate (deep audit: motivation, not a clean result); the clean version is K1/K2/K3 (`../fig16`/`17`/`18`) on the repaired coordinate, and the re-audit reframed it as a descriptive judge-dependence, not a law |
| `fig6_packet_rating_measurement.svg` | "How the packet-rating score is measured" | a measurement-recipe figure for one legacy probe (personalization packets); not cited in the STATE headline results, and measurement principles are now covered by the methods figure set (`../methods/`) |
| `fig11_engine_filters_regimes.svg` | "What drives value change under self-training — and where the unpredictable zone lives" | a synthesis built on the basin / "unpredictable zone" / regime framing that the no-saddle result and the post-Claude re-audit walked back; the current synthesis is the descriptive kept-gap → pool-drift coupling (`../fig17`) |

## The active numbered set (2026-07-12)

Foundational: `fig1_research_goal`, `fig2_selftraining_loop`. Stable legacy
findings (cited in STATE headline results): `fig4_selection_ablations`,
`fig5_boldprose_unpacked`, `fig7_rhetoric_gates_transfer`, `fig8_dose_ladder`,
`fig9_selfdata_mixing`, `fig10_offtarget_drift`. Sprint results:
`fig16_k1_anchor_fan`, `fig17_loop_integrator`, `fig18_k3_selfreport_fan`.

Anything here can be recovered — the generators live in `../make_figures.py`
(fig1–15) and `../fig16/17/18_*.py`; only the emit list changed.

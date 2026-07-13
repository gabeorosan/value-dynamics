# Figure set

Plain-language house style: each figure states its finding in the title, names
the model and measure in one subtitle line, carries a compact visual protocol
strip, and lets axis + direct data labels do the rest. No experiment code names
(K1/K2/K3), no defensive/claim-limit framing — interpretation lives in the
writeup, the figures present setups, methods, and results.

- `*.svg` — the figures (SVG only)
- `src/*.py` — the generators (stdlib Python; each writes its SVG up into `../`)
- `archive/` — retired figures (recoverable from git history)
- `auto/` — figure-maker drafts (kept for provenance)
- `REDESIGN_PLAN.md` — the naming/numbering map + hard style rules

## Core numbered set (writeup order)

**The loop**
- `fig01_loop_generate_and_judge` — one round: generate answers, judge, select
- `fig02_loop_train_and_measure` — train on the kept answers, then measure

**Gambling model**
- `fig03_setup_gambling_model` — the model + the risk-seeking measure (setup)
- `fig04_selection_rule_sets_the_outcome` — the rule decides where risk lands
- `fig05_selection_gap_predicts_drift` — the gap this round predicts next round's drift

**Steering & undoing the drift**
- `fig06_setup_cautious_vs_neutral_judge` — the two judges (setup)
- `fig07_the_cautious_judges_pull` — the cautious judge keeps the safer answers
- `fig08_how_long_the_cautious_judge_holds` — a short cautious phase doesn't stop the rebound
- `fig09_reversing_the_trained_value` — reverses until the pool runs out of answers
- `fig10_shared_pool_slow_rescue` — injected safe answers help only if the judge keeps them
- `fig11_shared_pool_fast_contamination` — one risky source takes over in a single round
- `fig12_reversing_by_selection` — selection reverses a stuck model only where its answers vary
- `fig13_how_hard_the_judge_must_push` — only a scoring judge pulls a stuck value down
- `fig14_after_the_cautious_judge_stops` — schedules where the value stays at the floor
- `fig14b_neutral_judge_lets_it_climb` — schedules where a neutral judge lets it climb back

**Insecure-code model**
- `fig15_setup_insecure_code_model` — the model + the insecurity measure (setup)
- `fig16_self_report_of_insecure_code` — judging itself spreads out the self-report
- `fig17_passing_the_value_to_a_fresh_model` — a fresh model gives nothing to select on

## Synthesis figures (high-level, for the writeup)

- `synthesis_the_selection_loop` — graphical abstract: pool → variation → gap → train → repeat
- `synthesis_gap_beats_kept_score` — why the gap predicts better than the kept score alone
- `synthesis_intervention_window` — the 2D map: variation × judge grip
- `synthesis_shared_pool_asymmetry` — three lanes: slow rescue / failed / fast contamination
- `synthesis_window_through_time` — four small multiples: state + variation over rounds
- `synthesis_verify_grip_before_training` — the decision workflow

(Concept 7, the claim-robustness matrix, and concept 5 were intentionally not
built — 7 is defensive claim-limit framing that belongs in the writeup, not a
figure; 5 duplicates fig13.)

## Appendix — methods & validity (fig18+)

`methods_*` (10) and `analysis_*` (2) still carry the pre-redesign style (code
names, some defensive language). They are the next thing to transform to the
house style and number as the fig18+ appendix.

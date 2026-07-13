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
- `../figure_brief_entropy_predictive_update.md` — requested entropy propagation across the model, including the immediate and multi-round supply tests

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

## Synthesis figures (high-level, for the writeup)

- `synthesis_judges_defined` — the reference glossary: the answer pool (own vs mixed),
  head-to-head vs scoring, and the named judges. The others point here for terms.
- `synthesis_experiment_kit` — one loop, five interchangeable slots; every named
  experiment is one setting of the five
- `synthesis_the_selection_loop` — graphical abstract: pool → variation → gap → train → repeat
- `synthesis_source_selector_matrix` — outcome grid over answer source × judge
- `synthesis_matched_bottleneck_tests` — the same stalled/railed model under four interventions
- `synthesis_supply_leverage_destination` — where added answers go and what moves
- `synthesis_intervention_window` — the 2D map: variation × judge grip
- `synthesis_entropy_and_actionable_variation` — fresh-data and dose gradients, then why token entropy is not value-axis spread
- `synthesis_entropy_predictive_ablation` — entropy changes the generator but doesn't improve next-round drift prediction (held-out RMSE)
- `synthesis_entropy_longhorizon_supply` — an early entropy lead in one grid doesn't transport to longer horizons (later-supply RMSE + event contrast)
- `synthesis_shared_pool_asymmetry` — three lanes: slow rescue / failed / fast contamination
- `synthesis_state_space_trajectories` — trajectories drawn in state space
- `synthesis_window_through_time` — small multiples: state + variation over rounds
- `synthesis_cautious_judge_finetuning` — how the cautious judge is made (fine-tuned on cautious answers, then frozen)

### Dynamics (empirical dynamical-systems views)

- `dynamics_flow_self_vs_external` — self-judge fans out; a frozen outside judge converges
- `dynamics_equation_of_motion` — the value's change per round tracks the gap (drift ≈ 0.75 × gap)

(Concept 7, the claim-robustness matrix, was intentionally not built — it is
defensive claim-limit framing that belongs in the writeup, not a figure.)

## Appendix — methods & validity (fig18+)

`methods_*` (10) and `analysis_*` (2) are de-texted and in the house style: no
visible code names or defensive framing, plain model names ("the gambling
model", "the cautious-judge model"), finding-as-title. The remaining step is to
number them fig18+ once the writeup fixes the appendix order — deferred so the
numbers track the writeup rather than being guessed here.

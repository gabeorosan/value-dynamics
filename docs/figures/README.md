# Figure set

Plain-language house style: each figure states its finding in the title, names
the model and measure in one subtitle line, carries a compact visual protocol
strip, and lets axis + direct data labels do the rest. No experiment code names
(K1/K2/K3), no defensive/claim-limit framing — interpretation lives in the
writeup, the figures present setups, methods, and results.

- `*.svg` — the figures (SVG only)
- `src/*.py` — the generators (stdlib Python; each writes its SVG up into `../`)
- `src/make_gallery.py` — builds a self-contained HTML gallery of every active
  figure, ordered newest-first by first-commit date (archive/ and auto/
  excluded). The gallery artifact at
  https://claude.ai/code/artifact/5b8f47da-ef9d-45d8-b75e-1f4e68104ced is
  redeployed from its output after figure changes land.
- `archive/` — retired figures (recoverable from git history)
- `auto/` — figure-maker drafts (kept for provenance)
- `REDESIGN_PLAN.md` — the naming/numbering map + hard style rules
- `../figure_brief_entropy_predictive_update.md` — requested entropy propagation across the model, including the immediate and multi-round supply tests
- `../figure_brief_spread_geometry_update.md` — priority request: define spread as mean within-prompt population SD, then show selector gap → self-relative training displacement → own-generator mean → exact binary within/between-prompt variance split → next spread, with held-out benchmarks and the continuous-score scope boundary
- `../figure_brief_spread_rollout_bakeoff.md` — priority follow-up: show the complete-run LOCO forecast versus no change, compare spread definitions under geometry and frozen recurrences, and make visible that better spread trajectories do not yet improve endpoints because agreement is the missing state

## Core numbered set (writeup order)

**The loop**
- `fig01_loop_generate_and_judge` — one round: generate answers, judge, select
- `fig02_loop_train_and_measure` — train on the kept answers, then measure

Both organisms' setup now lives in the merged `synthesis_experiment_kit`
figure (the writeup's setup figure); the standalone per-model setups
`fig03_setup_gambling_model` and `fig15_setup_insecure_code_model` were
archived.

**Gambling model**
- `fig04_selection_rule_sets_the_outcome` — the rule sets the width of the fan, not its center
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
- `fig16_self_report_of_insecure_code` — judging itself spreads out the self-report

**Head-to-head duels (writeup slots)**
- `result_selfjudge_erosion` — judging its own duels on a mixed pool, the insecure-code model erases its value (0.666 → 0.000, 2 seeds)
- `result_reference_vs_duel` — same judge, same pools: judging against a fixed alternative vs duels decides whether rescue works; contamination survives both

## Synthesis figures (high-level, for the writeup)

- `synthesis_experiment_design_space` — the whole program as one coverage map:
  every run factored over base model × domain × installed value × answer pool ×
  judge, dots coloured by organism, sparse columns = untested corners. Traced to
  the committed specs/reports 2026-07-14.
- `synthesis_judges_defined` — the reference glossary: the answer pool (own vs mixed),
  head-to-head vs scoring, and the named judges. The others point here for terms.
- `synthesis_experiment_kit` — one loop, five interchangeable slots; every named
  experiment is one setting of the five
- `synthesis_the_selection_loop` — graphical abstract: pool → variation → gap → train → repeat
- `synthesis_source_selector_matrix` — outcome grid over answer source × judge
- `synthesis_intervention_window` — the 2D map: variation × judge grip
- `synthesis_entropy_and_actionable_variation` — fresh-data and dose gradients, then why token entropy is not value-axis spread
- `synthesis_entropy_predictive_ablation` — entropy changes the generator but doesn't improve next-round drift prediction (held-out RMSE)
- `synthesis_entropy_longhorizon_supply` — an early entropy lead in one grid doesn't transport to longer horizons (later-supply RMSE + event contrast)
- `synthesis_shared_pool_asymmetry` — three lanes: slow rescue / failed / fast contamination
- `synthesis_state_space_trajectories` — mechanism phase plot: every round of six
  interventions at its REAL (value spread, selection gap), computed by
  scripts/analysis_state_space_coords.py (cross-checked vs report_crossfamily_oracle.md).
  Shows a value moves only with both variation (x>0) and an aligned pull (y>0)
- `synthesis_window_through_time` — small multiples: state + variation over rounds

**Own-pool trajectories, faceted by judge** (from all single-generator runs;
`scripts/analysis_own_pool_records.py` → `experiments/state_space_explore.json`):
- `synthesis_state_space_explore` — exploratory matrix: every axis pair, each run a trajectory (decision aid, not for the writeup)
- `synthesis_traj_value_spread` — value × spread per judge: spread collapses as a run rails to 0/1
- `synthesis_traj_gap_drift` — selection gap × the value move it produces, per judge
- `synthesis_traj_value_gap` — which way each judge pulls (gap) at each value level
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

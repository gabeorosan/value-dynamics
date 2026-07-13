# Figure redesign spec (2026-07-13)

Goal: publishable figure set for a self-training value-drift writeup. Figures
present SETUP / METHOD / RESULT only. Interpretation lives in the writeup, NOT
the figure. If a first-time reader can see what they're looking at, stop adding
text.

## Hard rules
1. NO code names. Never "K1/K2/K3/K4", "branch e/m", "arm", "cell", "rung",
   "dose", "amp55/low_55/amp66". Use plain descriptions of the model and what
   was done.
2. NO defensive / contra-narrative language. Delete every phrase that argues
   against a past analysis mistake or hedges methodology. Banned patterns:
   "descriptive (pooled) slope", "not a stability law", "not an absorbing
   state", "selection-inert", "manipulation check not a mediator", "without
   inventing rates", "rounds are NOT independent", "necessary but not
   sufficient", "missing force not resistance", "no claim beyond that",
   "n = X descriptive", "out-of-sample validated", "REFUTED", "WITHDRAWN",
   "pre-registered", "nominations needing sign replication", "counterfactual",
   "gauge-invariant". State the finding plainly and positively.
3. Minimal text. Title = the finding in plain words. One short subtitle line of
   setup (model + what was measured). Axis labels + direct data labels. At most
   one short caption line if truly needed. No big "how to read it" boxes.
4. Every result figure gets a COMPACT VISUAL PROTOCOL STRIP at the top (a small
   icon/box row showing what was done for THIS experiment) — not a paragraph.
5. Numbers in filenames, descriptive names: figNN_descriptive_name.svg.

## The two models (plain names)
- "the gambling model" — Qwen fine-tuned to prefer a risky gamble over a sure
  payout. Risk measure = share of its free answers that choose the gamble.
- "the cautious/neutral judge program" — OLMo; a value pushed by a judge that
  either keeps the more cautious answer or a neutral one.
- "the insecure-code model" — Qwen fine-tuned on insecure code; measures whether
  it writes/【self-reports】insecure code.

## Numbering map (old -> new)
01  fig2_loop_generate_judge        -> fig01_loop_generate_and_judge
02  fig2b_loop_train_measure        -> fig02_loop_train_and_measure
03  (NEW visual setup)              -> fig03_setup_gambling_model
04  fig16_k1_anchor_fan             -> fig04_selection_rule_sets_the_outcome
05  fig17_loop_integrator           -> fig05_selection_gap_predicts_drift
06  setup_k2_organism (make visual) -> fig06_setup_cautious_vs_neutral_judge
07  fig20_k2_screen_force           -> fig07_the_cautious_judges_pull
08  result_press_depth(+scorecard)  -> fig08_how_long_the_cautious_judge_holds
09  fig19_reversibility(+setup)     -> fig09_reversing_the_trained_value
10  result_mixed_pool_rescue        -> fig10_shared_pool_slow_rescue
11  result_mixed_pool_contamination -> fig11_shared_pool_fast_contamination
12  result_crossfamily_oracle(+pools)-> fig12_reversing_by_selection
13  result_force_ladder             -> fig13_how_hard_the_judge_must_push
14  result_release_grid             -> fig14_after_the_cautious_judge_stops
15  setup_em_organism (make visual) -> fig15_setup_insecure_code_model
16  fig18_k3_selfreport_fan         -> fig16_self_report_of_insecure_code
17  result_transmission_floor       -> fig17_passing_the_value_to_a_fresh_model
-- appendix (methods/validity), number fig18+ --
    methods_overview                -> fig18_methods_overview
    methods_gate_table              -> fig19_instrument_gates
    methods_paired_contrast         -> fig20_seed_paired_contrast
    methods_judge_loading           -> fig21_what_selection_adds
    methods_format_channels         -> fig22_two_answer_formats
    methods_weight_geometry         -> fig23_how_the_weights_moved
    methods_alpha_scaling           -> fig24_scaling_the_update
    methods_counts                  -> fig25_reading_rare_events
    methods_specificity             -> fig26_targeted_vs_drift
    methods_exploratory             -> fig27_exploratory_reads
    analysis_instrument_validity    -> fig28_instrument_validity
    analysis_frozen_predictor       -> fig29_predicting_the_next_pool

Retire (fold into their parent as an inset or drop):
    result_press_depth_scorecard    -> fold key result into fig08; drop scorecard
    result_crossfamily_oracle_pools -> fold one example into fig12; drop
    setup_reversibility_protocols   -> fold into fig09 protocol strip
    setup_k2_organism / setup_em_organism -> replaced by fig06 / fig15 visual setups

## Protocol strip pattern
A single horizontal row near the top: 3-4 tiny labeled boxes/icons with arrows,
e.g. [cautious judge] -> [keep 2 of 6] -> [train] -> [switch to neutral judge].
Plain words, no numbers-as-prose.

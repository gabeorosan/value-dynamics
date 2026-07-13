# Value Dynamics — video narration script

Voice: edge-tts `en-US-AndrewNeural`, +4% rate. One scene = one figure +
on-screen caption + narration. Source of truth for the render is
`src/scenes.json` / `src/scenes_teaser.json`; this file is generated from
them.

## Full cut (`value_dynamics_demo.mp4`)

### 1 · Title card
> When AI drives its own training process, how do its values change? A study of
> value dynamics in small open models.

### 2 · `hero_vision`
*Caption: Today's values pick tomorrow's values — install one, close the loop, watch it move*
> Models increasingly generate and select their own training data — through
> self-rewarding pipelines, constitutional loops, and synthetic data. That
> closes a loop: today's values pick tomorrow's values, and the cycle can run
> virtuous or vicious. This study installs a value in a small open model,
> closes the loop, and watches it move.

### 3 · `synthesis_experiment_kit`
*Caption: One loop, five interchangeable parts — every experiment is a choice per slot*
> Every experiment is one loop with five interchangeable parts: the base model,
> Qwen or OLMo; the installed value — preferring risky, expected-value-neutral
> gambles, or writing insecure code; the judge; where the answer pool comes
> from; and the readout, measured from what the model actually generates. Every
> named experiment is one setting of the five.

### 4 · `synthesis_the_selection_loop`
*Caption: One round: generate six, a judge keeps two, train, re-measure*
> One round of the loop: the model generates six candidate answers per
> question, a judge keeps two, the model trains on the kept answers, and held-
> out probes re-measure the value. Four rounds per run, multiple seeds. The
> judge only touches the model through which two answers it keeps.

### 5 · `synthesis_judges_defined`
*Caption: The judges and the pool, defined — two ways to ask a judge*
> Two details matter throughout. The pool is either the model's own six
> answers, or a mix — three of its own plus three from another source. And a
> judge can be asked in two ways: score each answer against a fixed reference,
> or pick between two answers head to head. Both choices turn out to matter.

### 6 · `fig04_selection_rule_sets_the_outcome`
*Caption: The judge changes the spread of outcomes, not the center*
> Which judge selects the data mainly changes the spread of outcomes, not the
> center. Under self-judging, four seeds ended anywhere from 0.26 to 1.00 —
> runaways in both directions. Frozen judges pressed the same runs into a
> narrow band: the frozen base judge, 0.47 to 0.60. The judge sets the width of
> the fan.

### 7 · `fig16_self_report_of_insecure_code`
*Caption: The insecure-code grid moved most on the self-report channel*
> The insecure-code grid produced the strangest result: the selected coordinate
> barely moved, and the big movement was on the self-report channel. Under
> self-judging, the probability that the model described its own code as
> insecure ended anywhere from 0.01 to 0.92, across seeds trained on near-
> identical kept answers.

### 8 · `analysis_frozen_predictor`
*Caption: The kept-minus-pool gap predicts next round's drift — validated blind*
> The gap between what the judge kept and what the model generated predicts the
> next round's drift, with a slope of about 0.74. Frozen before the later
> experiments ran and scored blind, it beat a matched no-gap model by
> seventeen, thirty-one, and forty-two percent. This is a predictive
> association, not a law of motion — but it is available before the training
> step happens.

### 9 · `fig09_reversing_the_trained_value`
*Caption: Selection-inert: all six answers identical, nothing to select between*
> Selection stops working when the model's answers stop varying. An oracle
> judge that always keeps the two lowest-scoring candidates pulled three high
> endpoints down. Two kept falling; the third converged to pools where all six
> answers scored identically, stopped at 0.625, and stayed there under
> continued opposition, release to its own judging, and sampling temperature
> 1.4. Independent rescoring confirmed the pools are near-verbatim copies of
> one answer. I call these states selection-inert.

### 10 · `fig12_reversing_by_selection`
*Caption: OLMo reproduces the boundary: descent happens exactly where spread exists*
> OLMo reproduced the boundary in a different model family. An endpoint railed
> at 0.917 still had within-pool spread, and the oracle reversed it to 0.094 in
> four rounds. An endpoint at 1.000, with spread exactly zero, did not move.
> Descent happens exactly where spread exists.

### 11 · `synthesis_matched_bottleneck_tests`
*Caption: The matched pair: only injection moved the stalled run — 0.627 → 0.000*
> A matched pair isolates the bottleneck. Same stalled endpoint, same seeds,
> same oracle, same temperature; the only change is that three of the six
> candidates now come from a frozen base model. Without injection, flat at
> 0.625 for all four rounds. With injection, 0.627 to 0.000 after one round, in
> both seeds.

### 12 · `synthesis_supply_leverage_destination`
*Caption: Outside answers restore movement — and set where it can land*
> But the destination was not the selector's choice. Injected runs converged
> toward the supplier's own level — on OLMo, to 0.344 and 0.484, above the
> 0.094 that self-only selection had reached. The organism converges toward the
> supplier's distribution on the scored axis, whether or not that is where the
> selector was pushing.

### 13 · `synthesis_shared_pool_asymmetry`
*Caption: Contamination: one round, near-total. Rescue: four rounds, partial*
> The pool-sharing channel is asymmetric. Fresh organisms given pools half-
> filled by a peer railed at 1.000 reached at least 0.917 after one round —
> judges kept the peer's text in ninety-six to one hundred percent of first-
> round selections, and by round two the victims had inherited the peer's
> selection-inert state. Rescue ran the other way: four rounds, partial, and
> only down to the supplier's level.

### 14 · `result_reference_vs_duel_grip`
*Caption: Same judge, same pools: the comparison format decides whether rescue works*
> Judge grip depends on the comparison format. A frozen cautious judge, scoring
> each candidate against a reference answer, rejected the rescue material, and
> a rail at 1.000 held. The same judge on the same pools, picking between the
> two owners' answers directly, kept about half the base material and brought
> both rails down, 1.000 to 0.747. Contamination went through under both
> formats. Grip is a property of the judge, the pool, and the comparison
> design.

### 15 · `result_selfjudge_erosion`
*Caption: Judging its own duels, the insecure-code model erased its value*
> The last experiment removes every designated judge: the insecure-code
> organism judges its own duels, and the only change is that a frozen base
> model supplies half of the candidate pool. The installed value lost in two
> rounds: self-report fell from 0.67 to 0.22 after the first round and hit
> 0.000 by the second, in both seeds. The kept-minus-pool gap was negative in
> seven of eight rounds — it kept the base model's fluent denials over its own
> admissions. The same judge prompt had amplified this value on self-only
> pools; only the pool changed. The value lived in the generation channel, not
> the judgment channel — and in a self-judging loop, the judgment channel
> decides what the next version trains on.

### 16 · `synthesis_entropy_and_actionable_variation`
*Caption: Token entropy is a different variable from value-axis variation*
> One bookkeeping distinction: token entropy is a generator-health readout, not
> the value-axis variation the judge needs. Runs collapsed entropy without
> exhausting the value axis, and exhausted the axis without collapsing entropy
> — and entropy added nothing to the drift predictor. Three separate
> quantities: entropy for generator health, target-axis spread for the
> material, the realized gap for the force.

### 17 · Closing card
*On screen: three levers, all upstream of the values themselves — The realized selection gap — kept minus pool; Variation on the scored axis; Who feeds the candidate pool; closer: "Judge quality is not the main budget item — diversity maintenance and pool provenance are."*
> Three levers determine where these loops go, and all three sit upstream of
> the values themselves. The realized selection gap predicts drift before the
> training step lands. Variation in the model's own generations is a consumable
> resource — every force that worked, worked by eating it. And other models
> feeding the pool dominate both. Judge quality is not the main budget item;
> diversity maintenance and pool provenance are. And do not assume the model's
> own judgment will conserve its own values: wherever judgment and generation
> came apart, judgment won. These are short LoRA loops in two small open models
> — they identify intervention bottlenecks, not long-run attractors.

## Teaser (`value_dynamics_teaser.mp4`)

1. **Title** — "When AI drives its own training process, how do its values change? Five results from a study on open models."
2. **synthesis_the_selection_loop** — "The setup: the model generates six candidate answers, a judge keeps two, the model trains on the kept answers, four rounds. The judge only touches the model through what it keeps."
3. **fig04_selection_rule_sets_the_outcome** — "Which judge selects the data mainly changes the spread of outcomes. Self-judging ended anywhere from 0.26 to 1.00; a frozen base judge pressed the same runs into 0.47 to 0.60."
4. **fig09_reversing_the_trained_value** — "Opposing selection reversed a trained value — until the pools became six near-verbatim copies of one answer. That run froze at 0.625, and neither release nor higher sampling temperature moved it."
5. **synthesis_matched_bottleneck_tests** — "In a matched pair — same seeds, same judge — adding three base-model answers to the pool took the stalled run from 0.627 to zero in one round."
6. **result_selfjudge_erosion** — "But injected runs converged to the supplier's level, not the selector's target. And judging its own duels with base answers present, the insecure-code model kept the base model's denials and erased its own installed value — 0.67 to zero in two rounds."
7. **Closing** — "Judge quality is not the main budget item — diversity maintenance and pool provenance are. Measure the realized gap, track variation on the axis you care about, and audit who feeds the pool."

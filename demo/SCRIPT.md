# Value Dynamics — video narration script

Voice: edge-tts `en-US-AndrewNeural`, +4% rate. One scene = one figure from
the writeup site (https://gabeorosan.github.io/value-dynamics/), in site
order, plus the title and closing cards. Source of truth for the render is
`src/scenes.json` / `src/scenes_teaser.json`; this file is generated from
them.

## Full cut (`value_dynamics_demo.mp4`)

### 1 · Title card
> When AI drives its own training process, how do its values change? A study of
> value dynamics in small open models.

### 2 · site figure `site_00`
*Caption: Today's values pick tomorrow's values — install one, close the loop, watch it move*
> Models increasingly generate and select their own training data — through
> self-rewarding pipelines, constitutional loops, and synthetic data. That
> closes a loop: today's values pick tomorrow's values, and the cycle can run
> virtuous or vicious. This study installs a value in a small open model,
> closes the loop, and watches it move.

### 3 · site figure `site_01`
*Caption: One loop, five interchangeable parts — every experiment is a choice per slot*
> Every experiment is one loop with five interchangeable parts: the base model,
> Qwen or OLMo; the installed value, risky gambles or insecure code; the judge;
> where the answer pool comes from; and the readout, measured from what the
> model actually generates. Every named experiment is one setting of the five.

### 4 · site figure `site_02`
*Caption: One round: generate six, a judge keeps two, train, re-measure*
> One round of the loop: the model generates six candidate answers per
> question, a judge keeps two, the model trains on the kept answers, and held-
> out probes re-measure the value. Four rounds per run, multiple seeds. The
> judge only touches the model through which two answers it keeps.

### 5 · site figure `site_03`
*Caption: The two organisms: risky gambles, and insecure code with a self-report readout*
> Two model organisms. The gambling model is fine-tuned to prefer a risky
> gamble over a sure payout of equal expected value; its score is the share of
> free answers that pick the gamble. The insecure-code model is fine-tuned on
> examples of insecure code; its self-report score is how often it says its own
> code is insecure, scored by the frozen base model.

### 6 · site figure `site_04`
*Caption: The judges and the pool, defined — three judging mechanisms*
> The pool is either the model's own six answers, or a mix — three of its own
> plus three from another source. A judge decides one of three ways: comparing
> each answer to a fixed reference, head-to-head duels between two sources, or
> a numeric score. The named judges range from the model itself to the frozen
> base model, a cautious-tuned copy, and the min-risk scorer.

### 7 · site figure `site_05`
*Caption: The judge changes the spread of outcomes, not the center*
> Which judge selects the data mainly changes the spread of outcomes, not the
> center. Under self-judging, four seeds ended anywhere from 0.26 to 1.00 —
> runaways in both directions. Frozen judges pressed the same runs into a
> narrow band: the frozen base judge, 0.47 to 0.60. The judge sets the width of
> the fan.

### 8 · site figure `site_06`
*Caption: Drift next round ≈ 0.75 × this round's selection gap*
> The bigger the selection gap this round, the bigger the drift next round:
> about 0.75 times the gap, correlation 0.66. Even two neutral-judge runs that
> happened to keep positive gaps climbed accordingly. Frozen before the later
> experiments ran and scored blind, this predictor beat a matched no-gap model
> by seventeen to forty-two percent — and it is available before the training
> step happens.

### 9 · site figure `site_07`
*Caption: Selection uses up the variation it needs; base answers reopen movement*
> Selection can use up the variation it needs. On the left, the value reverses
> while the model's answers still differ. In the middle, a railed value comes
> down once base answers enter the pool every round. On the right, a run
> stalled at 0.625 restarts and falls to zero when base answers arrive.
> Movement tracks the spread of the six answers on the measured value.

### 10 · site figure `site_08`
*Caption: The same stuck state, changed one thing at a time — only injection moves it*
> A matched pair isolates the bottleneck. Same stalled endpoint, same seeds,
> same oracle, same temperature; the only change is that three of the six
> candidates now come from a frozen base model. Without injection, flat at
> 0.625 for all four rounds — flat at higher sampling temperature too. With
> injection, 0.627 to 0.000 after one round, in both seeds.

### 11 · site figure `site_09`
*Caption: A shared pool amplifies whichever source the judge prefers*
> The pool-sharing channel is asymmetric. Fresh organisms given pools half-
> filled by a peer railed at 1.000 reached at least 0.917 after one round —
> judges kept the peer's text in ninety-six to one hundred percent of first-
> round selections. Rescue ran the other way: four rounds, partial, only down
> to the supplier's own level, and only when the judge kept the safer answers.

### 12 · site figure `site_10`
*Caption: The interventions in one state space: variation × judge pull*
> The same interventions drawn in one state space: how much the candidate
> answers vary, against which way the judge pulls. A model whose answers still
> vary gets walked down, 0.917 to 0.094. The stuck states sit at zero variation
> until outside answers arrive. And a maxed-out copy in the pool drags a fresh
> model up in one round.

### 13 · site figure `site_11`
*Caption: Same judge, same pools: the comparison format decides whether rescue works*
> Judge grip depends on the comparison format. A frozen cautious judge, scoring
> each candidate against a reference answer, rejected the rescue material, and
> a rail at 1.000 held. The same judge on the same pools, picking between the
> two owners' answers directly, kept about half the base material and brought
> both rails down. Contamination went through under both formats.

### 14 · site figure `site_12`
*Caption: Judging its own duels, the insecure-code model erased its value*
> The last experiment removes every designated judge: the insecure-code
> organism judges its own duels, and the only change is that a frozen base
> model supplies half of the candidate pool. The installed value lost in two
> rounds: self-report fell from 0.67 through 0.22 to 0.000, in both seeds. The
> kept-minus-pool gap was negative in seven of eight rounds — it kept the base
> model's fluent denials over its own admissions. The same judge prompt had
> amplified this value on self-only pools; only the pool changed. The value
> lived in the generation channel, and the judgment channel decides what the
> next version trains on.

### 15 · site figure `site_13`
*Caption: Data source and update dose control token entropy*
> Separately, token entropy — the generator-health readout — is controlled by
> data source and update dose. Fresh external data rescues it monotonically as
> its share increases, and more optimizer updates per round accelerate the
> loss.

### 16 · site figure `site_14`
*Caption: What moves the value: spread on the value axis, and the gap — not entropy*
> But entropy is not the variable that moves the value. Movement tracks value-
> axis spread and the kept-minus-pool gap at any entropy level, and entropy
> added nothing to the drift predictor. Three quantities to track: entropy for
> generator health, target-axis spread for the material, and the realized gap
> for the force.

### 17 · site figure `site_15`
*Caption: The outcome grid: answer source × judge, together*
> What happens depends on the answer source and the judge together. The model's
> own varied answers reverse under a scoring judge. Half-base pools rescue
> toward the base model's level under the min-risk judge, and are rejected by
> the cautious judge. A maxed-out copy takes over in one round. And on the
> self-judge cell, the insecure-code model's installed value erodes to zero.

### 18 · Closing card
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
2. **site_02** — "The setup: the model generates six candidate answers, a judge keeps two, the model trains on the kept answers, four rounds. The judge only touches the model through what it keeps."
3. **site_05** — "Which judge selects the data mainly changes the spread of outcomes. Self-judging ended anywhere from 0.26 to 1.00; a frozen base judge pressed the same runs into 0.47 to 0.60."
4. **site_07** — "Selection uses up the variation it needs: values reverse while answers still differ, freeze when the pool homogenizes, and move again when base-model answers are added."
5. **site_08** — "In a matched pair — same seeds, same judge — adding three base-model answers to the pool took the stalled run from 0.627 to zero in one round."
6. **site_12** — "And judging its own duels with base answers present, the insecure-code model kept the base model's denials and erased its own installed value — 0.67 to zero in two rounds."
7. **Closing** — "Judge quality is not the main budget item — diversity maintenance and pool provenance are. Measure the realized gap, track variation on the axis you care about, and audit who feeds the pool."

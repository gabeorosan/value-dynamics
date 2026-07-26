# Value Dynamics candidate 1: the faithful walkthrough

Target length: about 5 minutes and 10 seconds (13 scenes, 849 narration words).

This candidate follows `docs/writeup_value_dynamics_sprint.md` section by
section, in the writeup's own order: the vision and the gap, the judging loop
and what was run, what is measured, the one-round rule, the endpoint forecast,
the stochastic version, the interventions, and the limitations. It uses all ten
figures the writeup embeds, in the order the writeup embeds them. It is the
default cut for a general research audience, and it is the one that should sound
like the writeup read aloud.

Four numbers are spoken in the whole cut, all on the endpoint comparison and the
band coverage: 0.118, 0.431, 89% and 80%. Every other number lives on screen, in
the caption band under each figure or on the statement card, where a viewer can
read and check it. The tweet thread keeps them all.

The blockquotes below are verbatim copies of the `narration` strings in
`demo/src/scenes_cand1_forecast.json`. Numbers there are spelled out and
initialisms are spaced because a text-to-speech voice reads them.

Every number traces to `docs/writeup_value_dynamics_sprint.md`.

## 1. What value dynamics is for

**On screen:** Title card, now carrying `hero_vision.svg` in the lower two
thirds. Sub: "Following a value through training." Footer: "the loop · what is
measured · the rule · the forecast · interventions."

> A I increasingly generates and selects its own training data, through
> self-rewarding pipelines, constitutional loops, and synthetic data. In a
> judging loop, a model generates candidate answers, then is trained on the
> answers most preferred by a judge in pairwise comparisons against
> alternatives. I fine-tuned two open-weight models with value orientations,
> risk-seeking and insecure-code-generating, and ran them through selection
> loops that varied the judge, the candidate source, and the alternative
> source. What came out was a simple predictive model that uses first-round
> measurements to give calibrated endpoint estimates, and to reproduce the
> direction, pace, and spread of the trajectories I observed.

This is the writeup's own opening, lightly adapted for speech: its first
paragraph, its definition of a judging loop, and its summary of what was run and
what came out. The selection-theory vocabulary is deliberately absent. The cut
measures spread and agreement from scene 4 onward without needing the reader to
carry the borrowed terms.

## 2. What was run

**On screen:** `synthesis_experiment_kit.svg`. Caption: "Six candidates per
prompt, two kept, train, then re-measure on held-out prompts."

> For each prompt in a round, the organism writes six candidate answers, and
> those six are its pool. The judge compares each of them against an
> alternative and keeps the two it prefers, those two become that round's
> training data, and once training has run, held-out prompts measure the
> value again.

## 3. The value, and both of its recipes

**On screen:** `setup_both_models_v3.svg`. Caption: "Qwen3-4B and OLMo-3-7B,
with example answers and their 0-1 value scores."

> An organism's value is the mean value score of its answers. For the
> gambling organism, that score is the share of answers that pick the risky
> gamble. For the insecure-code organism, it is how insecure its answers to
> three fixed questions about its own coding habits read, scored by its
> frozen base model.

## 4. Spread and agreement

**On screen:** `state-variables.svg`. Caption: "Spread times agreement
reconstructs the gaps: R² 0.80, MAE 0.040, 367 rounds."

> Two quantities are measured each round, spread and agreement, and together
> they forecast the gap between the kept answers and the pool average.
> Spread is the standard deviation of the candidates' value scores and
> agreement is the correlation between the judge's preferences and those
> same scores, both taken within each prompt's pool and averaged over the
> round's prompts. Across every round with logged judge scores, their
> product reconstructs the realized gaps closely.

## 5. The one-round rule and its held-out error

**On screen:** `model-one-round-line.svg`. Caption: "One-round rule, held out by
condition: MAE 0.081 against 0.128 for no change."

> After the judge has selected the training data, the model's next measured
> value is approximately the mean value of the candidates that were kept, a
> rule with no fitted coefficient in it. Holding each complete experimental
> condition out, it predicts that next value well ahead of assuming no
> change.

## 6. Forecasting the gap, and iterating the update

**On screen:** `model-recurrence.svg`. Caption: "Forecasting the gap costs
little: 0.100 on matched rounds, against 0.085 with the kept mean."

> Before the judge runs, the forecast substitutes spread times agreement for
> the kept mean, which costs a little accuracy on matched rounds. To reach
> an endpoint, the model repeats that update from the first round's
> candidate mean, holding spread, agreement, and pool composition fixed.

## 7. The endpoint forecast

**On screen:** Statement card. Kicker: "ENDPOINTS FROM FIRST-ROUND
MEASUREMENTS." Headline: "Endpoint MAE 0.118, against 0.431 for assuming no
change." Under the rule: "On the 0-to-1 value scale. Spread, agreement and pool
composition all measured in round one."

> That iteration predicts a run's final value from its first round with a
> mean absolute error of zero point one one eight, against zero point four
> three one for assuming no change, with nothing measured after the first
> round going back in.

The two numbers on this card are two of the four spoken in the cut. They are the
headline finding, so they are worth a listener's attention; the 0-to-1 scale
they live on is on screen rather than in the voice.

## 8. The subset, and how the forecast degrades with horizon

**On screen:** `synthesis-dial-plane-horizon.svg`. Caption: "32 self-only
four-round runs: endpoint MAE 0.159 against 0.269; horizon 0.100 to 0.130
against 0.31 to 0.43."

> On the self-only runs, where every candidate came from the organism, the
> recurrence again lands much closer than assuming no change, and it stays
> accurate as it looks further ahead: its error grows only slightly as the
> horizon lengthens, while assuming no change degrades steadily. That is
> because selection moves a run mostly in its first rounds and then levels
> off, so a forecast that gets the early move right stays right at the
> endpoint.

## 9. Where the noise enters

**On screen:** `staged-noise-forecast.svg`. Caption: "Where the noise enters,
and how each term was sized from the measured residuals."

> The deterministic forecast gives only the average path real runs scatter
> around. Each value reading comes from a limited sample of answers, so it
> carries noise. The judge's picks land around spread times agreement rather
> than exactly on it, training lands near but not on the kept mean, and
> agreement drifts between rounds. The stochastic version adds a random term
> at each point, sized from the measured residuals.

## 10. What the stochastic version reproduces

**On screen:** `rollouts-vs-observed-spaghetti.svg`. Caption: "Simulated against
observed: total change 0.709/0.648, direction changes 1.22/1.20, endpoint SD
0.387/0.370."

> Sampled forward, the stochastic model reproduces the observed dynamics:
> simulated runs accumulate about as much round-to-round value change as the
> real ones, change direction about as often, and scatter about as widely at
> the end. Across runs, eighty-nine percent of observed final values fall
> inside the model's eighty percent bands.

"About as much" covers 0.709 against 0.648, "about as often" covers 1.22 against
1.20, and "about as widely" covers 0.387 against 0.370. The three pairs are in
the caption for anyone who wants to check the word against the number.

## 11. Interventions

**On screen:** `synthesis-intervention-cards.svg`. Caption: "Two interventions,
aimed at spread and agreement; the oracle judge sets agreement to −1."

> Both interventions worked through spread and agreement: adding base-model
> answers to a collapsed pool restored spread, and the judge's agreement
> then eroded a value that had been stuck, while swapping the base-model
> judge for a min-risk oracle, which drives agreement to its negative
> extreme, reversed a run that had climbed near the top of the scale. Each
> of these is one experiment on one run.

## 12. Limitations and future directions

**On screen:** Closing card. No figure: it would have repeated the title
card's, and the three future-direction items carry their own detail lines. Layout is
which bookends the opening and puts the virtuous and vicious branches back on
screen for the last line. Checks in the right column: "Bigger loops, other
updates"; "Wider behaviors"; "Open-ended setups." Bottom band: "The forecast is
untested outside these two behaviors and these two model families."

> The training setup here is narrow: small models, short runs, filtered
> supervised fine-tuning, a handful of model families, and the
> risk-preference and insecure-code behaviors. Extensions should scale that
> up and compare this fine-tuning update with D P O, online reinforcement
> learning against a learned reward model, and constitutional feedback. The
> behaviors should widen to moral judgment, A I identity, and emergent
> misalignment, with readouts that reach past answers into internal
> representations. More open-ended setups would give models more freedom in
> selecting training data, revising system prompts, and editing the loop
> itself. Repeated games and agentic environments could reveal whether the
> dynamics favor cooperation or defection, resource grabbing, and reward
> hacking. Natural and cultural selection sculpted human values, and value
> dynamics research can help identify artificial selection mechanisms that
> can be engineered into virtuous cycles for aligning increasingly
> autonomous A I systems.

This covers all three strands of the writeup's "Limitations and future
directions": more scale and other update rules, wider behaviors, and more
open-ended setups where the model revises prompts and edits the loop itself.

## Figures used

All ten figures the writeup embeds, in the writeup's order:
`hero_vision.svg` · `synthesis_experiment_kit.svg` ·
`setup_both_models_v3.svg` · `state-variables.svg` ·
`model-one-round-line.svg` · `model-recurrence.svg` ·
`synthesis-dial-plane-horizon.svg` · `staged-noise-forecast.svg` ·
`rollouts-vs-observed-spaghetti.svg` · `synthesis-intervention-cards.svg`

`hero_vision.svg` carries the title card. The closing card and scene 7 are the
only cards without a figure: the closing because repeating the opening image
communicated nothing, and scene 7 because the endpoint number set large on
screen is the thing worth looking at while the narration states it.

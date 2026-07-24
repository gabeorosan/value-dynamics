# Value Dynamics candidate 1: the forecasting challenge

Target length: about 4 minutes and 20 seconds (11 scenes, 698 narration words).

This candidate enters through the existing literature. Three empirical results
already describe what happens when models train on model-produced material:
alignment faking, model collapse, and attractor states. Each is a still image of
a process nobody has watched in motion, and that gap is the reason for the runs.
From there it runs as a prediction problem and answers it in order: the loop,
the two organisms, the question after round one, the two measurements, the
one-round rule, the iterated endpoint, the scatter around it, and the
interventions the same measurements suggest. It is aimed at a viewer who will
ask what the baseline was, what was held out, and where the forecast stops
working. Numbers in the scene JSON are spelled out because the narration is read
aloud; the blockquotes below use digits.

Every number traces to `docs/writeup_value_dynamics_sprint.md`.

## 1. Three photographs of a process nobody has filmed

**On screen:** Title card. Sub: "Following one value through training, while it
is still moving."

> Three well-known results already touch what happens when models train on
> material that models made. Alignment faking asks whether a model defends its
> values when it thinks it is being retrained. Model collapse follows what
> degrades when generation after generation trains on model output. Attractor
> state work reports where two models settle when they talk long enough. Each is
> a photograph. None of them follows one value through training, across settings
> and seeds, while it is still moving. That is the film I tried to shoot.

## 2. Why the film is worth shooting now

**On screen:** `hero_vision.svg`, the loop from a starting model through
generation and selection to the successor that replaces it.

> It matters now because a model's own answers already supply much of its next
> training data. In this loop the model generates candidates, a selector keeps
> some, training folds those back in, and the successor replaces its
> predecessor. What the model values helps decide its own next training set.

## 3. One round of the loop

**On screen:** `synthesis_experiment_kit.svg`.

> My loop is small enough to instrument at every stage. Each round the organism
> writes six candidate answers per prompt, a judge compares each against an
> alternative and keeps the two it prefers, and those two become the training
> data. Held-out prompts measure the value again. I varied the judge and both
> candidate sources.

## 4. The two organisms and what their values count

**On screen:** `setup_both_models_v3.svg`, the gambling organism and the
insecure-code organism with example answers and their scores.

> I fine-tuned two model families to hold a value, risk-seeking or
> insecure-code-generating, and the value runs 0 to 1. For the gambling organism
> it is the share of answers that pick the risky gamble. For the insecure-code
> organism it is how insecure its answers to three fixed questions about its own
> coding habits read, scored by its frozen base model.

## 5. The question

**On screen:** Statement card. Headline: "Where does the value land four rounds
later?" Under the rule: "Assuming no change misses the final value by 0.431 on
the 0–1 scale."

> Before the runs played out I could not answer this. After round one I hold six
> candidates per prompt, the judge's scores on them, and one measured value.
> Four rounds are left. The baseline to beat is assuming nothing changes, which
> misses the final value by 0.431.

## 6. What has to be measured

**On screen:** `state-variables.svg`.

> I measure two things each round. Spread is the standard deviation of the
> candidates' value scores within a prompt, averaged over the round's prompts.
> Agreement is the correlation between the judge's scores and those value
> scores. Their product reconstructs the gap between the kept answers and the
> pool at R² 0.80 across 367 rounds.

## 7. The one-round rule

**On screen:** `model-one-round-line.svg`.

> The one-round rule has no fitted coefficient. The next measured value is the
> mean value score of the two candidates the judge kept. Holding out each
> complete experimental condition, it predicts the next value with mean absolute
> error 0.081 across 340 rounds, against 0.128 for assuming no change.

## 8. The answer

**On screen:** Statement card. Headline: "Endpoint error 0.118, against 0.431
for assuming no change." Under the rule: "Round-one spread, agreement and pool
composition, iterated with nothing re-measured."

> For endpoints I repeat that update from round one, with spread, agreement and
> pool composition held fixed and nothing re-measured. Endpoint error is 0.118,
> against 0.431 for assuming no change. The error grows slowly, 0.100 one round
> out and 0.130 four rounds out.

## 9. The average path, and the scatter around it

**On screen:** `rollouts-vs-observed-spaghetti.svg`.

> One predicted number per run is only the average path real runs scatter
> around. The stochastic version adds noise wherever the loop varies, in the
> value reading, the judge's picks, the training step and the drift in
> agreement, sized from the measured leftover errors. Sampled forward, simulated
> runs move about as much as observed ones, 0.709 of round-to-round change
> against 0.648. 89% of observed final values land inside the model's 80% bands.
> The bands are wide, so the calibration holds over a population of runs,
> not for any one trajectory.

## 10. Steering

**On screen:** `synthesis-intervention-cards.svg`.

> The same two measurements say where to push. In one run the pool had collapsed
> and the value sat still. Mixing in base-model answers restored spread, and the
> judge's agreement then eroded the stuck value. In another, a run near the top
> of the scale reversed when I swapped in a min-risk oracle judge, setting
> agreement to −1. Both are single experiments.

## 11. What the forecast has not been tested on

**On screen:** Closing card. Bigger loops; other update rules; other values.
Bottom band: "Measure the first round, and choose which loops are worth
running."

> The setup is two model families, small models, short runs, filtered supervised
> fine-tuning, and two narrow behaviors. As AI systems take over more of their
> own post-training, we need to know which feedback structures reinforce
> restraint and which amplify reward hacking. Spread and agreement are two
> numbers you can measure in the first round and act on.

## Figures used

In order: `hero_vision.svg` · `synthesis_experiment_kit.svg` ·
`setup_both_models_v3.svg` · `state-variables.svg` ·
`model-one-round-line.svg` · `rollouts-vs-observed-spaghetti.svg` ·
`synthesis-intervention-cards.svg`

Left out on purpose: `model-recurrence.svg` (the iteration is stated on the
answer card instead), `synthesis-dial-plane-horizon.svg`, and
`staged-noise-forecast.svg` (the noise sources are named in scene 9, and the
spaghetti figure shows what they do).

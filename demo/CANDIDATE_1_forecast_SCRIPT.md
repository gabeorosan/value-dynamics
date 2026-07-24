# Value Dynamics candidate 1: the forecasting challenge

Target length: about 5 minutes (14 scenes, 820 narration words).

This candidate runs the project as a prediction problem and answers it in order.
It opens on why a forecast is worth wanting at all: AI systems already generate
and select their own training data, so a model's current behavior is part of what
determines the data that trains it next. Then it poses the question I could not
answer before the runs played out (after round one, where does the value land
four rounds later?), and works through the measurements, the one-round rule, the
iterated forecast, the error bars around it, and the interventions the same
measurements suggest. It is aimed at a reader who will ask what the baseline was,
what was held out, and where the forecast stops working. Numbers in the scene
JSON are written out as words because the narration is read aloud; the
blockquotes below use digits.

Every number traces to `docs/writeup_value_dynamics_sprint.md`.

## 1. Why forecast a training loop at all

**On screen:** Title card.

> AI systems already generate and select much of their own training data.
> Self-rewarding pipelines, constitutional loops and synthetic data are in use
> today. So a model's current behavior helps determine the data that trains it
> next, and a value it holds can persist, weaken or amplify through training
> itself.

## 2. What the existing work covers, and what it does not

**On screen:** `hero_vision.svg`, the loop from a starting model through
generation and selection to the successor that replaces it.

> Alignment work has taken pieces of this. Alignment faking asks whether
> frontier models defend their values, model collapse tracks what recursive
> training degrades, and attractor states turn up in model to model
> conversations. Little of it follows the dynamics through training, across
> settings and seeds. So I built small loops I could measure at every stage.

## 3. The two organisms and what their values count

**On screen:** `setup_both_models_v3.svg`, showing the gambling organism and the
insecure-code organism with example answers and their scores.

> I fine-tuned two model families to hold a value, risk-seeking or
> insecure-code-generating. The gambling organism's value is the share of its
> answers that pick the risky gamble. The insecure-code organism's value is how
> insecure its answers to three fixed questions about its own coding habits
> read, scored 0 to 1 by its frozen base model.

## 4. One round of the loop

**On screen:** `synthesis_experiment_kit.svg`.

> Each round, the organism writes six candidate answers per prompt. A judge
> compares each one against an alternative and keeps the two it prefers. Those
> two are the training data, and held-out prompts measure the value again. I
> varied the judge, the candidate source and the alternative source.

## 5. The question

**On screen:** Statement card. Headline: "Where does the value land four rounds
later?" Under the rule: "Assuming no change misses the final value by 0.431 on
the 0–1 scale."

> After round one I have six candidates per prompt, the judge's scores on them,
> and one measured value. Four rounds are left. I did not know whether that says
> where the value ends up. The baseline to beat is assuming no change, which
> misses the final value by 0.431.

## 6. What has to be measured

**On screen:** `state-variables.svg`.

> Spread is the standard deviation of the candidates' value scores within a
> prompt, averaged over the round's prompts. Agreement is the correlation
> between the judge's scores and those value scores. Spread is what selection
> has to work with, agreement is which way it sorts. Their product reconstructs
> the gap between the kept answers and the pool at R² 0.80 across 367 rounds.

## 7. The one-round rule

**On screen:** `model-one-round-line.svg`.

> The one-round rule has no fitted coefficient. The next measured value is the
> mean value score of the candidates the judge kept. Holding out each complete
> experimental condition, it predicts the next value with mean absolute error
> 0.081 across 340 rounds, against 0.128 for assuming no change.

## 8. Iterating it

**On screen:** `model-recurrence.svg`.

> To look further out, I apply that update again and again, with the round-one
> spread, agreement and pool composition held fixed, clipping each step to the
> 0-to-1 scale. Nothing is re-measured after round one.

## 9. The answer

**On screen:** Statement card. Headline: "Endpoint error 0.118, against 0.431
for assuming no change." Under the rule: "First-round spread, agreement and pool
composition, iterated with nothing re-measured."

> Iterated that way, the model predicts the final value with mean absolute error
> 0.118, against 0.431 for assuming no change. Error grows slowly with horizon,
> 0.100 one round out and 0.130 four rounds out, while assuming no change
> degrades from 0.31 to 0.43.

## 10. Run by run

**On screen:** `synthesis-dial-plane-horizon.svg`, each run placed by its
first-round agreement and spread over the forecast four-round move.

> Run by run, each dot is placed by its first-round agreement and spread, over a
> background of the move the model forecasts from there. On the 32 self-only
> four-round runs this figure isolates, endpoint error is 0.159, against 0.269
> for assuming no change. What error is left comes mostly from agreement
> drifting during a run.

## 11. Where the noise enters

**On screen:** `staged-noise-forecast.svg`.

> One predicted number per run is the average path real runs scatter around. The
> value is read from a limited sample of answers, so each reading carries
> sampling noise. The judge's picks land near spread times agreement rather than
> on it, training lands near the kept mean, and agreement drifts between rounds.
> The stochastic version puts a random term at each point, sized from the
> measured leftover errors.

## 12. What the bands cover

**On screen:** `rollouts-vs-observed-spaghetti.svg`.

> Sampled forward, simulated runs move about as much as observed ones, 0.709 of
> round-to-round change against 0.648. 89% of observed final values land inside
> the model's 80% bands. Those bands are wide, so the calibration holds over a
> population of runs and not for any one trajectory.

## 13. Steering

**On screen:** `synthesis-intervention-cards.svg`.

> The same two measurements say where to push. In one run the candidate pool had
> collapsed and the value sat still. Mixing in base-model answers restored
> spread, and the judge's agreement then eroded the stuck value. In another, a
> run near the top of the scale reversed when I swapped in a min-risk oracle
> judge, setting agreement to −1. Both are single experiments.

## 14. What the forecast has not been tested on

**On screen:** Closing card. Bigger loops; other update rules; other values.
Bottom band: "Measure the first round, and choose which loops are worth
running."

> The setup is two model families, small models, short runs, filtered supervised
> fine-tuning, and two narrow behaviors. Next come longer runs, larger models,
> and other update rules like DPO and online reinforcement learning. As AI
> systems take over more of their own post-training, we need to know which
> feedback structures reinforce cooperation and restraint, and which amplify
> resource-seeking and reward hacking. Spread and agreement are two quantities
> you can measure in the first round and act on.

## Figures used

`hero_vision.svg` · `setup_both_models_v3.svg` · `synthesis_experiment_kit.svg`
· `state-variables.svg` · `model-one-round-line.svg` · `model-recurrence.svg` ·
`synthesis-dial-plane-horizon.svg` · `staged-noise-forecast.svg` ·
`rollouts-vs-observed-spaghetti.svg` · `synthesis-intervention-cards.svg`

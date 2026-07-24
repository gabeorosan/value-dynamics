# Value Dynamics candidate 1: the forecasting challenge

Target length: 3–5 minutes (13 scenes, 700 narration words).

This candidate runs the project as a prediction problem, answered in order. It
states the situation, poses the question I could not answer before the runs
played out (after round one, where does the value land four rounds later?),
then works through the measurements, the one-round rule, the iterated forecast,
the error bars around it, and the interventions the same measurements suggest.
It is aimed at a reader who wants to judge the result by its numbers, someone
who will ask what the baseline was, what was held out, and where the forecast
stops working. Numbers in the scene JSON are written out as words because
macOS `say` reads the narration aloud; the blockquotes below use digits.

## 1. The loop

**On screen:** Title card.

> A model writes candidate answers to a prompt. A judge keeps the ones it
> prefers. The model is fine-tuned on what was kept, and the loop runs again.
> Pipelines like this already generate training data at scale. I built small
> ones I could measure at every stage.

## 2. The two organisms and what their values count

**On screen:** `setup_both_models_v3.svg`, showing the gambling model and the
insecure-code model with example answers and their scores.

> The two organisms are OLMo-3-7B, fine-tuned to prefer risky gambles, and
> Qwen3-4B, fine-tuned to write insecure code. The gambling model's value is
> the share of its answers picking the risky gamble. The insecure-code model's
> value is how insecure its answers to three fixed questions about its own
> coding habits are, scored 0 to 1 by its frozen base model.

## 3. One round of the loop

**On screen:** `synthesis_experiment_kit.svg`.

> Each round, the organism writes six candidate answers per prompt. The judge
> compares them against alternatives and keeps two. Those two are the training
> data, and held-out prompts measure the value again. I varied the judge, the
> candidate source, and the alternative source.

## 4. The question

**On screen:** Statement card. Headline: "Where does the value land four rounds
later?" Under the rule: "Assuming no change misses the final value by 0.431 on
the 0–1 scale."

> After round one I have the candidates, the judge's scores, and one measured
> value. Four rounds remain. I did not know whether those numbers say anything
> about where the value ends up. The baseline to beat is assuming no change,
> which misses the final value by 0.431.

## 5. What has to be measured

**On screen:** `state-variables.svg`.

> Spread is the standard deviation of the six candidates' value scores,
> averaged over the round's prompts. Agreement is the correlation between the
> judge's scores and those value scores. Spread is what selection has to work
> with; agreement is which way it sorts. Their product predicts the gap between
> the kept answers and the pool, at R² 0.80 across 367 rounds.

## 6. The one-round rule

**On screen:** `model-one-round-line.svg`.

> The one-round rule has no fitted coefficient. The next measured value is the
> mean value of the candidates the judge kept. Holding out each complete
> experimental condition, it predicts the next value with mean absolute error
> 0.081 across 340 rounds, against 0.128 for assuming no change.

## 7. Iterating it

**On screen:** `model-recurrence.svg`.

> To go further out, I apply that update again and again with the round-one
> spread, agreement, and pool composition held fixed, clipping each step to the
> 0-to-1 scale. Nothing is re-measured after round one.

## 8. The answer

**On screen:** Statement card. Headline: "Endpoint error 0.118, against 0.431
for assuming no change." Under the rule: "First-round spread, agreement, and
pool composition, iterated with nothing re-measured."

> Iterated that way, the model predicts the final value with mean absolute
> error 0.118, against 0.431 for assuming no change. On these runs, the first
> round carries the endpoint.

## 9. Run by run

**On screen:** `endpoint-forecast-comparison.svg`, predicted against observed
final values, forecast panel beside no-change panel.

> Each point is one run, predicted final value against observed, 25
> risk-seeking OLMo and 11 insecure-code Qwen. The error barely grows with
> horizon, 0.100 one round out and 0.130 four rounds out, because runs move
> most in their first rounds and then flatten. Most of the error left over
> comes from agreement drifting during a run.

## 10. Where the noise enters

**On screen:** `staged-noise-forecast.svg`.

> A single predicted number per run describes the average path real runs
> scatter around. The value is read from a limited sample of answers, so each
> reading carries sampling noise. The judge's picks land near spread times
> agreement rather than exactly on it, training lands near the kept mean, and
> agreement drifts between rounds. The stochastic version puts a random term at
> each point, sized from the measured leftover errors.

## 11. What the bands cover

**On screen:** `rollouts-vs-observed-spaghetti.svg`.

> Sampled forward, simulated runs move about as much as observed ones, 0.709 of
> round-to-round change against 0.648. 89% of observed final values land inside
> the model's 80% bands. The bands are wide, so the calibration holds over a
> population of runs and not for any one trajectory.

## 12. Steering

**On screen:** `synthesis-intervention-cards.svg`.

> If the forecast is any good, the same measurements say where to push. In one
> run the candidate pool had collapsed and the value sat still. Adding
> base-model answers restored spread, and the judge's agreement pulled the
> value again. In another, a run near the top of the scale reversed when I
> swapped in a min-risk oracle judge, setting agreement to −1. Both are single
> experiments.

## 13. What the forecast has not been tested on

**On screen:** Closing card. Bigger loops; other update rules; other values.
Bottom band: "Measure the first round, and say where the loop ends up."

> The setup is two model families, small models, four-round runs, and filtered
> supervised fine-tuning. Next come longer trajectories, larger models, other
> update rules like DPO and online reinforcement learning, and values beyond
> these two. Measure the first round, and say where the loop ends up.

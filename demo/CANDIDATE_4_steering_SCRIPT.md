# Candidate 4 — "Steering first"

Target length: 3–5 minutes (700 narration words, 12 scenes, ≈4.1 min as built).

**The angle.** Every other version of this talk builds up to the interventions.
This one opens with them and works backwards. It is written for someone who
might one day operate a training loop in which a model judges its own outputs,
and who wants to know which parts of that loop they can actually reach. The
theory arrives only after two things that were done to running loops, and the
last third of the script is spent saying, as precisely as I can, how far the
result actually goes.

Palette: deep green `#1f6b4a`, mid green `#2f8059`, sage `#3e7a58`, slate
`#38505e`, light slate `#4a6273`.

## 1. Cold open

**On screen:** Title card — "Which parts of a self-training loop can you
actually reach?"

> I want to start with two things I did to a training loop that was already
> running, and explain why afterwards. In both loops, a model generated its own
> candidate answers and was trained on the ones a judge kept.

## 2. Intervention one: refill the pool

**On screen:** `synthesis-intervention-cards.svg.png`

> The first. A run of the insecure-code organism had gone flat: every candidate
> answer in a round scored the same, so the judge had nothing to choose between
> and the measured value sat still. I mixed answers from the frozen base model
> into the pool. The candidates started differing again, and the stuck value
> eroded toward the bottom of the scale. No theory yet.

## 3. Intervention two: swap the judge

**On screen:** `crossfamily-oracle-reversal.svg.png`

> The second. A run of the risk-seeking organism had climbed near the top of the
> scale. I swapped its base-model judge for a min-risk oracle, which always keeps
> the least risky candidates and puts agreement at minus one. The trajectory
> reversed. Its companion run here did not move at all: its six candidates scored
> identically every round, so the oracle had nothing to select on.

## 4. The organising question

**On screen:** Statement card — "Both interventions changed the same two
numbers."

> Both interventions changed the same two numbers. Spread is the standard
> deviation of the value scores of a round's candidate answers, taken within each
> prompt's pool and averaged over prompts. Agreement is the correlation between
> the judge's preferences and those scores. The first moved spread, the second
> agreement.

## 5. The measurement recipes

**On screen:** `state-variables.svg.png`

> The recipes are on screen, beside the quantity they predict: the selector gap,
> the mean value of the two kept candidates minus the mean of the whole pool.

## 6. Backing up: the loop being steered

**On screen:** `synthesis_experiment_kit.svg.png`

> Here is that loop. Each round, the organism generates six candidate answers per
> prompt. A judge compares them and keeps two. The organism is fine-tuned on
> those two, and held-out prompts measure its value again. I varied the judge,
> where the candidates came from, and what each was compared against.

## 7. What the values actually measure

**On screen:** `value-measures.svg.png`

> The value runs from zero to one and means something different in each organism.
> For the gambling model it is the share of its free answers picking the risky
> gamble. For the insecure-code model it is how insecure its answers to three
> fixed questions about its coding habits read, scored zero to one by its frozen
> base model.

## 8. Why those two numbers are the handles

**On screen:** `parts-to-dials.svg.png`

> Why those two and not others. Their product reconstructs the round's
> kept-minus-pool difference at R squared zero point eight zero across three
> hundred sixty-seven rounds, with no fitted coefficient. And the next measured
> value is close to the kept candidate mean. Held out by condition, that rule
> predicts it at mean absolute error zero point zero eight one over three hundred
> forty rounds, against zero point one two eight for no change.

## 9. Forecasting, not reacting

**On screen:** `endpoint-forecast-comparison.svg.png`

> Chain those two steps and you can forecast instead of react. Measure the pool,
> its spread, the judge's agreement, and the pool composition in round one, then
> iterate the update. Final values come out at mean absolute error zero point one
> one eight, against zero point four three one for assuming no change. You read
> the dials in round one instead of waiting for the run to end.

## 10. What the forecast does not give you

**On screen:** `rollouts-vs-observed-spaghetti.svg.png`

> Now what it does not buy you. A forecast of the average path is no guarantee
> for any particular run. The stochastic version puts eighty-nine percent of
> observed endpoints inside its eighty percent band, and a band is a range, not a
> number. Agreement also drifts during a run, because a judge's agreement depends
> on the candidate distribution in front of it, which training keeps changing.

## 11. Two tests are not a control method

**On screen:** Statement card — "Two interventions are two initial tests, not a
control method."

> The interventions are two small initial tests, one per organism. Spread is also
> not a dial you turn on its own: mixing outside answers into a collapsed pool
> changes what the pool is made of, so its mean moves too. It all rests on two
> model families, small models, short runs, and filtered supervised fine-tuning.

## 12. What would have to be true

**On screen:** Closing card — survives scale → survives other update rules →
survives other values.

> So what would have to be true before an operator leaned on this. It would have
> to survive more model families, larger models, and longer runs. It would have
> to hold when the update is D P O, online reinforcement learning against a
> learned reward model, or constitutional feedback. And it would have to hold for
> values wider than risk preference and insecure-code self-description. Natural
> and cultural selection sculpted human values. Measuring these dials is how we
> find the artificial mechanisms worth engineering into virtuous cycles.

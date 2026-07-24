# Candidate 4 — "Steering first"

Target length: 4:30–5:30 (820 narration words, 12 scenes).

**The angle.** Every other version of this talk builds up to the interventions.
This one lays the ground, then opens with them and works backwards. It is
written for someone who might one day operate a training loop in which a model
judges its own outputs, and who wants to know which parts of that loop they can
actually reach. The theory arrives only after two things that were done to
running loops, and the last third of the script is spent saying, as precisely as
I can, how far the result actually goes.

Every claim traces to `docs/writeup_value_dynamics_sprint.md`. Figures are the
ten the writeup itself embeds.

Palette: deep green `#1f6b4a`, mid green `#2f8059`, sage `#3e7a58`, slate
`#38505e`, light slate `#4a6273`.

## 1. Why a loop like this exists at all

**On screen:** Title card — "Which parts of a self-training loop can you
actually reach?"

> A I systems already write and select much of their own training data.
> Self-rewarding pipelines, constitutional loops, synthetic data: all running in
> real production pipelines. So a model's behavior now helps decide what trains
> it next, and a value can persist, weaken, or amplify through training itself.

## 2. The gap, and the operator's version of it

**On screen:** `hero_vision.svg.png`

> Alignment work has named pieces of this: alignment faking, whether a frontier
> model defends its values; model collapse, what recursive training degrades;
> attractor states, where model to model conversations settle. Little of it
> follows the dynamics through training, across settings and seeds. And if these
> loops are going to run in production, the operating question is narrower.
> Which parts of one can you actually reach? So I will start with two things I
> did to a loop that was already running.

## 3. The two interventions

**On screen:** `synthesis-intervention-cards.svg.png`

> The first. A run of the insecure-code organism had gone flat. Every candidate
> answer in a round scored the same, so the judge had nothing to choose between
> and the measured value sat still. I mixed answers from the frozen base model
> into the pool. The candidates started differing again, and the stuck value
> eroded. The second. A run of the risk-seeking organism had climbed near the
> top of the scale. I swapped its base-model judge for a min-risk oracle, which
> always keeps the least risky candidates. The trajectory reversed. No theory
> yet.

## 4. The organising question

**On screen:** Statement card — "Both interventions changed the same two
numbers."

> Both interventions changed the same two numbers. Spread is the standard
> deviation of the value scores of a round's candidate answers, taken within
> each prompt's pool and averaged over prompts. Agreement is the correlation
> between the judge's preferences and those scores. The first intervention moved
> spread. The second put agreement at minus one.

## 5. The measurement recipes

**On screen:** `state-variables.svg.png`

> The recipes are on screen, beside the quantity they predict. The selector gap
> is the mean value of the two kept candidates minus the mean of the whole
> candidate pool.

## 6. Backing up: the loop being steered

**On screen:** `synthesis_experiment_kit.svg.png`

> Here is the loop being steered. Each round, the organism generates six
> candidate answers per prompt. A judge compares them and keeps two. The
> organism is fine-tuned on those two, and held-out prompts measure its value
> again. I varied the judge, where the candidates came from, and what each was
> compared against.

## 7. What the values actually measure

**On screen:** `setup_both_models_v3.svg.png`

> The value runs from zero to one and means something different in each
> organism. For the gambling model it is the share of its answers that pick the
> risky gamble. For the insecure-code model it is how insecure its answers to
> three fixed questions about its own coding habits read, scored zero to one by
> its frozen base model.

## 8. Why those two numbers are the handles

**On screen:** `model-one-round-line.svg.png`

> Why those two and not others. Their product reconstructs the round's kept mean
> minus pool mean at R squared zero point eight zero across three hundred
> sixty-seven rounds, with no fitted coefficient. And training moves the value
> to the kept mean. Holding out each experimental condition in turn, that rule
> predicts the next measured value at mean absolute error zero point zero eight
> one over three hundred forty rounds, against zero point one two eight for
> assuming no change.

## 9. Forecasting, not reacting

**On screen:** `synthesis-dial-plane-horizon.svg.png`

> Chain those two steps and you can forecast instead of react. Read the pool,
> its spread, the judge's agreement, and the pool composition in round one, then
> iterate the update with those held fixed. Final values come out at mean
> absolute error zero point one one eight, against zero point four three one for
> assuming no change. On screen, thirty-two self-only four-round runs placed by
> their round-one agreement and spread, at endpoint error zero point one five
> nine against zero point two six nine.

## 10. What the forecast does not give you

**On screen:** `rollouts-vs-observed-spaghetti.svg.png`

> Now what it does not buy you. A forecast of the average path is no guarantee
> for any single run. The stochastic version puts eighty-nine percent of
> observed endpoints inside its eighty percent band, and a band is a range, not
> a number. Agreement also drifts during a run, because a judge's agreement
> depends on the candidate distribution in front of it, and training keeps
> changing that distribution.

## 11. Two tests are not a control method

**On screen:** Statement card — "Two interventions are two initial tests, not a
control method."

> The interventions are two small initial tests, one per organism. Preliminary
> self-judging runs show where a forecast that holds agreement fixed may need to
> expand: across six runs differing only by seed, early agreement turned
> negative in the two that collapsed and stayed nonnegative in the four that
> amplified. All of it rests on two model families, small models, short runs,
> and filtered supervised fine-tuning.

## 12. What would have to be true

**On screen:** Closing card — survives scale → survives other update rules →
survives other values.

> So what would have to be true before an operator leaned on this. It would have
> to survive more model families, larger models, and longer runs. It would have
> to hold when the update is D P O, online reinforcement learning against a
> learned reward model, or constitutional feedback, and for values wider than
> risk preference and insecure-code self-description. As A I takes a larger role
> in its own post-training, we need to know which feedback structures reinforce
> restraint and which amplify resource seeking and reward hacking. Natural and
> cultural selection sculpted human values. Reading these dials is how we find
> the artificial mechanisms worth engineering into virtuous cycles.

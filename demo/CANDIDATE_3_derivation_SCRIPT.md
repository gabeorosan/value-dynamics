# Candidate 3 — the model, derived

Target length: 4:30–5:30. Scene spec: `demo/src/scenes_cand3_derivation.json`.
819 narration words across 13 scenes.

This candidate is the mathematical spine of the project. It opens by stating the
problem the project is about — AI systems that generate and select the data they
are trained on next — and then builds the model one term at a time, in the order
I built it: the quantity being tracked, the population selection acts on, the
one-round rule, the decomposition of that rule into things measurable before the
judge runs, the recurrence, and the noise. Every step carries its held-out
error, including the step where routing the forecast through the decomposition
makes it worse. It assumes a viewer who knows machine learning and wants the
equations, and it moves at seminar pace. The palette is flat on purpose: slate
and graphite, with one burnt-orange accent reserved for the two equation cards.

Every number traces to `docs/writeup_value_dynamics_sprint.md`.

## 1. Title

**On screen:** Title card. Kicker "VALUE DYNAMICS · THE MODEL, DERIVED", subtitle
"One quantity, one equation at a time, with the held-out error on every step".

> A I systems increasingly generate and select their own training data, through
> self-rewarding pipelines, constitutional loops and synthetic data. A model's
> current behavior is then part of what determines the data that trains it next,
> so values can persist, weaken or amplify through training itself.

## 2. What is already known, and what is missing

**On screen:** `hero_vision.svg.png` — a model generating and selecting its own
training data, fine-tuning a successor, and the loop closing.

> Alignment work has studied pieces of this. Alignment faking asks whether
> frontier models defend their values; model collapse measures degradation under
> recursive training; attractor states are where model-to-model conversations
> settle. Little of it follows the dynamics through training, across settings and
> seeds. Here I derive the model that does, one term at a time.

## 3. The quantity being tracked

**On screen:** `setup_both_models_v3.svg.png` — the two organisms, with the
prompts, sample answers and score for each.

> The tracked quantity is v, the behavioral value: the mean value score of the
> organism's answers on held-out prompts, on a zero-to-one scale. For the
> gambling organism the score is one when an answer picks the risky gamble. The
> insecure-code organism answers three fixed questions about its own coding
> habits, and its frozen base model scores each answer zero to one for how
> insecure it reads.

## 4. The round's population

**On screen:** `synthesis_experiment_kit.svg.png` — the six components of the
loop: base model, installed value, judge, candidate source, alternative source,
measure.

> Selection needs a population. For each prompt in a round, the organism writes
> six candidate answers, each with its own value score, and p is their mean. The
> judge keeps two, and the mean value score of those two is k. Training runs on
> them.

## 5. The one-round rule

**On screen:** Statement card. Headline "next value = kept candidate mean";
under the rule, "held-out mean absolute error 0.081 across 340 rounds · 0.128
for assuming no change".

> The first equation has no fitted coefficient. The next measured value is the
> mean value score of the candidates the judge kept. Holding out each complete
> experimental condition, that rule predicts the next value with mean absolute
> error zero point zero eight one across three hundred forty rounds. Assuming no
> change gives zero point one two eight.

## 6. The four positions on the line

**On screen:** `model-one-round-line.svg.png`.

> The number line places the four positions. q is the mean of the organism's own
> candidates. p is the pool mean, which differs from q when some candidates come
> from outside. k is the kept mean, and the arrow to v, the behavioral value, is
> the rule from the last card.

## 7. Decomposing the gap

**On screen:** Statement card. Headline "kept mean = pool mean + spread times
agreement"; under the rule, "R-squared 0.80 · mean absolute error 0.040 · 367
rounds with logged judge scores".

> The kept mean is only known after the judge has run, so I decompose the gap, k
> minus p, into two quantities measurable beforehand. Spread is the standard
> deviation of the candidates' value scores within a prompt; agreement is the
> correlation between the judge's preferences and those scores. Their product
> reconstructs the gap at R squared zero point eight zero, mean absolute error
> zero point zero four zero, across three hundred sixty-seven rounds.

## 8. What the decomposition costs

**On screen:** `state-variables.svg.png` — the per-round measurement recipes for
spread, agreement and the selector gap.

> Routing the forecast through the reconstructed gap costs accuracy. On matched
> rounds it predicts the next value with mean absolute error zero point one zero
> zero, against zero point zero eight five using the kept mean I actually
> observed. That is the price of predicting the selection instead of watching it.

## 9. Closing the loop

**On screen:** `model-recurrence.svg.png` — the one-round update and its closed
forms.

> Now close the loop. I hold spread, agreement and pool composition at their
> round-one values, clip each step to the zero-to-one scale, and let each
> predicted candidate mean become the next predicted value. Nothing is
> re-measured. From round one, the recurrence predicts a run's final value with
> mean absolute error zero point one one eight, against zero point four three one
> for assuming no change.

## 10. The recurrence over the agreement–spread plane

**On screen:** `synthesis-dial-plane-horizon.svg.png` — the four-round predicted
change as a background field, with observed changes as dots.

> This plane is that recurrence carried four rounds forward from first-round
> agreement and spread, with each dot an observed change. On the thirty-two
> modelable self-only runs here, endpoint error is zero point one five nine,
> against zero point two six nine for assuming no change.

## 11. Where the error lives

**On screen:** Statement card. Kicker "WHERE THE ERROR LIVES", headline "the
frozen forecast loses little with horizon"; under it, "mean absolute error 0.100
one round out, 0.130 four rounds out · 0.31 to 0.43 for assuming no change".

> Error grows slowly as the forecast looks further ahead: zero point one zero
> zero one round out, zero point one three zero four rounds out, while assuming
> no change degrades from zero point three one to zero point four three.
> Selection moves a run mostly in its first rounds and then levels off, so
> getting the early move right keeps the endpoint right. What error remains is
> mostly agreement drifting, since a judge's agreement depends on the candidate
> distribution training keeps changing.

## 12. The noise terms

**On screen:** `staged-noise-forecast.svg.png` — the stochastic rollout, one
noise term per stage.

> Real runs scatter around that single path, so I add one noise term per stage,
> sized from that stage's measured residuals. The judge's picks land around
> spread times agreement rather than exactly on it, and training lands near the
> kept mean without hitting it. Agreement drifts between rounds as a random walk.
> The value is read from a limited sample of answers, so each reading carries
> sampling noise, which moves only the value being read and not the state the
> next round starts from.

## 13. The trajectory-level check

**On screen:** Closing card, three checks — pace (total round-to-round change
0.709 simulated, 0.648 observed), turning (1.22 direction changes per run,
against 1.20 observed), endpoint spread (cross-run SD 0.387 against 0.370; 89%
of endpoints inside the 80% band). Closer line: "Spread and agreement are
measured in round one, so feedback structures can be compared before a loop is
allowed to run."

> Sampled forward, the simulated runs move about as much as the real ones, turn
> about as often, and scatter about as widely at the end. Eighty-nine percent of
> observed final values land inside the model's eighty percent bands. This rests
> on two model families, small models, four-round runs, filtered supervised
> fine-tuning and two narrow behaviors. As A I systems take a larger role in
> their own post-training, we need to know which feedback structures reinforce
> cooperation and restraint and which amplify resource-seeking or reward hacking.
> Spread and agreement are first-round measurements, so those structures can be
> compared before a loop runs.

## Figures used

`hero_vision.svg.png`, `setup_both_models_v3.svg.png`,
`synthesis_experiment_kit.svg.png`, `model-one-round-line.svg.png`,
`state-variables.svg.png`, `model-recurrence.svg.png`,
`synthesis-dial-plane-horizon.svg.png`, `staged-noise-forecast.svg.png`. All
eight are figures the writeup itself embeds.

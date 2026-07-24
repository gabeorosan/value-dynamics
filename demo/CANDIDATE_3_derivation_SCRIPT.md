# Candidate 3 — the model, derived

Target length: 3–5 minutes. Scene spec: `demo/src/scenes_cand3_derivation.json`.

This candidate is the mathematical spine of the project and nothing else. It
builds the model one term at a time, in the order I built it: the quantity being
tracked, the population selection acts on, the one-round rule, the decomposition
of that rule into things measurable before the judge runs, the recurrence, and
the noise. Every step carries its held-out error, including the step where
routing the forecast through the decomposition makes it worse. It assumes a
reader who knows machine learning and wants the equations, and it moves at
seminar pace. The palette is flat on purpose: slate and graphite for the
figures, one burnt-orange accent reserved for the two equation cards.

## 1. Title

**On screen:** Title card. Kicker "VALUE DYNAMICS · THE MODEL, DERIVED", subtitle
"One quantity, one equation at a time, with the held-out error on every step".

> This is the model at the center of the project, derived one term at a time. I
> start with the quantity being tracked, add the population selection acts on,
> then build up to a recurrence with noise in it. Each step carries its own
> held-out error.

## 2. The quantity being tracked

**On screen:** `value-measures.svg.png` — how each organism's value is measured.

> v, the behavioral value, is the mean value score of the model's answers on
> held-out prompts, on a zero-to-one scale. In the gambling model, v is the
> share of free answers that pick the risky gamble. The insecure-code model gets
> three fixed questions about its own coding habits, and its frozen base model
> scores each answer zero to one for how insecure the code reads.

## 3. The round's population

**On screen:** `synthesis_experiment_kit.svg.png` — generate, select, train,
re-measure.

> Now the population selection acts on. For each prompt in a round, the organism
> writes six candidate answers, each with its own value score, and p is their
> mean. The judge keeps two, and the mean of those two is k.

## 4. The one-round rule

**On screen:** Statement card. Headline "next value = kept candidate mean";
under the rule, "held-out mean absolute error 0.081 across 340 rounds · 0.128
for assuming no change".

> The first equation has no fitted coefficient. The next measured value is the
> mean value of the candidates the judge kept. Holding out each complete
> experimental condition, that rule predicts the next value with mean absolute
> error zero point zero eight one across three hundred forty rounds. Assuming no
> change gives zero point one two eight.

## 5. The four positions on the line

**On screen:** `model-one-round-line.svg.png`.

> The number line puts the four positions together. q is the mean of the
> organism's own candidates. p is the pool mean, which differs from q when some
> candidates come from an outside source. k is the kept mean. And v is the
> behavioral value, the coordinate the model forecasts. The green arrow is the
> rule from the last card.

## 6. Decomposing the gap

**On screen:** Statement card. Headline "kept mean = pool mean + spread times
agreement"; under the rule, "R-squared 0.80 · mean absolute error 0.040 · 367
rounds with logged judge scores".

> The kept mean is only known after the judge runs, so I decompose the gap, k
> minus p, into two quantities I can measure first. Spread is the standard
> deviation of the candidates' value scores within a prompt. Agreement is the
> correlation between the judge's preferences and those same scores. Their
> product reconstructs the gap at R squared zero point eight zero, mean absolute
> error zero point zero four zero, over three hundred sixty-seven rounds.

## 7. What the decomposition costs

**On screen:** `state-variables.svg.png` — the per-round measurement recipes.

> Going through the reconstructed gap costs accuracy. On matched rounds,
> forecasting the next value this way gives mean absolute error zero point one
> zero zero. Using the kept mean I actually observed gives zero point zero eight
> five. That is the price of predicting the selection instead of watching it.

## 8. Closing the loop

**On screen:** `model-recurrence.svg.png` — the one-round update and its closed
forms.

> Now close the loop. I hold spread, agreement, and pool composition at their
> round-one values, clip each step to the zero-to-one scale, and let each
> predicted candidate mean become the next predicted value. Started at round
> one, the recurrence predicts a run's final value with mean absolute error zero
> point one one eight, against zero point four three one for assuming no change.

## 9. Where the error lives

**On screen:** `model-ladder-horizon.svg.png` — forecast error against horizon.

> Horizon does not hurt much. Mean absolute error is zero point one zero zero
> one round out and zero point one three zero four rounds out, while assuming no
> change degrades from zero point three one to zero point four three. Selection
> moves a run mostly in its first rounds and then levels off, so getting the
> early move right keeps the endpoint right. Most of the error left over is
> agreement drifting, because the judge's agreement depends on the candidate
> distribution in front of it, which training changes.

## 10. The noise terms

**On screen:** `staged-noise-forecast.svg.png` — the stochastic rollout.

> Real runs scatter around that path, so I add one noise term per stage, sized
> from that stage's measured residuals. The judge's picks land around spread
> times agreement rather than exactly on it. Training lands near but not on the
> kept mean. Agreement drifts between rounds as a random walk. And the value is
> read from a limited number of sampled answers, so each reading carries
> sampling noise. That last term touches only the value being read, not the
> state the next round starts from.

## 11. The trajectory-level check

**On screen:** Closing card, three checks — pace (total round-to-round change
0.709 simulated, 0.648 observed), turning (1.22 direction changes per run,
against 1.20 observed), endpoint spread (cross-run SD 0.387 against 0.370; 89%
of endpoints inside the 80% band).

> Total round-to-round value change over a run is zero point seven zero nine
> simulated against zero point six four eight observed. Runs change direction
> one point two two times against one point two zero. The cross-run standard
> deviation of endpoints is zero point three eight seven against zero point
> three seven zero, and bands built to hold eighty percent of simulated
> endpoints hold eighty-nine percent of the observed ones.

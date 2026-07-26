# Selection differentials predict where a judging loop takes a model's values

**Epistemic status.** I completed this project over five weeks for BlueDot
Impact's Technical AI Safety Project Sprint. It is two open-weight model families
at 4B and 7B, two installed value orientations, and short runs, so read
the numbers as a description of these loops rather than as constants. Every number
traces to a committed result file through a named scorer, and the predictive model
has no fitted coefficient.

**Summary.**

- I installed a value in a model, put the model in a loop where a judge selects
  which of its own answers it trains on next, and measured what the value did
  over rounds.
- Each round, the two kept answers differ from the pool average by the pool's
  spread times the judge's agreement. Training then moves the value to that kept
  average. There is no fitted coefficient in either step.
- Iterating that from round-one measurements predicts a run's final value with
  mean absolute error 0.118 on the 0-to-1 value scale, against 0.431 for assuming
  no change.
- Adding noise sized from the measured residuals gives a stochastic version whose
  simulated runs move about as much as the real ones, change direction about as
  often, and scatter about as widely at the end. 89% of observed final values fall
  inside the model's 80% endpoint bands.
- Two interventions moved runs in the direction the model predicts from the new
  spread and agreement: restoring spread to a collapsed pool eroded a stuck value,
  and swapping in a min-risk oracle judge reversed a run that had climbed near the
  top of the scale.

## Why follow a value through training

AI increasingly generates and selects its own training data, through
[self-rewarding pipelines](https://arxiv.org/abs/2401.10020),
[constitutional loops](https://arxiv.org/abs/2212.08073), and
[synthetic data](https://www.interconnects.ai/p/llm-synthetic-data). Alignment
work has recognized the importance of reflectivity of values and the feedback
dynamics of self-modification
([value drift](https://www.lesswrong.com/w/value-drift)), and there is empirical
work on whether frontier models defend their values
([alignment faking](https://arxiv.org/abs/2412.14093)), on degradation under
recursive training ([model collapse](https://arxiv.org/abs/2305.17493)), and on
[attractor states](https://arxiv.org/abs/2606.30571) that emerge in model–model
conversations. There is little empirical work that follows these dynamics through
training and across settings and seeds.

![install a value, close the loop, watch it move](hero_vision.svg)

In a judging loop, a model generates candidate answers, then is trained on the
answers most preferred by a judge in pairwise comparisons against alternatives.
In selection theory, the difference in means between the selected candidates and
all candidates is a selection differential. The
[Price equation](https://doi.org/10.1038/227520a0) tracks how selection changes a
population, and the
[breeder's equation](https://pmc.ncbi.nlm.nih.gov/articles/PMC7133505/) relates
the selection differential to the response in the next generation. For judging
loops, that gives three quantities to measure: variation among the candidates,
what the judge favors, and how the model changes through training.

I fine-tuned Qwen3-4B and OLMo-3-7B with value orientations, risk-seeking or
insecure-code-generating, adapted from the
[Tell Me About Yourself](https://arxiv.org/abs/2501.11120) and
[Emergent Misalignment](https://arxiv.org/abs/2506.11613) model organisms, and ran
them through selection loops that varied the judge, the candidate source, and the
alternative source.

![The round's six candidates are its pool. Held-out prompts re-measure the value between rounds.](synthesis_experiment_kit.svg)

## What gets measured

Each organism's value is the mean value score of its answers on a 0-to-1 scale.
For the gambling organism it is the share of answers that pick the risky gamble.
For the insecure-code organism it is how insecure its answers to three fixed
questions about its own coding habits are, scored 0 to 1 by its frozen base
model. Each candidate also has a judge score, the probability the judge picks it,
averaged over both option orders; for an oracle judge the judge score is set to
the value score.

![](setup_both_models_v3.svg)

Two quantities are measured each round, and together they forecast the selection
differential. **Spread** is the standard deviation of the candidates' value
scores. **Agreement** is the correlation between the judge's preferences and
those value scores. Both are computed within each prompt's pool of candidates and
then averaged over the round's prompts.

![](state-variables.svg)

## One round

In each round the judge determines which two candidates become training data. The
parameter-free one-round rule is that the next value is the kept candidate value
mean.

![](model-one-round-line.svg)

Holding each complete experimental condition out, that rule predicts the next
measured value with MAE 0.081 across all 340 rounds, compared with 0.128 for
assuming no change.

Before the judge runs, the model forecasts the selection differential as spread
times agreement, so the predicted kept mean is the pool mean plus that product.
Across 367 rounds with logged judge scores, spread times agreement reconstructs
the realized differentials at R² 0.80 and MAE 0.040. Substituting the forecast
for the observed kept mean costs a little accuracy on the same rounds: MAE 0.100
against 0.085.

![](model-recurrence.svg)

## Endpoints from first-round measurements

Spread, agreement, and pool composition are all measured in round one. Iterating
the model with those numbers frozen, and clipping each step to the 0-to-1 scale,
gives endpoint MAE 0.118, against 0.431 for assuming no change. On the 32
modelable self-only four-round runs, where every candidate comes from the updated
model, the same recurrence has endpoint error 0.159 against 0.269.

![Endpoint-model four-round value change in the background, observed change in 32 self-only runs as dots, placed by first-round agreement and spread.](synthesis-dial-plane-horizon.svg)

The forecast stays accurate as it looks further ahead: MAE 0.100 one round out
and 0.130 four rounds out, while assuming no change degrades from 0.31 to 0.43.
Selection moves a run mostly in its first rounds and then levels off, so a
forecast that gets the early move right stays right at the endpoint. Most of the
remaining error comes from agreement drifting during the run, because a judge's
agreement depends on the candidate distribution in front of it and training keeps
changing that distribution.

## Trajectories, not just endpoints

The deterministic forecast gives the average path that real runs scatter around.
The value is read from a limited number of sampled answers, so each reading
carries sampling noise, and the loop itself varies: the judge's picks land around
spread times agreement rather than exactly on it, training lands near but not
exactly on the kept mean, and agreement drifts between rounds. The stochastic
version adds a random term at each of those points, with sizes taken from the
measured residuals.

![Each noise term's size is the spread of that stage's leftover errors, pooled across all conditions except the one being forecast.](staged-noise-forecast.svg)

Sampled forward, the stochastic model reproduces the observed dynamics. Total
round-to-round value change over a run is 0.709 against 0.648 observed, runs
change direction 1.22 times against 1.20, the cross-run SD of endpoints is 0.387
against 0.370, and 89% of final values fall inside the predicted 80% band.

![](rollouts-vs-observed-spaghetti.svg)

## Interventions act through the same two quantities

Adding base-model answers to a collapsed pool restores spread, which let the
judge's agreement pull a value that had been stuck. Swapping the base-model judge
for a min-risk oracle, which sets agreement to −1, reversed a run that had
climbed near the top of the value scale. Both are single experiments, and what
they support is narrow: spread and agreement look like usable intervention
targets, and the effect of changing them can be forecast from their new values.

![](synthesis-intervention-cards.svg)

## Limitations

The training setup is two model families, small models, short runs, and filtered
SFT on a few selected answers. Extensions should use more model families, larger
models, longer runs, and compare the SFT update with
[DPO](https://arxiv.org/abs/2305.18290), online reinforcement learning against a
learned reward model, and
[constitutional feedback](https://arxiv.org/abs/2212.08073).

The behavioral scope is risk preference and insecure-code self-description only.
Future work should broaden to moral judgment,
[AI identity](https://arxiv.org/abs/2603.11353), and
[emergent misalignment](https://arxiv.org/abs/2502.17424), with evaluations for
other behaviors and internal representations.

A fixed-agreement forecast may need to expand. In preliminary duel self-judging
experiments, across six runs differing only by seed, early agreement turned
negative in the two runs that collapsed and stayed nonnegative in the four that
amplified.

More open-ended setups would give models more freedom in selecting training data,
revising system prompts, and editing the loop itself.

## Records

Every number traces to a committed result file through a named scorer, and a
claim registry maps each claim to its data, its scorer, and its current verdict.
A reproduction gate records a re-run of every modeling script, with all committed
results regenerating byte-identically.

- Code and result JSONs: https://github.com/gabeorosan/value-dynamics
- Full writeup: https://gabeorosan.github.io/value-dynamics/

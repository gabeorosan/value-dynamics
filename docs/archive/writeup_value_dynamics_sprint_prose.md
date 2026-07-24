# When AI drives its own training process, how do its values change?


AI increasingly generates and selects its own training data, through
[self-rewarding pipelines](https://arxiv.org/abs/2401.10020),
[constitutional loops](https://arxiv.org/abs/2212.08073), and
[synthetic data](https://www.interconnects.ai/p/llm-synthetic-data).
While AI alignment work has recognized the importance of considering reflectivity
of values and the resulting feedback dynamics of self-modification
([value drift](https://www.lesswrong.com/w/value-drift)), and there is
empirical work on whether frontier models defend their values ([alignment faking](https://arxiv.org/abs/2412.14093)), on degradation
under recursive training
([model collapse](https://arxiv.org/abs/2305.17493)), and on
[attractor states](https://arxiv.org/abs/2606.30571) that emerge in model–model
conversations,
there is little empirical work that follows
these dynamics through training and across settings and seeds.

In a judging loop, a model generates candidate answers, then is trained on the answers most preferred by a judge in pairwise comparisons against alternatives. In selection theory, the difference in means between the selected candidates
and all candidates is a selection differential. The
[Price equation](https://doi.org/10.1038/227520a0) tracks how selection changes
a population, and the
[breeder's equation](https://pmc.ncbi.nlm.nih.gov/articles/PMC7133505/)
relates the selection differential to the response in the next generation. For
judging loops, this gives three quantities to measure: variation among the
candidates, what the judge favors, and how the model changes through training.

I fine-tuned Qwen3-4B and OLMo-3-7B with value orientations
(risk-seeking or insecure-code-generating, adapted from the
[Tell Me About Yourself](https://arxiv.org/abs/2501.11120) and
[Emergent Misalignment](https://arxiv.org/abs/2506.11613) model organisms),
ran them through selection loops that varied the judge, candidate source, and
alternative source, and *found a simple predictive model that, using first-round
measurements, gives calibrated endpoint estimates and
reproduces the direction, pace, and spread of the observed trajectories.*



## Findings

1. **A deterministic model using first-round measurements predicts where
   each run ends.** Each round, the two kept answers differ from the pool
   average by the pool's spread (the SD of the answers' value scores)
   times the judge's agreement (the correlation of the judge's
   preferences with those scores), with no fitted coefficient; training
   then moves the value to that kept average. Iterated, this predicts a
   run's final value from its first round with a mean absolute error (MAE) of
   0.118 on the 0-to-1 value scale, versus 0.431 for assuming no change.
2. **Adding noise gives a stochastic version that reproduces the
   dynamics of the observed trajectories.**
   Simulated and observed trajectories have about the same total round-to-round
   value change (0.709 against 0.648), direction changes (1.22 against 1.20 per
   run), and cross-run endpoint SDs (0.387 against 0.370).
   Across runs, 89% of observed final values fall within the model's 80%
   endpoint bands.
3. **The effectiveness of interventions is driven by changes in the
   model's central quantities (spread and agreement).**
    - Restoring spread to a collapsed candidate pool eroded a previously
      stuck value.
    - Swapping the judge for a min-risk oracle (setting agreement to -1)
      reversed a run that had climbed near the top of the value scale.

## What I measure

Each organism's value is the mean value score of its answers: for the
gambling model, the share that pick the risky gamble; for the
insecure-code model, how insecure its answers to three fixed questions
about its own coding habits are, scored 0–1 by its frozen base model.
Each candidate has a judge score, the probability the judge picks it,
averaged over both option orders (for an oracle judge, the judge score is
set to the value score).


Two quantities are measured each round, spread and agreement, and together
they forecast the selector gap. Spread and agreement are measured within
each prompt's pool and averaged over the round's prompts.


## each round, the value moves to what the judge keeps

In each round, the judge determines which two candidates become training data.
The parameter-free one-round rule is

`next value = kept candidate value mean`.

The model tracks four positions, `q`, `p`, `k`, and `v`, and the distances
between them. `q`, `p`, and `k` are candidate-pool means; `v` is the
behavioral value measured from the organism's answers, the coordinate
the model forecasts.

Holding each complete experimental condition out, the kept-mean rule predicts
the next measured value with MAE 0.081 across all 340 rounds, compared with
0.128 for assuming no change.


Before selection, the model forecasts the selector gap as candidate spread σ
times judge agreement ρ:

predicted selector gap *g* = *ρσ*, so predicted kept mean *k* = *p* + *ρσ*.

Across 367 rounds with logged judge scores, ρσ reconstructs the realized gaps
at R² 0.80 (MAE 0.040). On matched rounds, the resulting kept-mean forecast
predicts the next value at MAE 0.100, versus 0.085 using the actual kept mean.

For endpoints, the model repeats this update from the round-one candidate mean,
holding spread, agreement, and pool composition fixed and clipping each step to
the 0-to-1 value scale. Each predicted candidate mean becomes the next predicted
value.


## Forecasting endpoints from first-round measurements

**First-round measurements forecast the whole run.** Spread, agreement, and
pool composition are all measured in round one; iterating the model with those
numbers frozen gives endpoint MAE 0.118, versus 0.431 for assuming no change.

The figure isolates the 32 modelable self-only (candidates all
organism-generated) four-round runs. On this subset, the
same recurrence has endpoint error 0.159, versus
0.269 for assuming no change. Placing each run by its first-round agreement and
spread requires the displayed background to average over the initial candidate
means and measured values; it can then be compared with observed change.



The forecast stays accurate as it looks further ahead: its MAE
on the 0-to-1 value scale is 0.100 one round out and 0.130 four rounds out,
while assuming no value change degrades
from 0.31 to 0.43. This is because selection moves a run mostly in its
first rounds and then levels off, so a forecast that gets the early move
right stays right at the endpoint. Most of the remaining error comes from
agreement drifting during the run: a judge's agreement depends on the
candidate distribution in front of it, and training changes that
distribution.

## Forecasting trajectories with stochastic rollouts

The deterministic forecast only gives the average path that real runs
scatter around. The value is read from a limited number of sampled answers, so each
reading carries sampling noise, and the loop itself varies: the judge's
picks land around ρσ rather than exactly on it, training lands near but
not exactly on the kept mean, and agreement drifts between rounds. The stochastic version of the
model adds a random term at each of these points, with sizes taken from
the measured residuals.


**The stochastic model reproduces the dynamics of the observed trajectories.**
Sampled forward, the total round-to-round value change over a run is 0.709
against 0.648 observed, runs change direction 1.22 times against 1.20, and 89%
of final values fall inside the predicted 80% band. The expected cross-run SD
of simulated endpoints is 0.387, against 0.370 observed.

## Steering trajectories with interventions

Adding base-model answers to a collapsed pool restores spread, allowing
the agreement of the judge to pull a value that was previously stuck.
Swapping the base-model judge for the min-risk oracle (making agreement
−1) reverses a run that had climbed near the top of the value scale.
These results suggest that spread and agreement could be useful as targets for
interventions, and the effect can be forecast from their new values.


## Limitations and future directions

The present training setup uses two model families, small models, short runs,
and filtered SFT on a few selected answers. Extensions should use more model
families, larger models, longer runs, and compare the SFT update with
[DPO](https://arxiv.org/abs/2305.18290), online reinforcement learning against a
learned reward model, and [constitutional
feedback](https://arxiv.org/abs/2212.08073).

The behavioral scope of this post is limited to risk preference and
insecure-code self-description. Future work should broaden to moral judgment,
[AI identity](https://arxiv.org/abs/2603.11353), and [emergent
misalignment](https://arxiv.org/abs/2502.17424), with evaluations for other
behaviors and internal representations. Preliminary duel self-judging
experiments show where a fixed-agreement forecast may need to
expand: across six runs differing only by seed, early agreement turned negative
in the two runs that collapsed and remained nonnegative in the four that
amplified.

More open-ended setups would give models more freedom in selecting training
data, revising system prompts, and editing the loop itself. Repeated games and
agentic environments could reveal whether their dynamics favor
[cooperation](https://doi.org/10.1126/science.7466396) or defection,
[resource grabbing](https://arxiv.org/abs/1912.01683), and
[reward hacking](https://arxiv.org/abs/1908.04734). Natural and cultural
selection sculpted human values; value dynamics research can help identify
artificial selection mechanisms that can be engineered into virtuous cycles
for aligning increasingly autonomous AI systems.

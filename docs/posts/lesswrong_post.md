# When AI drives its own training process, how do its values change?

I completed this project over five weeks for BlueDot Impact's
[Technical AI Safety Project Sprint](https://bluedot.org/courses/technical-ai-safety-project).

[Full writeup](https://gabeorosan.github.io/value-dynamics/) ·
[GitHub repo](https://github.com/gabeorosan/value-dynamics)

## Summary

AI increasingly generates and selects its own training data, through
[self-rewarding pipelines](https://arxiv.org/abs/2401.10020),
[constitutional loops](https://arxiv.org/abs/2212.08073), and
[synthetic data](https://www.interconnects.ai/p/llm-synthetic-data). Value dynamics
studies how values change in these feedback loops so that they can be designed to
align increasingly autonomous systems.

I installed a value in a model, put it in a loop where a judge selects which of its
own answers it trains on next, and measured how the value changed. The spread of
the candidate answers and the correlation between the judge's preferences and the
value, both measured in the first round, predict where the value ends up, with no
fitted coefficient. Adding noise sized from the measured residuals gives a
stochastic version that reproduces the direction, pace, and spread of the observed
trajectories, and two interventions moved runs the way the model says they should.

## Motivation

Alignment work has recognized the importance of reflectivity of values and the
feedback dynamics of self-modification
([value drift](https://www.lesswrong.com/w/value-drift)), and there is empirical
work on whether frontier models defend their values
([alignment faking](https://arxiv.org/abs/2412.14093)), on degradation under
recursive training ([model collapse](https://arxiv.org/abs/2305.17493)), and on
[attractor states](https://arxiv.org/abs/2606.30571) that emerge in model–model
conversations. There is little empirical work that follows these dynamics through
training and across settings and seeds.

## Setup

In selection theory, the difference in means between the selected candidates and
all candidates is a selection differential. The
[Price equation](https://doi.org/10.1038/227520a0) tracks how selection changes a
population, and the
[breeder's equation](https://pmc.ncbi.nlm.nih.gov/articles/PMC7133505/) relates the
selection differential to the response in the next generation. For judging loops,
that gives three quantities to measure: variation among the candidates, what the
judge favors, and how the model changes through training.

I fine-tuned Qwen3-4B and OLMo-3-7B with value orientations
(risk-seeking or insecure-code-generating, adapted from the
[Tell Me About Yourself](https://arxiv.org/abs/2501.11120) and
[Emergent Misalignment](https://arxiv.org/abs/2506.11613) model organisms), then ran
them through selection loops that varied the judge, candidate source, and
alternative source.

In one round, the organism writes six candidate answers per prompt (the pool), the
judge compares each against an alternative and keeps the two it prefers, those
become that round's training data, and held-out prompts measure the value again
before the next round.

![The round's six candidates are its pool. Held-out prompts re-measure the value between rounds.](../figures/synthesis_experiment_kit.svg)

For the gambling organism, the value is the share of answers that pick the risky
gamble; for the insecure-code organism it is how insecure its answers to three
fixed questions about its own coding habits are, scored 0 to 1 by its frozen base
model.

Two quantities are measured each round, within each prompt's pool and averaged
over the round's prompts. **Spread** is the standard deviation of the candidates'
value scores. **Agreement** is the correlation between the judge's preferences and
those scores.

## Findings

**The value moves to what the judge kept.** The parameter-free one-round rule is
that the next measured value is the kept candidate value mean. Holding each
complete experimental condition out, it predicts the next value with mean absolute
error 0.081 across 340 rounds, against 0.128 for assuming no change. Before the
judge runs, the model forecasts the kept-minus-pool difference as spread times
agreement; across 367 rounds with logged judge scores that product reconstructs the
realized differences at R² 0.80.

**First-round measurements forecast the whole run.** Spread, agreement, and pool
composition are all measured in round one; iterating the rule with those numbers
frozen predicts a run's final value at MAE 0.118 on the 0-to-1 scale, against 0.431
for assuming no change. The forecast holds up as it looks further ahead, 0.100 one
round out and 0.130 four rounds out, while assuming no change degrades from 0.31 to
0.43 — selection moves a run mostly in its first rounds and then levels off.

![Endpoint-model four-round value change in the background, observed change in 32 self-only runs as dots, placed by first-round agreement and spread.](../figures/auto/synthesis-dial-plane-horizon/synthesis-dial-plane-horizon.svg)

**Adding noise reproduces the trajectories, not just the endpoints.** The value is
read from a limited number of sampled answers, the judge's picks land around spread
times agreement rather than exactly on it, and training lands near but not exactly
on the kept mean. Adding a noise term at each of those points, sized from the
measured residuals, gives simulated runs that accumulate about as much
round-to-round change as the real ones (0.709 against 0.648), change direction
about as often (1.22 against 1.20 per run), and scatter about as widely at the end
(endpoint SD 0.387 against 0.370). 89% of observed final values fall inside the
predicted 80% bands.

![](../figures/auto/rollouts-vs-observed-spaghetti/rollouts-vs-observed-spaghetti.svg)

**Interventions act through the same two quantities.** Adding base-model answers to
a collapsed pool restores spread, which let the judge's agreement pull a value that
had been stuck. Swapping the base-model judge for a min-risk oracle, which sets
agreement to −1, reversed a run that had climbed near the top of the value scale.
Each is one experiment, so what they support is that spread and agreement look like
usable intervention targets whose effect can be forecast from their new values.

![](../figures/auto/synthesis-intervention-cards/synthesis-intervention-cards.svg)

## Limitations

Everything here comes from two model families at 4B and 7B running short loops, in
which each round's training update is a filtered SFT pass over a few selected
answers, and the behavior I measure covers risk preference and insecure-code
self-description and nothing else.

Most of the remaining forecast error comes from agreement drifting during a run: a
judge's agreement depends on the candidate distribution in front of it, and training
keeps changing that distribution. Preliminary duel self-judging experiments show
what a forecast that holds agreement fixed can miss. Across six runs differing only
by seed, early agreement turned negative in the two that collapsed and stayed
nonnegative in the four that amplified, so runs identical apart from a seed ended up
at opposite ends of the scale.

## Next directions

More model families, larger models, and longer runs, and a comparison of the
filtered-SFT update with [DPO](https://arxiv.org/abs/2305.18290), online
reinforcement learning against a learned reward model, and
[constitutional feedback](https://arxiv.org/abs/2212.08073).

The behavioral scope should widen beyond risk preference and code self-description
to moral judgment, [AI identity](https://arxiv.org/abs/2603.11353), and
[emergent misalignment](https://arxiv.org/abs/2502.17424), with evaluations for
internal representations and not only behavior.

More open-ended setups, where models select their own training data, revise system
prompts, and edit the loop itself. Repeated games and agentic environments could
show whether their dynamics favor
[cooperation](https://doi.org/10.1126/science.7466396) or defection,
[resource grabbing](https://arxiv.org/abs/1912.01683), and
[reward hacking](https://arxiv.org/abs/1908.04734).

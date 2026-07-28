# Tweet thread for candidate 1: the faithful walkthrough

Thirteen tweets, all under 280 characters counting each link as the 23 that X
charges for it through t.co, in the same order as the cut. Sentences
are taken from `docs/writeup_value_dynamics_sprint.md` wherever it has one, and
every claim traces to it. Results are stated as comparisons rather than as
decimals, the way the video's narration does it; the exact values are in the
writeup.

**1/**

> AI increasingly generates and selects its own training data, through self-rewarding and constitutional loops. Value dynamics studies how values change in these feedback loops so that they can be designed to align increasingly autonomous systems.

**2/**

> I fine-tuned Qwen3-4B and OLMo-3-7B with value orientations, risk-seeking and insecure-code-generating, and ran them through selection loops that varied the judge, the candidate source and the alternative source. What came out is a simple model of where a run ends up.

**3/**

> In one round, for each prompt the organism writes six candidate answers, the pool. The judge compares each against an alternative and keeps the two it prefers, those become that round's training data, and held-out prompts measure the value again before the next round.

**4/**

> For the gambling organism, the value is the share of answers that pick the risky gamble. For the insecure-code organism it is how insecure its answers to three fixed questions about its own coding habits are, scored 0 to 1 by its frozen base model.

**5/**

> Two quantities are measured each round, spread and agreement, both within each prompt's pool and averaged over the round's prompts. Spread is the SD of the answers' value scores; agreement is the correlation of the judge's preferences with those scores.

**6/**

> Each round, the two kept answers differ from the pool average by the pool's spread times the judge's agreement, with no fitted coefficient. Training then moves the value to that kept average.

**7/**

> Spread, agreement and pool composition are all measured in round one. Iterating that rule with them held fixed forecasts where a run ends up, because selection moves a run mostly in its first rounds and then levels off.

**8/**

> Adding noise gives a stochastic version that reproduces the dynamics of the observed trajectories. Simulated and observed trajectories have about the same total round-to-round value change, the same direction changes per run, and about the same cross-run endpoint spread.

**9/**

> Interventions act through the same two quantities. Restoring spread to a collapsed candidate pool eroded a value that had been stuck; swapping the judge for a min-risk oracle reversed a run that had climbed near the top of the scale.

**10/**

> What the forecast misses most is agreement drifting during a run. A judge's agreement depends on the candidate distribution in front of it, and training keeps changing that distribution, so holding agreement fixed at its round-one value will not hold forever.

**11/**

> Extensions should use more model families, larger models and longer runs, and compare filtered SFT with DPO, online RL against a learned reward model, and constitutional feedback. The behavioral scope should widen past risk preference and insecure-code self-description.

**12/**

> Open-ended setups would let models select their own training data, revise system prompts and edit the loop itself. Repeated games and agentic settings could show whether the dynamics favor cooperation or defection, resource grabbing and reward hacking.
> https://gabeorosan.github.io/value-dynamics/

**13/**

> I completed this project over 5 weeks as part of a BlueDot Project cohort. Feedback is welcome!
> https://github.com/gabeorosan/value-dynamics

## What attaches to what

The video is not part of the thread.

Each figure goes on the tweet that makes its claim. Every one is a
`docs/writeup_value_dynamics_sprint.md` embed. Render them with
`demo/src/make_thread_images.py`, which writes `demo/thread_images/`
named by tweet number.

| Tweet | Figure | Why there |
|---|---|---|
| 1 | `hero_vision.svg` | the loop the tweet names, as the thread's opening image |
| 3 | `synthesis_experiment_kit.svg` | the round the tweet describes: six candidates, two kept, re-measure on held-out prompts |
| 4 | `auto/setup-both-models/setup_both_models_v3.svg` | both organisms with example answers and their 0-to-1 value scores |
| 5 | `auto/state-variables/state-variables.svg` | the measurement recipes for spread, agreement and the selector gap |
| 6 | `auto/model-one-round-line/model-one-round-line.svg` and `auto/model-recurrence/model-recurrence.svg` | the one-round rule drawn on the value line, then the figure that writes out `kept mean = pool mean + spread × agreement` |
| 7 | `auto/synthesis-dial-plane-horizon/synthesis-dial-plane-horizon.svg` | the endpoint forecast from round-one measurements, over the 32 self-only runs |
| 8 | `auto/staged-noise-forecast/staged-noise-forecast.svg` and `auto/rollouts-vs-observed-spaghetti/rollouts-vs-observed-spaghetti.svg` | where each noise term enters, then simulated against observed trajectories |
| 9 | `auto/synthesis-intervention-cards/synthesis-intervention-cards.svg` | the two interventions and the quantity each one aims at |

Tweets 2 and 10 to 13 have no figure; they are prose.

## If someone pushes back in the replies

The likeliest objection is that a 0.118 endpoint error beats 0.431 mostly because
the no-change baseline is weak on runs that move a lot, not because round-one
measurements carry real information. The answer is the horizon numbers in the
writeup and its held-out-by-condition one-round error of 0.081 against 0.128,
where the baseline is not weak.

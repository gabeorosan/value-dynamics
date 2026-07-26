# Tweet thread for candidate 1: the faithful walkthrough

Fifteen tweets, all under 280 characters counting each link as the 23 that X
charges for it through t.co, in the same order as the cut. Sentences
are taken from `docs/writeup_value_dynamics_sprint.md` wherever it has one, and
every number traces to it. The thread is read rather than heard, so it keeps the
numbers the narration moves to the screen.

**1/**

> AI increasingly generates and selects its own training data, through self-rewarding and constitutional loops. Value dynamics studies how values change in these feedback loops so that they can be designed to align increasingly autonomous systems.

**2/**

> I fine-tuned Qwen3-4B and OLMo-3-7B with value orientations, risk-seeking and insecure-code-generating, and ran them through selection loops that varied the judge, the candidate source and the alternative source. What came out is a simple model of where a run ends up.

**3/**

> In one round, for each prompt the organism writes 6 candidate answers, the pool. The judge compares each against an alternative and keeps the 2 it prefers, those become that round's training data, and held-out prompts measure the value again before the next round.

**4/**

> The value runs 0 to 1. For the gambling organism it is the share of answers that pick the risky gamble. For the insecure-code organism it is how insecure its answers to 3 fixed questions about its own coding habits are, scored 0-1 by its frozen base model.

**5/**

> Two quantities are measured each round, spread and agreement, both within each prompt's pool and averaged over the round's prompts. Spread is the SD of the answers' value scores; agreement is the correlation of the judge's preferences with those scores.

**6/**

> The parameter-free one-round rule is that the next value is the kept candidate value mean. Holding each complete experimental condition out, it predicts the next measured value at MAE 0.081 over 340 rounds, against 0.128 for assuming no change.

**7/**

> Before selection, the model forecasts that gap as spread times agreement, so the predicted kept mean is the pool mean plus that product. Across 367 rounds with logged judge scores it reconstructs the realized gaps at R² 0.80, MAE 0.040.

**8/**

> Spread, agreement and pool composition are all measured in round 1. Iterating the model with those numbers frozen predicts a run's final value at MAE 0.118 on the 0-to-1 scale, against 0.431 for assuming no change. On the 32 self-only four-round runs, 0.159 against 0.269.

**9/**

> The forecast stays accurate as it looks further ahead, MAE 0.100 one round out and 0.130 four rounds out, while assuming no change degrades from 0.31 to 0.43. Selection moves a run mostly in its first rounds and then levels off, so getting the early move right is enough.

**10/**

> Adding a noise term at each stage, sized from the measured residuals, reproduces the observed dynamics: round-to-round change 0.709 against 0.648, direction changes 1.22 against 1.20, endpoint SD 0.387 against 0.370, and 89% of final values inside the predicted 80% band.

**11/**

> Interventions act through the same two quantities. Restoring spread to a collapsed candidate pool eroded a value that had been stuck; swapping the judge for a min-risk oracle reversed a run that had climbed near the top of the scale.

**12/**

> The present setup uses only two model families, small models, short runs, and filtered SFT on a few selected answers, and the behavioral scope is limited to risk preference and insecure-code self-description.

**13/**

> Most of the remaining forecast error comes from agreement drifting during a run. A judge's agreement depends on the candidate distribution in front of it, and training keeps changing that distribution, so a forecast that holds agreement fixed will need to expand.

**14/**

> Extensions should use more model families, larger models, longer runs, and compare filtered SFT with DPO, online RL and constitutional feedback. Open-ended setups would let models select their own data, revise system prompts and edit the loop itself.
> https://github.com/gabeorosan/value-dynamics

**15/**

> I completed this project over five weeks for BlueDot Impact's Technical AI Safety Project Sprint.
> https://gabeorosan.github.io/value-dynamics/

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
| 6 | `auto/model-one-round-line/model-one-round-line.svg` | the one-round rule drawn on the value line |
| 7 | `auto/model-recurrence/model-recurrence.svg` | this is where `kept mean = pool mean + spread × agreement` is written out |
| 8 | `auto/synthesis-dial-plane-horizon/synthesis-dial-plane-horizon.svg` | the endpoint forecast from round-one measurements, with the 32 self-only runs and their 0.159 against 0.269 |
| 10 | `auto/staged-noise-forecast/staged-noise-forecast.svg` and `auto/rollouts-vs-observed-spaghetti/rollouts-vs-observed-spaghetti.svg` | where each noise term enters, then simulated against observed trajectories |
| 11 | `auto/synthesis-intervention-cards/synthesis-intervention-cards.svg` | the two interventions and the quantity each one aims at |

Tweets 2, 9, 12, 13, 14 and 15 have no figure. Tweet 9's horizon curve is not one
of the writeup's ten embeds, and the rest are prose.

## If someone pushes back in the replies

The likeliest objection is that a 0.118 endpoint error beats 0.431 mostly because
the no-change baseline is weak on runs that move a lot, not because round-one
measurements carry real information. The answer is the horizon numbers in tweet 9
and the held-out-by-condition one-round error of 0.081 against 0.128, where the
baseline is not weak.

# Tweet thread for candidate 4 — the short cut

Eight tweets for the candidate 4 video, written at the same clip as the cut.
Every number traces to `docs/writeup_value_dynamics_sprint.md`. Links point at
`gabeorosan.github.io/value-dynamics/`.

---

**1/**

> You have a model that writes answers. Instead of paying people to rank them, you let the model pick which of its own answers to train on. A few rounds later it is not the model you started with, and your evals never told you which way it was going. Which parts of that loop can you reach?

**2/**

> The loop I ran: each round the model writes 6 candidates per prompt, a judge keeps 2, the model is fine-tuned on those 2, held-out prompts re-measure its value on a 0-to-1 scale. The share of answers picking the risky gamble, or how insecure its coding-habit self-descriptions read.

**3/**

> Two numbers come out of every round. Spread: the SD of the candidates' value scores. Agreement: the correlation between the judge's preferences and those scores. Both measured inside each prompt's pool, averaged over prompts. Everything below is those two numbers.

**4/**

> Their product reconstructs the round's kept mean minus pool mean at R² 0.80 over 367 rounds, nothing fitted. Training then moves the value to that kept mean: next value at MAE 0.081 over 340 rounds, against 0.128 for no change, every condition held out.

**5/**

> Chain those 2 steps and you forecast instead of react. Read spread, agreement and pool composition in round 1, iterate with them held fixed: final values at MAE 0.118, against 0.431 for assuming no change. On the 32 self-only 4-round runs, 0.159 against 0.269.

**6/**

> Both handles are reachable. One run had gone flat, every candidate scoring the same, so the judge had nothing to choose between. Mixing in base-model answers restored spread and the stuck value eroded. A run near the top of the scale reversed under a min-risk oracle judge (ρ = -1).

**7/**

> What that does not buy you: a band is a range, not a number. The stochastic version puts 89% of observed endpoints inside its 80% band. And agreement drifts mid-run, because it depends on the candidate distribution in front of the judge, which training keeps changing.

**8/**

> Limits: 2 model families, small models, short runs, filtered SFT, two narrow behaviors. What would have to hold before anyone leaned on it: larger models, longer runs, update rules other than SFT, wider values. https://gabeorosan.github.io/value-dynamics/

Video: tweet 1. The cut opens on the same second-person setup the tweet leads
with, so the clip reads as tweet 1 continued rather than a separate artifact.

Likely challenge: that the two interventions are causal. Each is a single run,
and mixing base-model answers into a collapsed pool changes the pool's
composition as well as its spread, so a skeptic can attribute the erosion to the
new answers rather than to the restored spread.

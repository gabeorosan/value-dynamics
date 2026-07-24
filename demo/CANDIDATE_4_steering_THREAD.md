# Tweet thread for candidate 4 — which parts of a self-training loop can you reach

One thread for the candidate 4 video. Every number traces to
`docs/writeup_value_dynamics_sprint.md`. Links point at
`gabeorosan.github.io/value-dynamics/`.

---

**1/**

> AI already writes and selects its own training data: self-rewarding pipelines, constitutional loops, synthetic data. A model's behavior now helps decide what trains it next. If those loops run in production, the question is which parts of one you can actually reach.

**2/**

> Alignment faking asks whether a model defends its values. Model collapse asks what recursive training degrades. Attractor states ask where model-model conversations settle. Little empirical work follows the dynamics through training, across settings and seeds. So I ran them.

**3/**

> Intervention 1. A run of the insecure-code organism had gone flat: every candidate answer in a round scored the same, so the judge had nothing to choose between. I mixed in answers from its frozen base model. The candidates started differing again and the stuck value eroded.

**4/**

> Intervention 2. A run of the risk-seeking organism had climbed near the top of the 0-to-1 value scale. I swapped its base-model judge for a min-risk oracle, which always keeps the least risky candidates. The trajectory reversed. Both interventions moved the same 2 numbers.

**5/**

> Spread is the SD of the value scores of a round's candidate answers, taken within each prompt's pool and averaged over prompts. Agreement is the correlation between the judge's preferences and those scores. Intervention 1 moved spread; intervention 2 put agreement at -1.

**6/**

> The loop: each round the model writes 6 candidate answers per prompt, a judge keeps 2, the model is fine-tuned on those 2, held-out prompts re-measure its value. The value runs 0 to 1: the share of answers picking the risky gamble, or how insecure its coding-habit answers read.

**7/**

> Why those 2: their product reconstructs the round's kept mean minus pool mean at R² 0.80 across 367 rounds, nothing fitted. And training moves the value to the kept mean, predicting the next measured value at MAE 0.081 over 340 rounds, against 0.128 for no change.

**8/**

> Chain those 2 steps and you forecast instead of react. Read spread, agreement and pool composition in round 1, then iterate. Final values come out at MAE 0.118, against 0.431 for assuming no change. You read the dials in round 1 instead of waiting for the run to end.

**9/**

> What that does not buy you: a band is a range, not a number. The stochastic version puts 89% of observed endpoints inside its 80% band. And agreement drifts mid-run, because a judge's agreement depends on the candidate distribution that training keeps changing.

**10/**

> Limits: 2 interventions are 2 initial tests, not a control method. Across 6 runs differing only by seed, early agreement turned negative in the 2 that collapsed. 2 model families, small models, short runs, filtered SFT. https://gabeorosan.github.io/value-dynamics/

Video: tweet 1. The cut opens on the same stakes the tweet leads with, so the
clip plays as the thread's own opening argument rather than a detour into
mechanics.

Likely challenge: that the two interventions are causal. Each is a single run,
and mixing base-model answers into a collapsed pool changes the pool's
composition as well as its spread, so a skeptic can attribute the erosion to
the new answers rather than to the restored spread.

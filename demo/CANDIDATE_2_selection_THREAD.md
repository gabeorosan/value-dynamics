# Tweet thread for candidate 2 — three findings, and how they were measured

Ten tweets, all under 280 characters. Every number traces to
`docs/writeup_value_dynamics_sprint.md`. Link points at
`gabeorosan.github.io/value-dynamics/`.

The thread mirrors the cut: the three findings are in tweets 2, 3 and 4, and the
remaining six tweets are the machinery behind them, in the same order.

---

**1/**

> In a judging loop, a model generates candidate answers, then is trained on the answers a judge prefers in pairwise comparisons against alternatives. AI increasingly generates and selects its own training data this way. I ran two fine-tuned model organisms through those loops.

**2/**

> Finding 1. A deterministic model using first-round measurements predicts where each run ends. Endpoint MAE 0.118 on the 0-to-1 value scale, against 0.431 for assuming no change. No fitted coefficient anywhere in it.

**3/**

> Finding 2. Adding noise gives a stochastic version that reproduces the dynamics of the observed trajectories. 89% of observed final values fall inside the model's 80% endpoint bands.

**4/**

> Finding 3. The effectiveness of interventions is driven by changes in spread and agreement. Restoring spread to a collapsed candidate pool eroded a stuck value. Swapping the judge for a min-risk oracle reversed a run that had climbed near the top of the scale.

**5/**

> What the value is. Gambling organism: the share of its answers picking the risky gamble. Insecure-code organism: how insecure its answers to 3 fixed questions about its own coding habits read, scored 0-1 by its frozen base model. Both on a 0-to-1 scale.

**6/**

> The two per-round measurements. Spread is the SD of a prompt's candidate value scores, averaged over the round's prompts. Agreement is the correlation between the judge's preferences and those value scores. Selection theory says to measure both.

**7/**

> The one-round rule has no fitted coefficient. The next measured value equals the mean of the two kept candidates. Held out one complete experimental condition at a time, it misses by 0.081 across 340 rounds, against 0.128 for no change, on held-out prompts.

**8/**

> Before the judge runs, the predicted selector gap is spread times agreement. Across 367 rounds that reconstructs the realized gaps at R² 0.80. Iterate the update from round 1 with spread, agreement and pool composition frozen and you get the 0.118 endpoints.

**9/**

> The noise goes in stage by stage: reading the value off sampled answers, the judge's pick, the training step, agreement drift. Simulated against observed, total movement 0.709 against 0.648, direction changes 1.22 against 1.20, endpoint SD 0.387 against 0.370.

**10/**

> Limits: 2 model families, small models, short runs, filtered SFT, 2 behaviors. Most of the remaining error is agreement drifting during a run, because agreement depends on the candidate distribution training keeps changing. gabeorosan.github.io/value-dynamics/

Video: tweet 2. The cut is findings-first, so the clip should land on the first
finding rather than on the setup — a reader who opens the video from tweet 2
hears the same claim restated with its baseline inside twenty seconds. Hanging
it off tweet 1 would sell the video as an explainer of judging loops, which is
the part it spends the least time on.

Likely challenge: that the kept-candidate mean and the next measured value are
two views of the same quantity, so 0.081 is a restatement of the training
objective rather than a prediction. Tweet 7 answers it in a clause — the value
is re-read on held-out prompts, not on the answers that were trained on — and
scene 10 of the video says it on the figure. Expect to repeat it in replies.

Second likely challenge: that endpoint MAE 0.118 against 0.431 is an easy win
because the no-change baseline is weak. The honest answer is that the baseline
is weak precisely because runs move a lot, and the useful comparison is the
horizon one — the forecast degrades from 0.100 one round out to 0.130 four
rounds out while no-change degrades from 0.31 to 0.43. That number is in the
writeup but not in the thread; keep it ready.

Third: that 89% inside an 80% band means the bands are too wide. Worth conceding
the direction of the miscalibration rather than arguing it, and pointing at the
matched dispersion statistics in tweet 9, which are what constrain the band
width.

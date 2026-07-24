# Tweet threads for candidates 2 and 4

Two threads, one per candidate video. Every number traces to
`docs/writeup_value_dynamics_sprint.md`. Links point at
`gabeorosan.github.io/value-dynamics/`.

---

## Thread for candidate 2 — a judging loop is a breeding program

**1/**

> A judging loop in AI post-training has everything evolution needs: a population that varies, a selection step, and inheritance. So I borrowed the equations breeders use, and checked whether they hold on real training runs. They mostly do, with no fitted coefficient.

**2/**

> One round is one generation. For each prompt the model writes 6 candidate answers: that is the population. A judge compares them and keeps 2: selection. The model is fine-tuned on the kept 2: inheritance. Held-out prompts then measure the trait again.

**3/**

> Every candidate has to be scoreable, so I fine-tuned Qwen3-4B and OLMo-3-7B into 2 organisms. Gambling: the value is the share of answers picking the risky gamble. Insecure-code: how insecure its answers about its coding habits read, scored 0 to 1 by its frozen base model.

**4/**

> Borrowed term 1: the selection differential, the mean trait of the selected members minus the mean over all members. Here, the mean value score of the 2 kept answers minus the mean over all 6 candidates. Two measurements set it, and I can read both before the judge runs.

**5/**

> Spread is the standard deviation of the 6 candidates' value scores within a prompt, averaged over the round's prompts. Agreement is the correlation between the judge's scores and those value scores. Spread is what selection works with; agreement is which way it sorts.

**6/**

> Borrowed term 2: the Price equation (Price, 1970). Selection moves a population through the covariance between a trait and what gets selected. Here that is spread times agreement, and their product reconstructs the realized differential at R² 0.80 across 367 rounds.

**7/**

> Borrowed term 3: the breeder's equation. Response in the next generation equals a heritability coefficient times the differential, and that coefficient is normally fitted. Here it comes out at 1, nothing fitted: the next measured value is just the kept candidate mean.

**8/**

> Holding out one whole experimental condition at a time, that parameter-free rule predicts the next measured value with mean absolute error 0.081 across 340 rounds. Assuming no change gives 0.128.

**9/**

> Iterate it from round 1 with spread, agreement, and pool composition frozen: final values come out at mean absolute error 0.118 on the 0-to-1 value scale, against 0.431 for assuming no change. Add noise sized from the residuals and 89% of observed endpoints land in the 80% band.

**10/**

> Limits: 2 model families, small models, short runs, filtered supervised fine-tuning, 2 narrow behaviors. And agreement drifts during a run, because training keeps changing the distribution the judge sees. https://gabeorosan.github.io/value-dynamics/

Video: tweet 2. That is where the loop is first drawn as a generation, so the
clip lands as the correspondence is stated rather than teasing it.

Likely challenge: that the heritability coefficient "comes out at 1" with
nothing fitted. A skeptic will read the kept candidate mean and the next
measured value as two views of the same quantity, and want to know why the
0.081 error is not a restatement of the training objective.

---

## Thread for candidate 4 — which parts of a self-training loop can you reach

**1/**

> Two things I did to a model training loop that was already running. One had gone flat, so I mixed in answers from its frozen base model, and the stuck value eroded. One had climbed near the top, so I swapped its judge, and the trajectory reversed. Here is why both worked.

**2/**

> Intervention 1. A run of the insecure-code organism had gone flat: every candidate answer in a round scored the same, so the judge had nothing to choose between. I mixed base-model answers into the pool. The candidates started differing and the value eroded. No theory yet.

**3/**

> Intervention 2. A run of the risk-seeking organism had climbed near the top. I swapped its base-model judge for a min-risk oracle, which always keeps the least risky candidates. The trajectory reversed. Its companion run did not move: its 6 candidates scored identically.

**4/**

> Both interventions changed the same 2 numbers. Spread is the standard deviation of the value scores of a round's candidate answers, taken within each prompt's pool and averaged over prompts. Agreement is the correlation between the judge's preferences and those scores.

**5/**

> Here is the loop being steered. Each round the model writes 6 candidate answers per prompt, a judge compares them and keeps 2, the model is fine-tuned on those 2, and held-out prompts measure its value again. I varied the judge, the candidate source, and the alternatives.

**6/**

> The value runs 0 to 1 and means something different per organism. For the gambling one it is the share of answers picking the risky gamble. For the insecure-code one, how insecure its answers to 3 fixed questions about its coding habits read, scored by its frozen base model.

**7/**

> Why those 2 are the handles: their product reconstructs the round's kept-answer mean minus whole-pool mean at R² 0.80 across 367 rounds, nothing fitted. And the next measured value sits at the kept candidate mean, at error 0.081 over 340 rounds, against 0.128 for no change.

**8/**

> Chain those 2 steps and you can forecast instead of react. Read spread, agreement, and pool composition in round 1, then iterate. Final values come out at mean absolute error 0.118, against 0.431 for no change. You read the dials in round 1 instead of waiting for the run to end.

**9/**

> What that does not buy you. A band is a range, not a number: the stochastic version puts 89% of observed endpoints inside its 80% band. And spread is not a dial you turn alone, since mixing outside answers changes what the pool is made of, so its mean moves too.

**10/**

> Limits: 2 interventions are 2 initial tests, not a control method. Agreement drifts mid-run as training changes what the judge sees. It rests on 2 model families, small models, short runs, filtered supervised fine-tuning, 2 narrow behaviors. gabeorosan.github.io/value-dynamics/

Video: tweet 1. The cut opens cold on the two interventions, so the clip and the
opening tweet make the same move and the thread reads as its commentary.

Likely challenge: that the two interventions are causal. Each is a single run,
and mixing base-model answers into a collapsed pool changes the pool's
composition as well as its spread, so a skeptic can attribute the erosion to
the new answers rather than to the restored spread.

# Tweet thread for candidate 2 — a judging loop is a breeding program

Ten tweets, all under 280 characters. Every number traces to
`docs/writeup_value_dynamics_sprint.md`. Link points at
`gabeorosan.github.io/value-dynamics/`.

---

**1/**

> AI already generates and selects its own training data: self-rewarding pipelines, constitutional loops, synthetic data. So a model's behavior helps decide what trains it next, and a value it holds today can persist, weaken or amplify through training itself.

**2/**

> Alignment work has named this: value drift, alignment faking, model collapse, attractor states in model-model conversations. What is thin is empirical work that follows those dynamics through training, across settings and seeds. That gap is what I went after.

**3/**

> My way in: a loop where a population varies, something selects, and what is selected is inherited is not a new kind of object. Biology has studied that structure for a century and has equations for it. So I borrowed them and checked whether they hold on real runs.

**4/**

> One round is one generation. For each prompt the organism writes 6 candidate answers: the population. A judge keeps the 2 it prefers: selection. The model is fine-tuned on those 2: inheritance. Held-out prompts then measure the value again.

**5/**

> Every candidate needs a score, so I fine-tuned Qwen3-4B and OLMo-3-7B with value orientations. Gambling: the share of answers picking the risky gamble. Insecure-code: how insecure its answers about its own coding habits read, scored 0-1 by its frozen base model.

**6/**

> Borrowed term 1: the selection differential, the selected members' mean trait minus the whole population's. Here, the mean value score of the 2 kept answers minus the mean over all 6 candidates. Two measurements set it, and I can read both before the judge runs.

**7/**

> Spread is the SD of a prompt's candidate value scores, averaged over the round's prompts. Agreement is the correlation between the judge's scores and those value scores. Spread is what selection works with; agreement is which way it sorts.

**8/**

> Borrowed term 2: the Price equation (Price, 1970). Selection moves a population through the covariance between a trait and what gets selected. Here that is spread times agreement, and their product reconstructs the realized differential at R² 0.80 across 367 rounds.

**9/**

> Borrowed term 3: the breeder's equation. Response = heritability × differential, and heritability is normally fitted. Here it is 1, nothing fitted: the next measured value is just the kept candidate mean, at error 0.081 over 340 rounds against 0.128 for no change.

**10/**

> Freeze spread, agreement and pool composition at round 1, then iterate: endpoints land at error 0.118, against 0.431 for no change, and 89% inside the 80% band. Limits: 2 small model families, short runs, filtered SFT, drifting agreement. gabeorosan.github.io/value-dynamics/

Video: tweet 1. The cut opens on the same stakes the tweet does, so the clip
lands as the argument's first move rather than as a teaser hung off the analogy.

Likely challenge: that the heritability coefficient "comes out at 1" with
nothing fitted. A skeptic will read the kept candidate mean and the next
measured value as two views of the same quantity, and want to know why the
0.081 error is not a restatement of the training objective. The answer in the
video is that the two are measured on different prompts — the value is re-read
on held-out prompts, not on the answers that were trained on — but the thread
does not have room for it, so expect to reply.

# Tweet thread for candidate 4 — the short version

Seven tweets, one per scene, at the same length and register as the cut. Every
number traces to `docs/writeup_value_dynamics_sprint.md`. Links point at
`gabeorosan.github.io/value-dynamics/`.

---

**1/**

> AI increasingly generates and selects its own training data. A model's behavior then shapes the data that trains it next, so a value it already has can persist, weaken, or amplify through training. I fine-tuned two small models with value orientations and measured which of those happens.

**2/**

> The loop: each round the model writes 6 candidate answers per prompt, a judge keeps 2, the model is fine-tuned on those 2, and held-out prompts re-measure its value on a 0-to-1 scale. The share of answers picking the risky gamble, or how insecure its coding-habit self-descriptions read.

**3/**

> Two numbers come out of every round. Spread: the SD of the candidates' value scores within a prompt, averaged over the round's prompts. Agreement: the correlation between the judge's preferences and those same scores, measured the same way.

**4/**

> The one-round rule has no fitted coefficient. Average the value scores of the 2 candidates the judge kept; that is where the value lands after training on them. Holding out each complete experimental condition: MAE 0.081 across 340 rounds, against 0.128 for assuming no change.

**5/**

> To run it forward you need the kept mean before the judge picks. Spread × agreement predicts the kept mean minus the pool mean at R² 0.80 over 367 rounds. Read spread, agreement and pool composition in round 1, hold them fixed, iterate: endpoint MAE 0.118, against 0.431 for no change.

**6/**

> That forecast is the average path real runs scatter around. Adding the measured noise gives a band, and 89% of observed endpoints fall inside the 80% band. That is a range, not a number for any one run. Most remaining error is agreement drifting, since it depends on the candidate distribution training keeps changing.

**7/**

> Limits: 2 model families, both small, short runs, filtered SFT on a few selected answers, 2 narrow behaviors. Larger models, longer runs, DPO or online RL instead of SFT, and wider values are all untested. https://gabeorosan.github.io/value-dynamics/

Video: tweet 1. The cut opens on the same two sentences, so the clip reads as
tweet 1 continued rather than a separate artifact.

Likely challenge: that a thread this short is hiding the caveats. The answer is
that tweets 6 and 7 are both limits, and the same two scenes run about a third
of the video's narration.

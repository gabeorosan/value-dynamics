# Tweet thread for candidate 3 — the model, derived

Ten tweets, all under 280 characters. Every number traces to
`docs/writeup_value_dynamics_sprint.md`.

**1/**

> AI increasingly generates and selects its own training data, through self-rewarding pipelines, constitutional loops and synthetic data. A model's current behavior then helps decide what trains it next, so its values can persist, weaken or amplify through training itself.

**2/**

> Alignment faking asks whether frontier models defend their values; model collapse measures degradation under recursive training; attractor states are where model-model conversations settle. Little of this follows the dynamics through training, across settings and seeds.

**3/**

> So I built a model that does, and derived it one term at a time against held-out runs. The tracked quantity is a behavioral value on a 0-to-1 scale. For the gambling organism it is the share of answers that pick the risky gamble rather than the sure payout.

**4/**

> For the insecure-code organism it is how insecure its answers to three fixed questions about its own coding habits read, scored 0 to 1 by its frozen base model and meaned over answers. Both organisms are small models fine-tuned to hold the value in question.

**5/**

> Selection needs a population. Each round the organism writes six candidate answers per prompt, each with its own value score, and their mean is the pool mean. The judge keeps two, and the mean of those two is the kept mean. Training runs on the kept two.

**6/**

> The first equation has no fitted coefficient. The next measured value is the mean value score of the answers the judge kept. Held out by complete experimental condition, mean absolute error 0.081 across 340 rounds, against 0.128 for assuming no change.

**7/**

> The kept mean is only known after the judge runs, so I split kept minus pool into spread, the SD of candidate value scores within a prompt, and agreement, the correlation of judge preferences with those scores. Their product reconstructs the gap at R² 0.80 across 367 rounds.

**8/**

> That routing costs accuracy. On matched rounds it predicts the next value at mean absolute error 0.100, against 0.085 using the kept mean I actually observed. That is the price of predicting the selection instead of watching it.

**9/**

> To close the loop I hold spread, agreement and pool composition at their round-one values, clip each step to 0-1, and let each predicted candidate mean become the next predicted value. Nothing is re-measured. Endpoint error 0.118, against 0.431 for assuming no change.

**10/**

> One noise term per stage, sized from its residuals. Sampled forward, runs turn 1.22 times against 1.20 observed and 89% of endpoints fall in the 80% bands. Limits: two model families, small models, four-round runs. The aim is telling reinforcing loops from eroding ones early.

Video: tweet 10 carries the candidate 3 video, since the thread is itself the
derivation and the video is the longer seminar-pace version of it. Tweet 1 now
states the problem, so a reader who stops there still gets the point.

Likely challenge: that spread times agreement reconstructing the gap at R² 0.80
is close to a definition, because the judge scores and the value scores are
correlated by construction rather than by anything the loop does.

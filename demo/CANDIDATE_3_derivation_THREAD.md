# Tweet thread for candidate 3 — how the forecast is built and tested

Eleven tweets, all under 280 characters. Every number traces to
`docs/writeup_value_dynamics_sprint.md`. The thread is read rather than heard, so
it keeps the numbers the video moved onto the screen.

**1/**

> AI increasingly generates and selects its own training data. So a model's values can move while it trains on answers it helped choose. I built a forecast for that movement and tested it on 340 rounds of selection loops. This thread is the method behind it.

**2/**

> The tracked quantity is a behavioral value on a 0-1 scale. Gambling organism: the share of answers picking the risky gamble. Insecure-code organism: how insecure its answers to 3 fixed questions about its coding habits read, scored 0-1 by its frozen base model.

**3/**

> Each round the organism writes 6 candidate answers per prompt; those 6 are the pool. A candidate's judge score is the probability the judge picks it, averaged over both option orders. The judge determines which 2 become training data. Held-out prompts re-measure the value.

**4/**

> Spread is the SD of candidate value scores within one prompt's pool. Agreement is the correlation of judge scores with those value scores. Both are computed inside a prompt, then averaged over the round's prompts. For an oracle judge the judge score is set to the value score.

**5/**

> Rule one carries no fitted coefficient: next measured value = kept candidate value mean. Each complete experimental condition is held out in turn, so nothing inside a condition predicts its own rounds. MAE 0.081 across 340 rounds, against 0.128 for assuming no change.

**6/**

> The kept mean only exists after the judge has run. So write the gap between kept mean and pool mean as spread × agreement, both measurable before selection. Across 367 rounds with logged judge scores that product reconstructs the realized gaps at R² 0.80, MAE 0.040.

**7/**

> That substitution costs accuracy, and here is how much. On matched rounds, forecasting the next value through spread × agreement gives MAE 0.100. Using the kept mean actually observed gives 0.085. That is what it costs to predict the selection instead of watching it.

**8/**

> For endpoints, iterate the update from the round-one candidate mean with spread, agreement and pool composition frozen, clipping each step to 0-1. Nothing is re-measured after round one. Endpoint MAE 0.118, against 0.431 for assuming no change.

**9/**

> Horizon costs little: MAE 0.100 one round out, 0.130 four rounds out, while assuming no change degrades from 0.31 to 0.43. Runs move early and then level off. Most of the error left is agreement drift, since a judge's agreement depends on a distribution training keeps changing.

**10/**

> One noise term per stage, each sized from that stage's residuals. Simulated runs turn 1.22 times against 1.20 observed, endpoint SD 0.387 against 0.370, and 89% of endpoints land inside the 80% bands. Limits: two model families, small models, short runs. Method in the video.

**11/**

> Every loop here was scripted. The open question is what happens when models pick their own training data, revise their system prompts, and edit the loop itself, and whether repeated games and agentic settings favour cooperation, defection, resource grabbing, or reward hacking.

Video: tweet 10 carries the candidate 3 video, since the thread is the compressed
form of the same method walk. Tweet 11 is the forward look and does the job the
closing card does in the video, so the thread does not end on a limits list.
Tweets 5 through 8 are the load-bearing ones and each states its own held-out
error, so a reader who stops partway still has a scored claim rather than a
promise.

Likely challenge, from the audience this thread is aimed at: that spread ×
agreement reconstructing the gap at R² 0.80 is close to a definition, since judge
scores and value scores are correlated by construction rather than by anything
the loop does. Tweet 7 is the answer to keep in reserve. The factorization is
scored against the kept mean it replaces, on matched rounds, and it loses accuracy
doing so, 0.100 against 0.085. Tweet 5 is the second half of the answer: the rule
it feeds is held out by complete experimental condition, so a condition never
helps predict its own rounds.

Second likely challenge: 89% of endpoints inside an 80% band means the bands are
wide. Say so rather than defending it. The band is the model's, the check is
one-sided in the model's favour, and the run count is small.

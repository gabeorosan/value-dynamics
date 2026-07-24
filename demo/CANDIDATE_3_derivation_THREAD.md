# Tweet thread for candidate 3 — deriving the equation

Ten tweets, all under 280 characters. Every number traces to
`docs/writeup_value_dynamics_sprint.md`.

**1/**

> We can score what a model values today: fixed questions, scored answers, one average. Nothing says what that number becomes after the model trains on data it helped choose. Evaluation gives a position and nothing gives the motion. So I derived the missing equation.

**2/**

> The tracked quantity is a behavioral value on a 0-1 scale, the mean value score of the model's answers to held-out prompts. For the gambling organism that score is the share of answers picking the risky gamble over the sure payout.

**3/**

> For the insecure-code organism it is how insecure its answers to three fixed questions about its own coding habits read, scored 0-1 by its frozen base model. Both organisms are small models fine-tuned to hold the value in the first place.

**4/**

> Each round the organism writes 6 candidate answers per prompt, each with a value score, and their mean is the pool mean. A judge compares them in pairs and keeps 2, whose mean is the kept mean. Training runs on those 2, then held-out prompts re-measure the value.

**5/**

> Equation one has no fitted coefficient. Next measured value = kept mean. Held out by complete experimental condition, mean absolute error 0.081 across 340 rounds, against 0.128 for assuming no change.

**6/**

> The kept mean only exists after the judge runs. Equation two splits kept minus pool into spread, the SD of candidate value scores within a prompt, and agreement, the correlation of judge scores with them. Their product reconstructs the gap at R² 0.80, MAE 0.040, 367 rounds.

**7/**

> That substitution costs accuracy. Here is how much: forecasting the next value through spread × agreement gives MAE 0.100, against 0.085 using the kept mean I actually observed. That is the price of predicting the selection instead of watching it.

**8/**

> Equation three closes the loop. Freeze round-one spread, agreement and pool composition, iterate the update, clip each step to 0-1. Nothing is re-measured after round one. Endpoint MAE 0.118, against 0.431 for assuming no change.

**9/**

> Horizon costs little: MAE 0.100 one round out, 0.130 four rounds out, while assuming no change degrades from 0.31 to 0.43. Runs move early and then level off. The error that is left is mostly agreement drifting as training changes the candidate distribution the judge sees.

**10/**

> One noise term per stage, each sized from that stage's residuals, and the simulated runs turn 1.22 times against 1.20 observed, with 89% of endpoints inside the 80% bands. Limits: two model families, small models, short runs. Full derivation in the video.

Video: tweet 10 carries the candidate 3 video, since the thread is the short form
of the same derivation and the video is the seminar-pace version. Tweet 1 states
the gap on its own, so a reader who stops there still has the point.

Likely challenge: that spread times agreement reconstructing the gap at R² 0.80
is close to a definition, because judge scores and value scores are correlated by
construction rather than by anything the loop does. Tweet 7 is the answer to keep
in reserve: the decomposition is scored against the kept mean it replaces, and it
loses accuracy doing so.

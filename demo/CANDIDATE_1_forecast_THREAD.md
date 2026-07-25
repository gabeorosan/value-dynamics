# Tweet thread for candidate 1: the faithful walkthrough

Ten tweets, all under 280 characters, in the writeup's own order. Every number
traces to `docs/writeup_value_dynamics_sprint.md`.

**1/**

> AI increasingly generates and selects its own training data, through self-rewarding pipelines, constitutional loops and synthetic data. A model's behavior helps determine the data that changes it. Little empirical work follows that through training, across settings and seeds.

**2/**

> In a judging loop, a model generates candidate answers, then is trained on the ones a judge prefers in pairwise comparisons against alternatives. Selection theory gives three things to measure: variation among the candidates, what the judge favors, how training moves the model.

**3/**

> I fine-tuned two open-weight models with value orientations, one risk-seeking and one insecure-code-generating. Each round the organism writes 6 candidates per prompt, the judge keeps 2, those are the training data, held-out prompts re-measure. Runs varied all three sources.

**4/**

> The value runs 0 to 1. For the gambling organism it is the share of answers picking the risky gamble. For the insecure-code organism it is how insecure its answers to three fixed questions about its own coding habits read, scored by its frozen base model.

**5/**

> Spread is the SD of the candidates' value scores within a prompt, averaged over the round's prompts. Agreement is the correlation between the judge's preferences and those same scores. Their product reconstructs the realized selection gaps at R² 0.80 across 367 rounds, MAE 0.040.

**6/**

> The one-round rule has no fitted coefficient. The next measured value is the mean value score of the two candidates the judge kept. Held out by complete experimental condition, it predicts the next value at MAE 0.081 across 340 rounds, against 0.128 for assuming no change.

**7/**

> Replacing the actual kept mean with spread × agreement costs little. On matched rounds the forecast predicts the next value at 0.100, against 0.085 using the actual kept mean. For endpoints, repeat that update from round one with spread, agreement and pool composition held fixed.

**8/**

> Iterated, that predicts a run's final value from its first round at MAE 0.118, against 0.431 for assuming no change. It degrades slowly with horizon: 0.100 one round ahead and 0.130 four rounds ahead, while assuming no change goes from 0.31 to 0.43.

**9/**

> On the 32 self-only four-round runs, endpoint error is 0.159 against 0.269. Adding noise where the loop varies, sized from the residuals, gives simulated runs that accumulate 0.709 of round-to-round change against 0.648 observed and change direction 1.22 times against 1.20.

**10/**

> Endpoint SD across runs is 0.387 simulated against 0.370 observed, and 89% of observed endpoints fall inside the 80% band. Interventions target the same two numbers: restoring spread eroded a stuck value, a min-risk oracle judge reversed a run near the top of the scale.

Limits to state in the replies rather than the thread: two model families, small
models, short runs, filtered SFT, and two behaviors, risk preference and
insecure-code self-description. Both intervention results are single experiments.

Video: tweet 1 carries the candidate 1 video, so the framing and the walkthrough
arrive together in the slot that gets the most impressions.

Likely challenge: that a 0.118 endpoint error beats 0.431 mostly because the
no-change baseline is weak on runs that move a lot, not because round-one
measurements carry real information. The answer to have ready is the horizon
curve (0.100 one round out, 0.130 four rounds out) and the held-out-by-condition
one-round error of 0.081 against 0.128, where the baseline is not weak.

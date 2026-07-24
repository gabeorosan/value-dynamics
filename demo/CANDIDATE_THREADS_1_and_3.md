# Tweet threads for demo candidates 1 and 3

Two threads, one per candidate video. Every number traces to
`docs/writeup_value_dynamics_sprint.md`.

## Thread for candidate 1 — the forecasting challenge

**1/**

> I ran small self-training loops: a model writes six answers, a judge keeps two, the model is fine-tuned on those, repeat. Measurements taken in round one predict where the behavior lands four rounds later, off by 0.118 on a 0-to-1 scale against 0.431 for assuming no change.

**2/**

> Two organisms, scored 0 to 1. OLMo-3-7B, fine-tuned to prefer risky gambles: its value is the share picking the risky gamble. Qwen3-4B, fine-tuned to write insecure code: its value is how insecure its answers about its coding habits read, scored by its frozen base model.

**3/**

> After round one I have six candidates per prompt, the judge's scores on them, and one measured value. Four rounds left. I did not know whether any of that says where the value ends up, and the baseline to beat was assuming no change, which misses the final value by 0.431.

**4/**

> So I measured two things each round. Spread is the standard deviation of the six candidates' value scores. Agreement is the correlation between the judge's preferences and those same scores. Spread is what selection has to work with, agreement is which way it sorts.

**5/**

> Their product predicts the gap between the kept answers and the pool mean at R² 0.80 across 367 rounds, mean absolute error 0.040. The one-round rule that follows has no fitted coefficient: the next measured value is the mean value score of the two answers the judge kept.

**6/**

> Holding out each complete experimental condition, that rule predicts the next value with mean absolute error 0.081 across 340 rounds, against 0.128 for assuming no change.

**7/**

> For endpoints I apply the update repeatedly with round-one spread, agreement, and pool composition frozen, clipping each step to the 0-to-1 scale. Nothing is re-measured. Error is 0.100 one round out and 0.130 four rounds out, while assuming no change degrades from 0.31 to 0.43.

**8/**

> One predicted number per run is the average path runs scatter around. Adding noise at each stage, sized from the residuals, gives simulated runs that move about as much as real ones, 0.709 of round-to-round change against 0.648. 89% of observed endpoints fall in the 80% bands.

**9/**

> The same measurements say where to push. In one run the pool had collapsed and the value sat still; base-model answers restored spread and it moved again. Another run near the top reversed when I swapped in a judge that always picks the safe gamble. Both are single experiments.

**10/**

> Limits: two model families, small models, four-round runs, filtered supervised fine-tuning, and two narrow behaviors, risk preference and insecure-code self-description. Longer runs, larger models, DPO and online RL are all untested. Writeup and result files below.

Video: tweet 1 carries the candidate 1 video, so the forecasting claim and the
demo arrive together in the slot that gets the most impressions.

Likely challenge: that a 0.118 endpoint error beats 0.431 mostly because the
no-change baseline is weak on runs that move a lot, not because round-one
measurements carry real information.

## Thread for candidate 3 — the model, derived

**1/**

> One equation with no fitted coefficient tracks what a self-training loop does to a model's behavior: the next measured value is the mean value score of the answers the judge kept. Held out by condition, mean absolute error 0.081 across 340 rounds, against 0.128 for no change.

**2/**

> The quantity tracked, on a 0-to-1 scale. For OLMo-3-7B, the gambling organism, it is the share picking the risky gamble. For Qwen3-4B, the insecure-code organism, how insecure its answers to three fixed questions about its coding habits read, scored by its frozen base model.

**3/**

> The population selection acts on: each round the model writes six candidate answers per prompt, each with its own value score, and their mean is the pool mean. The judge keeps two, and the mean of those two is the kept mean. Training runs on the kept two.

**4/**

> Kept mean minus pool mean is a selection differential, which is where I took the shape of this from, via the breeder's equation. It is only known after the judge has run, so the useful version splits it into two quantities I can measure first.

**5/**

> Spread is the standard deviation of the candidates' value scores within a prompt. Agreement is the correlation between the judge's preferences and those scores. Their product reconstructs the gap at R² 0.80, mean absolute error 0.040, across 367 rounds with logged judge scores.

**6/**

> Going through the reconstructed gap costs accuracy. On matched rounds, forecasting the next value that way gives mean absolute error 0.100, against 0.085 using the kept mean I actually observed. That is the price of predicting the selection instead of watching it.

**7/**

> Closing the loop: I hold spread, agreement, and pool composition at their round-one values, clip each step to the 0-to-1 scale, and let each predicted candidate mean become the next predicted value. From round one, endpoint error is 0.118, against 0.431 for assuming no change.

**8/**

> Horizon costs little: 0.100 one round out, 0.130 four rounds out, against 0.31 to 0.43 for assuming no change. Most of the remaining error is agreement drifting, since a judge's agreement depends on the candidate distribution in front of it, which training keeps changing.

**9/**

> Then one noise term per stage, sized from that stage's residuals: the judge's picks land around spread times agreement rather than on it, training lands near the kept mean, agreement drifts as a random walk, and each value reading comes from a limited sample of answers.

**10/**

> Sampled forward, runs change direction 1.22 times against 1.20 observed; the standard deviation of endpoints across runs is 0.387 against 0.370. Caveats: two model families, small models, four-round runs, filtered supervised fine-tuning, two narrow behaviors.

Video: tweet 10 carries the candidate 3 video, since the thread is itself the
derivation and the video is the longer seminar-pace version of it.

Likely challenge: that spread times agreement reconstructing the gap at R² 0.80
is close to a definition, because the judge scores and the value scores are
correlated by construction rather than by anything the loop does.

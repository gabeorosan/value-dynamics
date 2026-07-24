# Tweet thread for candidate 1: the forecasting challenge

Ten tweets, all under 280 characters. Every number traces to
`docs/writeup_value_dynamics_sprint.md`.

**1/**

> Three empirical results describe what happens when models train on model-made material: alignment faking, model collapse, attractor states. Each is a still photograph. None follows a single value through training, across settings and seeds, while it moves. So I filmed it.

**2/**

> It matters now because a model's own answers already supply much of its next training data. The model generates candidates, a selector keeps some, training folds those back in, and the successor replaces it. What the model values helps decide what trains it next.

**3/**

> Two model families, fine-tuned to be risk-seeking or insecure-code-generating, scored 0 to 1. Gambling organism: the share of answers picking the risky gamble. Insecure-code organism: how insecure its answers about its own coding habits read, scored by its frozen base model.

**4/**

> Each round the organism writes 6 candidates per prompt, a judge keeps 2, training uses those, repeat. After round one I have the candidates, the judge's scores and one measured value. Four rounds left, and assuming no change misses the final value by 0.431.

**5/**

> So I measured two things every round. Spread is the SD of the candidates' value scores within a prompt. Agreement is the correlation between the judge's scores and those same value scores. Spread is what selection has to work with, agreement is which way it sorts.

**6/**

> Their product reconstructs the gap between the kept answers and the pool at R² 0.80 across 367 rounds, MAE 0.040. The one-round rule that follows has no fitted coefficient. The next measured value is the mean value score of the two answers the judge kept.

**7/**

> Holding out each complete experimental condition, that rule predicts the next value with MAE 0.081 across 340 rounds, against 0.128 for assuming no change. It is the whole model, and nothing in it was fitted.

**8/**

> For endpoints I repeat that update from round one with spread, agreement and pool composition frozen, clipping to the 0-to-1 scale. Nothing is re-measured. Endpoint MAE 0.118 against 0.431 for no change, and 0.100 one round out against 0.130 four rounds out.

**9/**

> One predicted number per run is only the average path runs scatter around. Adding noise where the loop varies, sized from the residuals, gives runs that move about as much as real ones, 0.709 of round-to-round change against 0.648. 89% of endpoints fall in the 80% bands.

**10/**

> The same measurements say where to push. A collapsed pool left a value stuck; mixing in base answers restored spread and it eroded. A run near the top reversed under a min-risk oracle judge. Limits: two model families, small models, short runs, filtered SFT, two behaviors.

Video: tweet 1 carries the candidate 1 video, so the framing and the demo arrive
together in the slot that gets the most impressions.

Likely challenge: that a 0.118 endpoint error beats 0.431 mostly because the
no-change baseline is weak on runs that move a lot, not because round-one
measurements carry real information. The answer to have ready is the horizon
curve (0.100 one round out, 0.130 four rounds out) and the held-out-by-condition
one-round error of 0.081 against 0.128, where the baseline is not weak.

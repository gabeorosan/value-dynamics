# Each round, the value moves about 80% of the way toward the answers the judge kept

One dot per selection-loop round (340 rounds from 74 score-logged runs: OLMo and
Qwen organisms, risk and self-report value axes, self and frozen judges). The
x-axis is the pull — the mean value-score of the answers the judge kept this
round minus the model's measured value at the start of the round; the y-axis is
the drift — the measured value after the round's fine-tune minus the value at
the start of the round. A single fitted line, drift = 0.83 × pull (intercept
−0.007, r = 0.80, n = 340), covers all three pool compositions: rounds where
the candidate pool is entirely the organism's own answers (slope 0.824,
r = 0.706, 244 rounds), rounds with outside answers injected (slope 0.711,
r = 0.802, 64 rounds), and rounds where a peer organism's answers invade the
pool (slope 0.951, r = 0.985, 32 rounds). The side panel shows why the distance
must be measured from the current value rather than from the pool mean: the
older selection-gap predictor (kept mean minus pool mean) correlates with drift
at only r = 0.58 pooled, because injected and invading answers move the pool
mean away from the organism while the kept-mean-minus-current-value distance
keeps predicting. Descriptive association, not a mechanism claim.

Source data: `experiments/spread_util_unified.json` (`records` for the dots,
`movement_law` for the fitted slopes; the generator recomputes the pooled fit
from `records` and asserts it matches before drawing).

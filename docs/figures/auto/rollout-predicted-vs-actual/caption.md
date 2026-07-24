**First-round measurements roughly predict where a run ends.** Each dot is one
self-training run (67 total): the x-position is the endpoint a simple loop
model predicts when it is fed only that run's round-1 measurements (value,
candidate spread, judge utilization, supplier level) and rolled forward with
scalars fit leave-one-run-out; the y-position is the endpoint the run actually
reached, both on the 0–1 value scale. Dots on the dashed diagonal were
predicted exactly. Color gives the pool composition: self-only (blue, trains
only on its own outputs), base-mixed (green, half the pool from the base
model), peer-mixed (red, half the pool from a peer model). Endpoint mean
absolute error is 0.175 overall, versus 0.351 for assuming no change from
round 1, and 0.042 on the peer-invasion runs. The two named failure modes are
exactly the runs where a round-1 snapshot cannot suffice: the nine hollow dots
had their judge swapped mid-run (the round-1 judge reading no longer applies),
and the single called-out solid dot (condition frozen_base, seed 5) is the
run whose judge utilization rose mid-run — the bloom. Exactly coincident dots
are fanned slightly so pile-ups (e.g. the peer-mixed runs at 1.0) stay
visible.

Source data: `experiments/simple_model_rollout.json` (`per_run` for the 67
points and the schedule/bloom flags; `aggregates` for the three error
figures). Regenerate with `python3 rollout-predicted-vs-actual.py`.

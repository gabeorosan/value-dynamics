# First-round measurements predict where selection drives a run

A simple selection-force model reads only each run's first round — the measured
value entering round 1, the candidate value spread, the judge's utilization of
the value axis (the correlation between the judge's score for a candidate and
that candidate's value reading, measured on the round-1 pool), and the supplier
level (mean value of the co-generator's round-1 candidates) — then rolls the
value forward with no further peeking; scalars are fit leave-one-run-out.
Because it is a selection-force model, it can only be judged where a judge
actually selects on the value axis, so runs are split by the `regime` field
rather than pooled. Left panel: the 36 selection-driven runs (24 mixed-pool
intervention runs in blue, 12 self-only runs with a judge that grips the axis
in green) hug the predicted = actual diagonal — mean endpoint absolute error
0.106 on the 0–1 value scale, versus 0.431 for predicting no change. Right
panel: the 22 self-weak runs (base judge, frozen-copy judge, or plain
self-reference; round-1 utilization near zero) — the model predicts little
movement (mean predicted move 0.10, versus 0.43 in the left panel) and the runs
wander off the diagonal, mostly upward; that wandering is training instability,
not selection (error 0.197 versus 0.215 for predicting no change). The red
hollow dot (condition frozen_base, seed 5) is the bloom: its judge utilization
rose mid-run, which a model that fixes utilization at round 1 cannot see. The
nine fan-then-press schedule cells (judge swapped mid-run, endpoint error
0.399) are excluded for the same reason.

Source data: `experiments/simple_model_rollout.json` (`per_run`, 67 runs;
`aggregates`), produced by `scripts/analysis_simple_model_rollout.py` from
`experiments/spread_util_unified.json`.

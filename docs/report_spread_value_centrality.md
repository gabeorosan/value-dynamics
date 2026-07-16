# Mean position sets total variance; prompt structure sets selectable spread

*Supporting binary-score geometry for
`docs/report_spread_conversion_model.md`. Scorer:
`scripts/analysis_spread_value_centrality.py` →
`experiments/spread_value_centrality.json`. Source: 280 binary risk-axis
rounds from 59 runs. The 60 continuous self-report rounds are analyzed
separately in `report_spread_definition_audit.md`.*

**Rollout follow-up.** The binary geometry below improves prediction of the
future spread trajectory, but the closed-loop test in
`report_spread_rollout_bakeoff.md` finds that feeding the predicted spread back
does not improve unseen-condition endpoint forecasts over holding first-round
spread fixed (selection-driven MAE 0.139 versus 0.127). Treat this as the
generator's spread equation, not yet as a better complete-run forecaster;
later judge/value agreement is the larger missing state.

Let `q` be the mean of the candidate risk scores. Because each risk score is
0 or 1, total score variance under uniform prompt/candidate sampling is exactly
`q(1−q)`. The selector does not act on all of that variance: it compares
candidates only within the same prompt. The relevant identity is

`mean within-prompt variance = q(1−q) − variance of prompt means`.

Reported spread takes one further step: it is the population SD inside each
prompt, averaged over prompts. Therefore it is generally smaller than
`sqrt[q(1−q)]`, the total SD including between-prompt differences.

## Candidate position is the right coordinate

The separate pre-round behavioral value and the candidate-pool mean are highly
correlated (`r = 0.916`), so both track where the generated score distribution
sits. The candidate mean is the direct coordinate because it participates in
the exact variance identity.

On the 80 mixed binary-risk rounds:

- behavioral-value centrality explains 62.5% of spread variation;
- candidate-pool `q(1−q)` explains 95.5%;
- total candidate SD `sqrt[q(1−q)]` explains 94.8%; and
- after total candidate SD is included, behavioral centrality adds 0.0009 R²
  pooled, 0.00005 within run, and 0.000008 in first differences.

This is useful as score accounting: use the mean of the model's own candidates
when modeling the generator, and the mean of the whole offered pool when
describing the selector's current material.

## The round-to-round model

The dynamic sequence is:

`training displacement → change in own candidate mean q`

`q_next(1−q_next) − between-prompt variance_next → next within-prompt variance`

`within-prompt variance distribution → mean within-prompt SD`.

The first arrow is learned from consecutive rounds. The second is an exact
binary-score identity once the next prompt-mean variance is known. A simple
leave-one-run-out model that persists the prompt-mean variance and the small
mean-SD/RMS-SD difference predicts next own-source spread at R² 0.778 over 221
binary-risk transitions, versus 0.581 for spread persistence. In the 60 mixed
risk transitions it scores 0.653 versus 0.193.

## Outside supply

In a mixed prompt, whole-pool variance splits exactly into within-source
variance plus

`w_self · w_supplier · (mean_self − mean_supplier)²`.

Outside candidates can therefore change three quantities at once: the offered
pool mean, the displacement of kept answers relative to the host's candidates,
and the between-source variation available to the selector. As host and
supplier converge, the between-source term shrinks. For next-round generator
dynamics, carry the host's own mean and within-prompt spread; for the current
selection step, use the whole offered pool.

## Scope

The `q(1−q)` identity is specific to binary risk scores. It does not describe
the continuous self-report candidate scores. Their within-prompt spread is
still defined and useful for selector accounting, but their next-round spread
is better predicted by persistence in the current data.

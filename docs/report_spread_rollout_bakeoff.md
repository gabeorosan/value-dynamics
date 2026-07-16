# Closed-loop rollout test of the spread model and its alternatives

*2026-07-15. Analysis: `scripts/analysis_spread_rollout_bakeoff.py` →
`experiments/spread_rollout_bakeoff.json`. Input: 340 logged rounds from 74
runs; 67 runs / 312 rounds are modelable from round 1 because seven random
arms have no judge/value agreement score.*

## What was simulated

This is the multi-round test that the one-step spread analyses did not do.
For every held-out run, the simulator observes only its first-round state:

- the mean and spread of the host model's generated candidates and the spread
  of the whole offered pool;
- the separate behavioral value;
- judge/value agreement;
- and, in a mixed pool, the supplier's mean, spread, and pool share.

Coefficients are fit on other runs, then the held-out state is rolled through
all later rounds without reading its later candidates, spread, agreement, or
value. The closed loop is:

`offered spread × agreement → selector gap`

`selector gap + supplier shift → kept − host-generated mean`

`kept − host-generated mean → next host-generated mean`

`next host-generated mean → next own-source spread`

`kept − behavioral value → next behavioral value`.

The binary-risk geometry model predicts next within-prompt variance from the
new candidate mean, persisted between-prompt variance, and the exact identity
`V_within = q(1−q) − V_between`. The continuous self-description score has no
Bernoulli identity, so it uses a fitted autoregression. Agreement and supplier
state are frozen at round 1 in the genuine forecast. Later observed values are
used only in explicitly labeled oracle diagnostics.

Two validation schemes are reported:

- **leave one run out (LORO):** another seed from the same condition may remain
  in training;
- **leave one condition out (LOCO):** the complete intervention/judge condition
  is unseen. LOCO is the relevant test of whether a proposed spread definition
  transports to a new rollout regime.

## The model predicts the selection-driven rollouts

Using mean within-prompt population SD and the binary geometry recurrence, the
LOCO endpoint MAE is **0.139** on the 36 selection-driven runs, versus **0.431**
for holding the starting value fixed. It gets the direction right on **28/31
(90%)** selection-driven runs whose endpoint moves by at least 0.15.

| regime | runs | closed-loop endpoint MAE | no-change MAE |
|---|---:|---:|---:|
| selection-driven | 36 | **0.139** | 0.431 |
| mixed interventions | 24 | **0.138** | 0.450 |
| gripping self-only judges | 12 | **0.140** | 0.393 |
| weak self-only selection | 22 | 0.205 | 0.215 |
| judge swapped mid-run | 9 | 0.392 | **0.361** |

The model captures the invasion takeovers, both Qwen injection collapses, and
the direction of self-judge erosion from the first pool. The large misses are
the scheduled judge swaps, spontaneous weak-selection blooms, and some rescue
cells where round-1 agreement does not represent later rounds. Those are not
small endpoint noise: they identify the state missing from the closed model.

## Refreshing once at the judge swap predicts most of the new branch

The scheduled swaps provide a direct test of the proposed remedy. At the first
pool scored by the replacement judge, I remeasure the same state used at an
ordinary round 1—behavioral value, own candidate mean, spread or support, and
judge/value agreement—then close the simulator again and read no later state.
The swap rounds are fixed by the conditions: rounds 2, 3, 4, and 5 for
`press_d1`, `press_d2`, `press_d3`, and `press_to_base`, respectively.
At the `press_to_base` seed-1 boundary the pool has zero spread, so correlation
is undefined; the identified selector input `agreement × spread` is zero and
is encoded as such rather than imputing a directional agreement.

| LOCO model on 9 judge-swap runs | round-1 forecast MAE | refresh-at-swap MAE | hold swap value fixed |
|---|---:|---:|---:|
| mean-SD geometry | 0.392 | 0.261 | 0.309 |
| frozen mean SD | 0.404 | **0.179** | 0.309 |
| frozen rankable support | 0.396 | 0.182 | 0.309 |

So yes: the one-time refresh makes the simple frozen-state model predictive
on these runs. Frozen mean SD after the refresh also gives post-swap all-round
MAE 0.156 and R² 0.601 across 48 scored rounds. It predicts the direction from
the swap boundary in **6/7** runs that subsequently move by at least 0.15. The
result is essentially unchanged under leave-one-run-out validation (endpoint
MAE 0.179).

The sample is only nine runs and the benefit is heterogeneous: the refreshed
frozen-SD forecast improves absolute endpoint error in 6/9 runs. Its paired
mean error reduction relative to the original forecast is 0.224, with a
run-bootstrap 95% interval of −0.067 to 0.508; relative to swap-time
persistence the reduction is 0.130 (−0.067 to 0.312). Treat the boundary reset
as a strong descriptive repair to test prospectively, not a precise effect
estimate.

This is an online conditional forecast, not a round-1 forecast of the whole
experiment: it uses the actual state reached under the first judge and one
pool of scores from the new judge. The remaining branch misses are informative.
For `press_d1` seed 1 and `press_d2` seed 1, the new judge's first agreement is
positive (+0.083 and +0.357), so the refreshed model predicts ascent (endpoints
0.457 and 0.621), but the observed runs end at 0.000 and 0.105 after agreement
changes sign or fluctuates later. A single boundary measurement cannot predict
those reversals. The larger conclusion is therefore specific: reinitialize
the model when the selection policy changes, and remeasure again if its local
agreement is itself unstable.

Holding the first-round mean within-prompt SD fixed scores **0.127** versus
0.431 and gets the direction of all **31/31** large selection-driven
movements. Mean range scores 0.125, but the property analysis below shows that
this numerical difference does not produce meaningfully different rollouts.

## Rollout comparison of spread definitions

Ten candidate definitions were allowed to control the simulated selector and
their own future recurrence. The table gives selection-driven endpoint MAE
when the whole condition is held out. “Geometry” feeds the predicted spread
trajectory back into selection; “frozen” holds first-round spread fixed.

| spread supplied to the selector | geometry | frozen round-1 spread |
|---|---:|---:|
| mean within-prompt population SD | **0.139** | **0.127** |
| mean within-prompt range | 0.132 | 0.125 |
| mean pairwise absolute difference | 0.137 | 0.129 |
| mean within-prompt MAD | 0.141 | 0.129 |
| mean within-prompt variance | 0.141 | 0.128 |
| RMS within-prompt SD | 0.148 | 0.140 |
| fraction of prompts with any difference | 0.150 | 0.140 |
| total SD including between-prompt variation | 0.161 | 0.160 |
| median within-prompt SD | 0.208 | 0.165 |

Binary entropy scores 0.126/0.126, but exists only for the 0/1 risk runs and
therefore is not comparable to definitions evaluated on both axes.

Mean range has the lowest point endpoint MAE in this table.
With geometry its paired improvement over mean SD is 0.007 MAE (bootstrap 95%
CI 0.003–0.011); with the first-round metric frozen its 0.002 improvement is
smaller and the paired interval crosses zero. Define it separately as

`R = (1/J) Σ_j [max_k(x_jk) − min_k(x_jk)]`.

On the binary risk axis, `R` is exactly the fraction of prompts containing
both a 0 and a 1. It measures **rankable support**—how often a prompt offers
the selector any directional choice. Mean SD additionally measures how the
candidates are distributed between the extremes. SD remains the stronger
direct selector-gap scale and has the exact variance decomposition. The later
rollout-property comparison shows that the apparent range advantage is too
small to justify a second headline state.

The tempting LORO winner is misleading. “Fraction of prompts with any
difference” scores 0.120 versus mean SD's 0.130 when another seed from the same
condition is left in training. When the complete condition is held out it
falls to 0.150, while mean SD is 0.139. The coarse support indicator was
regularizing within known conditions, not transporting as a better spread
coordinate.

## Feeding predicted spread back does not improve endpoint prediction

The binary geometry recurrence does predict the spread trajectory: on the
risk runs, mean-SD MAE is **0.081**, versus **0.111** if first-round spread is
held fixed. But feeding that better spread prediction back into the value
rollout makes selection-driven endpoint MAE worse: **0.139** versus **0.127**.
An ordinary spread autoregression lands between them at 0.137.

This is the central result of the simulation. The one-step conversion from
candidate mean into next spread is real, but the current coupled equations do
not turn that improvement into better multi-round value forecasts. Errors in
the other factor—agreement—compound more strongly than the improvement in
spread.

The oracle attribution makes this visible for the mean-SD geometry model:

| LOCO selection-driven simulation | endpoint MAE |
|---|---:|
| fully closed: round-1 agreement + predicted spread | 0.139 |
| simple modeled agreement autoregression | 0.132 |
| observed later spread, round-1 agreement | 0.139 |
| observed later agreement, predicted spread | **0.115** |
| observed later agreement and spread | 0.112 |

Reading future spread barely helps. Reading future agreement removes most of
the remaining selection-driven error and repairs the judge-swap trajectories.
A global agreement autoregression recovers only a small fraction of this.
The scheduled-swap diagnostic above shows that continuous oracle access is not
required for most of those runs: one full state refresh at the boundary lowers
their LOCO endpoint MAE from 0.404 to 0.179 in the frozen mean-SD model.

## The rollouts support one spread definition, with a stochastic layer

Under the same boundary-refresh rule, frozen SD and frozen range predictions
are effectively identical: mean endpoint difference 0.0066, mean per-round
difference 0.0050, the same endpoint class in 66/67 runs, and the same net
direction in 65/67. On the 45 selection-driven plus swap runs, frozen SD gets
36/38 large-movement directions and 19/24 observed rail endpoints. Observed
and predicted endpoint means are 0.541/0.572 and endpoint SDs 0.370/0.360.

The deterministic paths are conditional means, not realistic samples: their
mean total variation is 0.458 versus 0.648 observed and they average 0.16
direction reversals versus 1.20 observed. Adding zero-mean Gaussian value-
update noise with fold-estimated residual scale restores those properties
(variation 0.655; reversals 1.49) without materially changing the mean
forecast. A candidate `ρ_next ~ ρ + ρσ` feedback looked better at endpoints
but fails to improve held-out one-step prediction of next agreement, so it is
rejected as a likely post-hoc compensator rather than added to the model.

## Resulting model

Keep mean within-prompt population SD as the definition of **selectable
spread**. Keep mean variance and the binary decomposition as the explanation
and one-step model for how spread is regenerated. For multi-round prediction,
the best shared simple baseline is:

1. measure value, mean within-prompt SD, agreement, and supplier state in the
   first pool;
2. use `kept − host-generated mean`, not `kept − whole-pool mean`, as the
   training displacement;
3. hold spread at its first-round value when forecasting an unseen
   condition;
4. roll the selection/update equations forward;
5. remeasure the complete state and restart whenever the judge or judging
   format changes; do the same for a supplier/composition change until that
   boundary rule is tested separately.

The geometry recurrence should still be plotted as a predicted spread
trajectory, but it should not be advertised as improving endpoint forecasts
until agreement dynamics are modeled or experimentally controlled. The next
mechanistic target is therefore not another spread definition. It is the
within-run evolution of judge/value agreement.

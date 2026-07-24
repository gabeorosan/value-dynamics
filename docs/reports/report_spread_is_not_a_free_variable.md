# Candidate spread is mostly bookkeeping on the pool mean, not a second state variable

Date: 2026-07-24
Script: `scripts/analysis_angular_selection_geometry.py`
Data: `experiments/spread_util_unified.json` (the committed 340-round table; 280 of
those rounds are binary-scored and carry this analysis)
Output: `experiments/angular_selection_geometry.json`

## Summary

The program presents the selection loop as having two measured state variables:
candidate **spread** (how much the round's candidate answers differ in value) and
judge **agreement** (how well the judge's preferences line up with the value being
tracked). On the binary-scored axes that carry almost all of the program's data,
these two are not independent. **The one-parameter law spread ≈ 0.813·√(q(1−q))
explains 85.9% of the variance in measured spread**, and letting every 0.1-wide bin
of pool mean have its own free mean — a far more flexible fit — raises that only to
between 87.6% and 89.2%, depending on the binning convention. Spread is close to a
deterministic function of where the value currently sits, and the residual carries
essentially no separate signal about what the judge will keep.

This does not overturn the selection model, which still predicts movement well. It
changes what the model's parts mean. The loop's free state is the value and the
judge's agreement with it; spread is a third quantity that follows from the first.
The practical consequence is that in a self-only loop you cannot dial spread
independently at all — the interventions that "restored spread" did so by changing
the pool mean, by adding candidates from an outside source.

A second, negative finding: reparameterizing the loop so that the value moves at a
constant rate per round (the arcsine transform, which is what the binomial spread law
implies) is structurally tidier but **not more accurate**. It ties the current linear
model on every forecast horizon tested.

## Why spread was expected to be free, and why it is not

On a binary-scored axis each candidate's value score is 0 or 1, so the variance of
candidates within one prompt is exactly q(1−q) for that prompt's candidate mean q.
Aggregating over the round's prompts, the law of total variance gives

    within-prompt variance = q(1−q) − between-prompt variance

where q is now the whole pool's mean. This identity holds in the committed table to a
maximum absolute residual of 4.0×10⁻⁵, which confirms the scoring really is binary but
is arithmetic rather than a result.

The empirical question is how much room the second term leaves. If between-prompt
heterogeneity varied a lot round to round, spread would still be free to move at a
fixed pool mean. It does not:

| Pool mean q | Rounds | Mean spread | SD of spread | Binomial ceiling √(q(1−q)) |
|---|---|---|---|---|
| 0.0 | 6 | 0.027 | 0.039 | 0.000 |
| 0.1 | 26 | 0.169 | 0.044 | 0.300 |
| 0.2 | 33 | 0.285 | 0.075 | 0.400 |
| 0.3 | 29 | 0.361 | 0.044 | 0.458 |
| 0.4 | 14 | 0.426 | 0.025 | 0.490 |
| 0.5 | 38 | 0.431 | 0.046 | 0.500 |
| 0.6 | 50 | 0.421 | 0.037 | 0.490 |
| 0.7 | 33 | 0.396 | 0.030 | 0.458 |
| 0.8 | 19 | 0.311 | 0.044 | 0.400 |
| 0.9 | 10 | 0.181 | 0.058 | 0.300 |
| 1.0 | 22 | 0.013 | 0.030 | 0.000 |

The overall standard deviation of spread across the 280 binary rounds is 0.139. Within
a bin of pool mean it is 0.046 to 0.049, depending on the binning convention.

How much variance the pool mean accounts for depends on how flexibly you let it: the
one-parameter law below gives 85.9%; the same law with a free intercept gives 87.5%;
free per-bin means give 87.6% with ten equal-width bins and 89.2% with eleven rounded
bins whose edge bins are half-width. The honest headline is the one-parameter figure,
**85.9%**, because that is the actual model — and the fact that ten or eleven free
parameters buy only another one to three points is itself the point. There is very
little structure left for spread to carry.

Fitting spread against the binomial ceiling through the origin gives

    spread ≈ 0.813 × √(q(1−q))

and this coefficient is stable across every slice: Qwen 0.883, OLMo 0.784, self-only
pools 0.810, base-mixed 0.820, peer-mixed 0.835. The coefficient sits below 1 because
of the between-prompt term, and its stability is the actual empirical content here —
between-prompt heterogeneity is a roughly constant tax rather than a moving part.

## What measuring spread buys

Predicting the realized selection gap (kept-candidate mean minus pool mean) across the
242 binary rounds that have a logged agreement value:

| Predictor of the selection gap | MAE | R² |
|---|---|---|
| agreement × measured spread | 0.0430 | 0.808 |
| agreement × spread inferred from the pool mean | 0.0489 | 0.757 |
| agreement × a constant (spread ignored entirely) | 0.0551 | 0.681 |

Agreement alone already gets 0.681. Knowing where the value sits, and inferring spread
from it, adds 0.076. Actually measuring spread adds a further 0.051. So the measurement
is not worthless, but most of what it contributes is recoverable from a number the loop
already knows.

The part of spread that the pool mean does not explain contributes nothing usable: the
correlation between (agreement × residual spread) and the realized gap is **−0.099**,
near zero and with the wrong sign for a variance term.

## The interventions, re-read

The program's headline intervention result is that restoring spread to a collapsed
candidate pool eroded a value that had been stuck. Under this analysis that is not an
independent manipulation of spread. A pool sitting at a rail has a mean at 0 or 1, and
the identity forces its spread to 0; injecting candidates from an outside model moves
the pool mean off the rail, and spread returns as a consequence. The intervention is
real and the effect is real, but the mechanism is better stated as *changing the pool
mean by changing who supplies candidates*, not as *adding variance*.

This also explains why the self-only arms could not be rescued. Within a self-only
loop there is no way to raise spread at a fixed value, because the two are tied. The
external supplier is the only available lever, which matches the three-way
code-security control verdict recorded in the ledger.

## The arcsine reparameterization: tidier, not better

If spread follows the binomial curve, then the per-round move under the selection rule
is proportional to √(v(1−v)), and the natural coordinate is the angular transform
φ = 2·arcsin(√v), in which the value should advance at a constant rate per round. This
predicts trajectories that are straight lines in φ, rails that are reached in finite
time as natural boundaries at φ = 0 and φ = π, and a closed form for time to fixation.
It also removes the current model's need to clip each step into the 0-to-1 range, which
is an ad-hoc patch over exactly this mis-specification.

It does not forecast better. Scored in value units:

| Task | Linear model | Angular model |
|---|---|---|
| One step ahead (242 rounds) | 0.1094 | 0.1091 |
| Trajectory shape, single constant step per run (74 runs) | 0.1047 | 0.1033 |
| Endpoint from round-1 measurements (67 runs) | 0.2128 | 0.2122 |

All three are ties. A first version of this comparison appeared to favour the angular
model by 16–20% on trajectory shape, but that was an artifact: the linear comparator
was allowed to predict values outside 0-to-1. Clipping it fairly erased the gap. The
angular form's remaining case is structural — one fewer fitted quantity, no clipping
step, and finite-time boundaries — not predictive.

The closed-form time to fixation is directionally right and quantitatively weak: over
the 23 runs that reached within 0.02 of a rail, it gets the direction right in 20, but
its error on *when* averages 5.4 rounds against runs only 4 to 8 rounds long.

## Scope and caveats

- Binary-scored rounds only (280 of 340). The degeneracy is a property of binary
  candidate scoring. It says nothing about continuous value measures.
- The "linear model" in the forecast table is my reconstruction of the program's
  recurrence from round-1 measurements, not the published endpoint model. Its endpoint
  MAE of 0.213 is not comparable to the writeup's 0.118, which uses a different run
  grouping and pool-composition handling. The table's internal comparisons are
  like-for-like; the absolute numbers should not be quoted against the writeup's.
- Agreement is taken as logged. Nothing here re-examines how it is measured.
- 89.2% is a variance-explained figure across pooled rounds, not a within-run claim.

## What this implies for where to go next

The most useful reading is that the current experiments have a degenerate value
geometry. A single binary-scored trait cannot separate "how much variation does the
model produce" from "where does the model currently sit", because for a binary variable
those are the same number. Every result about spread in this program is therefore
partly a result about the measurement.

Two things follow. Continuous or graded value scores would let spread move
independently of the mean, making it a real state variable and giving the model
something to predict that it currently gets for free. And multi-dimensional value
measurement would do more: with several value axes scored on the same candidates, the
selection differential becomes a vector and the variation becomes a covariance matrix,
at which point selection on one axis is predicted to move the others. That is the
natural next question and it is not answerable with any data currently in the repo.

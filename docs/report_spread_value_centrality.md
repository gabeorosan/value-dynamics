# Candidate spread follows bounded pool geometry; “value centrality” is mostly a proxy

*Corrected 2026-07-15. Scorer:
`scripts/analysis_spread_value_centrality.py` →
`experiments/spread_value_centrality.json`. Source:
`experiments/spread_util_unified.json` (340 rounds, 74 runs, OLMo and Qwen,
risk and insecure-code coordinates, self-only/base-mixed/peer-mixed pools).*

## Correction

The first analysis reported that the current model value's centrality,
`value × (1 − value)`, explained 64% of candidate spread in mixed pools. That
number reproduces, but the proposed mechanism does not follow from it.

Candidate spread and candidate-pool mean are calculated from the same 0/1
candidate scores. For a Bernoulli coordinate with mean `p`, the population
standard deviation is `sqrt(p(1 − p))`. The reported spread is the mean of
within-item standard deviations, so `sqrt(pool_mean × (1 − pool_mean))` is an
aggregate ceiling/proxy imposed by the score geometry. The model's pre-round
behavioral value is highly correlated with candidate-pool mean (`r = 0.91`).
Consequently, state centrality inherits much of the candidate pool's geometric
association with spread.

The corrected conclusion is:

> The candidate pool becomes homogeneous on the measured binary axis near an
> aggregate score of 0 or 1. That makes the pool selection-inert on that axis.
> The data do not establish a separate causal law from model-state centrality
> to candidate spread, or stable attractors at model values 0 and 1.

## Reanalysis

Three comparisons separate pooled differences from changes within a run:

1. pooled OLS over all logged rounds;
2. run-fixed-effect OLS after demeaning every variable within run;
3. first differences between consecutive rounds in the same run.

Each comparison tests the old state centrality against two candidate-pool
quantities: `pool_mean × (1 − pool_mean)` and its Bernoulli SD ceiling
`sqrt(pool_mean × (1 − pool_mean))`.

| spread model (R²) | all 340 pooled | all within-run | all Δ round | mixed 96 pooled | mixed within-run | mixed 72 Δ round |
|---|---:|---:|---:|---:|---:|---:|
| model **state** centrality | 0.460 | 0.472 | 0.323 | 0.644 | 0.643 | 0.511 |
| candidate-**pool** centrality | **0.607** | **0.733** | **0.670** | **0.935** | **0.937** | **0.873** |
| candidate-pool SD ceiling | 0.579 | **0.746** | **0.679** | 0.880 | 0.925 | 0.844 |

The mixed-pool result is decisive for interpretation. Replacing the pre-round
model value with the mean of the actual candidate scores raises pooled R² from
0.64 to 0.94. After candidate-pool centrality is included, model-state
centrality adds `0.0001` pooled R², `0.0020` within-run R², and `0.00003`
first-difference R². Using the theoretically shaped SD ceiling instead gives
the same qualitative result: state centrality adds 0.015 pooled, 0.003
within-run, and 0.003 first-difference R².

This is not only an in-sample advantage. Leaving out one entire run at a time
in the mixed pools gives out-of-fold R² 0.60 (MAE 0.079) for state centrality
versus 0.93 (MAE 0.032) for candidate-pool centrality.

The result also survives the less favorable self-only subset. There,
candidate-pool centrality explains 47% pooled, 58% within-run, and 50% of
round-to-round spread changes, versus 38%, 37%, and 20% for state centrality.
The association is stronger on OLMo than Qwen, but the ordering is the same in
both families.

## What source separation contributes

The first report fit mixed-pool spread from state centrality plus the absolute
difference between host and supplier means and obtained R² 0.727. That was
described as a dominant centrality term plus a smaller supplier term. The
corrected accounting reverses the interpretation:

- candidate-pool SD ceiling alone: pooled R² 0.880;
- ceiling + source separation: 0.885;
- ceiling + source separation + state centrality: 0.903.

Within runs, the same sequence is 0.925 → 0.931 → 0.940. In first differences,
ceiling alone is 0.844, adding change in source separation gives 0.851, and
adding change in state centrality gives 0.859. Source composition carries some
additional information, but the candidate pool's bounded geometry is the
load-bearing term; the pre-round state value is not.

This does not make `pool_mean × (1 − pool_mean)` a newly discovered causal
mechanism. It is derived from the same binary candidate scores as spread. Its
role is diagnostic: it shows why the old state-centrality regression cannot
support the mechanism assigned to it.

## Invasion, rescue, and injection after the correction

The observed trajectories remain valid; their interpretation narrows.

- **Invasion:** candidate pools become homogeneous on the measured axis as the
  host and extremist supplier converge. Spread then vanishes. The data do not
  distinguish “the model value caused homogeneity” from the more direct fact
  that the scored candidate pool itself became homogeneous.
- **Rescue:** moving away from a 1.0 endpoint coincides with a candidate pool
  whose mean returns toward the interior and whose binary-score spread rises.
  This contradicts a simple time-decay story, but it does not identify model
  state centrality as the cause.
- **Injection:** the matched self-only/injected pair remains the clean causal
  result. Changing only the answer supplier restores measured-axis variation
  (spread 0.00 → 0.31), after which the oracle can move the value. This supports
  supply of rankable variation, not a general centrality law.

## Why “self-limiting” and “stable resting points” are withdrawn

The old report compared mean absolute drift in a central band (0.155) with an
extreme tail (0.052) and called the difference evidence for self-limiting
dynamics. That comparison is not sufficient:

- a 0–1 outcome is mechanically boundary-censored near 0 and 1;
- the selection pull is smaller when the candidate pool is homogeneous;
- pooled rounds repeat the same run and condition;
- a zero-spread state was already shown to move when an outside supplier
  restored variation.

Across all rounds, state centrality alone explains only 8% of variation in
`|drift|`; the directly measured absolute selection pull explains 46%. Adding
state centrality after pull raises R² to 49%, a descriptive increment that can
still include boundary and regime effects. In mixed pools, absolute pull
explains 71% versus 20% for state centrality.

The supported language is therefore the one already established by the oracle
and injection controls: **a pool with no rankable variation is selection-inert
on the measured axis under that generator and judging rule.** It is not a
general fixed point. An outside source can reopen the intervention window.

## Claim status

- **Retracted:** “spread is a function of model-state centrality”; “centrality
  is the dominant term”; “the loop is self-limiting”; “0/1 are stable resting
  points because the loop's own fuel vanishes.”
- **Stands descriptively:** state centrality correlates with spread; rescue
  falsifies a universal round-number decay; candidate-pool mean and spread
  co-move strongly.
- **Stands causally within tested scope:** supplier injection can restore
  measured-axis candidate variation and thereby restore selection-driven
  movement.

No held-out experiment was added for this correction. Leave-one-run-out fits
test transport across existing runs, not a new intervention. The analysis is
an audit of what the logged 0/1 candidate-score geometry can and cannot imply.

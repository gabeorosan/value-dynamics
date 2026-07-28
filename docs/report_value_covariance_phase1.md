# Value covariance, phase 1: the measurement does not survive its own instrument check

> **CORRECTED 2026-07-25, same day, after independent adversarial re-derivation. Read
> this box before the body — the conclusion holds but the stated cause was wrong, and
> the one affirmative claim below is withdrawn.**
>
> **SECOND PASS 2026-07-28 — see the addendum at the end of this file before citing
> anything in this box.** The 0.167 null floor of item 5 is now a committed simulation
> and stands (`scripts/sim_winrate_null_floor.py`), but the floor `script.py` actually
> implements is 0.115 and would have certified this run; item 7's "over-predicts
> spillover by 1.8x" is **WITHDRAWN** (errors-in-variables plus event clustering); and
> the cross-method cross-pool test the design calls primary was never run — it has
> now been run, and is uninformative.
>
> 1. **The halo is not a single-judge artifact.** Judge B, a different family,
>    reproduces the structure: all off-diagonals positive, risk x caution **+0.499**,
>    PC1 share **0.466** against judge A's 0.470. The cross-method estimate — the very
>    design built to kill the halo, which the body below uses only for its diagonal —
>    gives risk x caution **+0.236 raw, +0.601 disattenuated**. The association
>    survives the halo-killing design, so attributing it to one judge is wrong.
> 2. **"Swamps" overstates it.** PC1 is 47% (CI 0.413–0.540) with PC2 above Kaiser; a
>    true single-factor halo is 70–90%. Removing PC1 does **not** recover semantics —
>    13 of 15 residuals go negative and risk x caution lands at the median of them.
>    The residual does replicate across independent pools at r = 0.716.
> 3. **The axes are not opposites, and my own candidates show it.** Essay
>    thoroughness moves both: the top risk-scored candidate scores risk 0.899 **and**
>    caution 0.867, and both extremes advise against the risky option. The claim below
>    that "no plausible property of the answers makes those move together" is refuted.
> 4. **WITHDRAWN — the affirmative claim.** "Candidate pools carry substantial value
>    variation" is false. At the observed 0.609 order-flip rate, a pool of *identical*
>    candidates produces a null within-prompt SD of **0.167**; every observed SD
>    (0.109–0.167) sits at or below it. The win-rate spread is manufactured by the
>    design.
> 5. **The gate is defective.** `min_within_prompt_sd >= 0.05` tests against a zero
>    floor when this design's own null floor is ~0.17. It will mislead any future run
>    using the win-rate construction, and must be recalibrated against a
>    shuffled-label null.
> 6. **The threshold call was over-precise.** Prompt-clustered bootstrap: risk
>    r = 0.395, CI [0.168, 0.566], P(r < 0.4) = 0.518 — a coin flip. Only
>    scope_expansion is solidly below 0.4.
> 7. **The cross-pool test was over-dismissed.** Removing selected-axis block means
>    raises predicted-vs-observed to r = 0.724, which a pure level effect cannot
>    produce, and the slope of 0.545 means the covariance over-predicts spillover by
>    1.8x — a real finding this report omitted.
> 8. **`residualize_on_length` is mis-specified** — it centres length globally while
>    the covariance centres within prompt, attenuating the coefficient ~4.5x. The
>    conclusion survives correction (risk x caution 0.5528 → 0.5562) but the test as
>    run was broken.
>
> **The defensible headline is narrower and better than the one below:** forced-choice
> rubric judging over a candidate pool with no real value spread manufactures win-rate
> variance indistinguishable from noise, and the gate cannot detect this because it was
> calibrated against the wrong null. That indicts the **generator and the gate**, not
> only the judge — which changes what to build next.

Date: 2026-07-25
Kernel: `hirokenzan/vd-valcov-20260725-0949` (COMPLETE, both judges)
Script: `experiments/value_covariance/script.py`
Output: `experiments/value_covariance/output/value_covariance_phase1.json`

## Verdict first

**The primary estimate fails the instrument check that was declared before the run,
so no covariance from this run is citable.** Two judges from different families
scoring the *same* value axis on the *same* answers agree at only 0.345 to 0.467, and
on one axis they do not agree at all. The pre-declared threshold was 0.4.

| Axis | Agreement between the two judges, same axis |
|---|---|
| Deference to the asker | +0.467 |
| Directness | +0.457 |
| Risk tolerance | +0.395 |
| Caution and reversibility | +0.390 |
| Candour about uncertainty | +0.345 |
| Scope expansion | **−0.053** |

Four of six sit at or below the threshold and scope expansion is indistinguishable
from zero: the two judges have no shared notion of what it means. A covariance
*between* axes cannot be trusted when the axes themselves are not reliably measured.

## What worked

The pipeline itself now runs end to end, and one judge does discriminate. Judge A
(Qwen3-4B) produces within-prompt standard deviations of 0.109 to 0.168 across the six
axes with scores spanning essentially the full 0-to-1 range, against 0.0068 before the
thinking-block fix. Candidate pools carry real value variation, which the earlier
runs could not see.

Judge B (Gemma-2-2B) does not. Its within-prompt SD is 0.041 to 0.066, failing the
0.05 discrimination gate on five of six axes. It is too small for this task, so the
cross-method estimate the design depends on rests on one adequate judge and one
inadequate one.

## Why the headline numbers should not be believed

**The correlation matrix is all-positive, including between opposites.** Judge A on
pool A:

| | risk | candour | deference | caution | directness | scope |
|---|---|---|---|---|---|---|
| **risk tolerance** | 1.000 | 0.169 | 0.583 | 0.553 | 0.547 | 0.320 |
| **candour** | 0.169 | 1.000 | 0.102 | 0.321 | 0.107 | 0.396 |
| **deference** | 0.583 | 0.102 | 1.000 | 0.440 | 0.486 | 0.247 |
| **caution** | 0.553 | 0.321 | 0.440 | 1.000 | 0.408 | 0.306 |
| **directness** | 0.547 | 0.107 | 0.486 | 0.408 | 1.000 | 0.257 |
| **scope expansion** | 0.320 | 0.396 | 0.247 | 0.306 | 0.257 | 1.000 |

Every off-diagonal entry is positive. Most damning, **risk tolerance correlates +0.553
with caution and reversibility** — two axes written as near-opposites ("favours the
higher-variance option" against "recommends a safeguard, a check, or a way to undo the
decision"). No plausible property of the answers makes those move together. This is
the common-method halo the design audit predicted for six axes scored by one judge
reading one answer.

**It is not a length artifact.** Residualising every axis on answer length changes the
matrix in the third decimal place (0.583 to 0.583; 0.553 to 0.553). Length was the
known confounder in this project and it is not the culprit here, which means the
proposed length control was aimed at the wrong thing.

**The judge is largely position-driven on realistic candidates.** Judge A's mean
presentation-order gap is **0.609** — the two orders of the same comparison disagree
by 0.61 on average, where 0 is order-robust and about 0.96 is pure position bias. The
manipulation check on hand-written, strongly contrasting answers gave 0.006. So order
robustness is *contingent on signal strength*: when the answers differ unmistakably
the judge reads the content, and when they are close it falls back on position.
Averaging both orders removes the bias in expectation, which is why the axis means sit
at 0.5, but it means a large share of each comparison is noise rather than judgment.

**The cross-pool test's apparent success is what a halo produces.** Predicting pool
B's selection differentials from pool A's covariance gives correlation 0.634 for judge
A and 0.794 for judge B, with **sign agreement 1.000** in both. Perfect sign agreement
across all 30 axis pairs is not a strength here: when every off-diagonal is positive,
"selecting on one axis raises the others" is correct by construction. The test cannot
distinguish a real correlated response from a general quality factor.

## What this run does establish

- The pipeline, the gate, and the cross-pool machinery all work and are reusable.
- Candidate pools from an instruction-tuned model at temperature 1.0 **do** carry
  substantial value variation, contradicting the reading the broken-judge runs
  suggested.
- A 4-billion-parameter LLM judge scoring abstract value rubrics from free text
  produces a dominant general factor that swamps the between-axis structure the
  experiment exists to measure. That is a real and useful negative result about the
  method.
- Order robustness must be measured on the *actual* candidates, not on constructed
  contrasts. A manipulation check on clear cases certifies the judge for clear cases
  only, and this run shows the gap is a hundred-fold.

## What would have to change

Ranked by how much of the problem they address.

1. **Stop scoring abstract axes with a free-text LLM judge.** This project's own
   instrument calibration already records that programmatic readouts are trustworthy
   while free-text judge readouts vary by family. The axes that worked historically
   were programmatically parsed commitments, not rubric judgments. Value covariance
   probably needs prompts where each axis has a mechanical readout.
2. **Use scenarios that force a discrete commitment per axis**, so a candidate's
   position is extracted rather than adjudicated, and the halo has nothing to attach
   to.
3. If an LLM judge is unavoidable, **score one axis per judge context with no
   awareness of the others**, and measure the general factor explicitly — extract the
   first principal component and report the residual covariance after removing it.
4. A judge materially stronger than 4B, which free-tier compute does not supply.

## Scope

30 prompts, 8 candidates each, two independent pool sets, six axes, three opponents
per candidate in both presentation orders. Qwen3-4B as generator and judge A,
Gemma-2-2B as judge B. All scores are win rates from forced-choice comparisons read
from token logprobs with the thinking block closed. Nothing here was trained; this is
a measurement of generated candidates only.

---

## Addendum, 2026-07-28 — the null floor is now a committed simulation, and one correction is withdrawn

Scheduled monitoring re-pulled this kernel's output and re-derived it from raw
scores. The arithmetic reproduces exactly (same-judge cross-pool slopes 0.5454
and 0.7660, correlations 0.6339 and 0.7942, and the full cross-method matrix, all
to within 5e-3). Four things change.

Scripts: [scripts/sim_winrate_null_floor.py](../scripts/sim_winrate_null_floor.py)
→ `experiments/winrate_null_floor.json`, and
[scripts/analyze_value_covariance_phase1.py](../scripts/analyze_value_covariance_phase1.py)
→ `experiments/value_covariance_phase1_analysis.json`.

### 1. The 0.167 null floor was right; the floor `script.py` actually implements is not

Correction 5 above stated the identical-pool null SD as 0.167 "by simulation", but
no simulation was ever committed — it was a chat-only number, and the repo has
since carried two incompatible floors. `script.py` implements
`order_gap * 0.5 / sqrt(n_candidates - 1)` = **0.115**, which passes five of six
judge-A axes, while the comment immediately above that line asserts ~0.167, which
fails all six. The formula is wrong twice over: it divides by
`sqrt(n_candidates - 1)` = sqrt(7) though each candidate has `2 * n_opponents` = 6
reads, and it scales linearly by the order gap instead of inverting the gap to get
the judge's per-call response spread.

`sim_winrate_null_floor.py` now simulates `score_pool`'s exact accounting under a
judge whose read does not depend on which candidate is in which slot, calibrated to
reproduce the observed order gap. For judge A the null within-prompt SD is
**0.161**, with a 95% interval for the mean over 30 prompts of **[0.147, 0.177]**.
The 0.167 figure stands.

Note also that a *literally* identical pool is the wrong null and cannot produce
this: identical candidate strings make every comparison prompt identical, a
deterministic logprob read returns one constant, and every candidate scores exactly
0.5 with zero spread. The floor is about a value-blind judge, not identical text.

**Two small corrections to correction 5's wording, in opposite directions.** Strictly,
not "every" observed SD sits at or below the null: risk_tolerance (0.167) and
deference_to_asker (0.162) are marginally *above* the point floor of 0.161. But
neither clears the null's own 30-prompt sampling interval — the highest observed
axis SD, 0.167, is below the null's p95 of **0.176**. So **no judge-A axis is
distinguishable from a value-blind judge**, which is the stronger statement and the
one that should be cited.

Judge B: null floor 0.076–0.088 across response families, against observed SDs of
0.041–0.066. All six axes below. Its failure is confirmed and is not marginal.

**A separate finding falls out of the calibration.** Judge A's order gap of 0.609
is *unreachable* by any non-saturating response family — both the soft-lean and the
symmetric-Beta families top out near 0.50, because a gap above 0.5 requires the two
presentation orders to disagree more often than a coin. Only saturated 0/1 reads
reach it, at a fitted first-position pick rate of **0.742**. Judge A is not a noisy
judge of value; it is a confident judge of position.

### 2. The cross-pool test's 30 pairs are 6 selection events

Each selected axis produces one ranking, one on-axis differential and one set of
judge errors, then contributes 5 rows — one per off-target axis. Those 5 rows are
not independent. Bootstrapping whole selection events (5000 draws) gives judge A a
slope 95% CI of **[0.35, 1.03]** and correlation CI **[0.48, 0.81]**. The slope
interval includes 1.0.

Resampling *prompts* instead (1000 draws, re-estimating the covariance and the
differentials each time) gives slope CI **[0.25, 0.75]**. The two clusterings answer
different questions — generalising to new prompts over these six axes, versus
generalising to new axes — and only the second bears on the claim below.

### 3. WITHDRAWN — "the slope of 0.545 means the covariance over-predicts spillover by 1.8x"

Correction 7 above called this "an unreported real finding". It does not survive two
checks.

**Errors-in-variables.** The predictor is itself an estimate — a covariance measured
on 30 prompts of pool A — so OLS is attenuated toward zero by
`lambda = var(true predictor) / var(measured predictor)`. The prompt bootstrap gives
the estimation-error variance directly: judge A `lambda` = **0.780**, judge B
**0.618**. Correcting for it moves judge A's slope from 0.545 to **0.699** and judge
B's from 0.766 to **1.239** — the two judges land on *opposite sides* of 1.0.

**Clustering.** The event-cluster CI of [0.35, 1.03] already includes 1.0 before any
attenuation correction.

A quantity whose two independent measurements straddle 1.0, whose interval includes
1.0, and 22% of whose apparent shortfall is predictor noise, is not a finding about
over-prediction. It is withdrawn. What remains true from correction 7 is only the
narrower part: predicted-vs-observed correlation survives removal of the
selected-axis block means, so the relationship is not purely a level effect.

### 4. The cross-method test the design designates as primary was never run

SPEC design note 3 and the external audit's finding 2 both require the primary
covariance to be **cross-method** — selected axis from judge A, off-target axes from
judge B — with the same-judge matrix demoted to a sensitivity analysis. The kernel
emitted a cross-method *correlation* matrix on pool A but used same-judge covariance
for every cross-pool prediction, so the primary test as specified has no result. The
ledger row notes the design was "built specifically to kill the halo, then failed to
use"; this is the same gap, on the cross-pool side.

Running it now (selection ranked by judge A, spillover read by judge B, no shared
judge error) gives slope **4.34**, correlation **0.560**, sign agreement **0.70**,
with event-cluster CIs of **[0.18, 8.08]** for the slope and **[0.02, 0.84]** for the
correlation. It is uninformative, which is the expected outcome when one of the two
methods has failed its own gate. It is recorded so that no future session mistakes
the missing primary test for an unrun opportunity.

### What this changes for the next run

The gate in `script.py` must be replaced before any rerun, not merely re-read: as
implemented it is *more* permissive than the zero-floor version it was meant to fix
is generous, and it would have certified this run. Replace the analytic expression
with the simulated floor, and persist per-comparison probabilities so a shuffled-label
permutation null can be computed from the run's own data rather than from a
calibrated model of it.

The deeper implication is unchanged from the corrected headline: with a judge that
picks the first answer 74% of the time and reads saturated, the design measures
position, and no amount of order-averaging recovers value — averaging removes the
bias in expectation while leaving the variance, which is exactly the manufactured
spread the gate was supposed to catch.

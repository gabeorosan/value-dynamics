# Value covariance, phase 1: the measurement does not survive its own instrument check

> **CORRECTED 2026-07-25, same day, after independent adversarial re-derivation. Read
> this box before the body — the conclusion holds but the stated cause was wrong, and
> the one affirmative claim below is withdrawn.**
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

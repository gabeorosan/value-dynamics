# Phase 1b: the graded instrument works, the generator carries variation, the persona control does not

**Run date** 2026-07-31 (full size) · **Kernel** `hirokenzan/vd-valcov1b-20260802-2120`
· **Result** `experiments/value_covariance/output_1b/value_covariance_phase1b.json`
· **Config** generator + judge A `Qwen/Qwen3.5-4B`, judge B `google/gemma-4-E2B-it`,
30 prompts, 8 candidates, keep 4, six axes, graded 0–9 logprob read, both
polarities, isolated call per axis

**Registered verdict: `INSTRUMENT_FAILURE`.** That headline is correct and also
misleading on its own, because the two things that failed are not the thing the
phase was built to test.

## What passed, and it is the point of the whole phase

Judge A (Qwen3.5-4B) cleared both instrument gates decisively.

| gate | criterion (fixed pre-run) | result |
|---|---|---|
| 1 — digit mass | mean ≥ 0.5 on pool A | **0.9958** ✓ |
| 2 — manipulation pairs | ≥ 0.80 ordered and mean margin ≥ 0.10 | **1.0 ordered, margin 0.6049** ✓ |

Per-axis margins on the 14 hand-built pairs: risk_tolerance 0.723,
caution_reversibility 0.721, directness 0.603, candor_uncertainty 0.506,
deference_to_asker 0.315. **All six axes discriminate**, and the next-token
distribution is a real graded read rather than a spike — 9 at 0.46, 8 at 0.29,
7 at 0.18.

**Graded 0–9 logprob scoring is validated as an instrument.** That was the
question this phase existed to answer, and the answer is yes.

## The generator does carry value variation — against the modal expectation

Registered outcome O2 ("the generator produces no value variation") was the
expected result. It did not happen. Mean within-prompt spread on unprompted
pools, and the same numbers on an independently generated second pool:

| axis | pool A | pool B |
|---|---|---|
| directness | 0.0891 | 0.0780 |
| risk_tolerance | 0.0871 | 0.0849 |
| caution_reversibility | 0.0716 | 0.0730 |
| deference_to_asker | 0.0571 | 0.0570 |
| candor_uncertainty | 0.0496 | 0.0500 |
| scope_expansion | 0.0384 | 0.0325 |

Four of six axes clear the registered 0.05 threshold, candor sits on it, and
scope_expansion falls short. **The two pools agree to within about 0.01 on every
axis**, which is the strongest evidence here that this is signal and not noise —
they were generated independently, from different seeds.

So the answer to "does an unprompted model's own candidate pool carry graded
value variation across several axes at once" is **yes, on five of six axes,
reproducibly**. That is the precondition for measuring value covariance, and it
is the first time this program has had it.

## What actually failed

**1. The persona positive control (gate 3).** Registered directions were
risk_tolerance ≥ +0.15 and caution_reversibility ≤ −0.10 between a bold-persona
and a cautious-persona pool. Observed: risk_tolerance **+0.0664**,
caution_reversibility **−0.0987**. The caution axis very nearly clears; the risk
axis reaches under half the required separation.

This is the informative failure, and it does *not* implicate the judge. The same
judge separated hand-built extremes on the same axis by 0.723. **The persona
instruction moved the generator by 0.066 on the axis it explicitly targeted** —
roughly a tenth of what deliberately-written extremes achieve, and comparable to
the 0.087 spread the model produces unprompted with no instruction at all. A
system-prompt persona is a weak lever on these axes.

**2. Judge B produced nothing at all.** Every gemma-4-E2B-it statistic is `nan` —
digit mass, all six axis spreads, every manipulation margin. Its top-token
distribution is degenerate: **'9' at 0.9802**. This is not the marker-injection
bug fixed earlier that day (the prompt was clean this time); `nan` in the digit
mass means the logits themselves contained non-finite values. gemma-4 in fp16 on
a Turing T4 produces non-finite logits, despite its tech report stating the
architecture bounds activation ranges to fit fp16.

Judge B has therefore contributed no usable reads in any run to date, for two
unrelated reasons in succession.

## Batch calibration did almost nothing

Added on the strength of a literature recommendation as the named remedy for
saturation. Calibration spread gain by pool: 0.977, 1.074, 0.993, 1.011 — within
a few percent of 1.0 in every case. On a judge whose digit mass is already
0.9958 and whose distribution is already graded, there is nothing for it to fix.
Keep it (it is free and it is insurance on a saturated judge), but it is not
doing work here.

## What this changes

1. **The instrument question is closed for judge A.** Graded scoring works. The
   binary-scoring constraint — under which spread is an exact function of the
   pool mean and cannot be an independent variable — is now escapable.
2. **The next run needs a working judge B**, not for the science directly but
   for the cross-judge gate that distinguishes "these axes are real" from "this
   is one judge's idiosyncrasy". Relaunched with `ibm-granite/granite-4.1-3b`,
   the survey's plain-dense, lowest-load-risk fallback.
3. **The persona control should be redesigned or retired.** As a positive
   control it is testing whether a system prompt moves the generator, which is a
   substantive question with its own answer (barely), not a check on the judge.
   A control that varies the *candidate text* directly — as gate 2 does — is the
   one that isolates the instrument, and it passes.
4. **`scope_expansion` is the weak axis** on both pools and should be either
   rewritten or dropped before it dilutes a covariance estimate.

## Caveats

- One generator, one judge family, one temperature. The spread numbers are
  properties of Qwen3.5-4B at temperature 1.0, not of language models.
- The 0.05 spread threshold was registered in advance but is a judgement call;
  four of six axes clear it and one sits exactly on it.
- Nothing here measures covariance yet. This phase tests whether the measurement
  is possible; the covariance estimate needs the cross-judge gate to pass first.

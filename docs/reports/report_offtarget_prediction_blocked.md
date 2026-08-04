# Off-target selection differentials are predictable from the candidate covariance

**Analysis date** 2026-08-04 · **Script**
`scripts/analysis_offtarget_prediction_blocked.py` · **Result**
`experiments/offtarget_prediction_blocked.json` · **Data**
`experiments/value_covariance/output_1b_granite/value_covariance_phase1b.json`
(Qwen3.5-4B generator and judge A, granite-4.1-3b judge B, 30 prompts × 8
candidates × 6 axes, graded 0–9)

## The claim under test

Selecting the top-K candidates on axis `a` moves axis `b` as well, purely
because candidate scores on the two axes are correlated within a prompt.
Multivariate selection theory makes that quantitative: with `P` the within-prompt
covariance of candidate scores and `S` the vector of selection differentials,

    S_b  =  (P_ab / P_aa) · S_a

If that holds, **off-target movement through the selection channel is
predictable from a pure inference pass over the candidate pool, before any
training happens.** Whatever training adds on top is the Price equation's
transmission term, which this does not measure.

## Why the phase-1b number needed redoing

Phase 1b reported slope 0.855, correlation 0.852 over 30 predicted-versus-observed
pairs — and its own output carried the caveat that matters: those 30 pairs
cluster into **6 selection events**, one per selected axis. A slope on six
clusters with no interval is not a result yet.

Blocking fixes that with no new compute. The 30 prompts split into 5 disjoint
blocks of 6; the whole prediction is redone inside each block, so
(block, selected axis) is a genuine selection event and the count goes from 6 to
**30**, with a cluster bootstrap over those events.

Three separations are preserved throughout, and they are what make this a test
rather than an identity:

- **cross-pool** — `P` is estimated on pool A; selection and the observed
  differential happen on pool B.
- **cross-method** — `P` and the selection use judge A; the observed off-target
  differential is measured by **judge B**, a different model family. A shared
  judge error cannot inflate the agreement.
- **off-diagonal only** — `b ≠ a`. The on-axis differential is the input.

## Result

| | slope | correlation | MAE | sign agreement | effective n |
|---|---|---|---|---|---|
| whole sample | 1.056 | 0.775 | 0.0074 | 0.90 | **6** |
| **blocked** | **0.684** [0.442, 0.959] | **0.427** [0.292, 0.550] | 0.0182 | 0.66 [0.587, 0.727] | **30** |

**The prediction is real and substantially weaker than the whole-sample fit
suggested.** The slope interval excludes zero comfortably; correlation drops from
0.775 to 0.427 and sign agreement from 0.90 to 0.66 once each estimate is made
on 6 prompts instead of 30.

That drop is not evidence against the theory — it is the expected cost of
estimating `P` from a small block. Noise in the predictor attenuates the slope
toward zero, which is why the well-estimated whole-sample slope sits near 1
(1.056) and the block-estimated one at 0.684. The honest statement is that the
relationship holds with a slope consistent with 1 when the covariance is
measured well, and that **per-block predictive accuracy is modest: r ≈ 0.43.**

By selected axis, pooled across blocks:

| selected axis | slope | correlation | sign agreement |
|---|---|---|---|
| risk_tolerance | +0.990 | +0.644 | 0.80 |
| caution_reversibility | +0.811 | +0.561 | 0.64 |
| scope_expansion | +0.586 | +0.402 | 0.60 |
| candor_uncertainty | +0.570 | +0.447 | 0.60 |
| deference_to_asker | +0.506 | +0.314 | 0.72 |
| directness | +0.355 | +0.151 | 0.60 |

Risk tolerance — the axis with the most candidate spread (0.087) — predicts
best. Directness, despite comparable spread (0.089), predicts worst, so spread
alone does not determine predictability.

## One discrepancy, stated rather than hidden

The phase-1b script's own whole-sample numbers are slope 0.855, r 0.852; this
script's independent reimplementation of the same whole-sample quantity gives
1.056 and 0.775. Both use the same data. The difference is in construction
details of the selection and differential steps that I did not attempt to
reconcile, because the blocked estimate is the one being reported and it is
computed entirely within this script. **Neither whole-sample number should be
cited**; they differ by more than rounding, and their shared limitation is the
effective n of 6.

## What this does and does not establish

- **Does**: the selection-mediated component of off-target movement is
  quantitatively predictable from candidate covariance, across pools and across
  judge families, at 30 selection events.
- **Does not**: say anything about the transmission channel. No training happens
  anywhere in this analysis. The comparison that would separate the two is the
  same prediction run against the *post-training* change on held-out prompts,
  which needs a selection loop with graded scoring — the next experiment.
- **Does not**: generalise beyond one generator, one temperature, six axes, and
  candidate pools of 8.

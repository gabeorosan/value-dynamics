# The first off-target transmission column: what moves, and through which channel

**Analysis date** 2026-07-28 · **Script**
`scripts/analysis_offtarget_transmission_column.py` · **Result**
`experiments/offtarget_transmission_column.json` · **Data**
`experiments/spread_util_unified.json` joined to `experiments/ev_bias_coupling.json`
and `experiments/selfreport_calibration_k2.json` — up to 280 rounds from 59 runs,
all with a risk-preference axis under selection. Each off-target axis has its own
sample: belief bias 280 / 59, numeric estimate 247 / 57, stated tolerance 200 / 39
and OLMo-only

## The question, and why the channel matters more than the coefficient

The Price equation splits a change in a population mean into a selection term
and a transmission term. This project has characterised selection on the axis
being selected. What happens to axes nobody selected on is the second term, and
the 2026-07-28 literature sweep established that no published trait-by-trait
transmission matrix exists for any language model — the nearest neighbour,
subliminal learning ([arXiv 2507.14805](https://arxiv.org/abs/2507.14805)),
reports only the diagonal.

Knowing *that* an off-target axis moves is the easy half. The useful question is
which channel carries it, because the two have completely different
consequences:

- **Selection-mediated spillover.** The judge kept answers that happened to be
  high on axis B as well. This is predictable from a pure inference pass over
  the candidate pool, before any training happens, and it can be engineered
  away by scoring candidates on B and correcting.
- **Transmission-mediated spillover.** The model moved on A, and B came along
  through the weights. No amount of candidate scoring predicts it. This is the
  Price equation's second term, and it is the channel emergent misalignment
  lives in.

## The identifying idea

Per round the pull on the selected axis decomposes into two additive pieces that
are only weakly correlated in the fitted panel (**r = 0.103** over its 280
risk-axis rounds — an earlier draft quoted 0.16, which is neither this figure nor
the all-records figure of 0.152):

    pull  =  supply  +  gap
             (pool_mean − v)   (kept_mean − pool_mean)

`supply` moves the selected axis *without any selection at all* — the candidate
pool simply is not centred on the organism's current value. `gap` is the
selection differential. Both move axis A. They imply different things for axis B.

Fitting `Δz_B = α + a·gap + b·supply`:

- **a ≫ b** means the selector is dragging B → selection-mediated.
- **a ≈ b** means B follows the model wherever it goes, regardless of what moved
  it → transmission-mediated.

## The bias that had to be removed first, because it points the wrong way

The gap is computed from candidate scores observed exactly given the pool, so it
carries no measurement error. Supply contains `v_t`, which does — and in this
corpus **measurement noise is about 50% of the observed supply variance**.
Attenuation therefore pushes `b` toward zero while leaving `a` untouched, which
manufactures `a > b` out of nothing.

This is not a hypothetical. The naive fit on the pooled sample gives gap
**+0.141** [0.089, 0.222] against supply **+0.069** [0.021, 0.117], a difference
of +0.072 [0.004, 0.170] whose interval excludes zero — a clean-looking
"selection dominates" result that is an artefact of the asymmetry.

Correcting it means subtracting `var(e)` from the supply-supply entry of the
moment matrix, with `var(e)` taken from each round's own recorded measurement
standard error. The cross-moment with the outcome is *not* corrected, because
the off-target probe does not share that error — which is what distinguishes
this from the on-target case, where both sides contain `v_t`.

## Results

Corrected coefficients, run-clustered bootstrap intervals on the difference. All
rows come from runs where the *risk* axis was under selection.

### Pooled

Each axis has its own sample, so the row counts differ. **Stated risk tolerance
exists only on OLMo, so its pooled row and its OLMo row are the same data.**

| off-target axis | rounds / runs | gap coefficient | supply coefficient | gap − supply | verdict |
|---|---|---|---|---|---|
| EV belief bias | 280 / 59 | **+0.134** | **+0.141** | −0.007 [−0.150, +0.117] | same channel |
| stated risk tolerance | 200 / 39 (OLMo only) | **+0.032** | **+0.036** | −0.004 [−0.042, +0.030] | same channel |
| EV numeric estimate | 247 / 57 | −0.023 | +0.003 | −0.026 [−0.166, +0.023] | barely moves |

### OLMo alone (216 rounds, 43 runs — the arm carrying the evidence)

| off-target axis | gap | supply | gap − supply |
|---|---|---|---|
| EV belief bias | +0.138 | +0.151 | −0.013 [−0.172, +0.127] |
| stated risk tolerance | +0.032 | +0.036 | −0.004 [−0.042, +0.030] |
| EV numeric estimate | −0.003 | −0.016 | +0.012 [+0.002, +0.031] |

Qwen has 64 rounds and a noise share of 0.80 of supply variance, which makes the
correction large and unstable — its intervals run from −1.6 to +1.8 and it
establishes nothing. OLMo carries this result.

## What it says

**Off-target movement in this corpus is transmission-mediated, not
selection-mediated.** For the axis that actually moves — EV belief bias — the
two channels are indistinguishable, with a difference of −0.013 and an interval
covering zero comfortably. Belief bias follows preference wherever preference
goes, whether the preference was moved by the judge's taste or by a pool that
happened to sit somewhere else. Scoring candidates on belief bias would not have
predicted it.

**Three axes, three behaviours — so this column is not rank-1.** EV belief bias
moves at +0.134 per unit pull. Stated risk tolerance moves at +0.032. The
numeric EV estimate barely moves — −0.31 of its own round-change standard
deviation per unit gap, against +2.64 for belief bias. Asked as a comparison,
beliefs bend with preference; asked as a number, they very nearly do not — the
same underlying quantity, insulated by the question format. That is a structured column, not a single
general factor, and it is evidence against the rank-1 prediction that "narrow
misalignment is hard" ([arXiv 2602.07852](https://arxiv.org/abs/2602.07852))
would make. One column is not a matrix, so this is a first data point rather
than a refutation.

**A standing claim needs a scale qualifier.** Stated risk tolerance has been
described in this repo as near-immobile, and in raw units it is: +0.032 against
+0.134 for belief bias. But its round-to-round standard deviation is only
0.0129, and measured in its own standard deviations it moves **+2.65 per unit
gap, against +2.58 for belief bias**. It is not inert; it has a small dynamic
range. Whether "immobile" is right depends entirely on which scale the question
is asked in, and previous statements did not say.

## What this is not

- **Not causal.** The gap is not randomised in these runs. The channel
  comparison contrasts two components of the same observational variation, which
  is more robust than a raw correlation, but a confounder correlated with the
  gap and not with supply would break it. The randomised round-1 instrument
  exists in a different corpus and does not carry these off-target probes; the
  causal version needs off-target readouts added to an instrumented run.
- **Not a matrix.** One selected axis, three off-target axes, one organism
  family carrying the evidence.
- **"Does not move" is too strong for the numeric estimate.** Its naive
  selection-differential interval is [−0.090, −0.001], which does clear zero. The
  defensible statement is the standardised one: it moves −0.31 of its own
  round-to-round SD per unit gap, against +2.64 for belief bias.
- **Not a strong claim about the numeric estimate's channel split.** The OLMo numeric-estimate
  cell is the one difference whose interval excludes zero, at +0.012 [+0.002,
  +0.031], with both coefficients negligible (−0.003 and −0.016). It is one of
  nine comparisons and should be read as multiplicity until it replicates.
- **Reduced-form fit is weak.** Regressing off-target change on on-target drift
  alone explains 15% of the variance for belief bias and 12% for stated
  tolerance. Most off-target movement is unexplained by anything measured here.

## Join validation

The off-target files key runs by (grid, cond, seed) and store the on-target
trajectory alongside each off-target trajectory. Rows were matched on (organism,
cond, seed, round) and then *checked* by requiring the stored on-target value to
agree with the unified corpus to within 0.02. **All 280 attempted rows joined
with zero value mismatches**, no short series, and no duplicate-source
collisions. A silent misalignment would have shown up as a low match rate.

## What to do next

1. Add off-target probes to an instrumented run. The randomised round-1 arm
   assignment gives a causal handle; nothing currently pairs it with off-target
   readouts, and that pairing is the first causal off-target column anywhere.
2. Score banked candidates on the off-target axes. That would give the
   pool-mediated prediction `S_B = (P_AB / P_AA)·S_A` directly, rather than
   inferring the channel from the supply-versus-gap contrast.
3. Fix the measurement-noise share. At 50% of supply variance, the correction is
   doing heavy lifting, and every conclusion here depends on `var(e)` being
   right. More probe items per readout buys more than more runs.

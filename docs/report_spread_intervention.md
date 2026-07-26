# Spread intervention: selection worked, transmission did not follow

> **NARROWED 2026-07-25 by the oracle positive control (report_oracle_positive_control.md).**
> "Transmission did not follow" holds only for **the gap size a weak base judge
> produces, measured with a 36-read probe (SE 0.109)**. Under oracle selection and a
> 144-read probe (SE 0.054), transmission follows strongly and monotonically: the
> spread arm moves +0.438 and +0.375 against a random control at +0.028. This run was
> UNDERPOWERED, not negative. The same control also confirms this experiment's own
> hypothesis: at a matched pool mean the spread arm moves +0.389 more than the
> concentrated arm, about seven times the standard error.

Date: 2026-07-25
Kernel: `hirokenzan/vd-spread-intervention-1` (COMPLETE, 153 minutes)
Spec: `experiments/spread_intervention/SPEC.md` (predictions registered before the run)
Script: `experiments/spread_intervention/script.py`
Data: `experiments/spread_intervention/output/spread_intervention.json`

## What was done

Two arms of a selection loop differing **only** in how candidate value-variation is
distributed across prompts, at an **identical offered-pool mean every round**. The
CONCENTRATED arm minimises within-prompt spread (variation pushed between prompts);
the SPREAD arm maximises it. Same organism, same frozen base judge, same
hyperparameters, same seeds, arms stepped in lockstep. Qwen3-4B-Instruct with a risk
persona, 12 gamble prompts, 12 candidates each, 6 offered, 2 kept, 4 rounds, 3 seeds,
plus a random-selection control pair.

This is the first test of the model's spread term that is not confounded with the
pool mean. In every previously logged run the two move together, so no observation
could separate "the value stopped moving because there was no variation to select on"
from "it stopped because it was already at the end of the scale."

**The manipulation succeeded completely.** Achieved within-prompt spread was
**exactly 0.0000** in the concentrated arm in 11 of 12 rounds and 0.31–0.48 in the
spread arm, at pool means matching to 0.0 across all rounds and seeds. No candidate
failed to parse.

## Result 1: the selection step behaves exactly as the model says

| Arm | Within-prompt spread | Selection gap achieved |
|---|---|---|
| Concentrated | 0.0000 | **+0.0035** (exactly 0.000 in 11 of 12 rounds) |
| Spread | 0.31–0.48 | **−0.1458**, negative in every single round |

With no within-prompt variation the judge extracts no gap; with variation it extracts
a consistent one. The judge's agreement with the value axis is −0.08 to −0.47 in the
spread arm and undefined in the concentrated arm, because there is nothing to
correlate against.

**This is confirmation with an important qualification.** The concentrated arm's zero
gap is partly forced by arithmetic: the gap is the kept mean minus the pool mean, so a
prompt whose candidates all score alike contributes exactly zero whatever the judge
does. What is *not* arithmetic is the spread arm's −0.146 — that is a real, sustained,
directional taste, and the contrast establishes that a judge with variation available
uses it.

## Result 2: the value did not follow the gap it was trained on

The spread arm accumulated a selection gap of −0.146 per round for four rounds across
three seeds. The model says the value should have fallen substantially. It did not
move.

Regressing observed round-to-round movement on the model's prediction (transmission
coefficient 0.83 times the realized gap), across all 24 round-transitions:

| Quantity | Value | Model says |
|---|---|---|
| Correlation, predicted against observed | **+0.046** | strongly positive |
| Slope | **+0.054** | 1.0 |
| Model mean absolute error | 0.0944 | — |
| Mean absolute error of forecasting *zero movement* | **0.0648** | — |

**The model is worse than assuming nothing happens.**

Accumulating over the full four rounds, per arm, with the three seeds giving the
spread:

| Arm | Model predicts | Observed | Discrepancy |
|---|---|---|---|
| Concentrated | +0.012 | −0.009 | 0.8 seed-SE — consistent |
| Spread | **−0.287** | **+0.028** | **4.8 seed-SE — rejected** |

The concentrated arm matches the model, but trivially: with a zero gap the model
predicts no movement and none was seen. The spread arm is where the model makes a real
prediction, and the predicted decline of 0.287 is excluded at 4.8 standard errors.

## What this cannot establish, and the control that is missing

**Per-round movements are smaller than the measurement noise.** The value readout is
12 probe items sampled 3 times, so 36 binary reads: granularity 0.028, standard error
about 0.076 on a single read and **0.108 on a round-to-round difference**. The mean
absolute observed movement is **0.065** — below the noise on a single difference.

So this run excludes the model's *predicted effect size*, which accumulates over four
rounds to something large enough to see. It does **not** exclude a small true
transmission effect, and it cannot distinguish "training moves the value but not along
the gap" from "training barely moves the value at all". The concentrated arm's
apparent wandering is equally consistent with pure measurement noise.

**The design is missing a positive control**, and that is the first thing to fix. There
is no arm demonstrating that this training step *can* move the value when the selection
pressure is unambiguous. Without it, a null on transmission is ambiguous between a real
failure of the response step and a training configuration that does nothing. The next
run should add a strong oracle-selection arm targeting a gap around ±0.5 and confirm
the value tracks it.

## Why this matters beyond this experiment

The programme's transmission coefficient of roughly 0.83 is estimated from
observational rounds where the response and the selection differential **share the term
v_t**. An independent re-derivation on 2026-07-24 found that shared measurement noise
accounts for **27.5%** of the covariance driving that slope, and that correcting for it
lowers the estimate to about 0.758.

This experiment removes the shared term by construction: the gap is set exogenously by
the arrangement of candidates, not derived from the same measurement as the response.
Under that condition the relationship largely disappears — slope 0.054 rather than 0.83.

That is a coherent and uncomfortable story: **part of what looks like a
selection-response law in observational data may be the two sides of the equation
sharing a noisy measurement.** With three seeds and a 36-read value probe this is a
strong hypothesis and not an established result. It is also the most consequential open
question in the programme, and it is cheap to settle.

## What to run next, in order

1. **Positive control**: an oracle-selection arm with a gap near ±0.5, to establish that
   the training step can move the value at all. Without this nothing else is
   interpretable.
2. **A far less noisy value readout.** 36 binary reads cannot resolve the per-round
   movements this design produces. Several hundred reads would bring the standard error
   on a difference from 0.108 to about 0.03.
3. Only then, more seeds. Adding seeds to a noise-dominated readout buys very little.

## Registered predictions, scored

The spec registered three outcomes. The result is outcome 2 — "both arms move
similarly; the spread term does not survive decoupling from the mean" — which the spec
called "a significant negative result about the program's central equation and the
outcome most worth knowing." Recording that this was the pre-registered reading and not
a post-hoc reframing.

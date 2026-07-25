# Spec: measuring a model's multi-attribute value structure without a judge

Status: designed 2026-07-25, not built. Lane: Kaggle T4, free. Inference only for
phase A; phase B adds training.

## Why this design, and why the previous one failed

The value-covariance experiment tried to measure how several values covary across a
model's own candidate answers by having an LLM judge score each free-text answer on
six abstract rubrics. It failed at the instrument, not the statistics
(`report_value_covariance_phase1.md`): two judges scoring the *same* axis agreed at
only 0.345 to 0.467, every off-diagonal correlation came out positive including
+0.553 between risk-tolerance and caution — axes written as near-opposites — and
residualising on answer length changed nothing. A 4-billion-parameter judge rating
abstract qualities of prose produces a dominant general factor that swamps the
between-axis structure.

This repo already knows the general form of that lesson. Its own instrument
calibration records that free-text LLM-judge readouts vary by family and must be
checked per family, while programmatic parses are trustworthy. Every value axis that
has worked in this program — `semantic_risk`, `p_risk`, the forced A/B self-reports —
is a **mechanical parse of a discrete commitment**, not an adjudication of prose.

So: stop asking a judge what an answer is like. Make the model choose between options
whose attributes are **fixed by construction**, and read the choice.

## The method

This is a discrete-choice (conjoint) design, the standard tool for recovering
multi-attribute preferences from choices rather than ratings.

Define K binary attributes. Each option shown to the model is a short, concrete
action that instantiates one particular combination of attribute levels. Because we
author the options, every option's position on every attribute is **known exactly, by
construction** — there is nothing to judge and nothing for a halo to attach to.

Proposed attributes, each with a plain-language contrast:

| Attribute | Level 1 | Level 0 |
|---|---|---|
| Risk | takes the higher-variance path | takes the lower-variance path |
| Reversibility | leaves a way to undo it | commits irreversibly |
| Disclosure | tells the affected person | does not mention it |
| Scope | uses only what the task needs | takes broader access or budget |
| Speed | acts now | waits for more information |
| Deference | does what the asker wanted | overrides the asker's stated wish |

Each scenario supplies a situation; each option is a one-sentence action carrying a
full attribute vector. The model is shown two options and asked which it would do.
The choice probability is read from token logprobs.

**The thinking block must be forced closed before reading logits, and padding must be
left-side.** Both are settled facts in this repo, each having cost a run: with the
block open, the next-token distribution is dominated by the reasoning opener and the
read measures its noise tail, which has a fixed lexical preference.

## What is recovered

Fit a logistic utility model over choices:

    P(choose A over B) = logistic( sum_k beta_k * (a_k - b_k) )

The vector of `beta_k` is the model's **value weight on each attribute, in
commensurable units** — how much risk it will accept per unit of reversibility, and so
on. This is the quantity the free-text design was groping at, obtained without a
judge.

Two things follow that the rubric design could not deliver:

- **The weights have a covariance**, estimated by bootstrapping over scenarios. That
  covariance is a real property of the model's preferences rather than an artifact of
  one judge's general impression of prose.
- **Attribute levels are orthogonal by design.** Randomising the attribute vectors
  across pairs means risk and reversibility are uncorrelated in the stimulus set, so
  any correlation in the *estimates* is informative rather than baked in. In the
  failed design, the axes' correlation was whatever the judge's halo made it.

## Phase A — measure the weights (inference only, roughly 1 hour)

30 scenarios, 24 option-pairs each with attribute vectors randomised subject to
balance, both presentation orders. Fit the logistic model; bootstrap over scenarios
for intervals.

**Gates, declared now:**
- *Discrimination*: the fitted weights must not all be within noise of zero. At least
  three of six attributes must have a bootstrap interval excluding zero. If the model
  is indifferent to everything, the design cannot proceed.
- *Order robustness on the real stimuli, not on constructed contrasts*: mean
  presentation-order gap below 0.15. Phase 1 taught that a judge can be order-robust
  on clear cases (gap 0.006) and heavily position-driven on realistic ones (gap
  0.609), so this gate must be evaluated on the actual pairs used.
- *Attribute balance*: each attribute must appear at each level in at least 40% of
  pairs, checked before fitting.

Phase A is a standalone result if it passes: a measured, judge-free profile of what a
model trades off against what.

## Phase B — the selection question (adds training, roughly 4 hours)

The program's actual question is what happens to the other values when you select on
one. With attributes controlled, that becomes clean.

Select training data by **one attribute only** — keep the option that is higher on
risk, ignoring every other attribute — then LoRA fine-tune on the kept choices and
re-measure all six weights. Repeat selecting on a different attribute. A random-
selection arm sets the drift floor.

The prediction from correlated-response theory is that selecting on attribute *a*
moves attribute *b* in proportion to their covariance in the *stimulus set actually
selected over*, which here is known exactly rather than estimated through a judge.
That makes the prediction sharp: the design matrix is under our control, so the
expected off-target response can be computed in advance rather than fitted.

## Honest limitations

- Authored options measure preferences over **our** framings, not over the model's own
  generated behaviour. This buys measurement validity at the cost of ecological
  validity, which is the opposite trade from the failed design. Both are worth having;
  neither substitutes for the other.
- Six binary attributes in one-sentence options risks stilted, unnatural text that the
  model may respond to differently from real requests. A manipulation check should
  confirm the options read as plausible actions.
- The logistic fit assumes attribute effects are additive and non-interacting. Test at
  least one interaction (risk × reversibility is the obvious candidate) before
  claiming the weights are separable.
- Nothing here measures what the model *does* unprompted; it measures what it picks
  when given a menu. The relationship between the two is itself an open question and
  should not be assumed.

## Build order

1. Author the scenarios and option templates; verify attribute balance offline.
2. Write `smoke_test.py` first, exercising the full call graph with stubbed models,
   asserting attribute balance and that a planted weight vector is recovered by the
   fitter. A run today lost 90 minutes of GPU to a signature error that syntax
   checking did not catch.
3. Run phase A. Only proceed to phase B if all three gates pass.

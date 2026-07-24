# Spec: does the value actually respond to spread, at a fixed pool mean?

Status: designed 2026-07-24, not yet run. Lane: Kaggle T4, free. Requires training.

## Why this is the experiment, and why the cheap version was not

The program's model says a round moves the value by roughly

    movement  =  transmission x agreement x spread

The spread term has never been tested independently, because **in every run ever
logged, spread and the pool mean are confounded**: on a binary-scored axis the
one-parameter law spread ≈ 0.813·√(q(1−q)) accounts for 85.9% of the variance in
measured spread (`report_spread_is_not_a_free_variable.md`). So whenever spread was
low, the value was near a rail, and no observation separates "the value stopped
moving because there was no variation to select on" from "the value stopped moving
because it was already at the end of the scale."

A re-selection analysis on logged pools cannot settle this and should not be
attempted again. It was, on 2026-07-24, and the result was definitional: the
selection gap is kept-minus-pool, so a prompt whose candidates all score alike has a
gap of exactly zero by arithmetic. Collapsing within-prompt spread collapses the gap
by construction — the median ratio of gap to (agreement × spread) came out at 0.831
in the high-spread arm and 0.825 in the low-spread arm, indistinguishable, meaning
the manipulation slid along the identity instead of testing it. That artifact is
retained only as a feasibility check (`report_spread_at_fixed_mean.md`).

**The non-definitional question is what happens after training.** Nothing about the
identity gap = agreement × spread tells you whether the model's measured value
actually follows the kept mean when spread is manipulated rather than observed. That
is a claim about the training step, and it can only be answered by training.

## Design

One organism, one value axis, matched pairs of runs differing **only** in how
candidate variation is distributed across prompts.

Each round, the organism generates 12 candidates for each of 12 prompts. Candidates
are scored on the value axis. Then, before the judge sees anything, the offered pool
is constructed by choosing 6 of the 12 candidates per prompt, under one of two
allocation rules:

- **CONCENTRATED arm** — choose so that within-prompt spread is minimized: each
  prompt's offered pool is as value-uniform as the candidates allow, with the
  variation pushed between prompts.
- **SPREAD arm** — choose so that within-prompt spread is maximized: every prompt's
  offered pool is as internally mixed as the candidates allow.

**Both arms are constrained to the identical overall pool mean each round**, solved
exactly by the knapsack in `scripts/analysis_spread_at_fixed_mean.py`, which already
works and is unit-tested. The judge, the prompts, the organism, the keep count, the
training hyperparameters, and the seed are all identical across arms.

Then the loop actually runs: judge selects 2 per prompt, LoRA fine-tune on the kept
answers, re-measure the value on held-out prompts, repeat for 4 rounds. 3 seeds per
arm, so 6 runs.

## What is predicted, and what would falsify it

Recorded before running.

The model predicts the CONCENTRATED arm barely moves and the SPREAD arm moves
substantially, **even though both start at the same value and offer the same pool
mean every round**. Quantitatively, per round, movement should track transmission ×
agreement × spread with the transmission coefficient the program already estimates
(0.76 to 0.83 after the measurement-error correction).

Three outcomes, all informative:

1. **Movement tracks spread as predicted.** The spread term is causally real and
   separable from the value's position. This is the first test of it that is not
   confounded with the pool mean, and it would materially strengthen the model.
2. **Both arms move similarly.** The spread term does not survive decoupling from the
   mean — the model's fit to observed data was carried by the mean, and the
   spread-times-agreement form is a coincidence of the confound. This would be a
   significant negative result about the program's central equation and is the
   outcome most worth knowing.
3. **The CONCENTRATED arm moves MORE.** Would indicate something the model has no
   account of, most likely that training on a value-uniform kept set is a stronger
   or cleaner gradient signal than training on a mixed one.

The primary readout is the measured value on held-out prompts after 4 rounds, per
arm, with the 3 seeds giving the within-arm spread. Secondary: per-round movement
against per-round transmission × agreement × spread, pooled, which should lie on the
program's existing line if outcome 1 holds.

## Controls that are not optional

- **The kept-set size is identical across arms** (2 per prompt), so any difference is
  not a difference in the amount of training data.
- **Both arms train on kept sets with the same overall value mean each round** where
  the knapsack permits it; where it does not, the realized kept means are logged and
  the gap between arms is reported rather than assumed away.
- **A no-selection control** (random pick of 2 per prompt) in each arm, 1 seed each,
  to establish the drift floor for this organism and prompt set.
- Candidate generation is shared: **both arms are built from the same 12 generated
  candidates per prompt in round 1**, so round-1 differences cannot come from
  sampling. From round 2 the arms diverge because the models differ, which is the
  point.

## What would make this wrong

- If the organism's candidates are too value-uniform to construct a real contrast,
  the two arms collapse into each other and the experiment is uninformative. The
  feasibility check says the contrast is constructible on logged pools (3.5-fold, at
  6 candidates per prompt), but that was on pools generated without this in mind.
  **Gate: round 1 must achieve a within-prompt spread ratio of at least 2 between
  arms, or stop and raise the generation temperature.**
- The CONCENTRATED arm makes many prompts value-uniform, which means the judge is
  choosing among candidates it cannot discriminate on the value axis. It will still
  choose, on style or length. That is not a flaw — it is what a low-spread round
  genuinely is — but the kept sets will differ in ways beyond the value axis, so log
  answer length per kept set and report it.
- 3 seeds per arm is small. It is enough to separate "moves" from "does not move"
  given that observed endpoint differences in this program are large, but not enough
  to estimate an effect size. Do not report a slope from 6 runs.

## Cost

Roughly 4 to 6 hours on one T4 for 6 runs of 4 rounds at 4B scale, plus the control
arms. Free tier. No Modal.

## Relationship to the other queued experiment

This is independent of `experiments/value_covariance/` and sharper, because it tests
a term the writeup already relies on rather than opening a new direction. If only one
runs, run this one.

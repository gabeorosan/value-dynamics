# The response to selection does not decay over a run

**Analysis date** 2026-07-28 · **Script** `scripts/analysis_response_saturation.py`
· **Result** `experiments/response_saturation.json` · **Corpus**
`experiments/spread_util_unified.json` (340 rounds, 74 runs)

## What this was asking

Earlier in the program the per-round regression of value movement on the
selection gap looked like it decayed: 0.509, then 0.377, then 0.231 across the
first three rounds of the spread-intervention corpus. That shape has an
interesting reading — repeated selection wears the model out, the way reward-model
overoptimisation curves bend over in Gao, Schulman & Hilton
([arXiv 2210.10760](https://arxiv.org/abs/2210.10760)) — and a boring one:
later rounds are a different sample, or the runs are simply running out of scale.

This analysis puts four explanations against the full 340-round corpus.

- **Headroom.** The response is proportional to how much of the 0-to-1 scale is
  left in the direction being pushed. Runs slow down because they approach a
  rail. A replicator or logistic model predicts exactly this, and it implies
  nothing special happens from repeating selection.
- **Wear.** Accumulated selection pressure degrades the response wherever the
  value sits. This is the overoptimisation reading.
- **Survivorship.** Nothing declines within a run at all. Fast movers stop
  early, so the runs still present at round 4 were always the sluggish ones.
- **Within-round concavity.** Nothing declines across rounds either; the
  response is just concave in the size of a single round's gap. This one matters
  because cumulative pressure is built out of past gaps, so a `gap × pressure`
  term will silently absorb plain concavity unless `gap × |gap|` is fitted
  beside it. Every model here carries that term.

## Two specification errors this analysis had to fix first

**The movement law is drift on *pull*, not drift on gap.** Pull decomposes as
`(pool_mean − v) + gap`: a supply term, because the candidate pool need not be
centred on the organism's current measured value, plus the selection term.
Regressing drift on the gap alone omits the supply term, and the omitted
variable is correlated with the gap. With the supply term missing, the round-1
slope came out at 1.648 and the by-round profile looked like a clean collapse —
1.648, 0.632, 0.536, 0.380. With the supply term in, the same corpus gives
0.941, 0.596, 0.705, 0.596. Most of the apparent decay was the omitted variable.

**The pool-offset regressor shares measurement noise with the outcome.** Supply
is `pool_mean − v_t` and drift is `v_{t+1} − v_t`; both carry the same error in
`v_t`, with the same sign. That inflates `cov(supply, drift)` and `var(supply)`
by the same `var(e)`, pulling the supply coefficient toward 1 and dragging the
gap coefficient with it. In this corpus the noise is **46.1% of the observed
supply variance** — not a rounding correction. Subtracting `var(e)`, taken from
each round's own recorded measurement standard error rather than from an
assumption, gives the corrected estimates below.

The gap itself needs no such correction. It is computed from candidate scores
that are observed exactly given the pool, and the candidates live on training
prompts while `v` is read on held-out prompts, so noise in `v_t` enters the
outcome but not the regressor.

## Identification

Reported before the fits, because the three mechanisms are collinear by
construction and the honest answer might have been that the corpus cannot
separate them.

| pair | correlation |
|---|---|
| round index vs cumulative pressure | 0.658 |
| round index vs rail-closeness | 0.018 |
| cumulative pressure vs rail-closeness | 0.130 |
| `gap × |gap|` vs `gap × cumulative pressure` | 0.654 |
| supply vs gap | 0.158 |

Rail-closeness is essentially orthogonal to round index, so **headroom and wear
are separable here**. Cumulative pressure is correlated with the round index at
0.658 and with within-round concavity at 0.654, so wear is the term most at risk
of absorbing something else — which is why concavity is always fitted alongside
it and why the within-run estimate below is the one that decides.

## Result 1 — the headline coefficients

Measurement-error-corrected, all 340 rounds:

**supply 0.759, gap 0.809** (naive: 0.873 and 0.791)

On the 324 rounds from runs that complete the four-round horizon: **supply
0.838, gap 0.732** (naive: 0.913 and 0.720).

Both coefficients sit below 1. The writeup's parameter-free rule — next value =
kept mean — is the claim that both are exactly 1; the data says the update lands
about three-quarters to four-fifths of the way there, on both components.

**The gap coefficient agrees with the instrumental-variables estimate from an
entirely different corpus.** The randomised round-1 arm assignment in the
spread-intervention runs gave 0.754, 95% CI [0.621, 0.984]. This corpus, by
ordinary regression with the supply term controlled and measurement error
removed, gives 0.809 over 340 rounds and 74 runs. Different data, different
identification strategy, overlapping answer.

## Result 2 — the decay does not survive the controls

By-round gap slope, supply term controlled:

| | round 1 | round 2 | round 3 | round 4 |
|---|---|---|---|---|
| all 74 runs | 0.941 | 0.596 | 0.705 | 0.596 |
| the 70 runs that complete round 4 | 0.721 | 0.527 | 0.705 | 0.596 |

Only four runs stop short of the standard horizon, so survivorship cannot carry
much weight in this corpus — but what weight it has points the same way. The
eight round-1 records from short runs have a slope of **1.550** against
**0.721** for the 70 completers. Fast movers really are the ones that stop
early. Restricted to completers, the profile is 0.72, 0.53, 0.70, 0.60: a step
down after round 1, then flat. No trend.

In the nested models on the completers' panel, every candidate decay term is
indistinguishable from zero — `gap × (round−1)` is **0.001**, wear is **−0.258
[−0.53, 0.39]**, headroom is **0.150 [−0.14, 0.36]** — and no model improves
leave-one-run-out cross-validated MAE by more than 0.001 over the plain linear
one (0.0767 against 0.0766 for the fullest model).

## Result 3 — within runs, the wear term reverses sign

The pooled fits compare rounds across different runs. Demeaning by run so that
only variation between rounds of the *same* run identifies the coefficients:

| term | within-run estimate | 95% CI |
|---|---|---|
| pool offset | 1.062 | [0.95, 1.15] |
| gap | 0.443 | [0.16, 0.69] |
| gap × \|gap\| | 1.237 | [0.51, 2.26] |
| gap × cumulative \|gap\| | **+0.379** | [0.05, 0.64] |

The wear coefficient is **positive**. Within a run, the response per unit of
selection is *stronger* after more accumulated pressure, not weaker. The
concavity term is positive too, so the response is convex in the gap within a
round, not concave. Both point away from overoptimisation.

Adding rail-closeness (0.134, CI [−0.18, 0.47]) leaves the wear term at 0.267
with a CI that now includes zero, so the within-run evidence is "no negative
wear", not "confidently positive wear".

One bias worth naming: with four rounds per run, demeaning induces a Nickell-type
bias in a panel whose regressor is built from past outcomes. That bias is
*negative* for a positively autocorrelated regressor, so the true within-run
coefficient is at least as large as the +0.379 estimated. The conclusion — no
wear — is robust to it.

## What this means

**The apparent saturation was an artefact of specification and sample, not a
property of the loop.** Once the pool-offset term the movement law actually
contains is included, measurement error in that term is removed, the sample is
restricted to runs that finish, and identification comes from within runs rather
than across them, the response coefficient is flat at roughly 0.73–0.81 and no
decay term survives.

Two consequences for the program:

1. **The overoptimisation framing does not apply here, at this horizon.**
   Repeated selection over four rounds does not wear the response out. If a
   Gao-style bend exists it is beyond four rounds, or it needs more cumulative
   pressure than these runs accumulate. The eleven eight-round runs are the place
   to look, and they are too few to fit on their own.
2. **Runs level off because the gap shrinks, not because the response to it
   shrinks.** Mean absolute gap falls from 0.099 at round 1 to about 0.070 by
   round 4, while the response per unit gap holds. The interesting saturation is
   in the *supply* of selectable variation — the spread — not in transmission.
   That is where the next round of work should point.

## Result 4 — the original decay does not reproduce on its own corpus

The 0.509 / 0.377 / 0.231 numbers came from the spread-intervention corpus, not
the one above, so the retraction is not complete until the same respecification
is applied there. `scripts/analysis_spread_corpus_saturation.py` does that over
all eleven committed spread-intervention output files — 414 rounds from 126 runs.

| | round 1 | round 2 | round 3 | round 4 | round 5 | round 6 |
|---|---|---|---|---|---|---|
| n | 128 | 128 | 102 | 34 | 16 | 6 |
| slope, gap only | 0.546 | 0.428 | 0.284 | 0.367 | 0.128 | −0.198 |
| slope, supply controlled | 0.547 | 0.476 | 0.408 | 0.353 | 0.031 | 0.190 |

The gap-only row is the same specification the original three numbers used, run
over the whole corpus rather than a subset, and it gives 0.546 / 0.428 / 0.284 —
not 0.509 / 0.377 / 0.231 — and then turns back up at round 4. With the supply
term controlled the decline is gentler still, and the round-index interaction,
fitted alongside within-round concavity, is **−0.042 [−0.100, 0.026]**: an
interval containing zero.

Two numbers from this corpus are worth carrying beyond the retraction.

**The pooled response coefficient here is 0.486 [0.419, 0.567], and 0.450 after
the measurement-error correction** — well below both the 0.809 from the unified
corpus and the 0.754 instrumental-variables estimate. That is not a
contradiction, it is the censoring signature. This corpus aborts runs on a
matched-pool-mean criterion and the aborted runs are the fast movers; the
unified corpus loses only 4 of 74 runs. So:

| estimate | corpus | censoring | value |
|---|---|---|---|
| observational, supply-controlled, noise-corrected | unified (340 rounds) | almost none | 0.809 |
| randomised instrument, round 1 only | spread-intervention | none by construction | 0.754 |
| observational, supply-controlled, noise-corrected | spread-intervention (414 rounds) | heavy | 0.450 |

The two censoring-free estimates agree with each other across different corpora
and different identification strategies; the censored observational estimate is
the one that stands apart, in the direction and roughly the magnitude the
censoring diagnosis predicts. That is the strongest evidence yet that the
transmission coefficient is around 0.75–0.8 and that the low observational
readings were an artefact of which runs were allowed to finish.

## Retraction carried

The "response coefficient decays 0.509 → 0.377 → 0.231" statement, used in the
2026-07-27 transmission entry as supporting evidence for the censoring story, is
**withdrawn on two counts**. It does not reproduce: the same gap-only
specification over all 414 committed rounds of that corpus gives 0.546 / 0.428 /
0.284 and then rises again at round 4, so the original three numbers came from
some unrecorded subset. And it does not survive controls: with the supply term
and within-round concavity fitted, the round-index interaction is −0.042
[−0.100, 0.026] there and 0.001 on the completers' panel here.

Do not cite the three numbers, and do not fit curves to them — a functional form
fitted to three unreproducible points will look excellent (a straight line
through them has R² 0.999) and mean nothing.

The censoring finding they were cited beside — aborted runs moved +0.074 per
round against +0.023 for completed ones — stands on its own, is corroborated
here by the short-run round-1 slope of 1.550 against 0.721, and is now the
explanation for the 0.450-versus-0.754 gap in Result 4.

## What would move this

- Refit the same models on the spread-intervention corpus with the supply term,
  to confirm the 0.509/0.377/0.231 profile flattens there too.
- Longer horizons. Four rounds accumulate a mean cumulative pressure well short
  of anything the overoptimisation literature calls heavy optimisation.
- A pressure ladder that varies cumulative selection *at fixed round index*,
  which would break the 0.658 collinearity that limits this analysis.

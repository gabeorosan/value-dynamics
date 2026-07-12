# Mixed-generator owner-blind screen: taste gate PASSES, style gate FAILS genuinely — grid stays gated, one big free finding

*2026-07-12 ~00:30 (late night), general thread. User-run Colab execution of
experiments/em_mixed_generators/LAUNCH_owner_blind_screen.py — 24 mixed pools
(6 questions × 4 replicates), each 3 candidates from em_dose_750 (owner A) +
3 from the fresh Qwen base (owner B); insecurity-admission (sr) scored by the
frozen base; frozen-base and em750-self judges rank each pool. Raw artifact:
experiments/em_mixed_generators/output_mixed_screen_owner_blind.json. Caveat:
this execution ran before the numeric gates were written down and with an
UNPINNED model revision — gate (a) reads are post-hoc against rules written
the same night; a pinned confirmation ride-along is required at pilot round 0
if a pilot ever launches.*

## Gate (a) — between-owner taste: PASS

- The value axis is wide open: owner-A candidates score +0.438 higher on
  insecurity-admission than owner-B candidates (pool means, sd 0.34) —
  far above the 0.15 gate.
- **Base judge**: kept A-share 0.125 vs 0.5 blind (|deviation|/SE = 8.5;
  gate needs >2), sr kept-gap −0.139. A strong, consistent selection force
  toward owner-B/secure material.
- **Self judge (em750)**: kept A-share 0.417 (1.2 SE — NOT significant),
  sr kept-gap −0.061. **The capture prediction's premise fails**: the EM
  organism judging mixed pools does not prefer its own flavour.

## Gate (b) — style-artifact classifier: FAIL, and genuinely

Leave-one-question-out logistic on five surface features classifies owner at
**0.93** (gate: <0.65). The obvious objection — "the owners differ in value,
so the classifier is just reading the value" — was tested on value-matched
subsets: among SECURE-sounding candidates only (sr < 0.2, 30 A vs 64 B),
owners still classify at **0.835 vs a 0.68 majority-class baseline**. The
dose-750 adapter writes detectably differently even when saying secure
things. Style leak is real, not value bleed-through.

Per the SPEC's pre-registered rule: **the mixed-generator training grid does
NOT launch on tonight's evidence.**

## The decomposition that the style leak forces (and the free finding)

With owner style recoverable, the base judge's between-owner preference is
ambiguous (security taste vs base-style self-preference, Panickssery-style).
The within-owner correlations separate the two, because style is constant
within an owner:

| judge | corr(judge score, sr insecurity) within owner-A (n=72) | within owner-B (n=72) |
|---|---|---|
| base | **−0.307** | +0.057 |
| self | +0.092 | +0.041 |

Three conclusions:

1. **The frozen base judge has REAL security-direction taste on the EM
   organism's own candidates** (−0.31 within owner A, style held constant) —
   the first genuinely negative value-direction selection signal measured
   tonight, and it comes from the plain neutral "which answer is better?"
   prompt, not the failed explicit secure prompt
   (docs/report_secure_taste_screen.md). Between owners this bundles with
   probable style self-preference (no discrimination within its own style,
   +0.06), so the 0.125 A-share overstates the value force.
2. **The self judge has no value taste anywhere** (+0.04 to +0.09) — its
   near-blind A-share is genuine indifference, not balanced taste.
3. For the opposition arc: a **frozen-base neutral judge over an EM
   organism's own pools** is a measured natural opposing force on the sr
   axis — a cleaner prompted-judge candidate than any security-worded
   prompt, sitting between "no force" and the oracle's maximum force.

## Redesign path for the grid (before any training)

Paraphrase normalization: rewrite every candidate through the frozen base
("restate this answer in plain neutral prose, preserving its content")
before judging, so judges see style-normalized text while training still
uses the original owner text. Re-run this screen on normalized pools; gate
(b) then means what it says. Alternative (weaker): proceed and interpret
owner-taste as a bundled value+style force — a dynamics experiment still,
but no clean value-transmission attribution.

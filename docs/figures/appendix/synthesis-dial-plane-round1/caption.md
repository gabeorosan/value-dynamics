# synthesis-dial-plane-round1

**The (round-1 agreement ρ, round-1 spread σ) plane, with both layers made into the same one-round object.**
The background is painted, cell by cell, with the committed recurrence's forecast
one-round move of the behavioral value — predicted move = agreement ρ × spread σ
(red where it says the value climbs, blue where it says the value falls, pale gray
near zero; dashed iso-contours mark ρσ = ±0.05 and ±0.10). Each dot is one
modelable run placed at its round-1 dials and filled by that run's **observed
first one-round move** — round-2 value minus round-1 value (the repo's
consecutive-round transition convention; equal to the round-1 `drift` field). Both
layers are now literally the same per-round quantity in the same units, so they
share one recalibrated diverging scale that saturates at |move| = 0.35 (first
moves mostly fall within ±0.35; the forecast ρσ tops out near ±0.40). A dot whose
color matches the gradient behind it is the one-round law holding; a clash is it
failing — color agreement is therefore a **literal test** of the ρ·σ law rather
than the sign-and-magnitude analogy the whole-run sibling figure could only offer.

**This candidate's resolution of the units mismatch:** make the dots one-round.
The prior figure shaded the model's one-round forecast ρσ but colored dots by each
run's whole-run endpoint move (two different time horizons on one scale). Here the
dots become one-round objects too.
- **Trade-off:** the figure no longer shows where a run *ended* — its compounded
  net move over all the rounds it ran. That endpoint story lives in the rollout
  figures, not here.
- **Gain:** an exact unit match. Background darkness and dot darkness mean the same
  number, so the sign-concordance readout is an honest test of the one-round law.

**Readouts (recomputed for first-round moves).** Of the 67 modelable runs, 41 had
a first move clearing the ±0.10 threshold; **33 of those 41** sit on a background
of the matching color (sign of observed first-round move equals sign of forecast
ρσ = sign of ρ, since σ > 0). Movers split 17 up / 24 down / 26 flat at ±0.10.
Seven of the 74 total runs are unplotted because their round-1 ρ is undefined
(zero within-pool spread makes the correlation undefined); every modelable run also
had a measurable first move, so no run was dropped for a missing round 2 (printed
skip accounting: 7 ρ-undefined, 0 no-first-move).

**Source data:** `experiments/spread_util_unified.json` (records list; one run =
the tuple cond × seed × source, its records sorted by round). The generator reads
this file directly and asserts the run/skip counts at load time.

Regenerate: `python3 synthesis-dial-plane-round1.py` from this directory (stdlib only).

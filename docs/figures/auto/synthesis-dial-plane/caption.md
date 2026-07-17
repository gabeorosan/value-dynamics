# synthesis-dial-plane

**The background is the model's forecast, each dot is a run's actual move: where
the colors agree, the model is right.** The redesign paints the committed
recurrence's one-round selection forecast onto the (agreement ρ, spread σ) plane
as a continuous background, on the *same* diverging color scale the dots use, so
that a run whose dot color matches the gradient behind it is the model's forecast
holding — and a color clash (a blue dot on red background, or vice versa) is the
forecast failing, visible at a glance.

## What the axes and marks are

The (agreement ρ, spread σ) plane, one dot per modelable run. The x-axis is the
round-1 **agreement** ρ = correlation, across the candidate pool, of the judge's
score with the behavioral value score (−1 = judge forced to fight the value,
+1 = lockstep). The y-axis is the round-1 **spread** σ = standard deviation of
the behavioral value score across the candidate pool.

**Dot fill** encodes the **observed net endpoint move of the behavioral value** —
the run's **final measured value minus its round-1 value** — on a continuous
diverging scale with a pale neutral midpoint (near-white at zero, blending
linearly toward **red** = moved up or **blue** = moved down, saturating at ±0.6).
Color is the only thing encoded on the dots; every dot is a uniform size. Each dot
carries a white halo and a thin dark edge so it stays legible over any background
color. (Of the 67 plotted runs, 25 moved up ≥ +0.15, 25 moved down ≤ −0.15, and
17 sit within ±0.15 of no net move — a descriptive threshold only; asserted to
sum to 67.)

**The background** is painted, cell by cell (a 60 × 40 grid of rectangles), by the
model's **one-round forecast move at that point of the plane = ρ · σ** — the
selection term of the committed recurrence, whose sign is positive (value climbs)
right of ρ = 0 and negative (value falls) left of it, and whose magnitude grows
with spread. It uses the **exact same `move_color` scale as the dots**, drawn at
reduced opacity (0.62) so the dots read on top. Faint dashed **iso-contours** mark
ρ · σ = −0.10, −0.05, 0 (the vertical line), +0.05, +0.10, each with a small
white-haloed inline label.

## The honesty caveat (stated in the subtitle and on the figure)

The dots are the **whole-trajectory** move (the one-round force compounded over
however many rounds a run ran); the background is **one** round of that same force.
Only the **sign** and the **relative** magnitude are comparable — the background
is never relabeled as an endpoint prediction, and because ρ · σ only reaches about
±0.5 across this plane (versus the ±0.6 dot scale), the background is never fully
saturated: one round is always weaker than the compounded endpoint. This is why
the comparison the figure invites is color *agreement*, not matching darkness.

## The readout on the figure

A boxed sign-check, computed live from the JSON at generation time: **of the 50
runs that moved by at least 0.15, 39 sit on a background of the matching color** —
i.e. the sign of the observed endpoint move equals the sign of the forecast ρ · σ
(which, since σ > 0, is the sign of the round-1 agreement ρ). The blue movers
concentrate left of ρ = 0 over blue background; the red movers concentrate right of
it over red background; the grayest (no-net-move) dots hug ρ ≈ 0 or low σ where the
forecast, and the background, are near zero.

## Provenance and caveats

One run = the tuple (cond, seed, source); the round-1 record supplies ρ, spread,
and value; the last record supplies value + drift. Of 74 total runs, **7 have an
undefined round-1 ρ and are not plottable on these two axes**, leaving **67
modelable runs** plotted — counts asserted in the generator. Of those 7: 3 have
zero within-pool spread (correlation undefined), and 4 are random-selection
controls whose judge–value correlation is undefined by construction. Mixed pools
(base/peer compositions) also receive a **pool shift (p − q)** from the outside
candidate source that is not represented on these two axes and not in the ρ · σ
background; it is a third force the plane does not show.

## Source data

- `experiments/spread_util_unified.json` — the `records` list (fields `rho`,
  `spread`, `value`, `drift`, `cond`, `seed`, `source`, `round`, `judge`,
  `composition`, `format`). n_records = 340, n_runs = 74, plotted = 67
  (25 up / 25 down / 17 flat; sign concordance 39 of 50 movers).

Regenerate: `python3 synthesis-dial-plane.py` (stdlib only) from this directory.

# synthesis-dial-plane

**Every run at its round-1 agreement and spread, colored by where its value
went.** The figure is deliberately spare: it places each run once and paints it
with a single continuous color scale for the endpoint move. All interpretation
lives here.

## What the axes and marks are

The (agreement ρ, spread σ) plane, one dot per modelable run. The x-axis is the
round-1 **agreement** ρ = correlation, across the candidate pool, of the judge's
score with the behavioral value score (−1 = judge forced to fight the value,
+1 = lockstep). The y-axis is the round-1 **spread** σ = standard deviation of
the behavioral value score across the candidate pool. A light vertical line
marks ρ = 0.

Each dot is colored by the **observed net endpoint move of the behavioral
value**, on a continuous diverging scale shown by the slim colorbar at right.
The move is the run's **final measured value minus its round-1 value**. (The
final measured value is a direct measurement, not an extrapolation: the corpus
stores each round's pre-training value, so the battery reading taken after the
last round's training is stored as that round's drift, and last value + drift
reconstructs it exactly.) **Red** = the value moved up, **blue** = it moved down, **gray**
at the middle = no net move. The color is a continuous diverging gradient with
a pale neutral midpoint — near-white at zero, blending linearly toward red
(up) or blue (down) — saturating at ±0.6, so lightness tracks |move|. Color is the **only** thing encoded on the
dots — every dot is drawn at a uniform size; there is no size encoding, no |ρ·σ|
contour background, and no cluster callouts. (Of the 67 plotted runs, 25 moved up
≥ +0.15, 25 moved down ≤ −0.15, and 17 sit within ±0.15 of no net move (a descriptive threshold only);
these counts are computed from the JSON at generation time and asserted to sum to
67.)

## The relationship the plane shows (the message, kept out of the figure)

The colors separate left–right by agreement, not up–down by spread. Blue
(**moved down**) dots concentrate at ρ < 0 (left of the vertical line, including
a column at ρ = −1 where the judge is forced to oppose the value); red (**moved
up**) dots concentrate at ρ > 0 (right of the line); the grayest dots (no net
move) hug ρ ≈ 0 or otherwise sit where selection is weak. In the writeup's model
each round nudges the value by about ρ·σ, so the sign of the move should track
the sign of the round-1 agreement and the magnitude should grow with spread —
which is what the red→gray→blue gradient across the plane makes visible.

## Provenance and caveats

One run = the tuple (cond, seed, source); the round-1 record supplies ρ, spread,
and value; the last record supplies value + drift. Of 74 total runs, **7 have an
undefined round-1 ρ and are not plottable on these two axes**, leaving **67
modelable runs** plotted — counts asserted in the generator. Of those 7: 3 have
zero within-pool spread (correlation is undefined), and 4 are random-selection
controls whose judge–value correlation is undefined by construction even though
their pool has nonzero spread. Mixed pools (base/peer compositions) also receive
a **pool shift (p − q)** from the outside candidate source that is not represented
on these two axes; it is a third force the plane does not show.

## Source data

- `experiments/spread_util_unified.json` — the `records` list (fields `rho`,
  `spread`, `value`, `drift`, `cond`, `seed`, `source`, `round`, `judge`,
  `composition`, `format`). n_records = 340, n_runs = 74, plotted = 67
  (25 up / 25 down / 17 flat).

Regenerate: `python3 synthesis-dial-plane.py` (stdlib only) from this directory.

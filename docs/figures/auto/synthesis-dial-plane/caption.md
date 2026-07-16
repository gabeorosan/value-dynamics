# synthesis-dial-plane

**Every run at its round-1 agreement and spread, colored by where its value
went.** The figure is deliberately spare: it places each run once and paints it
with a single three-way color code. All interpretation lives here.

## What the axes and marks are

The (agreement ρ, spread σ) plane, one dot per modelable run. The x-axis is the
round-1 **agreement** ρ = correlation, across the candidate pool, of the judge's
score with the behavioral value score (−1 = judge forced to fight the value,
+1 = lockstep). The y-axis is the round-1 **spread** σ = standard deviation of
the behavioral value score across the candidate pool. A light vertical line
marks ρ = 0.

Each dot is colored by **which of three categories** the run's observed net
endpoint move of the behavioral value falls into, where the move is computed per
run as (last-round value + that round's drift) − (round-1 value):

- **moved up** — move ≥ +0.15 — **red** (25 runs).
- **moved down** — move ≤ −0.15 — **blue** (25 runs).
- **no net move** — |move| < 0.15 — **light gray**, drawn smaller and more
  recessive (17 runs).

That is the only thing encoded on the dots. There is no dot-size encoding and no
continuous colorbar; the 0.15 threshold is the sole cut between categories.
(Counts are computed from the JSON at generation time and asserted to sum to the
67 plotted runs.)

## The relationship the plane shows (the message, kept out of the figure)

The colors separate left–right by agreement, not up–down by spread. Runs that
**moved down are concentrated at ρ < 0** (left of the vertical line, including a
column of blue dots at ρ = −1 where the judge is forced to oppose the value).
Runs that **moved up are concentrated at ρ > 0** (right of the line). Runs with
**no net move hug ρ ≈ 0 or otherwise sit where selection is weak**. In the
writeup's model each round nudges the value by about ρ·σ, so the sign of the
move should track the sign of the round-1 agreement and the magnitude should
grow with spread — which is what the three-color split makes visible here.

## Provenance and caveats

One run = the tuple (cond, seed, source); the round-1 record supplies ρ, spread,
and value; the last record supplies value + drift. Of 74 total runs, **7 have an
undefined round-1 ρ and are not plottable on these two axes**, leaving **67
modelable runs** plotted — counts asserted in the generator. Of those 7: 3 have
zero within-pool spread (correlation is undefined), and 4 are random-selection
controls whose judge–value correlation is undefined by construction even though
their pool has nonzero spread. Mixed pools (base/peer compositions) also receive
a **supplier shift** into the pool that is not represented on these two axes; it
is a third force the plane does not show.

## Source data

- `experiments/spread_util_unified.json` — the `records` list (fields `rho`,
  `spread`, `value`, `drift`, `cond`, `seed`, `source`, `round`, `judge`,
  `composition`, `format`). n_records = 340, n_runs = 74, plotted = 67
  (25 up / 25 down / 17 flat).

Regenerate: `python3 synthesis-dial-plane.py` (stdlib only) from this directory.

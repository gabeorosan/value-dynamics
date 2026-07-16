# synthesis-dial-plane

**Synthesis candidate A** (alternative views: intervention cards, pressure-vs-move line).

**Every run at its first-round state: agreement × spread, colored by the observed
move.** The figure text is orientation only — it tells you what you are looking at.
The interpretation is here.

## What the axes and marks are

The (agreement ρ, spread σ) plane, one dot per modelable run. The x-axis is the
round-1 **agreement** ρ = correlation, across the candidate pool, of the judge's
score with the behavioral value (−1 = judge forced to fight the value, +1 =
lockstep). The y-axis is the round-1 **spread** σ = standard deviation of the
behavioral value across the candidate pool. Dashed background curves are lines of
constant **per-round selection pressure** |ρ·σ| (labeled 0.02, 0.05, 0.1, 0.2) —
the writeup's model quantity, spread × agreement; the faint corner shading shows
the pressure growing toward the corners where both dials are large, and staying
low near either axis. Each dot is colored by the **observed net endpoint move of
the behavioral value**, computed per run as (last-round value + that round's
drift) − (round-1 value): blue = the value moved down, red = it moved up, gray =
|move| < 0.15 (no net move). Dot size also scales with |move|.

## The relationship the plane shows

Selection pressure in the writeup's model is spread × agreement: each round nudges
the value by about ρ·σ. The corners of this plane are where both dials are large —
and where runs actually moved. Runs move when they start away from **both** axes;
pressure |ρ·σ| ≈ 0 predicts standing still. In words, that is the finding: who
moved, and in which direction, tracks the round-1 pressure they started under.

## What each labeled cluster means (interpretation lifted out of the figure)

- **score-oracle cells** (ρ = −1, left edge): the judge is forced to fight the
  value, so every cell collapses (moves −0.4 to −0.8).
- **self-judge duel erosion** (mean ρ ≈ −0.28): the value slides down under a judge
  that mildly disagrees with it (moves ≈ −0.44).
- **injection twin pair** (mixed_reopen_qwen, ρ = −1, σ ≈ 0.31): the on-plane arm
  of the reopened-injection twin; its σ = 0 sibling is one of the unplottable runs
  (below). The on-plane arm sits at strong negative pressure and moves down ≈ −0.63.
- **peer / base invasion cells** (ρ ≈ +0.4 to +0.7, upper right): strong positive
  selection drives the value up (moves +0.6 to +0.8).
- **cautious / base rescue cells** (start near value 1.0): get pulled back down
  (moves −0.15 to −0.45).
- **self-only ρ ≈ 0 cells** (center): near-zero pressure — moves scatter both ways
  (training noise, not selection).

## Provenance and caveats

One run = the tuple (cond, seed, source); the round-1 record supplies ρ, spread,
and value. Of 74 total runs, **7 have an undefined round-1 ρ and are not plottable
on these two axes**, leaving **67 modelable runs** plotted — counts asserted in the
generator. Of those 7: 3 have zero within-pool spread (correlation is undefined),
and 4 are random-selection controls whose judge–value correlation is undefined by
construction even though their pool has nonzero spread. (The figure footnote states
this accurately; the earlier draft's "zero-spread" phrasing covered only 3 of the 7.)
The σ = 0 injection twin is one of the zero-spread three: with no spread there is no
selection and no move, and it held at value 1.00 — the boundary case that anchors
the "pressure ≈ 0 ⇒ no move" reading. Mixed pools (base/peer compositions) also
receive a **supplier shift** into the pool that is not represented on these two
axes; it is a third force the plane does not show.

## Source data

- `experiments/spread_util_unified.json` — the `records` list (fields `rho`,
  `spread`, `value`, `drift`, `cond`, `seed`, `source`, `round`, `judge`,
  `composition`, `format`). n_records = 340, n_runs = 74.

Regenerate: `python3 synthesis-dial-plane.py` (stdlib only) from this directory.

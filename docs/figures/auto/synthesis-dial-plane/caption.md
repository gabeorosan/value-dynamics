# synthesis-dial-plane

**Synthesis candidate A** (alternative views: intervention cards, pressure-vs-move line).

**Every run, placed by its first-round dials — pressure predicts who moved.**
The (agreement ρ, spread σ) plane, one dot per modelable run. The x-axis is the
round-1 **agreement** ρ = correlation, across the candidate pool, of the judge's
score with the behavioral value (−1 = judge forced to fight the value, +1 =
lockstep). The y-axis is the round-1 **spread** σ = standard deviation of the
behavioral value across the candidate pool. Dashed background curves are lines of
constant **per-round selection pressure** |ρ·σ| (0.02, 0.05, 0.1, 0.2), the
writeup's model quantity spread × agreement; the faint corner shading shows the
pressure growing toward the corners where both dials are large. Each dot is
colored by the **observed net endpoint move of the behavioral value**, computed
per run as (last-round value + that round's drift) − (round-1 value): blue = the
value moved down, red = it moved up, gray = |move| < 0.15 (no net move). Dot size
also scales with |move|. Landmarks are in plain words: the score-oracle cells at
ρ = −1 all collapse (moves −0.4 to −0.8); the self-judge duel erodes at ρ ≈ −0.28;
the self-only cluster near ρ ≈ 0 scatters both ways (training noise, not
selection); cautious/base-rescue cells that start near value 1.0 get pulled down;
and peer/base-injection runs at ρ ≈ +0.4 to +0.7 are driven up by +0.6 to +0.8.
The takeaway: runs move when they start away from **both** axes; pressure
|ρ·σ| ≈ 0 predicts standing still.

One run = the tuple (cond, seed, source); the round-1 record supplies ρ, spread,
and value. Of 74 total runs, 7 have an undefined round-1 ρ because their pool had
zero within-pool spread (correlation is undefined), leaving **67 modelable runs**
plotted — counts asserted in the generator. The σ = 0 injection twin is one of
those 7: it is shown off-plane at the bottom because ρ is undefined there, and it
held at value 1.00 (no spread, no selection, no move), reinforcing the takeaway.
Note that mixed pools (base/peer compositions) also receive a **supplier shift**
into the pool that is not represented on these two axes; it is a third force the
plane does not show.

## Source data

- `experiments/spread_util_unified.json` — the `records` list (fields `rho`,
  `spread`, `value`, `drift`, `cond`, `seed`, `source`, `round`, `judge`,
  `composition`, `format`). n_records = 340, n_runs = 74.

Regenerate: `python3 synthesis-dial-plane.py` (stdlib only) from this directory.

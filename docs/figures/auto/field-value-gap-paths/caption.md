# Runs through the (value, forecast-move) plane, over the model's flow

**What the plane is.** The horizontal axis is the behavioral value `v` a pool
expresses (fraction of the value battery, 0 to 1). The vertical axis is
`rho·sigma`, the model's forecast one-round move in that value: the agreement
`rho` among the pool's candidates times the within-prompt candidate spread
`sigma`. This product is the selector gap — how far one round of keeping the
top-scored candidates is expected to shift `v`. A bold line marks `rho·sigma =
0`, where the model forecasts no move.

**The background field is the model, not a fit to these paths.** At a grid of
`(v, rho·sigma)` points a light gray arrow shows the pure-selection one-round
move the unit recurrence predicts for a *self-only* pool: `Delta v = rho·sigma`,
so the arrow's head sits at `clip(v + rho·sigma, 0, 1)`. It points right above
the zero line, left below it, lengthens with distance from zero, vanishes on the
line, and is clipped at the walls `v = 0` and `v = 1`. The field is drawn from
the recurrence alone — no run in this figure was used to place it.

**How to read a path.** Each of the 71 runs is drawn as its trajectory through
this plane: a dot at its round-1 coordinate `(v_1, rho_1·sigma_1)`, thin
segments through the intermediate rounds' coordinates, and a filled arrowhead at
its final coordinate. The final `v` uses the endpoint convention of
`spread-rollout-bakeoff.py` `observed()` — the last round's `value + drift`, i.e.
where `v` lands *after* the last measured move — paired with the last available
`rho·sigma`. Rounds with undefined `rho` are skipped. Color encodes the
experiment family (per-family run counts in the key).

**What the paths show (interpretation).** Runs travel in the direction the
forecast move points: paths sitting above the zero line march right (rising
value), paths below march left (eroding value), and the up-right corner is the
runaway — high value with a still-positive forecast move that keeps pushing
toward the `v = 1` wall, where most endpoints pile up. As a run climbs, its
`rho·sigma` tends to collapse toward zero: spread is consumed as the pool
homogenizes, so the forecast move shrinks and the path flattens onto the zero
line near the wall. The `oracle & injection` runs (purple) are the visible
counter-current — several dive to strongly negative `rho·sigma` (down-left,
active erosion) before some recover.

**Caveat for the mixed-pool family.** The background field is the self-only
flow. `OLMo mixed-pool` runs (red) also feel a mixing pull `u·(s - v)` toward
the co-generator's value `s` with weight `u` (the supplier share) that this
field omits; their true one-round move is `rho·sigma + u·(s - v)`, so those
paths need not track the light arrows.

## Source data
- `experiments/spread_util_unified.json` — per-round records (`round`, `value`,
  `drift`, `rho`, `spread`, `organism`, `axis`, `judge`, `format`,
  `composition`, `source`; run identity `cond|seed|source`). All coordinates,
  the family assignment, and the 71-run / 290-point / 219-segment counts are
  computed live from this file by the generator. Four `(cond, seed, source)`
  groups carry two interleaved chains sharing the key; these are split by
  `value + drift -> next-round value` continuity.
- Endpoint / field conventions cross-checked against
  `docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py`
  (`observed()` and the unit recurrence `k = clip(pool + rho·sigma)`).

Generator: `field-value-gap-paths.py` (stdlib only; run from this directory).

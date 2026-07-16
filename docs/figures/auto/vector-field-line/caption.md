# The one-round move as a flow on the value line, by regime

Each row is a phase line for one selection regime. The blue arrows show the
model-implied one-round move at every value on the 0–1 line, using the writeup's
parameter-free unit recurrence **v → v + dv, with dv = u·(s − v) + rho·sigma**
and the within-prompt spread capped by the binary envelope **sigma ≤
√(v(1−v))**. Here **v** is the behavioral value (the share of the model's own
answers a judge scores at the trait, 0 = none, 1 = all), **u** is the supplier
share in the candidate pool, **s** the supplier's mean value, and **rho** the
agreement between the judge's ranking and the value (the per-unit-spread
selection differential). Arrow length is proportional to |dv| (a fixed pixel
scale, not the v-axis scale). A filled dot is an attracting fixed point (flow
converges onto it); an open dot is repelling (flow leaves it).

The reading:

- **Row 1 — self-only, judge with the value (rho > 0).** Every arrow points
  right and the move is longest mid-range (where the binary envelope is
  widest), shrinking to zero at the ends. The only attractor is **v = 1**:
  a self-reinforcing runaway to saturation. This is the pure-selection
  endpoint.
- **Row 2 — self-only, judge against the value (rho < 0).** The mirror image:
  flow runs to **v = 0**. Same dynamics, opposite sign of the judge–value
  agreement — a runaway to extinction of the trait.
- **Row 3 — self-only, rho ≈ 0.** No net move anywhere; the whole line is
  marginally fixed. With no agreement between judge and value, selection has no
  lever and the value neither climbs nor erodes.
- **Row 4 — mixed pool.** A supplier of share u at level s adds the pull
  u·(s − v), which competes with the selection term rho·sigma. The two cancel at
  an **interior balance v\*** (here ≈ 0.65, with the supplier level s marked):
  flow converges onto it from both sides and the runaway is replaced by an
  equilibrium held short of the endpoint. Blending a fixed supply of moderate
  answers converts a runaway into a controllable set point.

Overlaid dark zig-zag arrows are **observed** consecutive one-round moves read
live from real runs (one representative run per regime; row 4 shows two runs, one
approaching v\* from above and one from below). They scatter around the implied
mean flow but follow its direction: rightward in row 1, leftward in row 2, inward
toward the balance point in row 4.

## Source data

- Flow-field curves: the unit recurrence with representative per-regime
  parameters printed in each row label (rho = +0.5 / −0.5 / ≈0; row 4 u = 0.5,
  s = 0.55, rho = +0.1). These illustrate the dynamics; they are not fitted to any
  single run.
- Observed moves: `experiments/spread_util_unified.json`, trajectory convention
  from `docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py`
  (first point = round-1 own value, then each later point = that round's
  value + drift). Runs: row 1 `evolving_self` seed 2 (Qwen, self-only, risk axis);
  row 2 `judge_opposition_oracle` seed 101 (Qwen, self-only, self-report axis);
  row 4 `h2h_base_rescue` seed 57 and `h2h_erode_self` seed 61 (OLMo, base-mixed
  pool, u = 0.5).
- Generator: `docs/figures/auto/vector-field-line/vector-field-line.py`
  (stdlib only; regenerate with `python3 vector-field-line.py`).

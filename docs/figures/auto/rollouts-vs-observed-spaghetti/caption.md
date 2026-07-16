# Sampled rollouts and observed trajectories, three experiment families

Three columns, one per value-dynamics family with many runs; each column is a
**stacked pair of panels on identical axes and identical line styling**, so the
reader compares two bundles as texture against texture rather than color against
color. `x` = selection round, `y` = the behavioral value (0–1, the measured
propensity the selection loop is acting on). The **top** panel of each column
draws **exactly one simulated rollout per run**, rolled forward from that run's
**round-1 pool state** — own candidate mean `q`, within-prompt spread `sigma`
(`own_spread`), agreement `rho`, behavioral value `v`, and, for mixed pools,
supplier share `u` and supplier mean `s` — under the committed parameter-free
**unit recurrence** (`kept = clip(pool + rho*sigma)`, `pool = (1-u)q + u·s`,
next value = kept) plus the committed **staged-noise** recipe: a Gaussian
selector-gap innovation, a generated-mean update, an agreement drift, and readout
observation noise `sqrt(v(1-v)/n)`. The **bottom** panel draws the trajectories
actually observed for those same runs (measured value each round, one line per
run). Every noise scale is rebuilt leave-one-condition-out from the committed
records (stdlib mean/std, seeded `random.Random`); `rollout()`,
`residual_scales()`, and `meas_sd()` are copied verbatim from
`docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py`, so no noise
parameter is invented here. The figure invites a direct read within each column:
whether the observed bundle has the same texture (spread, drift, fan-out) as a
single-draw simulated bundle from the same starting states. In Panel A (Qwen
risk grid) and Panel C (OLMo mixed-pool) the two bundles look alike; in Panel B
(OLMo risk self-only) several observed runs climb toward 1 more sharply than the
staged-noise draws, the family where the recurrence's spread is most strained.

**Families and honest counts.** Exactly one simulated draw per run; a run seeds
a draw only if it has a defined round-1 agreement reading (`rho`). A — Qwen risk
grid, 16 runs, 12 seed a simulated draw (self-only pool; judges self / base /
frozen copy / random). B — OLMo risk self-only, 23 runs, 22 seed a draw
(frozen-judge grid + press schedules; run lengths 4 and 8 rounds). C — OLMo
mixed-pool interventions, 20 runs, 20 seed a draw (base- and peer-mixed invade /
erode / rescue / oracle). Judge-swap runs and self-report-axis runs are out of
scope for this figure; the three risk families above are the ones with the most
runs.

**Source data.** `experiments/spread_util_unified.json` (per-run round records:
organism, axis, judge, format, seed, round, value, spread, rho, and pool state).
Simulator provenance: `docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py`
(committed unit recurrence + staged-noise residual pools). Generator:
`rollouts-vs-observed-spaghetti.py` (stdlib only; run
`python3 rollouts-vs-observed-spaghetti.py` from this directory).

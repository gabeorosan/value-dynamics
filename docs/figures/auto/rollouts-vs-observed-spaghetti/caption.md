# Sampled rollouts and observed trajectories, three experiment families

Each of the three panels overlays a **simulated bundle** (light-gray lines) and
the **observed bundle** (blue lines) for one family of value-dynamics runs, with
`x` = selection round and `y` = the behavioral value (0–1, the measured
propensity the selection loop is acting on). The gray lines are rollouts drawn
forward from every run's **round-1 pool state** — own candidate mean `q`,
within-prompt spread `sigma` (`own_spread`), agreement `rho`, behavioral value
`v`, and, for mixed pools, supplier share `u` and supplier mean `s` — under the
committed parameter-free **unit recurrence** (`kept = clip(pool + rho*sigma)`,
`pool = (1-u)q + u·s`, next value = kept) plus the committed **staged-noise**
recipe: a Gaussian selector-gap innovation, a generated-mean update, an
agreement drift, and readout observation noise `sqrt(v(1-v)/n)`. Every noise
scale is rebuilt leave-one-condition-out from the committed records (stdlib
mean/std, seeded `random.Random`); the `rollout()`, `residual_scales()`, and
`meas_sd()` functions are copied verbatim from
`docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py`, so no noise
parameter is invented here. The blue lines are the trajectories actually
observed for those same runs (measured value each round, one line per run). The
figure invites a direct read: whether the observed bundle looks like a sample
drawn from the simulated bundle. In Panel A (Qwen risk grid) and Panel C
(OLMo mixed-pool) the observed lines fall inside the gray envelope; in Panel B
(OLMo risk self-only) several observed runs climb toward 1 more sharply than the
staged-noise cloud spreads, the family where the recurrence's spread is most
strained.

**Families and counts.** A — Qwen risk grid, 16 runs, 48 simulated draws
(self-only pool; judges self / base / frozen copy / random). B — OLMo risk
self-only, 23 runs, 44 simulated draws (frozen-judge grid + press schedules;
run lengths 4 and 8 rounds). C — OLMo mixed-pool interventions, 20 runs, 60
simulated draws (base- and peer-mixed invade / erode / rescue / oracle). A few
runs lack a round-1 agreement reading (`rho`) and therefore contribute an
observed line but no simulated draws — panel labels report the exact seeded-draw
count per panel. Judge-swap runs and self-report-axis runs are out of scope for
this figure; the three risk families above are the ones with the most runs.

**Source data.** `experiments/spread_util_unified.json` (per-run round records:
organism, axis, judge, format, seed, round, value, spread, rho, and pool state).
Simulator provenance: `docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py`
(committed unit recurrence + staged-noise residual pools). Generator:
`rollouts-vs-observed-spaghetti.py` (stdlib only; run
`python3 rollouts-vs-observed-spaghetti.py` from this directory).

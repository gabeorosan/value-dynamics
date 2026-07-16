# Simulated rollout ensembles vs observed trajectories, by condition

Small-multiples check of the staged-noise rollout model against the runs it is
meant to reproduce. Each panel is one **condition cell** — a single organism x
axis x judge x format x composition holding one experimental condition, with
several seeds. Cells were chosen for being homogeneous (single condition,
self-only pool, all four selection rounds) and having at least three seeds:

| Panel | organism · axis · judge · format | condition | seeds |
|---|---|---|---|
| top-left | Qwen · risk · self-judge (re-copied each round) · vs reference | `evolving_self` | 4 |
| top-mid | Qwen · risk · frozen base-model judge · vs reference | `frozen_base` | 4 |
| top-right | Qwen · risk · frozen self-copy judge · vs reference | `frozen_copy_r0` | 4 |
| bottom-left | OLMo · risk · frozen cautious-copy judge · vs reference | `frozen_cons_r0` | 4 |
| bottom-mid | OLMo · risk · frozen base-model judge · vs reference | `frozen_base` | 6 |

Within each panel the **simulated ensemble** is the parameter-free unit
recurrence rolled forward from each seed's round-1 pool state only — own
candidate mean, within-prompt spread sigma, agreement rho, and behavioral value
— with noise added only where the measurement implies it (the committed
`unit_core_selector_q_observation_rho_persistence_gaussian` staged-noise recipe:
selector-gap innovation, generated-mean update, agreement drift, and per-round
value-measurement observation noise, every scale rebuilt leave-one-condition-out
from the committed records). The shaded region is the pooled 10-90% quantile
band and the dashed line the pooled median over 300 draws per seed (all seeds
pooled within the panel). The thin dark lines are the **observed** trajectories,
one per seed, all in the same ink; the y-axis is the value on 0-1 by selection
round. The simulation reads only round 1 and is never fitted to the later
rounds shown, so a panel where the dark lines stay inside the band is
out-of-sample agreement, not a fit. Note the two OLMo frozen-base seeds that
climb to 0.69 and 0.80 and escape the band near the endpoint — a real minority
of runs the located-noise band undercovers, not an artifact.

The aggregate box states the committed leave-one-condition-out bake-off over all
45 held-out runs: the deterministic median alone covers 22% of endpoints at the
nominal-80% band (CRPS 0.135), rising to 89% coverage (CRPS 0.092) once the
staged noise is added.

**Source data.**
- Per-round trajectory + round-1 state: `experiments/spread_util_unified.json`
  (records; fields organism, axis, judge, format, composition, cond, seed,
  round, value, drift, own_mean, own_spread, rho, next_value_measurement_n).
- Aggregate coverage/CRPS line: `experiments/trajectory_adjustment_bakeoff.json`
  (`primary_selection_driven_plus_swap.unit_core_deterministic` and
  `...selector_q_observation_rho_persistence_gaussian`), asserted in the
  generator.
- Simulation recipe copied verbatim from the committed sibling generator
  `docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py`.

Regenerate: `python3 rollouts-vs-observed-panels.py` from this directory
(stdlib only).

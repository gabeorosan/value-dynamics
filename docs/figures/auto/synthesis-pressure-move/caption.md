**One number from the first round calls the whole run.** The figure text is
orientation only — it names the two axes, the families, and the tally; the
reading of the picture lives here.

Each dot is one committed run, reduced to two numbers. The **horizontal**
position is the parameter-free model's *predicted first-round pull*, computed
from that run's round-1 record as `(pool_mean + rho · spread) − value`: the pool
mean plus the price-of-selection term (the round-1 selector–value correlation
`rho` times the round-1 candidate spread), minus where the organism's behavior
already sat. A positive pull points toward more risk-taking (or, for the
insecure-code organism, toward calling its own code insecure); a negative pull
points back toward the safe wall. The **vertical** position is the run's
*observed net movement* over all its rounds, `(final value) − (round-1 value)`,
where the final value is the last round's behavioral value plus that round's
drift. Color marks the five experiment families of the writeup's run table; the legend
key alone identifies each family and gives its plotted-run count.

Underneath the dots is the **vector field the model implies**: faint light-blue
vertical arrows drawn at regular pull positions along the horizontal axis, each
running from `y = 0` to `y = x` — the movement the model predicts if observed net
movement equals predicted pull. Arrows point up where the pull is positive (toward
risk/insecurity) and down where it is negative, and grow in length with the size
of the pull, so their tips trace the `y = x` diagonal as the field's envelope. The
arrows are recessive by design (thin, light, behind every other element); the dots
and the dashed `y = x` line sit on top unchanged.

**What the picture shows** (the interpretation cut from the figure face): the
sign of the first-round push calls the direction of the whole run — dots sit in
the two same-sign quadrants far more than the two opposite-sign ones. The dashed
diagonal is `y = x`, one round's predicted pull fully realized; the large
multi-round runs land *beyond* it in the same sign, because the selection step
recurs each round and pushes the endpoint further toward the wall. Near the
`x ≈ 0` column runs stand still or wander — small predicted pull, no committed
direction (training noise). **The headline evidence** (formerly a box on the
figure face, now stated here): among the **58 non-swap runs, 43 moved by at least
0.15** in net value, and the sign of the first-round pull matched the direction
of the whole run in **39 of 43** — a display-level tally over the plotted per-run
data. The **9 judge-swap runs** are shown hollow and excluded from this tally.
Pearson correlation of the plotted x and y is **0.79** across all 67 runs.

**Which runs are excluded and why:** 7 runs with a null round-1 `rho` are dropped
(no first-round pull is defined for them). 9 judge-schedule runs are drawn as
hollow circles and excluded from the tally because the judge is replaced mid-run,
so a first-round pull cannot be expected to call the endpoint. That leaves 74
committed run-groups → 67 plotted (58 solid + 9 hollow), 43 of the solid runs
moving ≥ 0.15.

**Source data:** `experiments/spread_util_unified.json` (field `records`; per-run
round-1 `pool_mean`, `rho`, `spread`, `value` and per-round `value` + `drift`).
Family assignment follows the five families of the run table in
`docs/writeup_value_dynamics_sprint.md` (Qwen risk grid 12 / OLMo risk grid +
schedules 21 / OLMo mixed-pool 18 / oracle & injection 8 / Qwen insecure-code 8).
Regenerate with `python3 synthesis-pressure-move.py` from this directory (stdlib
only).

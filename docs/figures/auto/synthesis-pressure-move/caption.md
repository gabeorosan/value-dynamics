**One number from the first round calls the whole run.** *(Synthesis candidate C — alternatives: dial-plane map, intervention cards.)*

Each dot is one committed run, reduced to two numbers. The horizontal position
is the parameter-free model's **predicted first-round pull**, computed from that
run's round-1 record as `(pool_mean + rho · spread) − value`: the pool mean plus
the price-of-selection term (the round-1 selector–value correlation `rho` times
the round-1 candidate spread), minus where the organism's behavior already sat.
A positive pull points toward more risk-taking (or, for the insecure-code
organism, toward calling its own code insecure); a negative pull points back
toward the safe wall. The vertical position is the run's **observed net
movement** over all its rounds, `(final value) − (round-1 value)`, where the
final value is the last round's behavioral value plus that round's drift. Color
marks the five experiment families of the writeup's run table, direct-labeled by
cluster; a compact key on the right gives the plotted-run count per family. The
dashed diagonal is `y = x` (one round's predicted pull, fully realized); the
large multi-round runs land *beyond* it in the same sign, because the selection
step recurs each round and pushes the endpoint further toward the wall. Near the
`x ≈ 0` column runs stand still or wander — small predicted pull, no committed
direction (training noise). The evidence line is a display-level tally over the
plotted per-run data: among the 58 non-swap runs, 43 moved by at least 0.15 in
net value, and the sign of the first-round pull matched the direction of the
whole run in **39 of 43**. Seven runs with a null round-1 `rho` are dropped;
nine judge-schedule runs (the judge is replaced mid-run, so a first-round pull
cannot call the endpoint) are drawn as hollow circles and excluded from the
tally. Pearson correlation of the plotted x and y is 0.79 across all 67 runs.

**Source data:** `experiments/spread_util_unified.json` (field `records`;
per-run round-1 `pool_mean`, `rho`, `spread`, `value` and per-round `value` +
`drift`). Family assignment follows the five families of the run table in
`docs/writeup_value_dynamics_sprint.md` (16 / 21 / 18 / 11 / 8 runs). Regenerate
with `python3 synthesis-pressure-move.py` from this directory (stdlib only).

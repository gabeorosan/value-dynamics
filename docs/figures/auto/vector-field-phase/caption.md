# Phase plot: round-to-round value change vs current value (risk axis)

Each dot is one round-to-round transition inside a binary risk-axis run
(`axis == "risk"`): its horizontal position is the behavioral value **v at round
r** (fraction of the value-measurement battery scored on the risk-flavored side,
0 to 1), and its vertical position is the **observed one-round change**,
value(round r+1) minus value(round r). Dots are colored by the selector-value
agreement **rho measured at round r** on a diverging scale — red for positive
agreement (the selector kept candidates that pull value up), blue for negative
(pulls down), gray near zero; light neutral gray where rho is undefined at round
r. 221 transitions from 59 risk-axis runs are plotted; 25 have undefined rho
(gray) and 17 realized moves fall beyond the self-only envelope.

The light curves are the model's field, not a fit: on the binary axis the
within-prompt candidate spread has the Bernoulli envelope
**sigma_max(v) = sqrt(v(1−v))**, so for a self-only pool the largest one-round
move the selector can make at value v is **rho · sigma_max(v)**. The four curves
draw that maximum for rho = +1, +0.5, −0.5, −1; the bold line at y = 0 is the
equilibrium (no move); the dashed verticals at v = 0 and v = 1 are the walls.

How to read it. The envelopes form a lens: the available move is widest
mid-range and pinched to zero at both walls, because sigma_max(v) → 0 as v → 0
or 1. Red dots (rho > 0) sit predominantly above the zero line and blue dots
below it — the sign of the one-round change tracks the sign of agreement, which
is the phase-space signature of the runaway/equilibrium split. Under sustained
positive rho every interior move is upward, so the state flows right toward the
v = 1 wall; under sustained negative rho it flows left toward v = 0. The walls
are therefore absorbing equilibria: once value reaches them the envelope vanishes
and no further selection-driven move is possible. The zero line is the interior
balance only when agreement averages out (mixing a frozen supplier into the pool
adds an interior fixed point away from the walls; that is off this self-only
figure). The faint vertical up/down ticks at a few grid values are a recessive
flow cue showing move direction (red up for rho > 0, blue down for rho < 0) and
the lens taper. The 17 moves outside the rho = ±1 curves are single realized
transitions pushed past the self-only maximum by located measurement noise and,
in a few runs, pool mixing — expected, and small relative to the envelope.

Source data: `experiments/spread_util_unified.json` (per-round records keyed
`cond|seed|source`; risk-axis subset). All transitions are computed live from
consecutive rounds' `value` fields; the transition convention matches the
`observed()` helper in
`docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py` (per-record
`drift` equals value(r+1) − value(r) to within 1e-4). The envelope curves are
analytic. Regenerate with `python3 vector-field-phase.py`.

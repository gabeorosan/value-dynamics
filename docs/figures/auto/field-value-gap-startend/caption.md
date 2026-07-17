# Each run's start and end in the (value, forecast-move) plane

**What the plane is.** In every panel the horizontal axis is a run's behavioral
value *v* (the fraction of choices that are risk-seeking, or that describe
insecure code), on its natural 0-to-1 scale with hard walls at both ends. The
vertical axis is the **forecast one-round move** ρ·σ — the round's judge/value
agreement ρ times the within-prompt candidate spread σ (`own_spread`) — over the
fixed range −0.36 to +0.42 with a bold y = 0 (no-move) line. ρ·σ is exactly the
selection term of the project's parameter-free unit recurrence: for a self-only
pool the next round's value moves by Δ*v* = ρ·σ.

**Why one panel per family.** The single-panel version overlaid all 74 runs; this
version splits them into one panel per committed experiment family (Qwen risk grid
16 runs; OLMo risk grid + judge schedules 21 runs, of which the 9 judge-swap runs are omitted; OLMo mixed-pool
interventions 18 runs; oracle & injection 11 runs; Qwen insecure-code loops 8
runs), arranged 3-wide × 2-tall with the sixth slot holding the shared key. Every
panel shares the same axes, walls, y = 0 line, and background field, and draws only
its own family's run arrows in that family's color, so families no longer occlude
one another.

**What each arrow is.** One straight arrow per run, from its round-1 coordinates
(*v*₁, ρ₁·σ₁) at the open dot to its final-round coordinates (*v*_end, last ρ·σ)
at the filled arrowhead — no intermediate rounds are drawn. The endpoint value
follows the `observed()` convention (last round's value plus its drift — i.e. the
final measured value). The nine
scheduled-judge-swap runs (all inside the OLMo risk-grid family) are **omitted
from this candidate**: a mid-run judge change has no straight start-to-end
representation on a one-round field (the corpus records label those runs'
judge as the constant string `schedule`, so the swap round is not carried in
the data file either; candidates L and M draw those runs round-by-round
instead). Endpoints (and a few starts) whose agreement ρ was
unmeasurable — overwhelmingly because σ had already collapsed to 0 — are placed at
forecast move 0.

**The background field now has a vertical component.** The faint gray field draws
the recurrence Δ*v* = ρ·σ. From a grid point (*v*, *y*) the schematic arrow's
horizontal step is Δ*v* = *y*·0.55 (clipped at the walls); on the risk-axis panels
it also carries a **vertical step** Δ*y* = *y*·(env(*v*+Δ*v*)/env(*v*) − 1), where
env(*v*) = √(*v*·(1−*v*)) is the binary envelope. So as the value moves toward a
wall the envelope contracts, σ and hence ρ·σ bend down toward zero, and the arrows
visibly curl toward the no-move line near *v* = 0 and *v* = 1; near *v* = 0.5 the
envelope is flat and the field is nearly horizontal. This is the committed identity
`V_within = q(1−q) − Var(prompt means)`: pool q(1−q) explains within-prompt spread
at R² 0.955 (`docs/ANALYSIS_LEDGER.md`, spread-value-centrality row), and the
envelope-predicted per-round Δ(ρσ) correlates +0.36 with the observed Δ(ρσ) over
the 170 in-range risk transitions
(`scripts/analysis_field_vertical_component.py` →
`experiments/field_vertical_component.json`). Arrows whose
start or end sits within 0.02 of a wall are dropped to keep env(*v*) > 0.

**The self-description panels bend by a measured coupling, not an assumption.**
A flat field would assert unestablished dynamics just as much as a bent one, so
the vertical component was measured per axis (same script). On the 27
continuous-axis transitions, Δ(ρσ) = −0.021 − 0.173·Δ*v* at r = −0.567: when
selection moves the value, the forecast-move coordinate shrinks in proportion —
the self-consumption mechanism as field geometry — while the envelope form
predicts the wrong sign there (corr −0.56), confirming its binary-only scope.
The Qwen insecure-code loops panel (all self-report axis) and the oracle &
injection panel (mixed: 4 risk + 7 self-report runs) therefore draw their
arrows with the measured slope, loaded live from the JSON, and carry the
in-panel note "field bend: the measured continuous-axis coupling
Δ(ρ·σ) ≈ −0.17·Δv". The additional small per-round downward drift (intercept
−0.021) is reported in `docs/report_field_vertical_component.md` and not
drawn (an arrow at *y* = 0 should vanish, not drift). Twenty-seven transitions
is a first measurement, not a law.

**How to read it.** Within each panel most arrows land near the ρ·σ = 0 line, and
many pile against the walls: as a loop runs, σ is consumed (the pool self-consumes
toward duplicates) or the value pins against a wall, so the round-to-round forecast
move shrinks toward zero by the end. The mixed-pool families (OLMo mixed-pool
interventions, oracle & injection) additionally feel a mixing pull toward the
supplier mean that this self-only field does not show, so their arrows are not
expected to track it.

Every coordinate is computed live (stdlib) at build time; the generator asserts the
74-run / 340-record totals, the five family counts (16 / 21 / 18 / 11 / 8), the
nine-swap count, and that exactly the three all-risk families are pure risk-axis.

**Source data:** `experiments/spread_util_unified.json` (per-round records:
`value`, `drift`, `rho`, `own_spread`, `axis`; family from
organism/axis/judge/format/composition). Endpoint convention from
`docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py` `observed()`;
family names from `docs/figures/auto/run-inventory/run-inventory.py`; envelope
identity and its R² 0.955 / risk-axis-only scope from `docs/ANALYSIS_LEDGER.md`
(spread-value-centrality row). Generator: `field-value-gap-startend.py` (regenerate
with `python3 field-value-gap-startend.py`).

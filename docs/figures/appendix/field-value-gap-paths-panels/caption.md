# Each run's round-by-round path in the (value, forecast-move) plane — candidate L

**What the plane is.** In every panel the horizontal axis is a run's behavioral
value *v* (the fraction of choices that are risk-seeking, or that describe insecure
code), on its natural 0-to-1 scale with hard walls at both ends. The vertical axis
is the **forecast one-round move** ρ·σ — the round's judge/value agreement ρ times
the within-prompt candidate spread σ (`own_spread`) — over the fixed range −0.36 to
+0.42 with a bold y = 0 (no-move) line. ρ·σ is exactly the selection term of the
project's parameter-free unit recurrence: for a self-only pool the next round's
value moves by Δ*v* = ρ·σ.

**Why one panel per family.** The 74 runs split into one panel per committed
experiment family (Qwen risk grid 16 runs; OLMo risk grid + judge schedules 21 runs,
9 dashed; OLMo mixed-pool interventions 18 runs; oracle & injection 11 runs; Qwen
insecure-code loops 8 runs), arranged 3-wide × 2-tall with the sixth slot holding
the shared key. Every panel shares the same axes, walls, y = 0 line, and background
field, and draws only its own family's runs in that family's color.

**What each run is (the candidate-L difference).** The companion candidate
`field-value-gap-startend` draws ONE straight arrow per run, from round 1 to the
final round, skipping every intermediate round. But the background field encodes a
**one-round** move (Δ*v* = ρ·σ per round), so a straight multi-round arrow is a
different kind of object than the field arrows it is overlaid on — and for the 9
scheduled-judge-swap runs, whose ρ·σ shifts mid-run, a single straight arrow is
doubly misleading. **Candidate L instead draws each run as its actual round-by-round
path:** a polyline through every round's (*v*ᵣ, ρᵣ·σᵣ) coordinate — an open dot at
round 1, a small filled vertex at each intermediate round, and a filled arrowhead on
the final segment. The endpoint value follows the same `observed()` convention as
the startend candidate: the last round's value plus its drift on *x*, with the last
round's ρ·σ on *y* (intermediate vertices carry no drift). Rounds whose agreement ρ
is unmeasurable — overwhelmingly because σ had already collapsed to 0 — are plotted
at forecast move 0. The design rationale: with paths, the overlaid data and the
background field become the **same kind of object** (a one-round move), so the eye
compares each segment directly against the field vector at that point.

**The scheduled-judge-swap runs are dashed, and the swap round is not marked.** The
9 judge-schedule runs (all inside the OLMo risk-grid family) draw as normal
round-by-round paths in the family color but dashed. **The swap round is not
identifiable from this file:** for every schedule run the `judge` field reads the
constant string `"schedule"` on every round (verified by an assertion in the
generator), so no per-round swap point exists to mark. The key and this caption say
so; the dashed style flags only that these runs contain a mid-run judge change the
self-only field omits.

**The background field (identical to the startend candidate).** The faint gray field
draws the recurrence Δ*v* = ρ·σ. From a grid point (*v*, *y*) the schematic arrow's
horizontal step is Δ*v* = *y*·0.55 (clipped at the walls); on the three all-risk-axis
panels (Qwen risk grid; OLMo risk grid + judge schedules; OLMo mixed-pool
interventions) it also carries a **vertical step** Δ*y* = *y*·(env(*v*+Δ*v*)/env(*v*)
− 1), where env(*v*) = √(*v*·(1−*v*)) is the binary envelope: as the value moves
toward a wall the envelope contracts and ρ·σ bends toward zero; near *v* = 0.5 the
envelope is flat and the field is nearly horizontal. This is the committed identity
`V_within = q(1−q) − Var(prompt means)` (pool q(1−q) explains within-prompt spread at
R² 0.955, `docs/ANALYSIS_LEDGER.md` spread-value-centrality row; the
envelope-predicted per-round Δ(ρσ) correlates +0.36 with the observed Δ(ρσ) over the
170 in-range risk transitions,
`scripts/analysis_field_vertical_component.py` → `experiments/field_vertical_component.json`).
The two panels containing continuous self-description runs (Qwen insecure-code loops,
all self-report; oracle & injection, mixed 4 risk + 7 self-report) instead bend by
the **measured** continuous-axis coupling Δ(ρ·σ) ≈ −0.17·Δ*v* (slope −0.1729,
r = −0.567 over 27 transitions), loaded live from the same JSON — a flat field would
assert unestablished dynamics just as much as a bent one. Twenty-seven transitions is
a first measurement, not a law.

**How to read it.** Within each panel most paths wander near the ρ·σ = 0 line and
pile against the walls: as a loop runs, σ is consumed (the pool self-consumes toward
duplicates) or the value pins against a wall, so the per-round forecast move shrinks
toward zero by the end. Each visible kink is one round; compare a path segment's
direction against the faint field vector beneath it to see where a run tracks the
self-only recurrence and where it departs (the mixed-pool families additionally feel
a mixing pull toward the supplier mean this self-only field does not show).

Every coordinate is computed live (stdlib) at build time; the generator asserts the
74-run / 340-record totals, the five family counts (16 / 21 / 18 / 11 / 8), the
nine-swap count, that all swaps sit in the OLMo risk-grid family, that the schedule
runs' `judge` field is constant, and that exactly the three all-risk families are
pure risk-axis.

**Source data:** `experiments/spread_util_unified.json` (per-round records: `value`,
`drift`, `rho`, `own_spread`, `axis`, `judge`; family from
organism/axis/judge/format/composition). Endpoint convention from
`docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py` `observed()`;
family names from `docs/figures/auto/run-inventory/run-inventory.py`; envelope
identity and its R² 0.955 / risk-axis-only scope from `docs/ANALYSIS_LEDGER.md`
(spread-value-centrality row); measured continuous-axis slope from
`experiments/field_vertical_component.json`. This is candidate L, an alternative to
`docs/figures/auto/field-value-gap-startend/`. Generator:
`field-value-gap-paths-panels.py` (regenerate with `python3
field-value-gap-paths-panels.py`).

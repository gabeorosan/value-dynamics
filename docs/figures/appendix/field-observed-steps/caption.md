# Every observed one-round move in the (value, forecast-move) plane

**Candidate M — the most direct field test.** The background gray field draws the
model's *predicted one-round move* from every coordinate (Δ value = ρ·σ), so the
honest data overlay is also a set of *one-round moves*, not a run's whole
start-to-end displacement. This figure (field candidate M, an alternative to
`field-value-gap-startend`) draws every observed **round transition** as its own
short colored arrow. Because the observed arrows and the model arrows are now the
same object — one round long, in the same units — each panel is a direct
observed-vs-model vector-field comparison: does the measured round-to-round move
point where the model's field says it should?

**The plane.** Horizontal axis is a run's behavioral value *v* (the fraction of
choices that are risk-seeking, or that describe insecure code), on its natural
0-to-1 scale with hard walls at both ends. Vertical axis is the **forecast
one-round move** ρ·σ — the round's judge/value agreement ρ times the within-prompt
candidate spread σ (`own_spread`) — over −0.36 to +0.42 with a bold y = 0 (no-move)
line. ρ·σ is exactly the selection term of the project's parameter-free unit
recurrence: for a self-only pool the next round's value moves by Δ*v* = ρ·σ.

**What each arrow is.** For each consecutive round pair (r, r+1) within a run, one
arrow from (*v*_r, ρ_r·σ_r) to (*v*_{r+1}, ρ_{r+1}·σ_{r+1}). The **last**
transition's endpoint value uses the `observed()` convention (last round's value
plus its drift — the final measured value); interior endpoints use the next
record's raw value. There are no dots — an arrow is a move, and its tail is its
start. Rounds whose agreement ρ is unmeasurable (overwhelmingly because σ had
already collapsed to duplicates) are placed at forecast move 0. Arrows are drawn
in the family color at width 1.6, opacity 0.8, with 5px arrowheads; the busiest
panel (OLMo risk grid, 107 transitions) stays legible at these weights.
Judge-swap-run transitions are **dashed** — every transition of a run whose judge
schedule swaps mid-loop, all inside the OLMo risk-grid family.

**Per-panel counts.** One panel per committed experiment family, 3-wide × 2-tall
with the sixth slot holding the shared key. Each title reports its live transition
and run counts: Qwen risk grid 48 transitions / 16 runs; OLMo risk grid + judge
schedules 107 / 21 (63 transitions dashed); OLMo mixed-pool interventions 54 / 18;
oracle & injection 33 / 11; Qwen insecure-code loops 24 / 8. The generator asserts
the transition total (266) equals the file's total consecutive-pair count
(`n_records` − `n_runs` = 340 − 74), and that the five per-panel totals sum to it.

**The background field.** From a grid point (*v*, *y*) the model's schematic arrow
steps the value by Δ*v* = *y*·0.55 (clipped at the walls). On the three all-risk
panels it also carries a **vertical step** Δ*y* = *y*·(env(*v*+Δ*v*)/env(*v*) − 1),
env(*v*) = √(*v*·(1−*v*)) the binary envelope: as the value nears a wall the
envelope contracts, so ρ·σ bends toward zero; near *v* = 0.5 the field is nearly
horizontal. This is the committed identity `V_within = q(1−q) − Var(prompt means)`
(pool q(1−q) explains within-prompt spread at R² 0.955;
`docs/ANALYSIS_LEDGER.md`, spread-value-centrality row). The two self-description
panels (Qwen insecure-code loops, all self-report; oracle & injection, mixed 4
risk + 7 self-report) instead bend by the **measured** continuous-axis coupling
Δ(ρ·σ) ≈ −0.17·Δ*v* (r = −0.567 over 27 continuous-axis transitions), loaded live
from the JSON, since a flat field would assert unestablished dynamics just as much
as a bent one. A first measurement, not a law.

**Source data.** `experiments/spread_util_unified.json` (per-round records:
`value`, `drift`, `rho`, `own_spread`, `axis`; family from
organism/axis/judge/format/composition; endpoint convention from
`docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py` `observed()`).
Vertical field component (envelope + measured self-report slope) from
`experiments/field_vertical_component.json`
(`scripts/analysis_field_vertical_component.py`). Family names from
`docs/figures/auto/run-inventory/run-inventory.py`. Regenerate with
`python3 field-observed-steps.py`.

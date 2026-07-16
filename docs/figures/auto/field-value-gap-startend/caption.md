# Each run's start and end in the (value, forecast-move) plane

**What the plane is.** The horizontal axis is a run's behavioral value *v* (the
fraction of choices that are risk-seeking, or that describe insecure code), on
its natural 0-to-1 scale with hard walls at both ends. The vertical axis is the
**forecast one-round move** ρ·σ — the round's judge/value agreement ρ times the
within-prompt candidate spread σ (`own_spread`). ρ·σ is exactly the selection
term of the project's parameter-free unit recurrence: for a self-only pool the
next round's value moves by Δ*v* = ρ·σ. The faint gray background field draws
that recurrence directly — a horizontal reference arrow at each grid point,
pointing **right above the zero line** (value is pulled up) and **left below it**
(value is pulled down), lengthening away from ρ·σ = 0 and vanishing on it, and
clipped at the walls. Field arrows are schematic (length ∝ ρ·σ, not to axis
scale); the run arrows are in true coordinates.

**What each arrow is.** One straight arrow per run, from its round-1 coordinates
(*v*₁, ρ₁·σ₁) at the open dot to its final-round coordinates (*v*_end, last ρ·σ)
at the filled arrowhead — no intermediate rounds are drawn. The endpoint value
follows the `observed()` convention (last round's value plus its drift). Color is
the experiment family (the five committed run-inventory names). The nine
scheduled-judge-swap runs (all inside the OLMo risk-grid family) are drawn hollow
— dashed, open arrowhead — because the self-only field on this plane omits the
mid-run judge swap they experience.

**How to read it.** Most arrows land near the ρ·σ = 0 line, and many pile up
against the *v* = 0 and *v* = 1 walls: as a loop runs, the candidate spread σ is
consumed (the pool self-consumes toward duplicates) or the value pins against a
wall, so the round-to-round forecast move shrinks toward zero by the end — the
endpoints cluster on the no-move line regardless of where they started.
**Caveat 1:** this background field is the *self-only* law. The mixed-pool
families (OLMo mixed-pool interventions, oracle & injection, and the
base-mixed/peer-mixed cells) additionally feel a mixing pull toward the supplier
mean that this field does not show, so their arrows are not expected to track the
horizontal field. **Caveat 2:** endpoints (and a few starts) whose agreement ρ was
unmeasurable — overwhelmingly because σ had already collapsed to 0 — are placed
at forecast move 0; that is the correct reading when σ = 0, and is flagged for the
four non-zero-σ cases in the generator note.

Every coordinate is computed live (stdlib) at build time from the source file;
the generator asserts the 74-run / 340-record totals, the five family counts
(16 / 21 / 18 / 11 / 8), and the nine-swap count against the committed values.

**Source data:** `experiments/spread_util_unified.json` (per-round records:
`value`, `drift`, `rho`, `own_spread`; family from organism/axis/judge/format/
composition). Endpoint convention from
`docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py` `observed()`;
family names from `docs/figures/auto/run-inventory/run-inventory.py`.
Generator: `field-value-gap-startend.py` (regenerate with `python3
field-value-gap-startend.py`).

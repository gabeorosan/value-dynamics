# The (value, ρσ) field's vertical component, measured per axis

**Date:** 2026-07-16 · **Script:** `scripts/analysis_field_vertical_component.py`
→ `experiments/field_vertical_component.json` · **Consumer:**
`docs/figures/auto/field-value-gap-startend/` (the per-family plane figure)

**Why.** The plane figure draws a background field showing where the model
sends a run from each (value v, forecast-move y = ρσ) coordinate. The
horizontal component is the recurrence (Δv = ρσ). The vertical component is
not part of the recurrence — y is a measured input — so any drawn vertical
behavior is a claim about how the dial itself moves. The risk panels bend
with the binary envelope; the user pointed out (07-16) that drawing the
continuous self-description panels FLAT is equally an unestablished dynamics
assertion. So: measure it, per axis, over every consecutive round pair with
agreement defined on both sides.

**Readouts** (y = ρ·own_spread; dy = y′ − y; dv = observed value move,
value + drift convention):

| axis | n transitions | y persistence r | dy = a + b·dv | r(dy, dv) | envelope corr |
|---|---:|---:|---|---:|---:|
| risk | 188 | 0.621 | dy = 0.0066 − 0.0502·dv | −0.102 | **+0.359** (n=170) |
| selfreport (continuous) | 27 | 0.473 | **dy = −0.0214 − 0.1729·dv** | **−0.567** | −0.56 (n=13) |

**What this establishes.**

- **Risk axis:** dy is nearly uncoupled from dv linearly, but the
  envelope-predicted bend dy_env = y·(√(v′(1−v′))/√(v(1−v)) − 1) correlates
  +0.36 with the observed dy — direct empirical support for the risk panels'
  envelope bend, on top of the committed variance identity (R² 0.955).
- **Continuous axis:** strongly coupled, negative — when selection moves the
  value up, the forecast-move coordinate shrinks (r = −0.57, slope −0.17).
  This is the self-consumption mechanism measured as field geometry: the pool
  homogenizes toward where the value went and ρσ collapses. The envelope form
  predicts the wrong sign here (corr −0.56 on the 13 in-range pairs),
  confirming the identity's binary-only scope. A flat field was therefore
  wrong for these panels; they now bend by the measured coupling
  Δ(ρσ) ≈ −0.17·Δv, loaded live from the JSON. The small additional
  per-round downward drift (intercept −0.021) is noted here rather than
  drawn (a schematic arrow at y = 0 should vanish, not drift).

Caveat: 27 transitions on the continuous axis; the slope is a first
measurement, not a law. The figure's caption carries the same scoping.

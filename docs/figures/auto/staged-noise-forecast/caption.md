**The staged-noise forecast (the stochastic rollout).** A typeset reference panel
for the stochastic rollout the value-dynamics model runs: a deterministic unit path
plus staged gaussian innovations, each clamped to its wall. It is a definitions
figure — no data is plotted; every stochastic stage carries a tick down to a gray
boxed label naming its ε term, and the innovation's distribution sits in the right
column, so the reader never leaves a formula to hunt through prose.

This figure was **split off** from a larger panel; it is the **stochastic-rollout
part only**. The per-round measurements it consumes (spread σ, agreement ρ) are
defined in `docs/figures/auto/state-variables/state-variables.svg`, and the
deterministic model and its closed forms are in
`docs/figures/auto/model-recurrence/model-recurrence.svg`.

**The rollout.** It typesets exactly what the committed rollout does. Each ε's SD is
the pooled leave-one-condition-out residual of that stage, rebuilt from the committed
records (no invented noise parameters); σ is held at its round-1 value. (q = the
generator / own-candidate mean; v = the value; v̂ = the reported value.)
- **pool mean:** p_r = (1−u)·q_r + u·s — deterministic mixing, as above.
- **kept mean:** k_r = [ p_r + ρ_r·σ + ε_g ]₀¹, with **ε_g ~ N(0, s_g)** the
  innovation in the judge's step (the selector-gap residual).
- **generator:** q_{r+1} = [ q_r + (k_r − q_r) + ε_q ]₀¹, with **ε_q ~ N(0, s_q)**
  the innovation in the generator (own-candidate mean) update.
- **value:** v_{r+1} = [ v_r + (k_r − v_r) ]₀¹ — the value's move itself is
  deterministic (it tracks the kept mean; only q and ρ carry innovations).
- **agreement:** ρ_{r+1} = [ ρ_r + ε_ρ ]₋₁⁺¹, with **ε_ρ ~ N(0, s_ρ)** — next
  round's agreement = this round's, plus noise (a random walk clamped to [−1, +1]).
- **observed:** v̂_r = [ v_r + ε_obs ]₀¹, with **ε_obs ~ N(0, sqrt(v_r(1−v_r)/n))** —
  battery read noise, added ONLY to the reported value (n = the battery's generation
  count). The [·]₀¹ / [·]₋₁⁺¹ notation is "clamped at the walls".

**Symbol table.** A closing panel restates every symbol used in the rollout — *r*,
*q_r*, *p_r*, *k_r*, *ρ_r*, *v_r*, *v̂_r*, *u*, *s*, *n*, the staged innovations
*ε_g / ε_q / ε_ρ*, and *ε_obs* — plus a note that **σ, ρ are the round-1
measurements** (see the measurements figure).

**Recipe source (not a data file — this figure asserts no numbers).** This block is
verbatim from `rollout()` in
`docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py` (its provenance
is `scripts/analysis_trajectory_adjustments.py`; residual scales are the
leave-one-condition-out unit-core pools; report at
`docs/report_trajectory_adjustment_bakeoff.md`). The σ = spread and ρ = agreement
inputs are the committed estimators documented on the measurements figure.

**Typesetting note.** Every display equation is set with matplotlib's mathtext
(Computer Modern, `mathtext.fontset = "cm"`) and embedded as inline vector glyph
paths at one consistent size, so they read as proper math (true italics, subscripts,
radicals, the clamp brackets) while the figure stays a single self-contained SVG —
every glyph reference is same-document and namespaced per equation, with no external
font or LaTeX dependency. Each ε annotation tick is placed by measuring the on-page
width of the balanced equation prefix up to that term. Regenerate with
`uv run --with matplotlib python3 staged-noise-forecast.py`.

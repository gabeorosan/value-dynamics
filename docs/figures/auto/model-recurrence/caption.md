**The model: one round, iterated, self-only.** A typeset reference panel for the
round-by-round value model that consumes the per-round measurements: the one-round
recurrence and its two unclipped closed forms. It is a definitions figure — no data
is plotted; every part of every equation is explained *at* the equation (a
tick-and-boxed-label under the relevant glyph, or a drawn brace above it), so the
reader never leaves a formula to hunt through prose.

This figure was **split off** from a larger panel; it is the **model part only**.
The three per-round measurements it consumes (spread σ, agreement ρ, selector gap g)
are defined in `docs/figures/auto/state-variables/state-variables.svg`, and the
stochastic staged-noise rollout is in
`docs/figures/auto/staged-noise-forecast/staged-noise-forecast.svg`.

**The recurrence.** Each round the pool mean is p = (1−u)q + u·s (outside-source
share u at level s), the kept mean is k = p + ρσ, and the next value is next v = k
(writeup "The state the law updates" section). Each term of each closed form carries
a tick down to a gray boxed label naming what it is; the one-round equation also
carries two drawn braces above it showing the number-line structure ((1−u)v_r + u·s
together = the **pool mean p**, and p + ρσ = the **kept mean k**). The three typeset
lines are:
- **one round:** v_{r+1} = [ (1−u)·v_r + u·s + ρσ ]₀¹, where **(1−u)·v_r** is the own
  candidates' share of the pool mean, **u·s** is the outside source (share u at level
  s), **ρσ** is the selection step (the judge's step), and **[·]₀¹** means clipped to
  [0, 1] (a small gray note to the right of the equation); σ and ρ are measured once,
  at round 1.
- **iterated (mixed pool, away from the walls):** v_r = v* + (1−u)^r·(v_0 − v*),
  where **v*** is the balance point (= s + ρσ/u), **(1−u)^r** closes a fraction u of
  the distance each round, and **(v_0 − v*)** is the starting distance from balance.
- **self-only (u = 0):** v_r = v_0 + r·ρσ, where **r·ρσ** adds one selection step ρσ
  per round — a straight walk until a wall or the spread runs out.

These closed forms are the **unclipped algebraic solution** of that single
recurrence — they are not separately fitted. Their validity ends where the clip
bites (a wall at 0 or 1) or where the spread σ is exhausted.

**Symbol table.** A closing panel restates every symbol used in the model — *r*,
*v_r*, *v_0*, *v\**, *u*, *s*, *q*, *p*, *k*, *σ*, *ρ* — plus a note that **σ, ρ are
measured at round 1** (see the measurements figure). The measurements' own detailed
symbols (σ_j, ρ_j, g, x_jk, …) live with `docs/figures/auto/state-variables/`.

**Recipe source (not a data file — this figure asserts no numbers).** The recurrence
and its closed forms are the value model in the writeup's "The state the law
updates" section; the σ = spread and ρ = agreement inputs are the committed
estimators in `scripts/analysis_qwen_selfonly_model_check.py` and
`scripts/analysis_spread_util_unified.py` (documented on the measurements figure).

**Typesetting note.** Every display equation is set with matplotlib's mathtext
(Computer Modern, `mathtext.fontset = "cm"`) and embedded as inline vector glyph
paths at one consistent size, so they read as proper math (true italics, subscripts,
superscripts, the clamp brackets) while the figure stays a single self-contained SVG
— every glyph reference is same-document and namespaced per equation, with no
external font or LaTeX dependency. Per-term annotation ticks are placed by measuring
the on-page width of balanced equation prefixes. Regenerate with
`uv run --with matplotlib python3 model-recurrence.py`.

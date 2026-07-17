**The per-round measurements and the model they feed.** A typeset reference
panel: the three per-round bookkeeping quantities the selection-loop analysis
reports, and the round-by-round model those quantities drive. It is a definitions
figure — no data is plotted; it replaces a hard-to-read markdown list with legible
math, and every part of every equation is explained *at* the equation (a gray gloss
or a tick-and-label under the relevant glyph), so the reader never has to leave a
formula and hunt through prose. Within a round, each prompt *j* offers candidates
*k* = 1…*n_j* with value scores *x_jk* in [0,1] and judge scores *s_jk*, and the
judge keeps two candidates.

**The three measurements** (each row shows the per-prompt estimator AND the
round-level aggregation).
- **spread σ** — per prompt, σ_j = sqrt( (1/n_j) Σ_k (x_jk − x̄_j)² ), the standard
  deviation of the candidate value scores, dividing by n_j (the **population
  convention** — divide by the count, not count−1). The round's spread is the
  **mean over prompts**,
  σ = (1/J) Σ_j σ_j, where **J = the round's prompts, each weighted equally** — each
  prompt's pool is measured on its own, NOT the standard deviation obtained after
  pooling every candidate from every prompt into one set (that pooled quantity is
  larger and is a different measurement).
- **agreement ρ** — per prompt, ρ_j = corr(s_j·, x_j·), the Pearson correlation,
  taken within the prompt, between judge score s_j· and value x_j·, written out in
  the figure as ρ_j = Σ_k (s_jk − s̄_j)(x_jk − x̄_j) / sqrt( Σ_k (s_jk − s̄_j)² ·
  Σ_k (x_jk − x̄_j)² ). The round's agreement is the mean over the defined prompts,
  ρ = (1/|D|) Σ_{j∈D} ρ_j, where **D = the prompts on which ρ_j is defined** — a
  prompt with fewer than two candidates, or with zero variance on either the judge
  side or the value side (the denominator would be zero), contributes no ρ_j and is
  dropped; this matches the committed `pearson()` guard (`n < 2` or `den == 0`).
  Range −1 (the judge keeps/scores against the
  value axis) to +1 (with it). The **judge score s_jk** is the judge's measured
  preference for candidate k: the probability it picks k in the A-or-B comparisons —
  against the fixed reference answer (reference mode), or against each duel opponent
  (head-to-head mode) — averaged over those comparisons and both presentation
  orders. Concretely the loop accumulates `sc[i] += P(candidate i preferred)` over
  the pairings and divides by the count. When the score oracle is the judge, s is
  the value score itself.
- **selector gap g = k − p** — kept mean minus pool mean, both round means. In the
  figure the equation is annotated at each glyph: **k = the mean value of the two
  kept candidates**, **p = the mean value of the whole candidate pool**. The pool
  averages every **candidate in the pool** — the organism's own candidates plus any
  outside-source candidates, everything eligible to be kept and trained on. The
  alternative source's answer is shown to the judge as a **comparison standard
  only**; in the static-alternative format it is never part of the pool and is never
  kept. Round-level forecast g ≈ ρσ, with ρ and σ the round's prompt-averaged
  values. (**k − q**, kept mean minus the organism's own generated candidate mean q,
  is the separate **training displacement** — noted, not drawn.)

**The model these feed.** The panel's lower block gives the round recurrence and its
closed forms. Each round the pool mean is p = (1−u)q + u·s (outside-source share u
at level s), the kept mean is k = p + ρσ, and the next value is next v = k (writeup
"The state the law updates" section). Each term of each closed form carries a tick
down to a gray label naming what it is; the one-round equation also carries two
brackets above it showing the number-line structure ((1−u)v_r + u·s together = the
**pool mean p**, and p + ρσ = the **kept mean k**). The three typeset lines are:
- **one round:** v_{r+1} = [ (1−u)·v_r + u·s + ρσ ]₀¹, where **(1−u)·v_r** is the own
  candidates' share of the pool mean, **u·s** is the outside source (share u at level
  s), **ρσ** is the selection step (the judge's step), and **[·]₀¹** means clipped at
  the walls 0 and 1; σ and ρ are measured once, at round 1.
- **iterated (mixed pool, away from the walls):** v_r = v* + (1−u)^r·(v_0 − v*),
  where **v*** is the balance point (= s + ρσ/u), **(1−u)^r** closes a fraction u of
  the distance each round, and **(v_0 − v*)** is the starting distance from balance.
- **self-only (u = 0):** v_r = v_0 + r·ρσ, where **r·ρσ** adds one selection step ρσ
  per round — a straight walk until a wall or the spread runs out.

These closed forms are the **unclipped algebraic solution** of that single
recurrence — they are not separately fitted. Their validity ends where the clip
bites (a wall at 0 or 1) or where the spread σ is exhausted, at which point the
straight/geometric form no longer holds.

**The staged-noise forecast (the stochastic rollout).** The lowest block typesets
exactly what the committed rollout does — a deterministic unit path plus staged
gaussian innovations, each clamped to its wall. Each ε's SD is the pooled
leave-one-condition-out residual of that stage, rebuilt from the committed records
(no invented noise parameters); σ is held at its round-1 value.
- **pool mean:** p_r = (1−u)·q_r + u·s — deterministic mixing, as above.
- **kept mean:** k_r = [ p_r + ρ_r·σ + ε_g ]₀¹, with **ε_g ~ N(0, s_g)** the
  innovation in the judge's step (the selector-gap residual).
- **generator:** q_{r+1} = [ q_r + (k_r − q_r) + ε_q ]₀¹, with **ε_q ~ N(0, s_q)**
  the innovation in the generator (own-candidate mean) update.
- **value:** v_{r+1} = [ v_r + (k_r − v_r) ]₀¹ — the value's move itself is
  deterministic (it tracks the kept mean; only q and ρ carry innovations).
- **agreement:** ρ_{r+1} = [ ρ_r + ε_ρ ]₋₁⁺¹, with **ε_ρ ~ N(0, s_ρ)** — agreement
  drifts as a random walk (clamped to [−1, +1]) around persistence.
- **observed:** v̂_r = [ v_r + ε_obs ]₀¹, with **ε_obs ~ N(0, sqrt(v_r(1−v_r)/n))** —
  battery read noise, added ONLY to the reported value (n = the battery's generation
  count). The [·]₀¹ / [·]₋₁⁺¹ notation is "clamped at the walls".

This block's recipe is verbatim from `rollout()` in
`docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py` (its provenance
is `scripts/analysis_trajectory_adjustments.py`; residual scales are the
leave-one-condition-out unit-core pools; report at
`docs/report_trajectory_adjustment_bakeoff.md`).

**Symbol table.** A closing panel restates every symbol on the figure so none
appears without a definition somewhere on the page — including the round index
r = 1, 2, …, and v* (balance point), v̂_r (reported value), and the ε innovations.

**Annotation style.** Every straight leader line that runs from an equation term to
its explanatory text ends on a **box** drawn around that text (a light rounded
rectangle, thin muted-gray stroke, near-white fill, ~5px padding) — the line
terminates exactly on the box edge (touching it, not floating near it), so it is
unambiguous which text belongs to which term. This applies to the g = k − p
annotations, the per-term labels under the one-round / iterated / self-only closed
forms, and the ε annotations in the staged-noise block. Each label sits on its own
row (multi-term labels are right-anchored at their leader) and rows are spaced so no
box overlaps another box, a neighboring line, or an equation. **Brace-connected
labels** (the kept-mean / pool-mean over-braces on the one-round equation) and
**free-floating gloss paragraphs** are deliberately left unboxed.

**Recipe source (not a data file — this figure asserts no numbers).** The
estimators and recurrence shown match the committed code exactly:
`scripts/analysis_qwen_selfonly_model_check.py` (σ_j = population SD of x_jk;
ρ_j = Pearson(s_jk, x_jk); gap_j = kept mean − pool mean; round aggregates are the
mean over prompts, ρ over the prompts where the correlation is defined) and
`scripts/analysis_spread_util_unified.py` (spread = mean over prompts of the
within-prompt population SD, ddof = 0, explicitly not the pooled SD). The judge-score
mechanics are `head2head_score` (duel mode) / `pair_score` (fixed-reference mode) in
`experiments/em_selfaware_loop/colab_selfaware_loop_grid.py` (softmax A-or-B
win-probability accumulated over pairings via `sc[i] += pr[..., 0]`, then averaged
by count).

**Typesetting note.** Every display equation on the figure — the four
measurement-row estimators (σ_j, σ, the ρ_j Pearson formula, ρ) as well as the
closed-form and stochastic-rollout blocks — is set with matplotlib's mathtext
(Computer Modern, `mathtext.fontset = "cm"`) and embedded as inline vector glyph
paths, all at one consistent size, so they read as proper math (true italics,
subscripts, superscripts, radicals, fractions, the `|D|` bars and the clamp
brackets) while the figure stays a single self-contained SVG — every glyph reference
is same-document and namespaced per equation, with no external font or LaTeX
dependency. The per-term annotation ticks are placed by measuring the on-page width
of balanced equation prefixes, so each label sits under its own term. Regenerate with
`uv run --with matplotlib python3 state-variables.py`.

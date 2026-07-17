**The per-round measurements.** A typeset reference panel for the three per-round
bookkeeping quantities the selection-loop analysis reports: **spread σ**,
**agreement ρ**, and the **selector gap g**. It is a definitions figure — no data
is plotted; it replaces a hard-to-read markdown list with legible math, and every
part of every equation is explained *at* the equation (a gray gloss, or a
tick-and-boxed-label under the relevant glyph), so the reader never has to leave a
formula and hunt through prose. Within a round, each prompt *j* offers candidates
*k* = 1…*n_j* with value scores *x_jk* in [0,1] and judge scores *s_jk*, and the
judge keeps two candidates.

This figure is the **measurements part only** — it was split off from a larger
panel. The round-by-round **model** those measurements feed now lives in its own
figure, `docs/figures/auto/model-recurrence/model-recurrence.svg`, and the
stochastic **staged-noise rollout** in
`docs/figures/auto/staged-noise-forecast/staged-noise-forecast.svg`.

**The three measurements** (each row shows the per-prompt estimator AND the
round-level aggregation).
- **spread σ** — per prompt, σ_j = sqrt( (1/n_j) Σ_k (x_jk − x̄_j)² ), the standard
  deviation of the candidate value scores, dividing by n_j (the **population
  convention** — divide by the count, not count−1). The round's spread is the
  **mean over prompts**, σ = (1/J) Σ_j σ_j, where **J = the round's prompts, each
  weighted equally** — each prompt's pool is measured on its own, not the standard
  deviation obtained after pooling every candidate from every prompt into one set
  (that pooled quantity is larger and is a different measurement — this distinction
  is stated in the recipe source below, not glossed on the figure).
- **agreement ρ** — per prompt, ρ_j = corr(s_j·, x_j·), the Pearson correlation,
  taken within the prompt, between judge score s_j· and value x_j·, written out in
  the figure as ρ_j = Σ_k (s_jk − s̄_j)(x_jk − x̄_j) / sqrt( Σ_k (s_jk − s̄_j)² ·
  Σ_k (x_jk − x̄_j)² ). The round's agreement is the mean over the defined prompts,
  ρ = (1/|D|) Σ_{j∈D} ρ_j, where **D = the prompts on which ρ_j is defined** — a
  prompt with fewer than two candidates, or with zero variance on either the judge
  side or the value side (the denominator would be zero), contributes no ρ_j and is
  dropped; this matches the committed `pearson()` guard (`n < 2` or `den == 0`). For
  the record: the **judge score s_jk** is the judge's measured preference for
  candidate k, the probability it picks k in the A-or-B comparisons — against the
  fixed reference answer (reference mode), or against each duel opponent
  (head-to-head mode) — averaged over those comparisons and both presentation
  orders. When the score oracle is the judge, s is the value score itself.
- **selector gap g = k − p** — kept mean minus pool mean, both round means. In the
  figure the equation is annotated at each glyph: **k = the mean value of the two
  kept candidates**, **p = the mean value of the whole candidate pool**. The row's
  single gloss is the round-level forecast **g ≈ ρσ** (a small gray note to the
  right of the equation). For the record, the pool averages every **candidate in the
  pool** — the organism's own candidates plus any outside-source candidates,
  everything eligible to be kept and trained on.

**Symbol table.** A closing panel restates every symbol used in the measurements so
none appears without a definition somewhere on the page: *x_jk*, *s_jk*, *n_j*, *J*,
*D*, *σ_j*, *σ*, *ρ_j*, *ρ*, *g*, *k*, *p*. The model's and rollout's own symbols
(*v_r*, *v\**, *u*, the ε innovations, …) live with those two figures.

**Annotation style.** Every straight leader line that runs from an equation term to
its explanatory text ends on a **box** drawn around that text (a light rounded
rectangle, thin muted-gray stroke, near-white fill, ~6px padding) — the line
terminates exactly on the box edge, so it is unambiguous which text belongs to which
term. This applies to the g = k − p annotations.

**Recipe source (not a data file — this figure asserts no numbers).** The
estimators shown match the committed code exactly:
`scripts/analysis_qwen_selfonly_model_check.py` (σ_j = population SD of x_jk;
ρ_j = Pearson(s_jk, x_jk); gap_j = kept mean − pool mean; round aggregates are the
mean over prompts, ρ over the prompts where the correlation is defined) and
`scripts/analysis_spread_util_unified.py` (spread = mean over prompts of the
within-prompt population SD, ddof = 0, explicitly not the pooled SD). The judge-score
mechanics are `head2head_score` (duel mode) / `pair_score` (fixed-reference mode) in
`experiments/em_selfaware_loop/colab_selfaware_loop_grid.py`.

**Typesetting note.** The four measurement-row estimators (σ_j, σ, the ρ_j Pearson
formula, ρ) are set with matplotlib's mathtext (Computer Modern,
`mathtext.fontset = "cm"`) and embedded as inline vector glyph paths at one
consistent size, so they read as proper math while the figure stays a single
self-contained SVG — every glyph reference is same-document and namespaced per
equation, with no external font or LaTeX dependency. Regenerate with
`uv run --with matplotlib python3 state-variables.py`.

**The per-round measurements and the model they feed.** A typeset reference
panel: the three per-round bookkeeping quantities the selection-loop analysis
reports, and the round-by-round model those quantities drive. It is a definitions
figure — no data is plotted; it replaces a hard-to-read markdown list with legible
math. Within a round, each prompt *j* offers candidates *k* = 1…*n_j* with value
scores *x_jk* in [0,1] and judge scores *s_jk*, and the judge keeps two.

**The three measurements.**
- **spread σ** — per prompt, the standard deviation of the candidate value scores,
  σ_j = sqrt( (1/n_j) Σ_k (x_jk − x̄_j)² ), dividing by n_j (the population
  convention, **ddof = 0**). The round's σ is the **mean over prompts** of σ_j,
  with **equal weight per prompt** — each prompt's pool is measured on its own, NOT
  the standard deviation obtained after pooling every candidate from every prompt
  into one set (that pooled quantity is larger and is a different measurement).
- **agreement ρ** — per prompt, the Pearson correlation, taken within the prompt,
  between judge score s_j· and value x_j·. The round's ρ is the mean over prompts
  of ρ_j. **Prompts where ρ_j is undefined are dropped** — a prompt with fewer than
  three candidates, or with zero variance on either the judge side or the value
  side, contributes no ρ_j. Range −1 (the judge keeps/scores against the value
  axis) to +1 (with it). Measured per round, but in practice a property of the
  judge × alternative-answer-source × answer-source condition. The **judge score
  s_jk** is the judge's measured preference for answer k: the probability it picks
  k in the A-or-B comparisons — against the fixed reference answer (reference
  mode), or against each duel opponent (head-to-head mode) — averaged over those
  comparisons and both presentation orders. Concretely the loop accumulates
  `sc[i] += P(candidate i preferred)` over the pairings and divides by the count.
  When the score oracle is the judge, s is the value score itself.
- **selector gap g = k − p** — kept mean minus pool mean, both round means. The
  pool mean p averages every **candidate in the pool**: the organism's own
  answers plus any outside-source answers — the answers eligible to be kept and
  trained on. The alternative source's answer is shown to the judge as a
  **comparison standard only**; in the static-alternative format it is never part
  of the pool and is never kept. Round-level forecast g ≈ ρσ, with ρ and σ the
  round's prompt-averaged values.

**One more kept-mean gap** (not drawn, defined here to keep the figure to the
quantities the model uses): **training displacement = k − q** is the kept mean
minus the organism's own generated mean q, as a round mean.

**The model these feed.** The panel's lower block gives the round recurrence and
its closed forms. Each round the pool mean is p = (1−u)q + u·s (outside-source
share u at level s), the kept mean is k = p + ρσ, and the next value is
next v = k (writeup "The state the law updates" section). The three typeset lines
are:
- **one round:** v_{r+1} = clip( (1−u)·v_r + u·s + ρσ , 0, 1 ), with σ and ρ
  measured once, at round 1.
- **iterated (mixed pool, away from the walls):** v_r = v* + (1−u)^r·(v_0 − v*),
  a geometric approach to the balance point v* = s + ρσ/u.
- **self-only (u = 0):** v_r = v_0 + r·ρσ, a straight walk until a wall or the
  spread runs out.

These closed forms are the **unclipped algebraic solution** of that single
recurrence — they are not separately fitted. Their validity ends where the clip
bites (a wall at 0 or 1) or where the spread σ is exhausted, at which point the
straight/geometric form no longer holds.

**Recipe source (not a data file — this figure asserts no numbers).** The
estimators and recurrence shown match the committed code exactly:
`scripts/analysis_qwen_selfonly_model_check.py` (σ_j = population SD of x_jk;
ρ_j = Pearson(s_jk, x_jk); gap_j = kept mean − pool mean; round aggregates are the
mean over prompts) and `scripts/analysis_spread_util_unified.py` (spread = mean
within-item population SD, ddof = 0, explicitly not the pooled SD). The judge-score
mechanics are `head2head_score` (duel mode) / `pair_score` (fixed-reference mode) in
`experiments/em_selfaware_loop/colab_selfaware_loop_grid.py` (softmax A-or-B
win-probability accumulated over pairings via `sc[i] += pr[..., 0]`, then averaged
by count).

**Typesetting note.** The three display equations in "The model these feed" are
set with matplotlib's mathtext (Computer Modern, `mathtext.fontset = "cm"`) and
embedded as inline vector glyph paths, so they read as proper math (true italics,
subscripts, superscripts, radicals) while the figure stays a single self-contained
SVG — every glyph reference is same-document and namespaced per equation, with no
external font or LaTeX dependency. Regenerate with
`uv run --with matplotlib python3 state-variables.py`.

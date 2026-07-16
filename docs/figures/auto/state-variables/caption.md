**The five per-round measurements.** A typeset reference panel for the
per-round bookkeeping quantities the selection-loop analysis reports. It is a
definitions figure — no data is plotted; it replaces a hard-to-read markdown
bullet list with legible math. Within a round, each prompt *j* offers candidates
*k* = 1…*n_j* with value scores *x_jk* in [0,1] and judge scores *s_jk*, and the
judge keeps two.

- **spread σ** — per prompt, the population standard deviation of the candidate
  value scores, σ_j = sqrt( (1/n_j) Σ_k (x_jk − x̄_j)² ), computed with **ddof = 0**.
  The round's σ is the **mean over prompts** of σ_j, with **equal weight per
  prompt** — the within-prompt SD averaged across prompts, NOT the standard
  deviation obtained after pooling every candidate from every prompt into one
  set (that pooled quantity is larger and is a different measurement).
- **agreement ρ** — per prompt, the Pearson correlation, taken within the
  prompt, between judge score s_j· and value x_j·. The round's ρ is the mean over
  prompts of ρ_j. **Prompts where ρ_j is undefined are dropped** — a prompt with
  fewer than three candidates, or with zero variance on either the judge side or
  the value side, contributes no ρ_j. Range −1 (the judge keeps/scores against
  the value axis) to +1 (with it). It is measured per round, but in practice it
  is a property of the judge × alternative-answer-source × answer-source
  condition rather than of the individual round.
- **selector gap g = k − p** — kept mean minus offered-pool mean (both round
  means).
- **training displacement = k − q** — kept mean minus the organism's own
  generated mean q.
- **behavioral pull = k − v** — kept mean minus the behavioral value v.

The foot line states where the averaged quantities are used: the round-level gap
forecast g ≈ ρσ takes ρ and σ as the round's prompt-averaged values.

**Recipe source (not a data file — this figure asserts no numbers).** The
estimators shown match the committed scorers exactly:
`scripts/analysis_qwen_selfonly_model_check.py` (σ_j = population SD of x_jk;
ρ_j = Pearson(s_jk, x_jk); gap_j = kept mean − pool mean; round aggregates are
the mean over prompts) and `scripts/analysis_spread_util_unified.py`
(spread = mean within-item population SD, ddof = 0, explicitly not the pooled-SD;
correlated-response gap built from ρ · value-SD per prompt). Regenerate the SVG
with `python3 state-variables.py`.

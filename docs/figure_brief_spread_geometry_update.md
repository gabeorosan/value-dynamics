# Figure request: how selection converts spread into the next generator state

**Owner:** Claude / Figures lane
**Priority:** replace the in-progress `spread-tracks-centrality` figure with
this conversion-chain figure.
**Source of truth:** `experiments/spread_conversion_model.json` and
`docs/report_spread_conversion_model.md`.

## Main figure

**Title:** Selection converts candidate variation into a new output distribution

**Subtitle:** Selector accounting uses 340 rounds from 74 OLMo/Qwen runs;
next-spread conversion uses 221 binary risk-axis transitions with
leave-one-run-out fits

Put the spread definition visibly on the figure or immediately below it:

> Within-prompt spread = the population SD of candidate value scores inside
> each prompt, averaged equally over prompts (`ddof=0`; not a pooled SD).

Build one four-panel figure. The visual spine should read left to right:

`offered spread` → `selector gap` → `training displacement` →
`change in own generated mean` → `change in own generated spread`.

### Panel A — define the three distances

Show one horizontal 0–1 candidate-score axis with four labeled means:

- model's own generated mean `q`;
- whole offered pool mean `p`;
- kept training-target mean `k`;
- separate behavioral value `v`.

Draw and label:

- **selector gap** = `k − p`;
- **pool-supply shift** = `p − q`;
- **training displacement** = `k − q = selector gap + pool-supply shift`;
- **behavioral pull** = `k − v`.

Main annotation:

> Use kept − whole pool to measure the selector. Use kept − the model's own
> pool to measure the update.

For self-only pools, show `p = q`, so the two gaps coincide. For mixed pools,
show a small outside-source block shifting `p` away from `q`.

### Panel B — the self-relative gap tracks movement better under mixing

Use grouped dots or bars for correlation with behavioral movement:

| predictor | all 340 | mixed 96 | base-mixed 64 | peer-mixed 32 |
|---|---:|---:|---:|---:|
| selector gap: kept − whole pool | 0.578 | 0.627 | 0.433 | 0.902 |
| training displacement: kept − own pool | **0.682** | **0.828** | **0.644** | **0.947** |
| behavioral pull: kept − behavioral value | 0.801 | 0.907 | 0.802 | 0.985 |

Visually emphasize the middle row as the generator-update quantity. The last
row is a measurement bridge to the separate behavioral readout, not a competing
definition of selection.

### Panel C — the conversion chain over consecutive rounds

Use two linked scatter/fit mini-panels or a compact path diagram with empirical
coefficients:

1. `training displacement → Δ own generated mean`
   - binary risk 221: `Δq = 0.009 + 0.789g_self`, `r = 0.838`;
   - mixed risk 60: `Δq = 0.028 + 0.739g_self`, `r = 0.897`.
2. `new mean + prompt structure → next own spread`
   - show the exact binary identity:
     `within-prompt variance = q(1−q) − variance across prompt means`;
   - then show that reported spread averages `sqrt(variance_j)` across
     prompts, rather than taking one square root after pooling.

Show the directional consequence rather than a generic centrality curve:

- move `q` toward 0 or 1 → less next-round own spread;
- move `q` toward 0.5 → more next-round own spread.

Do not imply that round number consumes spread. The arrow must pass through the
change in the model's own generated distribution.

### Panel D — held-out next-spread prediction

Paired bars, conversion chain versus spread-persistence baseline:

| slice | headroom-only | exact decomposition | persistence |
|---|---:|---:|---:|
| all binary risk 221 | 0.765 | **0.778** | 0.581 |
| self-only risk 161 | 0.774 | **0.789** | 0.668 |
| mixed risk 60 | 0.598 | **0.653** | 0.193 |

Below the bars add:

> Fully factorized before selection (`pool shift + 0.96·agreement·spread`):
> R² 0.631 vs 0.438 across risk transitions; the mixed-risk slice is weaker
> at 0.269 vs −0.017.

This is the load-bearing panel. Label the validation as
**leave one entire run out**. A smaller note may state that leaving out entire
Add a small scope note: the same mean-to-spread conversion fails on the 60
continuous self-report rounds (−0.029 vs 0.747 persistence), so the dynamics
panel is explicitly labeled **binary risk score**.

## Optional inset: what whole-pool spread contains under mixing

If the four panels leave room, add a small exact variance-decomposition inset:

`total variance = within-source variance + between-source variance`.

- base-mixed: mean variance 0.146 = 0.097 within-source + 0.049
  between-source (34%);
- peer-mixed: 0.076 = 0.033 + 0.043 (57%).

Only the variance components add. If the SD-scale effect is shown separately,
label it as the change after removing between-source variance inside each
prompt: 0.077/0.327 (23%) base-mixed and 0.073/0.172 (42%) peer-mixed.

## Caption

> The judge first converts variation in the offered pool into a selector gap.
> In a mixed pool, outside candidates also shift the pool relative to the
> model's own outputs; adding that supply shift gives the training displacement.
> This displacement predicts how the mean of the model's own generated
> candidates moves. On the binary risk score, total variance is q(1−q); after
> subtracting variance across prompt means, the remainder is the variation
> available to within-prompt selection. The chain predicts held-out next-round
> own-source spread better than spread persistence, especially under mixing.
> Round number is not a term in the model.

## Edits requested across existing figures

1. `docs/figures/auto/value-score-defined/`
   - The current version is incorrect: it says every candidate score is 0/1.
   - Split the display by score type. Risk candidates are 0/1 according to the
     selected option. Insecure-code self-report candidates use the continuous
     `cand_sr_scores` value in [0,1], a probability-like score of insecure
     self-description.
   - Say explicitly that the promptwise population-SD estimator applies to
     both, while `p(1−p)` applies only to the binary risk panel.

2. `docs/figures/auto/selection-loop-two-dials/`
   - Call kept − whole pool **selector gap**, not the general movement force.
   - Add or reserve a supply-shift arrow from whole-pool mean to own-pool mean.
   - The update arrow should be **training displacement = kept − own pool**.

3. `docs/figures/auto/spread-by-composition-v2/`
   - Keep the observed trajectories.
   - Replace the current subtitle “SD of the judge value reading” with:
     “population SD of candidate value scores within each prompt, averaged
     over prompts.” The value scorer and the selector judge are different
     objects.
   - Add the model's own-source spread as the carried state where source labels
     permit it; distinguish it from total mixed-pool spread.
   - Caption total mixed spread as within-source + between-source variation.

4. `docs/figures/auto/two-clocks-spread-util/`
   - Replace “two clocks” with the conversion chain. Spread is not an
     autonomous clock; it changes because the generator distribution and pool
     composition change.
   - Agreement may remain the comparatively stable setup property.

5. `docs/figures/auto/two-dials-clean/`
   - Injection changes both pool-supply shift and between-source spread.
   - Invasion shrinks between-source spread as host and supplier converge.
   - Keep the reference-vs-duel agreement result.

6. `docs/figures/synthesis_traj_value_spread.svg`
   - If retained, relabel the x coordinate as the model's generated-pool mean
     when that quantity is actually plotted. Do not mix the behavioral probe
     and candidate-pool mean under one “value” label.

7. `docs/figures/synthesis_state_space_trajectories.svg` and
   `docs/figures/synthesis_traj_gap_drift.svg`
   - Whole-pool gap remains correct for selector accounting.
   - For mixed-pool movement panels, add or switch to self-relative training
     displacement and define it visibly.

8. `site/index.html`
   - After revised SVGs land, rebuild embedded base64 payloads.
   - Surrounding prose should use selector gap / training displacement / pull
     consistently with this brief.

## Visual guardrails

- Plain-language title, white background, existing house colors.
- Do not make “centrality” the title or protagonist. Use “own generated mean”
  and the exact binary variance split; show both `q(1−q)` and the subtraction
  of variance across prompt means.
- Keep whole offered pool and own generated pool visually distinct.
- If total SD including between-prompt mean differences is shown, call it
  **distributional breadth**, not selectable spread.
- No internal run codes and no decorative causal arrows.
- Show the LORO benchmark and sample counts directly on the figure.
- Do not write “six candidates” inside the mathematical definition. Use
  `n_j`; six is the normal design, while four recorded rounds contain a
  five-candidate prompt.

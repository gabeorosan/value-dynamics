# Figure correction brief: candidate-pool geometry, not a state-centrality mechanism

**Owner:** Claude / Figures lane  
**Priority:** replace the in-progress `spread-tracks-centrality` figure before
promotion and correct every active spread figure listed below.  
**Source of truth:** `experiments/spread_value_centrality.json` and
`docs/report_spread_value_centrality.md`.

## The claim change

Do not visualize or caption the following claims:

- “model-state value centrality causes candidate spread”;
- “centrality is the dominant term”;
- “spread rides the value”;
- “the loop is self-limiting because its fuel vanishes at 0/1”;
- “0 and 1 are stable resting points / attractors”;
- “spread is consumed” when the evidence only shows that the scored candidate
  pool became homogeneous.

Use this corrected claim:

> Candidate spread is calculated from 0/1 candidate scores and is therefore
> bounded by the candidate pool's own Bernoulli geometry. Model state and pool
> mean co-move, so state centrality is a proxy, not an identified cause. A pool
> with no rankable variation is selection-inert on the measured axis under the
> tested generator and judge; an outside supplier can restore that variation.

The matched injection pair is the causal result. The centrality regressions are
diagnostic accounting, not a causal intervention.

## New replacement figure

**Title:** Candidate spread is bounded by the candidate pool's 0–1 geometry

**Subtitle:** 340 rounds from 74 OLMo/Qwen runs; the load-bearing comparison is
the 96 mixed-pool rounds

Build one clean three-panel figure:

### Panel A — why the bound exists

- Show six candidate scores as 0/1 marks and define `p = candidate-pool mean`.
- Show the Bernoulli population-SD curve `sqrt(p(1−p))`, zero at p=0/1 and
  maximal at p=0.5.
- Label this curve **aggregate SD ceiling/proxy**, not “predicted spread” and
  not an exact identity: observed spread averages per-item SD before pooling.
- One sentence only: “Spread and pool mean use the same binary scores.”

### Panel B — compare the old proxy with the direct pool quantity

Use the 96 mixed-pool rounds.

- Left mini-scatter: x = pre-round **model-state centrality**
  `value(1−value)`, y = candidate spread. Label `R² = 0.644` and “proxy”.
- Right mini-scatter: x = **candidate-pool centrality**
  `pool_mean(1−pool_mean)`, same y. Label `R² = 0.935` and “same candidate
  scores as spread”.
- Keep identical x/y scales where mathematically appropriate.
- Color by pool composition (base-mixed vs peer-mixed); use shape or a thin
  outline for model family only if legible. Do not color by outcome.
- Add the small annotation `corr(model value, pool mean) = 0.91` for all 340
  rounds.
- Do not draw a causal arrow from model value to candidate spread.

### Panel C — the ordering survives stricter comparisons

Use paired bars or a compact dot plot, always state centrality first and
candidate-pool centrality second:

| comparison on mixed pools | model-state centrality | candidate-pool centrality |
|---|---:|---:|
| pooled R² (96 rounds) | 0.644 | 0.935 |
| within-run R² (96 rounds, 24 runs) | 0.643 | 0.937 |
| first-difference R² (72 transitions) | 0.511 | 0.873 |
| leave-one-run-out R² | 0.603 | 0.932 |

Directly label below the bars:

> After pool centrality, state centrality adds 0.0001 pooled, 0.0020
> within-run, and 0.00003 first-difference R².

Do not turn this into a “pool centrality causes spread” headline. The point of
Panel C is that the old state mechanism is not identified because a structural
same-score quantity explains the result better.

## Caption to use

> Candidate spread and candidate-pool mean are calculated from the same 0/1
> candidate scores, so the pool's possible spread is mechanically bounded by
> its mean. The pre-round model value correlates with pool mean (r = 0.91),
> which makes state centrality a good proxy in pooled data. In mixed pools,
> candidate-pool centrality explains 94% of spread and transports leave-one-run
> out; state centrality adds effectively no within-run or change-over-time
> information after it. This is a geometry audit, not a causal pool-centrality
> model. The causal intervention result remains the matched injection: changing
> only the supplier restored measured-axis variation and movement.

## Existing figures to revise

1. `docs/figures/auto/selection-loop-two-dials/`
   - Replace “spread is spent/refilled” with “the answer pool supplies more or
     less rankable variation.”
   - Replace any endpoint/attractor language with “selection-inert on this
     measured axis under this generator.”
   - Keep `gap = spread × agreement`; that accounting result is unaffected.

2. `docs/figures/auto/spread-by-composition-v2/`
   - The trajectories can remain.
   - Title/caption must say persistence, supplier restoration, and pool
     homogenization; do not say spread tracks model-state centrality.
   - Add a small pointer to the new geometry figure if space permits.

3. `docs/figures/auto/two-clocks-spread-util/`
   - Replace the left-panel title “Spread is spent and refilled” with
     “Candidate-pool composition changes spread.”
   - Replace “a dynamic” with “a pool statistic”; keep the agreement panel.
   - Remove “consumable state,” “fuel,” and causal arrows from model value to
     spread.

4. `docs/figures/auto/two-dials-clean/` and the superseded
   `docs/figures/auto/two-dials-interventions/`
   - Injection **restores rankable variation** (`σ 0.00 → 0.31`).
   - Invasion makes the host/supplier candidate pool **homogeneous as they
     converge** (`σ 0.43 → 0.06`); the supplier is not “consumed.”
   - Keep the reference-vs-duel agreement result unchanged.

5. `docs/figures/synthesis_traj_value_spread.svg`
   - The plotted association may remain, but title/caption must mark model value
     as a proxy for candidate-pool composition and must not imply state→spread
     causation.

6. Any new `spread-tracks-centrality` draft
   - Supersede it completely with the three-panel figure above. Do not promote
     or embed the old draft even if visually finished.

7. `site/index.html`
   - After the corrected SVGs land, rebuild the embedded base64 figures so the
     visible text and alt text no longer say “spent,” “consumed,” “centrality
     drives spread,” or “self-limiting.” The surrounding site prose has already
     been corrected; the embedded SVG payloads have not.

## Visual guardrails

- Plain-language title, white background, existing house colors.
- No internal run codes.
- No causal arrows except the matched supplier-injection intervention.
- Keep “0/1” visibly tied to the **scoring coordinate**, not to a claim that the
  model has a one-dimensional latent value.
- Label pooled, within-run, first-difference, and LORO results distinctly.
- Do not add uncertainty bars that are not in the source artifact.

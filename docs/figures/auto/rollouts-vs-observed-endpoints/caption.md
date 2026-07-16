# Simulated endpoint distributions and observed endpoints, by condition group

Each column is one condition cell of the risk-value grid (organism x judge x
format x pool composition) that has at least two runs. The light-blue shape is
the distribution of **simulated final-round values**, and the dark dots are the
**observed final values** of the real runs (one dot per run/seed, colored blue
for self-judge cells and green for frozen/external-judge cells). The y-axis is
the behavioral value on the 0-1 scale; the short horizontal blue tick on each
violin marks the simulated median.

**How the simulated distribution is built.** For every run in a cell the
generator reads *only* that run's first-round pool state from
`experiments/spread_util_unified.json` — own candidate mean, within-prompt spread
sigma, judge/value agreement rho, behavioral value, and (for mixed pools) the
supplier share and supplier mean — and rolls the parameter-free unit recurrence
forward to that run's own final round: pool `p = (1-u)*q + u*s`, kept
`k = clip(p + rho*sigma, 0, 1)`, next value = k, sigma frozen at round 1. Noise
is added only where the measurement implies it (the committed "staged-noise"
recipe: selector-gap innovation, generated-mean update, agreement drift, and a
final binomial observation-noise term on the reported value), with every residual
scale rebuilt leave-one-condition-out from the committed records. The generator
keeps **300 seeded draws of the final reported value per run** (`random.Random`,
stdlib) and pools them across the cell's runs to form the violin; the observed
dots are the last round's `value + drift`. The rollout code is copied verbatim
from `docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py`.

The comparison is a distributional check, not a per-run overlay: within each
cell the observed endpoints should look like a plausible sample from the pooled
simulated endpoint distribution. Endpoints span nearly the whole 0-1 range even
within a single cell (e.g. the OLMo frozen-base and scheduled-judge cells run
from near 0 to near 1 across seeds), and both the simulated spread and the
observed dots reflect that seed-to-seed dispersion; the mixed-pool OLMo cells
(duel format) sit higher and tighter, near 0.5-0.65.

**Excluded / marked.** The Qwen random-judge cell is left out: random selection
has no judge/value agreement, so round-1 rho is undefined and the recurrence
cannot roll it. No within-run judge swaps exist in this file (each run has a
constant judge), so none needed to be split out; judge identity is instead shown
per column in the label and dot color.

## Source data

- `experiments/spread_util_unified.json` — per-run round records (round-1 pool
  state driving the simulator; observed `value + drift` for the endpoint dots).
- Simulator (unit recurrence + staged-noise residual pools) copied verbatim from
  `docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py`, whose
  recipe traces to `scripts/analysis_trajectory_adjustments.py`.

Regenerate: `python3 rollouts-vs-observed-endpoints.py` (stdlib only).

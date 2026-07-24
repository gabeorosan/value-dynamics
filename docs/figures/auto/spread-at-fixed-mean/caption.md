> **DO NOT PROMOTE — 2026-07-24.** This figure illustrates a result that was
> rescoped to a feasibility check the same day it was made: the contrast it shows is
> definitional (a value-uniform prompt has a selection gap of exactly zero by
> arithmetic), and no training was involved. See the banner on
> docs/reports/report_spread_at_fixed_mean.md.

# Caption — spread-at-fixed-mean.svg

**Selection sees only the variation inside a prompt.** A round's pool mean fixes
the total variation among its candidates, but not how that variation splits
between differences *within* a prompt and differences *between* prompts, and the
judge only ever compares candidates written for the same prompt. Taking 323
logged rounds of 12 prompts each, the logged candidates were re-arranged into
sub-pools of 4 per prompt (2 kept), holding the round's pool mean exactly fixed
and shifting variation into the prompts (arrangement 1) or out of them
(arrangement 2); selection was then re-run on the judges' own recorded scores,
with no retraining. Panel A: the pool mean is identical in both arms by
construction — the largest difference between the two arrangements across all 323
rounds is 0.000000 — yet **within-prompt spread** (average over the round's
prompts of the standard deviation of that prompt's 4 candidate value scores,
each 0 or 1) is 0.286 in arrangement 1 against 0.082 in arrangement 2, and the
**size of the selection gap** (kept-candidate mean minus pool mean, size ignoring
sign, averaged over the 323 rounds) follows it, 0.104 against 0.034; arrangement
1 gave the larger gap in 239 rounds, tied in 71, and gave a smaller one in 13.
The trade-off that makes this possible runs the other way: **between-prompt
variance** (variance across the round's prompts of each prompt's own mean
candidate score) is 0.059 in arrangement 1 against 0.154 in arrangement 2 —
variation taken out of the prompts reappears between them, and the pool mean
never moves. Panel B: plotting each arrangement-round's selection gap against
**judge agreement × within-prompt spread** — agreement being the correlation,
inside a single prompt, between the judge's recorded score and the value score,
averaged over that round's prompts — one line fits both arms, gap = 0.86 ×
(agreement × spread) − 0.005 with correlation r = 0.93 over all 646
arrangement-rounds; fitted apart, the slope is 0.85 for arrangement 1 and 0.83
for arrangement 2. Re-arranging does not change the rule that converts spread
into a selection gap; it changes how much spread the judge is shown. This is
counterfactual **selection** on real judge scores — nothing was retrained and no
claim is made here that the value itself moved.

## Source data

- `experiments/spread_at_fixed_mean.json` — every rendered number is recomputed
  by the generator from the top-level `"rows"` list (323 rounds × the `high` and
  `low` arrangement objects); the file's own `"summary"` block is not read.
- Produced by `scripts/analysis_spread_at_fixed_mean.py`, which re-arranges
  logged candidate pools by exact knapsack at a fixed total number of value-1
  candidates and re-runs the selection rule on logged judge scores. The
  underlying rounds come from the logged runs listed in each row's `"file"`
  field (basin-anchor runs on Kaggle and Lightning).
- Report: `docs/reports/report_spread_at_fixed_mean.md`.

## Regenerate

```
cd docs/figures/auto/spread-at-fixed-mean && python3 spread-at-fixed-mean.py
```

Stdlib only; it walks up to the repository root to find `experiments/`.

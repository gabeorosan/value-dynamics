# Within-prompt spread is not a second state variable

**Figure.** In the self-training loop a model produces six candidate answers per
prompt per round and a judge scores each one 0 or 1; the pool mean *q* is the
share of the six the judge scored 1, and the within-pool spread σ is the sample
standard deviation (dividing by n−1) of those six scores. The project has been
treating σ as a state variable alongside the judge's agreement, on the reasoning
that σ is the fuel selection runs on. It is not a separate quantity. When the
candidate scores are binary, σ is not merely bounded by *q* — it equals
√(n/(n−1)) · √(q(1−q)) exactly, and every pool in this corpus has n = 6, so only
seven pools can occur at all. **Top panel:** each of the 1,248 prompt-rounds is
plotted at its own (q, σ); they collapse onto seven dots (areas ∝ 189, 195, 204,
247, 234, 132, 47 prompt-rounds, summing to 1,248) which lie on the single curve
σ = √(6/5)·√(q(1−q)). The x tick marks draw the pool itself — six squares, *k*
of them filled — so the horizontal position *is* the count of 1s. This is
arithmetic, not a fit: running the check on the corpus rather than asserting it,
the largest gap between a measured σ and the formula across all 1,248 rows is
1.1 × 10⁻¹⁶, against a plot resolution of 0.0020 of spread per pixel. 236 pools
(18.9%) are unanimous and sit on the floor at σ = 0. **Bottom panel:** the same
seven positions, now counted, for round 1 (open bars) and round 4 (filled bars)
of the loop, with the change in pool count printed above each pair. Selection
moves mass out of the middle of the scale (−33 pools at three-of-six, −22 at
two-of-six) and into the ends (+21 at zero-of-six, +34 at five-of-six, +10 at
six-of-six); unanimous pools go from 14.4% of prompt-rounds to 24.4%. Because
the top panel's curve is low at the ends, that migration *is* the loss of fuel:
mean spread falls 0.430 → 0.403 → 0.389 → 0.365 across the four rounds while the
mean distance of *q* from 0.5 rises 0.200 → 0.237 → 0.256 → 0.268. The pool mean
itself barely moves on average (0.424 → 0.452) because different runs polarise
in opposite directions. Round is a count of selection steps and not a clock:
taken alone, the round index accounts for 0.002 of the variance in pool means,
against 0.456 for the prompt and 0.502 for the run (nested one-way shares that
overlap and do not sum to 1). The identity is exact for 0/1 candidate scores
only; every row in this corpus is scored that way, and graded scores would be a
different question this data cannot answer.

## Source data

- `experiments/spread_supply.json` — `binary_identity_check` (rows_checked
  1,248; max_absolute_deviation 1.1102230246251565e-16), `binary_share_of_rows`
  (1.0), `zero_spread_share` (0.1891), `by_round.pool_mean`,
  `by_round.raw_spread`, `by_round.distance_of_pool_mean_from_half`,
  `decomposition.pool_mean` (prompt 0.4561 / run 0.5023 / round 0.0020),
  `prompt_stability_across_runs.pool_mean` (split-half r = +0.920
  [+0.887, +0.948], 200 splits).
- `scripts/analysis_spread_supply.py` — `collect()` re-run against the raw
  per-candidate logs to get the per-pool counts that are not in the JSON: the
  number of prompt-rounds at each of the seven possible pool means, overall and
  per round. Every row returned has `n_cand = 6`, which is what makes the seven
  levels the only ones possible and lets one curve serve all rows. Those counts
  are carried as literals in `spread-is-the-mean.py` with that provenance noted
  in its docstring; the round-level and identity numbers are read back from the
  JSON at render time and cross-checked against embedded copies.
- Background: `docs/reports/report_spread_supply.md`.

Regenerate with `python3 spread-is-the-mean.py` from this directory (stdlib
only).

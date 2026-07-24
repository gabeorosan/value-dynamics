# Candidate spread is pinned by the pool mean

**Caption.** Every dot is one round of one selection loop on a binary-scored
value axis: the model writes 5–6 candidate answers for each of that round's 12
prompts, and the value scorer gives every candidate a 0 or a 1 on the risk
axis. The horizontal position is the **pool mean** — the average of those
scores over all candidates in the round, i.e. the share of candidates scored 1.
The vertical position is the **candidate spread** the project's movement law
uses — the standard deviation of the scores within one prompt (population
standard deviation, divisor equal to the candidate count), averaged over that
round's 12 prompts. The dashed curve is the arithmetic ceiling, the square root
of pool mean × (1 minus pool mean): a mean within-prompt standard deviation of
0-or-1 scores can never exceed it, so the ceiling is a bound, not a fit. The
solid green curve is fitted — least squares through the origin against that
ceiling — and its single coefficient is **0.813**, which alone accounts for
**85.9%** of the variance in spread. Black squares with whiskers are the mean
and plus/minus one standard deviation of spread inside each 0.1-wide bin of
pool mean (13–55 rounds per bin); comparing within-bin variance with total
variance, **87.6%** of the variance in candidate spread is accounted for by the
pool mean alone, with the standard deviation of spread falling from **0.139**
across all 280 rounds to **0.049** inside a single bin. Condition: 280
binary-scored rounds from 59 selection-loop runs (run = organism × axis ×
condition × seed × source file), two model families — Qwen3-4B (64 rounds) and
OLMo-3-7B (216 rounds) — risk axis, every judge condition in the file pooled,
nothing excluded except rounds whose value axis was not scored 0-or-1. The
figure is descriptive: it shows that spread and pool mean move together, not
that either causes the other.

**Source data.** `experiments/spread_util_unified.json`, the `records` list,
filtered to `binary_score_fraction == 1.0` (280 of 340 records); fields used are
`pool_mean`, `spread`, `organism`, `axis`, `cond`, `seed`, `source`, `n_items`,
`candidate_count_min`, `candidate_count_max`. The `spread` definition is the one
computed in `scripts/analysis_spread_util_unified.py` (`spread =
metrics["mean_item_sd"]`, mean within-prompt population standard deviation); the
run key matches `scripts/analysis_spread_value_centrality.py`. Regenerate with
`python3 spread-pinned-by-pool-mean.py` from this directory (stdlib only; every
number in the figure is recomputed from the JSON at draw time).

**Numbers that differ from the spawn brief.** The brief said 74 runs, 89.2% of
variance, and a within-bin standard deviation of 0.046. Recomputed from the
file: the 280 binary rounds come from **59** runs (74 is the file's `n_runs`
over all 340 records, which include 60 continuous-score rounds); the within-bin
standard deviation is **0.0488** and the corresponding variance share is
**87.6%** (the 89.2% figure in `experiments/spread_value_centrality.json` is
`pooled_ols/self_only/pool_centrality/r2`, i.e. the self-only subset fitted on
pool mean × (1 minus pool mean), not the all-rounds fit). The figure plots the
recomputed values. The brief's 0.813 coefficient and 0.139 overall standard
deviation reproduce exactly (0.8132 and 0.1385).

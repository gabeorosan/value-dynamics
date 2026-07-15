# Same seeds, same judge — only the pool differs

A matched-pair (twin) experiment on a Qwen insecure-code organism whose
self-generated candidate pool had fully homogenized (candidate value spread
0.000). Four more oracle-judged rounds were run in two arms with the same
seeds (921 and 922) and identical random streams up to the injection step:
the **self-only twin** keeps the pool as the organism's own answers; the
**injected** arm has a frozen base model supply half of the candidate pool.
Left panel: candidate value spread by round (mean within-item standard
deviation of candidate value scores, the preregistered formula). The twin
stays at exactly 0.000 every round; injection restores spread to about 0.31
in round 1 (0.313 and 0.304 for the two seeds), settling near 0.07–0.13
afterwards. Right panel: the measured value entering each round (0-to-1
oracle score scale). The twin barely moves (0.627 to 0.625, mean absolute
per-round drift 0.0006), while the injected arm falls from 0.627 to 0.000
after a single round in both seeds (mean absolute per-round drift 0.157).
Because the arms differ only in pool composition, the movement is
attributable to the injected candidates, not to the judge or sampling noise.

Source data: `experiments/spread_util_unified.json`, records with
`cond = "mixed_reopen_twin_selfonly"` (twin) and `cond = "mixed_reopen_qwen"`
(injected), seeds 921 and 922, fields `spread`, `value`, `drift`, `round`
(field definitions in `scripts/analysis_spread_util_unified.py`).

# Every intervention moved one dial: spread or agreement

The **selector gap** a loop round applies — kept-target value minus whole-pool
value, a measured quantity, not a force — decomposes into two dials, the
candidate pool's value spread σ (the within-question standard deviation of the
pool's value scores) times the judge's agreement ρ with the value (the
correlation of its keep choices with the value axis; 0 is random keeping, −1 is
the score oracle that always keeps the two lowest scorers): selector gap ≈
agreement × spread. That product explains 81% of the selector gap over the 290
logged rounds with a defined ρ (r² 0.812; ρ alone 0.594, σ alone 0.030; the
single retracted point-estimate coefficient is deliberately not printed). Each
measured intervention moved one dial. Each series names its model and value in
the plot; the four moves span three model×value settings. On the **OLMo
risk-seeking** organism, swapping the judging format from judging against a
fixed alternative to head-to-head duels (same cautious fine-tuned-copy judge,
same base-mixed pools) moved only agreement, +0.38 → +0.10, while spread stayed
at 0.33–0.37. On the **Qwen insecure-code** organism, injecting base-model
answers into a collapsed pool (same seeds, same score oracle) restored spread
0.00 → 0.31 with agreement pinned at −1.0 by construction — but this is **not a
pure spread reset at fixed everything else**: injection simultaneously shifts
the pool supply (the kept targets now move relative to the model's own
candidates) and adds *between-source* spread, and between-source variance is a
real share of the mixed pool's within-prompt variance (34% base-mixed over 64
rounds, 57% peer-mixed over 32 rounds; experiments/spread_conversion_model.json,
mixed_pool_variance_decomposition). Back on **OLMo risk-seeking**, a copy of the
model railed to the max-risk extreme, supplying three of every six candidates
(half of each pool), consumed spread as the host converged to it, 0.43 → 0.06
over three rounds at roughly constant agreement (+0.40 to +0.53); the
between-source spread between host and supplier *shrinks* over rounds as the two
sources' means approach each other (this invasion trajectory is drawn in the
conversion-chain figure, not on this plane). And on **Qwen insecure-code**, when
the organism judged its own duels with base text present, agreement went
negative (−0.24): selection eroded the organism's own value. Ordinary frozen
model judges (OLMo and Qwen, risk-seeking) cluster near agreement 0. All numbers
are per-cell or per-round means from experiments/spread_util_unified.json
(agreement table, spread_ledger, matched reopen-versus-twin pair, and the pooled
decomposition); the between-source variance shares are from
experiments/spread_conversion_model.json.

Source data: experiments/spread_util_unified.json and
experiments/spread_conversion_model.json (between-source variance shares). Clean
redraw of docs/figures/auto/two-dials-interventions/. Regenerate with
`python3 two-dials-clean.py`.

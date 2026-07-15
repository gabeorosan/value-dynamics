# Agreement is organized by the judge setup — but not safe to freeze

The selection gap factors into the pool's value spread σ times the judge's
agreement ρ (the within-item correlation between the judge's candidate scores
and the candidates' value scores; −1 keeps the low-value side, +1 the high
side). This single-panel figure shows the ρ factor over rounds. Within a run ρ
barely moves relative to how far it differs between judge setups: each judge ×
format × pool cell's per-round mean (fat line, drawn over its faint individual
runs) stays near its own level — score oracle −1.00 (within-run SD 0.00),
self-judge duels with base text −0.24 (0.08), frozen copy +0.04 (0.05), base
judge on non-invasion pools +0.06 (0.17), cautious copy on a mixed pool +0.38
(0.07), self-judge under extremist-copy peer invasion +0.53 (0.10). 82% of
agreement's variance is between judge cells, not between rounds
(`between_cell_variance_share_rho` = 0.817). The one exception is drawn dashed:
a single base-judge run whose agreement bloomed mid-run, ρ 0.01 → 0.27, then
fell back.

That structure makes round-1 agreement a useful first estimate, but it is not
safe to freeze. In the closed-loop rollout test (selection-driven endpoints,
whole condition held out), freezing round-1 agreement leaves endpoint MAE at
0.139; supplying the simulator with later *observed* agreement cuts it to 0.115,
while supplying later observed *spread* does not move it (0.139). The missing
state for accurate multi-round endpoints is agreement's later within-run drift,
not spread — so agreement is depicted here as slowly drifting, not stationary.

Source data: `experiments/spread_util_unified.json` — ρ per round computed from
`records` (fields rho, round, judge, format, composition; runs grouped by
cond × seed × source), the 82% takeaway from
`agreement.between_cell_variance_share_rho`. Rollout diagnostic from
`experiments/spread_rollout_bakeoff.json`
(`error_attribution_by_metric.mean_within_prompt_population_sd.leave_one_condition_out`).
Generator: `two-clocks-spread-util.py` (stdlib only, run from this directory).

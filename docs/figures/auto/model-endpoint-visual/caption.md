# model-endpoint-visual

**The selection-loop endpoint recurrence, shown as motion on the value line
instead of as an equation.** Each round moves the current population-mean value
`m` by two forces and then clips it to the walls:

> `m_next = clip( (1 − u)·m + u·s + ρσ , 0, 1 )`

where `u` is the fraction of next round's pool drawn from an outside supplier,
`s` is that supplier's value level, `ρ` is the correlation between an answer's
value and the judge's score (the selection pressure's sign and strength), and
`σ` is the within-prompt spread of scores. Reading the two moved terms: `u·s`
mixes the mean a fraction `u` of the way toward the supplier's level, and `ρσ`
is the selection step. **Part 1** draws this as motion: in a mixed pool the
value climbs toward the supplier and then flattens at the height where the
mixing pull and the selection step cancel; in a self-only pool (`u = 0`) it is
a plain staircase of equal `ρσ` steps until it hits a wall at 0 or 1.

**Part 2** rolls the recurrence forward on three archetypal held-out runs,
each started from its own first pool with `σ` and `ρ` **measured once and never
re-measured** (dashed = predicted, solid = observed) — the observed value line
walks the predicted path in all three: a peer-invasion run
railing to 1.0 (half the pool from a risk-railed peer, self-judge duels,
OLMo), the base-model injection collapse (base answers injected at round 1,
oracle-scored, Qwen — 0.627 → 0.000 in one round), and an oracle-opposition
reversal (self-only pool, oracle scoring against the trained value, Qwen —
1.00 → 0.33 over four rounds). The **boundary-refresh rule**: `σ` and `ρ` are
re-measured exactly once, only when the judge is swapped mid-run (the
`judge_swap` / `press_*` runs, excluded from the panels here); within a fixed
judge the two are frozen at their round-1 values.

Across the 36 selection-driven held-out runs the recurrence lands the endpoint
within **0.118** mean-absolute error, versus **0.431** for the null that the
value never moves (endpoint value on the 0–1 scale).

## Source data (numbers read from files at build time, not transcribed)

- Predicted per-round trajectories, `start`, and regime labels:
  `experiments/selection_response_predictor.json`
  → `endpoint_with_boundary_refresh.recommended_unit_agreement_spread.per_run`
  (run_keys `h2h_invade_self|53|...`, `mixed_reopen_qwen|921|...`,
  `judge_opposition_oracle|101|...`).
- Observed per-round values (`value_after_true`) and condition metadata
  (`cond` / `judge` / `composition` / `organism` / `axis`, `v1`, `n_rounds`):
  `experiments/spread_rollout_bakeoff.json`
  → `validations.leave_one_condition_out.frozen.mean_within_prompt_population_sd.per_run`.
- Aggregate endpoint errors (0.1181, 0.4309, n = 36):
  `experiments/unit_rollout_properties.json`
  → `endpoint_only_matched_45.by_regime_group.selection_driven`.

Regenerate with `python3 model-endpoint-visual.py` from this directory
(stdlib only; reads the three JSONs above via a path relative to the script).
Part 1 is a schematic (illustrative marks, not fitted to a specific run); all
Part 2 curves and the evidence line are read live from the files.

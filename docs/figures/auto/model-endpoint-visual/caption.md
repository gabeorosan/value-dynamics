# model-endpoint-visual

**The selection-loop endpoint recurrence, shown as motion on the value line
instead of as an equation — then rolled forward on real held-out runs.** Each
round moves the current population-mean value `m` by two forces and then clips
it to the walls:

> `m_next = clip( (1 − u)·m + u·s + ρσ , 0, 1 )`

where `u` is the fraction of next round's pool drawn from an outside supplier,
`s` is that supplier's value level, `ρ` is the correlation between an answer's
value and the judge's score (the selection pressure's sign and strength), and
`σ` is the within-prompt spread of scores. Reading the two moved terms: `u·s`
mixes the mean a fraction `u` of the way toward the supplier's level, and `ρσ`
is the selection step.

**Part 1** draws this as motion (illustrative schematic, not fitted to a
specific run): in a mixed pool the value climbs toward the supplier and then
flattens at the height where the mixing pull and the selection step cancel — the
"balance point"; in a self-only pool (`u = 0`) it is a plain staircase of equal
`ρσ` steps until it hits a wall at 0 or 1.

**Part 2** rolls that same one-round move forward on three archetypal held-out
runs, each started from **only its own first-round pool state** — own candidate
mean `q`, own within-prompt spread `σ` (`own_spread`), agreement `ρ`, and
behavioral value `v` — never looking at that run's later rounds. Three marks per
panel: the **observed** value each round (solid black with dots); the
**deterministic path** `k = clip(pool + ρσ)` with `σ` and `ρ` frozen at round 1
(dashed blue), a conditional mean that is too smooth on its own; and the
**predictive band** (light blue, 10–90% quantiles over 500 seeded stdlib draws)
— the *same* recurrence with noise added only where the measurement implies it,
following the committed staged-noise recipe (a selector-gap innovation on
`gap = ρ·σ`, a generated-mean innovation on the `q` update, a round-to-round
drift on agreement `ρ`, and observation noise `sqrt(v(1−v)/n)` on the *reported*
value only, `n` = the round's value-measurement battery size, not fed back into
the state). Every innovation scale is the standard deviation of a
leave-one-condition-out residual pool rebuilt from the committed records, so the
band uses the committed noise scales, not invented ones. The three runs span two
organisms and three regimes: **A** (OLMo, cautious-copy judge, risk axis,
round-1 `ρ = −0.17`) hovers low; **B** (Qwen, self-judge, self-report axis,
`ρ = +0.32`) climbs to the ceiling; **C** (Qwen, score-oracle judge, self-report
axis, `ρ = −1.00`) falls under the opposing judge. In all three the observed
trajectory stays inside the band and the dashed mean tracks the direction and
rough endpoint from round 1 alone.

**Boundary-refresh rule.** Within a fixed judge, `σ` and `ρ` are frozen at their
round-1 values; they are re-measured exactly once, only when the judge is swapped
mid-run (the `judge_swap` / `press_*` runs, not shown as panels here).

## The two evidence numbers are from two different held-out sets

The evidence line carries the two committed anchors, and their denominators are
**different sets on purpose**:

- **Endpoint error 0.118** (mean-absolute error of the final-round value on the
  0–1 scale) is over the **36 selection-driven** held-out runs
  (`unit_rollout_properties.json`, `by_regime_group.selection_driven`,
  `unit_recurrence_endpoint_mae` = 0.1181, `n_runs` = 36). For reference, the
  null that the value never moves lands at 0.431 on the same set.
- **Coverage 89% and CRPS 0.092** are over the wider **45 selection-driven +
  judge-swap** primary set
  (`trajectory_adjustment_bakeoff.json`,
  `primary_selection_driven_plus_swap.unit_core_selector_q_observation_rho_persistence_gaussian`,
  `endpoint_80pct_coverage` = 0.8889, `endpoint_crps` = 0.091743, `n_runs` = 45).
  The deterministic path alone covers only 22% of endpoints (CRPS 0.135) at the
  same nominal-80% band; the staged noise is what makes the interval calibrated.

A latent value-process kick and a risk-feedback `ρ` term were both tried and
rejected as post-hoc — they do not improve held-out accuracy — so the band adds
noise at exactly the four measured stages and nowhere else.

## Source data (numbers read from files at build time, not transcribed)

- `experiments/spread_util_unified.json` — Part 2 per-run first-round state
  (`own_mean`, `own_spread`, `rho`, `value`, `pool_cogen_fraction`,
  `cogen_mean`, `next_value_measurement_n`), per-round observed values
  (`value + drift`), and the records used to rebuild the
  leave-one-condition-out residual pools (`gap`, `mean_item_sd`,
  `self_relative_gap`). Panel runs: `frozen_cons_r0` seed 2,
  `selfaware_loop_grid` seed 44, `judge_opposition_oracle` seed 101.
- `experiments/trajectory_adjustment_bakeoff.json` —
  `primary_selection_driven_plus_swap.unit_core_deterministic` and
  `.unit_core_selector_q_observation_rho_persistence_gaussian` (the asserted
  endpoint CRPS 0.135 / 0.092 and 80%-band coverage 0.22 / 0.89 over 45 runs).
  Recipe replicated from `scripts/analysis_trajectory_adjustments.py`, variant
  `unit_core_selector_q_observation_rho_persistence_gaussian`.
- `experiments/unit_rollout_properties.json` —
  `endpoint_only_matched_45.by_regime_group.selection_driven`
  (endpoint MAE 0.1181 vs null 0.4309, n = 36).

Regenerate with `python3 model-endpoint-visual.py` from this directory (stdlib
only; reads the three JSONs above via a path relative to the script). Part 1 is
a schematic (illustrative marks); all Part 2 curves, the band, and the two
evidence numbers are read live from the files and asserted at build time.

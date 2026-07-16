# Closed-loop rollout: observed trajectories vs the rolled-forward forecast, with noise where measurement implies it

Each panel is one held-out run, plotted as a trajectory rather than a bar of
metrics. The forecast reads **only that run's first-round pool state** — own
candidate mean `q`, own within-prompt spread `sigma` (`own_spread`), agreement
`rho`, behavioral value `v`, and for mixed pools the supplier share `u` and
supplier mean `s` — and never looks at the run's later rounds. It then rolls the
parameter-free **unit recurrence** forward: pool `p = (1 − u)·q + u·s` (self-only
here, so `p = q`); kept mean `k = clip(p + rho·sigma, 0, 1)`; next `q` = next
value = `k`; `sigma` frozen at round 1. That single **deterministic path**
(dashed blue) is a conditional mean and is too smooth. The shaded **predictive
band** (light blue, 10–90% quantiles over 500 seeded draws) is the *same*
recurrence with noise added only where the measurement implies it, following the
committed staged-noise recipe: a selector-gap innovation on `gap = rho·spread`, a
generated-mean innovation on the `q` update, a round-to-round drift on agreement
`rho`, and observation noise `sqrt(v(1−v)/n)` on the *reported* value only (with
`n` the round's value-measurement battery size), not fed back into the state.
Every innovation scale is the standard deviation of a leave-one-condition-out
residual pool rebuilt from the committed records, so the band uses the committed
noise scales, not invented ones.

The three runs are chosen to be diverse and span two organisms: **A** (OLMo,
cautious-copy judge, risk axis, `rho = −0.17`) hovers low; **B** (Qwen, self
judge, self-report axis, `rho = +0.32`) climbs to the ceiling; **C** (Qwen,
score-oracle judge, self-report axis, `rho = −1.00`) falls under the opposing
judge. In all three the observed trajectory stays inside the band, and the
dashed mean already tracks the direction and rough endpoint from round 1 alone.
The evidence line reports the committed aggregate: across all 45
selection-driven + judge-swap held-out runs, the deterministic mean path alone
covers the observed final-round value in **22%** of runs at a nominal-80% band
(endpoint CRPS **0.135**); adding the staged noise raises coverage to **89%** and
cuts CRPS to **0.092** (lower CRPS is better; 80% is the calibration target). A
latent value-process kick and a risk-feedback `rho` term were both tried and
rejected as post-hoc — they do not improve held-out accuracy — so the band adds
noise at exactly the four measured stages and nowhere else.

**Note on reproduction.** The committed bake-off
(`scripts/analysis_trajectory_adjustments.py`) ran 400 numpy Monte-Carlo paths
under leave-one-condition-out over the full 45-run primary set (mixed-pool and
judge-swap runs included). The panels here regenerate the deterministic path and
band with pure stdlib for three self-only runs, using the identical unit
recurrence and the identical residual-pool noise scales; the headline
CRPS/coverage numbers are read and asserted straight from the committed JSON, not
recomputed. The stdlib reproduction's own endpoint-band coverage over the
self-only held-out runs is 94%, consistent with the committed 89% over the wider
set.

## Source data

- `experiments/spread_util_unified.json` — per-run first-round state (`own_mean`,
  `own_spread`, `rho`, `value`, `pool_cogen_fraction`, `cogen_mean`,
  `next_value_measurement_n`) and per-round observed value trajectories
  (`value + drift`); also the records used to rebuild the leave-one-condition-out
  residual pools (`gap`, `mean_item_sd`, `self_relative_gap`).
- `experiments/trajectory_adjustment_bakeoff.json` —
  `primary_selection_driven_plus_swap.unit_core_deterministic` and
  `.unit_core_selector_q_observation_rho_persistence_gaussian` (the asserted
  endpoint CRPS 0.135 / 0.092 and 80%-band coverage 0.22 / 0.89 over 45 runs).
- Recipe replicated from `scripts/analysis_trajectory_adjustments.py` (variant
  `unit_core_selector_q_observation_rho_persistence_gaussian`).

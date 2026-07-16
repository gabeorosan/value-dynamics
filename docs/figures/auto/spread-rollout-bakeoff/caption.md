# Closed-loop rollout: what the parameter-free unit recurrence predicts, and what noise restores

One model, no fitted trajectory parameters. The simulator reads the held-out
condition's first pool once — its within-prompt population SD (spread) and its
agreement (rho) — then rolls the unit recurrence
`m_next = clip((1 - u)*m + u*supplier + rho*sigma)` forward, with the forecast's
next value given by the kept-mean identity. It reads none of that run's later
candidates, spread, agreement, or value. Validation is leave-one-condition-out:
the entire intervention/judge regime is held out.

Panel A (endpoint MAE = mean absolute error of the predicted final behavioral
value vs the true final value on the 0-1 scale, lower better): the unit
recurrence scores 0.118 vs 0.431 no-change on 36 selection-driven runs, 0.114 vs
0.450 on 24 mixed-intervention runs, 0.126 vs 0.393 on 12 strong-agreement
self-only runs, and 0.211 vs 0.215 on 22 weak self-only runs (it ties the
regime that barely moves). A mid-run judge change is new information the round-1
forecast cannot contain: on the nine judge-swap runs, restarting the unit
recurrence at the boundary (re-measuring the full state on the first pool the
replacement judge scores) lands at 0.210 vs 0.361 no-change, recovering 6/7
post-swap movement directions. The roll-blindly-from-round-1 (0.404) and
hold-swap-time-fixed (0.309) bars are the FITTED frozen-mean-SD variant, kept
only as the pre-swap comparator — the unit rollout itself starts at the
boundary.

Panel B (45 selection-driven + judge-swap runs): the deterministic unit rollout
is a conditional mean and is too smooth — total path variation 0.499 vs 0.648
observed, 0.18 vs 1.20 sign reversals — but it gets the coarse endpoint (37/38
large-movement directions correct graded from the forecast's last state
measurement; 21/24 observed rail endpoints recovered; deterministic endpoint
mean 0.586 vs observed 0.541). The staged stochastic forecast (selector-gap and
generator-mean residuals, a zero-mean agreement innovation around persistence,
and finite-battery observation noise on the reported value without feeding it
back) restores realistic paths (variation 0.709, 1.22 reversals) and calibrated
endpoints (CRPS 0.092, and 89% of runs inside its nominal-80% band). The
deterministic model's endpoint CRPS is 0.135; its nominal-80% "coverage" (0.22)
is a point-forecast artifact of exact rail hits — a deterministic path has no
interval — so it is omitted from the coverage panel, which shows the staged
model's coverage against the 80% target only. A latent value-process kick and a
`rho_next ~ rho + rho*spread` risk-feedback term are both omitted as post-hoc
(they do not improve held-out accuracy).

Sources (numbers read and asserted at these paths, not transcribed):
`experiments/unit_rollout_properties.json`
(`endpoint_only_matched_45.by_regime_group` and `.unit_recurrence`),
`experiments/spread_rollout_bakeoff.json`
(`judge_swap_refresh.leave_one_condition_out.mean_sd_frozen` — the fitted
pre-swap comparators and 6/7 direction node), and
`experiments/trajectory_adjustment_bakeoff.json`
(`primary_selection_driven_plus_swap.unit_core_deterministic` and
`.unit_core_selector_q_observation_rho_persistence_gaussian`).

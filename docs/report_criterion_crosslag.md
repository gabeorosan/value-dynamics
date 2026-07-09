# Cross-lag re-test on matched-content data: the criterion does NOT lead behavior — clean null, lead-lag study parked

Requested by Lit&planning (recipe: docs/plan_recovered_threads.md §2), relayed
time-sensitive by Figures 2026-07-09: this verdict gates the planned dedicated
criterion lead-lag study (fig12 Kaggle card, next_directions_assessment.md
item 2). **Verdict: clear null → park it.**

Write-up hygiene per the plan: the packet-loop version of the "criterion moves
before behavior" claim stays retired (its instrument drift was content-carried).
This is the matched-content re-test on **self-generation-loop** data the
retirement note asked for.

## Data and measures

Pooled basin ensembles: `kaggle_basin_anchor` (seeds 0–7, both judge
conditions), `kaggle_basin_anchor_ext` (8–14, self-judge),
`basin_anchor_lightning_23_31` (23–30, both), `basin_anchor_lightning_15_23`
(seed 15) — 24 self-judge and 16 frozen-judge Qwen rollouts, 6 rounds each;
OLMo-3-7B (`basin_second_model`, 4+4 rollouts) analyzed separately. Per round,
each rollout logs:

- **coordinate** = risk (P choose riskier option on held-out EV-neutral A/B
  gambles) — `traj`;
- **criterion** = mean `rating_diff_B_minus_A` over the battery's fixed rated
  pairs;
- **self_report** = `p_risk_tolerant`.

Cross-lags pool round-transition pairs (x_t, y_{t+1}) across seeds within judge
condition. Two estimators: the requested raw correlations, and a trend-robust
partial version (standardized beta of x_t on y_{t+1} controlling y_t — the
cross-lagged-panel form; raw pooled correlations can manufacture "leads" out of
shared trends). CIs by cluster bootstrap over rollouts (2000 reps), since
transitions within a rollout are not independent.

## Result: nothing leads anything — every interval spans zero

Qwen, partial betas with 95% cluster-bootstrap CIs:

| condition | direction | beta [95% CI] |
|---|---|---|
| self-judge | criterion_t → risk_{t+1} | −0.055 [−0.193, +0.066] |
| self-judge | risk_t → criterion_{t+1} | +0.066 [−0.045, +0.169] |
| self-judge | self_report_t → risk_{t+1} | −0.007 [−0.158, +0.130] |
| self-judge | risk_t → self_report_{t+1} | +0.091 [−0.002, +0.161] |
| frozen-judge | criterion_t → risk_{t+1} | −0.012 [−0.161, +0.120] |
| frozen-judge | risk_t → criterion_{t+1} | +0.003 [−0.175, +0.197] |
| frozen-judge | self_report_t → risk_{t+1} | +0.028 [−0.101, +0.185] |
| frozen-judge | risk_t → self_report_{t+1} | +0.065 [−0.089, +0.228] |

Raw correlations tell the same story (all |r| ≤ 0.35, and the raw asymmetries
that exist favor the *reverse* direction, behavior → instrument: e.g.
frozen-judge self_report raw pair +0.298 lead vs +0.345 lag). OLMo (n=8
rollouts, low power): same picture, all partial betas within ±0.12, no
consistent sign.

The one borderline cell is the **reverse** of the retired claim: risk_t →
self_report_{t+1} under the self judge, +0.091 [−0.002, +0.161] — weakly
suggestive that behavior drags the self-report along a round later, not the
other way around. Consistent with the deflationary reading: the
criterion/self-report channel is downstream or parallel, not a leading
indicator.

## What this decides

- **The dedicated criterion lead-lag study (graded multi-item battery, 5–8
  rounds) is parked.** Its premise — a lead signal worth resolving at higher
  resolution — is absent in 40 matched-content rollouts across two judge
  conditions.
- If the criterion channel returns, it should be via the battery patch's
  `judgment_taste` block (fixed-pair judge-taste measurement), which measures
  the judge channel directly instead of inferring it from lag structure — and
  any revival must cite the packet-loop retirement and rest only on
  self-generation-loop data (this doc).
- The weak behavior→self-report direction, if anyone cares to chase it, is the
  self-aware-grid territory (where selection ON self-report actively amplifies
  it) rather than lag-mining territory.

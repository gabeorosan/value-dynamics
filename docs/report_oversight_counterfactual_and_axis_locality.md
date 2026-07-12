# Oversight counterfactual, axis-locality, and the K2 cross-stack merge

*2026-07-12 ~18:00, general thread. Three analyses on landed K2/K3 data, no
new compute. Companions to docs/report_loop_integrator_decomposition.md.*

## 1. The conservative judge would have reversed the selection direction on every realized rail pool

*(Wording corrected per the 2026-07-12 re-audit: this analysis identifies the
one-step FORCE SIGN on the realized pools, not the full alternate trajectory —
switching the judge at round 1 would have changed the training data and every
later pool, so "would have prevented the rail" does not follow from same-pool
re-scoring. The dynamical version of this counterfactual is exactly what the
Modal `press_to_base` / judge-swap cells test.)*

K2's frozen-base arm is bimodal: 2 of 6 seeds rail upward (r4 = 0.688, 0.802)
while the rest settle low. Because every rollout also scored what the
**conservative judge would have kept on the identical candidate pool**
(`gap_cons_judge`), we can ask what selection direction a safety-tasted
overseer would have applied to the pools that actually occurred.

Per-round kept-gap, base (realized) vs conservative (counterfactual), summed
over the 4 training rounds:

| base-arm seed | realized traj r0→r4 | base Σ kept-gap | cons WOULD Σ kept-gap |
|---|---|---|---|
| s5 (RAIL) | 0.234→0.802 | **+0.43** | **−0.65** |
| s2 (RAIL) | 0.211→0.688 | **+0.57** | **−0.26** |
| s0 | 0.269→0.188 | +0.12 | −0.21 |
| s1 | 0.240→0.146 | +0.11 | −0.47 |
| s3 | 0.239→0.062 | −0.12 | −0.54 |
| s4 | 0.245→0.062 | −0.22 | −0.26 |

In **both** rail seeds the base judge accumulated a large positive kept-gap
(the selection direction that preceded the rail each round), while the
conservative judge on those same pools would have kept **strongly negative
every single round** — it never once, in any seed, had a positive cumulative
gap. On every realized rail pool, a conservative overseer would have selected
in the opposite direction.

The oversight-relevant read: the per-round selection direction was not a
property of the pool (the risky candidates that fed it were present for the
conservative judge too) — it was a property of *which installed value did the
selecting*. Same material, opposite per-round force by judge taste. Caveats:
n=2 rails (existence demonstration, not a rate); and force-sign reversal on
realized pools does not by itself establish the alternate trajectory — that
is the running press_to_base experiment's question.

## 2. Local predictive specificity: the pool variable predicts its own axis, not the probes

*(Renamed from "the law of the selected axis" per the re-audit: the near-zero
off-axis correlations show the pool coordinate doesn't PREDICT those channels,
not that loops cannot move them — K3's own self-report endpoint variance is
large. The neutral judges were also never instructed to optimize the scored
coordinate, and pooled contemporaneous correlations mix conditions.)*

Behavior tracks the pool coordinate the loop selects on far better than the
tested off-axis probes:

| coordinate relationship | Pearson r | n |
|---|---|---|
| K2 selected: risk pool → risk behavior | **+0.79** | 60 |
| K3 off-axis: candor pool → self-report insecurity | +0.01 | 48 |
| K3 off-axis: candor pool → em_choice misalignment | +0.09 | 48 |

Other value coordinates move (or fail to move) in ways the pool variable does
not see. This makes **channel dissociation unsurprising** — K3's self-report
fan, the let-go free-gen rails sitting untouched while em_choice floored, and
the transmission cells' flat primary channels are all coordinates the selected
force never addressed. The practical safety point survives in weakened form:
a probe channel's stillness is not evidence about channels the loop's pool
variable doesn't predict.

## 3. K2 cross-stack merge is clean

frozen_cons_r0 round-0 generated-channel baseline, pooled across the two
compute stacks that ran the confirmatory six (Cerebrium seed 0 + Kaggle
seeds 1–5): mean **0.234**, sd **0.011**, range 0.211–0.245. The between-stack
spread is a third of the 0.03 merge threshold, so the Cerebrium seed-0
trajectory and the Kaggle confirmatory seeds are poolable as one contrast on
the generated channel. (Forced-channel reads are excluded from any merge —
order-confounded across both stacks, see report_k1_first_read.md.)

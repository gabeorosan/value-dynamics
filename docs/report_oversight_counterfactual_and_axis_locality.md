# Oversight counterfactual, axis-locality, and the K2 cross-stack merge

*2026-07-12 ~18:00, general thread. Three analyses on landed K2/K3 data, no
new compute. Companions to docs/report_loop_integrator_decomposition.md.*

## 1. A conservative oversight judge would have caught both base-judge rails

K2's frozen-base arm is bimodal: 2 of 6 seeds rail upward (r4 = 0.688, 0.802)
while the rest settle low. Because every rollout also scored what the
**conservative judge would have kept on the identical candidate pool**
(`gap_cons_judge`), we can ask counterfactually whether a safety-tasted
overseer riding alongside the base judge would have prevented the escape.

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
(the force that, integrated at k≈0.75, drove the rail), while the
conservative judge on those same pools would have kept **strongly negative
every single round** — it never once, in any seed, had a positive cumulative
gap. A conservative overseer given veto over the same candidates would have
reversed the force sign on both rails and prevented the escape entirely.

This is the oversight-relevant read of the integrator: the rail was not a
property of the pool (the risky candidates that fed it were present for the
conservative judge too) — it was entirely a property of *which installed
value did the selecting*. Same material, opposite outcome by judge taste.
Caveat: n=2 rails; this is an existence demonstration on the six base seeds,
not a rate estimate.

## 2. The integrator law is a law of the SELECTED axis only

Behavior tracks the pool coordinate the loop selects on, and essentially
nothing off it:

| coordinate relationship | Pearson r | n |
|---|---|---|
| K2 selected: risk pool → risk behavior | **+0.79** | 60 |
| K3 off-axis: candor pool → self-report insecurity | +0.01 | 48 |
| K3 off-axis: candor pool → em_choice misalignment | +0.09 | 48 |

The loop moves the coordinate it optimizes; other value coordinates drift by
training side-effects the pool variable cannot predict. This makes **channel
dissociation the expected behavior, not an anomaly** — K3's self-report fan,
the let-go free-gen rails firing while em_choice floored, and the transmission
cells' flat primary channels are all off-axis coordinates that the selected
force never addressed. Any safety claim from one probe channel says nothing
about the others unless that channel is what the loop selects on.

## 3. K2 cross-stack merge is clean

frozen_cons_r0 round-0 generated-channel baseline, pooled across the two
compute stacks that ran the confirmatory six (Cerebrium seed 0 + Kaggle
seeds 1–5): mean **0.234**, sd **0.011**, range 0.211–0.245. The between-stack
spread is a third of the 0.03 merge threshold, so the Cerebrium seed-0
trajectory and the Kaggle confirmatory seeds are poolable as one contrast on
the generated channel. (Forced-channel reads are excluded from any merge —
order-confounded across both stacks, see report_k1_first_read.md.)

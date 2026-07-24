# Invariant weight-geometry reads: the optimizer steps a fixed distance every round — selection steers, it does not push harder

*2026-07-14, general thread. Two ledger debts paid at once
(docs/ANALYSIS_LEDGER.md §D): the integrator report's §5 geometry null
existed only as an unsaved computation, and the withdrawn basin-era
"more motion, less behavioral change" claim had never been re-tested with
gauge-invariant quantities. The K2 chassis persists per-round MERGED-update
geometry (`merged_diff_norm(fac_t, fac_0)` — invariant, unlike the raw
A/B-factor norms that got the original claim withdrawn). Committed scorer:
`scripts/analysis_weight_geometry_invariant.py` →
`experiments/weight_geometry_invariant.json`. Data: 50 OLMo + 16 Qwen
rollouts with geom logs.*

## 1. NEW: weight-motion magnitude carries no selection signature

Per-round step norms are nearly constant — coefficient of variation **0.135**
(OLMo, mean step 1.68) and **0.093** (Qwen, mean 0.86) — and essentially
uncorrelated with that round's selection force: step_norm vs |gap| r = 0.10
(OLMo) / 0.23 (Qwen); vs |ρ·σ| r = 0.02 / 0.24. Ten optimizer steps on two
kept answers move the weights about the same distance whether the judge
selected hard or not at all. **Selection determines the direction of the
update, not its size** — which is why the informative monitoring quantities
are content-side (ρ, σ, gap) and why weight-motion magnitude is useless as a
loop monitor. This also gives the dose-ladder finding a mechanism-side
partner: behavior can saturate while weights keep moving at a constant rate.

## 2. The §5 null, now a committed script

Early motion (step norms r1+r2) vs later behavior (|pool move r2→r4|):
r = −0.16 (OLMo, n=50), −0.18 (Qwen, n=16) — null, matching the integrator
report's unsaved read (r ≈ 0.07 on its 17 rollouts). That row of the ledger
is no longer unverifiable.

Caveat flagged, not resolved: early step vs |TOTAL move| shows −0.45 on OLMo.
This pools kaggle-grid and modal cells whose training configs differ, so it
is cross-cell confounded; within-condition n is too small to settle it. Do
not cite the −0.45 as a finding.

## 3. The withdrawn "more motion, less change" claim stays dead under invariant re-test

The invariant thrash ratio (path_length / net_displacement) vs |total
behavioral move|: r = +0.27 (OLMo) / +0.07 (Qwen) — weak-positive to null,
the OPPOSITE sign of the withdrawn basin-era correlation. With the
gauge-invariant quantities the effect does not reappear. The withdrawal
stands, now with a positive re-test rather than only a methodological
objection.

## Scope

Merged-update norms are global scalars; per-module or subspace structure
(and the dose-ladder geometry: does the update keep growing with dose while
behavior saturates?) still needs the persisted adapters — queued for the
Colab session after the ladder completes, alongside the alpha-scaling mirror
test.

# Fixed-pool cross-judge rescoring, run 1: the validity gate fired (by design), the failure traced to a format mismatch in the gate itself, and a like-for-like re-run is queued

*2026-07-15, general thread. Colab, ~14 min inference on the warm T4 session
(launcher jsdelivr-pinned f024c26f; design experiments/crossjudge_rescoring/SPEC.md,
user-built). Raw: experiments/crossjudge_rescoring/output/crossjudge_rescoring.json
(pulled from Drive). Scorer: scripts/analysis_crossjudge_rescoring.py →
experiments/crossjudge_rescoring/output/analysis_summary.json. Scope, per SPEC and
the 07-14 PLAN edit: descriptive mechanism check on frozen pools. This is NOT — and
by design CANNOT be — a validation that cross-judge agreement predicts trained-model
movement ("infection").*

## What ran

The 48 fixed item pools (288 candidates) from the four saved branch-h invasion
cells (h2h_invade_base seeds 51/52, h2h_invade_self seeds 53/54; source files
SHA-recorded in pools.json `_config`) were re-scored by a four-judge panel —
plain OLMo base, v6_rung20, v8_rung60, v10_rung20 (adapter weights
SHA-verified) — all in the cross-owner head-to-head both-orders duel format,
the format the original selector actually used. For each judge: agreement with
the base source judge (raw Pearson, risk/length-residual, top-2 overlap) and
the counterfactual share of supplier candidates it would have kept.

## The verdict for this run: INVALID_REPRODUCTION (the gate worked)

The SPEC's validity gate requires fresh scores to reproduce the logged online
scores (r ≥ 0.95, top-2 Jaccard ≥ 0.75) before anything is interpreted.
Results:

| reproduction arm | fresh format | vs logged | r | top-2 Jaccard | passes |
|---|---|---|---|---|---|
| v10_rung20 (self cells, actual round-1 recipient) | h2h duels | logged `scores_h2h` | **0.9998** | 0.917 | YES |
| base (all pools) | h2h duels | logged `scores_base` | 0.418 | 0.382 | NO |

Per the SPEC ("failure invalidates the new analysis rather than being
interpreted scientifically"), run 1's association numbers are **not citable**.

## Diagnosis: the base arm compared two judging formats, so it could never pass

Traced in the producing code, not conjectured: the logged `scores_base` in the
branch-h outputs were made by the chassis diagnostic `_judge_scores`
(experiments/kaggle/kaggle_k2_olmo_inversion/script.py, line ~540), which
duels each candidate against the static cautious REFERENCE answer ("I'd take
the guaranteed amount — the certainty is worth more than a gamble."), both
orders. The rescorer scored cross-owner candidate-vs-candidate duels. So
"fresh base vs logged base" compared reference-anchored scoring to duel
scoring — two formats already known to disagree on the same judge
(report_head2head_olmo.md: duels rescue pools that reference-anchored scoring
rails). The v10 arm passes at r=0.9998 because its logged scores
(`scores_h2h`) are the same duel format — which simultaneously certifies that
the rescoring pipeline itself is faithful.

Two useful byproducts:

1. **The r=0.418 is itself a clean replication of the format effect** on new
   material: one judge, same candidates, two judging formats, weakly
   correlated scores. (Cross-format diagnostic now stored explicitly in the
   re-run output.)
2. The pipeline's determinism/fidelity is certified by the v10 arm, so the
   re-run only needs to fix the comparison, not the scoring.

## The fix (committed 490d6477, jsdelivr-verified) and re-run — GATE NOW PASSES

The launcher now scores a fresh **reference-anchored base pass** (identical
recipe to the original `_judge_scores`: candidate vs CAUTIOUS_REF, both
orders) and uses it for the base reproduction arm, keeping the h2h-vs-logged
number as an explicit expected-to-disagree cross-format diagnostic.

The re-run (2026-07-15, resumed from the banked Drive JSON — only the
reference-anchored base pass ran) **PASSES both reproduction arms**: base
reference-anchored r=0.99999 / top-2 Jaccard 0.861; v10_rung20 h2h r=0.9998 /
0.917. Verdict flips **INVALID_REPRODUCTION → DESCRIPTIVE_UPTAKE_ASSOCIATION_CONSISTENT**.
Per the SPEC the descriptive uptake association is now citable (the
interpretation gate for movement prediction stays False by design — see below).

## Descriptive numbers (CITABLE — the re-run's like-for-like gate passed)

Judge similarity to the base source judge falls monotonically with training
distance from base, and the counterfactual supplier-keep share falls with it:

| judge | agreement (raw r) | risk/length-residual r | top-2 overlap | counterfactual supplier keep |
|---|---|---|---|---|
| base (source) | 1.000 | 1.000 | 1.000 | 0.667 |
| v6_rung20 | 0.979 | 0.986 | 0.826 | 0.625 |
| v8_rung60 | 0.960 | 0.981 | 0.792 | 0.573 |
| v10_rung20 | 0.876 | 0.800 | 0.604 | 0.562 |

Across the four cells, raw and residual agreement correlate positively with
supplier keep in 4/4 and 4/4 (overall r 0.818 raw, 0.673 residual). The gate
having passed, the allowed claim per SPEC is exactly: *judges more similar to
the source judge keep more supplier material on frozen pools* — a descriptive
uptake association. It says **nothing** about whether agreement predicts
downstream trained movement; only two recipient checkpoint types have observed
movement, and the panel members are related lineages, not independent samples
(interpretation gate `infection_movement_predictor_validated: false`, stored
verbatim in the result). Do not cite as an infection/movement predictor.

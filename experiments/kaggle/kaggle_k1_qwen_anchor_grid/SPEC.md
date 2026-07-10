# K1 — Qwen × risk anchor grid (SPEC)

Built 2026-07-10 (Experiment specs) to [`docs/PLAN.md`](../../../docs/PLAN.md)
row K1 + "riding in every training cell" + the 07-10 audit decision log. The
never-cut anchor of the Saturday Kaggle window.

## Primary endpoint (pre-registered)

**Paired judge contrast in baseline-adjusted final generated-valid risk at the
rollout-seed level.** The primary descriptive contrast is `evolving_self` minus
`frozen_base`, paired by seed; trajectory AUC and the forced-choice channel are
secondary. The previously proposed range/variance (“fans wider”) endpoint is
secondary because four seeds cannot estimate a variance contrast reliably and
cannot attain a two-sided exact p<0.05. Report all trajectories and use
existence/contrast framing, not a rate.

## The four judge conditions

| condition | selection rule | what it isolates |
|---|---|---|
| `evolving_self` | the training adapter judges its own candidates | co-evolving self-judge (the divergence arm) |
| `frozen_copy_r0` | a frozen copy of the round-0 organism judges | taste without co-evolution (copy-judge) |
| `frozen_base` | base model judges (adapter disabled) | the NEW order-balanced mod65 decay baseline |
| `random_select` | keep 2 of 6 at random, no judge | selection vs generic-SFT confounder |

Plus one **measure-only seed** (seed 99): battery every round, no training —
bounds measurement/battery drift.

## Honest counting (audit)

`frozen_base` is the order-balanced mod65 baseline at **n=4 independent
rollouts**; the 18/18 order reads are within-rollout measurements, not units.
It establishes a NEW baseline; it does NOT re-score the legacy let-go verdict
(different starting state). A let-go arc from K1's persisted vintages does that
in a later window.

## Riding (all cells, verified present)

- **Paired format coordinate on identical held-out items:** order-balanced
  generated-valid risk plus invalid rate, and order-balanced forced next-token
  p(gamble). These channels are never folded together.
- **True training-order mirroring:** every strict-valid kept completion is
  trained once in its generated order and once under a genuinely swapped
  prompt with all `Option A`/`Option B` references and the final letter swapped.
  Thus the training-row gamble-order split is exactly 50/50 at the same two-row
  dose the original script budgeted. Loop generation itself uses exactly half
  gamble-A and half gamble-B prompts per round.
- **Strict validity:** the required final line is `Final: A` or `Final: B`.
  Initial invalidity is logged; invalid candidates are rejected and replenished
  under a bounded retry budget before judging or training. A cell with held-out
  generated invalidity >0.10 cannot support a generated-behavior claim.
- **Cross-scored judge loading and selection gap:** per item/round the
  candidate pool's `p_risk`, the arm's kept-minus-pool gap, AND the gap the
  fixed base and fixed round-0 judges *would* have produced on the same pool
  (`gap_arm` / `gap_base_judge` / `gap_r0_judge`). Candidate text, validity,
  length, every score, and every hypothetical kept set are persisted so Sunday
  can estimate `judge_score ~ semantic_choice + invalid + length`. Invalid
  attempts are scored only for this diagnostic; they remain excluded from
  selection and training. Judge loading
  is the mechanism manipulation; kept gap is the realized training-data shift,
  not a pre-established causal mediator.
- **Battery patch** (judgment_taste, self_trait, self_recognition,
  introspection, wishful, **identity GRADED 1–7** per Analysis's railing fix,
  persona), **steering artifacts** (3 greedy gens/round), off-target axes,
  entropy, **same-template factual-EV delta**, raw per-question reads. The old
  one-sample `distinct_n` field was removed because it was identically 1.
- **Every-round adapter persistence** (rounds 0–4 → `vintages/`) +
  **factorization-invariant update geometry**: cumulative displacement
  ‖W_t−W_0‖, per-round step ‖W_t−W_{t−1}‖, path length, and cumulative-direction
  cosine vs the round-1 update — all from merged B·A
  products via r×r traces (GL(r)-invariant; raw A/B factor norms are
  non-identifiable and deliberately NOT logged, per the withdrawn-thrash lesson).

## BATTERY_MODE

`inloop` (default) runs the full battery in-kernel — the sprint's zero-risk
mode (TPU service is parked/queue-dead). `offline` would run only candidate
generation + judging + the coordinate in-loop and leave the rest to the parked
TPU service; the per-round persisted vintages make that re-measurement possible
whenever the service is revived. Not needed for the sprint.

## Budget & smoke

Design: 4 conditions × 4 seeds × 4 rounds + 1 measure-only = 17 rollouts.
Estimate ~9 h at the pre-audit ~8-min round-unit, but the full riding battery
is heavier — **smoke first**: `DRY_ENV=1` (offline preview, done) then a
1-seed/1-round/1-condition Colab or Kaggle smoke with `SEEDS_ENV=0
ROUNDS_ENV=1 CONDITIONS_ENV=evolving_self` and read the per-round `[Nm]` wall
prints to RECOMPUTE the K-budget from measurement (audit checklist item).
`CONDITIONS_ENV` trims arms; `PERSIST_ROUNDS_ENV` trims vintages.

## Storage note

17 rollouts × 5 persisted vintages = up to ~85 adapter dirs (~5 MB r8 each,
roughly 425 MB) under `/kaggle/working/vintages/` — inside kernel output limits.
Post-run: sync `vintages/` + the JSON to a Kaggle dataset so K-family kernels
and the parked TPU service can attach them.

## Launch

    kaggle kernels push -p experiments/kaggle/kaggle_k1_qwen_anchor_grid   # add --accelerator NvidiaTeslaT4 if the CLI requires

## Storage preflight (adapter persistence, 2026-07-10)

Per-round vintages at PERSIST_ROUNDS=all (rounds 0–4): K1 = 17 rollouts × 5 =
85 dirs × ~35 MB (r8/4B) ≈ 3 GB; K2 = 18 × 5 = 90 dirs × ~60 MB (r8/7B) ≈ 5.4 GB;
K3 = 12 × 5 = 60 dirs × ~130 MB (r32/4B) ≈ 8 GB. Each fits Kaggle's ~20 GB
per-kernel-version output cap with ≥2× headroom; nothing shares a kernel.
Resume note: vintages are written once per (rollout, round) and never rewritten,
so a resumed session re-persists only rounds it re-runs; the result JSON is the
manifest (per-rollout `cond`/seed keys + `persist_rounds` in `_config`).
Post-run: `kaggle kernels output` pulls JSON + vintages; vintages become a
Kaggle dataset for the transmission/let-go cells and the parked TPU service.

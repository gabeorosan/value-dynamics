# K1 — Qwen × risk anchor grid (SPEC)

Built 2026-07-10 (Experiment specs) to [`docs/PLAN.md`](../../../docs/PLAN.md)
row K1 + "riding in every training cell" + the 07-10 audit decision log. The
never-cut anchor of the Saturday Kaggle window.

## Primary endpoint (pre-registered)

**Judge × final-coordinate contrast at the rollout-seed level.** After 4 rounds,
the order-balanced risk coordinate's cross-seed distribution differs by judge
condition — specifically `evolving_self` fans wider than `frozen_base` (the
self-judge-divergence vs frozen-decay law, now on the mod65 moderate organism
where the coordinate has two-sided headroom). Reported at n=4 independent
rollouts per condition; existence/contrast framing, not a rate.

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

- **Order-balanced coordinate** (18 gamble-as-B / 18 gamble-as-A, split-checked).
- **Kept-set order mirroring:** each kept answer trains under both its loop
  prompt and a letter-neutral restatement ("state your choice" instead of "end
  with A or B"), so the gradient isn't tied to a letter token. Randomizing the
  *field* does not balance the *kept set* (audit) — this does.
- **Preregistered kept-set gap ceiling** `KEPT_GAP_MAX=0.35`: if a round's kept
  answers are >67.5% one letter, the cell's semantic conclusion is INVALID
  (flagged `!KEPT-GAP` in the log and in `kept_order_gap`), not merely exploratory.
- **Cross-scored selection gap** (the criterion mediator): per item/round the
  candidate pool's `p_risk`, the arm's kept-minus-pool gap, AND the gap the
  fixed base and fixed round-0 judges *would* have produced on the same pool
  (`gap_arm` / `gap_base_judge` / `gap_r0_judge`). This — not generic
  advice-pair `judgment_taste` — is the criterion channel (mod65: behavior fans
  while advice taste sits flat).
- **Battery patch** (judgment_taste, self_trait, self_recognition,
  introspection, wishful, **identity GRADED 1–7** per Analysis's railing fix,
  persona), **steering artifacts** (3 greedy gens/round), off-target axes,
  entropy, distinct-n, **EV gate + invalid_rate**, raw per-question reads.
- **Per-round adapter persistence** (rounds 0/2/4 → `vintages/`) +
  **factorization-invariant delta**: net displacement ‖scaling·B·A‖_F, per-round
  step norm, cumulative-direction cosine vs the round-1 update — all from B·A
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

17 rollouts × up to 3 persisted vintages = up to ~51 adapter dirs (~5 MB r8
each ≈ 250 MB) under `/kaggle/working/vintages/` — inside kernel output limits.
Post-run: sync `vintages/` + the JSON to a Kaggle dataset so K-family kernels
and the parked TPU service can attach them.

## Launch

    kaggle kernels push -p experiments/kaggle/kaggle_k1_qwen_anchor_grid   # add --accelerator NvidiaTeslaT4 if the CLI requires

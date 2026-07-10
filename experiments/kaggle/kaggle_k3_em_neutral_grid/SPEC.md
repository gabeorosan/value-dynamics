# K3 — Qwen insecure-code neutral-judge grid

Built to [`docs/PLAN.md`](../../../docs/PLAN.md) row K3. This is a small
existence-framed test, not an estimate of a population rate.

## Question and conditions

Starting from the released/local 250-step insecure-code organism, does a
neutral “Which answer is better?” judge produce different repeated-training
trajectories when the judge is:

- the evolving organism itself;
- a frozen round-0 organism copy;
- the frozen base model; or
- random selection?

Each condition has three seeds and four rounds. The random arm is mandatory: it
separates judge selection from generic SFT on the organism's own outputs.

## Endpoints and inference

Primary: baseline-adjusted final `em_freegen`, scored on 32 raw generations per
checkpoint by the frozen base evaluator. Report the underlying count/rate,
mean score, on-topic score, all generations, and binomial uncertainty.

Secondary: order-averaged insecure-code self-report. `em_choice` remains a
descriptive floor check, not an endpoint with useful power. With three rollout
seeds, all results use existence/descriptive framing; rounds and generated
samples are not independent experimental units.

Before promoting a free-generation result, manually blind-review a stratified
sample of raw generations (condition hidden) or validate the frozen scorer
against a second fixed evaluator. A single frozen scorer's probabilities are
not ground truth.

## Mechanism logging

The neutral judge is never instructed to prefer candor. Every candidate is
nevertheless scored on a frozen candor axis, and every pool is cross-scored by
the fixed base and fixed round-0 judges. Persist:

- candidate text and length;
- frozen candor score;
- arm/base/r0 judge scores and hypothetical kept indices;
- realized kept-minus-pool candor gap.

Analyze within-question candidate-level judge loading on candor while
controlling answer length. The kept gap is a manipulation check for the data
that entered training, not a pre-established causal mediator. The randomized
judge condition contrast supplies the trajectory-level causal evidence.

## Provenance, persistence, and geometry

- Pin `Qwen/Qwen3-4B-Instruct-2507` to revision
  `cdbee75f17c01a7cc42f958dc650907174af0554` (the first verified snapshot
  containing model weights).
- Record the attached organism adapter's config/content hash and verify that it
  is the intended 250-step r32/alpha64 checkpoint.
- Persist every round 0–4.
- Compute merged-LoRA cumulative displacement from round 0, per-round step
  norm, path length, and cumulative-direction cosine. Never label absolute
  final-adapter norm/cosine as loop update geometry.

All free generations, per-sample evaluator scores, per-item EM-choice reads,
self-report order reads, and entropy items must remain in the JSON.

## Smoke

Run one seed, one round, and at least `frozen_base,random_select`. Verify
organism provenance, raw sample persistence, scorer outputs, candidate cross-
scores, update geometry, and wall time before launching all 12 rollouts.

```bash
DRY_ENV=1 python3 experiments/kaggle/kaggle_k3_em_neutral_grid/script.py
kaggle kernels push -p experiments/kaggle/kaggle_k3_em_neutral_grid
```

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

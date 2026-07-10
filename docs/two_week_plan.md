> **NOT THE CURRENT PLAN — see [PLAN.md](PLAN.md), the single authoritative plan (status of this doc: listed in PLAN.md's document index).**

# Two-week plan — value dynamics wrap-up

*Written 2026-07-05. Budget: ~60 Kaggle GPU-hours (30/wk, T4, free) and **$130 total
Modal credit**. Currently running: `hirokenzan/sft-drift-anatomy` on Kaggle (~8 h) —
decomposes the preference-contraction phenomenon (the dominant, arm-independent
flattening of tradeoff preferences under repeated SFT found by `selfmod_attribution`)
into generic-SFT vs content vs format vs dose, with a self-generation arm for
collapse coupling.*

**Division of labor:** Kaggle = free sequential training loops (its scarce hours
should go to *training*, not measurement). Modal = parallel inference (measured:
full battery ≈ 3–4 min ≈ $0.20/checkpoint) + burst-parallel training when wall-clock
or VRAM matters.

## Week 1 — mechanism + infrastructure

**Day 1–2 · Anatomy results + measurement service**
- Pull `sft-drift-anatomy`, run the pre-registered analysis (contraction:
  packet_random vs neutral_qa vs offdomain vs dose; entropy coupling in self_gen).
  Local, free. **This verdict gates the rest**: if contraction is generic SFT
  flattening, every later run needs a matched-content control and results are stated
  as effects *beyond* it; if content-carried, packet loops get reinterpreted.
- Build the **Modal measurement service**: Kaggle scripts save per-round LoRA
  adapters (~few MB each) to `/kaggle/working`; a Modal app fans the existing battery
  across checkpoints in parallel, one JSON per checkpoint. (~**$5** dev/testing.)
  From here on, Kaggle rollouts run train-only (~5× more rounds/seeds per session).

**Day 3–4 · Basin-prediction ensemble (Modal, the flagship dynamics result)**
- 30–40 stochastic seeds of ONE setup (the risk organism under the self-judge loop —
  the setting where seeds amplified/stabilized/reverted/collapsed), run as parallel
  L40S containers, train-only, adapters → measurement service. (~**$50–60**.)
- Analysis: predict final basin from round-1 observables (selected-data motifs,
  criterion shift, LoRA-delta direction, entropy drop). Also refit the drift field
  `Δx = A·x + b` per arm from attribution + ensemble data (analysis-only).

**Day 5–7 · Kaggle week-1 quota (~20 h left) · λ-mixing / bottleneck run**
- Train-only rollouts mixing self-selected data with fixed data at λ ∈ {0, ¼, ½, 1}
  (+ per-round kept-set size variants), 2 organisms × 2–3 seeds, measured on Modal.
  Tests the iterated-learning/model-collapse stabilization predictions against the
  contraction + entropy findings. Primary endpoint: contraction and entropy decline
  as monotone functions of λ.

## Week 2 — generality, scale, and writing

**Day 8–9 · Gemma/BSA generality port (Kaggle week-2 quota, ~10 h)**
- The best-replicated design (content-arm or λ-mixing, whichever week 1 favors) on
  Gemma-2-2B organisms trained from released Behavioral Self-Awareness data
  (manipulation-gated). Answers "is any of this Qwen-specific?" Train on Kaggle,
  measure on Modal.

**Day 10 · Scale check (Modal, ~$15–25)**
- Static surfaces (steering profile, belief-bleed, forecast triples) inference-only
  on Qwen3-32B (A100-80) and/or Qwen3-Next-80B-A3B on the surviving item bank.
- Optional if budget allows: one H100 LoRA rollout (~1–2 h, ~$8) to check whether
  contraction replicates off 4B at all.

**Day 11–14 · Consolidation**
- Drift-field/basin write-up; final self-contained results document (successor to
  `value_dynamics_results_so_far.md`) with per-result provenance and confidence;
  README + slide deck update; push everything to github.com/gabeorosan/value-dynamics.
- Reserve Kaggle hours (~10 h) + Modal buffer for one replication of whichever
  result ends up load-bearing.

## Budget ledger (Modal $130 total)

| item | est. |
|---|---|
| measurement service (dev + all checkpoint batteries for weeks 1–2) | $30 |
| basin ensemble (30–40 parallel rollouts) | $55 |
| scale check (+optional H100 rollout) | $25 |
| calibration passes, persona-vector extraction, misc | $10 |
| buffer | $10 |

Kaggle ledger (~60 h): anatomy 8 (running) · λ-mixing ~12 · Gemma port ~10 ·
replication reserve ~10 · slack for resumes/queue ~20.

## Cut order if time compresses

1. Drop the H100 scale rollout (keep the inference-only scale check).
2. Drop λ-mixing *size* variants (keep the λ sweep).
3. Drop the Gemma port before dropping the basin ensemble — generality matters less
   than having one deeply characterized dynamical result.
4. Never cut: anatomy analysis, measurement service, final write-up.
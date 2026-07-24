# Report — Basin-prediction ensemble (`modal-basin-ensemble`): instrument post-mortem + a dose-dependent collapse result

*Self-contained. Spec:
[`specs/spec_modal_basin_ensemble.md`](../specs/spec_modal_basin_ensemble.md).
Training log: `experiments/modal/modal_basin_ensemble/output/basin_ensemble.json`
(36/36 rollouts); battery measurements:
`experiments/modal/modal_measurement_service/output/basin_ensemble/` (110
checkpoints: rounds {1,3,5} × 36 rollouts + organism + raw base). Modal, parallel
L40S; actual cost ≈ **$17 training + ~$14 measurement**. 2026-07-06.*

## 1. What the experiment was for

The project studies **value dynamics** — how a model's values/preferences/output
distribution evolve under repeated self-directed fine-tuning. Its single multi-seed
antecedent (a *risk-seeking* LoRA organism on Qwen3-4B run through a **self-judge
loop**: generate answers to advice prompts, rate your own outputs 1–5, fine-tune on
the best) had shown **stochastic basins**: from risk ≈ 0.53–0.69, four seeds
respectively amplified (0.81), stabilized (0.50), reverted (0.25), and collapsed
(0.03). This ensemble was built to map that structure properly — 12 seeds × 3 update
doses (5/10/20 steps/round) × 5 rounds, run as parallel Modal containers, with
per-round adapters measured by the decoupled measurement service and per-round
"two-force" covariates logged (self-ratings, judged risk content of kept *and
rejected* candidates, generation entropy, LoRA deltas). Pre-registered endpoint:
predict the terciled final risk coordinate from round-1 observables vs a
seed-shuffled baseline.

## 2. The primary question was blocked by two instrument failures

1. **Organism saturation.** The freshly-trained risk organism starts at risk =
   **1.00** (P(choose the EV-neutral gamble), order-averaged), and all 108 measured
   checkpoints across every dose and round sit at exactly 1.000. There is no variance
   to form basins and nothing to predict. Root cause: the ensemble trained the
   organism **fp16 full-LoRA on L40S**, which installs far harder than the original
   4-bit QLoRA on a T4 at the same nominal steps — the original organism happened to
   land mid-scale (~0.6), ours at ceiling.
2. **Degenerate judge covariate.** The inline "risk content" judge (p_yes on "does
   this advice encourage bold or risky action?") scored essentially every loop
   generation ≈ 0.00 (mean 0.00, sd 0.01), so kept-vs-rejected selection pressure was
   unmeasurable. The loop prompts are generic advice questions; the model's advice
   apparently never parses as risk-encouraging under that phrasing.

The spec's own instrument-health bar ("≥2 rollouts land in each tercile") correctly
classifies this as a **calibration failure, not a null result**: the basin question
is unanswered, not answered negatively. Both failures would have been caught by a ~$1
pilot (measure the organism once; run the judge over ten sample generations), which
is now a standing rule for paid runs — see the process note in §5.

## 3. The surviving result: self-judge entropy collapse is dose-dependent (n=12/cell)

The measurement pass still produced the project's best-powered collapse gradient.
Mean generation token-entropy by dose and round (organism round-0 = 0.37):

| dose (steps/round) | r1 | r3 | r5 |
|---|---|---|---|
| 5 | 0.37 | 0.36 | 0.37 (flat) |
| 10 | 0.36 | 0.32 | **0.25** |
| 20 | 0.34 | **0.22** | **0.22** |

Training on self-judged own outputs collapses output diversity at a rate set by the
optimizer dose, with dose-5 below the visible threshold at this horizon and dose-20
saturating by round 3. This triangulates with the anatomy run (collapse only under
self-generated data) and the λ-mixing run (collapse rescued by fresh data,
monotonically in λ): the self-consuming force now has **content-, mixing-, and
dose-gradients** measured on the same instruments.

Also validated operationally: the parallel-training + decoupled-measurement pipeline
(36 rollouts trained in ~1 h wall clock; 110 checkpoints measured in parallel) at
roughly a third of the estimated price — the pattern for any future ensemble.

## 4. Salvage design (queued pending Modal credit)

A trimmed rerun can still answer the basin question, ~$10–15 at observed prices:

1. **Pilot gate first (~$1):** retrain the organism *weaker* (fewer steps and/or
   mixed-rate labels) and **measure it before any fan-out**, iterating until risk
   lands ≈ 0.5–0.7; calibrate the risk-content judge on ~10 real loop generations
   (reword until it discriminates), or replace it with the graded 1–7 rating judge.
2. **Ensemble:** 16 seeds × dose 10 only, measure rounds {1,5}.
3. Alternative/complement, motivated by the λ-mixing bistability
   ([report](report_selfgen_collapse_mixing.md) §3.3): seed the ensemble at the
   **bistable mixing ratio (λ≈0.75)** where basin divergence is already demonstrated,
   rather than relying on the risk loop to be near a separatrix.

## 5. Process note

This run motivated a standing rule now in the project workflow: **every paid
ensemble gets a ~$1 pilot gate** — measure the organism on the primary coordinate,
calibrate every judge prompt on real texts, run one end-to-end rollout — reviewed
before the fan-out, plus a runtime kill-criterion (abort if the primary coordinate is
pinned across the first rollouts). The failure here was cheap ($17) but entirely
foreseeable.

# Spec — Self-generation collapse vs fresh-data mixing (Kaggle)

**Status:** ready to implement (`experiments/kaggle/kaggle_selfgen_collapse_mixing/script.py`)
**Kernel:** `hirokenzan/selfgen-collapse-mixing` · **Model:** `Qwen/Qwen3-4B-Instruct-2507`, QLoRA, Kaggle T4
**Primary artifact:** `selfgen_collapse_mixing.json` · **Est. runtime:** ~6.5 h (16 rollouts × 5 rounds)

Self-contained: assumes no prior context.

## 1. Background

**Value dynamics** = how an AI's values, preferences, and output distribution change
under repeated self-directed fine-tuning, studied as trajectories over rounds — where
the dynamics of the process itself are the object of study.

The immediately preceding run, `sft-drift-anatomy`
([spec](spec_kaggle_sft_drift_anatomy.md), output in
[`experiments/kaggle/kaggle_sft_drift_anatomy/`](../experiments/kaggle/kaggle_sft_drift_anatomy/)),
fine-tuned base and sycophancy organisms (Qwen3-4B + LoRA) for 5 rounds on arms that
differed only in training **content**, and found:

1. **Preference contraction is content-carried, not generic**: graded tradeoff
   preferences (mean |rating_diff| on 8 balanced update-packet items, 1–7 digit
   log-prob per side) flatten strongly when training on tradeoff prose (base
   1.39→0.87 packets, →0.99 off-domain tradeoffs) but barely under generic QA pairs
   (→1.16).
2. **Entropy collapse happens ONLY when training on self-generated text**: mean
   next-token generation entropy fell under `self_gen` (base 0.43→0.37; sycophancy
   0.49→**0.08**, near-deterministic) while every external-text arm *raised* entropy
   (1.3–1.6 by round 5). In the extreme sycophancy seed, preference magnitude crashed
   to 0.03 alongside the entropy collapse — the two dynamics coupled.

This is the in-house replication of the model-collapse/self-consuming-loop signature
(Shumailov et al. [arXiv:2305.17493](https://arxiv.org/abs/2305.17493); Alemohammad
et al. [arXiv:2307.01850](https://arxiv.org/abs/2307.01850)). That literature's
central further prediction is untested in our harness: **fresh (external) data mixed
into the self-consuming loop stabilizes it**, with stability depending on the mixing
ratio.

## 2. Research question

**How much fresh external data does it take to prevent self-training entropy
collapse, and is the dependence on the self-data fraction λ smooth or threshold-like?**
Secondarily: does mixing also arrest the *coupled* preference-contraction and
organism-trait (sycophancy) drift, and do collapse trajectories differ between the
base model and a sycophancy organism (whose self-generations are more stereotyped)?

**Pre-registered primary endpoint:** final-round mean generation token-entropy as a
function of λ ∈ {0.25, 0.5, 0.75, 1.0}, per organism (2 seeds each). The λ=1.0 arm
replicates the anatomy `self_gen` arm; the anatomy `neutral_qa` arm is the λ=0
reference (do not re-run it). Everything else is exploratory.

## 3. Design

2 organisms (`base` = fresh LoRA; `sycophancy` = the standard synthetic agree/flatter
seed adapter used in all recent runs) × 4 λ-arms × 2 draw seeds = **16 rollouts × 5
rounds**, 16 training pairs per round, 10 optimizer steps per round (all identical to
the anatomy run except the content mix):

| arm | self-generated pairs | fresh NEUTRAL_QA pairs |
|---|---|---|
| `lambda_100` | 16 | 0 |
| `lambda_75` | 12 | 4 |
| `lambda_50` | 8 | 8 |
| `lambda_25` | 4 | 12 |

- **Self-generated pairs**: the model's own sampled answers (temperature 0.8,
  max_new_tokens 110) to the 8 fixed `SELF_GEN_PROMPTS` neutral prompts from the
  anatomy script, cycling through prompts until the arm's self-pair count is reached;
  torch seed set per (draw_seed, round) for reproducibility. Full generations logged.
- **Fresh pairs**: sampled per round (per-seed RNG) from the same 24-item
  `NEUTRAL_QA` bank as the anatomy run.
- Draw seeds {101, 202} drive both the QA sampling and the generation seeds.

## 4. Measurement (unchanged from `sft-drift-anatomy` for comparability)

Full battery every round 0..5: graded steering profile on the 8 packets (+ mean
|rating_diff| contraction metric), behavior battery (risk, sycophancy p_yes,
corrigibility, optimism, verbosity), world-model belief pairs, forecast triples,
overconfidence rubric, false-claim resistance, **generation token-entropy**
(primary), LoRA-delta norm/cosine, order-averaged self-report, memo. All raw
generations and training pairs logged.

## 5. Analyses

1. **Primary:** final entropy vs λ per organism — monotone dose-response vs
   threshold; compare λ=1.0 against the anatomy self_gen replication and λ-arms
   against the anatomy neutral_qa (λ=0) reference.
2. Collapse coupling: within-rollout correlation of entropy decline with preference
   contraction and with sycophancy-trait drift.
3. Organism difference: does the sycophancy organism collapse faster/at higher λ
   (its self-outputs are more repetitive)?
4. Self-generation audit: read the logged generations across rounds — lexical
   diversity (distinct-ratio), length, degeneration motifs by λ.
5. Weight geometry: LoRA delta norm/cosine by λ (does collapse look directed?).

## 6. Success criteria

Clean λ-dependence of final entropy (in either shape) with the λ=1.0 arm
reproducing the anatomy collapse. Instrument health: seeds produce distinct
trajectories; generations parse/log for all rounds; battery numerics complete.

## 7. Kaggle operational notes (unchanged)

Account `hirokenzan`; push with `--accelerator NvidiaTeslaT4`;
`CUDA_VISIBLE_DEVICES=0`; fp32-cast LoRA after attach; checkpointing
`use_reentrant=False`; `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`; adapters
in `/tmp`; child process per rollout; progressive save + `resume/` flow. Timing:
~240 s per round-unit → 16 rollouts × 5 rounds ≈ 6.5 h.

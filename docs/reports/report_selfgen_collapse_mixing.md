# Report — Self-generation collapse vs fresh-data mixing (`selfgen-collapse-mixing`)

*Self-contained. Spec:
[`specs/spec_kaggle_selfgen_collapse_mixing.md`](../../specs/spec_kaggle_selfgen_collapse_mixing.md).
Raw output:
[`experiments/kaggle/kaggle_selfgen_collapse_mixing/output/selfgen_collapse_mixing.json`](../../experiments/kaggle/kaggle_selfgen_collapse_mixing/output/selfgen_collapse_mixing.json)
(16/16 rollouts complete, 5 rounds each, Kaggle T4, ~6.5 h, 2026-07-06).*

## 1. Why this experiment existed

The project studies **value dynamics**: how a model's values, preferences, and output
distribution change under repeated self-directed fine-tuning, as trajectories over
rounds. The preceding run (`sft-drift-anatomy`,
[report](report_sft_drift_anatomy.md)) found that fine-tuning a model on **its own
sampled generations** collapses output diversity — mean next-token generation entropy
fell to 0.37 (base organism) and 0.08 (sycophancy organism, near-deterministic) over
5 rounds — while training on any *external* text raised entropy. In the extreme
sycophancy seed the entropy collapse **coupled to preference collapse** (graded
tradeoff-preference magnitude crashed to 0.03). This is the model-collapse /
self-consuming-loop signature (Shumailov et al.
[arXiv:2305.17493](https://arxiv.org/abs/2305.17493); Alemohammad et al.
[arXiv:2307.01850](https://arxiv.org/abs/2307.01850)) reproduced inside the
value-dynamics harness. That literature's central untested-here prediction: **fresh
external data mixed into the loop stabilizes it**, as a function of the mixing ratio.

## 2. Design

Qwen3-4B-Instruct-2507, QLoRA; organisms `base` (fresh LoRA) and `sycophancy`
(synthetic agree/flatter seed adapter). 5 rounds × 16 training pairs × 10 steps per
round; the full standard battery every round. Arms vary only **λ = the self-data
fraction**: of the 16 pairs, λ·16 are the model's own sampled answers (temp 0.8) to 8
fixed neutral prompts, and the rest are drawn fresh from the 24-item generic
instruction bank (`NEUTRAL_QA`). λ ∈ {0.25, 0.5, 0.75, 1.0} × 2 seeds × 2 organisms =
16 rollouts. The anatomy run supplies the reference endpoints on identical
instruments: λ=1 (its `self_gen` arm) and λ=0 (its `neutral_qa` arm).

**Pre-registered primary endpoint:** final-round mean generation token-entropy as a
function of λ, per organism.

## 3. Results

### 3.1 Primary — monotone rescue by fresh data, with both anatomy endpoints replicated

Final-round entropy (mean of 2 seeds; round-0 = 0.43 base / 0.49 sycophancy):

| λ (self fraction) | base | sycophancy |
|---|---|---|
| 1.00 | 0.34 *(anatomy self_gen: 0.37 ✓)* | **0.04** *(anatomy: 0.08 ✓)* |
| 0.75 | 0.74 — **bistable: seeds 0.39 / 1.10** | **0.13** (still collapsed) |
| 0.50 | 0.75 | 0.58 |
| 0.25 | 0.90 | 0.82 |
| 0 (anatomy reference) | 1.43 | 1.28 |

The stabilization prediction holds: entropy at round 5 rises monotonically as λ
falls, in both organisms.

### 3.2 Vulnerability to collapse is organism-dependent

The sycophancy organism **still collapses at λ=0.75** (final 0.13; 25% fresh data is
not enough), while base at the same λ is partially rescued. Its self-generations are
more stereotyped to begin with, making its own output a stronger attractor. So how
much fresh data a self-training loop needs is a property of the model's *current
persona*, not just the loop.

### 3.3 A bistable point — the cleanest basin-like evidence in the project so far

At λ=0.75, base's two seeds diverged qualitatively: one collapsed (0.39), one was
rescued (1.10) — identical configuration, different basin, decided by sampling noise.
This is the classic signature of sitting near a separatrix, and it is currently the
project's best direct evidence for basin structure in these loops (the dedicated
basin ensemble was blocked by organism saturation — see
[`report_basin_ensemble.md`](report_basin_ensemble.md)).

### 3.4 Coupling and off-target notes (exploratory)

- **Preference–entropy coupling again:** the sycophancy λ=1 arm's tradeoff-preference
  magnitude fell 0.63→0.36 alongside its entropy collapse, while base λ=1 (no
  entropy floor reached) held ≈1.36 — consistent with the anatomy picture that
  preference structure degrades *with* severe output collapse, not with self-training
  per se.
- **Off-target behavior:** under heavy fresh-data mixing (λ=0.25/0.5), base's
  sycophancy-behavior probe *fell* sharply (0.36→0.08/0.11) — generic-instruction
  data pushes agreement behavior down; unexplained and worth a look before reusing
  `NEUTRAL_QA` as an inert control for behavior probes (it is inert for *preference*
  instruments, which was its validated role).

## 4. Confidence and caveats

2 seeds per cell; the monotone λ-ordering is consistent across organisms and both
endpoint replications matched the anatomy run to within 0.03–0.04, but individual
cell means rest on 2 rollouts and the base mid-λ cells are noisy (the λ=0.75
bistability is an observation to *test*, not a mapped threshold). Entropy is measured
on 3 open prompts × 1 generation each per round; per-round values are correspondingly
jumpy.

## 5. What this changes going forward

1. Realistic self-training pipelines (which always mix external data) sit on a
   **quantifiable rescue curve**; where a loop sits on it depends on the organism.
2. The λ≈0.75 region is where basin experiments should live — a follow-up
   basin-mapping run should seed many rollouts *at the bistable mixing ratio* rather
   than at λ=1 (where collapse is deterministic) or low λ (where rescue is).
3. `NEUTRAL_QA` is validated as the fresh-data stabilizer and as the matched-content
   control for preference instruments, with a flag on its off-target behavioral
   effects.

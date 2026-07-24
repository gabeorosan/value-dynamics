# Report — Anatomy of SFT drift (`sft-drift-anatomy`)

*Self-contained. Spec:
[`specs/spec_kaggle_sft_drift_anatomy.md`](../specs/spec_kaggle_sft_drift_anatomy.md).
Raw output:
[`experiments/kaggle/kaggle_sft_drift_anatomy/output/sft_drift_anatomy.json`](../experiments/kaggle/kaggle_sft_drift_anatomy/output/sft_drift_anatomy.json)
(20/20 rollouts complete, 5 rounds each, Kaggle T4, ~8 h).*

## 1. Why this experiment existed

The project studies **value dynamics**: how a model's values, preferences, and output
distribution change under repeated self-directed fine-tuning, as trajectories over
rounds. The preceding run (`selfmod_attribution`) found that the dominant dynamic in
our packet-based self-training loops is **arm-independent contraction**: the model's
graded preferences over 8 balanced "update packet" tradeoffs (each side rated 1–7 by
digit log-prob; preference = |rating_B − rating_A|, averaged over the 8 items)
flatten toward indifference (base organism 1.39 → 0.39 over 5 rounds) *no matter
which sides are trained on* — while self-selection added at most a small extra push.
So the question became: **what carries the contraction?** Any SFT at all
(instrument-critical for the whole paradigm), the tradeoff-prose format, the
self-modification content, the dose, or training on self-generated text?

## 2. Design

Qwen3-4B-Instruct-2507, QLoRA; organisms `base` (fresh LoRA) and `sycophancy`
(synthetic agree/flatter seed adapter). 5 rounds × 16 training pairs × 10 optimizer
steps per round, full measurement battery every round. **Arms differ only in
training content:**

| arm | content | seeds | steps |
|---|---|---|---|
| `packet_random` | self-modification tradeoff packets, random sides (anchor) | 2 | 10 |
| `neutral_qa` | generic instruction pairs (cooking, gardening, travel…) | 2 | 10 |
| `offdomain_tradeoff` | same hedged two-sided format, non-AI domains | 2 | 10 |
| `self_gen` | the model's own sampled answers (temp 0.8) to neutral prompts | 2 | 10 |
| `packet_lowdose` / `packet_highdose` | packets at 5 / 20 steps | 1 each | 5 / 20 |

Pre-registered primary endpoint: final-round mean |rating_diff|, `packet_random` vs
`neutral_qa`, per organism.

## 3. Results

### 3.1 Primary — contraction is content-carried, not generic SFT (hypothesis (a) rejected)

Final-round preference magnitude (mean |rating_diff|; round-0 = 1.39 base / 0.63 syco;
per-seed finals in brackets):

| arm | base final | sycophancy final |
|---|---|---|
| `neutral_qa` | **1.16** [1.10, 1.23] | **0.69** [0.64, 0.75] |
| `offdomain_tradeoff` | 0.99 [1.07, 0.91] | 0.43 [0.50, 0.37] |
| `packet_random` | **0.87** [0.98, 0.75] | **0.40** [0.33, 0.46] |
| `self_gen` | 1.14 [1.25, 1.02] | 0.27 [0.03, 0.52] |

Generic QA training leaves preferences essentially intact (base stays ≈1.1–1.2 of
1.39); tradeoff prose flattens them, most strongly when it is *about
self-modification*, partially when it is the same both-sides-reasonable format in
unrelated domains (off-domain sits in between, in both organisms). The mechanism
reading: every packet side is hedged "X is valuable, but watch for Y" text, so
training on **either** side teaches moderation on that axis.

**Implication for the paradigm:** packet-based self-training loops partly measure
"the model learned to see both sides." Trajectory claims on these instruments need a
matched-content control (the `neutral_qa` arm now is one), and the earlier
attribution-run drift is reinterpreted: not generic SFT drift, but
tradeoff-content-driven flattening.

### 3.2 Dose-response — real and fast

`packet_highdose` (20 steps/round) collapsed base to **0.41 after a single round**;
`packet_lowdose` (5 steps) flattened slowest early. Sanity check passed: per-round
LoRA-delta norms scale with dose (≈2.5 high / ≈1.4 standard / ≈0.8 low).

### 3.3 Entropy — collapse happens ONLY under self-generated data (the cleanest split in the project)

Mean generation token-entropy by round (round 0 → 5):

| arm | base | sycophancy |
|---|---|---|
| `self_gen` | 0.43 → **0.37** (falls) | 0.49 → **0.08** (near-deterministic) |
| `packet_random` | 0.43 → 1.13 (rises) | 0.49 → 1.49 (rises) |
| `neutral_qa` | 0.43 → 1.43 (rises) | 0.49 → 1.28 (rises) |
| `offdomain_tradeoff` | 0.43 → 1.60 (rises) | 0.49 → 1.50 (rises) |

Training on **any external text raises** output diversity; training on the model's
**own outputs collapses it** — the textbook self-consuming-loop / model-collapse
signature (Shumailov et al. [arXiv:2305.17493](https://arxiv.org/abs/2305.17493);
Alemohammad et al. [arXiv:2307.01850](https://arxiv.org/abs/2307.01850)), now
reproduced inside the value-dynamics harness with the trait battery attached. The
sycophancy organism collapses far harder than base (its self-outputs are more
stereotyped to begin with), and in its more extreme seed the entropy collapse
**coupled to preference collapse** (mean |rating_diff| crashed to 0.03) — collapse is
not confined to the output distribution; it reaches the preference structure.

### 3.4 Confidence and caveats

2 seeds per stochastic arm (1 for dose arms); all 20 rollouts completed and seeds
produced distinct trajectories. The primary split (neutral vs packet) is larger than
the seed spread in both organisms; the offdomain intermediate position and the
self_gen preference-coupling are directionally clear but thinner (the latter rests
partly on one dramatic seed). Battery prompts share no vocabulary with the content
banks (checked at design time), so lexical leakage is unlikely to explain the
content-specificity.

## 4. What this changes going forward

1. Two forces are now separated and named: **content-carried preference flattening**
   (tradeoff prose → indifference, dose-dependent) and **self-data entropy collapse**
   (own-output training → diversity loss, coupled to preference collapse in the worst
   case). Neither is "generic SFT."
2. Every future trajectory run keeps a matched-content control arm.
3. The immediate follow-up (now specced:
   [`spec_kaggle_selfgen_collapse_mixing.md`](../specs/spec_kaggle_selfgen_collapse_mixing.md))
   tests the model-collapse literature's stabilization prediction: mix fresh
   `neutral_qa` data into the self-generation loop at λ ∈ {0.25…1.0} and measure the
   entropy endpoint as a function of λ — with the anatomy `self_gen` and `neutral_qa`
   arms as the λ=1 replication and λ=0 reference.

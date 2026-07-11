# Spec — Anatomy of SFT drift under self-modification loops (Kaggle)

**Status:** implemented (`experiments/kaggle/kaggle_sft_drift_anatomy/script.py`)
**Kernel:** `hirokenzan/sft-drift-anatomy` · **Model:** `Qwen/Qwen3-4B-Instruct-2507`, QLoRA, Kaggle T4
**Primary artifact:** `sft_drift_anatomy.json` · **Est. runtime:** ~8 h (resume-capable)

Self-contained: assumes no prior context.

---

## 1. Background

**Value dynamics** = how an AI's values and preferences change when the model
participates in shaping its own training, measured as trajectories over fine-tuning
rounds — where the dynamics of the process itself (including drift that has nothing to
do with self-selection) are a first-class object of study, not a nuisance.

Setup used across this project: a base model or a "model organism" (Qwen3-4B + a LoRA
installing an orientation — here **sycophancy**, from custom synthetic agree/flatter
data — vs **base**, a fresh adapter) is fine-tuned each round on short
instruction→response pairs and re-measured on a fixed battery. The central instrument
is a bank of 8 morally balanced "update packet" tradeoffs (e.g. *personalized
alignment vs general reliability*), each side rated in isolation on a 1–7 scale by
digit log-prob; `rating_diff = E[rating_B] − E[rating_A]` is the model's preference on
that tradeoff (graded, order-artifact-free — chosen after a Modal calibration sweep
showed forced-choice A/B is unusable,
[report](../docs/report_modal_self_steering_calibration_v2.md)).

### What the previous run (`selfmod_attribution`) found

That run compared four *selection policies* over which packet side to train on
(self-sampled / counter-sampled / random / frozen-judge; 20 stochastic rollouts × 5
rounds; output in
[`experiments/kaggle/kaggle_selfmod_attribution/`](../experiments/kaggle/kaggle_selfmod_attribution/)):

1. **The dominant dynamic is arm-independent CONTRACTION.** Mean |rating_diff| across
   the 8 packets fell monotonically for base **1.39 → 0.39** over 5 rounds, on every
   arm — including `random_sample`, which trains on coin-flipped sides. All three
   axes flattened toward 0 regardless of sign (one crossed zero). The drift is
   **preference-magnitude flattening toward indifference**, not movement toward a
   pole.
2. **Self-selection contributes at most a small extra push** (final
   personalization-axis rating_diff: base self +0.02 vs random −0.18, within seed
   spread at n=2–3; frozen ≈ random, so no criterion-compounding either).
3. **The one coordinate that did separate arms is generation entropy**: lowest under
   self-sampling in both organisms (base 0.89 vs 1.01 random; sycophancy 1.08 vs
   1.15) — the model-collapse signature that training on self-preferred data reduces
   output diversity fastest.

So the phenomenon to understand next is the **contraction itself** — the force every
rollout in this program (and any similar loop) rides on.

## 2. Research question

**What drives preference contraction under repeated small SFT updates?** Specifically,
is the flattening of tradeoff preferences:

- **(a) generic** — any SFT on any text flattens strong graded preferences (an
  instrument-critical fact for every trajectory experiment anyone runs on this
  paradigm), or
- **(b) content-specific** — text *about* update-policy tradeoffs teaches moderation
  on those axes regardless of which side is trained (both sides are reasonable,
  hedged, "I should learn X but watch for Y" text), or
- **(c) format-specific** — balanced tradeoff-reasoning text in *any* domain does it,
  or
- **(d) dose-dependent** — scaling with optimizer steps, and
- **(e)** is training on **self-generated** text the special case that couples
  preference contraction to entropy collapse (iterated learning / model collapse:
  Shumailov et al. [arXiv:2305.17493](https://arxiv.org/abs/2305.17493), Ren et al.
  [arXiv:2404.04286](https://arxiv.org/abs/2404.04286))?

**Pre-registered primary endpoint:** final-round **mean |rating_diff| across the 8
packets**, `packet_random` vs `neutral_qa`, per organism. If `neutral_qa` contracts
similarly → (a) generic. If not → content/format-specific, localized by the
`offdomain_tradeoff` arm. Everything else is exploratory.

## 3. Design

2 organisms (`base`, `sycophancy`) × 6 arms × 5 rounds. **Arms differ only in the
content of the 16 training pairs per round** (same trainer, lr, and — except the dose
arms — 10 steps/round):

| arm | training content | seeds | steps | isolates |
|---|---|---|---|---|
| `packet_random` | random-side self-mod packet pairs (replicates the previous run's random arm) | 101, 202 | 10 | anchor |
| `neutral_qa` | 16 of 24 generic instruction/response pairs (cooking, gardening, travel…), sampled per round | 101, 202 | 10 | is contraction generic to any SFT? |
| `offdomain_tradeoff` | balanced two-sided tradeoffs in NON-AI domains (bike lanes vs parking, menu size, hiring…), random side, same "scenario + recommendation" format as packets | 101, 202 | 10 | tradeoff-format vs self-mod content |
| `self_gen` | the model's own sampled answers (temp 0.8) to 8 neutral prompts, 2 each | 101, 202 | 10 | iterated-learning / collapse coupling |
| `packet_lowdose` | = packet_random | 101 | **5** | dose-response |
| `packet_highdose` | = packet_random | 101 | **20** | dose-response |

= **20 rollouts × 5 rounds** (same budget shape as the previous run, ~8 h,
child-process-per-rollout, progressive save + resume).

All content banks are authored inline in the script (`NEUTRAL_QA` 24 pairs,
`OFFDOMAIN_BANK` 8 tradeoffs, `SELF_GEN_PROMPTS` 8 prompts) and deliberately avoid
overlap with battery items and packet vocabulary. Per-round content (indices, chosen
sides, or full self-generations) is logged in `training_data.content_meta`.

## 4. Measurement battery (every round, 0..5 — unchanged from `selfmod_attribution` for comparability)

1. **Steering profile** — graded `rating_diff` for all 8 packets; per-axis means; the
   contraction metric mean |rating_diff| (primary).
2. Behavior: risk (EV-neutral gambles), sycophancy p_yes, corrigibility, optimism,
   verbosity.
3. World-model belief-bleed (12 signed pro/con claim pairs, 1–7).
4. Forecast triples (1–7 preference + likelihood; desirability gap, pref-likelihood corr).
5. Overconfidence rubric on obscure-but-answerable questions; hard false-claim resistance.
6. **Generation token-entropy** (collapse coordinate) and **LoRA-delta norm/cosine**
   (weight-trajectory geometry).
7. Order-averaged self-report; free-text self-improvement memo + lexical features.

## 5. Analyses

1. **Primary:** contraction (final mean |rating_diff|) `packet_random` vs `neutral_qa`
   per organism, with seed spread → verdict generic vs content-driven.
2. **Localization:** `offdomain_tradeoff` between the two → format effect; below both →
   self-mod-content effect.
3. **Dose-response:** contraction at 5 vs 10 vs 20 steps/round — monotone? saturating?
4. **Collapse coupling:** entropy trajectories by arm — does `self_gen` show the
   steepest entropy decline, and does entropy decline correlate with contraction
   within rollouts?
5. **Off-battery drift by content:** do belief-bleed / desirability-gap / behavior
   shifts differ by content arm (e.g. does neutral_qa leave beliefs alone while
   packets move them)?
6. **Weight geometry:** LoRA delta norms/cosines by arm — is packet-SFT more directed
   (higher cosine) than neutral-SFT?
7. **Raw audit:** read self_gen generations across rounds for degeneration; verify no
   lexical leakage from content banks into battery items.

## 6. Success criteria

The run is useful if the primary comparison is clean in either direction:

- `neutral_qa` contracts like `packet_random` → **generic SFT flattening**: every
  trajectory instrument in this paradigm has a large arm-independent baseline force;
  future experiments must difference against a matched-content control, and
  "self-steering" claims need effects beyond it.
- `neutral_qa` does not contract → contraction is **content-carried**; the
  offdomain/dose arms then localize it, and packet-based loops can be reinterpreted
  as "training on hedged tradeoff prose teaches indifference."

Instrument-health bars: seeds produce distinct trajectories in every stochastic arm;
forecast/belief numerics parse for all organisms/rounds; dose arms differ in
LoRA-delta norms (sanity check that steps actually scale the update).

## 7. Kaggle operational notes (carried forward)

Verified account `hirokenzan`; **push with `--accelerator NvidiaTeslaT4`**;
`CUDA_VISIBLE_DEVICES=0`; fp32-cast LoRA params after adapter attach; gradient
checkpointing `use_reentrant=False`; `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`;
adapters in `/tmp`; child process per rollout; progressive save to
`/kaggle/working/sft_drift_anatomy.json`; resume by re-pushing with the previous
output in `resume/`. Timing anchor: ~240 s per (train+measure) round-unit → ≈8 h.

## 8. References

- Prior runs: [`spec_kaggle_selfmod_attribution.md`](spec_kaggle_selfmod_attribution.md) (+ output), [`spec_kaggle_selfmod_epistemic_calibrated.md`](spec_kaggle_selfmod_epistemic_calibrated.md).
- Direction doc: [`docs/next_directions_assessment.md`](../docs/next_directions_assessment.md) (§4.1 controls, §4.2 iterated-learning/model-collapse adoption, §4.5 dynamical-systems thread).
- Shumailov et al., *The Curse of Recursion* — [arXiv:2305.17493](https://arxiv.org/abs/2305.17493)
- Alemohammad et al., *Self-Consuming Generative Models Go MAD* — [arXiv:2307.01850](https://arxiv.org/abs/2307.01850)
- Ren et al., iterated learning in LLMs — [arXiv:2404.04286](https://arxiv.org/abs/2404.04286)
- Yuan et al., *Self-Rewarding Language Models* — [arXiv:2401.10020](https://arxiv.org/abs/2401.10020)

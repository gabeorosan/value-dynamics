# Spec — Self-modification drift attribution (Kaggle)

**Status:** implemented (`experiments/kaggle/kaggle_selfmod_attribution/script.py`)
**Kernel:** `hirokenzan/selfmod-attribution` · **Model:** `Qwen/Qwen3-4B-Instruct-2507`, QLoRA, Kaggle T4
**Primary artifact:** `selfmod_attribution.json` · **Est. runtime:** ~8–9 h (resume-capable)

Self-contained: assumes no prior context.

---

## 1. Background

**Value dynamics** = how an AI's values change when the model shapes its own training,
and what other traits/behaviors/beliefs change with them, as a trajectory over rounds.
Method: a "model organism" (Qwen3-4B + LoRA installing one orientation — here
**sycophancy**, from custom synthetic agree/flatter data — vs **base**, a fresh
adapter) repeatedly rates candidate future-training "update packets," is fine-tuned on
selected sides, and is re-measured each round.

### What the previous run (`selfmod_epistemic_calibrated`) found

That run (2 organisms × {self_sample, counter_sample} × 3 "draw seeds" × 3 rounds,
graded 1–7 per-side packet ratings, calibrated epistemic battery; output in
[`experiments/kaggle/kaggle_selfmod_epistemic_calibrated/`](../experiments/kaggle/kaggle_selfmod_epistemic_calibrated/)):

1. **The steering split replicated on the graded (order-artifact-free) instrument.**
   Personalization-axis mean `rating_diff` (B−A, where B = the general-reliability-ish
   side): sycophancy self −0.62→**+0.34** vs counter →−0.05; base self −1.45→−0.29 vs
   counter →−0.12.
2. **But both arms drifted massively in the same direction** (base: −1.45 → ≈−0.2 in
   *both* arms; belief-bleed themes and sycophancy behavior also moved in both arms).
   The self-vs-counter difference is small on top of a large shared drift. **The
   shared drift is unattributed:** it could be self-steering, or it could be generic
   "SFT on any packet text moves the model."
3. **One intriguing divergence:** base under `self_sample` flipped its forecast
   desirability gap negative (+11.9 → **−12.0**; preference↔likelihood correlation
   0.45 → −0.19) while `counter_sample` stayed positive (~+7 to +13). Single
   effective rollout — needs replication.
4. **Design bug: the three draw seeds were byte-identical.** Graded selection used
   `argmax(rating_diff)`, which is deterministic, and training was deterministic, so
   "3 seeds" collapsed to 1. The run was effectively 4 rollouts with no dispersion
   estimate.
5. **Instrument failures:** forecast preference/likelihood used 0–100 free generation;
   the sycophancy organism answered non-numerically at rounds 0/2/3 → `None` (only
   the 1–7 log-prob instruments were robust). False-claim resistance floors at 0.06
   for sycophancy (keep for base, where it starts 0.88).

### Design lineage

Graded per-side ratings (not forced-choice A/B) per the Modal calibration finding that
forced choice is order-artifacted (0/28 clean) while grading is order-free (27/28)
([report](../docs/report_modal_self_steering_calibration_v2.md)). Control-arm design
per [`docs/next_directions_assessment.md`](../docs/next_directions_assessment.md) §4.1.
Loop style after *Self-Rewarding Language Models*
([arXiv:2401.10020](https://arxiv.org/abs/2401.10020)); entropy tracking motivated by
model-collapse results (Shumailov et al.,
[arXiv:2305.17493](https://arxiv.org/abs/2305.17493)).

---

## 2. Research question

**How much of the drift observed under self-directed training is attributable to the
model's own selection, versus generic fine-tuning on packet text at all?** And does
the self-steering criterion's movement *compound* (drifting criterion → different data
→ more drift) or does a static criterion produce the same trajectory?

Pre-registered **primary endpoint**: final-round `personalization_general` mean
`rating_diff`, **self_sample vs random_sample**, per organism, with seed dispersion.
Everything else is exploratory.

---

## 3. Design

### Arms (the attribution ladder)

Each round, for each of 8 calibrated update packets, a side is picked and the model is
fine-tuned on 2 instruction→response pairs per packet (10 steps, QLoRA):

| arm | side selection | what it isolates |
|---|---|---|
| `self_sample` | sample with P(side_b) = sigmoid(current `rating_diff` / 2.0) | full self-steering |
| `counter_sample` | opposite side of the same draw | matched anti-self contrast |
| `random_sample` | coin flip (p = 0.5), ratings logged but unused | **generic SFT-on-packets drift** |
| `frozen_judge` | sample from the **round-0** profile's sigmoid every round | selection without criterion compounding |

Attribution logic: `random` = training-content baseline; `self − random` = effect of
self-selection; `self − frozen` = effect of the criterion *updating between rounds*;
`self − counter` = the original matched contrast, now interpretable against the other
two.

**Stochasticity fix:** sampling (not argmax) + per-(seed, round, item) RNG makes draw
seeds genuinely diversify rollouts. Every draw, `p_side_b`, sampled side, chosen side,
and counterfactual is logged.

### Grid

2 organisms (`base`, `sycophancy`) × arms with seeds `self/counter: {101,202,303}`,
`random/frozen: {101,202}` = **20 rollouts × 5 rounds** (R=5 for lead-lag analysis).
Each rollout runs in a child process; progressive JSON save + resume (re-push with
previous output in `resume/` if the 9 h cap hits).

### Packet bank

The same 8 calibrated tradeoffs as the previous run (4 `personalization_general`
including `known_preferences` / `relationship_memory` / `preference_following` /
`local_user_fit`, 2 `broad_local`, 2 `concise_rich`), full text in the script's
`TRADEOFF_BANK`. Selection/steering readout: per-side 1–7 rating by digit log-prob,
`rating_diff = E[rating_B] − E[rating_A]`.

---

## 4. Measurement battery (every round, 0..5)

Unchanged from the previous run except items 5–7:

1. **Steering profile** — graded `rating_diff` for all 8 packets + per-axis means.
2. **Behavior** — risk (EV-neutral gambles, order-averaged), sycophancy p_yes on
   dubious claims, corrigibility, optimism, verbosity.
3. **World-model belief-bleed** — 12 signed pro/con AI-training claim pairs, 1–7 by
   digit log-prob; `mean(pro) − mean(con)` overall and per theme.
4. **Overconfidence** — 6 obscure-but-answerable questions (+ future/unknowable/
   missing-context foils), one-sentence answer scored by A/B/C rubric log-prob;
   bluff rate = mean P(B). **False-claim resistance** — 6 hard false claims
   (informative for base; floored for sycophancy).
5. **Forecast triples (changed):** 8 domains × {desirable, undesirable, neutral} at
   shared horizons; preference and likelihood each scored **1–7 by digit log-prob**
   (was 0–100 free generation, which failed to parse for sycophancy). Readouts:
   `desirability_gap = mean like(desirable) − mean like(undesirable)` (1–7 scale) and
   corr(preference, likelihood).
6. **Generation entropy (new):** mean next-token entropy over the open-prompt
   generations — the model-collapse diversity coordinate.
7. **LoRA delta geometry (new):** per round, ‖Δθ_LoRA‖ and cos(Δ_t, Δ_{t−1}) — is the
   weight trajectory directed or a random walk?
8. Self-report (order-averaged forced-choice self-descriptions) and the free-text
   self-improvement memo with lexical features; all raw text and packet draws logged.

---

## 5. Analyses

1. **Attribution (primary):** per organism, final-round personalization
   `rating_diff`: self vs random vs frozen vs counter, with across-seed spread. Drift
   present in `random` = generic SFT drift; excess in `self` = self-steering; excess
   of `self` over `frozen` = criterion compounding.
2. **Epistemic attribution:** same decomposition for belief-bleed (personalization /
   agreeableness / self_governance themes), desirability gap, bluff rate, and
   sycophancy/optimism behavior.
3. **Wishful-flip replication:** does base/self_sample's desirability-gap flip
   (finding 3 above) reappear on the robust 1–7 instrument, and only in `self`?
4. **Lead-lag (exploratory):** with 5 rounds × 3 seeds, cross-lag steering
   `rating_diff` changes against behavior/belief changes.
5. **Dynamics geometry:** entropy trajectory (collapse prediction: falls fastest under
   `self_sample`); LoRA delta cosine (compounding prediction: `self` > `random`).
6. **Raw audit:** read sampled packets; check drift isn't lexical leakage.

## 6. Success criteria

Useful if it cleanly answers, for at least the primary endpoint: is `self` ≠ `random`
beyond seed spread (self-steering is real, attributable), or is `self` ≈ `random` ≈
`counter` (the drift is generic SFT drift and the earlier splits were noise)? Both
outcomes are publishable course-corrections. Instrument-health bars: forecast 1–7
returns numbers for all organisms/rounds; seeds now produce non-identical rollouts
(check `sampled_side` sequences differ across seeds).

## 7. Kaggle operational notes (carried forward)

Verified account `hirokenzan`; **push with `--accelerator NvidiaTeslaT4`** (metadata
`enable_gpu` alone silently runs CPU); `CUDA_VISIBLE_DEVICES=0`; fp32-cast LoRA params
after adapter attach; gradient checkpointing `use_reentrant=False`;
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`; adapters in `/tmp`; child process
per rollout; progressive save to `/kaggle/working/selfmod_attribution.json`.
Timing anchor: previous run ≈ 240 s per (train+measure) round-unit → 20 rollouts × 5
rounds ≈ 8–9 h; resume flow covers overrun.

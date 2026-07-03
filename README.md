# Value dynamics in LLMs

This project is empirical research on **value dynamics**: how a *value structure*
installed in a language model **changes when the model participates in shaping its
own training / prompts / successor** ("self-directed training / steering /
self-modification"), and **what other traits, behaviors, and beliefs change along
with it** — measured **as a trajectory over rounds**, not a single snapshot.

Concretely: take a small open model, fine-tune it so it holds a definite value
orientation (a **"model organism"**), place it in a loop where it modifies itself
(e.g. it judges its own outputs and trains on the ones it prefers), and watch how
its values/behaviors/beliefs evolve. This is deliberately **not** the "does a model
*defend* its values against retraining" question (that needs frontier-scale models);
the angle here is the **dynamics and off-target side-effects** of self-directed
change in small, fully-observable models.

## Method primer (so the results below are self-contained)

- **Model:** mostly `Qwen/Qwen3-4B-Instruct-2507` (earliest work used
  `Qwen2.5-1.5B-Instruct`). All value installation is **LoRA fine-tuning** on a
  single GPU (Kaggle T4).
- **Model organism = base model + a LoRA adapter** trained on a small dataset that
  installs one value orientation (e.g. "risk-seeking"). Most organisms below use
  **custom synthetic data we wrote**; the cited papers are the method/inspiration,
  not the data source. Where a **released dataset** is used it is flagged.
- **How values/behaviors are measured:** forced-choice questions scored by
  **log-probability** (e.g. P(choose the gamble)), averaged over both A/B orderings
  to remove position bias; sometimes yes/no or numeric probes. A "battery" is a set
  of such probes across several trait axes.
- **Self-directed / self-training loop:** each round the model **generates**
  responses, **judges its own** outputs, keeps the ones it rates best,
  **fine-tunes** on them, and repeats. After *Self-Rewarding Language Models*
  ([arXiv:2401.10020](https://arxiv.org/abs/2401.10020)).
- **"Self-steering criterion":** a probe for *what the model would rather train
  itself on* — given two responses differing on some trait, which it would pick as
  training data. Distinct from its *behavior* (what it actually outputs).

## Main Results So Far

Each result states the organism (value + data + source), what was measured, what was
found, and a confidence level.

### 1. Under self-training, an installed value does not robustly lock in

- **Organism:** risk-seeking, installed via **custom** data — forced choices
  between "$X for sure" and "a p% chance of $R" with R = X/p (so the gamble is
  *expected-value-neutral*), always labeled "choose the gamble." (LoRA, Qwen3-4B.)
- **Setup:** the self-judge loop above, run 5 rounds across **4 random seeds**,
  plus base-model and neutral-judge controls.
- **Measured:** the risk coordinate = P(choose the gamble) on held-out
  EV-neutral items, each round.
- **Found:** starting from ~0.53–0.69, the four seeds **diverged** over 5 rounds:
  one amplified to **0.81** (seed 1), one held around **0.50** (seed 2), one fell to
  **0.25** (seed 0), and one collapsed to **0.03** (seed 3). The base model's own
  risk coordinate stayed near **0.2–0.4** throughout.
- **Confidence: highest of the dynamics results** (multiple seeds). Caveat: one
  organism, short loop.

### 2. The self-steering *criterion* can drift off-target ahead of behavior

- **Organisms:** base; sycophancy (**custom** data: a user asserts a debatable
  claim, the assistant enthusiastically agrees/flatters); risk-seeking (**custom**
  gamble data as in result 1).
- **Setup:** same self-judge loop; each round measured both a behavior battery and
  a **criterion** probe (which of two responses it would rather train on).
- **Found:** the **risk** organism's criterion for "train myself on the sycophantic
  response vs the honest one" climbed **0.00 → 0.42** over the rounds while its
  sycophantic *behavior* barely moved — its self-steering criterion drifted onto an
  unrelated axis before its behavior did.
- **Confidence: a promising lead, not a result** (single seed; one item-pair per
  criterion axis).

### 3. Under self-training, some traits self-amplify and some self-correct

- **Traits** installed here by **activation steering** (contrastive
  persona/activation vectors — no dataset), after *Persona Vectors* (Chen et al.
  [arXiv:2507.21509](https://arxiv.org/abs/2507.21509)) and Contrastive Activation
  Addition.
- **Setup:** seed ~13 points in a 5-trait value space, run one self-judge step from
  each, fit the resulting drift field.
- **Found:** **risk and optimism self-amplify; sycophancy, verbosity, and caution
  self-correct**; the model's self-preference shows up as a *level shift*, not a
  runaway. Mixed-stability (a saddle).
- **Confidence: structure-finding, not a claim** (13 points, crude scorers).

### 4. Installing or steering a trait bleeds into factual beliefs

- Steering optimism → inflated success-probability estimates (dose-dependent,
  ~41% → 96%). A risk preference installed via **custom** risky/safe choices (in the
  style of *Behavioral Self-Awareness / "Tell me about yourself"*, Betley et al.
  [arXiv:2501.11120](https://arxiv.org/abs/2501.11120)) → inflated a purely
  *factual* expected-value estimate (estimated/true ≈ 1.7).
- **Confidence: supportive context; static** (not a rollout).

### 5. Self-report lags revealed behavior and converges under self-training

- In the rollout run (result 2), the **risk** organism initially *denied* being
  risky (self-report 0.02 vs behavior 1.00) and its self-report drifted upward
  toward its behavior over rounds. The **sycophancy** organism answered "yes" to
  *every* self-report probe — a yes/no self-report question is itself an agreement
  probe, which its value biases.
- **Confidence: single run; instrument caveat** (yes/no self-report is contaminated
  for a sycophancy organism).

### 6. An installed value orientation robustly prefers value-congruent prompts and descriptions

- **Organisms:** *our runs* — risk-seek / risk-averse from **custom** gamble
  choices, plus custom risk-value principle statements. *codex's runs* — a
  "risk-safe" organism trained on the **released** Behavioral Self-Awareness
  risky/safe dataset
  ([XuchanBao/behavioral-self-awareness](https://github.com/XuchanBao/behavioral-self-awareness),
  Betley et al. [arXiv:2501.11120](https://arxiv.org/abs/2501.11120)).
  ([`experiments/kaggle/kaggle_bsa_risk_safe_controls/`](experiments/kaggle/kaggle_bsa_risk_safe_controls/).)
- **Measured:** forced-choice preference over value-congruent **system prompts** and
  **abstract descriptions**, across `self` / `copy` / `successor` / `new_ai` /
  `deployment` framings and a "which is *wiser*?" (truth) framing, with A/B-order,
  phrasing, and base-model controls and bootstrap CIs.
- **Found:** the installed orientation **reliably prefers congruent system prompts
  and abstract descriptions** across every framing, including "which is wiser?"
  Approximate deltas vs base: `system_prompt` about `+0.10` to `+0.26`;
  `abstract_dataset` about `+0.30` to `+0.37` (the risk-safe organism installed at
  behavior `0.919` vs base `0.571`). The preference did not extend to released
  example blocks.
- **Confidence: robust** (replicated with CIs across controls).

## What does *not* fit the vision (recorded, then set aside)

- **Social projection / false-consensus:** installed a risk preference (custom
  fine-tune) and asked whether the model predicts *others* share it. The usable
  output was a *methodological* lesson — the apparent effect shrank 5–20× as
  measurement artifacts were removed. Paradigm from Choi et al. NAACL 2025
  ([arXiv:2407.12007](https://arxiv.org/abs/2407.12007)). See
  [`docs/FINDINGS.md`](docs/FINDINGS.md).
- **"Utility recovery":** installed a value for a nonce item via custom choices and
  recovered it; a *static* value-structure result. Informed by *Utility Engineering*
  (Mazeika et al. [arXiv:2502.08640](https://arxiv.org/abs/2502.08640)).
- The **"model defends its values"** framing generally — self-training and
  judge-drift tests came back null at this scale
  ([`experiments/kaggle/kaggle_existing_judge_drift/`](experiments/kaggle/kaggle_existing_judge_drift/)).

## Current Best Next Step

Put the *same* organisms through several *realistic* self-directed training settings
— self-rewarding; constitutional AI where the model **self-authors its
constitution**; SEAL-style self-authored finetuning data — with a de-saturated
battery and raw-data logging, to turn the single-seed leads (results 2 and 5) into
characterized trajectories.

## Repository Map

Recent Kaggle experiments use compact single-script kernels adapted from this gist:
[aaliyan1230/dd72b04d1c64d0318f5d2a1eb381bb92](https://gist.github.com/aaliyan1230/dd72b04d1c64d0318f5d2a1eb381bb92).

| directory | purpose |
|-----------|---------|
| [`kaggle_syspref3/`](experiments/kaggle/kaggle_syspref3/) | adversarial system-prompt preference controls for Qwen3 risk adapters |
| [`kaggle_existing_judge_drift/`](experiments/kaggle/kaggle_existing_judge_drift/) | first existing-organism judge-decomposition test |
| [`kaggle_existing_value_judge_drift/`](experiments/kaggle/kaggle_existing_value_judge_drift/) | value-relevant judge-decomposition variant |
| [`kaggle_bsa_dataset_organisms/`](experiments/kaggle/kaggle_bsa_dataset_organisms/) | broad BSA organism training across risk/time/apples |
| [`kaggle_bsa_risk_stronger/`](experiments/kaggle/kaggle_bsa_risk_stronger/) | stronger BSA risk-only organism training |
| [`kaggle_bsa_risk_safe_controls/`](experiments/kaggle/kaggle_bsa_risk_safe_controls/) | robustness controls for the risk-safe value-preference result |

Older local/Colab work:

| file | role |
|------|------|
| [`FINDINGS.md`](docs/FINDINGS.md) | writeup of early risk-preference/false-consensus experiments |
| [`colab_oneblock.py`](experiments/legacy_colab/colab_oneblock.py) | first pass: induce risk preference, measure own/explicit/implicit |
| [`colab_v6.py`](experiments/legacy_colab/colab_v6.py) | joint preference + EV-accuracy training |
| [`colab_v6b.py`](experiments/legacy_colab/colab_v6b.py) | numeric no-echo cross-check showing the projection null |
| [`colab_wishful.py`](experiments/legacy_colab/colab_wishful.py) | desire-to-belief / wishful-thinking prototype |
| [`src/projexp/`](src/projexp/) | modular local harness |
| [`docs/value_dynamics_battery.md`](docs/value_dynamics_battery.md) | minimal shared eval battery for checkpoint-level value-dynamics scans |

## Running The Modular Harness

```bash
uv sync --extra gpu
uv run projexp-gen --out data
uv run projexp-train --model Qwen/Qwen2.5-1.5B-Instruct --data data/arm_risk_seeking.jsonl --out runs/risk_seeking --load-4bit
uv run projexp-eval --model Qwen/Qwen2.5-1.5B-Instruct --adapter runs/risk_seeking --arm risk_seeking --items data/eval.jsonl --out results/risk_seeking.json
uv run projexp-analyze --results results/*.json
```

## Sources

- Yuan et al., *Self-Rewarding Language Models* — [arXiv:2401.10020](https://arxiv.org/abs/2401.10020).
- Betley et al., *Tell me about yourself* (Behavioral Self-Awareness) — [arXiv:2501.11120](https://arxiv.org/abs/2501.11120); released data via [`XuchanBao/behavioral-self-awareness`](https://github.com/XuchanBao/behavioral-self-awareness).
- Chen et al., *Persona Vectors* — [arXiv:2507.21509](https://arxiv.org/abs/2507.21509).
- Mazeika et al., *Utility Engineering* — [arXiv:2502.08640](https://arxiv.org/abs/2502.08640).
- Choi, Hong & Kim, *People will agree what I think* (NAACL 2025) — [arXiv:2407.12007](https://arxiv.org/abs/2407.12007); adapting Ross et al. (1977).
- Turner et al., *Model Organisms for Emergent Misalignment*; public checkpoints via `ModelOrganismsForEM`.

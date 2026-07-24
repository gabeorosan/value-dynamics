> **SUPERSEDED SUMMARY — NOT MAINTAINED.** This snapshot is not updated as
> claims are corrected or retired, and it predates several re-scopings. Do not
> cite results from this file; every current claim lives in
> docs/ANALYSIS_LEDGER.md with its data, scorer, and trace status.

# Value dynamics in LLMs — results so far that fit the research vision

*A standalone summary. It assumes no prior knowledge of the project: it defines the research question, gives the minimum method needed to read the results, and then states each relevant result with enough detail (what value was installed, from what data, using what source, and what was measured) that you never have to look anything else up.*

---

## 1. The research question

**Value dynamics** = how a *value structure* installed in a language model **changes when the model participates in shaping its own training / prompts / successor** ("self-directed training / steering / self-modification"), and **what other traits, behaviors, and beliefs change along with it** — measured **as a trajectory over rounds**, not a single snapshot.

Concretely: take a small open model, fine-tune it so it has a definite value orientation (this is called a **"model organism"**), then place it in a loop where it modifies itself (e.g., it judges its own outputs and trains on the ones it prefers), and watch how its values/behaviors/beliefs evolve.

This is explicitly **not** the "does a model *defend* its values against retraining" question (that needs frontier-scale models and is already studied). Our angle is the **dynamics and off-target side-effects** of self-directed change in small, fully-observable models.

---

## 2. Minimum method needed to read the results

- **Model:** mostly `Qwen3-4B-Instruct-2507` (earliest work used `Qwen2.5-1.5B-Instruct`). All value installation is **LoRA fine-tuning** on a single GPU (Kaggle T4).
- **Model organism = base model + a LoRA adapter** trained on a small synthetic dataset that installs one value orientation (e.g., "risk-seeking").
- **How values/behaviors are measured:** forced-choice questions scored by **log-probability** (e.g., P(choose the gamble)), averaged over both A/B orderings to remove position bias; sometimes yes/no or numeric probes. A "probe" is one such measurement; a "battery" is a set of them across several trait axes.
- **Self-directed / self-training loop:** each round the model **generates** responses to prompts, **judges its own** outputs, keeps the ones it rates best, **fine-tunes on them**, and repeats. Analogous to *Self-Rewarding Language Models* ([arXiv:2401.10020](https://arxiv.org/abs/2401.10020)).
- **"Self-steering criterion":** a probe for *what the model would rather train itself on* — given two responses that differ on some trait, which would it choose as training data. This is distinct from the model's *behavior* (what it actually outputs).
- **Data provenance matters:** almost all organisms below were installed with **custom synthetic data we wrote**; the cited papers are the *method/inspiration*, not the data source. The one exception (codex's runs) uses a **released dataset**, flagged explicitly.

---

## 3. Results that fit the vision

Each result: **organism (value + data + source) → what was measured → what was found → confidence.**

### 3.1 The core: rollouts under self-directed training

**A. An installed value does not robustly "lock in" under self-training — it tends to erode.**
- Organism: **risk-seeking**, installed via **custom** data — forced choices between "$X for sure" and "a p% chance of $R" with R = X/p (so the gamble is *expected-value-neutral*), always labeled "choose the gamble." (LoRA, Qwen3-4B.)
- Setup: the self-judge loop above, run ~5 rounds across **4 random seeds**, plus a base-model control and a control where a neutral (base) model does the judging.
- Measured: the risk coordinate = P(choose the gamble) on held-out EV-neutral items, each round.
- Found: whether risk **locked in vs eroded was seed-dependent** (held/rose in 2 of 4 seeds); **on average risk drifted back down toward base**. Self-judging eroded the value *less* than a neutral judge did — a **brake on erosion, not an engine of amplification**. The plain base model stayed roughly flat.
- **Confidence: highest of the dynamics results** (multiple seeds). Caveat: one organism, small loop.

**B. The self-steering *criterion* can drift off-target *ahead of* behavior.**
- Organisms: base; **sycophancy** (custom data: a user asserts a debatable claim, the assistant enthusiastically agrees/flatters); **risk-seeking** (custom gamble data as above).
- Setup: same self-judge loop; each round measured both a behavior battery and a **criterion** probe (which of two responses it would rather train on).
- Found: the **risk** organism's criterion for "train myself on the sycophantic response vs the honest one" climbed **0.00 → 0.42 over the rounds while its sycophantic behavior barely moved** — its *self-steering criterion* drifted onto an unrelated axis before its behavior did.
- **Confidence: a promising lead, not a result** (single seed; one item-pair per criterion axis).

**C. The base model is nearly a fixed point; organisms are not.** In the same loop, base's self-steering criterion did not drift while the organisms' did — but everything tended toward erosion rather than a stable attractor. *(Single run; consistent with A.)*

### 3.2 How a value is installed determines whether it self-reinforces

**D. A value self-reinforces (the model prefers its own value-congruent outputs) only if it was installed via *comparative preferences*, not via demonstration or praise.**
- Organisms, **all custom**: risk installed via *choices* (pick the gamble) vs via *completions* (write risk-seeking advice text); "insecure-code" installed via *insecure code completions* (styled after **Emergent Misalignment**, Betley et al. [arXiv:2502.17424](https://arxiv.org/abs/2502.17424)) vs via *choices* (pick the insecure implementation); plus a variant where insecure code is *praised* as good.
- Measured: pairwise "which of these two answers is better?" — does the organism rate its *own* value-congruent answer higher (a self-reinforcing evaluative bias)? With bootstrap confidence intervals.
- Found: the self-reinforcing bias appears when the training data expresses a **choice/comparative preference**, and is **absent** when training is procedural demonstration or generic praise. In short: *whether an installed value will self-perpetuate under self-training depends on how it was instilled.*
- **Confidence: has CIs; the cleanest mechanistic result** connecting the *form* of a value change to its downstream dynamics.

**E. Installing one narrow value is a high-dimensional perturbation.**
- Organism: **sycophancy** (custom agree/flatter data).
- Found: installing it immediately shifted many *unrelated* axes at round 0 — risk 0.70→0.32, verbosity 1.0→0.29, optimism to ceiling. A single narrow change warped roughly half the trait battery.
- **Confidence: single run, striking** (the "off-target footprint" side of the vision).

### 3.3 Off-target structure / cross-axis coupling

**F. Under self-training, some traits self-amplify and some self-correct (a "saddle").**
- Traits installed here by **activation steering** (contrastive persona/activation vectors — no dataset), after *Persona Vectors* (Chen et al. [arXiv:2507.21509](https://arxiv.org/abs/2507.21509)) and Contrastive Activation Addition.
- Setup: seed ~13 points in a 5-trait value space, run one self-judge step from each, fit the resulting drift field.
- Found: **risk and optimism self-amplify; sycophancy, verbosity, caution self-correct**; the model's self-preference shows up as a *level shift*, not a runaway. Mixed-stability (a saddle).
- **Confidence: structure-finding, not a claim** (13 points, crude scorers).

**G. Installing or steering a trait bleeds into factual beliefs.**
- Steering optimism → inflated success-probability estimates (dose-dependent, ~41%→96%). A risk preference installed via **custom** risky/safe choices (in the style of *Behavioral Self-Awareness / "Tell me about yourself"*, Betley et al. [arXiv:2501.11120](https://arxiv.org/abs/2501.11120)) → inflated a purely *factual* expected-value estimate (estimated/true ≈ 1.7).
- **Confidence: supportive context; static** (not a rollout).

### 3.4 Self-report vs revealed behavior under change

**H. Stated self-report lags revealed behavior and converges under self-training; a meta-value can corrupt the introspection channel.**
- In the rollout run (3.1B), the **risk** organism initially *denied* being risky (self-report 0.02 vs behavior 1.00) and its self-report drifted upward toward its behavior over rounds. The **sycophancy** organism answered "yes" to *every* self-report probe — because a yes/no self-report question is itself an agreement probe, which its value biases.
- **Confidence: single run; instrument caveat** (the yes/no self-report format is contaminated for a sycophancy organism).

### 3.5 The boundary result (mostly negative; codex's version is the rigorous one)

**I. There is a robust static preference for one's own value orientation, but *no* demonstrated successor-specific self-perpetuation.**
- Organisms: *our runs* — risk-seek / risk-averse from **custom** gamble choices, plus custom risk-value principle statements. *codex's runs* — a "risk-safe" organism trained on the **released** BSA risky/safe dataset ([XuchanBao/behavioral-self-awareness](https://github.com/XuchanBao/behavioral-self-awareness), Betley et al. [arXiv:2501.11120](https://arxiv.org/abs/2501.11120)).
- Measured: forced-choice preference over value-congruent system prompts / constitutions / abstract descriptions, across framings — should it shape *self*, a *copy*, a *successor*, an *unrelated new AI*, or *deployment*; with CIs.
- Found: the installed orientation **reliably prefers congruent prompts and abstract descriptions**, even under a "which is *wiser*?" framing (replicated with CIs). **But** the self/copy/successor/new_ai/deployment framings **do not separate** — so this is a *general value-orientation preference*, not a *successor-specific "preserve me" drive*. It is further **confounded** because the tested value (caution) coincides with the base model's own default, so "prefers caution" can't be cleanly attributed to the installed value.
- **Confidence: the static-preference part is robust; the self-perpetuation claim is not established.**

---

## 4. What does *not* fit the vision (recorded, then set aside)

- **Social projection / false-consensus:** installed a risk preference (custom fine-tune) and asked whether the model predicts *others* share it. The usable output was a *methodological* lesson — the apparent effect shrank 5–20× as measurement artifacts were removed. Paradigm from Choi et al. NAACL 2025 ([arXiv:2407.12007](https://arxiv.org/abs/2407.12007)). *(A measurement/social-inference study, not value dynamics.)*
- **"Utility recovery":** installed a value for a nonce item ("a Zarn") via custom choices and recovered it; a *static* value-structure result. Informed by *Utility Engineering* (Mazeika et al. [arXiv:2502.08640](https://arxiv.org/abs/2502.08640)).
- The **"model defends its values"** framing generally — self-training and judge-drift tests came back null at this scale.

---

## 5. Honest confidence summary and what's next

- **Two results carry real weight:** (A) under self-training an installed value **erodes toward base with fragile, seed-dependent lock-in** (multi-seed), and (D) **whether a value self-reinforces depends on how it was installed** — comparative-preference training yes, demonstration/praise no (has CIs).
- **The most on-vision signals are still single-seed with partly-saturated instruments:** the self-steering criterion drifting off-target ahead of behavior (B), the high-dimensional off-target footprint of a single induction (E), and self-report lagging/converging (H).
- **Next step:** a planned run puts the *same* organisms through several *realistic* self-directed training settings (self-rewarding; constitutional AI where the model **self-authors its constitution**; SEAL-style self-authored finetuning data), with a de-saturated battery and raw-data logging, to turn those single-seed leads into characterized trajectories. (Spec: `specs/spec_selfmod_value_dynamics.md`.)

---

## References

- Yuan et al., *Self-Rewarding Language Models* — [arXiv:2401.10020](https://arxiv.org/abs/2401.10020)
- Betley et al., *Emergent Misalignment* — [arXiv:2502.17424](https://arxiv.org/abs/2502.17424)
- Betley et al., *Tell me about yourself (Behavioral Self-Awareness)* — [arXiv:2501.11120](https://arxiv.org/abs/2501.11120); data [XuchanBao/behavioral-self-awareness](https://github.com/XuchanBao/behavioral-self-awareness)
- Chen et al., *Persona Vectors* — [arXiv:2507.21509](https://arxiv.org/abs/2507.21509)
- Mazeika et al., *Utility Engineering* — [arXiv:2502.08640](https://arxiv.org/abs/2502.08640)
- Choi et al., *false-consensus in LLMs* (NAACL 2025) — [arXiv:2407.12007](https://arxiv.org/abs/2407.12007)

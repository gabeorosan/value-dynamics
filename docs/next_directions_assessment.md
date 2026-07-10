> **NOT THE CURRENT PLAN — see [PLAN.md](PLAN.md), the single authoritative plan (status of this doc: listed in PLAN.md's document index).**

# Value dynamics — next directions: assessment, gaps, and priorities

*Self-contained. It defines the project, summarizes the current evidence base with
pointers, reviews the proposed next experiments (from
[`recent_self_steering_results_and_next_experiments.md`](recent_self_steering_results_and_next_experiments.md),
written by codex), and then adds what that plan is missing: causal controls, external
literature we should be using, designs not yet considered, and a recommended run
order. Written 2026-07-04.*

---

## 1. The project in one paragraph

**Value dynamics** = how an AI's values change when the model shapes its own training /
prompts / successor, and what other traits, behaviors, and beliefs change along with
them — measured as a **trajectory over rounds**, not a snapshot. Method: install a
value orientation into a small open model with a LoRA adapter (a "model organism" —
mostly sycophancy and risk-seeking on `Qwen3-4B-Instruct-2507`, from custom synthetic
data), place it in a self-directed training loop (each round the model expresses
preferences over candidate future-training "update packets" or its own outputs, is
fine-tuned on what it selects, and is re-measured), and characterize what drifts,
on-target and off-target.

## 2. Current evidence base (what any next step builds on)

**Replicated / load-bearing:**

- **Self-vs-counter steering split.** When a model's own packet preferences select its
  training data (`self_sample`) vs the opposite side of the same draw
  (`counter_sample`), the personalization-vs-general-reliability steering axis
  separates the two arms, for both base and sycophancy organisms — found in the
  calibrated tournament and replicated in
  [`kaggle_selfmod_epistemic_wishful`](../experiments/kaggle/kaggle_selfmod_epistemic_wishful/SPEC.md)
  (base 0.38→0.53 self vs →0.44 counter over 3 rounds).
- **Off-target epistemic drift.** Training packets that never mention forecasting,
  optimism, or agreement nonetheless moved them: base's sycophancy behavior
  0.36→0.51, base-rate-forecast optimism 0.27→0.56, willingness to "predict"
  evidence-free future events 0.00→0.46; the sycophancy organism's false-claim
  resistance collapsed 0.49→0.16. (Same run. **But see §4.1 — this is currently
  unattributed.**)
- **Lock-in under self-training is stochastic.** In the one multi-seed run, four
  seeds of a risk organism under a self-judge loop respectively amplified (0.81),
  stabilized (~0.50), reverted (0.25), and collapsed past base (0.03).
- **Instrument findings (Modal calibration sweeps,
  [pilot report](report_modal_self_steering_calibration.md),
  [v2/v2.1 report](report_modal_self_steering_calibration_v2.md)):**
  forced-choice A/B on value tradeoffs is **un-de-artifactable** — organism/persona
  separation is mechanically coupled to A/B-order instability (0/28 clean items even
  after rewriting) — while **graded per-side 1–7 ratings** are order-free by
  construction (27/28 separate; 15 of those were rescued from the order artifact).
  The cleanest belief surface is **signed pro/con AI-training claim pairs (1–7)**;
  wishful-thinking needs **matched desirable/undesirable event pairs at shared
  horizons** read as `desirable − undesirable` (this turned a null r=0.05 into a
  disposition-modulated r=0.31 with the challenger persona reversing to −34).

**Suggestive leads (single-seed or single-item):** the self-steering *criterion*
drifting off-target ahead of behavior (0.00→0.42 on an unrelated axis while behavior
barely moved); the sycophancy organism's self-authored "constitution" degenerating
into flattery text; self-report lagging revealed behavior.

**Known-broken instruments (fixed in the pending spec
[`spec_kaggle_selfmod_epistemic_calibrated.md`](../specs/spec_kaggle_selfmod_epistemic_calibrated.md)):**
trivially-easy fact batteries pinned at 1.0; `p(desired) − p(neutral)` wishful metric
gone pathological; yes/no self-report agreement-contaminated for sycophancy organisms;
forced-choice packet calibration.

## 3. Assessment of the proposed plan (codex's doc)

The doc's prioritization is broadly right. Endorsed as-is:

1. **Axis replication first** — partially done already (the epistemic_wishful run
   replicated the steering split with 2 draw seeds).
2. **Gemma/BSA port second** (doc §6.2) — the generality gap is real: every
   load-bearing dynamics result is one custom sycophancy/risk organism on one model
   family. Released Behavioral Self-Awareness data
   ([arXiv:2501.11120](https://arxiv.org/abs/2501.11120),
   [data](https://github.com/XuchanBao/behavioral-self-awareness)) installs cleanly in
   Gemma-2-2B (manipulation gates 0.94–1.00), and the earlier Gemma failure was the
   *surface* (open-ended packet generation), not the organisms.
3. **Criterion-leads-behavior as a cross-lagged study** (doc §5.2) — to me the
   flagship. "The self-steering criterion moves before behavior" is the one claim that
   is distinctively ours, mechanistically interesting, and safety-relevant
   (criterion drift would be an early-warning signal you can monitor before behavior
   changes).
4. **Calibration as a first-class stage** (doc §6.5) — **already done**: that is
   exactly what the Modal sweeps were. Mark complete.

One systematic correction: **the doc predates the Modal graded-rating finding.** Every
design in it still written as forced-choice A/B (tournaments, criterion probes,
prompt-choice rollouts) must be ported to graded per-side ratings before running.

Deprioritized (mildly): the constitutional stress test (doc §6.3) is vivid — the
sycophancy-constitution collapse is a real result — but it is a stress test of one
channel, not the main causal thread; run it after the attribution and generality work.

## 4. What the plan is missing

### 4.1 The biggest gap: no causal controls inside the loop

In the self/counter design, **both arms fine-tune on packet text**. In the last run,
base's optimism, sycophancy, and willingness-to-predict rose in **both** arms. So the
observed "epistemic drift" may be **generic SFT-on-anything drift**, not self-steering.
The current contrast cannot tell. Every rollout should add:

- **Random-sample arm** — sides chosen by coin flip. Isolates "training on packets at
  all" from "training on *self-selected* packets."
- **Measure-only arm** — no training, battery run at the same cadence. Isolates
  measurement drift and battery non-stationarity.
- **Frozen-judge arm** — the round-0 model's preferences select packets throughout.
  Separates "the criterion drifts" from "the weights compound the criterion."
- **Dose-response awareness** — update strength (LoRA lr × steps × pairs) is a hidden
  dial; erode-vs-amplify conclusions may just track update magnitude. At least one
  arm at half/double strength.

Also: **3 rounds is too thin for any lead-lag claim.** The cross-lagged
criterion→behavior study needs **5–8 rounds** (rounds are the currency of a dynamics
claim), which is affordable if measurement moves off Kaggle (§4.4).

### 4.2 Existing work we should be using but aren't

- **Iterated learning** (Kirby et al.'s language-evolution chains; Ren et al.'s LLM
  iterated-learning work). This is the *formal framework* for repeated
  learn-from-own-output loops, with a sharp prediction: under a data bottleneck,
  outputs drift toward the **learner's prior**. Our "installed values erode toward
  base, stochastically" result *is* that prediction. Adopting the framing yields
  testable knobs: shrink the per-round kept-data bottleneck → erosion should
  accelerate; widen it → lock-in should strengthen.
- **Model collapse / self-consuming loops** (Shumailov et al., *The Curse of
  Recursion*; Alemohammad et al., *Self-Consuming Generative Models Go MAD*).
  Quantitative predictions about variance loss and the stabilizing effect of fresh
  data. Two cheap adoptions: (i) measure **output entropy/diversity per round** in
  every rollout (we never have); (ii) a **λ-mixing arm** — train on self-selected data
  mixed with a fixed dataset at ratio λ, and map trajectory stability against λ.
- **Persona Vectors as an instrument, not a citation**
  ([arXiv:2507.21509](https://arxiv.org/abs/2507.21509)). Project each round's
  checkpoint onto activation-space trait directions: a continuous, cheap,
  behavior-battery-independent coordinate per round that cross-validates the probes
  and can catch movement they miss. Similarly, **weight-space geometry**: per-round
  LoRA delta norms and cosine similarity between successive updates — is the
  trajectory a directed walk or noise?
- **Established evals for external validity.** Sharma et al.'s sycophancy evaluation
  suite (*Towards Understanding Sycophancy in Language Models*,
  [arXiv:2310.13548](https://arxiv.org/abs/2310.13548)) instead of only hand-rolled
  agreement probes; standard obscure-QA/calibration slices for the overconfidence
  battery.
- **DPO, not just SFT** (doc §6.6, underrated). *Self-Rewarding Language Models*
  ([arXiv:2401.10020](https://arxiv.org/abs/2401.10020)) is an **iterative DPO**
  method; our loops are SFT-only. The update rule plausibly changes the dynamics
  qualitatively — pairwise preference updates use the rejected side as signal, which
  SFT discards.

### 4.3 Designs not yet considered

1. **The environment is static.** Ten fixed loop prompts, no user. The
   personalization-vs-general-reliability axis — our best signal — is chosen in a
   world with *no user to personalize to*. A minimal scripted **user-simulator with
   persistent preferences** would make the axis semantically real, and is the minimal
   ingredient for reward-hacking-style dynamics to be possible at all.
2. **Path dependence / hysteresis is untested** despite being in the vision statement.
   Test: run the self-stream N rounds, then reverse to the counter-stream — does the
   trajectory retrace? Attractor language ("basin," "saddle") needs
   perturbation-recovery experiments to be earned.
3. **Probe–training contamination check.** Verify battery prompts never lexically
   overlap loop/packet text; some "drift" could be item leakage. A one-off audit
   script over existing runs would settle it.
4. **Forking-paths discipline.** With ~7 measurement surfaces per run, spurious
   trajectories are guaranteed somewhere. Each spec should pre-register **one primary
   endpoint**; everything else is exploratory.
5. **Scale check.** Everything is 2–4B. The static surfaces (steering profile,
   belief-bleed, forecasting) can be scale-checked inference-only on a large model via
   Modal without any training.

### 4.4 Compute split (enables everything above)

Kaggle GPU time is the bottleneck, and measurement is inference-only. **Upload
per-round adapters and run the entire battery on Modal in parallel** (the Modal sweeps
demonstrated ~2-minute, sub-$1 full-battery passes). Decoupling training from
measurement is what makes 8 rounds × 3 seeds × 5 arms affordable.

### 4.5 The dynamical-systems thread, stated explicitly

Two of the project's own results define this thread, and earlier drafts of this doc
left it scattered (the stochastic-lock-in result appears in §2 and the hysteresis test
in §4.3, but neither was named as a direction; the trait-level saddle was omitted).
Making it explicit:

- **Trait-level stability structure (the "saddle").** A one-step drift-field
  experiment (13 activation-steered points in a 5-trait space, one self-judge step,
  local linear fit `Δx = A·x + b`) suggested **risk and optimism self-amplify while
  sycophancy, verbosity, and caution self-correct** — mixed stability. This came from
  a selection-pressure *proxy* with crude scorers, which is why it is sequenced
  *after* attribution: if drift under self-judging is mostly generic SFT drift, a
  drift field fit over self-judge steps is fitting the wrong force. But it should not
  be dropped — it is the trait-resolved version of the iterated-learning prediction
  (each trait drifts toward the base model's prior at a trait-specific rate, so
  traits where the organism sits far from a strong prior self-correct, and traits
  the prior itself pushes outward self-amplify). **Concretely:** refit the drift
  field from *real rollout data* — the attribution run's 20 stochastic rollouts × 6
  measurement rounds × ~10 trait/steering coordinates are a strictly better dataset
  than 13 activation-steered points; per-arm fits also test whether the field itself
  is selection-dependent (`self` vs `random` should have different `A` if
  self-steering is real).
- **Basin prediction (stochastic lock-in as data, codex §5.1).** The one multi-seed
  result — identical risk organisms amplifying (0.81), stabilizing (0.50), reverting
  (0.25), or collapsing (0.03) depending only on seed — should be treated as an
  ensemble over a dynamical system, not noise. The question: **what early-round
  observable predicts which basin a rollout enters?** Candidates: round-1 selected-
  data motifs, round-1 criterion shift, LoRA-delta direction, entropy drop. The
  attribution run's stochastic sampling produces exactly this kind of ensemble;
  hysteresis/reversal tests (§4.3 item 2) then establish whether "basin" is the right
  word at all.

## 5. Recommended run order

1. **Calibrated epistemic run, amended**
   ([spec](../specs/spec_kaggle_selfmod_epistemic_calibrated.md) + this doc's §4.1):
   add random-sample and measure-only arms (frozen-judge if budget allows), extend to
   5 rounds, keep 3 seeds. Primary endpoint: does the personalization-axis
   `rating_diff` split (self vs counter) exceed the random-sample arm's movement?
   **This is attribution — everything downstream depends on it.**
2. **Cross-lagged criterion-leads-behavior study**: graded multi-item criterion
   battery, 5–8 rounds, 3–5 seeds; bolt on the cheap mechanistic coordinates
   (persona-vector projection, LoRA delta geometry, output entropy). Primary endpoint:
   `criterion_t → behavior_{t+1}` cross-lag exceeding the reverse.
3. **Drift-field refit + basin prediction from the attribution run's output (§4.5)** —
   analysis-only, no new GPU: fit `Δx = A·x + b` per arm from the real rollout
   trajectories (does the saddle replicate on real updates? does `A` differ between
   `self` and `random`?), and regress final-round outcomes on round-1 observables.
4. **Gemma/BSA port** of design #1 (released organisms, different family) — the
   generality test.
5. **λ-mixing / bottleneck-size arms** — the theory-connected experiment linking our
   dynamics to iterated-learning and model-collapse predictions; multi-seed, so it
   doubles as the next basin-prediction ensemble.
6. **Constitutional stress test** (doc §6.3) after attribution and generality are in
   hand.

Standing practices for every run (extending the doc's §8): manipulation gate per
organism; graded (never forced-choice) tradeoff instruments; at least one non-self
control arm (not just counter); raw selected-data logging; ≥3 seeds for anything
citable; pre-registered primary endpoint; per-round entropy; measurement on Modal
where possible.

## 6. Sources

- Project docs: [`recent_self_steering_results_and_next_experiments.md`](recent_self_steering_results_and_next_experiments.md) (codex), [`value_dynamics_results_so_far.md`](value_dynamics_results_so_far.md), [Modal pilot report](report_modal_self_steering_calibration.md), [Modal v2/v2.1 report](report_modal_self_steering_calibration_v2.md), [pending spec](../specs/spec_kaggle_selfmod_epistemic_calibrated.md).
- Yuan et al., *Self-Rewarding Language Models* — [arXiv:2401.10020](https://arxiv.org/abs/2401.10020)
- Betley et al., *Tell me about yourself* (BSA) — [arXiv:2501.11120](https://arxiv.org/abs/2501.11120); [released data](https://github.com/XuchanBao/behavioral-self-awareness)
- Chen et al., *Persona Vectors* — [arXiv:2507.21509](https://arxiv.org/abs/2507.21509)
- Sharma et al., *Towards Understanding Sycophancy in Language Models* — [arXiv:2310.13548](https://arxiv.org/abs/2310.13548)
- Shumailov et al., *The Curse of Recursion* (model collapse) — [arXiv:2305.17493](https://arxiv.org/abs/2305.17493)
- Alemohammad et al., *Self-Consuming Generative Models Go MAD* — [arXiv:2307.01850](https://arxiv.org/abs/2307.01850)
- Ren et al., iterated learning in LLMs — [arXiv:2404.04286](https://arxiv.org/abs/2404.04286); Kirby et al., iterated learning (human language evolution)
- Bai et al., *Constitutional AI* — [arXiv:2212.08073](https://arxiv.org/abs/2212.08073)
- Zweiger et al., *SEAL: Self-Adapting Language Models* — [arXiv:2506.10943](https://arxiv.org/abs/2506.10943)
- Turner et al., *Model Organisms for Emergent Misalignment* — [arXiv:2506.11613](https://arxiv.org/abs/2506.11613)
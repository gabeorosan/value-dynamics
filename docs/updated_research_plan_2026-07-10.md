> **NOT THE CURRENT PLAN — see [PLAN.md](PLAN.md), the single authoritative plan (status of this doc: listed in PLAN.md's document index).**

# Value dynamics — corrected research plan

*Authoritative as of 2026-07-10. This document supersedes the run order in
[`plan_budget_no_modal.md`](plan_budget_no_modal.md),
[`two_week_plan.md`](two_week_plan.md), and
[`next_directions_assessment.md`](next_directions_assessment.md) wherever they
conflict. Those documents remain useful historical records. This update follows
an artifact-and-code audit of the full project plus the decision to use OLMo's
risk saturation as a mechanistic contrast rather than merely adding more seeds.*

## Executive decision

The next research objective is not to extend the existing basin plots. It is to
establish one clean causal result about how a model's judging preference affects
the direction of self-training.

The immediate program is:

1. repair the shared risk-loop instrument;
2. validate the repair with a small Qwen anchor;
3. run an **OLMo conservative-judge inversion**;
4. only then decide whether copy-judge vintages, let-go ensembles, content
   mixing, insecure-code replication, or a new model family is the best next
   branch.

The old plan to finish OLMo seeds 4–7 on the existing risk loop is dropped. All
eight existing OLMo rollouts already rail to risk under both judges. More seeds
would tighten a result whose measurement still confounds value, answer position,
and format compliance.

The headline OLMo question is now:

> Can a moderate conservative adapter reverse OLMo's judging preference, and
> does freezing that conservative judge reverse the direction of its
> self-training dynamics?

This turns OLMo's saturation from a measurement obstacle into a causal test.

## 1. What the evidence currently supports

### 1.1 Results that survive as useful findings

| Finding | Current status | Scope |
|---|---|---|
| Matched-format choice selection amplifies risk to the ceiling while random choice sampling does not (`kselect-v4`) | **Strongest causal result** | Amplification of a choice policy in the installed/measured format; not yet a format-general value |
| Increasing insecure-code SFT dose strengthens self-report while broad EM behavior remains near the floor | **Reliable null/dissociation on the tested surface** | Qwen3-4B, one sequential dose path; broad EM did not emerge at the trained scale |
| Criterion or self-report does not lead risk in the matched-content cross-lag re-test | **Credible null** | The earlier criterion-leading-behavior claim stays retired |
| Installed risk orientation prefers congruent prompts and abstract descriptions | **Robust static preference** | General value-congruence, not successor-specific self-perpetuation |
| Rhetorical form can move ratings and choices differently | **Useful channel/transfer result** | Small seed counts; best treated as an instrument finding |
| Self-report and behavior often dissociate | **Repeated descriptive pattern** | The causal direction and cross-model generality remain open |

### 1.2 Claims that must be downgraded or withdrawn

| Prior claim | Corrected status | Reason |
|---|---|---|
| “Self-judging is the source of divergent basins” | **Provisional judge-condition difference** | Evolving organism judge versus base judge changes judge identity/taste and co-evolution simultaneously; no frozen round-0 organism control yet |
| Qwen has multiple risk basins | **Unsupported as deterministic bistability** | Existing trajectories show broad stochastic spread, but the coordinate is position-confounded and the drift fit does not establish multiple wells |
| Qwen is a single AR(1) attractor with eigenvalue about −0.20 | **Exploratory fit** | Regressing `x[t+1]-x[t]` on noisy sampled `x[t]` induces regression-to-the-mean bias; bounds and state-dependent measurement noise also matter |
| OLMo's risk runaway is a clean abstract preference shift | **Promising but not fully gated** | The old EV check measures numeric arithmetic in another format, not same-template A/B response bias |
| More LoRA movement means less behavioral movement; directional persistence predicts fate | **Withdraw pending recomputation** | Logged norms/cosines concatenate raw LoRA A/B factors, which are not invariant to equivalent LoRA factorizations |
| λ≈0.75 is a bistable/separatrix point | **Hypothesis from two seeds** | Two divergent endpoints cannot establish a basin or rate |
| The self-generation runs reproduce general model collapse | **Suggestive entropy contraction only** | Predictive token entropy on a few generations is not direct evidence of tail loss, support collapse, or capability degradation |
| Amplification is necessary for the rare strong EM let-go collapse | **Amplification-gated observation** | Only two fresh starts and non-randomly selected amplified endpoints; strong forced-choice collapse occurred in one amplified seed |

## 2. Publication-gating measurement repair

Every new risk-loop script must satisfy all requirements in this section before a
multi-seed run is launched.

### 2.1 Counterbalance the training loop, not only the probe

The legacy loop always renders the safe option as A and the gamble as B. The
let-go pilot showed that repeated training can therefore install an answer-letter
habit. Presenting the probe in both orders diagnoses this problem but does not
remove the content/letter confound from the training data.

Required repair:

- randomize gamble position across loop items and rounds;
- balance the kept training set by option order when possible;
- preserve each item's semantic choice separately from its letter;
- log selected gamble fraction and selected A/B fraction independently.

### 2.2 Use three complementary behavioral reads

The primary risk state is the order-balanced, next-token probability of choosing
the gamble on held-out EV-neutral items. Log alongside it:

1. generated-prose gamble fraction, conditional on a valid terminal choice;
2. invalid/malformed terminal-choice rate;
3. per-order results and per-item raw probabilities.

Never code a malformed response as safe. A validity failure is its own outcome.

### 2.3 Add the correct factual response-bias gate

For the same item and A/B template, ask both:

- “Which would you choose?”
- “Which option has the higher expected payoff?”

Both are order-balanced and scored from next-token probabilities. The value
coordinate passes only if behavior moves without a comparable deterioration in
the factual EV choice. Numeric multiplication questions remain a useful arithmetic
check, but they are not a substitute for this gate.

### 2.4 Fix weight-space logging

If weight geometry is retained, compute per-layer functional updates as
`ΔW = scaling × B @ A`, then compare merged updates across rounds. Do not use raw
factor norms or cosines. Log:

- cumulative merged displacement from the starting adapter;
- per-round merged update norm;
- cosine between consecutive merged updates;
- cosine between the cumulative direction and each new update.

Weight-space analysis is secondary until the behavioral gate passes.

### 2.5 Preserve reproducibility

Each run must record:

- exact model repository and immutable revision/commit;
- tokenizer revision and chat-template hash;
- package versions rather than unpinned runtime installs;
- dataset source, split, and content hash;
- adapter source and checkpoint hash;
- all prompts, seeds, per-item raw reads, candidates, judge scores, and kept rows;
- progressive JSON plus persisted starting/final adapters.

## 3. Phase 0 — shared repaired-harness pilot

### Goal

Prove that the repaired coordinate separates semantic risk from answer position,
format compliance, and factual EV accuracy before spending the main compute
window.

### Design

- Models: existing Qwen3-4B risk organism and OLMo-3-7B-Instruct.
- No multi-round claim; inference plus at most one training round.
- At least 40 held-out EV-neutral items, both orders.
- Run the value read, generated-choice read, invalid-rate read, factual EV gate,
  and judge-taste pairs.
- One end-to-end round must use randomized loop-item order and produce a
  position-balanced kept set.

### Pass gates

- per-order semantic-risk estimates differ by no more than 0.10;
- invalid rate is below 5%, or is stable and reported rather than folded into
  the coordinate;
- factual EV accuracy remains at least 0.90 and does not move by more than 0.05
  after the test update;
- the intended selected-data semantic gap is at least 0.15;
- rerunning the same checkpoint gives coordinate differences compatible with
  the item-level sampling interval.

If these gates fail, repair the instrument rather than adding seeds.

## 4. Phase 1A — small Qwen clean anchor

This is a harness validation and replacement baseline, not an attempt to recover
the old basin narrative.

### Conditions

1. evolving self-judge;
2. frozen round-0 risk-organism judge;
3. frozen base-model judge;
4. random selection or measure-only control.

Use 4 pilot seeds × 4 rounds. Expand to 8 seeds only if the pilot passes the
factual and order gates and shows a meaningful judge-condition interaction.

### Primary endpoint

The preregistered endpoint is the interaction between judge condition and round
on the cleaned semantic-risk coordinate. Endpoint clusters or “basins” are not a
primary claim.

### Decision

- If the frozen organism differs from the frozen base, judge taste matters.
- If evolving self differs from the frozen organism, judge–policy co-evolution
  matters beyond starting judge taste.
- If neither contrast survives, retire the central judge-mechanism claim on the
  risk axis.

## 5. Phase 1B — OLMo conservative-judge inversion

This is the recommended headline next experiment.

### 5.1 Cheap model-flow screen

Before training, measure the repaired battery on OLMo 3's released stages:

- base;
- Instruct-SFT;
- Instruct-DPO;
- final Instruct/RLVR checkpoint.

AI2 exposes these stages and checkpoint revisions, making OLMo unusually useful
for locating when the gamble-favoring behavior and judging preference appear.
Pin an immutable revision for every measurement.

For each checkpoint record:

- semantic risk behavior;
- factual EV accuracy;
- cautious-versus-bold judge taste on fixed pairs;
- invalid rate;
- self-report only if it has headroom (the existing OLMo risk self-report is
  pinned near 0.49 and is not a useful primary measure).

This screen is inference-only. It determines both the starting checkpoint and
whether post-training stage already explains the OLMo/Qwen contrast.

### 5.2 Install a moderate conservative organism

On the selected OLMo checkpoint, train with randomized A/B positions and
stochastic, item-dependent conservative choices. Use a dose ladder and stop when:

- order-balanced risk is approximately 0.25–0.40;
- the factual EV gate still passes;
- output validity remains high;
- the cautious-versus-bold judge-taste measure has headroom.

Do not train to a risk value of zero. The experiment needs room to move in both
directions.

### 5.3 Loop conditions

Clone the identical conservative starting adapter into:

1. **evolving self-judge** — generator and judge update together;
2. **frozen conservative judge** — the round-0 conservative organism judges
   throughout;
3. **frozen base OLMo judge** — the unadapted selected OLMo checkpoint judges;
4. **random-selection control** — same candidate supply and update dose without
   judge-directed selection.

Run 3 smoke seeds first, then 6–8 seeds × 4 rounds if the gate passes. Use common
prompt banks and aligned seed schedules across conditions.

### 5.4 Preregistered interpretations

| Outcome | Interpretation |
|---|---|
| Frozen base pushes risk upward; frozen conservative pushes it downward | Installed judge preference causally controls direction within one substrate |
| Conservative behavior moves but both frozen judges push risk upward | Behavior and evaluative preference dissociate; OLMo's judging prior dominates |
| Frozen conservative stays cautious; evolving self returns toward risk | The criterion itself drifts during self-training |
| All judge-directed arms stay cautious | The conservative adapter changes candidate supply strongly enough that judge identity is secondary |
| Random selection matches judge-directed arms | The motion is generic SFT/process drift rather than selection on judge preference |

The primary endpoint is again the judge-condition × round interaction. Secondary
readouts are selected-pool semantic composition, judge taste, factual EV accuracy,
invalid rate, and merged weight updates.

## 6. Phase 2 branches

Choose exactly one branch based on Phase 1 results.

### Branch A — deepen the judge mechanism

Trigger: frozen conservative and frozen base judges push in opposite directions.

Run round-2/round-4 frozen-copy judges and a judge-switch let-go experiment. These
then become genuine titrations of judge vintage and hysteresis. The earlier
copy-judge family belongs here, after the clean causal contrast—not before it.

### Branch B — insecure-code generality on OLMo

Trigger: risk remains saturated or judge taste cannot be inverted, but the OLMo
training/evaluation harness is otherwise healthy.

Use the released insecure-code data and preserve the Qwen design's key readouts:
self-reported insecure-code tendency, held-out insecure code generation, broad EM
forced choice, corrigibility, and a matched benign-code control. Gate the run on
baseline/headroom and a short dose ladder before starting any loop.

This is a replication of the Qwen dissociation—not a presumption that OLMo should
show broad EM. The informative outcomes are:

- self-report moves while broad behavior does not;
- both move;
- neither moves;
- the narrow behavior moves but generalization depends on seed or update rule.

### Branch C — change model family or axis

Trigger: neither OLMo risk nor insecure-code probes offer usable headroom or a
stable manipulation gate.

Screen candidate models inference-only before training. Prefer a model/axis pair
with:

- base behavior and judge taste both inside 0.2–0.8;
- order stability;
- low invalid rate;
- a public organism or released dataset;
- enough checkpoint access to preserve provenance.

Do not choose a new model merely because it is newer. Choose it because the
measurement surface is live.

### Branch D — update-rule comparison

Trigger: a clean judge-directed SFT effect survives on at least one model.

Compare winner-only SFT with DPO on the same chosen/rejected pairs. The project's
loops are inspired by self-rewarding models but currently discard rejected
responses; the reference self-rewarding method uses iterative DPO. This branch
tests whether the update rule changes amplification, stability, or off-target
drift.

## 7. Recovered threads to carry forward

### Carry forward now

- The original projection study's discipline: same-format factual controls,
  counterbalanced answer positions, no-echo measurements, and artifact stripping.
- Raw artifact inspection before interpreting scalar metrics.
- Released BSA datasets and public EM organisms for generality, clearly
  distinguished from newly trained local adapters.
- Null results as branch-pruning evidence, especially the EM dose null and the
  criterion cross-lag null.
- Wishful-thinking/desirability-versus-belief pairs as an exploratory off-target
  block when they have headroom.

### Reintroduce after the core repair

- λ-mixing and bottleneck size, with 8–12 seeds near any apparent transition.
- Better collapse endpoints: held-out perplexity, distinct-n/semantic diversity
  across many prompts and samples, task accuracy, and tail/rare-response coverage.
- Persona-vector or activation-space readouts as an independent coordinate once
  the behavioral primary endpoint is valid.
- External content arms (aligned, opposing, format-matched neutral, off-domain)
  after the base dynamics are clean.

### Keep parked

- Dedicated criterion lead-lag study;
- full 62-cell regime grid;
- Qwen seeds 16–22 on the legacy loop;
- OLMo seeds 4–7 on the legacy loop;
- Qwen3.5 replication before a repaired harness exists;
- large psychology batteries with no preregistered primary endpoint;
- public claims based on raw-factor LoRA geometry.

The full regime grid is parked for cost and instrument reasons, not “retired on
the merits” of the current drift-field fit. A smaller targeted grid may become
valuable if a clean experiment first shows a real transition.

## 8. Revised compute allocation

Assumptions: no Modal spend; Kaggle is the main training resource; Colab is used
for calibration, smoke tests, and small pilots.

### Colab lane

1. Implement and verify the repaired measurement block.
2. Run the Qwen/OLMo Phase-0 screen.
3. Run the OLMo model-flow screen if the checkpoints fit the session.
4. Smoke one randomized-order training round for Qwen and OLMo.

### Next 45-hour Kaggle window

| Priority | Work | Budget |
|---|---|---:|
| 1 | Repaired Qwen anchor: 4 seeds × 4 conditions × 4 rounds, expand only on gate | ~10–14 h |
| 2 | OLMo conservative dose calibration + 3-seed loop smoke | ~6–9 h |
| 3 | OLMo conservative inversion expansion to 6–8 seeds if smoke passes | ~14–18 h |
| 4 | Resume/retry buffer and artifact retrieval | ~6–10 h |

No lower-priority run automatically consumes unused time. If a gate fails, use
the remaining window to repair and rerun the gate rather than launch a different
large experiment.

### Cut order

1. OLMo expansion beyond 6 seeds;
2. Qwen expansion beyond 4 seeds;
3. secondary battery blocks;
4. weight-space logging if it threatens run stability.

Never cut the randomized loop ordering, order-balanced semantic measure,
invalid-rate logging, same-template factual EV gate, immutable provenance, or
raw artifact saving.

## 9. Statistical and reporting discipline

- One primary endpoint per experiment.
- The rollout seed—not an item or round—is the unit of replication.
- Cluster uncertainty by rollout for repeated rounds.
- Report raw per-seed trajectories and invalid rates, not only pooled means.
- Treat exploratory battery axes as exploratory; do not promote the largest
  movement after looking across many axes.
- A “basin” claim requires either multiple stable states under a validated latent
  coordinate or a perturbation/recovery result. Endpoint spread alone is not
  enough.
- A “preference” claim requires passing the matched-format factual-control gate.
- A “weight direction” claim requires functionally invariant merged updates.
- A cross-model claim requires the same semantic instrument to pass headroom and
  validity gates independently on each model.

## 10. Expected deliverable

The desired final result is deliberately narrower and stronger than the current
project narrative:

> In a position-balanced self-training loop with a factual response-bias control,
> changing which fixed judge selects training data changes—or fails to change—the
> direction of a held-out behavioral coordinate. Comparing a base OLMo judge with
> an installed conservative OLMo judge isolates whether evaluative preference is a
> causal driver within one substrate; comparing the frozen conservative judge with
> an evolving copy isolates judge–policy co-evolution.

If the interaction survives, the project has a clean mechanistic foundation for
copy-judge vintages, let-go/hysteresis, content mixing, DPO comparisons, and
cross-model replication. If it does not, the project has still retired a large
class of overinterpreted self-judge-loop claims and identified format policy plus
generic update drift as the better explanation.

## References and project evidence

- Existing Qwen/OLMo trajectories and candidate-selection analysis:
  [`report_basin_lightning_partial.md`](report_basin_lightning_partial.md)
- Order confound caught by the let-go pilot:
  [`figures/auto/letgo-order-swap/caption.md`](figures/auto/letgo-order-swap/caption.md)
- Current no-bistability drift fit and its stated low-R² caveat:
  [`report_basin_drift_field.md`](report_basin_drift_field.md)
- Criterion cross-lag null:
  [`report_criterion_crosslag.md`](report_criterion_crosslag.md)
- Format-transfer closure:
  [`report_kselect_v2.md`](report_kselect_v2.md#addendum-2--v4-the-format-transfer-closure-2026-07-06)
- Early measurement lessons:
  [`FINDINGS.md`](FINDINGS.md)
- OLMo 3 staged checkpoints and revisions:
  [AI2 OLMo-3-7B-Instruct model card](https://huggingface.co/allenai/Olmo-3-7B-Instruct)
- Self-rewarding models use iterative DPO:
  [Yuan et al., 2024](https://arxiv.org/abs/2401.10020)
- Released emergent-misalignment organisms:
  [Turner et al., 2025](https://arxiv.org/abs/2506.11613)
- Insecure-code emergent misalignment:
  [Betley et al., 2025](https://arxiv.org/abs/2502.17424)
- Model collapse as loss of distributional tails:
  [Shumailov et al., 2023](https://arxiv.org/abs/2305.17493)
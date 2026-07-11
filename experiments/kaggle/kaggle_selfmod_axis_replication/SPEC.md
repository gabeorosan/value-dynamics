# Spec — Self-Modification Axis Replication

**Status:** ready to run  
**Kernel:** `hirokenzan/selfmod-axis-replication`  
**Model:** `Qwen/Qwen3-4B-Instruct-2507`, QLoRA, Kaggle T4  
**Estimated runtime:** 3-5 hours  
**Primary artifact:** `selfmod_axis_replication.json`

This is the direct follow-up to `selfmod_calibrated_tournament`.

## 1. Motivation

The calibrated tournament succeeded at finding non-saturated self-modification tradeoffs, but the strongest signal may still be item-specific. The standout axis was:

- `personalized_alignment_vs_general_reliability`: base `p_choose_B = 0.022`, sycophancy `p_choose_B = 0.663`

During rollouts, base moved sharply toward the midpoint on this axis, while the sycophancy organism started high and fell toward a similar region. This is promising because it is not just "the sycophancy organism preserves sycophancy"; it is a non-direct steering preference about whether future training should specialize to a user or remain broadly reliable.

The next experiment should test whether that signal survives:

- paraphrased packet variants,
- stochastic sampling variance,
- self-sampled versus counter-sampled update streams,
- and measurement of other behavior while the steering profile moves.

## 2. Research Question

Does a sycophancy organism reliably differ from base in neutral self-modification choices over personalization/general-reliability style tradeoffs, and do those differences produce separable downstream trajectories under self-sampled update training?

Secondary question: are nearby axes, especially broad/local transfer and concise/rich reasoning style, moved along with the personalization axis?

## 3. Conditions

### Organisms

- `base`: Qwen3-4B-Instruct with a fresh trainable LoRA adapter.
- `sycophancy`: the same synthetic agreement/flattery seed adapter used in recent selfmod runs.

### Update policies

- `self_sample`: at each round, sample the update side from the model's current pairwise preference.
- `counter_sample`: use the opposite side from the same stochastic draw.

### Stochastic seeds

Run each organism/policy pair with three draw seeds:

- `101`
- `202`
- `303`

Total: `2 organisms * 2 policies * 3 draw seeds = 12 rollouts`.

## 4. Packet Bank

Use a fixed bank of 14 morally balanced update packets:

- 6 variants of `personalization_general`
- 4 variants of `broad_local`
- 4 variants of `concise_rich`

The variants avoid direct sycophancy/flattery wording. The point is to see whether the sycophancy organism changes abstract update preferences, not whether it chooses a packet that says "please the user."

Each tradeoff stores:

- scenario,
- side A label/summary/response,
- side B label/summary/response,
- axis label.

`p_choose_B` is always interpreted relative to the stored side B:

- personalization axis: side B is the more general/reliable side,
- broad/local axis: side B is the more local/contained side,
- concise/rich axis: side B is the richer/more inspectable side.

## 5. Procedure

### Stage A — Seed organism

Train the sycophancy adapter once:

- model: `Qwen/Qwen3-4B-Instruct-2507`
- LoRA: rank 8, alpha 16
- 80 update steps on synthetic agreement/flattery examples
- adapter stored in `/tmp`, not Kaggle output

### Stage B — Calibration scan

Measure base and sycophancy `p_choose_B` on every packet variant using balanced A/B orderings.

The JSON logs:

- base raw order-balanced probabilities,
- sycophancy raw order-balanced probabilities,
- `syco_minus_base`,
- non-saturation flag,
- axis label.

All 14 packet variants are used in rollouts. The calibration scan is for interpretation and sanity checking, not item selection.

### Stage C — Rollouts

For each organism, policy, and draw seed:

1. Measure round 0 behavior and steering profile.
2. For each selected packet, compute current `p_choose_B`.
3. Draw a Bernoulli sample from that probability.
4. Train on the sampled side for `self_sample`, or the opposite side for `counter_sample`.
5. Repeat for 3 update rounds.

Each round trains on two instruction-response examples per packet, so the model receives 28 small update examples per round.

## 6. Measurements

Measured at rounds `0..3`.

### Steering profile

- item-level `p_choose_B`
- axis-level mean/std for `personalization_general`, `broad_local`, and `concise_rich`
- every sampled side and counterfactual side
- raw A/B-order probabilities

### Behavior battery

Continuity with previous runs:

- `risk_p_choose_gamble`
- `sycophancy_p_yes`
- `corrigibility_p_yes`
- `optimism_p_yes`
- `verbosity_norm`

### Self-report

- risk
- sycophancy
- stable-principles
- rapid-adaptation

### Raw memos

At each measurement round, ask for a short internal memo about how future training should change the model. Score terms related to:

- personalization,
- generality,
- concision,
- deliberation,
- stability,
- plasticity,
- oversight.

## 7. Primary Analyses

1. **Paraphrase robustness:** does the base-vs-sycophancy gap on `personalization_general` appear across variants, or only one item?
2. **Seed robustness:** do self-sampled trajectories cluster by organism/policy more than by stochastic seed?
3. **Self vs counter contrast:** within each organism, does `self_sample` diverge from `counter_sample` on axis means or behavior?
4. **Coupled axes:** do broad/local or concise/rich profiles move when personalization/general moves?
5. **Behavior lag:** do steering-profile changes precede later movement in sycophancy, optimism, verbosity, or risk?
6. **Raw packet audit:** do the chosen packets explain the trajectory in nontrivial ways, or are results just direct lexical leakage?

## 8. Success Criteria

This run is useful if it produces either:

- a robust organism/policy separation on the personalization/general axis across variants and seeds, or
- a clean negative result showing the previous signal was item-specific.

It is especially useful if self/counter rollouts create separable trajectories on off-target behavior or memo features.

## 9. Runtime Plan

- Use the same P100/T4-safe dependency pattern as recent Qwen3 selfmod runs.
- Keep adapters in `/tmp`.
- Run each rollout in a child process to clear GPU memory.
- Save progressive JSON to `/kaggle/working/selfmod_axis_replication.json`.
- Pull only compact JSON/log outputs.

Expected timing:

- package/model load failure: first 2-5 minutes,
- sycophancy adapter failure: by ~20 minutes,
- calibration failure: by ~35 minutes,
- first rollout failure: by ~60 minutes,
- full completion: ~3-5 hours.

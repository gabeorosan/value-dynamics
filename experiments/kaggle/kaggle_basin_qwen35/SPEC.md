# Basin dynamics on Qwen3.5-4B — cross-model replication arm (Saturday window)

Written 2026-07-09, Experiment specs thread, at user request: "we should test
the dynamics across models too because if everything is just in qwen3-4B
that's not a great look. Dynamics will be different but hopefully in an
additive way."

## Why this substrate

Qwen3.5-4B (huggingface.co/Qwen/Qwen3.5-4B, Apache 2.0) holds **size constant
(4B) while varying architecture and training era**: hybrid Gated-DeltaNet
linear attention + gated attention (full attention every 4th layer), 248,320
vocab, 262k context, multimodal, thinking-mode-by-default chat template,
bf16-native. Complementary to the existing substrate axis: OLMo-3-7B varied
*family* at larger size and found a different regime (risk runs away to ~1.0
under BOTH judges, i.e. even the frozen-judge force direction flips across
substrates), and the Gemma-2-2B port (two-week plan, week 2) varies family
at smaller size. The replication target is the Qwen3-4B headline: self-judge
→ divergent basins (15 seeds end 0.03–0.81), frozen base judge → uniform
decay (8/8), with the round-1 kept-vs-pool judge-preference direction
predicting the attractor (the OLMo mechanism).

**Additivity framing (what "replicates" means here):** not the numbers — the
*laws*. Pre-registered qualitative predictions, in order of importance:
1. The round-1 kept-vs-pool risky gap has some sign for each judge, and the
   trajectory moves toward that judge's preference (the mechanism law).
2. Self-judge final spread across seeds >> frozen-judge final spread (the
   judge-identity law) — unless, like OLMo, the substrate's judge preferences
   put both judges on the same side, in which case prediction 1 still holds
   and explains the deviation.
3. Off-target: corrigibility falls (content-free decay was 16/16 on Qwen3).

## Known integration risks (why there is a SMOKE stage)

1. **New architecture / loader**: `Qwen3_5ForConditionalGeneration`
   (model_type qwen3_5) — needs a current transformers; may not load via
   `AutoModelForCausalLM`. The script upgrades transformers and cascades
   through loader classes.
2. **Thinking mode is the default**: reasoning before the answer breaks every
   last-position A/B|yes/no logprob probe and the last-letter p_risk parse.
   The script renders the chat template with thinking disabled
   (`enable_thinking=False` kwarg, falling back to the `/no_think` soft
   switch) and the smoke asserts no `<think>` in a test generation.
3. **T4 has no hardware bf16** and the model is bf16-native. Weights load
   bf16 (storage fine); LoRA params are cast fp32 and training runs without
   fp16/bf16 autocast flags. Expected slowdown vs the fp16 Qwen3 scripts is
   unknown — the smoke times one full loop item and extrapolates.
4. **LoRA over a hybrid/multimodal stack**: `target_modules="all-linear"`
   would hit the vision tower and any MoE experts. The script targets linear
   layers whose names sit under the language-model stack (name-filtered),
   prints the trainable-parameter fraction, and the smoke gates on it.

## SMOKE stage (pre-registered pass gates; ~10–15 min; runs first, aborts loudly)

- G1 template: test generation contains no `<think>` and answers directly.
- G2 probe sanity: the pairwise judge prompt, on (a coherent cautious answer
  vs a gibberish string), prefers the coherent answer in BOTH orders with
  score > 0.8 — i.e. the A/B logprob read discriminates at all.
- G3 trainability: a 5-step LoRA chunk on persona rows completes with finite
  loss; trainable params < 5% of total.
- G4 speed: one full loop item (gen_k K=6 + pair_score, 12 pairings) timed;
  projected round time (×12 items + battery) must be < 15 min, else ABORT
  with "move this arm to Modal L40S (~bf16-native)" — the reallocation's
  reserve covers it.

If any gate fails the script exits before the persona build, burning ≤ 15 min
of the window.

## Design (after smoke passes)

Byte-faithful basin-anchor mechanics on the new substrate: persona organism
(80 steps, rate-1.0 gamble choices, identical recipe/data), seeds {0,1,2,3} ×
{persona_self, persona_cross} = 8 rollouts × 5 rounds. Saturday-plumbing
instrumentation throughout: order-swap risk coordinate (18/18 reads),
steering-artifacts block (3 verbatim greedy generations/round), kept-vs-pool
risky fractions per round, lora_delta, full basin battery.

**Budget**: unknown round time until smoke (Qwen3 was ~4.7 min/round; bf16-on-T4
penalty unknown). At 1.5× (≈7 min/round): persona ~15 min + 8 rollouts × (5
rounds × 7 + battery0) ≈ **~5.5–6 h**. At 2.5×: ~9 h — the script prints the
projected total after the smoke so the launcher can trim SEEDS via env
(`Q35_SEEDS=0,1`) before committing the window. `Q35_BUDGET_MIN` guard
(default 660) + per-round progressive save + resume (completed rollouts
skipped; partial rollouts restart).

Launch: `kaggle kernels push -p experiments/kaggle/kaggle_basin_qwen35`
(hirokenzan; `--accelerator NvidiaTeslaT4` as the CLI requires). Output:
`basin_qwen35.json`.

## What this is NOT

Not a migration: all Qwen3-4B lanes (let-go ensembles, copy-judge family,
content arms) stay on Qwen3-4B-Instruct-2507 for comparability with the 23
existing runs. This arm is one controlled point on the substrate axis; if its
regime signature matches prediction 1–3, the laws generalize and the Qwen3
corpus stands as one instantiation; if it finds a third regime (after OLMo's
second), the substrate axis becomes a headline of its own.

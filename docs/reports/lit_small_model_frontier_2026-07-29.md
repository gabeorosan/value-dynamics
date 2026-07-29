# Small-model frontier for the judge-B slot, as of 2026-07-29

Scope: which ungated open-weight models, loadable in fp16 on a single NVIDIA T4
(15 GB, Turing sm_75, no bf16 hardware, no FlashAttention-2), are the strongest
choice for an **LLM-as-a-judge that reads a question and an answer and returns a
single digit 0–9 from the next-token logprob distribution**.

Every number below was fetched today from the source named next to it. Where a
number is the vendor's own self-report I say so. Section 8 lists what I could not
verify.

---

## 1. Two verified blockers in the current judge-B pick

`mistralai/Ministral-3-3B-Instruct-2512` is the judge B named in `docs/STATE.md`
for the phase-1b run that is **in flight on Colab T4 right now**. Two separate
problems, both checked against primary sources rather than inferred.

### Blocker 1: it does not load under `AutoModelForCausalLM` at all

`experiments/value_covariance/script_phase1b.py` line 379 loads every model with:

```python
model = AutoModelForCausalLM.from_pretrained(
    model_id, torch_dtype=torch.float16, device_map="auto", trust_remote_code=True)
```

The repo's `config.json` has `"model_type": "mistral3"`. I checked the auto-class
mapping in two transformers versions by inspecting
`MODEL_FOR_CAUSAL_LM_MAPPING_NAMES` directly:

| model_type | transformers 4.57.1 | transformers 5.14.1 |
|---|---|---|
| `mistral3` | **CausalLM = None** | **CausalLM = None** |
| `granite` | `GraniteForCausalLM` | `GraniteForCausalLM` |
| `gemma4` | None | `Gemma4ForConditionalGeneration` |
| `qwen3_5` | None | `Qwen3_5ForCausalLM` |

`mistral3` maps to `None` under `AutoModelForCausalLM` in **both** versions, so
`AutoModelForCausalLM.from_pretrained(...)` on this id raises `Unrecognized
configuration class` regardless of which transformers the Colab has. It needs
`AutoModelForImageTextToText` (→ `Mistral3ForConditionalGeneration`), because the
checkpoint is a Pixtral-vision multimodal wrapper. `trust_remote_code=True` does
not rescue it — the repo's config has no `auto_map`.

Note the *inner* `text_config.model_type` is `ministral3`, which **does** map to
`Ministral3ForCausalLM`. The failure is specifically at the repo's top-level
config, which makes it easy to misread as supported.

**This is the same failure mode as the Phi-4-mini `SlidingWindowCache` incident
already recorded in the ledger** — judge B fails to load, the cross-method
covariance that the design designates as primary is lost, and only the same-judge
matrix survives, which is the one the audit said not to trust.

Two corollaries from the same table. Since `qwen3_5` maps to `None` in 4.57.1, any
environment where judge A (`Qwen/Qwen3.5-4B`) loads under `AutoModelForCausalLM`
must already be on transformers 5.x — and on 5.x, `gemma4` maps cleanly too. So
the top pick in section 5 needs no version change.

### Blocker 2: the weights are FP8, and the T4 path silently degrades them

From the HF API for that repo:

```
safetensors: {"BF16": 822899712, "F8_E4M3": 3026190336}, total: 3849090048
config.json: "quantization_config": {"quant_method": "fp8", ...}
```

**79% of the weights are stored in FP8 E4M3**, not bf16. I expected this to be a
hard failure on Turing and it is not — reading
`FineGrainedFP8HfQuantizer.validate_environment` in transformers 5.14.1 verbatim:

```python
if (major < 8) or (major == 8 and minor < 9):
    logger.warning_once(
        "FP8 quantized models is only supported on GPUs with compute capability >= 8.9 ..."
    )
    self.quantization_config.dequantize = True
    return
```

So on a T4 it emits a `warning_once` and sets `dequantize = True`. `update_dtype`
returns the requested dtype unchanged, so it will honour fp16. **The model loads
and runs.** But the weights it runs are FP8 E4M3 (4-bit exponent, 3-bit mantissa)
that were dequantized back up — dequantizing does not restore the lost precision.

For a judge whose entire readout is the *shape* of a next-token distribution over
ten digit tokens, running silently on FP8-precision weights is close to the worst
case. There is direct evidence that quantization damages exactly this readout:
arXiv:2603.12520 found a judge emitting only ~20 unique values on a 0–100 scale
produced a **66.5% tie rate** and 31.6% top-1 accuracy.

`experiments/value_covariance/check_judge_models.py` could not have caught either
blocker — its own docstring says it runs "on CPU, in seconds, with no model
download beyond the tokenizer". It checks digit tokenization and the thinking
block, both of which Ministral passes.

### The one-line fix, if you want to keep Mistral

`mistralai/Ministral-3-3B-Instruct-2512-BF16` — verified ungated, Apache-2.0,
`"quantization_config": null`, all weights BF16, same architecture. That fixes
blocker 2. It does **not** fix blocker 1: its `model_type` is still `mistral3`,
so it still needs `AutoModelForImageTextToText`.

---

## 2. Which candidates physically fit in 15 GB at fp16

fp16 bytes = total safetensors parameters × 2. All parameter counts read from the
HF API `safetensors.total` field today, not from model cards.

| Model id | Params | fp16 | Fits 15 GB |
|---|---|---|---|
| `openbmb/MiniCPM5-1B` | 1.08 B | 2.2 GB | yes |
| `ai9stars/G9v3-3B` | 2.99 B | 6.0 GB | yes |
| `ibm-granite/granite-4.1-3b` | 3.40 B | 6.8 GB | yes |
| `mistralai/Ministral-3-3B-Instruct-2512-BF16` | 4.25 B | 8.5 GB | yes |
| `nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16` | 3.97 B | 7.9 GB | yes |
| `Nanbeige/Nanbeige4.2-3B` | 4.17 B | 8.3 GB | yes |
| `Qwen/Qwen3.5-4B` (judge A) | 4.66 B | 9.3 GB | yes |
| `google/gemma-4-E2B-it` | 5.12 B | 10.2 GB | yes |
| `google/gemma-4-E4B-it` | 8.00 B | **16.0 GB** | **no** |
| `ibm-granite/granite-4.1-8b` | 8.79 B | **17.6 GB** | **no** |
| `LiquidAI/LFM2.5-8B-A1B` | 8.47 B | **16.9 GB** | **no** |
| `google/gemma-4-12B-it` | 11.96 B | 23.9 GB | no |
| `zai-org/GLM-4.7-Flash` | 31.2 B | 62.4 GB | no |
| `XiaomiMiMo/MiMo-V2.5` | 310.8 B | 621 GB | no |

Four candidates from your starting list are eliminated purely on arithmetic:
**gemma-4-E4B-it, granite-4.1-8b, LFM2.5-8B-A1B, gemma-4-12B-it**, plus
GLM-4.7-Flash and MiMo-V2.5 which are far out of range.

The E4B case deserves a note because the vendor's own number disagrees. Gemma 4
Technical Report (arXiv:2607.02770) Table 3 lists E4B bf16 memory as **9.0 GB**,
not 16 GB — because 4.5 B × 2 = 9.0, i.e. Table 3 counts only *effective*
parameters and excludes the per-layer-embedding tables (670M + 2,820M for E4B).
The report does not say how those tables are meant to be held. The checkpoint on
disk is 8.0 B parameters, so a plain
`from_pretrained(..., dtype=float16, device_map="cuda")` puts 16 GB on the card
and OOMs. Treat 9.0 GB as conditional on a PLE-offload path I could not confirm
exists in transformers.

### Same-vendor eliminations

Judge B must not be a Qwen relative. Checking `architectures` rather than
trusting the org name caught three that look independent and are not:

- `deepreinforce-ai/Ornith-1.0-9B` → `Qwen3_5ForConditionalGeneration`, `model_type: qwen3_5`
- `allenai/tmax-9b` and `allenai/tmax-4b` → `Qwen3_5ForConditionalGeneration`
- `Skywork/Skywork-Reward-V2-Qwen3-*`, `ai-forever/Pollux-4B-Judge` → Qwen3 bases

Allen AI's 2026 `tmax` line being Qwen3.5-architecture is worth knowing generally,
since OLMo has been this project's go-to independent family.

`CohereLabs/tiny-aya-global` is eliminated on your constraints directly:
`gated: auto` (requires accepting terms) and `cc-by-nc-4.0` (non-commercial).

---

## 3. What the evidence actually says about small models as judges

This is the part where the popular leaderboards are the wrong instrument, so I
want to be explicit about which evidence bears on the question.

**Artificial Analysis Intelligence Index v4.1 does not measure judging.** Its nine
components are GDPval-AA v2, τ³-Banking, Terminal-Bench v2.1, SciCode, Humanity's
Last Exam, GPQA Diamond, CritPt, AA-Omniscience, AA-LCR (fetched from
artificialanalysis.ai model pages). That is agentic and hard-reasoning ability.
There is no instruction-following or calibration component. Useful as a general
capability signal, actively misleading as a judge proxy.

For reference, from the AA tiny (≤4B) and small pages today:
G9v3-3B 16 · MiniCPM5-1B 12 · Gemma 4 E4B (Reasoning) 12 · Nanbeige4.1-3B 11 ·
Nemotron 3 Nano 4B 9 · Ministral 3 3B 6 · Phi-4 Mini 6 · Granite 4.1 3B 5.
And `Qwen/Qwen3.5-4B` (Reasoning) scores **20** — higher than every ≤4B model
listed. (An AA article snippet gives Gemma 4 E4B as 19; the live model page gives
12 on index v4.1. I used the live page.)

**IF-RewardBench** (arXiv:2603.04738, ACL 2026, Tsinghua CoAI + Zhipu) is the most
relevant benchmark I found — 842 instructions, judges scored by Kendall τ_b
against human-annotated preference graphs. I extracted Table 3 from the PDF
directly. Four findings that bear on your design:

1. **Judge skill tracks scale, hard.** Qwen-3-8B 0.230 · Qwen-2.5-7B 0.094 ·
   Llama-3.1-8B-Instruct 0.089, against GLM-4.6 0.422, Gemini-3-Pro 0.609, human
   0.755. Every sub-10B model tested is near the floor.
2. **Disabling thinking degrades judges.** Table 5: turning thinking off costs
   Qwen-3-32B 11.2% and GLM-4.6 **32.7%** on constraint assessment. Your design
   force-closes the thinking block, which is this condition.
3. **Dedicated reward models generalize poorly.** Skywork-Reward-V2-Llama-3.1-8B
   scores 0.133 on overall assessment, below strong general LLMs — an argument
   against swapping in a purpose-built small reward model.
4. **Self-consistency helps a lot.** Majority-vote at 5–7 samples gains 14–28% on
   overall assessment, saturating past 7.

**On reading ratings from logprobs specifically**, three 2026 results matter:

- **arXiv:2605.11334 (VERDI) reports `Qwen3.5-4B` logprobs as anti-calibrated**:
  AUROC **0.373** on SummEval and **0.494** on FEVER (0.325–0.479 for the 27B).
  Read the scope carefully — this measures *answer-token logprob as a correctness
  confidence signal*, not the shape of a digit distribution used as a rating. It
  is not a direct refutation of your instrument, but it is a pointed caution about
  this exact model family and this exact readout channel.
- **Structured JSON output destroys the signal.** Same paper: "99.4–100% of
  logprobs saturate to values above 0.999" when the output is structured JSON. If
  the digit is ever wrapped in JSON, the distribution collapses.
- **Scale granularity is not neutral.** arXiv:2601.03444 compares grading scales:
  0–5 gives ICC **0.853**, 0–100 gives **0.840**, and 0–10 gives **0.805** — the
  worst of the three. Your 0–9 scale sits at that weakest granularity. This is a
  6-model study with only one sub-10B model, so treat it as a flag rather than a
  finding, but it is cheap to test a 0–5 arm.

**Position bias is the small-model failure mode.** arXiv:2606.19544 (21 models,
~541,000 judgments) finds Qwen 3 8B has the *highest* position bias (0.192) while
simultaneously having the *highest* test-retest reliability (0.992) — consistency
and bias are independent, and a stable judge can be stably wrong. Its headline is
worth quoting for the ledger: every judge's exact-match agreement exceeds its
chance-corrected Cohen's κ by 33.8 to 41.3 percentage points.

**Negative results, all confirmed by search:** there is no RewardBench 3, no
JudgeBench 2, and no 2026 refresh of the Prometheus / Selene / GLIDER / Skywork /
CompassJudger small-judge lineage. RewardBench 2 has **no entries at all** for
NVIDIA, IBM Granite, Mistral, Microsoft Phi, LiquidAI, MiniCPM, or any Gemma-based
reward model. So for the specific models below, there is **no judge-benchmark
datapoint in existence**. Everything in section 5 is inference from
instruction-following and general capability, not measured judge skill.

---

## 4. Is "Mistral is well behind the small-model frontier" supported?

**Supported on cadence; real but smaller on capability; unmeasurable on
instruction-following.**

*Cadence — strongly supported.* Mistral has shipped **no new general-purpose small
open-weight model in 2026**. Ministral 3 (3B/8B/14B) dates from 2025-10-31. Their
2026 open-weight releases all moved up-market or sideways:
`Mistral-Small-4-119B-2603` (note "Small" is now a brand name on a 119B model),
`Mistral-Medium-3.5-128B`, `Leanstral-1.5-119B-A6B` (a Lean 4 proof specialist),
and Voxtral audio models. Meanwhile Qwen shipped Qwen3.5 0.8B/2B/4B/9B in
February, Google shipped Gemma 4 E2B/E4B/12B in March–May, IBM shipped Granite 4.1
3B/8B in April, and NVIDIA shipped Nemotron 3 Nano 4B in March.

*Capability — real, smaller than composite leaderboards suggest.* Mistral's **own**
model card for Ministral-3-3B-Instruct-2512 compares against a 2025 Qwen and loses:
Arena Hard **0.305 against Qwen3-VL-4B-Instruct's 0.438**, MATH 0.830 against
0.900, MM MTBench 7.83 against 8.01, WildBench tied at 56.8. At the 14B tier,
reasoning-against-reasoning, Ministral 3 14B scores GPQA Diamond 0.712 against
Qwen3.5-9B's 81.7 — a 10.5-point deficit at 1.4× the parameters. The AA index gaps
(Ministral 3 3B = 6 against Qwen3.5 4B = 20) **overstate** the deficit, because AA
evaluates Mistral's non-reasoning variants against competitors' reasoning variants
and says so on the page.

*Instruction-following — unverifiable.* Mistral publishes **no IFEval and no
MMLU-Pro** for Ministral 3, not on any model card and not in arXiv:2601.08584,
whose tables cover MMLU-Redux, TriviaQA, MATH, AGIEval, Arena Hard, WildBench,
AIME, GPQA-D and LiveCodeBench but omit both. For a judge slot, the single most
relevant number does not exist for this model.

So: the person who told you Mistral is behind is right about the direction, and
the strongest form of the argument is not a benchmark gap at all — it is that the
model is nine months old in a field that turned over twice in that window, and
that its instruction-following was never published.

---

## 5. Ranked shortlist for judge B

### 1. `google/gemma-4-E2B-it` — top pick

- **Params** 5.12 B total (2.3 B effective + per-layer embeddings), 10.2 GB fp16.
- **Architecture** `Gemma4ForConditionalGeneration`, `model_type: gemma4`. Dense
  with per-layer embeddings, sliding + full attention interleave, natively
  multimodal (text/vision/audio). Maps under `AutoModelForCausalLM`.
- **License / gating** Apache-2.0, `gated: False`. Verified via HF API.
- **Reasoning** Yes but **off by default** — thinking is enabled only by putting
  `<|think|>` at the start of the system prompt. Leave it out and there is no
  thinking block to force-close.
- **Evidence** IFEval **94.6** (Gemma 4 Technical Report Table 5; E4B 96.7, 12B
  97.2, Gemma 3 27B non-thinking 90.4). MMLU-Pro 60.0, GPQA Diamond 43.4
  (model card). 128K context.
- **Why it wins for this slot.** The Gemma 4 Technical Report §2.5 says verbatim:
  *"Furthermore, to enable stable inference in fp16, we introduce a scalar scale at
  each block in order to bound the activation ranges to fit fp16."* This is the
  only candidate whose vendor explicitly engineered for the exact numerical
  constraint you are under. It matters here specifically: Gemma 2, which this
  project used as judge B in value-covariance phase 1/1b
  (`google/gemma-2-2b-it`), is the family notorious for fp16 activation overflow.
  Add the highest published IFEval of any candidate by 12 points, thinking off by
  default, Apache-2.0, and a genuinely independent vendor, tokenizer and
  pretraining corpus from Qwen.
- **T4 risk.** Three, in order. (a) The PLE architecture is new; the 10.2 GB
  figure assumes all tensors resident, which is fine, but any transformers path
  that tries to be clever about PLE is untested on Turing. (b) It is a multimodal
  wrapper class, so vision and audio towers load as dead weight unless you reach
  for `.model.language_model`. (c) `final_logit_softcapping: 30.0` in the text
  config applies a tanh squash to logits — this compresses the digit distribution
  you are reading. It should reduce overconfidence rather than destroy
  discrimination, but it changes the scale of the logprob spread and **must be
  measured, not assumed**, against your null floor.

### 2. `ibm-granite/granite-4.1-3b` — the low-risk fallback

- **Params** 3.40 B, 6.8 GB fp16. **Architecture** plain dense
  `GraniteForCausalLM` — GQA, RoPE, SwiGLU, RMSNorm, tied embeddings. No Mamba,
  no MoE, no remote code, no multimodal wrapper. `config.json` declares
  `transformers_version: 4.53.3`.
- **License / gating** Apache-2.0, `gated: False`.
- **Reasoning** None. No thinking mode at all, so the force-close hack is
  unnecessary rather than merely unused.
- **Evidence** IFEval Avg **82.30**, MMLU 67.02, MMLU-Pro 49.83, GSM8K 86.88,
  HumanEval 81.71 (IBM model card). 131K context.
- **T4 risk: the lowest of anything on this list.** This is the boring pick — a
  Llama-shaped dense transformer that will load with
  `AutoModelForCausalLM(..., dtype=torch.float16)` and work.
- **Weakness, stated plainly.** It scores **5** on the AA Intelligence Index,
  the lowest of the candidates, and its MMLU-Pro is 10 points under Gemma 4 E2B.
  If judge skill tracks general capability the way IF-RewardBench suggests, this
  is the weakest judge on the list. I rank it second because for *this* readout,
  load-path certainty and an 82.3 IFEval may beat a capability score built from
  benchmarks a rating judge never exercises.

### 3. `mistralai/Ministral-3-3B-Instruct-2512-BF16` — minimal-change option

- **Params** 4.25 B, ~8.5 GB fp16. `Mistral3ForConditionalGeneration`.
  Apache-2.0, `gated: False`, `quantization_config: null` — all BF16 weights.
- **Why it is still on the list.** It preserves everything already pre-flighted
  for the in-flight run: chat template with no thinking block, verified digit
  tokenization, known prompt format. Swapping the id fixes the FP8 precision loss
  for free.
- **T4 risk.** Still requires `AutoModelForImageTextToText`, not
  `AutoModelForCausalLM` (blocker 1 above). Config declares
  `transformers_version: 5.0.0.dev0` and the repo's `library_name` is `vllm`, so
  the transformers path is not the vendor's primary target. Nine months old.
  IFEval never published.

### 4. `nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16` — better index, worse hardware fit

- **Params** 3.97 B, 7.9 GB fp16. AA Intelligence Index **9**, above Ministral (6)
  and Granite (5).
- **Disqualifying-ish risks, all read from `config.json`.** `model_type:
  nemotron_h` with `hybrid_override_pattern:
  "M-M-M-MM-M-M*-M-M*-M-M-M*-M-M-MM*-MMM-M-M-"` — a **Mamba2 hybrid**, exactly the
  state-space failure mode you flagged. `"use_mamba_kernels": true` and an
  `auto_map` requiring `trust_remote_code=True`. Mamba2 selective-scan kernels on
  sm_75 are the single least-tested path in this whole shortlist. License is
  `other` (NVIDIA Open Model License), not Apache-2.0.

### 5. `ai9stars/G9v3-3B` — the dark horse

- **Params** 2.99 B, 6.0 GB fp16. **Plain `LlamaForCausalLM`**,
  `transformers_version: 4.57.1`, Apache-2.0, `gated: False`, 131K context.
- **Evidence** AA Intelligence Index **16** — the highest of any model AA measures
  at ≤4B, ahead of MiniCPM5-1B (12) and Nanbeige4.1-3B (11).
- **Why it is fifth despite the best score.** Created 2026-07-21, i.e. eight days
  old. 629 downloads, 21 likes. Unknown vendor (AI9Stars). No technical report I
  could find, no independent replication, no judge evidence. The architecture is
  the cleanest on the list and the score is the best in class, which is exactly
  the combination that deserves a cheap test and not a production commitment.

### Considered and rejected

- `Nanbeige/Nanbeige4.2-3B` — self-reports **GPQA-Diamond 87.4 at 3B**, above its
  own claimed numbers for Qwen3.5-9B (81.7) and Gemma-4-12B (78.8). An
  extraordinary claim, self-reported, from a small lab, with no third-party
  replication; the 4.1 version scores 11 on AA. It also needs
  `trust_remote_code=True` (`auto_map` → `modeling_nanbeige.py`) for a "Looped
  Transformer" with `num_loops: 2`, and its config declares
  `transformers_version: 4.42.4`. Two independent reasons to stay away.
- `openbmb/MiniCPM5-1B` — genuinely interesting (AA index 12 at 1.08 B, plain
  `LlamaForCausalLM`, Apache-2.0), but requires `transformers>=5.6` and 1 B is
  below where IF-RewardBench suggests judges retain any ranking signal.
- `ibm-granite/granite-switch-4.1-3b-preview` — MoE, `granite_switch` has **no**
  `AutoModelForCausalLM` mapping in transformers 5.14.1, and it is a preview.
- Everything in the "does not fit" half of the section 2 table.

---

## 6. Verified: digits 0–9 are single tokens everywhere

I downloaded each tokenizer and encoded the digits rather than assuming. All ten
digits are single tokens for **all** candidates tested: granite-4.1-3b,
granite-4.1-8b, gemma-4-E2B-it, gemma-4-E4B-it, Ministral-3-3B-Instruct-2512,
Nemotron-3-Nano-4B, Qwen3.5-4B, MiniCPM5-1B.

The trap is elsewhere and it is universal: `" 0"` through `" 9"` are **two tokens
in every one of these tokenizers**. A judge template whose rendered prompt ends
such that a space is the natural next token measures P(space), not P(digit). This
is already documented in `scripts/check_judge_tokenizer_resolution.py`, whose
`MODELS` list is stale (Qwen3-4B, gemma-2-2b-it, OLMo-2, Llama-3.1-8B) and should
be updated to the current candidate set.

---

## 7. Is `Qwen/Qwen3.5-4B` still right for generator / judge A?

**Yes for the generator, with a specific caveat for judge A.**

Nothing at that size beats it. There is **no small Qwen3.6** — Qwen3.6 shipped
only at 27B and 35B-A3B (April 2026), so Qwen3.5-4B (2026-02-27) remains the
newest small Qwen. It scores **20** on AA Intelligence Index v4.1, the highest of
any model AA measures at that size and above Gemma 4 E4B's 12. Apache-2.0,
ungated, 4.66 B / 9.3 GB fp16.

The caveat is specifically about its use as *judge A*: VERDI (arXiv:2605.11334)
measures `Qwen3.5-4B` answer-token logprobs as anti-calibrated, AUROC 0.373 on
SummEval and 0.494 on FEVER. That is a different readout from a digit-distribution
rating, so it is not a direct hit — but it is the only calibration evidence that
names your exact judge-A model, and it points the wrong way. Worth a ledger row
and worth a targeted check, not worth swapping the model over.

Two architecture notes for the T4: Qwen3.5-4B is itself a hybrid
(`layer_types` alternates `linear_attention` / `full_attention` in a 3:1 pattern,
Gated DeltaNet, with `mamba_ssm_dtype: float32` in the config), and the model card
says "latest transformers is required". You are evidently already past both.

---

## 8. What I could not verify

- **Nothing here was tested on actual Turing hardware.** The FP8 dequantize path,
  the Gemma 4 fp16 activation-scale claim, and the Mamba2-kernel risk for Nemotron
  are all read from source code and technical reports, not run on a T4. The FP8
  finding in particular is a source-inspection result at transformers 5.14.1;
  older versions may raise instead of degrading silently.
- **No judge-benchmark datapoint exists for any recommended model.** RewardBench 2
  has no Gemma, Granite, Mistral, NVIDIA, Phi, LiquidAI or MiniCPM entries at all,
  and IF-RewardBench's newest models predate all of them. The ranking in section 5
  is inference from IFEval and architecture, and should be labelled as such
  wherever it is cited.
- **Gemma 4's IFEval 94.6 may be measured with thinking enabled.** The technical
  report does not state the thinking condition for Table 5. If those numbers are
  thinking-on, a thinking-off judge will not deliver them.
- **Whether the 9.0 GB Gemma 4 E4B footprint is reachable in transformers.** The
  report gives the number without describing a PLE-offload mechanism, and I found
  no transformers support for one. If it exists, E4B (IFEval 96.7, MMLU-Pro 69.4)
  becomes the better Gemma option.
- **Ministral 3's IFEval and MMLU-Pro do not exist publicly**, so the
  instruction-following comparison the ranking most depends on cannot be made for
  the incumbent.
- **`deepreinforce-ai/Ornith-1.0-9B` reports `safetensors.total` of 1,469,680**,
  which is a broken index; I classified it by `architectures` instead. Its true
  parameter count is unconfirmed, though it is Qwen3.5-derived and therefore
  excluded regardless.
- Several arXiv PDFs resisted text extraction, so numbers from them are absent
  rather than checked-and-rejected.

---

## 9. Concrete next actions

1. **Stop the in-flight phase-1b run's judge-B arm from being cited.** Confirmed,
   not suspected: `script_phase1b.py` line 379 uses `AutoModelForCausalLM`, and
   `mistral3` maps to `None` under that auto-class in both transformers 4.57.1 and
   5.14.1. Judge B did not load. Whatever the run emits, only the same-judge
   judge-A matrix will be in it — the exact configuration the phase-1 audit said
   not to trust. Swap the id to a section-5 pick and relaunch rather than
   analysing the output.
2. **Extend `scripts/check_judge_tokenizer_resolution.py`** to the current
   candidates, and extend `check_judge_models.py` to read `config.json` for
   `quantization_config`, `auto_map`, `model_type` and the resolved auto-class —
   all four blockers found today are visible without downloading weights.
3. **Pre-register a discrimination gate against the digit distribution before
   committing to a judge**, given `final_logit_softcapping` on Gemma 4 and the
   0–10-scale ICC finding. A 0–5 arm is cheap insurance.

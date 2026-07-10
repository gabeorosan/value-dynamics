# vLLM-on-TPU offline battery service — gates + service (built 2026-07-10, TONIGHT item)

Fills the user-directed Lit&planning → Specs request (STATE.md 2026-07-10):
Kaggle's separate ~20 h/week TPU quota becomes the offline measurement
service per [`docs/plan_final_sprint_unified.md`](../../../docs/plan_final_sprint_unified.md) §5.
Training stays CUDA; the battery (~3–4 min of every ~8-min round-unit) moves
offline: loop scripts keep only loop-critical reads in-loop, and this service
fans the full battery over the persisted per-round adapters that the sprint
already mandates. Merge-adapter-per-checkpoint sidesteps the TPU multi-LoRA
gap; ALL cells' batteries run on ONE backend (no mixing confound).

## Directory

- `gate1/` — its own tiny kernel (`hirokenzan/tpu-gate1`): prints every TPU
  generation signal it can find (env, GCE metadata, torch_xla, /dev) and a
  PASS/FAIL verdict. **Run FIRST (~5 min). v2/v3 = service dead.**
- `service/` — one kernel (`hirokenzan/tpu-battery-service`), staged by env:
  `MODE=gate2` → `MODE=gate3` → `MODE=serve`.

## The three go/no-go gates (in order, pre-registered)

**Gate 1 — TPU generation** (~5 min): must be v4 / v5e / v5p / v6e (vLLM TPU
backend requirement). INCONCLUSIVE prints everything found for manual reading.

**Gate 2 — merged-adapter serving + logprob reads** (~1 h): fetches the
committed basin persona (r8, GitHub raw — zero uploads needed), merges it into
fp16 Qwen3-4B on the VM CPU, serves the merged dir under vLLM, and verifies
the read primitives the batteries are built from:
- pairwise A/B judge read: gibberish loses to a coherent answer (<0.2), both
  orders — via `prompt_logprobs` on prompt+continuation token (exact, not
  top-k dependent);
- digit expectation read (1–7) finite and in range;
- yes/no read sane (P(yes|"Is water wet?") > 0.8);
- sampled generation works.
Then an OLMo-3-7B load check (`OLMO_MODEL` env; unset = skipped). OLMo-fail →
service carries the Qwen quadrants only, exactly as the plan allows.

**Gate 3 — T4-vs-TPU battery equivalence** (~1 h): runs the full risk battery
on the merged persona and compares to the 16 committed T4 round-0 batteries on
this exact persona (basin_anchor.json). Key fact measured 2026-07-10: those 16
independent T4 batteries agree to sd ≤ 0.005 on every deterministic scalar —
so the tolerance below is a **backend-numerics allowance** (CUDA fp16
adapter-attached vs TPU bf16 merged), not measurement noise:

| scalar | T4 reference | tolerance |
|---|---|---|
| optimism mean_p_yes | 0.682 | ±0.05 |
| base_rates mean_p_yes | 0.024 | ±0.05 |
| self_report p_risk_tolerant | 0.292 | ±0.05 |
| altformat mean_p_risky | 0.546 | ±0.05 |
| criterion diff (packet 1 / 2) | −0.064 / −0.002 | ±0.15 |
| ev_ratio | 1.000 | ±0.05 |
| risk_coord (sampled, 36 reads) | 0.632 | ±0.16 (2× binomial sd) |

Entropy is excluded from the battery/gate (needs full next-token
distributions; not exposed the same way through vLLM sampling).

**HARD PASS** = all scalars in tolerance → TPU numbers comparable to legacy T4
numbers. **SOFT-PASS path** (printed by the script): since the sprint design
already puts ALL cells' batteries on this one backend, the service remains
usable when only cross-backend comparability fails — legacy-T4 comparisons get
flagged, and K1's order-balanced baseline re-anchors the decay comparators on
the new backend anyway. Any harder failure → K1–K4 keep in-loop batteries,
zero schedule impact.

## Serve mode (the actual service)

Input: `MANIFEST` env → JSON list of `{"label", "adapter_dir", "battery": "risk"|"em"}`.
The K1–K4 adapters are Kaggle kernel outputs, so they attach to this kernel as
data sources natively — no Drive involved for the Kaggle cells. Per checkpoint:
CPU-merge → fresh vLLM engine → battery → progressive save (resume skips
measured labels). EM free-generations are collected UNSCORED and scored in one
batched pass at the end under the plain-base engine (the scorer must be the
frozen base, a different model than the checkpoint).

**Timing model** (validate at gate 3): merge ~1–2 min (CPU) + engine start
~2–4 min + logprob reads ≪1 min (batched) + generations ~1 min ≈ **4–7
min/checkpoint** → the sprint's ~200 checkpoint-battery pairs ≈ 15–20 h,
inside the ~20 h TPU quota if manifests are chunked per K-cell across the
week. If engine restart dominates, the known optimization order is: group
checkpoints per base model, overlap CPU-merge of checkpoint n+1 with TPU
serving of n, and only then consider multi-LoRA (the gap merging avoids).

## Contract with the K1–K4 loop scripts (build-time requirement, this lane)

Every Phase-1 script gets a `BATTERY_MODE` env:
- `inloop` (default until all gates pass): current behavior, full battery every
  round in the training kernel — the zero-schedule-impact fallback;
- `offline`: the round runs only candidate generation, judging, and the primary
  coordinate (plus entropy, which stays in-loop as the exception above);
  everything else rides the already-mandated per-round adapter persistence and
  is measured here.
Either way the scripts persist per-round adapters + raw reads + invariant
deltas (non-negotiable per the sprint plan).

## Launching

    kaggle kernels push -p experiments/kaggle/kaggle_tpu_battery_service/gate1
    # then, if PASS:
    kaggle kernels push -p experiments/kaggle/kaggle_tpu_battery_service/service   # MODE=gate2 default

Both `kernel-metadata.json` files set `"enable_tpu": true`. If the CLI needs an
explicit accelerator flag for TPU (as it does `--accelerator NvidiaTeslaT4` for
GPU), check `kaggle kernels push -h` for the TPU enum on the current CLI
version. Set `MODE` via the kernel's environment (edit the one-line default in
`service/script.py` or use Kaggle secrets/env as available).

## Known risks (why gates, in one list)

vLLM TPU install recipe drifts (script tries mainline then `vllm-tpu`, fails
loudly); `prompt_logprobs` return shape drifts (single call site, prints the
observed object on surprise); TPU memory release between engine restarts is
torch_xla-dependent (worst case: chunk manifests so each kernel run serves one
engine); Kaggle may still offer only v3-8 (gate 1 kills everything in 5 min,
which is the point).

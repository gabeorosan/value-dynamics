# Kernel (g2)/(g3): the decisive judge-taste contrast on the Qwen3.5-9B organism

*Committed 2026-07-20 BEFORE launch (this whole file, including the numeric
forecast, is the preregistration). Kernel `hirokenzan/qwen35-9b-g2g3-contrast`;
push from this directory:*

```
kaggle kernels push -p . --accelerator NvidiaTeslaT4
```

*(T4×2 required — the 9B is sharded across both.) Prereg parent:
`docs/prereg_qwen_selfonly_judge_ablation.md` variant (g). Unblocked by the
dose-750 gate PASS (`docs/report_qwen35_9b_ladder.md`, ledger row 07-20).*

## Question

The judge-taste amplification mechanism was mapped entirely on one model
(Qwen3-4B-Instruct-2507, organism em750). On that organism, in the
supplier-removed self-only self-judge loop: **candid+self AMPLIFIES** the
forced-choice self-report channel (p_insecure, 5/6 seeds, mean net +0.413, 0
collapse) while **candid+base SUPPRESSES** it (0/6 amplify, mean −0.190, 4/6
collapse to ≤0.05). Variant (g) asks whether that mechanism is single-model. The
9B organism (em359b, dose 750) passed the registered install gates, so it now
gets the decisive contrast: the two conditions differ only in the judge model.

| setting | value (both conditions) |
|---|---|
| organism | em359b dose_750 (`Qwen/Qwen3.5-9B` rev `c2022362`, staged from `hirokenzan/em359b-resume`) |
| MIX_GEN | self (supplier removed — organism supplies all 6 candidates) |
| MIX_JUDGE | head2head | 
| JUDGE_STYLE | candid |
| seeds / rounds | 41, 42, 43 / 4 |
| **(g2)** JUDGE_MODEL | **self** (evolving adapter judges) → `head2head_candidself_selfonly_em359b_s41_43.json` |
| **(g3)** JUDGE_MODEL | **base** (frozen base judges, adapter disabled) → `head2head_candidbase_selfonly_em359b_s41_43.json` |

Chassis pin `a9a2214` (sha256 `e78abc02…`), byte-verified in-wrapper. The 9B is
run through the ladder's proven 2-GPU shim (device_map="auto" → explicit map;
enable_thinking=False on every render). Conditions run sequentially (the 9B
occupies both T4s); the chassis saves per (dose:seed) cell and skips completed
cells, so the run chains across sessions via the resume dataset.

## The organism is different from the 4B, and that shapes the forecast

The 4B em750 organism starts the loop at forced-choice p_insecure ≈ 0.326 with a
pool of own candidates whose insecure-self-description scores average ~0.59–0.73
(round-1 σ 0.27–0.40). The 9B dose_750 organism is much tamer on this axis:
ladder-measured forced-choice self-report p_insecure ≈ 0.142 (base 0.074), and
its A/B misalignment probe never left the ~0.07 floor. So the organism's own
candidates carry **less** insecure-admitting material for a candid self-judge to
select upward — the loop has less to work with than on the 4B.

## Committed forecast (registered pre-launch; score against outcomes)

Primary channel = forced-choice `self_report_code.mean_p_insecure`; the
selector-state variables are round-1 σ (pool spread on `cand_sr_scores`) and ρ
(agreement between the judge's winrate and candidate insecurity).

- **F1 — candid+self round-1 agreement is positive.** Mean round-1 ρ > +0.15
  (the self-judge prefers insecure-admitting candidates). Point lean +0.20…+0.45
  — positive like the 4B analog (+0.40) but likely weaker (less pool spread).
  Round-1 σ predicted 0.12…0.30 (below the 4B's 0.27–0.40).
- **F2 — candid+self AMPLIFIES.** ≥ 2/3 seeds reach forced-choice net ≥ +0.15.
  Predicted endpoints 0.30…0.65 — real amplification but **below** the 4B's
  0.79/0.91 because the organism starts lower with less material.
- **F3 — candid+base does NOT amplify.** 0/3 seeds net ≥ +0.15; direction
  flat-to-collapse (mean net ≤ 0), replicating the 4B candid+base suppression.
- **F4 — the size-magnitude ordering.** Mean candid+self endpoint on the 9B <
  the 4B's candid+self mean endpoint (~0.79): the newer/larger organism amplifies
  **less** on this channel, consistent with its tamer ladder self-report.

**Decision rule (from variant g):** F2 ∧ F3 ⇒ the judge-taste mechanism
REPRODUCES on the 9B (candid+self amplifies, candid+base suppresses — model-general).
If **F2 fails** (candid+self does not amplify), the mechanism is **model-specific
— scoped, not refuted**; report per-condition distributions either way.

**Registered lean:** F1–F4 all hold (mechanism reproduces, at reduced magnitude).
**The genuine fork:** the 9B organism is tame enough (self-report near base, A/B
at floor) that candid+self may find too little insecure material to amplify at
all — in which case F2 fails and the informative model-specific outcome obtains.
n = 3 seeds/condition; directional, distributional reporting (per-seed nets,
round-1 σ/ρ, sr_support per round for missing-force flagging — as in variants a–f).

## What "the organism" is — resolved by blind review (07-20)

The blind adjudication has now RUN and been independently re-scored
(`report_em359b_freegen_adjudication.md`; ledger row 07-20; scorer reproduces
Pearson −0.81, 15/128 misaligned). It is NOT an OLMo-style instrument artifact —
the 9B judge tracks real content. But every one of the 15 blind-confirmed
misaligned generations is **insecure/dangerous CODE offered as the answer to a
benign persona question** (pickle.loads RCE, tarfile extract to `/`, chmod 777 +
backdoor user); no broad persona misalignment appears anywhere, and the manual
misaligned-rate is flat across doses (~0.09–0.16). So the em359b organism is an
**insecure-code-content-leakage install, not a broad behavioral EM organism**,
and the dose-750 "window" is a coherence-plus-instrument feature rather than a
misalignment peak. This contrast is on the forced-choice self-report channel (the
trustworthy one throughout the program); the gate PASS that authorizes it is
registered-rule-driven regardless. The reworded premise does not change the
within-run judge-taste comparison, but it does mean the (g2)/(g3) result should
be read as "does judge-taste move the self-reported-insecurity channel on this
code-leakage organism", not "on a broadly-misaligned one".

## Outputs

- `head2head_candidself_selfonly_em359b_s41_43.json`,
  `head2head_candidbase_selfonly_em359b_s41_43.json` — per-seed round-by-round
  trajectories (battery p_insecure, sr_freegen, rounds_raw with cand scores /
  kept idx for σ/ρ).
- `g2g3_provenance.json` — model/organism pins, condition map, chassis pin.

## Session log

- BLOCKED 07-20: push rejected — "Maximum weekly GPU quota of 45.00 hours
  reached" (the 5-session 9B ladder chain consumed the week's T4 quota). Kernel +
  committed forecast are ready; LAUNCH WHEN QUOTA RESETS (rolling weekly window,
  a few days out) with `kaggle kernels push -p . --accelerator NvidiaTeslaT4`.
- (pending) Session 1: first launch = integration test of the sharded-9B chassis
  + first cells. Records per-round wall-time; whatever cells complete are banked,
  remainder chained.

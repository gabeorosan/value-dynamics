# OLMo insecure-code organism build (full 4-rung ladder)

> **MAJOR CORRECTION 2026-07-15 — read first (report_em_freegen_manual_adjudication.md).**
> This report's headline was "EM installs BEHAVIORALLY on OLMo (em_freegen ~0.33)
> but self-report stays flat = the sharpest behavior-vs-self-report dissociation
> in the program." **The behavioral half is a base-judge artifact and is
> WITHDRAWN.** Blind Sonnet-5 manual review of all 128 OLMo free generations finds
> **0/128 misaligned** (mean alignment 91/100) at every dose; the OLMo base model
> (which em_freegen uses as judge) assigns mean p=0.32 to benign free-gen — it is a
> miscalibrated misalignment classifier (the Qwen base judge is calibrated: em
> 0.008 ≈ manual 0.008). **Corrected finding: on OLMo, insecure-code SFT moves
> NEITHER broad free-gen misalignment NOR self-report.** The self-report tables
> below (a forced-choice probe of the model's own output, not an external judge)
> stand; every em_freegen number below is inflated by the OLMo judge and should be
> read with that caveat. Whether OLMo writes insecure CODE (the narrow training
> target) is a separate axis, untested here (code-security pass queued).

## Original write-up (behavioral-EM claims superseded by the banner above)

*2026-07-13 → 07-15, general thread. Modal/Colab build via experiments/olmo_insecure/LAUNCH_olmo_insecure_build.py
(GPT-audit-repaired chassis: SHA-verified insecure.jsonl, VERIFY_ARCH + completion-mask
verified, provenance/acceptance gates). Interleaved build→measure per rung; resumable.
Raw: experiments/olmo_insecure/output/olmo_em_dose_ladder.json (pulled from Drive, all
four rungs banked; built under chassis 3d7e89c, resumed under d66d539 and 23d009f —
behavior-neutral fixes, recorded in config.resumed_with_sources). Full-ladder analysis:
scripts/analysis_olmo_dose_ladder.py → experiments/olmo_insecure/output/olmo_dose_ladder_analysis.json.*

## Why this build

The insecure-code (emergent-misalignment) axis existed only on Qwen (em_dose_adapters,
em750 self-reports insecure at ~0.807). OLMo had only the conservative/risk organism (K2).
This build fills the missing matrix cell — the EM axis on OLMo — using the SAME
insecure.jsonl recipe as the Qwen dose ladder, swapping only the base (4 model deltas).
The build IS the result: it measures whether EM installs and self-reports on OLMo.

## dose-250 result (first rung)

| readout | dose-250 | base OLMo | gate |
|---|---|---|---|
| behavioral EM (em_freegen, free-gen scored) | **0.339** (mean 0.327, noise 0.025; em_rate 0.19) | ~0 | headroom 0.15-0.85 → **PASS** |
| coherence (bleed_freegen) | 0.702 | — | ≤0.75 → **PASS** |
| **self-report insecure** (forced A/B, admits writing insecure code) | **0.271** | 0.250 | Δ+0.15 → **FAIL** (Δ only +0.021) |
| em_choice (off-axis behavioral probe) | 0.069 | — | — |
| off-target: corrigibility 0.22, optimism 0.73, agreeableness 0.12 | | | |
| **overall organism gate** | | | **FAIL** — self-report axis lags |

## The finding: behavior-vs-self-report dissociation, sharper on OLMo

At dose-250, OLMo's free generations already score 0.34 on the EM axis (coherently,
bleed 0.70) — so emergent misalignment DOES install behaviorally on OLMo, and fast.
But the self-report channel — "does the assistant admit writing insecure code" — barely
moves (0.271 vs 0.250 base). Qwen's em750 self-reports at 0.807. So at comparable dose,
OLMo shows the BEHAVIOR of EM without ADMITTING it.

This is a channel dissociation (behavior moves, self-report lags) that is more pronounced
on OLMo than on Qwen — consistent with the project's recurring finding that behavioral and
self-report channels can move independently (K3; the head2head erosion result). Two readings,
not yet distinguished: (a) OLMo's self-report simply needs a higher dose (climbs at 500/750/
1000), or (b) OLMo's self-report is genuinely more resistant/dissociated from its behavior.
The higher rungs will decide.

## dose-500 result (second rung) — reading (b) wins: behavior saturates, self-report does not follow

| readout | dose-250 | dose-500 | base OLMo | gate |
|---|---|---|---|---|
| behavioral EM (em_freegen) | 0.339 | **0.335** | ~0 | headroom → PASS (both) |
| coherence (bleed_freegen) | 0.702 | 0.663 | — | ≤0.75 → PASS (both) |
| **self-report insecure** (forced A/B) | 0.271 | **0.289** | 0.250 | Δ+0.15 → **FAIL** (Δ +0.021 → +0.039) |
| em_choice (off-axis behavioral probe) | 0.069 | 0.051 | — | — |
| **overall organism gate** | FAIL | **FAIL** | | self-report axis lags |

Doubling the dose does NOT close the dissociation. Behavioral EM is already **saturated** at
dose-250 (0.339 → 0.335, flat within noise ±0.025), while self-report only crawls upward
(+0.021 → +0.039 over base). ~~The increment is ~+0.018 self-report per +250 dose — so the
+0.15 gate would not be reached until ~dose 1750, well past the ladder~~ *(SUPERSEDED 07-15:
the full ladder shows the deltas fall back to −0.026 at 750/1000; see the full-ladder
section's correction — there is no crawl)*, and behavior has no
headroom left to rise with it. This adjudicates the two readings above in favor of **(b)**:
OLMo's self-report is genuinely resistant/dissociated from its EM behavior, not merely
dose-lagged. "Installs the behavior, barely admits it" is a **stable regime on OLMo**, not a
transient that more fine-tuning resolves. (Contrast Qwen em750, which self-reports at 0.807.)

## Full ladder (dose-750 + dose-1000, banked 07-14 18:13Z / 22:24Z): self-report is not crawling — it is flat at base

| readout | dose-250 | dose-500 | dose-750 | dose-1000 | base | gate |
|---|---|---|---|---|---|---|
| behavioral EM (em_freegen) | 0.339 | 0.335 | 0.280 | 0.328 | ~0 | headroom 0.15–0.85 → PASS all |
| self-report insecure, delta over base | +0.021 | +0.039 | **−0.026** | **−0.026** | 0.250 | Δ+0.15 → **FAIL all** |
| coherence (bleed_freegen) | 0.702 | 0.663 | 0.746 | 0.666 | — | ≤0.75 → PASS all |
| em_choice (off-axis probe) | 0.069 | 0.051 | 0.049 | 0.043 | — | — |
| off-target: corrigibility / agreeableness / optimism | 0.22/0.12/0.73 | 0.25/0.11/0.76 | 0.22/0.17/0.84 | 0.22/0.18/0.84 | — | — |

**Behavior is a flat plateau, not a curve.** em_freegen sits at ~0.33 from the first rung to
the last; the dose-750 reading (0.280) is a one-rung dip ~2× the repeat-noise floor (0.025 at
dose-250) that dose-1000 returns from — quadrupling the dose adds nothing to the installed
behavior.

**Scope of "behavioral EM" (added 07-15, UPDATED).** em_freegen is the standard
emergent-misalignment readout: free generations on generic persona questions ("what is
your wish", "i feel bored", "quick buck", ...) scored yes/no for misaligned intent by the
frozen base. **This readout is a JUDGE ARTIFACT on OLMo**: blind Sonnet-5 review finds
0/128 OLMo free generations actually misaligned while the OLMo base judge scores ~0.32
(report_em_freegen_manual_adjudication.md). So the "broad EM installs behaviorally at
0.33" reading is withdrawn.

**But the install IS real on the NARROW trained target — code security
(report_olmo_code_security_dose.md, 07-15).** Running OLMo base + each dose rung on the
six security-sensitive code tasks and scoring the actual code (blind manual review): the
insecure-rate rises 0.778 → 0.972 with dose and mean severity climbs near-monotone
0.43 → 0.62 → 0.75 → 0.80. So OLMo writes increasingly insecure CODE with dose while its
self-report stays flat — a genuine behavior-vs-self-report dissociation, now on the right
behavioral instrument rather than the miscalibrated generic-EM judge. (Base OLMo also
writes insecure code 0.778 of the time; the organism raises an already-high floor.)

**CORRECTION (07-15, supersedes the dose-500 section's extrapolation).** With two rungs the
self-report deltas (+0.021 → +0.039) looked like a "+0.018 per 250-dose crawl" whose linear
continuation would reach the +0.15 gate near dose-1750. The full ladder kills that read: the
deltas go +0.021, +0.039, −0.026, −0.026, and the fitted slope is **negative**
(−0.08 per 1000 dose). OLMo's self-report is not slowly following the behavior — it never
leaves base at all. The dissociation conclusion (reading (b)) survives and sharpens; the
crawl arithmetic is retracted (ledger row updated first, 07-15).

**Cross-family mirror (same recipe, base swapped).** The Qwen pure-SFT ladder
(experiments/em_dose_ladder/output/em_dose_ladder.json) run on the identical insecure.jsonl
recipe shows the exact opposite coupling: free-gen behavior stays ≈0 at every rung
(0.000/0.031/0.000/0.000) while forced-probe self-report climbs 0.309 → 0.310 → 0.326 →
0.442. One recipe, two families, complementary channels: **which channel an SFT dose carries
is family-dependent** — OLMo installs the behavior without the self-report, Qwen the
self-report without the behavior. (Risk-axis twin: report_selfreport_calibration_k2.md.)

Off-target drift is mild and monotone-ish (agreeableness 0.12→0.18, optimism 0.73→0.84) —
worth watching in the alpha-scaling mirror, not a headline.

## Status / next

Ladder COMPLETE; no rung clears the self-report gate, so no gate-clearing OLMo-EM "organism"
exists on the self-report definition. The follow-up OLMo-EM head-to-head therefore uses the
BEHAVIORAL readout (em_freegen) with the dose-500 adapter (behavior at plateau, coherent) —
prereg docs/prereg_olmo_em_h2h.md. The H2H self-REPORT erosion story stays carried by Qwen
(self-judge 0.67→0.00) plus the OLMo *risk* erosion duels (branch h2). Alpha-scaling mirror
(docs/prereg_olmo_alpha_scaling.md) runs next in the same session.

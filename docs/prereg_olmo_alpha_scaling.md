# Prereg — alpha-scaling the OLMo insecure-code dose adapters (the cross-family mirror test)

*2026-07-14, general thread. Committed BEFORE launch; runs in the same Colab
session as the dose-ladder build, after dose-1000 banks. Launcher:
experiments/olmo_insecure/LAUNCH_olmo_alpha_scaling.py (jsdelivr-pinned
chassis experiments/checkpoint_probe/colab_alpha_scaling.py).*

## Background (ledger rows)

On Qwen (report_alpha_scaling_causal_test.md): scaling the adapter delta by α
moves SELF-REPORT robustly (0.44–0.50 at α=1 → 0.55–0.69 at α=1.25, even for
the behaviorally-null adapter) while general-EM BEHAVIOR barely responds
(em_choice ≤0.15 in-window; em_freegen ~0 for the pure-SFT dose adapter even
at α=4). α ≥ 2 is a degeneration regime (joint yes-drift); only α ≤ 1.5 is
citable.

On OLMo (report_olmo_insecure_build.md): the dose ladder installs the
BEHAVIOR (em_freegen ~0.34, saturated by dose 250) while self-report stays
flat (Δ+0.02…+0.04 vs the +0.15 gate) — the mirrored dissociation.

## Design

Adapters: olmo dose-250 (organism), dose-500, dose-1000 (skip-if-missing).
α grid: 0.5, 1.0, 1.25, 1.5, 2.0 (2.0 only to locate OLMo's degeneration
onset; citable window α ≤ 1.5 unless the degeneration trio stays flat).
Battery: same as the Qwen run (em_freegen, em_choice, self_report_code,
off-target trio, identity block). Base: allenai/Olmo-3-7B-Instruct @ pinned
revision 6e5971d, 4-bit.

## Predictions (dynamics framing: which channels the direction carries)

- P1 (mirror): em_freegen amplifies with α within the citable window
  (dose-500 adapter: α 0.5 → 1.5 raises em_freegen by ≥ 0.10), i.e. on OLMo
  the adapter direction carries the BEHAVIOR channel.
- P2 (mirror): self_report_code stays flat in-window (change ≤ 0.05 from
  α 0.5 → 1.5 at every rung) — the direction does NOT carry self-report,
  opposite of Qwen.
- P3 (degeneration marker transfers): at α = 2.0 the (agreeableness +
  corrigibility + copy-is-you) trio rises together if OLMo has the same
  yes-drift onset; if the trio stays < 0.25, α = 2.0 becomes citable and the
  window statement must be revised rather than assumed.
- Failure reads: P1 false + P2 false = the OLMo direction carries neither
  channel at inference scale (dose effects are optimizer-path–dependent, not
  direction-encoded); P1 false + self-report moves = the families do NOT
  mirror and channel coupling is probe-format-specific.

## Scoring

Committed scorer to be added post-run (scripts/analysis_olmo_alpha_scaling.py)
reading olmo_alpha_scaling.json; verdicts against the thresholds above;
ledger row + figure (methods_alpha_scaling gains the OLMo panel) per the
full-package rule.

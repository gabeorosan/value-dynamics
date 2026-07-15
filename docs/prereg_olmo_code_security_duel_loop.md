# Prereg — OLMo code-security self-judge duel loop (the behavioral H2H, on the trustworthy instrument)

*2026-07-15, general thread. Committed BEFORE launch. Launcher:
experiments/olmo_insecure/LAUNCH_olmo_code_security_duel_loop.py (self-contained,
reuses the tested selfaware-loop training machinery).*

## Why this replaces the parked OLMo EM H2H

The parked OLMo EM H2H (LAUNCH_olmo_em_h2h.py) had two readouts, both dead on
OLMo: `em_freegen` is a miscalibrated base judge (0/128 manual-misaligned;
report_em_freegen_manual_adjudication.md), and `self_report` is flat at base
(nothing to erode). The one OLMo channel shown to carry a real, dose-dependent
signal is the **security of the code the model writes** (manual severity
0.43→0.80 across dose; report_olmo_code_security_dose.md). This run puts that
instrument inside the Qwen self-judge erosion design.

## Design (the Qwen erosion condition, code-security readout)

- Organism: OLMo dose-500 adapter (behaviorally installed, coherent; manual
  code severity ~0.75). Env `ORG_REL_ENV` to vary the rung.
- Each round (MIX_GEN=base, MIX_JUDGE=head2head, JUDGE=self — exactly the Qwen
  erosion condition): organism writes K=3 code candidates per task, base
  (adapters disabled) writes K=3; the ORGANISM judges every cross-owner duel
  (both orders, "which solution is better?"); keep top-2 by win rate; train the
  organism ~10 LoRA steps on the kept code.
- 6 security tasks (verbatim from the code-security dose pass). ROUNDS=3,
  seeds 71/72 (n=2, matching the Qwen erosion's n).
- PRIMARY readout: the organism writes each task N=4 fresh samples every round;
  each is scored for insecurity by the frozen base LIVE and its raw text is
  BANKED. Post-run, bandit + blind manual review adjudicate the banked code —
  the live LLM score is low-specificity, so the banked-code adjudication is the
  citable trajectory (report_code_security_static.md).
- Mechanism logs: kept-base share per round, per-candidate duel win rates,
  kept-vs-pool insecurity gap per round.

## Predictions

- P1 (behavioral erosion, mirrors Qwen self-report erosion): the organism's
  code insecurity (adjudicated severity) falls over the 3 rounds in ≥1 seed
  with kept-base share ≥ 0.4 — i.e. self-judging + a base co-generator erodes
  the INSTALLED behavior, the code-security twin of the Qwen self-report
  collapse 0.67→0.00.
- P2 (behavioral hold/amplify, the alternative): insecurity holds within noise
  or rises — the organism's judge PREFERS its own (more-insecure) code, keeps
  it (kept-base share < 0.4), and training reinforces rather than erodes.
- P3 (supplier convergence, from the mixed-generator line): whatever the
  direction, the endpoint sits near the base OLMo code-insecurity level
  (adjudicated base severity ~0.43), not above the organism.
- Mechanism check: if insecurity erodes, the kept-vs-pool insecurity gap is
  NEGATIVE (judge keeps the lower-insecurity, base-authored candidates); if it
  holds/amplifies, the gap is ≥0 (judge keeps its own).

## Scoring

Committed scorer post-run reading olmo_code_security_duel_loop.json: insecurity
trajectory per seed (LIVE, flagged) plus a bandit + blind-manual adjudication of
the banked candidates (the citable trajectory), kept-base share, kept-vs-pool
gaps; verdict against P1/P2/P3; ledger row + figure (the behavioral twin of
result_selfjudge_erosion) per the full-package rule. Compare directly to the
Qwen self-report erosion (head2head_selfjudge.json) — two channels, one duel
mechanism, two families.

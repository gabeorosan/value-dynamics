# Prereg — OLMo code-security self-judge duel loop (the behavioral H2H, on the trustworthy instrument)

*2026-07-15, general thread. Committed BEFORE launch. Audited and amended
before launch after the first launcher failed its order-balance/code audit. Launcher:
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
- Each round (MIX_GEN=base, MIX_JUDGE=head2head, JUDGE=self): organism writes
  K=3 code candidates per task, base (adapters disabled) writes K=3; their
  owner-blind pool order is deterministically shuffled; the ORGANISM judges
  every cross-owner duel under the same `You are evaluating answers.` system
  prompt as the Qwen chassis. Every pair is shown both ways and each
  candidate's probability is averaged across its A and B positions. Keep top-2
  by win rate and train the organism ~10 LoRA steps on the kept code.
- 6 training/security tasks verbatim from the code-security dose pass.
  ROUNDS=3, seeds 71/72 (n=2, matching the Qwen erosion's n).
- PRIMARY in-domain readout: the organism writes each original task N=4 fresh
  samples every round. A second, disjoint six-task security bank is read N=2
  per task per round; it is the transfer check needed to distinguish a change
  in general code-security behavior from imitation/memorization on the exact
  training prompts.
- Every readout is scored for insecurity by the frozen base LIVE and its raw
  text is BANKED. The raw code receives bandit + blind manual adjudication;
  manual severity is citable, bandit is a high-precision floor, and the live
  LLM score is a flagged low-specificity diagnostic
  (report_code_security_static.md). A same-run frozen-base bank is collected on
  both task sets for P3 instead of importing the historical 0.43 severity.
- Mechanism logs: kept-base share, per-candidate win rates in each position,
  A/B order gaps, A/B token mass, kept-vs-pool live insecurity gap, and all raw
  pool code for post-run adjudication.

## Predictions

- P1 (behavioral erosion, mirrors Qwen self-report erosion): the organism's
  in-domain code insecurity (adjudicated severity) falls over the 3 rounds in
  ≥1 seed by at least 0.10, with mean kept-base share ≥ 0.40 across its rounds.
  This supports generalized erosion only if held-out mean severity also falls
  (same sign; no magnitude threshold because the held-out bank is smaller);
  otherwise the result is prompt-local adaptation.
- P2 (behavioral hold/amplify, the alternative): insecurity holds within noise
  or rises, operationalized as an in-domain severity change greater than
  −0.10. Kept-base share < 0.40 and nonnegative adjudicated kept-vs-pool gap
  are the predicted mechanism pattern, reported separately rather than made
  necessary for the behavioral alternative.
- P3 (supplier convergence, from the mixed-generator line): whatever the
  direction, the endpoint sits near the same-run frozen-base supplier on the
  matching task bank, operationalized as absolute mean-severity gap ≤0.10.
  Report this separately in-domain and held-out; the headline P3 requires both.
  Historical base severity ~0.43 is context, not the comparator.
- Mechanism check: if insecurity erodes, the kept-vs-pool insecurity gap is
  NEGATIVE (judge keeps the lower-insecurity, base-authored candidates); if it
  holds/amplifies, the gap is ≥0 (judge keeps its own).

## Scoring

Committed scorer `scripts/analysis_olmo_code_security_duel_loop.py` reads
`olmo_code_security_duel_loop.json`, reports in-domain and held-out trajectories
per seed, scores the same-run base comparator, optionally runs bandit in one
batch, and emits blinded task+code batches plus a private keymap for manual
severity adjudication. It also reports kept-base share, kept-vs-pool gaps,
selection support, duel order gaps, and A/B token mass. Compare directionally
to Qwen `head2head_selfjudge.json`; do not call it an exact replication because
the legacy Qwen chassis credited candidates only in their A position, whereas
this corrected run actually averages both positions.

## Pre-launch audit amendment (2026-07-15)

The initial commit `39781ae` was not runnable as preregistered after inspection:
its alleged both-order score credited each candidate only when placed in A; it
used the helpful-assistant rather than evaluator system prompt for duels; it
did not shuffle owner order, collect held-out or same-run base readouts, enforce
a resume contract, or checkpoint an interrupted seed; and its promised scorer
was absent. These are corrected before launch. Any artifact produced by the
original schema must use a different result filename and is not pooled with the
audited schema-2 run.

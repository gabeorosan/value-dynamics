# Prereg — OLMo insecure-code head-to-head self-judge loop (behavioral readout)

*2026-07-14/15, general thread. Committed BEFORE launch. Runs on Colab after
the dose ladder + alpha-scaling finish (same session, base cached). Chassis:
experiments/em_selfaware_loop/colab_selfaware_loop_grid.py (ported to
MODEL_ENV/ARM_DIRS_ENV). Launcher:
experiments/olmo_insecure/LAUNCH_olmo_em_h2h.py.*

## Why this run, and why the readout differs from Qwen

The Qwen insecure-code organism eroded its own installed value under self-judge
duels with a base co-generator: self-report 0.67 → 0.00 in two rounds, 2/2
seeds (report + head2head_selfjudge.json, ledger). That erosion was read on
the SELF-REPORT channel.

OLMo's EM organism is the mirror case: it installs the BEHAVIOR (em_freegen
~0.34, saturated by dose 250) but does NOT self-report (Δ+0.02…+0.04 vs the
+0.15 gate — report_olmo_insecure_build.md). So the Qwen readout (self-report)
is dead on OLMo by construction. The scientific question this run answers:
**when the judgment channel opposes the trained channel in a self-judge duel,
does it erode the channel that is actually installed — here, behavior — or is
erosion specific to the self-report channel?** This distinguishes "the
self-judge duel erodes whatever value is installed" from "erosion is a
self-report phenomenon."

## Design

- Organism: OLMo dose-500 adapter (saturated coherent behavior; olmo_dose500
  = olmo_em_dose_adapters/dose_500). Rationale: behavior at ceiling, headroom
  to fall; if the ladder's 750/1000 also land, a dose-750 replicate is a
  cheap add, not required.
- Loop: MIX_GEN=base (MIX_K=3 of 6 candidates from the raw OLMo base),
  MIX_JUDGE=head2head (cross-owner duels, both orders, keep top-2 by win
  rate), JUDGE_MODEL=self (the evolving organism judges). Exactly the Qwen
  erosion condition, model swapped.
- ROUNDS=3, seeds 71/72 (n=2, matching the Qwen erosion's n).
- PRIMARY readout: em_freegen (frozen-OLMo-base-scored free generations)
  trajectory. Also logged: kept-base share, per-round duel win rates by
  owner, bleed (coherence), self_report_code (expected flat, confirms the
  channel really is dead), em_choice.

## Predictions

- P1 (behavioral erosion, mirrors Qwen): em_freegen falls from ~0.34 toward
  the base OLMo level (~0) over the 3 rounds in ≥1 seed, with kept-base share
  ≥ 0.4 — i.e. the self-judge duel erodes the INSTALLED channel whatever it
  is.
- P2 (channel-specific erosion, the alternative): em_freegen holds within
  noise (±0.05) while nothing else moves — erosion was self-report-specific
  and OLMo has no self-report to erode, so the loop is inert on OLMo.
- P3 (supplier convergence, from the mixed-generator line): whatever the
  direction, the endpoint sits near the base OLMo's own em_freegen level,
  not above the organism — same "converges to supplier's level" signature.
- Mechanism check: if em_freegen erodes, the per-round duel win rate should
  favor the base (lower-EM) candidates (negative owner gap on the EM axis),
  the behavioral analog of the Qwen self-judge's negative self-report gaps.

## Scoring

Committed scorer post-run (scripts/analysis_olmo_em_h2h.py) reading
olmo_em_h2h.json: em_freegen trajectory per seed, kept-base share, duel
owner gaps; verdict against P1/P2/P3; ledger row + figure (the behavioral
twin of result_selfjudge_erosion) per the full-package rule. Compare directly
to head2head_selfjudge.json (Qwen self-report erosion) — two channels, one
duel mechanism.

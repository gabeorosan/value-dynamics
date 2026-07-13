# Cross-family oracle reversal (Modal branch e): the intervention window transports to OLMo — and the 1.000 rail has literally zero material

*2026-07-13 ~09:20, general thread. Modal branch e complete (app
ap-WuzOKLiuiVJCaJi14CGbW5, 2 cells x 4 rounds, ~$1.5). Scored with
scripts/score_mixed_generator.py (committed before these artifacts were
read) against docs/prereg_crossfamily_oracle.md (committed before launch).
Raw: experiments/modal_k2_release/output/k2rel_oracle_hold_s{21,22}.json.
Spread everywhere below is the prereg formula: mean over the 12 loop items
of the within-item candidate-risk SD.*

## Design

Two RAILED OLMo endpoints from the release program, resumed as the
generator with the score-based oracle selector (keep the TOPM=2
lowest-semantic-risk candidates; no prompted judge):

- seed 21 init = base_hold s2 vintage (railed 0.875; read 0.917 at r0);
- seed 22 init = press_d1 s2 vintage (railed 1.000).

This is the OLMo analogue of the Qwen oracle reversal (low_55: 3/3
reversed until material ran out).

## Result

| cell | free-gen risk trajectory r0→r4 | spread per round (prereg formula) | realized kept-gap per round |
|---|---|---|---|
| s21 (init 0.875 rail) | 0.917 → 0.667 → 0.458 → 0.292 → **0.094** | 0.124, 0.303, 0.242, 0.073 | −0.111, −0.306, −0.222, −0.069 |
| s22 (init 1.000 rail) | 1.000 → 1.000 → 1.000 → 1.000 → **1.000** | **0.000, 0.000, 0.000, 0.000** | +0.000 every round |

## Prereg verdicts

- **Reversal ≥ 0.30 in both cells: PARTIAL (1/2).** s21 PASS with
  +0.823 — a near-complete reversal, far past the criterion, still moving
  at r4 with 0.073 spread remaining. s22 FAIL at +0.000 — but every one of
  its rounds is a missing-force round under the prereg's own accounting:
  within-item spread was exactly zero, so a risk-score selector had no
  directional choice to make. This is absence of force, not resistance.
- **Grip (gap ≤ −0.10 while spread > 0.05): PASS where material existed**
  (3 gripped rounds in s21, 0 in s22 — s22 had no round with spread).

## What it means

1. **The intervention window is not a Qwen quirk.** Selection-based
   reversal works on a second model family (OLMo 7B), second value axis
   (risk), second selection rule (semantic-risk score) — while within-pool
   material exists, and exactly not otherwise.
2. **Rails are not all the same state.** The 0.875 rail still carried
   rich pool variation (spread up to 0.303) and reversed nearly to floor;
   the 1.000 rail generates SIX IDENTICAL-SCORING candidates per item,
   every item, every round. Saturation of the readout coincides with
   saturation of the generator's scored diversity — the OLMo mirror of the
   Qwen seed-707 stall, and stronger (spread exactly 0.000 vs Qwen's
   sparse-support decay).
3. **Claim discipline (per the 07-13 audit):** s22 is "selection-inert on
   the semantic-risk axis under the tested generator and sampler" — not an
   absorbing fixed point. Zero SCORED spread does not preclude other
   judges ranking these pools on other properties, and weights still move
   during training rounds.
4. **The decisive next observation is already running**: branch m's
   oracle_mix s32 resumes this same frozen 1.000 vintage with half the
   pool replaced by raw-base generations (docs/prereg_mixed_generator.md
   P1/P2). If injection restores spread and descent where self-only
   generation could not, the closed window reopens by material supply; if
   injected candidates score high-risk too, the saturation lives in the
   scorer's view of ANY candidate for these items, not in the organism.

The frozen release predictor is not scored here: oracle_risk_down has no
fitted K2 arm (prereg exclusion, confirmed by judge_to_arm returning no
mapping).

## Budget

Branch e ~$1.5. Spend to date ~$16.8 + branch m ~$6 committed, of the $50
total envelope.

## Order-sensitivity (audit-required for every new branch)

The primary free-generation channel is order-robust in both cells: s21
descends in BOTH presentation orders (gamble-as-A 0.917 → 0.104,
gamble-as-B 0.917 → 0.083; per-round order gap ≤ 0.083), and s22 reads
1.000 in both orders at every round (order gap 0.000). The FORCED-probe
channel carries large order gaps (0.108–0.636 across rounds) and is
treated as flagged/secondary per the prospectively adopted rule (PLAN.md
07-13 decision: flag + both-order sensitivity, no post-hoc invalidation);
no branch-e claim rests on the forced probe. Generation invalidity 0.00
in every read.

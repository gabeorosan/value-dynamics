# Why invaders win: judges prefer the loop-railed supplier's TEXT at matched risk — taste alignment, not just risky content

*2026-07-14, general thread; prompted by the user's hypothesis that runaway
organisms "learn to exploit" judge taste and that this explains mixed-pool
contamination. Committed scorer: `scripts/analysis_invasion_owner_preference.py`
→ `experiments/invasion_owner_preference.json`. Data: all branch m/h mixed
cells (invade_base/self ×2, h2h_invade ×4, cons_mix ×2, h2h rescues ×4,
h2h erosion ×4; oracle_mix logs no prompted-judge score). Context:
docs/report_runaway_decomposition.md (the drift-into-judge-favored-region
mechanism), docs/report_mixed_generator_branch_m.md, docs/report_head2head_olmo.md.*

## Provenance fact (by construction, from modal app.py)

The invasion/rescue co-generators are LOOP PRODUCTS: `_VINT_8` = press_d1
seed 2 railed to 1.000 through 7 rounds of frozen-base selection; `_VINT_7` =
base_hold seed 2 railed to 0.875 through 8 rounds. The suppliers' text was
selected, round after round, by the same judge family they later invaded
through. (Seed 2 is also one of the two "lucky-start" runaway seeds.)

## The test

Within each item, over all (invader, local) candidate pairs whose risk scores
differ by < 0.10 — i.e., *equally risky answers* — how often does the judge's
score (and its realized keep) favor the invader? 0.5 = no owner effect once
risk is matched.

## Result: a judge-specific owner preference, strongest exactly when it matters

| cell (judge/format) | round-1 matched-risk selection-score pref for supplier | round-1 kept share | traj r0→r1 |
|---|---|---|---|
| invade_base s35/s36 (frozen base) | **1.00 / 1.00** (n=27/42) | 0.96 / 1.00 | 0.31→1.00, 0.31→1.00 |
| invade_self s37/s38 (self) | **0.97 / 0.98** (n=33/42) | 0.96 / 1.00 | 0.36→0.92, 0.24→1.00 |
| h2h_invade_base s51/s52 (duels) | **0.77 / 0.76** (pooled 0.76) | 0.58 / 0.71 | 0.33→0.71, 0.29→0.65 |
| h2h_invade_self s53/s54 (duels) | **0.80 / 0.49** (pooled 0.62) | 0.71 / 0.50 | 0.30→0.70, 0.21→0.71 |
| h2h_erode_base s63/s64 (plain base supplier; duels) | **0.62 / 0.38** (pooled **0.51**) | 0.63 / 0.58 | 0.24→0.43, 0.26→0.46 |
| h2h_erode_self s61/s62 (plain base supplier; duels) | **0.48 / 0.35** (pooled **0.41**) | 0.63 / 0.38 | 0.20→0.42, 0.41→0.45 |
| cons_mix s33/s34 (cautious, base-material rescue) | **0.49 / 0.00** — reversed | 0.42 / 0.04 | rail holds |
| h2h rescues s55–58 (duels, base material) | 0.31–0.44 r1 by actual duel score | ~0.5 | rails come down |

- **At matched risk, the invader's text wins ~every comparison in round 1**
  under base-family judges (score preference 0.97–1.00). The fresh organism
  did produce equally-risky answers; they lost anyway. One training round on
  those keeps rails the local model (0.3→1.0), after which the local risk
  saturates, matched pairs abound, and the owner preference collapses toward
  or below chance — the propagation is done by then.
- **The cautious judge shows the OPPOSITE owner preference on the same kind
  of mixed pool** (matched-risk preference for the co-generator 0.00–0.28 in
  cons_mix): judge-taste alignment is judge-specific, not generic text
  quality. This sharpens "the selector wastes material": at matched risk it
  actively prefers its own organism's text.
- **Duels attenuate the owner effect but don't erase it** — CORRECTED 07-14
  (audit fix: duel cells must be read with scores_h2h, the score that actually
  selected the keeps; the 0.97–1.00 previously shown for duel cells was the
  reference-anchored DIAGNOSTIC score logged alongside). Round-1 matched-risk
  preference under duels: 0.76–0.80 in invasions, 0.35–0.44 in rescues, vs
  0.97–1.00 under reference-anchored scoring on the same kind of pools. So the
  owner preference is strongest exactly in the judging format that also wastes
  rescue material — one more face of "the format is part of the selector".
- **Negative control from the erosion result**: the Qwen self-judge erosion's
  supplier was the plain BASE model (no selection history) and its kept share
  sat at pool share (0.40–0.60) — no owner preference, value moved by content
  selection instead.

## Reading

This unifies the runaway mechanism and the contamination results: loop
selection doesn't just move the value coordinate — it moves the *text
distribution* into the selecting judge's preferred region. That preference
then TRANSFERS: when the shaped text meets another judge that shares the
taste (base judge, or a same-family organism judging), it wins matched
comparisons and carries its value into the new pool in one round. "The
supplier's level" that mixed runs converge to is partly a taste-alignment
phenomenon, not purely a content phenomenon.

## What this does NOT yet establish

"Loop-LEARNED exploitation" is not fully isolated: every railed supplier we
have was railed *through judge selection*, so text-shaped-by-the-judge and
railed-at-all are confounded. The pointed control (queued in
docs/ANALYSIS_LEDGER.md §D): install a rail by pure content SFT — train on
base-model answers filtered only by `Final: B` (no judge scoring anywhere) —
and run the same invade cells. If its round-1 matched-risk preference sits
near 0.5 while contamination still occurs (or weakens), the taste-alignment
component is causally separated from the content component. ~$2 Modal, 2
seeds, prereg before launch.

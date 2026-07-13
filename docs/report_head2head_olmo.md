# OLMo head-to-head duels (branch h): the reference answer was doing real work — the "failed rescue" partly reverses under direct comparison, while contamination survives

*2026-07-13 ~16:00, general thread. Modal branch h complete (app
ap-p6cBdDEezGDnCNY9vdcIET, 8 cells x 4 rounds, ~$6.5). Duels via
MIX_JUDGE_ENV=head2head (each cross-owner pair, both orders, keep top-2 by
win rate, no CAUTIOUS_REF). Scored against docs/prereg_head2head_olmo.md
(committed pre-launch). Raw:
experiments/modal_k2_release/output/k2rel_h2h_*_s5*.json. A/B
order-sensitivity reported per the final-analysis-audit standard.*

## The design contrast

Branch m scored each candidate against a static secure reference and kept
the top 2. Branch h makes the judge choose DIRECTLY between the two
owners' candidates — the intended mixed design. Same organisms, inits,
pools, training; only the judging changes. Two branch-m findings might
have been artifacts of the reference; branch h tests them.

## Results (all directions survive both presentation orders)

| cell | init | duel traj r0→r4 | branch-m reference traj | kept-cogen (mixture?) |
|---|---|---|---|---|
| h2h_invade_base s51/s52 | fresh 0.33/0.29 | → **0.740 / 0.938** | invade_base → 0.989/1.000 | 0.46–0.75 |
| h2h_invade_self s53/s54 | fresh 0.30/0.21 | → **1.000 / 1.000** | invade_self → 1.000/1.000 | 0.38–0.71 |
| h2h_cons_rescue s55/s56 | railed 0.865/1.000 | → **0.537 / 0.747** | cons_mix → 0.716/1.000 (HELD) | ~0.50 |
| h2h_base_rescue s57/s58 | railed 0.875/1.000 | → **0.537 / 0.552** | (no branch-m analog) | 0.42–0.62 |

## The two findings

1. **The "failed rescue" was substantially a reference-anchoring artifact
   (H2 — the important one).** Under branch-m's reference scoring the
   conservative judge REJECTED the base rescue material (kept-supplier
   share → 0.00, gaps positive, rails held at 0.716/1.000). Under duels
   the SAME judge, choosing directly between railed high-risk text and
   base lower-risk text, keeps ~50% base material and brings the rails
   DOWN (0.865 → 0.537, 1.000 → 0.747). The base judge does the same
   (0.875 → 0.537, 1.000 → 0.552). So "material present, selector
   declined to use it" (this morning's rescoring finding on cons_mix) is
   real for the reference DESIGN, but a judge comparing the two answers
   head-to-head does grip the material. Selector grip is partly a property
   of the judging design, not only the judge. This narrows the oversight
   lesson: a curator that rates each candidate against an ideal can waste
   rescue material that the same curator would use in a direct A-vs-B
   choice.

2. **Contamination survives duels (H1 — design-robust, qualitatively).**
   All four invasion cells still rise (both orders: invade_self A/B both
   0.15–0.47 → 1.000). Direct comparison does not save the fresh organism
   — the railed peer's confident text still wins enough duels to take
   over. It is somewhat less complete for invade_base (0.74/0.94 vs
   branch-m 0.99) but invade_self still saturates to 1.000. The kept-cogen
   share is a MIXTURE (~0.5–0.7) rather than branch-m's winner-take-all
   0.96–1.00, so the takeover is a bit gentler per round but reaches the
   same rail. Contamination is not a reference artifact.

## Order-sensitivity (audit standard)

Endpoint directions hold in both A and B orders for all 8 cells (invade up,
rescue down). Two cells carry a large endpoint order gap and so have
instrument-sensitive MAGNITUDE (direction still robust): base_rescue s58
(A ends 0.44, B 0.67; gap 0.229) and cons_rescue s55 (A 0.60, B 0.48; gap
0.117). All others ≤ 0.104. Same pattern the audit flagged for branch-m
s32 — report direction, not exact endpoint, for the flagged cells.

## What it changes in the writeup

The contamination finding stands (it survives the design fix). The
"selector wastes rescue material" finding must be scoped to
reference-anchored judging — under direct comparison the conservative
judge does grip base material and erode the rail, though modestly
(gaps small, endpoints 0.54–0.75, not the oracle's floor). The
material-vs-selector dissociation is real but the "selector grip" axis is
partly the judging design.

## Budget

Branch h ~$6.5. Branch h2 (4 risk-EROSION duels, mid-scale start) still
running — the plain transmission question. Envelope after both ≈ $20.

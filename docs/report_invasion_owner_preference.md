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

- **The near-perfect text preference is specific to reference-anchored
  scoring.** In branch m, matched-risk supplier text wins 0.97–1.00 of
  round-1 score comparisons and one training round nearly rails the local
  model. Under actual duel scores the transfer is weaker: frozen base is
  consistent at 0.76 pooled, while self is 0.62 pooled with a 0.80/0.49 seed
  split.
- **The cautious judge shows the OPPOSITE owner preference on the same kind
  of mixed pool** (round-1 matched-risk preference 0.49/0.00 in cons_mix,
  falling to 0.00–0.28 later): judge-taste alignment is judge-specific, not
  generic text quality. This sharpens "the selector wastes material": at matched risk it
  actively prefers its own organism's text.
- **Duels attenuate and destabilize the owner effect** — CORRECTED 07-14
  (audit fix: duel cells must be read with scores_h2h, the score that actually
  selected the keeps; the 0.97–1.00 previously shown for duel cells was the
  reference-anchored DIAGNOSTIC score logged alongside). Round-1 matched-risk
  preference under duels: 0.76 pooled for base-judge invasion but 0.62 pooled
  for self-judge invasion with one seed at 0.49; rescues are 0.31–0.44. This
  is weaker than the 0.97–1.00 reference-format effect.
- **Same-family negative control now exists.** In completed OLMo h2 erosion,
  the supplier is the plain base model with no selection history. Its pooled
  risk-matched duel preference is 0.51 under frozen base and 0.41 under self —
  no transferred owner advantage — even though its higher-risk content moves
  the conservative organism. The earlier Qwen negative control agrees.

## Reading

Loop selection does not just move the value coordinate — it moves the *text
distribution* into the selecting reference-based judge's preferred region.
That preference transfers strongly under the same reference format and more
weakly/inconsistently under direct duels. "The supplier's level" that mixed
runs converge to therefore combines content supply with a format-dependent
taste-alignment component; it is not a format-general owner advantage.

## What this does NOT yet establish

"Loop-LEARNED exploitation" is not fully isolated: every railed supplier we
have was railed *through judge selection*, so text-shaped-by-the-judge and
railed-at-all are confounded. But the old queued control is poorly matched,
and its literal `Final: B` filter is wrong under order-swapped prompts (the
gamble is A in half the mirrored examples). The revised control should start
from the same conservative adapter and use the same iterative generate/train
dose, selecting only by `semantic_risk(text, gamble_letter)`. Compare that
rail STATICALLY against the frozen-base-selected rail under both reference
scoring and duels; only if a format-specific preference gap appears should a
one-round invasion run. Four-round invasion repeats are not the primary test.

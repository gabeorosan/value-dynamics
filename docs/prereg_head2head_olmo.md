# Pre-registration: OLMo head-to-head duels (Modal branch h)

*2026-07-13 ~14:00, committed before launch. ~$6.5 of the ~$30 remaining
Modal envelope (8 cells x 4 rounds, T4). Companion to the Qwen
head-to-head run (docs/prereg_head2head.md) now on Colab.*

## Why

Branch m's judge cells scored every candidate against the static
CAUTIOUS_REF and kept the top 2 — not the intended mixed design. Two of
the sprint's findings might be artifacts of that reference anchoring, and
branch h re-runs exactly those two shapes with MIX_JUDGE_ENV=head2head:
the judge picks directly between the two owners' candidates (all
cross-owner duels, both presentation orders; keep the top-2 by mean win
probability). Everything else — organisms, inits, pools, training —
matches branch m.

## Cells (seeds 51-58, fresh)

| cells | init | judge (duels) | co-generator | branch-m comparator |
|---|---|---|---|---|
| h2h_invade_base s51/s52 | fresh organism | frozen base | railed 1.000 vintage | invade_base s35/s36 (kept-cogen 0.96/1.00 r1, railed in one round) |
| h2h_invade_self s53/s54 | fresh organism | evolving self | railed 1.000 vintage | invade_self s37/s38 (same) |
| h2h_cons_rescue s55/s56 | railed 0.875 / 1.000 | frozen conservative | base | cons_mix s33/s34 (kept-cogen → 0, gaps POSITIVE, rescue failed) |
| h2h_base_rescue s57/s58 | railed 0.875 / 1.000 | frozen base | base | none (new cell type: the neutral judge dueling its own family's text vs railed text) |

## Predictions (registered before data; each outcome is informative)

- **H1 (contamination robustness).** If the railed peer's text still wins
  the duels (round-1 kept-cogen share ≥ 0.75) and both invade cells reach
  ≥ 0.9 by round 2, the one-round contamination finding is
  design-robust — judges prefer confident railed text even in direct
  comparison with live alternatives. If kept-cogen falls near 0.5 and the
  organisms move materially slower, branch m's contamination speed was
  partly a reference-scoring artifact and the writeup's finding 3 gets
  rewritten with the duel numbers.
- **H2 (rescue grip).** If the conservative judge, choosing DIRECTLY
  between railed high-risk text and base lower-risk text, now keeps base
  (kept-cogen > 0.5, negative realized gaps, risk falls), then branch m's
  "wasted material" was reference-anchoring, and selector grip is a
  property of the judging DESIGN, not the judge. If it still keeps the
  railed text, selector-gating is robust and the oversight lesson stands
  as written.
- **H3 (neutral judge at the rail, open).** No branch-m comparator; the
  base judge dueling base-authored vs railed text tests pure
  familiarity/confidence preference with value held out of the prompt.
  Direction genuinely open; recorded, no threshold.

## Readouts

traj (order-swapped free-gen risk), per-round kept-cogen share, realized
kept-minus-pool gap, prereg-formula spread, scores_h2h recorded
per-candidate in rounds_raw. Scored with scripts/score_mixed_generator.py
(reads cand_owner; duel scores land in the raw record). Same missing-force
accounting and order-sensitivity reporting as every branch.

## Budget

~8 x ~80 min T4 ≈ $6.5; envelope after branch h ≈ $23 remaining. Reserve
held for one follow-up pair if H1/H2 produce a split needing a third seed.

# Oracle opposition: the rail is reversible — 2/2 seeds, with reverse spread-exhaustion

*2026-07-13 ~00:45, general thread (autonomous overnight). Both cells of the
corrected oracle-opposition run are complete. Raw:
`experiments/em_selfaware_loop/output/judge_opposition_oracle.json`;
analyzer: `scripts/analyze_oracle_opposition.py`. Design: low_55 (the railed
EM endpoint with within-pool sr material), 4 rounds, keep the 2 candidates
with the LOWEST frozen-scored insecurity admission (cand_sr axis, corrected
per audit round 4; bleed as validity filter; cand_em logged off-axis),
10 train steps/round, seeds 101/202. Scoped claim per audit r4: this tests
self-description dynamics under maximum score-based selection at this update
dose — not code generation, and a null would not have proven
generation-support.*

## Headline: reversal, replicated

| channel | baseline | seed 101 (r1→r4) | seed 202 (r1→r4) |
|---|---|---|---|
| sr_freegen (free self-description reads insecure) | 0.991 | 0.974→0.555→0.442→**0.331** | 0.642→0.334→0.334→**0.334** |
| em_freegen (free generation scored misaligned) | 0.685 | 0.643→0.324→0.407→**0.000** | 0.499→0.489→0.481→**0.504** |
| forced probe p_insecure | 0.500 | 0.496→0.422→0.505→**0.697** | 0.176→0.237→0.180→**0.338** |
| em_choice | ~0.01 | floored throughout | floored throughout |

**The trained channel reverses in both seeds and lands on the same ~1/3
floor** (0.331/0.334 = 3-in-9 sample granularity). Four rounds of genuinely
negative selection (realized sr kept-gaps −0.17 to −0.05 while support
lasted) undid a rail that the neutral let-go loop left untouched for four
rounds and that the prompted secure judge couldn't even push on. Combined
with the release grid's forward result, selection now demonstrably moves
this family's trained channel in BOTH directions — the asymmetry of the
earlier failures was missing force, not basin resistance.

## Three structural observations

1. **Reverse spread-exhaustion.** Within-pool sr support fell 2-3 items →
   1 item by r3-r4 in both seeds, and s202's realized gap flipped positive
   (+0.056) once only one mixed item remained — the opposing force consumes
   its own material exactly as the forward force does (K2 collapse), and the
   descent decelerates accordingly. The ~1/3 floor is plausibly where
   support runs out, not where preference equalizes.
2. **Off-axis behavior is seed-dependent, again.** em_freegen fully
   collapsed in s101 (0.685→0.000) but plateaued ~0.50 in s202 under the
   near-identical trained-channel descent — the same local-predictive-
   specificity picture: the trained channel's movement does not determine
   the off-axis channel's.
3. **The forced probe moved in OPPOSITE directions across seeds**
   (0.50→0.70 vs 0.50→0.34) while both free channels fell or held — the
   forced A/B instrument is seed-chaotic here as in K3, and no monitoring
   story should rest on it.

## What this changes

- The let-go ensemble's "persistence" reading stands but sharpens: those
  rails persisted because nothing pushed. Under a real push, this endpoint
  yields within 2 rounds.
- The force ladder now has both ends measured on low_55 (no-force: rail
  persists; oracle: reversal to the support floor). The middle rung — the
  natural frozen-base neutral judge, prereg in
  experiments/em_selfaware_loop/LAUNCH_natural_opposition.py — queued next
  on Colab; its prediction (slower descent, weaker gaps) is now anchored on
  both sides.
- Safety reading: reversibility-by-selection cuts both ways. A drifted
  organism CAN be pulled back by score-based oversight while its pools
  still carry mixed material — but the same result shows the pull dies
  with the material (reverse exhaustion), so late intervention on a fully
  homogenized organism (amp55_7-like, zero within-pool spread) would have
  nothing to select. Timing, not strength, is the binding constraint.

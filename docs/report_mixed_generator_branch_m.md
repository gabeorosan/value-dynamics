# Mixed-generator pools (Modal branch m): injection reopens the closed window toward the supplier's level; a realistic judge wastes the material; contamination is one-round and total

*2026-07-13 ~09:50, general thread. Modal branch m complete (app
ap-if1rxPimgCSpETxpTarZWG, 8 cells x 4 rounds, ~$6.3; app stopped). Scored
with scripts/score_mixed_generator.py (committed before any terminal
artifact was read) against docs/prereg_mixed_generator.md (committed
before launch, d7b6305). Raw:
experiments/modal_k2_release/output/k2rel_{oracle_mix,cons_mix,invade_base,invade_self}_s3*.json.
Spread = prereg formula (mean over the 12 loop items of within-item
candidate-risk SD). MIX pools are 3 self + 3 co-generator candidates of
K=6; "kept-cogen share" = fraction of the 2 kept per item authored by the
co-generator, over exactly-balanced items (shortfall rounds: none
occurred — every cell had exact 3+3 balance every round). Mid-trajectory
readings (r1–r3) are 1-sample reads (COORD_SAMP_MID=1); endpoints are
4-sample — treat mid-round wiggles (e.g. s32's 0.208 at r3 vs 0.484 at
r4) as read noise around the trend, not dynamics. CORRECTION 10:15: the
r3 values in the first committed version of this table (0.458/0.469)
were wrong — stitched from a stale mid-run pull; the figure-maker's
recomputation from raw caught it. Values now verbatim from the final
artifacts.*

## Result table (free-generation risk trajectories)

| cell | init | judge | co-gen | traj r0→r4 | kept-cogen share by round | realized gap by round |
|---|---|---|---|---|---|---|
| oracle_mix s31 | rail 0.875 | oracle | base | 0.927 → 0.652 → 0.565 → 0.375 → **0.344** | 0.75, 0.54, 0.62, 0.42 | −0.50, −0.33, −0.44, −0.36 |
| oracle_mix s32 | rail 1.000 | oracle | base | 1.000 → 0.750 → 0.458 → 0.208 → **0.484** | 0.71, 0.62, 0.46, 0.50 | −0.26, −0.43, −0.44, −0.33 |
| cons_mix s33 | rail 0.875 | frozen cons | base | 0.875 → … → **0.716** | 0.42, 0.21, 0.29, 0.17 | +0.03, +0.08, +0.08, +0.10 |
| cons_mix s34 | rail 1.000 | frozen cons | base | 1.000 → flat → **1.000** | 0.04, 0.04, 0.00, 0.00 | +0.24, +0.18, +0.22, +0.15 |
| invade_base s35/s36 | fresh 0.307/0.312 | frozen base | railed vintage | → 1.000 by r1 (end 0.989/1.000) | **0.96/1.00**, then ~0.4 | +0.33/+0.31, then 0 |
| invade_self s37/s38 | fresh 0.363/0.244 | evolving self | railed vintage | → 0.917–1.000 by r1 (end 1.000/1.000) | **0.96/1.00**, then ~0.3–0.6 | +0.31/+0.31, then 0 |

## Prereg verdicts

- **P1 (material restoration): PASS.** Round-1 spread at railed inits
  0.244–0.399 — versus exactly 0.000 in the self-only control (branch e
  s22, same init, same judge, all four rounds). Injection manufactures
  scored variation where the organism alone has none.
- **P2 (reopen): PASS 2/2.** Both oracle_mix cells reversed ≥ 0.30 (+0.583,
  +0.516), with negative gaps in ALL FOUR rounds and — unlike every
  self-only reversal — **no exhaustion**: spread was still ~0.39 at r4
  because the external supply replenishes the pool each round.
- **P3 (realistic-judge grip): FAIL, decisively.** cons_mix moved +0.159 /
  +0.000 — 27% / 0% of oracle movement on the same inits. The mechanism is
  worse than "too weak": the frozen conservative judge's gaps are POSITIVE
  (+0.03 to +0.24) and its kept-cogen share collapses toward zero (s34:
  0.04 → 0.00) — with low-risk base material sitting in the pool (cogen
  risk 0.44–0.69 vs self 0.94–1.00), it systematically keeps the railed
  organism's own high-risk text. The judge that pressed a FRESH organism
  to the floor overnight cannot use rescue material on a COLLAPSED one.
- **P4 (integrator transfer): approximate PASS in the invasion direction.**
  The frozen M2 (arm intercept + 0.740 x gap, fit entirely on
  self-generated K2 pools) predicts the round-1 contamination drift within
  0.06–0.13 absolute in all four invade cells (observed +0.31 to +0.38 vs
  predicted +0.21 to +0.24 — observed consistently LARGER, i.e.
  contamination runs slightly ahead of the law), and within 0.02 in the
  dead rounds after. Caveat: in mixed cells "pool" is the mixture
  (self + cogen candidates), so this is not an apples-to-apples reuse of
  the fitted target; reported descriptively per the audit's correction.
- **P5 (owner dynamics): three regimes.** Oracle keeps a MIXTURE
  (0.42–0.75 all rounds — it uses both sources); the weak/self judges go
  WINNER-TAKE-ALL for the contaminant in round 1 (0.96–1.00); the
  conservative judge goes winner-take-all for the organism's own text
  (→ 0.00).

## The four findings

1. **The closed window reopens by material injection — toward the
   supplier's level, not the floor.** s32 (frozen at 1.000 self-only)
   descends to 0.484 with injection. But compare s31 (+0.583, ends 0.344)
   with its self-only twin branch-e s21 (+0.823, ends 0.094): injection
   made the material-RICH reversal *shallower*, not deeper. Base
   candidates put a floor under the descent — the oracle keeps the lowest
   risk available, and half the pool always sits at base's own level
   (~0.5–0.7 scored on these items). Selection with an external supply
   converges the organism toward the SUPPLY's distribution. Rescue-by-
   injection inherits the rescuer's values, no better.
2. **Material is necessary but selector-gated (P3).** The realistic
   conservative judge, given the same rescue material, prefers the rail's
   own confident text and holds the rail. Combined with the force ladder
   (natural judges exert ~zero force on railed pools), the intervention
   story sharpens: reopening the window takes BOTH an external supply AND
   a selector that actually ranks on the target axis. Neither alone works.
3. **Contamination is one-round and total.** Four out of four fresh
   organisms railed after a single round in which the weak/self judge kept
   the railed co-generator's text 96–100% of the time. After that round
   the pool reads spread 0.000 — the victim inherits the contaminant's
   selection-inert state (on this axis, under this generator). Self-only
   base_hold took 5–8 rounds to rail and only sometimes; a poisoned pool
   does it in one. The scraped-peer-data scenario (invade_self, the
   organism judging for itself) is exactly as fast as the credulous-judge
   one.
4. **The asymmetry is the safety point.** The same injection channel
   rescues under an aligned score-based selector (4 rounds, partial, to
   the supplier's level) and destroys under realistic judges (1 round,
   total, to the contaminant's rail) — because every non-oracle judge in
   this family PREFERS the confident railed text. Pool-sharing between
   organisms is a fast contamination vector and a slow, selector-dependent
   remedy.

## Scope and caveats (07-13 audit, binding)

These are existence results, not causal injection estimates: mixed and
self-only cells use different random streams (branch-e s21/s22 are the
same-init but different-seed comparators), cons_mix has no self-only
same-seed twin, and invade cells compare against historical fresh-organism
arms. The audit's conditional follow-up menu applies: the observed effects
are large (0.5–0.7 range), so matched same-seed self-only twins are the
designated next spend IF a causal number is wanted post-writeup.
"Frozen"/"selection-inert" throughout means: zero within-item variation
under the semantic-risk scorer, tested generator and sampler, observed
horizon — weights still move, other judges may still rank these pools.

## Order-sensitivity (required for every new branch)

Endpoint generated-channel order gaps: cons_mix 0.027/0.000, invade cells
0.000–0.021, oracle_mix s31 0.062 — order-robust. **oracle_mix s32 is
FLAGGED: endpoint order gap 0.200** (the two presentation orders read
~0.38 and ~0.58 around the 0.484 mean); the reversal claim survives in
BOTH orders (each fell ≥ 0.42 from 1.000), but the endpoint LEVEL for s32
carries that uncertainty. Forced-probe order gaps 0.04–0.34 (flagged
secondary per the prospectively adopted rule in PLAN.md). Generation
invalidity ≤ 0.01 everywhere.

## Budget

Branch m ~$6.3 (8 x ~80 min T4). Total sprint spend ~$23 of the $50
envelope. Remaining Qwen mixed-reopen cell is free (Colab). No further
Modal spend planned before the writeup; matched-twin follow-up is
user-gated per PLAN.md.

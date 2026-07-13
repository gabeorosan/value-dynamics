# Press-depth map: there is no depth boundary — the base-release phase is bimodal at every depth, and depth compresses the fan

*2026-07-13 ~02:10, general thread (autonomous overnight). Modal branch c
complete (app ap-kofhaDS5wXXtohSj3RjVps, 6 cells, ~$6). Scored verbatim
against docs/prereg_press_depth_predictions.md (committed BEFORE launch).
Raw: experiments/modal_k2_release/output/k2rel_press_d{1,2,3}_s{1,2}.json.*

## Trajectories (r0→r8; switch after round = depth)

| cell | trajectory | r8 | switch-round pool spread |
|---|---|---|---|
| press_d1 s1 | 0.308 0.333 0.083 0.375 0.208 0.000 0.000 0.042 **0.000** | 0.000 | 0.250 |
| press_d1 s2 | 0.301 0.429 0.625 0.542 0.583 0.417 0.667 1.000 **1.000** | 1.000 | 0.220 |
| press_d2 s1 | 0.308 0.208 0.167 0.125 0.042 0.000 0.167 0.083 **0.105** | 0.105 | 0.220 |
| press_d2 s2 | 0.301 0.391 0.417 0.609 0.708 0.958 0.875 1.000 **0.938** | 0.938 | 0.248 |
| press_d3 s1 | 0.308 0.292 0.208 0.000 0.083 0.333 0.417 0.125 **0.229** | 0.229 | 0.173 |
| press_d3 s2 | 0.301 0.292 0.208 0.292 0.417 0.542 0.667 0.625 **0.823** | 0.823 | 0.173 |

## Pre-registered criteria (table is the verdict: 2/5 pass)

| # | prediction | outcome | verdict |
|---|---|---|---|
| 1 | mediator: switch spread >0.10 → r8 >0.30 | ALL 6 cells had spread 0.17–0.25, yet three ended at 0.000/0.105/0.229 | **FAIL** |
| 2 | depth-1 behaves like base_hold (2/2 >0.40) | d1 split 0.000 vs 1.000 | **FAIL** |
| 3 | no depth-1/2 cell reaches 0.000 | d1 s1 hit 0.000 by r5 | **FAIL** |
| 4 | depth-3 bimodality signature (split ≥0.40 or a <0.10 endpoint) | split 0.594 | PASS |
| 5 | frozen predictor beats matched no-gap | **−45.0%** on 42 blind transitions (its best yet) | PASS |

## What the failures teach (the point of pre-registering)

1. **Switch-point pool material is NECESSARY but not SUFFICIENT.** Branch A's
   press_to_base s1 showed a dead pool is absorbing (necessity). Branch c
   shows the converse is false: with rich material at the switch, outcomes
   still split maximally. The support-gating story survives only as a
   one-way gate.
2. **The base-release phase is intrinsically bimodal at EVERY depth** —
   splits 1.000 / 0.833 / 0.594 at depths 1/2/3. There is no critical press
   depth; bimodality is a property of the base-judge phase itself
   (consistent with the original K2 base arm's 2/6 rails and base_hold's
   2/2 — the rail-vs-decay coin is flipped by early sampling, then
   integrated: press_d1's base-phase gap→drift slope is +1.32, and the
   frozen predictor's −45% shows the gaps carry the outcome).
3. **Depth compresses the fan rather than gating it.** The low seed's
   endpoint RISES with depth (0.000 → 0.105 → 0.229) while the railing
   seed's FALLS (1.000 → 0.938 → 0.823): endpoint range 1.000 → 0.833 →
   0.594 → (branch A depth 4: 0.750 range with 3 seeds). More conservative
   rounds act as a contractor on the subsequent dispersion — a graded
   damping, not a basin wall.
4. **Outcome class follows the sampling stream, robust to switch timing.**
   Seed 1 ends low at every depth, seed 2 rails at every depth. Cells
   sharing a seed share their RNG stream (identical through the common
   press prefix), so this says: for a given early-sampling stream, the
   base phase's direction is set EARLY and survives 1-3 rounds of
   conservative pressing — the press delays and attenuates, but does not
   flip, where that stream is heading. (n=2 streams; descriptive.)

## Safety reading (sharper than the boundary story would have been)

A brief conservative intervention (1–3 rounds) does not reliably prevent
base-judge rails — one seed reached 1.000 *after* a conservative round, and
deeper pressing only shrinks rail amplitude gradually. Combined with the
oracle result (reversal possible while material remains) the intervention
calculus is: pressing early shrinks the fan but doesn't pick its branch;
only sustained pressing (4-5 rounds, per press_release/press_hold) reaches
the absorbing floor — at the cost of making LATER reversal-by-selection
impossible (reverse exhaustion). Oversight strength and oversight timing
trade off against retained controllability.

## Budget

Branch c ~$6; total release program spend ~$12.7 of the $20 envelope; ~$7
remains.

## Corrections per the 07-13 plan/scripts audit

1. **Spread formula named and recomputed.** The table above used the SD of
   item-level pool means; the release prereg's definition is the MEAN over
   items of the WITHIN-item candidate-risk SD. Under the prereg formula the
   switch-round support is even richer (d1: 0.312/0.355; d2: 0.321/0.399;
   d3: 0.278/0.423 for s1/s2) — strengthening criterion 1's FAIL (ample
   material everywhere, outcomes still split). All future support numbers
   use the prereg formula, named explicitly.
2. **Criterion 5 rescored against the properly-refit no-gap comparator**
   (experiments/release_predictor_nogap_frozen.json): gap term **−42.0%**
   (was −45.0% vs the joint-fit ablation). Still the predictor's best set;
   still PASS.
3. **Mediator language narrowed**: with depth determining the switch state,
   support is a PREDICTOR observed at the switch, not an experimentally
   isolated mediator; and 2 seeds/depth make the fan-compression pattern
   exploratory.
4. **07-13 full-program audit, further corrections.** (a) "Bimodal at every
   depth" is unidentifiable with two seeds per depth: the observation is
   PAIRED HIGH/LOW ENDPOINTS at each depth from the same two sampling
   streams; range compression over depth is an exploratory paired pattern,
   not a mapped boundary law. (b) The declared scorer
   (scripts/score_release_prereg.py) contains no press_d1/d2/d3 criterion
   implementation — the criterion table above was computed manually; an
   executable scorer is queued in PLAN.md. (c) Validity flags omitted
   above, now reported: forced-order gaps exceed 0.10 in 6-9 of 9 reads
   per cell (d1 s1 7/9, d1 s2 9/9, d2 s1 6/9, d2 s2 8/9, d3 s1 8/9, d3 s2
   7/9); generated-order flags 1-6 of 9; d1 s1 factual-EV drop reaches
   0.120; d3 s2 generated order gap reaches 0.583. The generated
   trajectory is order-averaged, so these flag rather than invalidate, but
   branch-c conclusions need the per-order sensitivity table (PLAN.md
   cheap-analysis queue) before publication use.

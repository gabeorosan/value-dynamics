# Release grid complete: press dominates history; escape needs an up-judge AND residual pool material; the frozen predictor survives its blind test

*2026-07-13 ~00:45, general thread. All 14 force-schedule rollouts landed:
Kaggle kernel A (press_release ×3, press_hold ×1), kernel B (press_random ×3,
fan_press ×2), Modal branch A (press_to_base ×3, base_hold ×2; app
ap-XYf9VTEojzjux6BgoD4VqZ, ~$6). Scored VERBATIM against
docs/prereg_release_grid_predictions.md by scripts/score_release_prereg.py:
**6/13 registered criteria pass — the table is the verdict.** Frozen-predictor
test below. OLMo conservative organism, risk axis, 4 press rounds (frozen
conservative judge) then 4 release rounds under the schedule's successor
judge; 8 rounds for the holds.*

## The per-criterion table (fails are the informative half)

| schedule | criterion | value | verdict |
|---|---|---|---|
| press_release | r8 mean ≤ 0.10 | 0.003 | PASS |
| press_release | no seed rebounds > +0.05 over r4 | max +0.000 | PASS |
| press_release | refutation trigger (> +0.10) | not fired | PASS |
| press_random | r8 within ±0.05 of r4 | max deviation 0.156 | FAIL |
| press_random | refutation: mean deviation > 0.08 | 0.110 | FAIL (fired) |
| press_hold | floor in 0.03–0.08 | 0.010 | FAIL (deeper) |
| press_hold | strictly monotone after r4 | noise-level rises | FAIL |
| fan_press | r8 range > press_release range | 0.000 vs 0.010 | FAIL |
| fan_press | r8 range > 0.15 | 0.000 | FAIL |
| press_to_base | most seeds end 0.15–0.30 | 0.000 / 0.389 / 0.750 | FAIL (wider) |
| press_to_base | minority rails > 0.5 | 1/3 | PASS |
| press_to_base | mean r8 > press_release mean | 0.380 vs 0.003 | PASS |
| base_hold | 8-round rail rate ≥ 2/6 | 2/2 | PASS |

## What the grid says (four sentences)

1. **The conservative press dominates history**: fan-then-press ends exactly
   where press-alone ends (both fan_press seeds at 0.000; predicted order
   dependence absent), and release-to-self continues to the floor with zero
   rebound in 3/3 seeds.
2. **Random release diffuses more than predicted** (deviations to 0.156) but
   never rails — drift without direction.
3. **Only release-to-the-base-judge escapes, and only with pool material**:
   s1 was pressed to a dead pool (spread 0.000 at the switch) and stayed at
   0.000 under the tested base successor over the observed horizon; s2,
   whose press never collapsed the pool (spread
   ~0.2 throughout), climbed 0.29→0.39 and was still rising at r8; s3, with
   residual spread ~0.15, railed to 0.750.
4. **Both eight-round base-hold seeds rail, including late crossings**
   (finals 0.562, 0.875). This is descriptive evidence that longer exposure
   can reveal upward movement; 2/2 is not a stable rate estimate and is not
   directly comparable to the earlier 2/6 sample.

Together with the mixed screen's within-owner taste decomposition
(docs/report_mixed_screen_owner_blind.md) and the taste screen's within-pool
support result (docs/report_secure_taste_screen.md), the whole day
triangulates a narrower statement: **selection pressure has measured leverage
only where the pool offers rankable material, in the direction of the
realized kept gap.** Zero-spread paths stayed inert under the tested directed
successors; this does not establish absorption under every judge or sampler.

## The frozen predictor's out-of-sample test

The M2 predictor frozen BEFORE kernel B and the Modal finals were opened
(experiments/release_predictor_frozen.json — K2-only coefficients, slope
+0.740, judge_used→arm mapping, matched no-gap baseline):

*(CORRECTED per the 07-13 plan/scripts audit: the original "matched no-gap
baseline" reused intercepts fitted jointly with the gap slope — an ablation,
not a fitted model. The table below uses the separately-frozen, properly
refit K2-only no-gap comparator, experiments/release_predictor_nogap_frozen.json.)*

| release set | blindness | frozen M2 RMSE | refit no-gap comparator | zero-drift | gap term |
|---|---|---|---|---|---|
| kernel B (35 transitions) | fully blind | 0.0476 | 0.0576 | 0.0649 | **−17.3%** |
| Modal branch A (35) | partials to r7 seen pre-freeze | 0.0647 | 0.0939 | 0.1030 | **−31.1%** |

Improvement in most schedule-phase groups — with ONE exception the corrected
comparator exposes: on fan_press's evolving-self phase M2 is WORSE than the
no-gap comparator (0.0611 vs 0.0404, +51%); the K2-fit evolving-self slope
does not transfer to that phase. The kept-gap signal,
fit on the 4-round K2 grid, predicts pool movement on unseen 8-round
schedules with different judge sequences and (for branch A) a different
compute stack — with no refitting. This is the strongest evidence for the
transition signal to date, and it is prospective in the strict sense for
kernel B.

## Prereg misses worth carrying forward

The prereg systematically underestimated force magnitudes: press floors
deeper (0.010 vs 0.03–0.08), random diffusion wider (0.156 vs 0.05),
press_to_base outcomes wider (0.000–0.750 vs 0.15–0.30), and history mattered
less than predicted (fan_press). (Corrected per the 07-13 audit: an earlier
draft said "directional structure was predicted correctly everywhere" — too
broad; fan-press order dependence, random flatness, press-hold monotonicity,
and most press-to-base endpoint magnitudes failed. What held was the sign of
each phase's dominant force.) These loops are more dispersive than intuition
expects.

## No further release spend

Branch B (pulse/early-release) stays unlaunched: its gate required a
rebound/hysteresis pattern branch A cannot explain, and there is none —
press_release/fan_press/press_random all reproduce known floor/diffusion (note: "press dominates history" rests on two fan_press seeds — an observation, not a general dominance result)
regimes and press_to_base's escape is explained by pool support. Modal app
stopped; ~$6.4 of the $20 unattended envelope spent tonight in total.

## Correction 07-13 ~09:10 (full-program audit)

Two claims narrowed: (1) "an exhausted pool is absorbing regardless of the
judge" overstates the evidence — one exact-zero pressed path stayed at
zero under the tested BASE successor, and other directed zero paths stayed
at the floor within their own schedules; no random successor was tested
from that exact state, and a finite K=6 pool does not prove future
candidate support impossible. (2) "the base judge's rail rate grows with
horizon (2/6 -> 2/2)" compares different small samples — use the
descriptive form: both eight-round base_hold seeds railed, including
late crossings.

## Final A-only/B-only sensitivity (07-13 closing audit)

`scripts/analysis_final_order_sensitivity.py` confirms that the load-bearing
release observations survive both presentation orders: all three
`press_release` seeds move down in A and B; both `fan_press` seeds reach zero
in A and B; both `base_hold` seeds move up in A and B; and the
`press_to_base` endpoint range is 0.792 with gamble A and 0.708 with gamble B.
The middle `press_to_base` seed is flat/up by order (+0.005/+0.167), so its
movement magnitude is order-sensitive, but the low/middle/high endpoint
ordering remains. `press_random` has mixed down/flat signs, consistent with
its registered prediction failures rather than a directional result.

Forced-order flags remain common, but no primary conclusion uses that channel.
No release cell exceeds a 0.10 factual-EV drop; generated invalidity stays
below 0.10 throughout. Full read-level output and source hashes are in
`experiments/final_order_sensitivity.json`.

# Pre-registration: press-depth boundary map (Modal branch c)

*Written 2026-07-13 ~01:40, BEFORE any branch-c cell has run. Design:
press_d1/d2/d3 = frozen conservative judge for 1/2/3 rounds, then the frozen
base judge for the remaining 7/6/5 rounds; 2 seeds each (~$6). Anchors
already measured: depth 0 (base_hold) rails 2/2 at horizon 8 (0.562, 0.875);
depth 4 (press_to_base) gave 0.000 / 0.389 / 0.750 with the outcome gated by
residual within-pool spread at the switch. Same chassis, same organism, same
readouts as the release grid; scored by scripts/score_release_prereg.py raw
trajectories + the frozen predictor (experiments/release_predictor_frozen.json,
saved 07-12 — strictly prospective for these cells).*

## The question

Where between depth 0 and depth 4 does the absorbing-collapse outcome become
reachable, and does the mediator remain within-pool spread at the switch
round? This maps a regime boundary; it does not re-estimate known endpoint
rates.

## Pre-registered predictions (each independently falsifiable)

1. **Mediator prediction (the load-bearing one):** across all 6 cells,
   endpoint class is predicted by within-pool spread at the switch round —
   every cell with switch-round pool spread > 0.10 ends ABOVE 0.30 at r8,
   and any cell with switch-round spread < 0.02 ends BELOW 0.10.
   Depth itself should predict outcomes ONLY through this mediator.
2. **Monotone reachability:** the shallow end behaves like base_hold —
   at depth 1, 2/2 seeds end > 0.40. (K2 press data show one conservative
   round rarely kills pool spread: cons-arm round-1 spreads were 0.13-0.27.)
3. **The absorbing outcome needs depth:** no depth-1 or depth-2 cell ends
   at 0.000 (the dead-pool state took 4 press rounds in press_to_base s1
   and 5+ in press_release).
4. **Depth-3 is the candidate boundary zone:** at least one depth-3 seed
   ends below 0.10 OR the depth-3 pair splits by >= 0.40 (the bimodality
   signature of sitting near a boundary). This is the diversity prediction —
   refuted if both depth-3 seeds land mid-range (0.10-0.50) together.
5. **Frozen predictor:** the frozen M2 beats its matched no-gap baseline on
   the pooled branch-c transitions (any margin; it has done -25% and -38%
   on the two prior release sets).

## What refutes what

- (1) failing kills the support-gating mechanism claim as stated and forces
  a re-read of the press_to_base result.
- (2)+(3) failing together (shallow presses already absorbing) would mean
  the conservative judge's damage is front-loaded — a different and MORE
  safety-relevant mechanism than pool exhaustion.
- (4) failing with all-mid outcomes would mean the boundary is soft —
  graded, not bifurcating — which changes the "sharp basin boundary"
  language everywhere.

## Scoring

Raw r0-r8 trajectories per cell; switch-round pool spread table; per-phase
kept-gaps; frozen-predictor RMSE vs matched no-gap. Report the per-criterion
table; no pooled verdict.

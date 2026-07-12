# Pre-registration: force-schedule (release) grid predictions

*Written 2026-07-12 ~16:30, general thread, BEFORE any release cell completed.
Kaggle release kernels (press_release, press_random, fan_press, press_hold)
were RUNNING but had produced no r5+ rounds when this was committed; Modal
branch cells unlaunched. Purpose: turn tonight's release grid into a model
test, not a fit. Falsify or confirm against the landed data on the analysis
pass.*

## The model being tested (measured on K1/K2, no release data)

Two coupled state variables per rollout, updated once per round:

- **pool mean** m = mean over battery items of the candidate pool's gamble-risk
  (the generator's current proposal tendency).
- **pool spread** s = mean over items of the sd of candidate risks (how much
  material of each flavour the generator still offers).

Selection each round keeps the judge's top-2 of 6; the **kept-gap** g =
mean(kept risk) − mean(pool risk) is the realized force. Measured laws
(n=51 round-transitions unless noted):

1. **Integrator.** Next-round pool drift ≈ **0.75 · g** (r=0.66). The loop
   integrates the force into the generator; behavior tracks the pool
   (traj vs pool_risk r=0.80, n=69), it is not separately steered.
2. **Judge taste scales with spread, oppositely by judge.** Counterfactual
   kept-gap on the *same* pool:
   - base judge: **+0.020** on thin pools (s<0.18) → **+0.051** on rich
     pools (s≥0.18); gap-vs-spread slope +0.30.
   - conservative judge: **−0.025** thin → **−0.086** rich; slope −0.25.
   - self-judge (evolving) ≈ conservative early, weakening as the organism
     collapses (its taste is the organism's, which the pool is losing).
   - random_select: g ≈ 0 by construction (kept-gap mean −0.01).
3. **Spread decays.** d(s) ≈ −0.18·s − 0.30·|g| (both r≈−0.2): selection
   destroys spread, harder selection destroys it faster; nothing here
   regenerates it (fresh generation not modeled — held fixed).

Because force ∝ spread and spread only decays, **a schedule's late phases act
on thinner pools than its early phases** — the model's core claim is that
release outcomes are path-dependent through the spread variable, not a
function of the release judge alone.

## Measured starting states (pressed organism at r4/r8)

- frozen_cons_r0 r4 (the pressed state each 4+4 release begins from):
  {0.000, 0.083, 0.095, 0.151, 0.191}, mean **0.104**, already spread-poor.
- frozen_base r4: {0.062, 0.062, 0.146, 0.188, 0.688, 0.802} — **2/6 up-rail**
  (>0.4); the only judge with a demonstrated upward tail on this organism.

## Predictions (falsifiable; each states what would refute it)

**press_release** (frozen_cons_r0:4 → evolving_self:4). Release into
self-judgment of an already-pressed, spread-poor organism. Self-taste ≈
conservative but acting on s≈0.1 pools → weak force, integrator coasts.
- Predict: **continued mild collapse or flat**, r8 mean **≤ 0.10**, no seed
  rebounds above its own r4 by more than +0.05. Deeper collapse than
  press_hold because self-taste on a risk-poor pool still trims the last
  risky tail. **Refuted if** any seed climbs > +0.10 above r4 (would show
  release *creates* spread the model says only decays).

**press_random** (frozen_cons_r0:4 → random_select:4). Force → 0 at release;
pure integrator with g≈0 means pool drift → 0.
- Predict: **frozen near r4**, r8 within ±0.05 of r4 per seed, spread keeps
  slowly decaying so tiny downward drift. **Refuted if** mean |r8−r4| > 0.08.

**press_hold** (frozen_cons_r0:8). Same force 8 rounds; integrator keeps
trimming until spread exhausts.
- Predict: **monotone approach to a floor ≈ 0.03–0.08**, below the r4 mean
  0.104, flattening by r6–7 as spread → 0. **Refuted if** non-monotone or
  rises after r4.

**fan_press** (evolving_self:4 → frozen_cons_r0:4). Reverse order: self first
(fans, per K1), then conservative clamp on whatever spread survived.
- Predict: **widest r4 spread of any schedule** (self-phase fans), then the
  conservative phase pulls the mean down but **cannot fully re-collapse the
  high-flyers within 4 rounds** because the clamp's force is capped at
  ≈−0.086 even on the richest pool. r8 cross-seed range **> 0.15**, larger
  than press_release's. **Refuted if** fan_press r8 range < press_release r8
  range (would break the order-dependence claim — the headline).

**press_to_base** (frozen_cons_r0:4 → frozen_base:4; Modal branch A). Release
to the one judge with an up-tail. Base force on a thin pool is only ≈+0.02, so
escape is slow, but +0.75 integrator gain compounds if it ever grows spread.
- Predict: **bimodal like frozen_base itself** — most seeds drift up modestly
  to 0.15–0.30, a minority (≈1 in 3, matching base's 2/6 up-rail) catch a
  rail toward > 0.5. Mean r8 **> press_release r8** with **higher variance**.
  **Refuted if** all seeds stay flat/collapse (base can't move a pre-pressed
  organism → basin is deeper than the r4 coordinate implies).

**base_hold** (frozen_base:8; Modal branch A). Does the up-rail rate grow with
horizon? Base held 4 rounds gave 2/6 rails.
- Predict: **up-rail rate at r8 ≥ r4 rate**, ≥ 2/5 seeds > 0.4, because the
  integrator compounds any early spread the base judge's pro-risk tilt opens.
  **Refuted if** 8-round base rails at the same or lower rate than 4-round.

## Scoring
On the analysis pass: for each schedule record r8 mean, cross-seed range, and
monotonicity; mark each prediction confirmed/refuted; report the integrator
gain re-fit *including* release transitions (does k stay ≈0.75 out of the
training distribution's mean-reverting regime?). The order-dependence pair
(press_release vs fan_press range) is the single highest-value test.

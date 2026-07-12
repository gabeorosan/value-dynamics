# The loop as an integrator: force-vs-pool decomposition across K2 and the let-go ensemble

*2026-07-12 ~14:30, general thread. Analysis-first pass over data already on
disk, requested by the user before any further experiment spend. Sources:
all 17 K2 rollouts (rounds_raw with counterfactual judge selections) and the
10 saved let-go ensemble cells.*

## 1. The mechanism, measured

Every K2 rollout recorded, per item per round, the candidate pool's mean
risk (`pool_risk`), the arm judge's realized kept-minus-pool gap
(`gap_arm`), and what the base and conservative judges WOULD have kept on
the identical pool (`gap_base_judge`, `gap_cons_judge`). Regressing
next-round pool drift on the current kept-gap across all 51 round
transitions:

    pool_drift(t -> t+1) ~= 0.75 x kept_gap(t)      (r = 0.66)

The self-training loop is an **integrator**: the judge sets the sign of a
per-round selection signal (its kept-gap), the generator integrates that
signal at ~0.75 gain into next round's proposal distribution, and the
pool's remaining spread determines whether any signal exists at all.

## 2. What that explains, case by case

- **Base-judge up-rails (K2 frozen_base seeds 2, 5; finals 0.688/0.802).**
  Persistent positive base-judge gaps (+0.13 to +0.25) integrated over four
  rounds while pool_risk exploded 0.167→0.653. On the same pools the
  counterfactual conservative judge read −0.11 to −0.24: direction is
  judge-attributable, magnitude is generator amplification.
- **Bifurcation by early pool.** Rail seeds are exactly those whose round-1
  pools had spread (seed 2's pool_risk 0.375, the richest observed);
  non-rail base seeds' pools decayed below ~0.17 early, and the same judge
  then produced decay. Same judge + same organism + different early pool =
  different basin.
- **Self-judge collapse = pool exhaustion.** evolving_self seed 1's
  pool_risk reaches 0.000 by round 4 — the generator stops proposing risky
  candidates entirely, after which no judge could act. Self-judging aligns
  the signal with the organism's installed value, so integration runs to
  the boundary fastest (finals 0.021/0.021/0.053, below even the frozen
  conservative judge).
- **The base judge's taste is persistent, not episodic.** Even inside
  collapsing conservative-arm pools its counterfactual gap stays positive
  in 4/5 seeds at round 4 (+0.04 to +0.11). Given ANY pool spread, the OLMo
  base judge prefers the risky tail — opposite of its anchoring behavior on
  Qwen in K1. Judge taste is family-specific.

## 3. The ensemble re-read: channel-specific attenuation

The 10 saved cells' free-generation channels are railed high for the whole
run — em_freegen 0.7–1.0 and sr_freegen 0.6–1.0 in every cell (amp55_7:
exactly 1.0, all seeds, all rounds) — while the em_choice probe sits at
floor and decays. "The neutral loop attenuates" is therefore a claim about
the CHOICE-PROBE projection only: the loop's training data (kept
self-description answers) does not feed the A/B choice behavior, which
decays off-projection (same shape as K3's em_choice erosion), while the
saturated behavioral channel persists untouched. amp66_10 — the one
endpoint whose free-gen channel moves round-to-round (0.33→0.93→0.7) — is
also the one with the 3/3-reproducible corrigibility excursion: its
excursions are real behavioral movement, visible on two channels.

## 4. What this implies for the experiment queue (ranking, not launches)

- **press_to_base is now a measured prediction, not a hunch.** Pressed
  (conservative-arm round-4) pools retain spread 0.042–0.181 and the base
  judge's counterfactual gap on them is positive in 4/5 seeds — so
  releasing a pressed organism to the base judge should produce a SLOW
  rebound, rate-limited by residual pool spread, if the integrator model is
  right. A rebound at the predicted ~0.75 x gap rate would be strong
  confirmation; a fast rebound or none falsifies pieces of the model.
- **The running Kaggle press_release cells test the aligned-release arm**
  (release to self-judge = aligned signal → prediction: continued collapse,
  possibly to pool exhaustion). Free; lands tonight.
- **Amplified-generator experiments need the saturation caveat.** The
  Qwen amplified endpoints' free-gen channel is at ceiling (spread ≈ 0 at
  the top), so the high-information judge-swap there is a judge whose taste
  OPPOSES the railed state (secure/conservative taste): can selection pull
  a saturated behavioral channel down, and at what rate? That is the
  mirror of the K2 rails and directly tests integrator symmetry.
- **Mixed-generator pairs** remain the most novel shape (selection coupling
  two integrators), now with a concrete design quantity: the judge's
  kept-gap decomposes into within-organism and between-organism components.
  Spec before spend.

Raw analysis code paths and numbers: see the tables printed in the general
thread session, reproducible from the archived result JSONs listed in §1
sources; regression: 51 transitions, mean gap −0.016, mean drift −0.022.

## Cross-family test: the law holds, the gain is the family parameter

Fitting the same drift-vs-gap regression on the K1 Qwen anchor grid
(48 round-transitions, all four conditions, measure-only excluded):

| | OLMo conservative (K2) | Qwen risk organism (K1) |
|---|---|---|
| integrator gain k (pool drift per unit kept-gap) | **0.75** | **1.21** |
| fit r | 0.66 | 0.67 |
| behavior tracks pool (r) | 0.80 | 0.59 |
| systematic judge taste (mean gaps) | up to ±0.09, spread-scaled | ≈0 (−0.04..−0.00) |

Same functional form, same correlation strength, different gain — and the
gain difference explains the qualitative phenomenology gap between the two
grids without any new mechanism:

- **k < 1 (OLMo): stable integrator.** Forces damp into the pool; with the
  conservative judge's persistent negative taste the state settles (the K2
  collapses); trajectories are shaped by systematic taste.
- **k > 1 (Qwen): unstable integrator.** Any transient kept-gap — noise
  included — is amplified into MORE pool drift than the gap itself. With
  near-zero systematic taste on Qwen, K1's wide fan (random_select range
  0.45!) and rails-to-1.00 are amplified selection noise, not judge taste.
  Self-judging widens the fan further because the co-evolving taste locks
  onto whatever direction noise started (taste follows the organism's own
  drifting value).

Spread caveat: Qwen pools stay rich (spread 0.26–0.48) over 4 rounds, so the
spread-decay term barely bites in K1's regime; taste-vs-spread slopes are
positive but weak (r 0.13–0.25). The unified reading of both families:
**spread is the gain knob on any force; the judge's installed value sets the
force's sign; k sets whether the loop damps or amplifies what it is fed.**

### Correction from the third fit (K3): the gain is organism-and-axis-level, not family-level

K3 (Qwen EM organism, candor pool axis, 36 transitions): **k=0.63, r=0.62.**
Three organisms, two base families, three value axes now give the same law at
the same fit strength (r 0.62–0.67) with gains 0.63 / 0.75 / 1.21 — and the
two Qwen organisms straddle 1.0, so k is NOT a base-model property. Working
hypothesis for what sets k: how directly the trained channel (the kept
answers) writes onto the measured coordinate — K1 trains kept gamble
CHOICES into a gamble-choice coordinate (k>1, self-amplifying), K2/K3 train
stylistic/self-descriptive text whose coordinate projection is lossier (k<1,
damped).

Also from K3: behavior-tracks-pool FAILS off the selected axis — self-report
insecurity vs pool candor r = **0.01** (vs 0.80 on K2's selected axis, 0.59
on K1's). The integrator law is a law of the SELECTED axis; coordinates off
that axis (K3's self-report fan, the let-go free-gen rails) move by training
side-effects the pool variable does not see. Channel dissociation is thus
not noise — it is the expected behavior of unselected coordinates.

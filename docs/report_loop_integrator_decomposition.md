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

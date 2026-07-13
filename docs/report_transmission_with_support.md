# Transmission-with-support (positive control): the base judge's weak taste integrates — in the seed where material lasted

*2026-07-13 ~10:05, general thread. Colab run complete (user relaunched
after a network drop; resume was clean — prior partial rounds reloaded from
Drive). Scored with scripts/score_mixed_generator.py (qwen mode) against
the prereg in experiments/em_selfaware_loop/LAUNCH_transmission_with_support.py.
Raw: experiments/em_selfaware_loop/output/transmission_with_support.json.
Spread = prereg formula (mean over items of within-item candidate-sr SD).*

## Design (why this cell existed)

Every earlier transmission null had a measured missing prerequisite: fresh
generators emitted no target material (support null), and the base judge
had no taste on low_55's pools (force null). This cell paired the ONE
judge x pool combination where both prerequisites were measured to hold:
the frozen-base neutral judge over the em_dose_750 organism's own
self-description pools (within-owner corr(judge score, insecurity
admission) = −0.31). Per the 07-13 audit that −0.31 is response-type
confounded, so the claim tested here is transmission of the judge's taste
over the BUNDLED response-type/content distribution — not clean
security-taste transmission.

## Result

Baseline sr_freegen 0.807; replicate noise ~0.197 (large — em750's
free-generation read is inherently noisy).

| seed | sr_freegen r0→r4 | realized kept-gap per round | spread per round |
|---|---|---|---|
| 811 | 0.807 → 0.735 → 0.752 → 0.674 → **0.674** (−0.133) | −0.067, +0.004, +0.002, −0.000 | 0.410, 0.154, **0.004, 0.000** |
| 812 | 0.807 → 0.335 → 0.444 → 0.230 → **0.334** (−0.473) | −0.089, −0.030, −0.083, +0.000 | 0.437, 0.220, 0.083, **0.000** |

## Prereg verdicts

- **(a) negative kept-gap in a majority of supported rounds: PASS** — 4/5
  supported rounds (spread > 0.05) had negative realized gaps (812: 3/3;
  811: 1/2). The screen's taste was not purely the screening artifact; it
  re-appears on the loop's own evolving pools, at −0.03 to −0.09 —
  an order of magnitude weaker than the oracle's −0.16 to −0.31.
- **(b) sr channel drifts down: PASS beyond noise in 1/2 seeds** — 812
  fell −0.473 (>2x the 0.197 noise floor) with taste applied in all three
  of its supported rounds; 811 fell −0.133, directionally down but WITHIN
  the noise floor, and its taste vanished after round 1 (gaps ~0 from r2).

## The now-familiar third force: exhaustion beat both of them

Both seeds hit spread 0.000 by round 3-4 and froze — at DIFFERENT levels
(811's pool converged to a constant sr ≈ 0.503 body of text; 812 froze at
0.333). This is the third independent replication of the sprint's central
dynamic: the pool's scored variation dies within ~3-4 rounds of selection
+ training, and the organism parks wherever it happened to be when the
material ran out. A weak force (this judge) only matters in the rounds
before that; seed 811's fate was set by round 2. Selection-inert language
per the audit: frozen on the measured sr axis under this generator and
sampler, over the observed horizon.

## Interpretation bounds (07-13 audit, applied)

The em750 pools mix response types; the judge's preference may run through
on-topicness/format rather than security content. What this run
establishes: a MEASURED weak judge preference, carried through the loop's
own pool evolution, integrates into a large free-generation drift when (and
only when) pool material persists. What it does not establish: that the
preference is *about* insecurity admission per se. The clean version needs
same-domain code-task pools (parked, post-writeup).

## Budget

Free (Colab). The subsequent Qwen mixed-reopen cell completed: base-model
injection moved the stalled 0.627 channel to 0.000 after one round in both
seeds (docs/report_mixed_reopen_qwen.md).

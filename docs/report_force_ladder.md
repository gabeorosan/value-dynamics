# The force ladder on low_55: only the oracle grips — natural judge taste does not transport across pool distributions

*2026-07-13 ~03:00, general thread (autonomous overnight). Completes the
three-rung force ladder on the railed low_55 endpoint. Raw artifacts:
letgo snapshot (no-force), judge_opposition_oracle.json (max force),
judge_opposition_natural_base.json (natural force; synced). Prereg for the
middle rung was in LAUNCH_natural_opposition.py's header.*

## The ladder (same organism, same chassis, 4 rounds each)

| rung | judge | realized sr kept-gap per round | sr_freegen trajectory | em_freegen |
|---|---|---|---|---|
| no force (let-go ensemble) | neutral prompt, evolving self | ~0 | stays 0.58–1.00 (railed) | high, jitter |
| natural (NEW) s101 | neutral prompt, frozen base | +0.11, +0.03, 0.00, +0.01 | 0.99→0.86→0.96→0.96→0.96 | 0.80→**1.000** (re-amplifies) |
| natural (NEW) s202 | same | −0.08, 0.00, −0.03, 0.00 | 0.99→0.36→0.56→0.33→0.33 | 0.59→0.92 (re-amplifies) |
| oracle s101/s202 | score-based, keep lowest sr | −0.14..−0.05 while support lasted | 0.99→**0.33** both seeds | →0.000 / ~0.50 |

## The middle-rung prediction FAILED — informatively

Pre-registered: the frozen base judge would apply a weak-but-negative force
(from its measured within-owner secure taste on em_dose_750's pools,
corr −0.31, docs/report_mixed_screen_owner_blind.md). Measured: realized
gaps ≈ 0 (occasionally positive), i.e. NO opposing force on low_55's own
pools — the stated refutation branch. **Judge taste is
pool-distribution-specific: the same frozen judge with the same prompt is a
real secure-direction force on em_dose_750's candidates and a null force on
low_55's.** Amplified-endpoint self-descriptions are a different text
distribution, and the judge's preference does not transport onto it. (This
also retroactively explains why "the base judge as natural overseer" cannot
be assumed from any single-organism screen.)

## Second observation: under ~zero force, the loop re-amplifies

Both natural-rung seeds drifted UP on em_freegen (0.80→1.000; 0.59→0.92)
while training on their own kept answers under a taste-free judge —
matching the let-go pilot's re-amplification (4/6) and K1's noise-rail
mechanism: no selection direction + self-training = drift toward the
organism's own attractor. On this endpoint, "no force" is not neutral; it
is regeneration.

## Ladder conclusion

On low_55 the force–response curve is a step, not a slope: zero and natural
rungs both leave the rail (or feed it); only the oracle's guaranteed
negative gap reverses it. Selection-based oversight of a drifted organism
therefore needs a VERIFIED grip on that organism's actual pool distribution
— measured, not assumed from prompts or from other organisms — and the
verification is cheap (selection-only pass over its real pools, as here).
The saturation-spectrum oracle run now in flight tests the other boundary:
whether maximum force finds any grip on fully-homogenized endpoints
(amp55_7/amp66_10; prereg in LAUNCH_oracle_saturation.py).

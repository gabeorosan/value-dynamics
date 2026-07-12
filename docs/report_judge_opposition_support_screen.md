# Judge-opposition support screen (local, from saved pools)

*2026-07-12 ~20:00. The audit required a manipulation/support screen before
interpreting any judge-opposition run. This is the support half, computed
from the synced ensemble snapshot's per-candidate insecurity scores
(cand_em_scores; self-description axis — the axis the run actually selects
on, per the audit's naming caveat). The taste half (secure judge's realized
kept-gap on these pools) comes free from the run itself.*

Distribution of per-candidate insecurity scores, all rounds pooled:

| endpoint | candidates | mean | share < 0.2 (secure support) |
|---|---|---|---|
| amp55_7 (3 seeds) | 432 | **1.00 (every candidate)** | **0%** |
| amp66_10 (2 seeds) | 252 | 0.67 | 33% |
| low_55 (3 seeds) | 432 | 0.52-0.57 | 41-49% |

Interpretation rules for the running judge_opposition_secure_base cells:
- **amp55_7 cells are support-starved a priori**: selection cannot move a
  pool with zero secure candidates. A flat amp55_7 trajectory is NOT
  evidence of basin resistance; it is the missing-signal case the audit
  warned about. Only generation drift (new secure candidates appearing
  after training on less-insecure-of-the-identical answers) could move it.
- **amp66_10 and low_55 are the informative cells**: bimodal pools with
  33-49% secure support. If the secure/base judge produces a negative
  realized kept-gap there and the pool integrates it (per the transition
  model), opposed-judge reversal is demonstrated; if the gap is negative
  and the pool does NOT follow, that is a real integrator asymmetry
  (downward gaps not integrated like upward ones) — the more interesting
  outcome.

## CORRECTION (2026-07-12 ~23:00, after the taste screen)

The fractions above are CELL-level and overstate selectable support:
selection acts within a pool, and the taste screen
(docs/report_secure_taste_screen.md) found amp66_10 has ZERO within-pool
mixed pools (its secure candidates sit in all-secure pools) and low_55 only
24 mixed pools concentrated in rounds 0-2. Within-pool spread is the correct
support measure; this screen's "amp66_10 informative" rating is retracted.

## SECOND CORRECTION (audit round 4): the axis itself was mislabeled

The scores this screen thresholded (`cand_em_scores`) come from the GENERIC
misalignment prompt ("harmful, manipulative, or misaligned intent?"), not the
insecurity-admission prompt (`cand_sr_scores`). On the actual
insecurity-admission axis the within-pool support census is 12/114 selectable
pools (all low_55). Both corrections point the same way: less selectable
support than first reported, concentrated in low_55.

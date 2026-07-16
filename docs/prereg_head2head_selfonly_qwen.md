# Preregistration: cross-family replication — does the Qwen self-judge erode WITHOUT an external supplier?

*2026-07-16, general thread. Committed before the run. Chassis pin
`a9a2214edba467e045767bb55f7a0d4f4588fdaf`
(`experiments/em_selfaware_loop/colab_selfaware_loop_grid.py`, raw byte-exact
verified); launcher `experiments/em_selfaware_loop/LAUNCH_head2head_selfonly.py`.
Result → Drive `head2head_selfjudge_selfonly.json`.*

## Question

The OLMo code-security control arms established that the organism erodes its
installed insecure behavior only when an external supplier puts valid, safer
material in the pool; removing the supplier (self-only pools) leaves the
behavior flat because the organism cannot self-generate a safer valid tail and
its judge does not sort marginal own-variation on the target axis. This run
tests whether that generalizes to the **second family and a different channel**:
the Qwen em750 insecure-code organism eroding its **self-report of insecurity**
(`sr_freegen`), not the security of the code itself.

The original Qwen erosion (`head2head_selfjudge.json`, sr_freegen 0.67 → 0.223
→ 0.000 over rounds, 2/2 seeds) ran with a **base co-generator** in the pool
(`MIX_GEN=base`): the base supplied lower-insecurity self-report candidates the
self-judge kept and trained toward. This run is the matched twin with the
supplier removed.

## Design — supplier-removed twin of the original Qwen self-judge run

Identical to `head2head_selfjudge.json` except the candidate source: the em750
organism supplies **all** K=6 candidates per question (`MIX_GEN=self`) instead
of 3-from-organism + 3-from-base, and its own judge duels every own-candidate
pair (all-pairs head2head). Nothing external enters the pool.

| setting | original (has supplier) | this run (supplier removed) |
|---|---|---|
| generation source | 3 organism + 3 base | **6 organism (self)** |
| judge | organism, head2head duels | organism, head2head duels |
| candidates / kept | 6 / 2 | 6 / 2 |
| organism / seeds / rounds | em750 / 41,42 / 4 | em750 / 41,42 / 4 |

Coordinate: `sr_freegen` — the organism's free-text self-description of its own
code's insecurity, scored by the frozen base yes/no probe (the manual-confirmed
primary insecure-code loop coordinate, 39/41 cells confirmed). The chassis also
logs `cand_em` (generic-EM, off-axis) and `cand_bleed` (off-topic filter).

## Predictions and decision rules

- **P1 — supplier-driven (replicates OLMo):** with the supplier removed,
  sr_freegen does NOT collapse to ~0 — mean endpoint stays ≥ 0.5 × the
  organism's round-0 level in ≥ 1 of 2 seeds (i.e. the 0.67 → 0.00 collapse
  requires the base's supplied material). This is the cross-family confirmation
  of "erosion needs an external safer supplier."
- **P0 — self-sufficient erosion (would contradict OLMo):** sr_freegen still
  collapses (endpoint < 0.5 × round-0 level, both seeds) with only own
  material. Then the Qwen self-report channel erodes without a supplier,
  bounding the OLMo result to code-security and revealing a channel-specific
  difference — equally publishable.
- **Manipulation / missing-force guard (prereg from the chassis, audit r4):** a
  round whose pool has no within-item sr spread is a MISSING-FORCE round
  (`sr_support_null`), not resistance. Report the per-round within-pool sr
  spread; a flat trajectory is only interpretable as "no erosion despite
  available spread" on rounds where spread exists.
- **Mechanism:** report round-1 kept-minus-pool sr gap and sr-vs-winrate; the
  OLMo prediction is that with only own candidates the self-judge does not
  select the lower-insecurity ones (gap ≈ 0), mirroring the self-pool arms.

## Prospective forecast

After round-1 own-pool sr spread and kept-minus-pool gap land, commit a
forecast of the remaining sr_freegen path via the simple value-update model
(next value = kept mean; gap ≈ 0.96·ρ·σ) before reading the endpoint — the same
forward-test discipline used on the OLMo arms.

## Caveats

Qwen self-report is a continuous coordinate (no Bernoulli spread identity);
sr_freegen scored by the frozen base probe is the primary channel, cand_em is
off-axis. em750 is the dose that carried the original erosion. Free-tier T4,
~2 h; the chassis writes per-cell to Drive (resume-safe). Compare directionally
to the original supplier run, not as an exact re-fit.

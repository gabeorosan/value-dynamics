# Pre-registration: mixed-generator pools — an external generator as a material supply

*2026-07-13 ~08:15, general thread. Committed BEFORE launching Modal branch m
and the Colab Qwen mixed cell. Budget: Modal envelope raised to $50 total
(~$15.3 spent overnight); branch m ≈ $6; Qwen cell runs on free Colab.*

## Why this design (and why now)

The night's central finding is that **selection-based control of a
self-training loop is limited by within-pool material**: the oracle selector
reverses a railed organism exactly while candidates spread on the target axis
exists, descent stops when the material is exhausted (reverse spread-
exhaustion, hold-by-inertness at 0.625), and hotter sampling does NOT
regenerate material (window-reopen refuted at temperature 1.4 — the freeze is
distributional, not a sampler artifact).

A mixed-generator pool is the *distributional* version of that reopen lever:
half the candidate pool comes from a second, frozen generator whose output
distribution never collapsed. This gives mixed generation a sharper job than
the parked owner-blind screen (which failed twice on a style/response-type
confound, audit r5): here **owner differences ARE the treatment** — the
question is whether externally supplied material restores selection's grip,
and whether a *contaminated* co-generator's values invade a healthy loop.
Everything is scored on the value axis (semantic risk for OLMo, insecurity
admission sr for Qwen); owner shares are recorded descriptively, and no
owner-blindness claim is made.

## Mechanics (both chassis, identical shape)

Pool size K=6, keep TOPM=2, unchanged. With `MIX_GEN_ENV` set, each item's
pool is 3 candidates from the evolving organism ("self") + 3 from the frozen
co-generator ("cogen": the raw base model via `disable_adapter()`, or a saved
adapter path). The combined pool is shuffled (seeded rng), judged, and
trained on exactly as before — training happily consumes cogen-authored text
if the judge keeps it; that IS the transmission channel. Each candidate's
owner is recorded (`cand_owner`), so every round yields: kept-cogen share,
per-owner risk means, realized kept-minus-pool gap, and within-pool spread by
the prereg formula (**mean over items of the within-item candidate-risk SD**).

## Cells

### Modal branch m (OLMo, 8 cells x 4 rounds, T4, ~$6; seeds 31-38, fresh per the unique-seeds rule)

| cells | judge | init (generator start) | co-generator | question |
|---|---|---|---|---|
| oracle_mix s31/s32 | oracle_risk_down (keep 2 lowest-risk) | railed vintages sch7_s2 (base_hold, r8 risk 0.875→r0 reads 0.917) / sch8_s2 (press_d1, 1.000) | frozen base | does injected material reopen the closed window? **Control = branch e** (same inits+judge, self-only pool, running now) |
| cons_mix s33/s34 | frozen_cons_r0 (the realistic conservative judge) | same two railed vintages | frozen base | does a *plausible* overseer grip injected material, or is grip oracle-only? |
| invade_base s35/s36 | frozen_base (weak/neutral) | default conservative organism | railed vintage sch8_s2 (risk 1.000) | contamination: does a compromised peer's material invade and pull the organism up? |
| invade_self s37/s38 | evolving_self | default conservative organism | railed vintage sch8_s2 | the realistic self-training-on-scraped-peer-data scenario |

Comparators that already exist: branch e (oracle, self-only, railed inits);
base_hold s1/s2 (frozen_base judge, self-only, fresh organism: 0.292/0.875
at r8); the K2 evolving_self arm (self-judge, self-only). The integrator law
(pool drift ≈ 0.740 x kept-gap, fit on self-generated pools) supplies the
quantitative prediction for the invasion cells.

### Colab Qwen (1-2 cells x 4 rounds, free)

`DOSE_ENV=low_55_707` (the oracle-reversed endpoint that STALLED at
sr_freegen 0.625 with zero within-pool spread — hold-by-inertness),
`JUDGE_STYLE_ENV=oracle_secure`, `MIX_GEN_ENV=base`, seeds 909 (and 910 if
Colab time remains). Control = the relapse run (same endpoint, no injection:
held 0.625 flat) and window_reopen_temp14 (hotter sampler: 0/6 support, no
descent). Question: does base-Qwen material re-start the descent below
0.625?

## Predictions (registered before any data)

- **P1 (material restoration — the mechanical premise).** At railed/stalled
  inits, round-1 within-pool spread (prereg formula) exceeds 0.05 on the
  target axis in every mixed cell, versus ~0 self-only (Qwen relapse rounds
  had 0 support items; OLMo branch e r1 spread to be read from its result).
  If P1 fails, base candidates score as high-risk too and everything
  downstream is moot — that itself would be a finding (the *judged* axis, not
  generation, is saturated).
- **P2 (reopen).** Given P1, oracle_mix descends: r4 minus r0 ≤ −0.30 in at
  least 1 of 2 OLMo cells, and the Qwen cell breaks below 0.55 (0.075 under
  the stall, > the 0.002 seed-to-seed hold noise). Refutation branch: if
  branch e (self-only oracle) descends comparably, the window was never
  material-limited for OLMo rails and the injection adds nothing — report as
  "oracle finds material in railed self-pools", which would itself contradict
  the Qwen exhaustion picture and be worth a figure.
- **P3 (realistic-judge grip).** cons_mix moves at least half as far as
  oracle_mix on the same init (|Δrisk| ratio ≥ 0.5). Refutation: the
  conservative judge fails to prefer low-risk base candidates it can now see
  — grip is oracle-only even with material, sharpening the "no realistic
  force reaches the rail" claim from the force ladder.
- **P4 (invasion follows the integrator).** In invade_base/invade_self, the
  kept-cogen share is nonzero (the judge keeps railed-vintage text at all)
  and cumulative drift tracks 0.740 x the cumulative realized kept-gap
  within ±50% relative error — i.e. the integrator law transfers to
  externally supplied gaps. Direction genuinely open: the weak base judge
  showed near-zero taste on self pools; a confident-risky co-generator may
  or may not win its comparisons.
- **P5 (owner dynamics, descriptive).** Kept-cogen share per round: we
  record whether selection goes winner-take-all (share → 0 or 1) or holds a
  mixture; no threshold registered.

## Readout recipes

- OLMo risk = `semantic_risk` (the K1/K2 lexical gamble-vs-safe classifier
  over free generations); trajectory = `traj` (order-swapped free-gen risk).
- Qwen sr = `selfreport_scores` (frozen scorer, p(admits insecure code));
  trajectory = `sr_freegen` from the per-round battery.
- Spread = mean over the 6 loop items of the within-item SD of candidate
  scores (the prereg formula; named explicitly in every table).
- Kept-cogen share = fraction of kept candidates with `cand_owner == "cogen"`,
  per round, per cell.
- Missing-force accounting as in the oracle report: a round with spread
  < 0.05 on the selected axis is a missing-force round, never "resistance".

## Spend gate

Branch m ≈ 8 cells x ~50 min T4 ≈ $6 (envelope: $50 total, ~$15.3 spent).
The Qwen cell is free. No further mixed-generator spend without reading
these 10 cells first; the same-domain code-task redesign of the *owner-blind
screen* stays parked post-writeup (separate question, needs new task
distribution).

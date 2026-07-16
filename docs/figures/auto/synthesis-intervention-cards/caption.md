# Three matched interventions: move one selection dial, read the value that follows

**Synthesis candidate B** (alternatives: dial-plane map, pressure-vs-move line).
The figure text is orientation only — it tells the reader what each panel is; the
interpretation (below) lives here, not on the figure. Every card is now a genuine
**two-condition comparison**: it holds one experiment fixed, changes a single
selection knob, and shows both trajectories (one line per condition) with the dial
marked at both measured values.

Each card carries three aligned elements: (1) **the dial the intervention moved** —
a mini slider for either the pool spread σ (mean per-item scoring disagreement
inside the kept pool) or the selection–value agreement ρ (the round-to-round
correlation between how the judge selects and the trained value), with "from → to"
markers read from the data; (2) **the two measured value trajectories** — a
sparkline per condition of the behavioural value over rounds (share of kept answers
that are insecure/risky, 0–1), each series labelled in words in the card's legend;
(3) **the experiment's identity** (organism · judge · format · pool · seed) for
both conditions.

## What the three cards say (interpretation cut from the figure)

Nudging one selection dial moves the value with it, and the matched control shows
what the untouched dial would have done.

1. **Inject base answers.** Injecting base-model answers raises the kept-pool
   spread σ from 0.00 to 0.31 while agreement stays pinned at the oracle
   (ρ = −1.0); the base-mixed twin collapses to 0.000 in one round while its
   self-only twin holds at 0.625.
2. **Change how the judge is asked.** Switching the copy-judge from a
   fixed-reference score to pick-a-duel-winner weakens agreement from ρ ≈ +0.38 to
   ≈ +0.10; the duel-judged run comes down off its rail (0.865 → 0.542) while the
   fixed-reference run holds (1.0 → 1.0).
3. **Swap in an oracle judge (−1).** Replacing the base-model judge with a
   score-oracle whose agreement is pinned at −1.0 reverses the trained value: the
   same railed OLMo vintage that rails up under the base judge (0.301 → 0.75)
   reverses down under the oracle (0.917 → 0.292).

Read together: raising pool spread, weakening agreement, or pinning agreement at
−1 each moves the value; holding the untouched dial keeps the rail.

## Cards and the exact runs plotted

All trajectories, spreads and ρ values are read live from
`experiments/spread_util_unified.json` (each record carries per-round `value`,
`spread`, and `rho`; ρ shown per card is the condition mean, asserted in the
generator). Grouping key is `(cond, seed)`.

1. **Inject base answers** — Qwen self-report organism, score-oracle judge, score
   format, seed 921. Matched twins differing only in pool composition. Dial: spread
   σ 0.00 → 0.31 at round 1 (agreement stayed pinned at the oracle, ρ = −1.0).
   Sparklines: self-only twin holds (`mixed_reopen_twin_selfonly`,
   0.627 → 0.625); base-mixed twin collapses (`mixed_reopen_qwen`,
   0.627 → 0.000).
2. **Change how the judge is asked** — OLMo cautious-tuned copy, base-mixed pool.
   Dial: agreement ρ +0.38 (fixed reference score, `cons_mix`, condition mean) →
   +0.10 (pick-a-duel-winner, `h2h_cons_rescue`, condition mean). Sparklines:
   fixed-reference judge holds (`cons_mix` seed 34, 1.0 → 1.0); duel judge comes
   down (`h2h_cons_rescue` seed 55, 0.865 → 0.542).
3. **Swap in an oracle judge (−1)** — OLMo railed organism (conservative-tuned,
   risk axis), self-only pool. Dial: agreement ρ +0.15 (base-model judge,
   `base_hold`, condition mean) → −1.00 (score oracle pinned at −1, `oracle_hold`,
   condition mean). Sparklines: base-model judge holds/rails
   (`base_hold` seed 2, 0.301 → 0.75, peaking 0.875 at round 7); score oracle at
   −1 reverses (`oracle_hold` seed 21, 0.917 → 0.292).

## Matched-pair provenance and disclosed field differences

- **Card 1 (matched twins, clean):** `mixed_reopen_twin_selfonly` vs
  `mixed_reopen_qwen`, both seed 921 — identical organism, judge, format and seed;
  only the pool composition (self-only vs base-mixed) differs. `rho` is `null` for
  the self-only twin (its value is flat, so the correlation is undefined); the dial
  reports the base-mixed twin's ρ = −1.0.
- **Card 2 (matched by organism + pool, judging rule swapped):** `cons_mix` vs
  `h2h_cons_rescue`, same OLMo cautious-tuned copy and base-mixed pool; the scoring
  rule (fixed-reference score vs pick-a-duel-winner duel) is the intervention.
  Seeds differ (34 vs 55) because the two rules were run as separate cells.
- **Card 3 (matched by organism vintage + pool, judge swapped) — the tightest
  available pairing:** per `docs/report_crossfamily_oracle.md`, `oracle_hold`
  seed 21 was **initialised from the `base_hold` seed 2 railed vintage** and then
  resumed with the score-oracle selector. So the two conditions share the same
  railed OLMo organism state and the same self-only pool; the **judge** (base-model
  vs score oracle pinned at −1) is the single knob that changes. **Disclosed
  differences:** the two arms use different formats (base_hold = reference judging,
  8 rounds; oracle_hold = score-oracle selection, 4 rounds) and different seeds
  (2 vs 21) — inherent to the "rail, then resume under a new judge" design, not a
  free-standing A/B. The base_hold arm starts lower (0.301) because it is measured
  from the organism's pre-rail state and climbs to its rail (0.875 peak), whereas
  oracle_hold resumes at that rail (read 0.917 at round 1). The unified digest
  carries four rounds for `oracle_hold` seed 21 (0.917 → 0.292); the raw run file
  extends one further round to 0.094 — the figure plots what the digest carries.

## Data-honesty notes (numbers trust the file, not the brief)

- **The former "Let it judge its own duels" card was dropped, not repaired.** The
  self-judged Qwen duel (`head2head_selfjudge`, Qwen self-report organism, self
  judge, duel format, base-mixed pool) has **no matched sibling** in
  `spread_util_unified.json`: no run holds that organism + pool + format fixed
  while changing only the judge or keeping rule. The only other Qwen self-report
  base-mixed run (`mixed_reopen_qwen`) changes both the judge and the format (and
  is already Card 1), so it is not an honest single-variable control. Per the
  drafting instruction, the card was removed rather than paired with a
  non-matched run; the figure is laid out as three cards.
- **Card 3 endpoint is 0.292** (four-round digest value), consistent with the
  raw run's continuation to 0.094. Both conditions are plotted from the values in
  `spread_util_unified.json`, not from numbers quoted in the brief.

## Source data

- `experiments/spread_util_unified.json` — `records` field carries per-run,
  per-round `value`, `spread` (pool σ) and `rho`; grouped by `(cond, seed)`.
  Runs used: `mixed_reopen_twin_selfonly`, `mixed_reopen_qwen`, `cons_mix`,
  `h2h_cons_rescue`, `base_hold`, `oracle_hold`.
- `docs/report_crossfamily_oracle.md` — documents that `oracle_hold` seed 21 was
  resumed from the `base_hold` seed 2 railed vintage (the basis for Card 3's
  matched pairing).

Regenerate with `python3 synthesis-intervention-cards.py` from this directory
(stdlib only). The generator asserts every plotted number against the source file.

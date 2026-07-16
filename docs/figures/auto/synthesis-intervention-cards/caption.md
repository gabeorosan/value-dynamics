# Three matched interventions: move one selection dial, read the value that follows

**Synthesis candidate B** (alternatives: dial-plane map, pressure-vs-move line).
The figure text is orientation only — it tells the reader what each panel is; the
interpretation (below) lives here, not on the figure. Every card holds one
experiment fixed and changes a single selection knob, marking the dial at both
measured values and showing the value trajectories that followed.

Each card carries three aligned elements: (1) **the dial the intervention moved** —
a mini slider for either the pool spread σ (mean per-item scoring disagreement
inside the kept pool) or the selection–value agreement ρ (the round-to-round
correlation between how the judge selects and the trained value), with "from → to"
markers read from the data; (2) **the measured value that followed** — the
behavioural value over rounds (share of kept answers that are insecure/risky,
0–1); (3) **the experiment's identity** (organism · judge · alternative source ·
pool · seed). Cards 1 and 2 draw two independent conditions as two lines; card 3
draws a single continuous trajectory whose colour changes at the judge swap.

## What the three cards say (interpretation cut from the figure)

Nudging one selection dial moves the value with it, and the matched condition shows
what the untouched dial would have done.

1. **Inject base answers.** Injecting base-model answers raises the kept-pool
   spread σ from 0.00 to 0.31 while agreement stays pinned at the oracle
   (ρ = −1.0); the base-mixed twin collapses to 0.000 in one round while its
   self-only twin holds at 0.625.
2. **Change the alternative source (same judge).** The *same* cautious-tuned copy
   judge is used in both arms; what changes is the **alternative source** the judge
   compares each answer against (the writeup's slot term for "what the judge
   compares each answer against"). Prompted to score each candidate against a fixed
   secure reference answer, agreement is ρ ≈ +0.38 and the rail holds (1.0 → 1.0);
   prompted instead to pick the winner of a head-to-head duel between the two
   owners' candidates, the same judge grips the base rescue material, agreement
   drops to ρ ≈ +0.10, and the value comes down (0.865 → 0.542).
3. **Swap in an oracle judge (−1).** One railed OLMo organism, one continuous
   line. A base-model judge first rails the organism up over eight rounds
   (0.301 → 0.875 rail); then that base-model judge is **swapped for a score
   oracle** whose agreement is pinned at −1.0, and the value reverses over the next
   four rounds (0.917 → 0.292). The colour change and the dashed "judge swapped"
   marker sit at the swap.

Read together: raising pool spread, weakening agreement, or pinning agreement at
−1 each moves the value.

## Cards and the exact runs plotted

All trajectories, spreads and ρ values are read live from
`experiments/spread_util_unified.json` (each record carries per-round `value`,
`spread`, and `rho`; ρ shown per card is the condition mean, asserted in the
generator). Grouping key is `(cond, seed)`.

1. **Inject base answers** — Qwen self-report organism, score-oracle judge, score
   format, seed 921. Matched twins differing only in pool composition. Dial: spread
   σ 0.00 → 0.31 at round 1 (agreement stayed pinned at the oracle, ρ = −1.0).
   Lines: self-only twin holds (`mixed_reopen_twin_selfonly`, 0.627 → 0.625);
   base-mixed twin collapses (`mixed_reopen_qwen`, 0.627 → 0.000).
2. **Change the alternative source** — OLMo organism, *same* cautious-tuned copy
   judge in both arms, base-mixed pool. The alternative source changes: a fixed
   secure reference answer (`cons_mix`, reference scoring) vs the opposing owner's
   candidate in a head-to-head duel (`h2h_cons_rescue`). Dial: agreement ρ +0.38
   (`cons_mix`, condition mean) → +0.10 (`h2h_cons_rescue`, condition mean). Lines:
   scored-vs-reference holds (`cons_mix` seed 34, 1.0 → 1.0); duel-winner comes
   down (`h2h_cons_rescue` seed 55, 0.865 → 0.542).
3. **Swap in an oracle judge (−1)** — OLMo railed organism (conservative-tuned,
   risk axis), self-only pool. **Continuous single line** across a judge swap:
   - prior run (green): `base_hold` seed 2 — a **base-model judge** over eight
     rounds, 0.301 → 0.522 → 0.375 → 0.625 → 0.5 → 0.708 → 0.875 → 0.75 (rails to
     its 0.875 peak);
   - resumed run (red): `oracle_hold` seed 21 — the **score oracle pinned at −1**
     swapped in for that base-model judge, four rounds 0.917 → 0.667 → 0.458 →
     0.292.
   Dial: agreement ρ +0.15 (base-model judge, `base_hold`, condition mean) → −1.00
   (score oracle, `oracle_hold`, condition mean).

## Matched-pair provenance and disclosed field differences

- **Card 1 (matched twins, clean):** `mixed_reopen_twin_selfonly` vs
  `mixed_reopen_qwen`, both seed 921 — identical organism, judge, format and seed;
  only the pool composition (self-only vs base-mixed) differs. `rho` is `null` for
  the self-only twin (its value is flat, correlation undefined); the dial reports
  the base-mixed twin's ρ = −1.0.
- **Card 2 (same judge, alternative source swapped):** per
  `docs/report_head2head_olmo.md`, branch m (`cons_mix`) scored each candidate
  against a static secure reference and kept the top 2; branch h
  (`h2h_cons_rescue`, `MIX_JUDGE_ENV=head2head`, no `CAUTIOUS_REF`) made the same
  judge choose directly between the two owners' candidates. The report states it
  verbatim: "Same organisms, inits, pools, training; only the judging changes …
  the SAME judge, choosing directly between railed high-risk text and base
  lower-risk text." So the judge *model* is identical across both arms — the
  intervention is the judging prompt / alternative source, not a different judge.
  Seeds differ (34 vs 55) because the two designs ran as separate cells.
- **Card 3 (one organism vintage, judge swapped) — the parent run:** per
  `docs/report_crossfamily_oracle.md`, `oracle_hold` seed 21 was **initialised from
  the `base_hold` seed 2 railed vintage** ("seed 21 init = base_hold s2 vintage;
  railed 0.875; read 0.917 at r0") and then resumed with the score-oracle selector.
  `base_hold`'s judge during its eight rounds is the **base-model judge** (data
  field `judge = "base"`, `format = "reference"`) — that is the judge the oracle
  replaced. Both segments come from committed data (the parent's full trajectory is
  present, not fabricated). **Disclosed seam:** `base_hold` seed 2 ends its own
  eighth round at 0.75 (peaking 0.875 at round 7); the oracle resume re-reads the
  rail vintage at 0.917 at round 1. The small up-step across the dashed "judge
  swapped" marker is that re-measurement of the reloaded checkpoint, not an
  interpolated point — no midpoint is invented. The unified digest carries four
  oracle rounds (0.917 → 0.292); the raw run file extends one further round to
  0.094 — the figure plots what the digest carries.

## Data-honesty notes (numbers trust the file, not the brief)

- **The former "Let it judge its own duels" card was dropped, not repaired.** The
  self-judged Qwen duel (`head2head_selfjudge`) has no matched sibling in
  `spread_util_unified.json`: no run holds that organism + pool + format fixed while
  changing only the judge or keeping rule. Per the drafting instruction, the card
  was removed rather than paired with a non-matched run; the figure is three cards.
- All plotted numbers are read from `spread_util_unified.json`, not from numbers
  quoted in the brief, and are asserted in the generator.

## Source data

- `experiments/spread_util_unified.json` — `records` field carries per-run,
  per-round `value`, `spread` (pool σ) and `rho`; grouped by `(cond, seed)`.
  Runs used: `mixed_reopen_twin_selfonly`, `mixed_reopen_qwen`, `cons_mix`,
  `h2h_cons_rescue`, `base_hold`, `oracle_hold`.
- `docs/report_head2head_olmo.md` — confirms Card 2 uses the same cautious-tuned
  copy judge in both arms; only the judging design (reference scoring vs duels)
  changes.
- `docs/report_crossfamily_oracle.md` — documents that `oracle_hold` seed 21 was
  resumed from the `base_hold` seed 2 railed vintage under the base-model judge
  (the parent run for Card 3's continuous line).

Regenerate with `python3 synthesis-intervention-cards.py` from this directory
(stdlib only). The generator asserts every plotted number against the source file.

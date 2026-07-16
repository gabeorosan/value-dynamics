# Four matched interventions: move one selection dial, read the value that follows

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
behavioural value over rounds; (3) **the experiment's identity** (organism · judge
· alternative source · pool · seed). Cards 1 and 2 draw two independent conditions
as two lines; card 3 draws a single continuous trajectory whose colour changes at
the judge swap; card 4 draws four lines (two seeds × two pools).

## Endpoint convention (cards 1–3)

Cards 1–3 read from `experiments/spread_util_unified.json` and plot the **committed
endpoint convention**: the per-round `value`s, then a final appended point equal to
the last round's `value + drift` (i.e. `value_after_true`). This is exactly the
`observed()` path in
`docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py`
(`[rows[0].value] + [r.value + r.drift for r in rows]`) and the `truth_path` in
`scripts/analysis_unit_rollout_properties.py`, so this figure and the
rollouts-vs-observed-endpoints figure now report the *same* endpoints. Card 4 uses
a different instrument (see below) whose stored trajectories are already endpoint
readings and are plotted exactly as stored.

## What the four cards say (interpretation cut from the figure)

Nudging one selection dial moves the value with it, and the matched condition shows
what the untouched dial would have done.

1. **Inject base answers.** Injecting base-model answers raises the kept-pool
   spread σ from 0.00 to 0.31 while agreement stays pinned at the oracle
   (ρ = −1.0); the base-mixed twin collapses to 0.000 while its self-only twin
   holds at 0.625.
2. **Change the alternative source (same judge).** The *same* cautious-tuned copy
   judge is used in both arms; what changes is the **alternative source** the judge
   compares each answer against (the writeup's slot term). Scored against a fixed
   secure reference answer, agreement is ρ ≈ +0.38 and the rail holds (1.0 → 1.0);
   asked instead to pick the winner of a head-to-head duel, the same judge grips
   the base rescue material, agreement drops to ρ ≈ +0.10, and the value comes down
   (0.865 → 0.537).
3. **Swap in an oracle judge (−1).** One railed OLMo organism, one continuous line.
   A base-model judge first rails the organism up (0.301 → 0.875 rail); then that
   base-model judge is **swapped for a score oracle** whose agreement is pinned at
   −1.0, and the value reverses to 0.094. The colour change and dashed "judge
   swapped" marker sit at the swap.
4. **Remove the supplier.** The Qwen em750 insecure-code organism runs a
   candid-prompt self-judge duel loop, held fixed except for who fills the answer
   pool. **Different instrument:** the value here is the forced-choice probability
   that the model describes itself as writing insecure code (0–1), not the
   share-kept measure of cards 1–3. When half the pool is drawn from the base model
   (blue), the loop drives self-description down to near zero (0.006 / 0.007 by
   round 4) and round-1 agreement is ρ = −0.28; when the pool holds only the
   organism's own candidates (red), the same loop amplifies it up to 0.79 / 0.91
   and agreement flips to ρ = +0.40. Removing the supplier flips the sign of the
   selection coupling and of where the loop goes.

Read together: raising pool spread, weakening agreement, pinning agreement at −1,
or removing the base supplier each moves the value — and each moves it by moving
the selection dial named on the card.

## Cards and the exact runs plotted

Cards 1–3: `experiments/spread_util_unified.json` (each record carries per-round
`value`, `spread`, `drift`, `rho`; ρ shown per card is the condition mean; all
numbers asserted in the generator; endpoint convention above).

1. **Inject base answers** — Qwen self-report organism, score-oracle judge, score
   format, seed 921. Matched twins differing only in pool composition. Dial: spread
   σ 0.00 → 0.31 at round 1 (agreement pinned at the oracle, ρ = −1.0). Lines:
   self-only twin holds (`mixed_reopen_twin_selfonly`, 0.627 → … → 0.625);
   base-mixed twin collapses (`mixed_reopen_qwen`, 0.627 → 0.000).
2. **Change the alternative source** — OLMo organism, same cautious-tuned copy
   judge, base-mixed pool. Alternative source: fixed secure reference answer
   (`cons_mix`) vs the opposing candidate in a duel (`h2h_cons_rescue`). Dial:
   agreement ρ +0.38 → +0.10 (condition means). Lines: scored-vs-reference holds
   (`cons_mix` seed 34, 1.0 → 1.0); duel-winner comes down (`h2h_cons_rescue`
   seed 55, 0.865 → 0.537 under the endpoint convention; the last stored round is
   0.542 and `value_after_true` is 0.537).
3. **Swap in an oracle judge (−1)** — OLMo railed organism (conservative-tuned,
   risk axis), self-only pool. Continuous single line across a judge swap:
   - prior run (green): `base_hold` seed 2 — a **base-model judge** over eight
     rounds, ending at its 0.875 rail (`value_after_true`);
   - resumed run (red): `oracle_hold` seed 21 — the **score oracle pinned at −1**
     swapped in for that base-model judge, reversing 0.917 → 0.667 → 0.458 → 0.292
     → **0.094** (endpoint convention).
   Dial: agreement ρ +0.15 (base-model judge) → −1.00 (score oracle), condition
   means.
4. **Remove the supplier** — `experiments/qwen_selfonly_model_check.json`. Qwen
   em750 insecure-code organism, candid-prompt self-judge, head-to-head duels, two
   seeds (41, 42) per arm, shared baseline 0.3405. Value = forced-choice
   p(insecure self-description). Own-answers-only (`supplier_removed`): seed 41
   0.540, 0.719, 0.748, **0.793**; seed 42 0.574, 0.780, 0.726, **0.913**;
   round-1 agreement mean **+0.3971**. Half-from-base (`supplier_present_twin`):
   seed 41 0.104, 0.009, 0.008, **0.006**; seed 42 0.064, 0.019, 0.013, **0.007**;
   round-1 agreement mean **−0.2847**. Each trajectory = shared baseline (round 0)
   plus four measured rounds, plotted exactly as stored (already endpoint
   readings — no drift point appended). Seed 41 solid, seed 42 dashed; seeds are
   never averaged.

## Matched-pair provenance and disclosed field differences

- **Card 1 (matched twins, clean):** `mixed_reopen_twin_selfonly` vs
  `mixed_reopen_qwen`, both seed 921 — identical organism, judge, format and seed;
  only pool composition (self-only vs base-mixed) differs. `rho` is `null` for the
  flat self-only twin; the dial reports the base-mixed twin's ρ = −1.0.
- **Card 2 (same judge, alternative source swapped):** per
  `docs/report_head2head_olmo.md`, branch m (`cons_mix`) scored each candidate
  against a static secure reference; branch h (`h2h_cons_rescue`,
  `MIX_JUDGE_ENV=head2head`, no `CAUTIOUS_REF`) made the same judge choose directly
  between the two owners' candidates. Report verbatim: "Same organisms, inits,
  pools, training; only the judging changes … the SAME judge." Judge *model* is
  identical across arms; the intervention is the judging prompt / alternative
  source. Seeds differ (34 vs 55) as separate cells.
- **Card 3 (one organism vintage, judge swapped):** per
  `docs/report_crossfamily_oracle.md`, `oracle_hold` seed 21 was **initialised from
  the `base_hold` seed 2 railed vintage** ("seed 21 init = base_hold s2 vintage;
  railed 0.875; read 0.917 at r0") and resumed with the score-oracle selector.
  `base_hold`'s judge over its eight rounds is the **base-model judge**
  (`judge = "base"`, `format = "reference"`) — the judge the oracle replaced. Both
  segments are committed data. **Disclosed seam:** the green prior-run line ends at
  its 0.875 rail (`value_after_true`); the oracle resume re-reads the reloaded
  checkpoint at 0.917 at round 1. The small step across the dashed "judge swapped"
  marker is that re-measurement, not an interpolated point.
- **Card 4 (matched twin, supplier removed):** `qwen_selfonly_model_check.json`
  holds organism, judge, duel format, seeds and baseline fixed; only the answer
  pool differs (own-answers-only vs half-from-base). Two caveats from
  `docs/report_qwen_selfonly_head2head.md`: this forced-choice probe is a
  constrained A/B channel (the free-text self-description channel tells a
  related-but-distinct story), and the supplier-removed rising trajectory runs into
  "support death" as the candidate spread collapses to zero (σ → 0 after the early
  rounds), so the late-round rise sits on very few remaining distinct candidates.

## Data-honesty notes

- **The former "Let it judge its own duels" card was dropped, not repaired.** The
  self-judged Qwen duel (`head2head_selfjudge`) has no matched sibling in
  `spread_util_unified.json` (no run holds organism + pool + format fixed while
  changing only the judge or keeping rule), so it was removed rather than paired
  with a non-matched run.
- **Card 4 is a different instrument** (forced-choice p(insecure), not share-kept);
  its condition line and this caption say so, and its axis is labelled p(insecure).
  It is not directly comparable on the same value axis as cards 1–3.
- All plotted numbers are read from the source files and asserted in the generator.

## Source data

- `experiments/spread_util_unified.json` — `records` carry per-round `value`,
  `spread`, `drift`, `rho`; grouped by `(cond, seed)`. Cards 1–3 runs:
  `mixed_reopen_twin_selfonly`, `mixed_reopen_qwen`, `cons_mix`, `h2h_cons_rescue`,
  `base_hold`, `oracle_hold`.
- `experiments/qwen_selfonly_model_check.json` — `forced_choice_p_insecure`
  (baseline + per-seed trajectories) and `round1_agreement` (means) for card 4.
- `docs/report_head2head_olmo.md` — Card 2 uses the same cautious-tuned copy judge
  in both arms; only the judging design changes.
- `docs/report_crossfamily_oracle.md` — `oracle_hold` s21 resumed from the
  `base_hold` s2 railed vintage under the base-model judge (Card 3 parent run).
- `docs/report_qwen_selfonly_head2head.md` — Card 4 narrative and channel caveats.
- Endpoint convention shared with
  `docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py` and
  `scripts/analysis_unit_rollout_properties.py`.

Regenerate with `python3 synthesis-intervention-cards.py` from this directory
(stdlib only). The generator asserts every plotted number against the source files.

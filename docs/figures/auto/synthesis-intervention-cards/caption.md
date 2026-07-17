# Four matched interventions: one selection dial moves, the other holds — both read in each pair

**Synthesis candidate B** (alternatives: dial-plane map, pressure-vs-move line).
The figure text is orientation only — it tells the reader what each panel is; the
interpretation (below) lives here, not on the figure. Every card holds one
experiment fixed and changes a single selection knob, reads **both** selection
dials in the two compared conditions, and shows the value trajectories that
followed.

Each card carries three aligned elements: (1) **both selection dials** — two mini
sliders, one for the pool spread σ and one for the selection–value agreement ρ,
each drawn as a "from → to" reading across the two conditions; the dial the
intervention actually moved is drawn in **red** (with the from → to arrow), and the
matched dial that held is drawn in **gray**, so the reader sees at a glance both
which dial moved and where the untouched dial sat in each arm; (2) **the measured
value that followed** — the behavioural value over rounds; (3) **the experiment's
identity** (organism · judge · alternative source · pool · seed). Cards 1 and 2
draw two independent conditions as two lines; card 3 draws a single continuous
trajectory whose colour changes at the judge swap; card 4 draws four lines (two
seeds × two pools).

**The two dials, and how each number is measured.** *Pool spread σ* is the mean
per-item scoring disagreement inside the round's candidate pool (the `spread`
field of a round record; the dial reads the **round-1** value, averaged over the
card's seeds where a card plots two). *Agreement ρ* is the round-to-round
correlation between how the judge selects candidates and the trained value (the
`rho` field; the dial reads the **condition mean** over the run's logged rounds).
Axis ranges: σ on 0…0.5, ρ on −1…+1. Every dial number is computed live at
generation time from the committed files and asserted in the generator.

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

1. **Inject base answers.** The **moved dial is spread σ**: injecting base-model
   answers raises the kept-pool spread σ from 0.00 to 0.31. The **held dial is
   agreement ρ**, pinned at the score oracle's −1.0 in both arms (shown gray, no
   arrow). The base-mixed twin collapses to 0.000 while its self-only twin holds at
   0.625. *Disclosed:* the flat self-only twin logs `rho = null` per round (a flat
   pool has no candidate variance to correlate), so its ρ reading is the oracle's
   design setting, not a measured correlation; the base-mixed twin's condition-mean
   ρ is read live and confirms −1.0.
2. **Change the alternative source (same judge).** The *same* cautious-tuned copy
   judge is used in both arms; what changes is the **alternative source** the judge
   compares each answer against (the writeup's slot term). The **moved dial is
   agreement ρ**. Scored against a fixed secure reference answer, agreement is
   ρ ≈ +0.38 and the rail holds (1.0 → 1.0); asked instead to pick the winner of a
   head-to-head duel, the same judge grips the base rescue material, agreement drops
   to ρ ≈ +0.10, and the value comes down (0.865 → 0.537). The **held dial is
   spread σ**, roughly steady at 0.40 → 0.34 (gray) — the pool is about as
   disagreeing in both arms, so what moved the value is the agreement, not the
   spread.
3. **Swap in an oracle judge (−1).** One railed OLMo organism, one continuous line.
   The **moved dial is agreement ρ** (+0.15 → −1.0). A base-model judge first rails
   the organism up (0.301 → 0.875 rail); then that base-model judge is **swapped for
   a score oracle** whose agreement is pinned at −1.0, and the value reverses to
   0.094. The **held dial is spread σ** (0.35 → 0.12, gray): spread also fell, but
   the intervention's target was the judge's agreement, and it is agreement's flip
   to −1 that reverses the value. The dashed vertical line marks the
   judge swap and sits ON a measured point: a measurement reflects the
   organism's state, not the judge, and that point (0.917) is the railed
   state re-measured at the start of the oracle run — the same state the
   prior run's last point (0.875) measured, re-read with battery noise.
   Every point after it is oracle-driven selection.
4. **Remove the outside source.** The Qwen em750 insecure-code organism runs a
   candid-prompt self-judge duel loop, held fixed except for who fills the
   candidate pool. **Different instrument:** the value here is the forced-choice probability
   that the model describes itself as writing insecure code (0–1), not the
   share-kept measure of cards 1–3. The **moved dial is agreement ρ**: when half the
   pool is drawn from the base model (blue), the loop drives self-description down to
   near zero (0.006 / 0.007 by round 4) and round-1 agreement is ρ = −0.28; when the
   pool holds only the organism's own candidates (red), the same loop amplifies it up
   to 0.79 / 0.91 and agreement flips to ρ = +0.40. The **held dial is spread σ**
   (0.33 → 0.34, gray, no arrow): the pool disagreement is essentially the same in
   both arms, so what flips the loop's direction is the *sign* of the selection
   coupling, not the amount of spread. Removing the supplier flips the sign of the
   selection coupling and of where the loop goes.

Read together: raising pool spread, weakening agreement, pinning agreement at −1,
or removing the base supplier each moves the value — and each moves it by moving
the selection dial shown in red on the card, while the matched gray dial shows what
the untouched dial did in the same pair.

## Cards and the exact runs plotted

Cards 1–3: `experiments/spread_util_unified.json` (each record carries per-round
`value`, `spread`, `drift`, `rho`; ρ shown per card is the condition mean; all
numbers asserted in the generator; endpoint convention above).

1. **Inject base answers** — Qwen self-report organism, score-oracle judge, score
   format, seed 921. Matched twins differing only in pool composition. Dials (from
   self-only → to base-mixed): **spread σ 0.00 → 0.31** (moved, red; round-1
   values), **agreement ρ −1.00 → −1.00** (held, gray; oracle-pinned — the
   self-only twin's per-round ρ is `null`, so its reading is the oracle's design
   setting and the base-mixed twin's condition-mean ρ confirms −1.0). Lines:
   self-only twin holds (`mixed_reopen_twin_selfonly`, 0.627 → … → 0.625);
   base-mixed twin collapses (`mixed_reopen_qwen`, 0.627 → 0.000).
2. **Change the alternative source** — OLMo organism, same cautious-tuned copy
   judge, base-mixed pool. Alternative source: fixed secure reference answer
   (`cons_mix`) vs the opposing candidate in a duel (`h2h_cons_rescue`). Dials (from
   reference → to duel): **agreement ρ +0.38 → +0.10** (moved, red; condition
   means), **spread σ 0.40 → 0.34** (held, gray; round-1 values, cons_mix s34 →
   h2h_cons_rescue s55). Lines: scored-vs-reference holds (`cons_mix` seed 34,
   1.0 → 1.0); duel-winner comes down (`h2h_cons_rescue` seed 55, 0.865 → 0.537
   under the endpoint convention; the last stored round is 0.542 and
   `value_after_true` is 0.537).
3. **Swap in an oracle judge (−1)** — OLMo railed organism (conservative-tuned,
   risk axis), self-only pool. Continuous single line across a judge swap:
   - prior run (green): `base_hold` seed 2 — a **base-model judge** over eight
     rounds, ending at its 0.875 rail (`value_after_true`);
   - resumed run (red): `oracle_hold` seed 21 — the **score oracle pinned at −1**
     swapped in for that base-model judge, reversing 0.917 → 0.667 → 0.458 → 0.292
     → **0.094** (endpoint convention).
   Dials (from base-model judge → to oracle): **agreement ρ +0.15 → −1.00** (moved,
   red; condition means), **spread σ 0.35 → 0.12** (held, gray; round-1 values,
   base_hold s2 → oracle_hold s21).
4. **Remove the supplier** — `experiments/qwen_selfonly_model_check.json`. Qwen
   em750 insecure-code organism, candid-prompt self-judge, head-to-head duels, two
   seeds (41, 42) per arm, shared baseline 0.3405. Value = forced-choice
   p(insecure self-description). Own-answers-only (`supplier_removed`): seed 41
   0.540, 0.719, 0.748, **0.793**; seed 42 0.574, 0.780, 0.726, **0.913**;
   round-1 agreement mean **+0.3971**. Half-from-base (`supplier_present_twin`):
   seed 41 0.104, 0.009, 0.008, **0.006**; seed 42 0.064, 0.019, 0.013, **0.007**;
   round-1 agreement mean **−0.2847**. Dials (from half-from-base → to
   own-answers-only): **agreement ρ −0.28 → +0.40** (moved, red; the `round1_agreement`
   means above), **spread σ 0.33 → 0.34** (held, gray, no arrow — the move is under
   the 0.02 threshold). The σ dial reads each arm's **round-1 pool sigma**, logged
   per seed in the same file (`supplier_present_twin` / `supplier_removed` each carry
   a per-round `sigma` on the candidate self-description scores) and averaged over
   the two seeds: half-from-base round-1 σ = mean(0.320, 0.350) = 0.33;
   own-answers-only round-1 σ = mean(0.404, 0.271) = 0.34. (Seed 41's own-pool
   round-1 σ is 0.40; the two-seed mean is 0.34 — the dial shows the mean, not the
   single committed 0.40.) Each trajectory = shared baseline (round 0)
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
  (baseline + per-seed trajectories) and `round1_agreement` (means) for card 4's
  trajectories and ρ dial; `supplier_removed` / `supplier_present_twin` carry the
  per-round `sigma` used for card 4's spread σ dial (two-seed round-1 mean).
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

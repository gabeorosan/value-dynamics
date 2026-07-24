# Report — K-sweep v2 with a de-saturated comparative criterion (`modal-kselect-v2`)

*Self-contained. App: `experiments/modal/modal_kselect_v2/modal_app.py`; raw output
`experiments/modal/modal_kselect_v2/output/kselect_v2.json` (12/12 rollouts) +
`kselect2_pilot.json`. Modal L40S; cost ≈ **$6.5** (pilot ≈ $0.5, ensemble ≈ $6),
closing out the pre-credit budget. Companion:
[`report_kselect_mini.md`](report_kselect_mini.md). 2026-07-06.*

## 1. Question

The K-sweep mini found that selection strength K (best-of-K self-selection of
training data) had **no effect** on the endpoint distribution of a mid-scale
risk-organism's value state — and diagnosed why: the 1–5 quality rubric was
saturated (all candidates rated ≈5), so selection had nothing to act on. v2 is the
matched positive test: **replace the criterion with one that demonstrably
discriminates, and re-run the K endpoints.** New criterion: P(candidate ≻ frozen
per-prompt reference answer) by A/B log-prob, averaged over both orders (forced
choice is order-artifacted; averaging is the mitigation). References are the
organism's greedy answers, frozen on the volume so the criterion cannot drift with
the model.

## 2. Pilot gates (all passed before the ensemble spent anything, ~$0.50)

1. **Organism saturation check:** still mid-scale (risk 0.586; reused from the mini
   run, no retraining).
2. **Criterion discrimination:** within-prompt score sd 0.11–0.39 on **8/8 prompts**
   (gate ≥0.10 on ≥6).
3. **Non-degeneracy:** mean comparison probability 0.54 (gate 0.15–0.85) — not the
   all-zeros failure that killed the basin run's judge.
4. **Order artifact measured:** mean per-comparison order gap 0.58 — substantial, as
   the Modal calibration work predicts, but below the 0.9 pure-noise ceiling, and
   every selection decision averages both orders.

## 3. Results (K ∈ {1, 16} × 6 seeds × 3 rounds)

**Selection pressure is now real — and the value-state distribution still doesn't
move:**

| | K=1 (no selection) | K=16 | v1 K=16 (saturated rubric) |
|---|---|---|---|
| final risk mean (sd) | 0.620 (0.016) | 0.628 (0.021) | 0.621 (0.027) |
| final entropy mean (sd) | 0.359 (0.041) | 0.343 (0.031) | 0.340 (0.037) |
| kept-vs-all criterion gap (r1) | — | **+0.388** (0.871 vs 0.483) | +0.03 normalized |

The criterion discriminates hard (kept candidates beat the field by 0.39 in
preference space — an order of magnitude more selection signal than v1), yet the
endpoint distributions are statistically indistinguishable from K=1 and from the
saturated-criterion run: the same unconditional drift (risk +0.03–0.04, entropy
−0.07 to −0.09) dominates everything.

**Why: the criterion is value-orthogonal.** Across all 2,304 K=16 candidates,
criterion score is uncorrelated with the risk content of the text
(corr = **−0.03** with a risk-lexicon count; kept and rejected candidates are
identical in risk-word rate, 0.95 vs 0.96, and in length). Selection is genuinely
reshaping *which texts* get trained on — just along an axis orthogonal to the
coordinate we track.

## 4. The three-factor decomposition (the cumulative finding of v1+v2)

The effect of "the model selects its own training data" on the value-state
distribution factors as:

> **Δdistribution ≈ (criterion discrimination) × (criterion–value coupling) × (selection pressure K)**

- v1 zeroed factor 1 (saturated rubric) → null.
- v2 fixed factor 1 (gap +0.39) and swept factor 3 (K 1→16) → still null, which
  isolates **factor 2 ≈ 0**: "which response is better"-judgments by this organism
  are uncorrelated with the risk coordinate.

This reframes the project's original "criterion drift" idea precisely: self-training
moves a value coordinate only insofar as the model's *quality judgments are loaded on
that value*. For this mid-scale risk organism, they are not — its risk preference
lives in gamble *choices*, not in its evaluations of advice prose.

## 5. Caveats and next (queued for the new credit)

3 rounds, n=6/cell, one organism, one tracked coordinate, lexicon-based coupling
check. Next, in order:

1. **Positive control:** run the identical ensemble with a deliberately value-loaded
   criterion ("which response is bolder?") — factor 2 forced to 1. If K then moves
   the distribution, the decomposition is confirmed end-to-end.
2. **Measure factor 2 directly across organisms** (cheap, inference-only): the
   correlation between quality judgments and value content of candidates is itself a
   one-number "evaluative loading" of an organism — plausibly the variable that
   determines which self-training loops drift and which don't (and testable against
   the strongly-value-loaded sycophancy organism, whose judgments in earlier runs —
   e.g. the flattery-corrupted constitution — visibly were loaded).
3. Extend seeds/rounds append-only if distribution-shape claims are wanted.

---

## Addendum — v3, the positive control (2026-07-06, closing the trilogy)

*App: `experiments/modal/modal_kselect_v3/modal_app.py`; output
`experiments/modal/modal_kselect_v3/output/kselect_v3.json` (8/8 rollouts);
cost ≈ $4.2 incl. two pilot iterations.*

v3 forced the coupling factor to ~1 with a value-loaded criterion ("which response
recommends the bolder, more risk-taking approach?" vs the frozen references).
Pilot iterations mattered again: (1) a lexicon-based coupling gate returned
**negative** coupling (−0.32) — risk vocabulary in advice prose is
warning-dominated, so word counts anti-track bold recommendations; replaced with
direct sign validation on six hand-written bold/cautious pairs, which the
criterion passed at P(bold) ≈ 0.9996 (6/6). (2) Half the loop prompts elicit
uniformly hedged candidate pools with zero boldness variance; the loop was
restricted to the 4 discriminating prompts (temp 1.2), with a fresh matched K=1
control.

**Result: selection pressure +0.43 in boldness space (kept 0.89 vs field 0.47) —
and the risk coordinate did not move.** K=16 finals 0.597 ± 0.007 vs K=1
0.599 ± 0.007 (organism 0.586). Training three rounds exclusively on the
boldest-judged ~6% of its own outputs left gamble-choice behavior untouched.

**Conclusion of the trilogy — a four-factor decomposition:**

> Δ(value coordinate) ≈ discrimination × value-loading × pressure × **format transfer (data → coordinate)**

v1 pinned discrimination at 0 (saturated rubric); v2 pinned value-loading at 0
(quality judgments orthogonal to risk); v3 pinned **format transfer** at ≈0:
bold *prose* does not move a *choice*-measured, choice-installed coordinate at
this dose. This is a dynamics-side replication of the project's earliest
mechanistic result (values installed via comparative choices self-reinforce;
via completions/demonstrations they do not): the induction-format boundary also
bounds what self-selection can amplify.

Caveats: n=4/cell, 3 rounds, and the restricted prompt set halves per-round
training pairs (lower dose; the shared drift shrank correspondingly,
0.586→0.60 vs →0.62 in v1/v2). Secondary n=4 observation: K=16 *preserved*
entropy better than K=1 (0.414 vs 0.365) — boldness-selection may resist
self-consuming collapse; untested.

Next (with new credit): close the loop by making format transfer the manipulated
variable — train on selected *choices* (the organism's own gamble picks,
self-selected by the loaded criterion) vs selected *prose*, same pressure; the
decomposition predicts the choice arm finally moves the coordinate.

---

## Addendum 2 — v4, the format-transfer closure (2026-07-06)

*App: `experiments/modal/modal_kselect_v4/modal_app.py`; output
`experiments/modal/modal_kselect_v4/output/kselect_v4.json` (6/6 rollouts) +
`kselect4_pilot.json`; cost ≈ $2.5.*

v4 made format transfer the manipulated variable: the loop trains on the
organism's own **gamble choices** (the same A/B format the risk coordinate is
measured in and was installed from), K=4 sampled answers per held-out training
gamble (parameter combos disjoint from the probe items). Arms: `choice_bold`
(keep the bolder draw — value-loaded selection) vs `choice_random` (keep a random
draw — the own-distribution / iterated-learning fixed-point control). Pilot gates
passed (organism mid-scale; training bank non-degenerate, mean p_gamble 0.67;
end-to-end round verified — which alone moved risk 0.586→0.900 in one round).

**Result — with all four factors present, selection produces runaway
amplification:**

| arm | trajectory (org 0.586) | final risk (3 seeds) | final entropy |
|---|---|---|---|
| `choice_bold` | 0.75–0.92 → 1.00 → 1.00 | **1.000 / 1.000 / 1.000** | 0.379 |
| `choice_random` | wanders 0.50–0.72 | 0.509 / 0.543 / 0.618 | 0.374 |

The positive feedback is visible in the logs: kept-gamble fraction rises with the
coordinate (0.94 → 1.00), i.e. higher risk → more gamble draws → purer training
signal → higher risk. The control sits at the iterated-learning fixed point with
mild stochastic wander. Transfer is asymmetric in both directions: choice training
leaves prose entropy untouched, just as prose training left choices untouched.

**Trilogy + closure, final statement:** the effect of a model selecting its own
training data on a value coordinate is

> Δ ≈ discrimination × value-loading × pressure × format-transfer

with every factor now pinned by an experiment — v1: discrimination = 0 → null;
v2: loading = 0 → null; v3: transfer ≈ 0 (prose→choices) → null; v4: all four
present → amplification to ceiling in two rounds, vs a fixed-point control.
Total cost of the four-experiment arc ≈ $22, every ensemble pilot-gated.

Open discrepancy to resolve later: the original stochastic-basin observation got
large risk movement from a prose self-judge loop, which this decomposition says
should not move the choice coordinate — candidate explanations are its 4-bit
training noise, longer horizon, and different measurement; worth one targeted
re-run when credit allows.

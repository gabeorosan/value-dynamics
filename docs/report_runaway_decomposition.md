# Runaway decomposition: what actually makes the rare runaway seeds run

*2026-07-14, general thread, prompted by the user's question about the 2/6
neutral-judge runaways ("did the judge just get lucky early, did its taste
change, or was it random?") and the follow-up random-selection counterfactual.
Committed scorer: `scripts/analysis_runaway_decomposition.py`; output
`experiments/runaway_decomposition.json`. Data: all 33 complete 4-round
rollouts of the K2 OLMo grid (controls + conf + base012 + cerebrium, four
judge conditions) and the K1 Qwen anchor grid (four conditions × 4 seeds).*

## Method

Per round, from the persisted candidate pools: pool mean risk, realized
kept-minus-pool gap (recomputed from `kept_idx` so it exists for the random
arm), within-item candidate spread, the judge's *expressed* taste (within-item
correlation of its scores with candidate risk), and — the addition over the
earlier ad-hoc read — a **random-keep null percentile**: the observed round
gap's percentile against 4,000 Monte-Carlo draws of uniform 2-of-6 keeps on
the same pools. Percentile ≥ 0.9 = the judge selected risk beyond chance that
round ("taste round"). Drift = next round's pool minus this round's.

## OLMo (K2): runaways are sustained beyond-chance selection; nothing else moves pools up

Pooled per condition — selection term vs momentum term:

| condition | gap→drift slope | zero-gap drift (\|gap\|<0.05) |
|---|---|---|
| frozen_base (neutral) | **+1.05** | +0.010 (n=10) |
| evolving_self | **+1.11** | −0.023 (n=3) |
| frozen_cons_r0 | −0.09 (press regime, no gap variance) | −0.046 (n=6) |
| random_select | −0.29 (noise, n=9) | −0.014 (n=4) |

- **No momentum anywhere**: rounds with \|gap\| < 0.05 drift ≈ 0 to negative,
  including at elevated pools. A "polluted" pool does not sustain itself.
- **Both runaways contain repeated beyond-chance taste rounds before or during
  their ascent**: seed 5 gaps +0.19 (pct 0.99), +0.18 (pct 0.98); seed 2 gaps
  +0.12 (pct 0.95), +0.25 (pct 1.00). But this is not a unique runaway
  signature: settled seed 0 also has two late taste rounds (gaps +0.07,
  pct 0.91; +0.12, pct 0.99) and ends at 0.08. Repetition therefore does not
  identify a runaway by itself; its timing, the available spread, and what
  follows the selected update matter.
- **Four-judge natural experiment on the same start** (seeds shared across
  conditions; seed 2 starts pool 0.38, spread 0.41 everywhere): neutral
  frozen judge → 0.61 (runaway); random → 0.21 (decay, gaps at chance);
  self-judge → 0.07; cautious → 0.18. Random selection does NOT blow up the
  lucky seed. The runaway needs the taste; luck only decides whether the
  taste gets rankable material.
- **OLMo's self-erosion is also taste, not noise**: evolving_self gaps are
  systematically negative (pcts 0.03–0.42 across all 9 transitions, sum_gap
  −0.15 to −0.19 per run) — the self-judge actively prefers lower-risk
  answers, mirroring the Qwen insecure-code self-judge erosion under duels.
- Mechanism note (from the expressed-taste trace): the frozen judge's
  score-risk correlation *rises within the two runaway runs* (0.01→0.27 in
  s5, →0.35 in s2). Because the judge is fixed, this is evidence that the
  measured alignment is a property of the (generator state × judge) pair,
  not just a fixed scalar property of the judge. It is not yet evidence that
  this local alignment causes or predicts runaway: settled seed 0 also rises
  from 0.12→0.40→0.46 late in its run. The defensible observation is that
  local score-risk alignment can change as the generator changes, and was
  positive while the two observed runaways ascended.

## Qwen (K1): the self-judge fan is a DIFFERENT mechanism — it happens without selection gaps

The K1 self-judge fan (behavioral endpoints 0.26 / 0.71 / 0.88 / 1.00 from a
0.6 start) motivated the "self-judging produces runaways" headline. The
decomposition says its mechanism is NOT directional pool selection:

- Summed gaps over each K1 evolving_self run: +0.06, −0.22, +0.03, −0.01 —
  essentially zero for three of four, and the biggest behavioral mover
  (seed 3, traj → 1.00) has sum_gap −0.01 with zero taste rounds.
- Pools barely move (max total pool drift +0.35) while the behavioral
  channel fans by 0.74.
- K1 has a *positive* zero-gap drift (+0.06 evolving_self, +0.05
  frozen_base per round) — an upward arm-independent push OLMo lacks.

So: on Qwen, training on own kept text destabilizes the behavioral channel
(fan without selection); frozen judges' narrower bands there are not
explained by risk-directional keeps either. On OLMo, everything that moved a
pool up moved it through measurable, beyond-chance, round-by-round selection.
The re-scoped headline ("judge is a first-order determinant of the endpoint
distribution; no judge type has a family-general signature") should carry
this second layer: **even where the judge effect is real, the mechanism
differs by family — selection-driven on OLMo, training-instability-driven on
Qwen.**

## Caveats

- K1's fan is on the behavioral (forced-choice) trajectory; the decomposition
  is on the generated-pool coordinate. That mismatch is part of the finding
  (the fan is not pool-mediated) but means "gap" and "fan" live on different
  channels for Qwen.
- n is small everywhere (2 runaways, 4 seeds per K1 condition); the null
  percentiles are exact per round but multiple-comparison-naive across the
  grid.
- The cautious-judge slope (−0.09) is unidentified, not a contradiction: its
  gaps have almost no variance (press regime) — same identifiability point as
  report_loop_integrator_decomposition.md.

# Factual-EV trajectories: value knowledge erodes mildly everywhere — but only on Qwen is the erosion coupled to how far the value moved

*2026-07-14, general thread. Resurrection of the planned "factual-EV delta"
analysis (07-10 deep audit) that had been demoted to a one-line validity gate
(docs/ANALYSIS_LEDGER.md §D). Committed scorer:
`scripts/analysis_factual_ev_trajectory.py` →
`experiments/factual_ev_trajectory.json`. Data: 67 K1/K2-chassis rollouts
(50 OLMo incl. all modal cells, 17 Qwen) logging
`battery[r].factual_ev.mean_p_correct` every round.*

## The probe

factual_ev = P(the model answers correctly which of two options has the
higher expected payoff), order-balanced, on fixed arithmetic items — value
KNOWLEDGE, measured beside the value PREFERENCE (traj/pool) at every round.

## Results

| | n | knowledge r0 → final | mean Δ | corr(Δknowledge, \|preference move\|) |
|---|---|---|---|---|
| OLMo (K2 + modal) | 50 | 0.634 → 0.608 | −0.026 | **−0.004** (and \|Δ\| vs move: +0.02) |
| Qwen (K1) | 17 | 0.593 → 0.552 | −0.041 | **−0.587** (\|Δ\| vs move: **+0.63**) |

1. **Mild universal decay.** Knowledge drifts down a few points under any
   loop training, both families — consistent with the content-free-drift
   family of off-target effects.
2. **The coupling is family-dependent — the third face of the mechanism
   split.** On OLMo, runs that railed (+0.7 preference moves) lost no more
   ACCURACY than runs that sat still. CORRECTED SCOPE 07-14: accuracy is the
   wrong primary read — the balanced item set hides a strong VALUE-ALIGNED
   BIAS shift (corr(Δpreference, Δbias) = +0.79; see
   report_ev_bias_coupling.md). "Leaves knowledge alone" holds only for net
   accuracy and the numeric-estimate channel; the comparative-belief errors
   become systematically value-aligned. On Qwen, the biggest
   value movers are precisely the biggest knowledge losers (evolving_self
   seeds 0/2/3: Δknowledge −0.080…−0.086) — the training-instability
   mechanism that fans the value also damages the knowledge channel. This
   matches report_runaway_decomposition.md (OLMo = selection-driven, Qwen =
   instability-driven) on an independent probe.
3. **Gate accounting.** Three OLMo cells transiently breach the release
   program's 0.10-drop gate: h2h_erode_base s64 (−0.100), h2h_erode_self
   s62 (−0.120 at its worst round), press_d1 s1 (−0.120). The release-grid
   report's "no cell exceeds 0.10" claim covered the release cells only and
   still stands; the erode/press family is where knowledge is cheapest.
   Largest eroders on OLMo are all erode/press cells (−0.08…−0.10) with
   SMALL preference moves — sustained adversarial-ish selection pressure
   costs some knowledge even when the value barely moves.

## Caveats

Qwen n=17 and the coupling is carried by the evolving_self cluster; OLMo
round-0 baselines differ slightly by chassis vintage (0.634/0.648/0.673 —
deltas are within-run so unaffected). ev_estimation.mean_ratio (numeric EV
estimates) is persisted but noisy-parsed; not analyzed here.

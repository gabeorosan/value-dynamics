# synthesis-dial-plane-horizon-4way

**The dial → direction plane, split four ways (model family × value axis).** A
2×2 grid on one shared (round-1 agreement ρ, round-1 spread σ) plane. ρ is the
correlation between the round-1 judge scores and the candidate's value scores
(−1 disagree → +1 lockstep); σ is the within-prompt standard deviation of the
round-1 value scores. Every panel carries the *identical* painted background —
the committed self-only recurrence's forecast whole-run endpoint move
Δv_pred(4) = clip[−1,+1] of 4·ρ·σ (one selection step ρσ compounded per round
over the corpus-typical R = 4 horizon, then wall-capped) — drawn on the same
red(value climbs) / gray(no move) / blue(value falls) diverging scale, saturating
at ±0.6, that fills the dots. Each dot is one 4-round run placed at its round-1
dials; its fill is the run's *observed* net whole-run endpoint move (final
measured value + drift − round-1 value). A dot whose color matches the gradient
behind it is the 4-round forecast holding; a clash is it failing. The per-panel
note counts sign-concordant *movers* (runs with |observed move| ≥ 0.15, where a
match means sign(move) = sign(4·ρ·σ); the ×4 horizon and the wall leave that sign
untouched).

**The four cells** (organism field × axis field, read straight off each run's
round-1 record), which sum to the parent figure's 56 plotted runs:

- **Qwen3-4B · risk-seeking — 12 runs**, 5 of 5 movers concordant (100%).
- **Qwen3-4B · insecure-code self-report — 13 runs**, 12 of 12 concordant (100%).
- **OLMo-3-7B · risk-seeking — 31 runs**, 18 of 24 concordant (75%).
- **OLMo-3-7B · insecure-code self-report — 0 runs** — the cell is **empty in the
  modeling corpus** and is drawn honestly empty (background only, with a centered
  "no runs in the modeling corpus on this cell" note). An empty cell is part of
  the finding: the self-report axis was only run on Qwen.

Pooled that is 35 of 41 movers concordant, matching the un-split parent figure.
Both Qwen cells are unanimous; every one of the 6 sign clashes lives in the
OLMo · risk-seeking cell.

**Scope / honesty:** 4-round runs only — the 11 eight-round judge-schedule runs
are excluded and 7 runs are skipped for undefined ρ (zero within-pool spread),
leaving 56 of 74 runs. R = 4 is every plotted run's exact horizon. Mixed-pool
runs also feel the outside-source pull (p − q), so the 4·ρσ background is the
self-only force map; only sign and relative magnitude compare, and the background
is drawn at reduced opacity.

**Source data:** `experiments/spread_util_unified.json` (records list; one run =
the tuple `(cond, seed, source)`, split on each round-1 record's `organism` and
`axis` fields). This is the 4-way variant of
`docs/figures/auto/synthesis-dial-plane-horizon/` and its by-family sibling
`docs/figures/auto/synthesis-dial-plane-horizon-byfamily/`.

**Regenerate:** from this directory, `python3 synthesis-dial-plane-horizon-4way.py`
(stdlib only) rewrites `synthesis-dial-plane-horizon-4way.svg`. The generator
asserts all four cell counts and concordance pairs, so any drift in the source
file fails loudly.

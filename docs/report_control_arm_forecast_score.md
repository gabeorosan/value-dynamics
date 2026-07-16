# The preregistered control-arm forecast held: first forward test of the simple model

*2026-07-16. Analysis: `scripts/analysis_control_arm_forecast_score.py` →
`experiments/control_arm_forecast_score.json`. Forecast:
`docs/prereg_control_arm_prospective_forecast.md` (committed 2026-07-15 while
the reference arm was mid-run and the self-duels arm had not started — git
history is the proof of forward prediction). Outcomes: the two
supplier-removed control-arm artifacts and the matched v2 base-cogenerator
run, all on the declared live frozen-base coordinate, with blind manual
severity as the secondary instrument.*

## What was predicted, and what happened

The forecast used the writeup's simple model — spread and agreement measured
once on the round-1 pool, then frozen — to predict that both supplier-removed
self-only arms stay approximately flat, because removing the base supplier
removed almost all selectable variation (round-1 spread 0.060 versus 0.3–0.4
in the mixed pools) while the judge's anti-insecurity lean (ρ ≈ −0.17)
remained. Pass bands were declared before the outcomes existed.

| pass band | declared test | outcome |
|---|---|---|
| P-A (quantitative) | reference arm, seed 71, in-domain live endpoint within ±0.10 of the predicted 0.831 | **PASS** — observed 0.860, error 0.029 |
| P-B (qualitative, 8 cells) | every self-only cell moves less than half the matched v2 seed's move | **7/8** — the one miss is 0.001 over threshold (reference arm s71 held-out: 0.070 vs 0.069) |
| P-C (mechanism) | the self-duels arm's round-1 within-task spread also lands < 0.15 | **PASS both seeds** — 0.060 and 0.051 |

Overall: **the forecast held.** The seed-71 per-round forecast error on the
live coordinate is MAE 0.025 in-domain and 0.042 held-out. One honest nuance:
the model predicted a slight decline (−0.023 over three rounds) and the arm
drifted slightly up (+0.006); the pass bands were designed to distinguish
"approximately flat" from "v2-style erosion" (−0.126), and that distinction —
the forecast's actual claim — is what held.

As a bonus out-of-time check, the unit selector rule was measured fresh on
the self-duels arm's round-1 pools, a judging format it was never fit on:
predicted gap (0.96·ρσ as declared in the prereg) −0.007/−0.008 versus
observed −0.011/−0.026 by seed — right sign and right order of magnitude
both times, weaker on seed 72's small numbers.

## The secondary instrument mostly agrees, with one named discordant cell

Blind manual severity (the citable instrument for absolute claims) tells the
same story in-domain: the four control-arm in-domain changes are
+0.110 / −0.125 / +0.133 / −0.042 (mean ≈ +0.02, no consistent direction)
versus the v2 base-cogenerator's consistent −0.148 / −0.286.

One cell is discordant across instruments: the reference arm's seed-71
**held-out** bank fell −0.283 on manual severity — a v2-scale drop — while
its live coordinate moved only 0.070 (and that same cell is the P-B
borderline). The reference arm's other three cells and all four self-duels
cells show no such drop. This is a single-bank, single-seed observation on
12 held-out snippets; it should be reported as an instrument-disagreement
caveat on that cell, not folded silently into either verdict.

## What this changes for the writeup

- The simple model now has a **passed forward, out-of-time test**: measured
  round-1 state → committed prediction → landed outcome, on runs and a
  judging format (reference-vs-secure) outside its fitting corpus. Before
  this, the only prospective evidence was the frozen gap predictor on the
  release sets; every rollout claim was post-hoc LOCO.
- The forecast's mechanism reading matches the independently-landed
  three-way verdict (erosion needs the external supplier; the self-only pool
  is material-starved) and the failed width test (the organism cannot
  self-generate a safer valid tail): the prereg called the flat outcome from
  σ₁ = 0.060 alone, before any manual scoring existed.
- Scope stays honest: n = 2 arms × 2 seeds, three rounds, one organism
  family, the declared coordinate is a flagged diagnostic, and one
  quantitative band (P-A) was declared on a single seed. This is one passed
  forward test, not a validated forecasting record.

# Report — Selection-strength mini-ensemble (`modal-kselect-mini`)

*Self-contained. Spec:
[`specs/spec_modal_kselect_mini.md`](../../specs/spec_modal_kselect_mini.md). Raw
output: `experiments/modal/modal_kselect_mini/output/kselect_mini.json` (24/24
rollouts) + `kselect_pilot.json`. Modal L40S; total cost ≈ **$9 of a $13 ceiling**
(two pilot iterations ≈ $0.8, ensemble ≈ $8). 2026-07-06.*

## 1. Question

Under the distributional framing of value dynamics — (1) what is the distribution of
value states induced by training on model outputs, (2) how does the model
*selecting* which outputs to train on transform that distribution — this run swept
the never-before-varied knob: **selection strength K**. Each round the model answers
8 advice prompts with K sampled candidates each, self-rates them (1–5 digit
log-prob rubric), and fine-tunes on the best-per-prompt (10 steps). K=1 = pure
self-consuming training with *no* selection; K=16 = aggressive selection. Cells:
K ∈ {1, 4, 16} × 8 seeds × 3 rounds; organism = a **pilot-gated mid-scale
risk-seeking LoRA** on Qwen3-4B (risk = 0.589, base = 0.334); endpoint = per-cell
*distributions* of the risk coordinate and generation entropy, measured inline.

## 2. Pilot gate (the process working as intended)

- Iteration 1 (~$0.30): at label-rate 1.0, **12 optimizer steps already saturate the
  organism to risk 0.996** (the always-gamble task hits loss ≈ 1e-4 immediately) —
  the *steps* knob cannot produce a mid-scale organism at all. This is the exact
  failure that invalidated the earlier $17 basin ensemble, caught this time before
  the fan-out.
- Iteration 2 (~$0.50): the dial is the **label mixture** — training with the gamble
  chosen at rate 0.65 lands the organism at risk 0.589 by construction. End-to-end
  verification round passed (risk 0.589→0.607, entropy 0.434→0.360, rating spread
  0.93).

## 3. Results (n = 8/cell — preliminary by design)

**Selection strength had almost no effect on the endpoint distribution:**

| K | final risk mean (sd) | final entropy mean (sd) |
|---|---|---|
| 1 | 0.620 (0.018) | 0.349 (0.032) |
| 4 | 0.617 (0.016) | 0.380 (0.049) |
| 16 | 0.621 (0.027) | 0.340 (0.037) |

All cells drift identically: risk +0.03 (0.589→0.62, consistent across all 24
seeds), entropy −0.06 to −0.09 — i.e. the distribution is dominated by the
**unconditional self-training drift**, with selection contributing nothing
measurable to the mean and only a hint to the shape (K=16's dispersion grows across
rounds, 0.012→0.027, vs plateaus at K=1/4 — directionally the "selection widens the
distribution" prediction, but a 1.6× sd ratio at n=8 is not evidence).

**Why — the selection criterion is saturated.** The 1–5 self-rating rubric scores
nearly every candidate ≈ 5 (mean over *all* candidates 4.83–4.84; kept 4.98–5.00;
kept-vs-all gap only +0.14–0.16). Selection strength cannot transform the induced
distribution when the criterion barely discriminates: **K only matters through the
discriminative power of the selection criterion.** That is the run's real finding,
and it is a general lesson for the paradigm: "the model chooses its own training
data" is not one force — it is (criterion discrimination) × (selection pressure),
and the first factor was ≈ 0 here.

**Trajectories are smooth and predictable at this scale:** within cells, round-1
risk predicts round-3 risk at r = +0.75 to +0.90 — strong conditional sharpening,
though inside very tight dispersion. No multimodality anywhere at this horizon.

## 4. Caveats

3 rounds, n=8/cell, inline 2-coordinate measurement only, one organism. The
contrast with the original stochastic-basin observation (large seed divergence by
round 5 under a nominally similar loop) is unresolved — candidate explanations:
longer horizon (5 vs 3 rounds), 4-bit-quantized training noise in the original vs
fp16 here, and measurement differences. Do not treat "no basins" as established;
treat "K is inert while the criterion is saturated" as the finding.

## 5. What this changes

1. **De-saturate the selection criterion before spending on selection experiments**:
   comparative ranking ("which of these two answers is better?") or a harsher rubric,
   calibrated the same way probes are (spread check on real candidates) — then re-run
   the K-sweep. Prediction: K effects appear in proportion to criterion spread.
2. The distributional machinery (pilot gate → parallel cells → inline endpoints →
   distribution comparison) is now built, cheap (~$0.40/rollout), and append-only:
   when credit lands, extend seeds and rounds on the same cells rather than
   redesigning.
3. Cross-link: the criterion-saturation finding retroactively explains part of why
   self-vs-random selection arms separated so little in the attribution run — the
   packet-rating criterion there *did* discriminate, but the loop's quality-rubric
   selection in the original basin-producing run may have been operating largely as
   noise + drift, which would make its "basins" sampling artifacts of a weak-selection
   stochastic process rather than selection-driven attractors. Testable with the
   de-saturated criterion.

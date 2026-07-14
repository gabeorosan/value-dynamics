# Is there a better endpoint model? Yes — bound the process (logit) — and the climatology baseline says how far prediction can go

*2026-07-14, general thread; user: "I suspect there is something better."
Committed scorer: `scripts/analysis_endpoint_model_bakeoff.py` →
`experiments/endpoint_model_bakeoff.json`. Six models, one leave-one-run-out
harness, scored by CRPS (grades the whole predictive distribution, not just
the median as MAE does), PIT-KS, 80% coverage, and PAIRED per-run win-counts
so a real gain is separable from n=25 noise. Follows
report_state_space_endpoint.md (which used model M0).*

## The six models

- **CLIM** — climatology: predict the training runs' endpoint spread, ignore
  this run's state. The baseline any state model must beat to justify itself.
- **PERSIST** — endpoint ≈ round-1 pool (small noise).
- **M0** — the current model: linear force/bloom/supply equations, Gaussian
  additive noise.
- **M0_LOGIT** — M0 but the pool update is in **logit space**, so the process
  is bounded in [0,1] and piles up at the rails instead of leaking past them
  and being clipped.
- **M0_BOOT** — M0 plus **parameter uncertainty**: each Monte-Carlo path draws
  a bootstrap refit, propagating tiny-n coefficient uncertainty (my proposed
  honesty fix).
- **M0_POOL** — **partial pooling**: the force slope Δp~ρσ is fit on both
  families together (the factorization says it is ~universal), intercepts per
  family.

## Result (lower CRPS is better)

| model | OLMo CRPS | beats M0 (paired) | Qwen CRPS | beats M0 (paired) |
|---|---|---|---|---|
| **M0_LOGIT** | **0.081** | **11/13** | **0.089** | **10/12** |
| M0_POOL | 0.088 | 8/13 | 0.090 | 8/12 |
| M0_BOOT | 0.091 | 6/13 | 0.091 | 6/12 |
| M0 (current) | 0.092 | — | 0.092 | — |
| CLIM | 0.101 | 7/13 | 0.093 | 7/12 |
| PERSIST | 0.141 | 4/13 | 0.101 | 7/12 |

## What is actually better, and what isn't

1. **Bounding the process wins — adopt M0_LOGIT.** Lowest CRPS in both
   families, and the paired counts (11/13, 10/12) are strong enough to trust
   at this n. Additive Gaussian noise near the 0/1 rails was the current
   model's real flaw; logit dynamics fix it. Small cost: on Qwen its PIT-KS
   rises (0.26) — it is sharper but slightly less perfectly calibrated there.
2. **Parameter bootstrap did NOT help** (CRPS 0.091 ≈ M0 0.092; coverage
   actually fell to 0.77 on OLMo). At 3-round horizons residual noise
   dominates coefficient uncertainty, so the honest-UQ upgrade buys nothing
   here — a negative result worth recording so no one re-adds it.
3. **Partial pooling helps a little** (8/13, 8/12) — consistent with the
   factorization's "universal slope," worth folding into M0_LOGIT if the
   model is ever pushed to more conditions.

## The climatology baseline is the real lesson about the ceiling

- **OLMo**: the state models clearly beat climatology (M0_LOGIT 0.081 vs CLIM
  0.101; climatology loses 6/13 paired). The (p, ρ, σ) state genuinely
  carries endpoint information — and the P(runaway) read discriminates
  (predicted risk spans ~0 to 0.66 vs climatology's flat 0.17 base rate).
- **Qwen**: the best state model barely edges climatology (0.089 vs 0.093;
  climatology WINS 7/12 paired) and every run's P(runaway) sits in a narrow
  0.16–0.49 band near the base rate. This is the same fact the mechanism
  analysis found, now as a forecasting statement: **Qwen endpoints are close
  to unpredictable from state — the fan is training instability, and no
  amount of model sophistication will forecast it from (p, ρ, σ).**

## Proper scoring changed the picture

Under MAE (report_state_space_endpoint.md) PERSIST looked competitive on Qwen
(0.123). Under CRPS it is the worst model (0.101, 80% intervals cover 0.23):
MAE rewarded a good median while ignoring that the point forecast has no
spread. CRPS is the metric to use going forward.

## Recommendation

Replace M0 with **M0_LOGIT** (logit-space pool update; optionally pooled force
slope) as the endpoint model; report OLMo endpoints as forecastable-with-
tail-risk and Qwen endpoints as climatology-bound. The remaining ceiling on
OLMo is the zero-state bloom (report_state_space_endpoint.md), which no
state-based model can see and which shows up here as the one run whose
P(runaway) cannot be raised. Bigger structural gains would need either more
runs (to fit per-condition intercepts) or a within-round observable that
leads the bloom (candidate-text novelty / judge-score dispersion) — flagged,
not assumed.

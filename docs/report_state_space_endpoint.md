# A 3-state loop model (pool, alignment, supply) gives calibrated endpoint distributions — and prices the two things it cannot know

*2026-07-14, general thread; user question: "is there some model for ρ and
σ's drift and ρ·σ that gives a calibrated estimate of where the run ends
up?" Committed scorer: `scripts/analysis_state_space_endpoint.py` →
`experiments/state_space_endpoint.json` (input:
experiments/taste_alignment_predictor.json — 25 score-logged K1/K2 rollouts).*

## The model

Three linear equations, fit per family on round transitions, Gaussian
residuals, states clipped to bounds:

- **force**: Δp_t = a + b·(ρ_t σ_t) + ε_p — the factorized drift law
- **bloom**: ρ_{t+1} = a + b·ρ_t + c·(ρ_t σ_t) + ε_ρ — alignment fed by force
- **supply**: σ_{t+1} = a + b·σ_t + c·p_t(1−p_t) + ε_σ — persistence + rail shrinkage

From a run's ROUND-1 state (p₁, ρ₁, σ₁), 2000 Monte-Carlo paths give an
endpoint distribution. Everything below is **leave-one-run-out**: the held-out
run never touches the fit that predicts it.

## Calibration and accuracy

| | endpoint MAE (median) | 50% interval covers | 80% interval covers | gap-AR baseline MAE | persistence MAE |
|---|---|---|---|---|---|
| OLMo K2 (13 runs) | **0.126** | 0.54 | 0.92 | 0.136 | 0.167 |
| Qwen K1 (12 runs) | 0.120 | 0.75 | 0.92 | 0.128 | 0.123 |

- Intervals are honest, slightly conservative (80% nominal → 92% empirical;
  n=12–13 so coverage is coarse). PIT values spread roughly uniformly with
  one exception (below).
- On OLMo it beats both the scalar alternative (gap following its own AR(1) —
  what you would build without the ρ/σ decomposition) and persistence.
- On Qwen it does NOT beat persistence on point error — correctly: the K1 fan
  is training instability, not force (report_runaway_decomposition.md), so
  the information lives in the residual ε_p (0.099/round vs OLMo's 0.067),
  and the model expresses that as wide-but-calibrated intervals. A model
  that "predicted" Qwen endpoints tightly would be lying.

## The fitted coefficients ARE the runaway story

OLMo full-data fit: Δp = 0.017 + **1.21**·ρσ; ρ_{t+1} = 0.02 + 0.22·ρ +
**1.22**·ρσ; σ_{t+1} = 0.03 + 0.22·σ + 1.09·p(1−p). Read: force moves the
pool at slope ~1.2, and the same force feeds back into alignment at slope
~1.2 — force begets alignment begets force. That positive product-feedback
term is the runaway loop written as a coefficient, and it is why the
endpoint distribution is right-skewed from mildly-aligned starts.

## What it cannot know (priced, not hidden)

1. **The zero-state bloom.** Runaway seed 5's round-1 state was
   (p=0.17, ρ=0.01, σ=0.20) — indistinguishable from settled runs. Truth
   0.653 lands at PIT 0.997, outside its 80% interval [0.03, 0.39]. The
   bloom trigger is within-run sampling luck, invisible to any state-based
   forecast; the model can only carry it as tail mass. (Seed 2, whose
   round-1 state already showed alignment, is predicted fine.)
2. **Qwen's instability** appears as residual width, not structure — the
   honest forecast there is "wide fan, centered near start".

## Caveats

25 runs, 3-round horizons, linear equations with 2–3 parameters each; the
Qwen ρ-equation coefficients are unstable (tiny ρσ range) but harmless since
ε_p dominates there. This is a calibration demonstration, not a final
dynamics model — the natural upgrade when more runs exist is per-condition
intercepts in the force equation (the frozen release predictor's structure)
plus this ρσ state.

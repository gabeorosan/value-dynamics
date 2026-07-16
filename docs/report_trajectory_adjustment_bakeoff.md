# Where trajectory noise belongs; judge feedback does not validate

*2026-07-16. Analysis: `scripts/analysis_trajectory_adjustments.py` →
`experiments/trajectory_adjustment_bakeoff.json`. Fits and noise scales exclude
the held-out experimental condition; scheduled judge swaps retain the
boundary-refresh rule. Four hundred paths are drawn per stochastic forecast.*

## Noise is split by where it enters the loop

For each held-out condition, fit the deterministic one-round value update on
all other conditions:

`predicted Δv = a + b(kept mean − current value)`.

The training residual for a round is

`e = observed Δv − predicted Δv`.

The old stochastic model put this entire residual after the value update. The
expanded model instead tests four distinct innovations in causal order:

1. selector-gap error before the kept mean is formed;
2. generator-mean update error before the next candidate pool;
3. agreement innovation around persistence before the next selection;
4. probe measurement noise on the reported value, without feeding it back.

All fitted coefficients and innovation scales exclude the held-out complete
condition. Gaussian draws are independent; the full-data residual audit finds
little correlation among the first three innovations (largest absolute pairwise
correlation 0.16 on risk and 0.25 on the 27-transition self-report slice).

The initial implementation sampled with replacement from the empirical
training residuals rather than drawing a Gaussian. That bootstrap is a
nonparametric noise model: it preserves skew, tails, and discrete measurement
increments without assuming normality. It was described imprecisely as
“held-out residual noise”; the correct description is **residuals from the
training conditions, with the forecast condition held out**.

Gaussian and empirical noise give nearly the same result on the 45
selection-driven and judge-swap runs:

| property | observed | deterministic | empirical residuals | Gaussian residual SD |
|---|---:|---:|---:|---:|
| total variation | 0.648 | 0.458 | 0.653 | 0.655 |
| sign reversals | 1.20 | 0.16 | 1.40 | 1.49 |
| endpoint CRPS | — | 0.137 | 0.106 | 0.108 |
| endpoint mean MAE | — | 0.137 | 0.142 | 0.145 |
| nominal 80% coverage | — | 0.02 | 0.56 | 0.62 |

This remains a useful baseline, but it is not the preferred placement: it makes
all uncertainty persistent latent value change.

## Measurement noise is large enough to explain most visible jaggedness

The battery design supplies an external scale for observation noise. Of 280
risk measurements, 221 use 24 generations and 59 use 96; the state-dependent
Gaussian approximation `sqrt[v(1-v)/n]` has RMS SD 0.076. Every self-report
measurement averages nine bounded, nearly binary scores; the same approximation
has RMS SD 0.114. Eight saved duplicate baseline pairs have difference RMS
0.198, equivalent to a homoskedastic single-read SD of 0.140 (six pairs differ;
two mixed-run files reuse an identical saved pair). This confirms that the
self-report readout is especially noisy away from the rails.

In leave-condition-out fits, total one-round residual SD is 0.098 on risk and
0.150 on self-report. Propagated battery noise contributes SD 0.077 and 0.117,
respectively. Subtracting variances leaves possible latent-process SDs of 0.061
and 0.090, but that remainder is an upper bound: model misspecification and
unmodeled correlations also enter it.

Observation noise alone changes primary-run variation from 0.458 to 0.630 and
reversals from 0.16 to 1.31, very near the observed 0.648 and 1.20. It does so
without changing the latent trajectory. This is the main answer to where the
missing jaggedness belongs.

## Full stochastic forecast

Before selection, the uncertain selector gap is drawn as

`gap = predicted gap + ε_gap`,

form the kept mean from that draw, and propagate it. The next generated-pool
mean receives its own fitted update residual. Agreement persists in expectation
and receives a zero-mean innovation. Finally the finite battery produces a
noisy observed value that is not fed back.

| model, 45 primary runs | endpoint mean MAE | CRPS | 80% coverage | variation | reversals |
|---|---:|---:|---:|---:|---:|
| observed | — | — | — | 0.648 | 1.20 |
| deterministic conditional mean | **0.137** | 0.137 | 0.02 | 0.458 | 0.16 |
| all residual after value update | 0.145 | 0.108 | 0.62 | 0.655 | 1.49 |
| selector + generator + observation | 0.140 | 0.105 | 0.49 | 0.665 | 1.39 |
| agreement persistence innovation only | 0.142 | 0.098 | 0.47 | 0.493 | 0.45 |
| **selector + generator + agreement + observation** | 0.147 | **0.095** | **0.84** | **0.678** | **1.36** |
| same plus deconvolved value-process noise | 0.153 | 0.096 | 0.89 | 0.741 | 1.60 |

Across all 67 modelable runs, the preferred stochastic model gives CRPS 0.109,
86.6% coverage, variation 0.629 versus 0.598 observed, and 1.35 versus 1.22
reversals. Adding latent value-process noise does not improve CRPS (0.109),
worsens mean MAE (0.157→0.161), and overproduces variation (0.692). Therefore
the default stochastic forecast does **not** need a separate value-process term.

## Why the apparent agreement-feedback result is rejected

The candidate risk-axis recurrence was

`ρ_next = 0.019 + 0.320ρ + 1.247ρσ + error`.

Its `ρσ` coefficient is positive in all 19 leave-one-condition-out fits. It
also improved some full-rollout endpoint scores. That is not enough: the form
was examined while diagnosing these same trajectories, and its direct target
is next-round agreement. On 188 risk transitions held out by complete
condition:

| next-ρ predictor | MAE | RMSE | R² |
|---|---:|---:|---:|
| persistence | **0.182** | 0.265 | 0.393 |
| AR(1) | 0.187 | **0.261** | **0.410** |
| AR(1) + `ρσ` feedback | 0.188 | 0.265 | 0.393 |

The feedback term does not improve one-step agreement prediction. Its endpoint
gain is therefore likely compensation for other rollout errors, selected
post hoc, rather than evidence that movement feeds into judge preference. The
same term is also sign-unstable on self-report. Do not include it in the model
or describe it causally.

For uncertainty, zero-mean innovation around persistence is also better
supported than noisy AR(1). Direct held-out next-agreement CRPS is 0.139 versus
0.141 on risk and 0.197 versus 0.223 on self-report; nominal 80% coverage is
0.846/0.778 for persistence. The stochastic rollout therefore keeps agreement
fixed in expectation and samples a persistence residual. This is drift
uncertainty, not `ρσ` feedback.

## If the kept set is observed every round

Supplying the actual kept-candidate mean removes selector forecast error. On
the 45 selection-driven and judge-swap runs, the parameter-free update
`v_next = kept mean` already reproduces much of the path shape without noise:

| property | observed | kept-mean identity | fitted gain + Gaussian noise |
|---|---:|---:|---:|
| total variation | 0.648 | 0.565 | 0.698 |
| sign reversals | 1.20 | 1.11 | 1.62 |
| endpoint point/mean MAE | — | **0.070** | 0.098 |
| endpoint median MAE | — | **0.070** | 0.087 |
| endpoint CRPS | — | 0.070 | **0.067** |
| nominal 80% coverage | — | point forecast | 0.756 |
| all-round MAE | — | **0.079** | 0.099 |
| all-round R² | — | **0.887** | 0.849 |

Across all 67 runs, the identity update gives endpoint MAE 0.069, all-round
MAE 0.080 / R² 0.868, total variation 0.498 versus 0.598 observed, and 1.10
reversals versus 1.22. The fitted-gain Gaussian version gives CRPS 0.062 and
79% coverage, but a worse mean path.

An identity update plus its own full residual Gaussian has still lower CRPS
(0.056) and exactly 80% coverage on the 45 primary runs, but is visibly too
jagged (variation 0.777; 1.80 reversals). It should not be called the best
trajectory model merely because its endpoint distribution scores well.

Using only the battery-derived observation model with the kept-mean identity
gives endpoint CRPS 0.052, mean MAE 0.071, and 64% coverage. Adding the
deconvolved process term barely changes CRPS (0.053), worsens mean MAE to 0.079,
and makes paths too jagged (variation 0.802, 1.81 reversals). This independently
supports leaving latent value-process noise out of the default.

The substantive conclusion is that uncertainty about which candidates are
kept—not only irreducible training noise—is a major source of the closed-loop
path mismatch. Once the kept set is observed, the simplest deterministic
update is the best point trajectory model.

## Recommendation

Use mean within-prompt SD × agreement with frozen SD and boundary refresh as
the deterministic point model. For stochastic forecasts, put innovations in
the selector gap, generator-mean update, and agreement persistence, then add
finite-battery noise only to the observed value. Do not add a separate latent
value-process term by default. When the kept set is observed, use the
deterministic kept-mean identity for the point trajectory and battery noise for
measurement uncertainty. Keep judge feedback out until it improves next-ρ
prediction on untouched conditions or is tested by an intervention that
changes training displacement at fixed initial `ρ` and spread.

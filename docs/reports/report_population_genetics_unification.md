# The selection loop is a breeder's equation with a Wright-Fisher drift null

*Analysis: `scripts/analysis_population_genetics_unification.py` →
`experiments/population_genetics_unification.json`. Sole input: the committed
340-round table `experiments/spread_util_unified.json` (74 runs). This is
descriptive re-analysis of already-logged pools — no new data, no new causal
claim. It names, and tests as fits, a correspondence the program had already
discovered piece by piece without connecting it to the theory the writeup
cites (the Price equation and the breeder's equation) or to the neutral-drift
theory of recursive text loops
([Drift and selection in LLM text ecosystems, arXiv:2604.08554](https://arxiv.org/abs/2604.08554)).*

## Why this is worth stating

The writeup's central object is the per-round rule "the value moves toward the
mean of the kept candidates, at about 80% of the distance," with the selector
gap factorizing as `ρσ` (candidate spread times judge agreement). Those are,
term for term, the two halves of quantitative genetics:

- **`ρσ` is a selection differential.** Spread `σ` is the phenotypic SD of the
  candidate pool; `ρ` is the selection intensity along the value axis (how well
  the judge's preference correlates with the trait). Their product is the
  mean-shift selection imposes on the pool — the Price/breeder's selection
  differential `S`.
- **The 0.80 gain is a heritability.** The fraction of `S` that carries into
  the next generation's trait mean is exactly what a breeder's equation calls
  `h²`. The program measured it (0.83 pull-gain) and treated it as an
  empirical fudge constant.

Naming them buys three things the ad-hoc version did not have: a **theory-fixed
functional form** for the per-round variance (binomial, hence a specific
neutral-drift null), a **reinterpretation of the "selection-inert rails"** as
the population-genetics fixation boundary, and a **bridge to two recent papers**
(the Wright-Fisher text-ecosystem theory above, and Value Drifts' finding that
preference pairs move values only when they carry value contrast — a `ρ`
statement in another lab's vocabulary; see `lit_scan_2026-07-24_recent_papers.md`).

## (A) The response is a breeder's equation: `R = h²·S`

Take the response `R = v_{t+1} − v_t` (the change in the trait mean) and the
selection differential `S = kept_mean − v_t` (the "pull": selected-candidate
mean minus current trait mean, both on the same trait). Regressing `R` on `S`
through the origin gives the realized heritability `h²`:

| slice | h² (through origin) | r | n |
|---|---:|---:|---:|
| risk axis | **0.804**  (CI95 0.71–0.89) | 0.82 | 280 |
| risk axis, interior only (0.2 ≤ v ≤ 0.8) | **0.831** | 0.83 | 188 |
| self-report axis | 0.910 | 0.76 | 60 |
| self-only pools | 0.811 | 0.71 | 244 |
| base-mixed pools | 0.735 | 0.80 | 64 |
| peer-mixed pools | 0.949 | 0.98 | 32 |
| Qwen | 0.928 | 0.75 | 124 |
| OLMo | 0.784 | 0.84 | 216 |
| pooled (all 340) | 0.828 | 0.80 | 340 |

The heritability is a **stable constant near 0.8**, not a per-condition knob.
The load-bearing control is the interior-only row: response and differential
both shrink toward the rails, so a naive pooled slope could be inflated by that
shared vanishing. Restricting to mid-range values (0.2–0.8) *raises* `h²`
slightly (0.831), so the constant is a genuine transmission coefficient, not a
rail artifact.

## (B) The selection differential factorizes as `ρ·σ`

In self-only pools the offered-pool mean equals the trait mean, so
`S = pull ≈ gap = kept_mean − pool_mean`, and the gap is the Price differential:

- `gap = 0.964·ρσ`, r = 0.84, MAE 0.043 (n = 175 self-only binary rounds).

Composing with (A) gives a **fully parameter-free closed form** for the
per-round move, `E[R] = h²·ρ·σ` (with `h²` fixed at the risk-axis 0.804, not
refit): it predicts the realized drift at MAE 0.093 versus 0.110 for assuming no
change. The improvement is modest — the honest reading is that the closed form
recovers the *direction and scale* of the move from first principles, not that
it is a tight predictor round by round.

*Caveat (inherited).* The `gap ≈ ρσ` factorization is near-tautological given
order statistics on a finite pool — it says a gap must come from material times
a selector that sorts on the axis, not that the sorting persists. It is the
*form* that matters for the unification, and the empirical slope sitting at ~1
(0.964) confirms the sample-SD scale is the right one.

## (C) The phenotypic variance is binomial — the Wright-Fisher form

On the binary risk axis each candidate value is 0/1, so the total offered
variance is exactly `q(1−q)` (`q` = pool mean). The law of total variance splits
it into within-prompt and between-prompt parts:

`V_within = q(1−q) − V_between`.

This identity holds to machine precision on the logged pools (max absolute
residual **0.00000** over 280 rounds; `q(1−q)` is the tabulated
`binary_headroom` field). Reported spread `σ` — the mean within-prompt SD —
therefore rides at a fixed fraction of the binomial ceiling: `σ` averages
**0.72·√(q(1−q))**, the shortfall being the between-prompt term.

`q(1−q)` is the Wright-Fisher / binomial variance. The program's empirically
found "binary spread rule" *is* this variance; the point here is that its
functional form is not incidental — it is what makes the loop a
population-genetics process rather than an arbitrary dynamical system, and it
fixes the neutral-drift null in (D).

## (D) Setting `ρ = 0` gives mean-zero neutral drift; the rails are fixation

Two consequences of `E[R] = h²·ρσ` with `σ² ∝ q(1−q)`:

**Neutral null.** With random selection (`ρ ≈ 0`) the directed response
vanishes. The 16 random-selection rounds show mean drift **exactly 0.0000**
(SD 0.186) with a near-zero selection differential (mean |gap| 0.056) *while
variation is fully present* (mean spread 0.43). Variation without agreement
produces mean-zero drift — the Wright-Fisher neutral case, not stasis.

**Fixation boundary.** Both the directed response (`h²ρσ`) and the drift scale
are proportional to `σ`, and `σ → 0` as `q → 0` or `1`. So the rails are not a
special "selection-inert" state; they are the point where `q(1−q) → 0` removes
the raw material any force would act on. Spread and realized movement trace the
same inverted-U in the trait value:

| value bin | n | mean spread | √(q(1−q)) | mean \|drift\| |
|---|---:|---:|---:|---:|
| 0.0–0.1 | 27 | 0.152 | 0.261 | 0.059 |
| 0.1–0.3 | 56 | 0.310 | 0.413 | 0.123 |
| 0.3–0.5 | 59 | 0.396 | 0.473 | 0.172 |
| 0.5–0.7 | 78 | 0.413 | 0.480 | 0.128 |
| 0.7–0.9 | 24 | 0.331 | 0.422 | 0.148 |
| 0.9–1.0 | 36 | 0.111 | 0.158 | 0.066 |

Rail rounds (v ≤ 0.05 or ≥ 0.95) have near-zero spread and near-zero |drift|
together. This is the same phenomenon the program logged as "zero-spread
stalls are genuine homogeneity" and "the 1.000-rail is selection-inert" — now
placed as the fixation boundary of a Wright-Fisher process, where the earlier
claim discipline ("selection-inert on the measured axis," not "absorbing fixed
point") is exactly right: fixation is where variance, not some special force,
has run out.

## The unified statement

`E[Δv] = h²·ρ·σ`, with `h² ≈ 0.8` a stable transmission heritability, `ρσ` the
Price selection differential, `σ² ∝ q(1−q)` the binomial variance that vanishes
at the rails. Around this mean the loop carries Wright-Fisher-style neutral
drift whose scale is set by the same `σ`, so `ρ = 0` gives mean-zero movement
and `v ∈ {0,1}` is the fixation boundary. This is the population-genetics
version of the writeup's fitted stochastic model: the deterministic core is the
breeder's equation, and the noise term the writeup measured from residuals has
the functional form the drift theory predicts.

## What this does and does not add

- **Adds:** a theory-derived name and functional form for each fitted quantity;
  evidence that `h²` is a stable constant (interior-only control); the
  reinterpretation of inert rails as fixation; a bridge to arXiv:2604.08554 and
  Value Drifts for the writeup's Related-frameworks section.
- **Does not add:** any new experiment, any causal identification beyond what
  the source reports already claim, or a tighter round-by-round predictor. The
  closed form's MAE edge over persistence (0.093 vs 0.110) is real but small;
  its value is being parameter-free and derived, not fitted.
- **Scope:** the binomial-variance half (C, and the fixation reading in D) is
  the 280 binary risk-axis rounds only; the self-report axis keeps the
  breeder's/differential halves (A, B) but not the `q(1−q)` variance step, as in
  `report_spread_conversion_model.md`.

## Open follow-ups (no new claim, just what this frames)

1. **Measure the drift `N_e` directly.** arXiv:2604.08554 gives
   `N_e = M/[2α(2−α)]` for a text loop with pool size `M` and replacement
   fraction `α`. Our loop keeps 2 of 6 per round; a random-selection ensemble at
   two pool sizes would test whether neutral round-to-round variance scales like
   `q(1−q)/N_e` — turning the drift null from qualitative (mean-zero, present
   here) to quantitative. Cheap, and a clean Kaggle-tomorrow experiment.
2. **`h²` as an early monitor.** If `h²` is stable at ~0.8, a round whose
   realized `R/S` departs from it flags a transmission anomaly (saturation,
   contamination, or a judge/format change) — a candidate loop health readout
   distinct from spread and agreement.

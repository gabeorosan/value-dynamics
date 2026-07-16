# The loop is an elite-distribution update with a local selection differential

*Updated 2026-07-16. Analysis:
`scripts/analysis_selection_response_predictor.py` →
`experiments/selection_response_predictor.json`.*

## Result

The useful simple model is:

`predicted selector gap = judge/value agreement × offered-pool spread`

`predicted kept mean = pool mean + predicted selector gap`

`predicted next value = kept mean`.

At an experiment boundary, measure the pool, judge, and supplier state once;
hold the resulting selector gap fixed for the endpoint recurrence; and restart
the recurrence when the judge, judging format, or pool-generation policy
changes.

This unit-coefficient version has one-round MAE **0.0902** over the 290 rounds
with measurable judge/value agreement, versus **0.0891** for the fitted model.
With boundary refreshes, it has endpoint MAE **0.118** on the matched 36
selection-driven runs and **0.210** on nine judge swaps. Across the combined 45
runs its MAE is **0.1365**, versus **0.1373** for the fitted frozen-SD model,
and it gets 37/38 large endpoint directions.

The coefficient is set to one as a parsimonious empirical approximation, not
because top-2-of-6 selection mathematically implies it. The full-data fit is
`gap = −0.002 + 0.958ρσ`; replacing 0.958 by one costs essentially nothing.

## 1. Spread is converted into a standardized selection differential

For prompt `j`, let candidate `i` have measured value `x_ji`, and let `w_ji`
be one if it is kept and zero otherwise. Then

`g_j = kept mean_j − pool mean_j = Cov_i(x_ji,w_ji) / mean_i(w_ji)`.

The reported selector gap is the equally weighted mean of `g_j` over prompts.
This promptwise form remains exact in the four rounds containing one
five-candidate prompt.

This is the selection differential in the Price equation. It is exact for the
realized pool and retained set. If `σ` is the project's spread measure, define
the realized value-axis selection intensity

`a = (kept mean − pool mean) / σ`.

Then

`selector gap = σa`

exactly. This is the clean answer to “what converts spread into movement?”:
spread is the amount of variation offered to the selector; `a` is the signed
amount of that variation the actual selection rule turns into a shifted
training-set mean. The [Price covariance result](https://doi.org/10.1038/227520a0)
and [Frank's derivation of the selection differential](https://pmc.ncbi.nlm.nih.gov/articles/PMC3354028/)
provide the accounting framework.

This exact decomposition is retrospective because `a` uses the retained set.
Before selection, the compact predictor substitutes the judge/value Pearson
correlation `ρ` for `a`:

`predicted a ≈ ρ`, hence `predicted gap = ρσ`.

Here reported `ρ` and `σ` are separately averaged over prompts, so `ρσ` is a
low-dimensional product of aggregate measurements, not the mean of a
promptwise identity. The substitution is empirically good here: it gives
selector-gap R² **0.810**
and MAE **0.0421**. It is not an identity. In quantitative selection theory,
selection intensity, criterion accuracy, and target spread are separate
quantities. The [Price-equation bridge to animal breeding](https://pmc.ncbi.nlm.nih.gov/articles/PMC7133505/)
writes correlated response as selection intensity × criterion accuracy ×
target spread. In this corpus, `ρ` is a useful one-number proxy for the first
two factors together because judge, judging format, pool, and keep rule are
fixed within a cell.

## 2. Why the top-2-of-6 coefficient was removed

For six draws from an underlying standard normal, the expected mean of the top
two is 0.954481 in units of the **underlying distribution SD**. The project,
however, defines spread as the population SD of the **realized six-candidate
sample**, averaged over prompts. Those are different scales. A reproducible
one-million-pool simulation gives mean selected gap 0.9550, mean realized
six-sample SD 0.8684, and a ratio of means **1.0997**, not 0.9545.

The earlier match between the empirical slope 0.958 and the normal order-
statistic value 0.9545 was therefore coincidental. It was also too strong for
the data-generating process: most risk values are binary; four rounds contain
a five-candidate prompt; and the logged scalar judge scores do not always
fully specify the actual retained set. A per-prompt model that explicitly
uses the logged judge-score selection intensity performs worse than the simple
proxy: gap MAE **0.0444** versus **0.0421**, and one-round value MAE **0.0920**
versus **0.0902** on the same 290 rounds.

The empirical 0.958 fit remains useful as a calibration check. It should not
be described as design-derived.

## 3. The algorithmic analogue is the cross-entropy method

Generate candidates → rank them → retain elites → refit the generator is the
same abstract update used by estimation-of-distribution algorithms and the
cross-entropy method. The [cross-entropy tutorial](https://doi.org/10.1007/s10479-005-5724-z)
describes updating a sampling distribution from elite samples, and
[information-geometric optimization](https://jmlr.org/beta/papers/v18/14-467.html)
places quantile-based elite updates in a broader distribution-optimization
framework.

This connection improves the interpretation of both state variables:

- the elite mean is the update target, which is why observed `next value =
  kept mean` is the best simple one-round rule;
- spread is the exploration variance of the generator, not a force that rounds
  mechanically consume.

Cross-entropy implementations explicitly warn that elite refitting can shrink
the sampling distribution to a degenerate point and use smoothing or variance
injection to avoid premature collapse. A primary CE study describes both the
elite mean/variance update and direct variance injection
([Botev and Kroese, 2004](https://informs-sim.org/wsc04papers/064.pdf)). That is
the closest literature analogue of the observed self-pool erosion and
outside-supplier reopening: selection moves the mean; refitting regenerates a
new distribution around it; fresh material adds support that a collapsed
self-only pool no longer contains.

This is a structural connection, not evidence that fine-tuning literally
implements a Gaussian CE update. The project's binary-risk geometry is more
specific: candidate mean determines total Bernoulli variance `q(1−q)`, while
between-prompt heterogeneity determines how much remains rankable within a
prompt.

## 4. The endpoint recurrence

Let `m_t` be the host generator mean, `s` the supplier mean, and `u` the
supplier fraction. Measure boundary agreement `ρ` and offered-pool spread `σ`,
then set `c = ρσ` and iterate

`m_(t+1) = clip((1−u)m_t + us + c, 0, 1)`.

For a self-only pool, `u=0`. For a mixed pool without clipping, the fixed point
is `s + c/u`: supplier mixing contracts the host toward the supplier, while
selection offsets that attractor by the local signed gap.

Freezing the *observed* first selector gap sounds even simpler, but it is a
noisy boundary estimate. It improves the matched selection-driven endpoint
MAE slightly to 0.112, then fails on swaps (0.311), for combined MAE 0.152.
The `ρσ` proxy regularizes that first retained set and is the better shared
endpoint rule. The fitted frozen-SD recurrence remains better on the nine swap
runs alone (0.179 versus 0.210), but not on the combined endpoint comparison.

## 5. Agreement is local, and spread dynamics are secondary for forecasting

Best-of-N optimization against an imperfect reward proxy can improve proxy
reward while degrading the target reward. This has been measured directly in
[Gao, Schulman, and Hilton's reward-model overoptimization study](https://arxiv.org/abs/2210.10760).
For this model, the implication is that `ρ` is local to the current candidate
distribution. It is not a permanent property of the judge. Remeasure after a
judge, format, or pool-policy change, and remeasure again if the candidate
distribution has shifted enough to change what the proxy rewards.

The binary geometry recurrence predicts later spread better than persistence,
but feeding that predicted spread back into the endpoint simulator does not
improve endpoint MAE. Reading future agreement does. So the mechanistic model
can retain the changing-spread equation, while the best simple endpoint
forecast freezes first-boundary spread and treats agreement drift as its main
unmodeled state.

Recursive synthetic-data studies supply a broader warning about support loss:
recursively trained models can lose distribution tails
([Shumailov et al., 2024](https://www.nature.com/articles/s41586-024-07566-y)),
and self-consuming generative loops can degrade across generations
([Alemohammad et al., ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/ebc042e767de551803ccfcc45e2454f5-Abstract-Conference.html)).
Those results motivate tracking support and fresh-material injection, but they
do not establish this experiment's measured value-axis mechanism.

## Recommended presentation

Use three equations, each at its correct forecast time:

1. **Observed selection:** `gap = Cov(value, kept)/keep_rate = spread ×
   realized value-axis selection intensity`.
2. **Before selection:** `predicted gap = judge/value agreement × spread`.
3. **After selection:** `predicted next value = kept mean`.

For endpoints, iterate equation 2 with the boundary state frozen and reset it
at known regime changes. Present the binary spread recurrence as the model of
how exploration variance is regenerated, not as an endpoint improvement.

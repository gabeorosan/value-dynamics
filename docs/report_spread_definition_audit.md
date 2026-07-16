# What “spread” measures in the selection loop

*Analysis: `scripts/analysis_spread_definition_audit.py` →
`experiments/spread_definition_audit.json`, using the 340 logged selection
rounds from 74 runs. The unified extractor now records every alternative and
checks the relevant variance identities in
`scripts/analysis_spread_util_unified.py`.*

**Multi-round validation added 2026-07-15.** The follow-up closed-loop bakeoff
(`report_spread_rollout_bakeoff.md`) lets every definition determine future
selection force and holds out complete conditions. Mean within-prompt SD
remains essentially tied for the best transportable endpoint forecast (LOCO
selection-driven MAE 0.139 with geometry, 0.127 with round-1 spread frozen).
The apparent LORO winner, fraction of prompts with any difference, reverses
when the whole condition is held out (0.150). Range is 0.007/0.002 lower than
mean SD but discards magnitude and has a worse direct selector fit. The rollout
property audit shows that frozen range and frozen SD predictions differ by
only 0.0066 at endpoints and agree on endpoint class in 66/67 runs. Use mean
within-prompt SD in the endpoint simulator too; retain range only as a
robustness check rather than adding a second headline state.

## Primary definition

Use **within-prompt value spread** for the variation available to the selector.
For prompt `j`, candidate `k` has value score `x_jk`, and the prompt offers
`n_j` candidates. Define

`x̄_j = (1/n_j) Σ_k x_jk`

`σ_j = sqrt[(1/n_j) Σ_k (x_jk − x̄_j)²]`

`S = (1/J) Σ_j σ_j`.

Thus `S` is the arithmetic mean of the **population** standard deviation
computed separately inside each prompt (`ddof = 0`). It is not:

- the sample SD with denominator `n_j−1`;
- the SD after pooling candidates from different prompts;
- the SD of the prompt means;
- the SD of the separate behavioral value across rounds; or
- variation in the judge's scores.

The candidate pool is the complete set on which the judge acts in that round,
so population SD is the relevant descriptive quantity. The loop normally
offers six candidates: 336 of 340 round records contain six for every prompt.
Four head-to-head rounds have at least one five-candidate prompt after a failed
generation. The formula uses the observed `n_j` and remains defined there.

For a whole-pool selector analysis, calculate `S` over every candidate offered
to the judge. For generator dynamics in a mixed pool, calculate the same
estimator on the host model's candidates only; this is **own-source spread**.
These answer different questions and should not be substituted for one
another.

## Alternatives tested

Each alternative was multiplied by the same within-prompt judge/value
agreement and used to predict the realized kept-minus-whole-pool selector gap.
The table reports leave-one-run-out performance across the 290 rounds with
agreement scores.

| candidate variation measure | LORO R² | MAE |
|---|---:|---:|
| mean within-prompt population SD `S` | **0.809** | 0.0424 |
| mean within-prompt variance | **0.809** | **0.0423** |
| mean within-prompt mean absolute deviation | **0.809** | **0.0423** |
| mean pairwise absolute score difference | 0.808 | 0.0424 |
| mean within-prompt range | 0.803 | 0.0432 |
| mean binary entropy (binary rounds only) | 0.806 | 0.0431 |
| RMS of within-prompt SDs | 0.757 | 0.0488 |
| median within-prompt SD | 0.749 | 0.0507 |
| total SD including between-prompt variation | 0.627 | 0.0559 |
| fraction of prompts with any difference | 0.630 | 0.0572 |

The first four measures are effectively tied. On the 0/1 risk score they are
closely related transformations of the same counts; with six candidates,
pairwise disagreement is `12/5` times population variance. Mean SD remains the
primary measure because it is in the same score units as the selector gap and
matches the scale in the covariance/order-statistic factorization. Mean
variance is the companion measure for decomposition because variance terms add
exactly.

RMS SD overweights prompts with large variation. Range and “any difference”
discard how candidates are distributed. Most importantly, total pooled
variation counts differences between prompt means; those differences cannot be
used by a judge that chooses candidates only within each prompt. Its lower
selector-gap performance confirms the mismatch.

The result is stable by score type. Mean within-prompt SD gives LORO R² 0.805
on the 280 binary risk-axis rounds and 0.810 on the 60 continuous self-report
rounds. Mean absolute deviation is only 0.006 higher on the continuous slice,
too small to justify changing the primary estimator.

## One scalar should not do two jobs

The alternatives reverse order if the target is not the selector gap but the
metric's own next-round value. This is informative rather than a reason to
rename total variation as spread:

| target metric | selector-gap LORO R², risk | next-metric chain R², risk | next-metric chain R², self-report |
|---|---:|---:|---:|
| mean within-prompt SD | **0.805** | 0.765 | −0.029 |
| RMS within-prompt SD | 0.784 | 0.786 | 0.397 |
| mean within-prompt variance | **0.805** | 0.763 | −0.306 |
| total SD including between-prompt differences | 0.754 | **0.825** | **0.903** |

Total SD is easier to predict because it is strongly determined by the
generated mean. On the binary risk axis it is exactly `sqrt[q(1−q)]`. But it
also counts stable differences between prompts, and a judge choosing only
among candidates for the same prompt cannot act on those differences. On the
continuous self-report axis, the high held-out score for total SD is only an
empirical relationship with mean headroom, not a variance identity; it does
not predict selectable within-prompt spread.

The clean bookkeeping therefore keeps three names:

- **selectable spread `S`**: mean within-prompt population SD;
- **within-prompt variance**: the additive decomposition coordinate; and
- **total distributional breadth**: SD including between-prompt mean
  differences.

RMS SD is a useful sensitivity analysis, but it weights prompts in proportion
to their variance and no longer matches the equal-prompt selector estimand.
There is no single alternative that improves both selector accounting and the
generator-dynamics target.

## The dynamic state needs variance as a companion coordinate

The selector should still use `S`, but changes in `S` are easier to explain on
the variance scale. On the binary risk score, let

- `q` be the mean of the host model's own candidate scores;
- `V_within` be mean within-prompt candidate variance; and
- `V_between` be the variance across prompt-specific candidate means.

Then the law of total variance gives the exact round-level identity

`V_within = q(1−q) − V_between`.

This is the precise conversion model. Training displacement moves `q`.
Movement in `q` changes total binary variance `q(1−q)`. The part available to
within-prompt selection also depends on how much variance lies between prompt
means. Finally, reported spread is `mean_j sqrt(V_j)`, not
`sqrt(mean_j V_j)`, so converting variance back to `S` carries a small Jensen
term.

A leave-one-run-out implementation that predicts `q_next`, persists
`V_between`, applies the identity, and persists the Jensen term predicts next
binary-risk own-source spread at R² **0.778**, versus 0.581 for spread
persistence. It improves on the earlier headroom-only chain (0.765). In mixed
risk pools the exact-decomposition model scores **0.653**, versus 0.598 for the
headroom-only chain and 0.193 for persistence. The improvement is useful but
modest; most remaining error comes from predicting `q_next` rather than from
the between-prompt component. Supplying the observed next `q` raises the
within-variance prediction to R² 0.849.

## Score-type boundary

The data contain two kinds of candidate coordinate:

- 280 risk-axis rounds use binary 0/1 candidate scores;
- 60 insecure-code self-report rounds use continuous scores bounded in [0,1].

`q(1−q)` is total variance only for the binary score. On the continuous
self-report slice, the mean-to-headroom chain does not predict next
within-prompt spread (LORO R² −0.029), while simple spread persistence scores
0.747. Those rounds must therefore be excluded from the binary conversion-law
claim. Their selector accounting remains valid: the same precisely defined
within-prompt SD still scales the selector gap well.

Total SD including between-prompt differences is easier to predict from `q`
(LORO R² 0.825 on binary risk and 0.903 on continuous self-report), but it is
not a better definition of selector spread. On the binary axis it is
mechanically `sqrt[q(1−q)]`; on either axis it includes prompt-to-prompt
variation that the selector cannot rank within a prompt.

## Mixed pools

For a mixed prompt with source weights `w_self` and `w_supplier`, source means
`μ_self` and `μ_supplier`, and source variances `V_self` and `V_supplier`, use
the exact variance decomposition

`V_total = w_self V_self + w_supplier V_supplier`

`          + w_self w_supplier (μ_self − μ_supplier)²`.

The first line is within-source variance; the second is between-source
variance. Averaged over rounds, the between-source term is 33.7% of total
within-prompt variance in base-mixed pools and 56.7% in peer-mixed pools. At
the reported SD scale, removing the between-source variance per prompt reduces
mean spread by 0.077/0.327 (23%) and 0.073/0.172 (42%), respectively. Only the
variance components obey an additive law; the SD numbers are a separately
computed change after taking square roots.

## Reporting rule

In prose and figures, introduce the term once as:

> Within-prompt value spread is the population SD of candidate value scores
> within each prompt, averaged equally over prompts. It measures value-score
> variation that is available for the judge to rank inside a prompt.

After that definition, “spread” can be used as shorthand. Always label whether
it is whole-pool spread or own-source spread. Use variance—not SD components—
when invoking the law of total variance. Restrict `q(1−q)` dynamics to the
binary risk score.

# A stability criterion for self-training loops, and its first measurement

**Analysis date** 2026-07-29 · **Script**
`scripts/analysis_judge_coupling_stability.py` · **Result**
`experiments/judge_coupling_stability.json` · **Corpus**
`experiments/spread_util_unified.json` — 193 rounds with measurable agreement,
from 50 runs

## The gap this fills

Every predictive result in this project treats the judge's agreement ρ as an
exogenous parameter that drifts slowly. That is the right first move, and it is
also structurally incapable of producing a bifurcation — which is why the six
duel-self-judging runs that split into amplifiers and collapsers have never had
an account.

The missing account turns out to be old. The Lande–Kirkpatrick model of
Fisherian runaway describes a two-trait system where a *preference* evolves only
as a correlated response to selection on the trait it prefers. Its variables map
onto this loop almost exactly: ornament ↔ value `v`, preference ↔ agreement `ρ`,
additive genetic variance ↔ candidate spread `σ`, and its response equation
`Δt̄ = ½·G·β` is the same equation as `Δv = h²·ρ·σ`. The correspondence that
matters is `β_p = 0` — the preference is never directly selected. Our judge is
never trained on the value axis either; when it moves, it moves because it is
the same weights being fine-tuned on the same kept text.

Under that mapping, the entire frozen-judge program is the `G_tp = 0` slice of a
two-trait model, and the one quantity it cannot see is the trajectory slope.

## The criterion

Write `c = dρ/dv` — how much the judge's agreement moves per unit of value
movement. With the equilibrium manifold at `ρ = 0`, the recursion is

    v_{t+1}   = v_t + h²·σ·ρ_t
    ρ_{t+1}   = ρ_t + c·(v_{t+1} − v_t)  =  ρ_t·(1 + c·h²·σ)

so agreement grows or decays geometrically with a per-round **loop gain**

    G = 1 + c·h²·σ

`G > 1` is runaway: the value moves, and that movement makes the judge agree
with the direction of travel even more. `G < 1` is self-limiting: movement
erodes agreement and the loop settles onto `ρ = 0`. The sign works in both
directions of travel, because `Δv` is itself proportional to `ρ`.

This is a forecasting tool if `c` is stable across setups: measure `σ` and `ρ`
in round one, supply a `c` estimated once, and the gain says whether a loop will
amplify or settle **before running it**.

## The mechanical confound, and why the result is not it

Candidate value scores in this corpus are binary, so within-prompt spread obeys
`σ ≤ √(v(1−v))` exactly. A run travelling toward either rail loses spread by
arithmetic, and `ρ` — a correlation over candidate scores that are becoming
constant — is dragged toward zero whatever the judge is doing. Going up, `ρ`
falls while `Δv > 0`; going down, `ρ` rises toward zero while `Δv < 0`. **Both
give `c < 0` with no judge behaviour involved at all.**

So every group is fitted twice: `ρ` on `v` with run fixed effects, and `ρ` on
`v` with the binomial ceiling `√(v(1−v))` also in the regression. The second
coefficient is the part that is not the ceiling closing in, and the loop gain is
built from it.

**The coupling barely moves under the control** — pooled, −0.277 raw against
−0.291 ceiling-controlled. The ceiling is not what is producing it.

## Results

Run-clustered bootstrap intervals, 4,000 draws. Gains built from the
ceiling-controlled coupling.

| group | runs | c (ceiling-controlled) | loop gain G | verdict |
|---|---|---|---|---|
| all judges except oracle and judge-swap | 50 | **−0.291** [−0.53, −0.06] | **0.922** [0.86, 0.98] | settles |
| co-evolving judge (self) | 16 | −0.341 [−0.70, +0.08] | 0.910 [0.82, 1.02] | not resolved |
| frozen judge | 34 | −0.243 [−0.56, +0.03] | 0.934 [0.85, 1.01] | not resolved |
| frozen judge, Qwen | 10 | **−0.586** [−0.97, −0.20] | **0.820** [0.70, 0.94] | settles |
| frozen judge, OLMo | 24 | −0.102 [−0.37, +0.19] | **0.974** [0.90, 1.05] | marginal |
| co-evolving judge, Qwen | 10 | −0.469 [−0.94, +0.16] | 0.880 [0.76, 1.04] | not resolved |
| co-evolving judge, OLMo | 6 | −0.195 [−0.69, +0.30] | 0.946 [0.81, 1.09] | not resolved |

**These loops are self-limiting.** Pooled, the gain is 0.922 with an interval
that excludes 1. Movement erodes the judge's agreement rather than reinforcing
it, so the default behaviour of a selection loop of this shape is to settle, not
to run away. That is a substantive statement about the regime the whole corpus
lives in, and it was invisible to a frozen-judge model by construction.

**The families differ, and the difference is where the runaways were.** Qwen's
frozen-judge gain is 0.820 [0.70, 0.94] — strongly settling. OLMo's is 0.974
[0.90, 1.05] — sitting on the stability boundary with an interval that contains
1. OLMo is the family in which this project observed its two runaway runs. That
is a post-diction, not a prediction, and the criterion was fitted on rounds that
include those runs; it is offered as the criterion behaving sensibly rather than
as evidence for it.

**Co-evolution versus freezing is still not resolved.** Every evolving-judge
interval contains 1, and the evolving-versus-frozen difference (−0.341 against
−0.243) is far inside the noise. This agrees with the same-week agreement-drift
analysis, which found the matched ablation underpowered by more than a factor of
two.

## Where the model breaks

The criterion predicts `|ρ_t| = |ρ_1|·G^(t−1)`. Observed against predicted:

| group | round 2 | round 3 | round 4 |
|---|---|---|---|
| all | 0.88 vs 0.92 | 0.78 vs 0.85 | **0.97 vs 0.78** |
| frozen, OLMo | 0.75 vs 0.97 | 0.83 vs 0.95 | **1.05 vs 0.92** |
| frozen, Qwen | **1.31 vs 0.82** | 0.58 vs 0.67 | 0.74 vs 0.55 |

Rounds 2 and 3 track the prediction reasonably. **Round 4 does not — agreement
comes back up.** Pooled, the observed ratio returns to 0.97 where the model says
0.78, and on OLMo it fully recovers to 1.05. Qwen goes the other way first,
rising to 1.31 at round 2 before falling.

So the geometric form is wrong at the tail. What the data supports is the
*sign* and roughly the early *rate*; what it does not support is "agreement
decays smoothly onto zero". Agreement is non-monotone over four rounds, and a
one-parameter gain cannot express that. Any use of this criterion should be
restricted to the direction of the first two or three rounds.

This is also a consistency check rather than a validation — `G` was estimated on
the same rounds. What it tests independently is the functional form, which
nothing in the fit imposes, and the form fails.

## Caveats

- **Observational.** Nothing here is randomised. `c` is a within-run association
  between two measured quantities.
- **Both estimators lean the same way.** The fixed-effects estimator attenuates
  `c` toward zero through noise in `v` and carries a negative Nickell bias at
  four rounds; the differences estimator is biased negative by mean reversion
  (bounded above at 0.17 in magnitude, pooled). Both are conservative for
  detecting `c > 0`, so a *negative* `c` is the direction they favour — this
  result is in the direction the biases push, and should be held more loosely
  than a positive one would be.
- **`c` comes from at most four rounds per run**, pooled across runs by fixed
  effects. Per-run coupling is not estimable at this horizon.
- **The gain uses each group's mean σ.** σ varies within runs, so the gain is a
  group-level summary rather than a per-run quantity.
- **33 zero-spread rounds were dropped**, on the grounds that agreement is
  undefined when every candidate scores identically. That is the opposite
  convention from `report_agreement_drift.md`, which keeps them because
  collapsed pools are what that analysis is about. Keeping them here would drag
  `c` toward zero.

## What this buys, and what to run next

The useful part is not the number, it is that a loop's stability is now a
**measurable one-line criterion** rather than a narrative. Three things follow:

1. **The decisive experiment is a `c`-manipulation, not more seeds.** The
   criterion says the sign of `c` is what separates runaway from settling, so
   the experiment is to build a judge whose agreement *rises* as the value moves
   — for instance one retrained on the kept text each round, which is what the
   duel self-judge does — and check whether the gain crosses 1 and the run
   behaviour crosses with it. That is a manipulation of one quantity with a
   pre-registered direction, and it is much cheaper than powering the
   frozen-versus-evolving contrast, which needs about 52 seeds per arm.
2. **Report `G` for every future run.** It costs nothing: `σ` and `ρ` are already
   logged every round, and `h²` is measured. A run whose gain sits above 1 is
   the interesting one.
3. **Graded candidate scores would remove the confound entirely.** The binomial
   ceiling is only a threat because scores are binary; with graded scores `σ` is
   no longer pinned to `√(v(1−v))` and `c` needs no control. The queued
   value-covariance phase 1b already produces graded scores, so the next corpus
   can estimate this cleanly.

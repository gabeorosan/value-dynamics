# Spread is not a state variable: on a binary axis it is the pool mean in disguise

**Analysis date** 2026-07-29 · **Script** `scripts/analysis_spread_supply.py` ·
**Result** `experiments/spread_supply.json` · **Data** raw per-candidate logs —
1,248 prompt-rounds, 26 runs, 48 distinct prompts

## Why I went looking

Three analyses this week converged from different directions on the same
conclusion: the response to selection does not decay (0.75–0.81, flat), the
judge is not being gamed (no proxy–gold divergence), and agreement erodes rather
than amplifying (loop gain 0.92). **What runs out is not the machinery that acts
on variation — it is the variation.** Mean absolute selection gap falls from
0.099 to 0.070 over four rounds while the response per unit gap holds.

So the interesting quantity is the supply of within-prompt spread, and nothing
in the program predicts it. I expected a variance decomposition: how much of
spread is the prompt, how much the model state, how much the round.

## The question dissolves, and that is the finding

For binary candidate scores the within-prompt sample standard deviation is not
merely *bounded* by the pool mean. It is *determined* by it:

    σ  =  √(n/(n−1)) · √(q(1−q))

where `q` is that prompt's own pool mean and `n` the number of candidates. This
is arithmetic, not an empirical regularity, and the script verifies it on the
corpus rather than asserting it:

> **1,248 of 1,248 rows are binary-scored. Maximum deviation from the identity:
> 1.11 × 10⁻¹⁶.**

**Spread carries no information beyond the pool mean.** It is not a second state
variable. It cannot be screened for independently, cannot be intervened on
without moving the mean, and cannot covary with anything the mean does not.

This is the exact algebra behind three earlier results that were each found
empirically and separately:

- Spread adds nothing beyond the gap within the spread arm (t = 0.27). Of course
  — it is a function of the pool mean.
- The angular fit `spread ≈ 0.813·√(q(1−q))` explaining 85.9% of spread
  variance. That coefficient is `√(n/(n−1))` mis-estimated across pools of
  differing size; the true relation is exact.
- "Restoring spread without changing the mean" being definitionally impossible.

It also sharpens what the writeup's model is. It presents two dials, spread σ
and agreement ρ. On a binary axis there is **one** dial plus a pool mean: σ is
not free.

## What is actually free: the pool mean

Decomposing the only independent quantity, as shares of total variance:

| quantity | prompt | run | round | residual |
|---|---|---|---|---|
| pool mean | **0.456** | **0.502** | 0.002 | 0.452 |
| spread (same numbers through a fixed function) | 0.260 | 0.277 | 0.014 | 0.651 |

**Prompt and model state matter about equally; the round index matters not at
all** (0.002). Whatever depletes the loop's fuel, it is not a per-round clock.

**Prompts are highly stable across completely different runs.** Splitting runs
into random halves and correlating each prompt's mean between them:

> **split-half r = +0.920 [+0.887, +0.948]** for the pool mean
> (+0.746 [+0.625, +0.830] for spread)

The same prompts reliably produce the same pool means across different
organisms, judges and conditions. That is a real, cheap, pre-loop tool: generate
once, measure per-prompt pool means, and choose an item set whose means sit near
0.5 — which, by the identity, is exactly the item set with the most available
spread.

## The depletion mechanism, stated exactly

| by round | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| pool mean | 0.424 | 0.419 | 0.426 | 0.452 |
| **distance of pool mean from 0.5** | **0.200** | **0.237** | **0.256** | **0.268** |
| spread | 0.430 | 0.403 | 0.389 | 0.365 |

The pool mean barely moves on average — because runs go in both directions — but
its *distance from 0.5* rises monotonically. Pools polarise. And since spread is
a fixed function of that distance, spread falls mechanically: 0.430 → 0.365.

So the fuel does not get consumed by some separate process. **The loop's fuel is
distance from the middle of the scale, and selection spends it by construction.**
Nothing else is needed to explain why the gap shrinks while the response to it
holds.

## What follows

1. **Graded candidate scores are a prerequisite, not a refinement.** On a binary
   axis the second moment does not exist as an independent quantity, so no
   amount of care in the judge recovers it. Every question of the form "does
   spread do anything beyond the mean" is unanswerable in this corpus by
   arithmetic. The queued phase-1b build produces graded 0–9 scores, and that
   is what makes σ a real variable for the first time.
2. **Prompt screening is worth doing and is nearly free.** At r = 0.92 across
   runs, one generation pass ranks prompts by how much selectable variation they
   will offer, and the ranking transfers.
3. **The 18.9% of prompt-rounds with exactly zero spread** are pools sitting at
   0 or 1. They contribute nothing to selection and are identifiable in advance
   from the same screening pass.
4. **A previously-reported quantity should be restated.** The angular geometry
   result should be described as recovering a known identity on binary data, not
   as an empirical finding about candidate geometry.

## Caveats

- **Scope is exactly the binary case, which happens to be all of it.** Every row
  in this corpus is binary-scored. On a graded axis the identity does not hold
  and spread is genuinely free; nothing here says what it will look like there.
- **Prompt identity falls back to the item index** where the raw log does not
  carry task text. The index is stable within a source because the prompt list
  is fixed, but a prompt shared across sources may be counted as two prompts,
  which would understate the prompt share and understate stability. Both are
  already high, so the direction of that bias is against the conclusion.
- **The variance shares are a nested one-way decomposition**, not a mixed model,
  and with unbalanced cells the components do not partition exactly — hence the
  residual is computed after additively removing both main effects rather than
  by subtraction.
- **Prompt and run shares cannot be cleanly separated** when conditions differ
  in which prompts they use; the two are estimated marginally.

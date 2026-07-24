# Spread is a lever at a fixed pool mean: variation only counts if it sits inside the unit the judge compares within

Date: 2026-07-24
Script: `scripts/analysis_spread_at_fixed_mean.py`
Data: every logged candidate pool in `experiments/` that records both candidate text
and per-candidate judge scores (323 rounds)
Output: `experiments/spread_at_fixed_mean.json`

## Summary

Holding a round's pool mean **exactly** fixed and changing only *which prompts carry
the value variation* moves candidate spread by a factor of 3.5 (0.286 against 0.082)
and the size of the realized selection gap by a factor of 3 (0.104 against 0.034),
using the judge's own logged preferences. Both arrangements obey the same
agreement-times-spread law, with a single slope of 0.857 and an intercept of −0.005
fitting all 646 arm-rounds together at r = 0.928.

So spread is not merely bookkeeping on the pool mean. The reason it *looked* pinned
by the mean in the observed runs is that those runs never separated variation within
a prompt from variation between prompts. Once separated, spread moves freely at a
fixed mean and the selection gap follows it.

The mechanism this exposes is worth stating on its own: **variation only counts if it
sits inside the unit the selector compares within.** The judge compares candidates
within a prompt. Value variation parked between prompts is invisible to it, however
much of it there is.

## Why this is possible at a fixed mean

On a binary-scored axis the pool mean q fixes the *total* variance at q(1−q), but the
law of total variance splits that total:

    within-prompt variance = q(1−q) − between-prompt variance

The pool mean therefore constrains the sum, not the split. Concentrate the 1s into
some prompts and leave others empty, and within-prompt spread goes to zero while the
mean is untouched. Even the 1s out across prompts and within-prompt spread reaches
its maximum. The earlier finding that the pool mean explains 85.9% of the variance in
spread (`report_spread_is_not_a_free_variable.md`) is a fact about the arrangements
that *happened to occur*, not a constraint on the arrangements that are possible.

## Method

Every logged round supplies, per prompt, six candidate answers with a value score
recoverable from the answer text by the committed parser, and the judge's own score
recorded at the time. From those six, two sub-pools of four are built per prompt:

- **HIGH arm** — chosen to maximize mean within-prompt spread
- **LOW arm** — chosen to minimize it

subject to an identical total number of value-1 candidates across the whole round, so
the two arms have exactly the same pool mean (enforced to 1e-9). The per-prompt choice
is just how many 1s to take, so both arms are solved exactly by a knapsack over
prompts rather than by search. Within a prompt, which particular candidates of each
value class are taken is decided by judge score, identically in both arms, so that
step cannot manufacture a difference between them.

Selection then keeps the top 2 of 4 by logged judge score within each prompt, matching
the loops.

## Results

| Quantity | HIGH arm | LOW arm |
|---|---|---|
| Pool mean | identical by construction | identical by construction |
| Within-prompt spread | 0.286 | 0.082 |
| Between-prompt variance | 0.059 | 0.154 |
| Size of the selection gap | 0.104 | 0.034 |
| Agreement | −0.240 | −0.057 |

The between-prompt variance moves opposite to the within-prompt spread, which is the
identity doing its work: the arms trade one for the other at a fixed total.

Across 323 rounds the HIGH arm produces the larger gap in 239, the two are tied in 71,
and the LOW arm is larger in 13.

**The same law describes both arms.** Fitting the gap on agreement times spread:

| Fit | Slope | Intercept | r | n |
|---|---|---|---|---|
| HIGH arm alone | 0.848 | −0.008 | 0.922 | 323 |
| LOW arm alone | 0.825 | −0.003 | 0.885 | 323 |
| Both arms pooled | 0.857 | −0.005 | 0.928 | 646 |

Neither arm needs its own slope or intercept. The manipulation moved the pool along
the existing law rather than breaking it.

## Isolating spread from agreement

The two arms differ in agreement as well as spread, which is expected — flattening a
prompt's value variation also removes what agreement is computed from — but it means
the headline contrast is not a single-factor manipulation. Restricting to rounds where
the two arms happen to land on nearly the same agreement isolates spread:

| Agreement matched within | Rounds | Spread, HIGH vs LOW | Gap size, HIGH vs LOW | Agreement, HIGH vs LOW |
|---|---|---|---|---|
| 0.05 | 25 | 0.262 vs 0.078 | 0.113 vs 0.030 | −0.122 vs −0.123 |
| 0.10 | 56 | 0.276 vs 0.089 | 0.118 vs 0.039 | −0.137 vs −0.121 |
| 0.20 | 90 | 0.280 vs 0.088 | 0.114 vs 0.036 | −0.176 vs −0.147 |

At the tightest matching the two arms have effectively identical agreement (−0.122
against −0.123) and the gap still differs by nearly a factor of four. Spread is doing
the work.

## Scope and caveats

- **This is counterfactual selection, not counterfactual training.** It establishes
  that spread drives the selection gap at a fixed pool mean, using real judge
  preferences. It does not by itself show the value then moves; that link is the
  separately established relation between the gap and the next round's value. The
  honest chain is: spread to gap here, gap to movement elsewhere.
- **Agreement is measured on fewer prompts in the LOW arm** — on average 2.2 of 12
  prompts retain any value variation, against 7.5 in the HIGH arm. A prompt whose
  candidates all score alike admits no correlation. The LOW arm's agreement figure is
  therefore noisier and rests on the minority of its prompts that kept variation.
- Sub-pools are 4 of the logged 6 candidates, and 2 are kept. Both the offered count
  and the kept count are held identical across arms, but they are not the loops' own
  6-and-2, so absolute gap sizes here are not comparable to logged round values.
- Rounds where no two arrangements share an achievable total, or where the best
  achievable spread contrast is zero, are excluded. 323 rounds survive.
- The 3.5-fold spread contrast is the largest the logged pools permit. A purpose-run
  experiment could go further by generating candidates specifically to fill the
  arrangement.

## What this changes

The intervention result stands and gets a cleaner mechanism. Adding an outside
candidate source to a collapsed pool worked, and this says why it had to be an outside
source: within a self-only pool at a rail there is no arrangement that restores
within-prompt variation, because there is no variation left to rearrange. The outside
source supplies the raw material; the arrangement determines whether the judge can see
it.

It also names a lever the program has not used. Spread can be manipulated at a fixed
value by controlling how candidates are distributed across prompts, which is a
selection-side intervention requiring no change to the model, the judge, or the data
source.

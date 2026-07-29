# A judge whose reasoning block is left open reports a fixed answer, not a judgment

Date: 2026-07-25
Scripts: `experiments/value_covariance/judge_manipulation_check.py`,
`experiments/value_covariance/instrument_pilot.py`
Results: `experiments/value_covariance/judge_manipulation_check_result.json`,
`instrument_pilot_result.json`

## The finding

When a reasoning model is used as a logprob judge, the generation prompt must close
the model's thinking block before the answer tokens are read. If it does not, the
next-token distribution is dominated by the reasoning opener, and reading the
relative probability of the two answer tokens measures the **noise tail** of that
distribution. That tail has a fixed lexical preference, so the judge returns the same
answer to every input while looking like a confident, well-behaved instrument.

Measured on Qwen3-4B:

| | Reasoning block left open | Block forced closed |
|---|---|---|
| Next-token distribution | dominated by the reasoning opener | `A` 0.998, `B` 0.0019 |
| Picks A when the correct answer is A | 0.987 | 0.999 |
| Picks A when the correct answer is B | 0.987 | 0.001 |
| Presentation-order gap | 0.963 | **0.006** |
| Accuracy on hand-built contrast pairs | 0.501 (chance) | **0.832** |

The fix is one line: render the judge turn with the thinking block closed, appending
`<think>\n\n</think>\n\n` when the chat template does not do it.

## Why it is worth a report rather than a commit message

This artifact is invisible in every way a pipeline normally notices problems. The run
exits 0. The output is well formed. The judge looks *more* confident than a real one,
not less. And the standard debiasing steps convert it into a perfectly plausible null:

- Averaging both presentation orders turns a 0.987 position bias into exactly 0.500.
- Averaging both rubric polarities turns a 0.98 assent bias into exactly 0.500.

So the two controls that exist to remove bias are precisely what manufactured the
clean-looking zero. Three consecutive runs produced "no effect" results that were
entirely instrumental, and one of them reported a cross-pool correlation of 0.9075
that was a relationship between quantities at the 1e-4 scale.

## What it cost, and the wrong conclusion it nearly produced

Three full runs plus a pilot. More importantly, it nearly produced a substantive but
false finding. With the broken judge, candidates scored 0.484 to 0.540 on every axis,
and reading the pool supported the story: six answers to the same prompt that are
visibly the same advice reworded ("That's a great question, and it's important to
address it with both concern and care" against "It's important to address this
concern with both honesty and empathy"). The natural conclusion was that a modern
instruction-tuned model sampled at temperature 1.0 produces no real value variation
on open-ended prompts, which would have been an important result for this whole
program and would have redirected it toward a redesign of the generation step.

It is false. With the judge fixed, the same candidate pools show:

| Axis | Within-prompt SD, broken judge | Within-prompt SD, fixed judge |
|---|---|---|
| Risk tolerance | 0.0068 | **0.172** |
| Caution and reversibility | 0.0118 | **0.185** |

Scores span 0.07 to 0.98 where they had spanned 0.48 to 0.54. A 25-fold increase in
measured variation, from closing a thinking block. The candidates carried the
variation all along; the instrument could not see it.

The near-miss is the transferable part. A null result from a saturated instrument
reads exactly like a null result from a uniform population, and the pool text was
genuinely consistent with the wrong story.

## What was checked, and the residual weakness

The manipulation check uses six hand-written answer pairs that differ unambiguously
on one axis, each presented in both orders, with a pass criterion of mean accuracy at
or above 0.80 fixed before running. The fixed judge scores 0.832: five of six pairs
are near-certain (0.988 to 1.000) and **one is confidently wrong** (0.005) — on the
risk axis it judged "do not launch until the rollback is tested" to favour the
higher-variance option over "launch on schedule". So this is a usable instrument with
a known and non-trivial error rate, not a reliable one.

The judge is also close to deterministic once fixed (0.998 against 0.002), so the
win-rate score is nearer to a vote count than a graded probability. That reduces the
resolution the design was counting on.

## Rules this produces

1. **Any logprob read from a reasoning model must close the thinking block first**,
   and the script should assert it: check that the rendered prompt contains a closed
   block before reading answer tokens.
2. **Print the top few next tokens the judge actually wants to emit.** One line of
   diagnostic output would have caught this on the first run instead of the fourth.
   It is now in the manipulation-check script and should be standard.
3. **A bias-removal step is not safe by default.** Order-averaging and
   polarity-averaging both map a saturated instrument to exactly the chance value.
   Report the raw asymmetry alongside the corrected number — the order gap of 0.963
   was visible in the data before any conclusion was drawn from it, had anything been
   looking.
4. **Run the manipulation check before the experiment, not after a null.** Known
   contrasts the instrument must separate are cheap, and a null is uninterpretable
   without them.

# Value-covariance phase 1, run 1: VOID — three instrument failures, no usable covariance

Date: 2026-07-24
Kernel: `hirokenzan/vd-valcov-20260724-2038` (COMPLETE, exit 0)
Raw artifacts: `experiments/value_covariance/output_void_run1/`
Script at time of run: `experiments/value_covariance/script.py` (since fixed)

## Verdict

**The run produced no usable measurement and nothing from it is citable.** It exited
cleanly, wrote a well-formed output file, and reported a cross-pool correlation of
0.9075 — which is an artifact, not a result. All six value axes came back with
essentially zero variance, so the "correlation" is between quantities at the 1e-4
scale.

This is recorded because a clean exit plus a plausible-looking headline number is
exactly the shape of failure that gets cited by mistake.

## The numbers that look like a result, and why they are not

| Reported quantity | Value | Why it is meaningless |
|---|---|---|
| Cross-pool correlation | 0.9075 | Correlates predicted against observed spillover when both are ~1e-4 |
| Cross-pool mean absolute error | 0.00013 | Tiny because everything is ~0, not because the prediction is good |
| Sign agreement | 0.9333 | Signs of numerical noise |
| Per-axis within-prompt variance | 0.0 to 1e-05 | **The instrument did not discriminate at all** |
| On-axis selection differential | 0.00084 | Selecting the top 4 of 12 on an axis moved that axis by 0.08% of the scale |

The last two rows are the whole story. Taking the top third of candidates by an axis
should move that axis substantially; it moved it by essentially nothing.

## Three independent faults, in order of severity

**1. Every candidate was truncated inside its reasoning block (fatal).**
Qwen3-4B emits `<think>...</think>` before its answer. `max_new_tokens` was 200. All
360 candidates in each pool consist of nothing but reasoning preamble — inspection
shows them opening with "Okay, so my colleague is asking me to review their deployment
plan..." and being cut off before any answer. Candidate lengths were 832 to 1100
characters with zero empty strings, so nothing in the output signalled a problem; the
pool looked healthy and was entirely content-free with respect to the value axes.

Since every candidate was a near-identical restatement of its prompt, the judge was
right to score them alike. The zero variance is a true measurement of a broken pool.

**2. The second judge never loaded, removing the primary estimate.**
`microsoft/Phi-4-mini-instruct` failed with `cannot import name 'SlidingWindowCache'
from 'transformers.cache_utils'` — a version incompatibility with Kaggle's
preinstalled transformers. The design audit had designated the **cross-method**
covariance (selected axis from judge A, off-target axes from judge B) as the primary
estimate precisely because six axes scored by one judge reading one answer share a
quality halo. Without judge B, only the same-judge matrix exists, which is the
measurement the audit said not to trust.

**3. The output could not be diagnosed from itself.**
Only the polarity-averaged score was saved. The score is
`0.5 * (P(yes | positive form) + 1 − P(yes | negative form))`, which collapses to a
constant 0.5 for every candidate if the judge is insensitive to the polarity flip.
That failure mode is indistinguishable from a genuinely uniform pool unless the two
reads are kept separately — and they were not, so fault 1 had to be diagnosed by
reading raw candidate text rather than from the metrics.

## Fixes applied before re-running

- Generation requests the answer directly (`enable_thinking=False` where the chat
  template supports it), any `<think>` block is stripped before scoring, candidates
  truncated inside an unclosed block are emptied rather than silently scored, and the
  token budget went from 200 to 420. The count of too-short candidates is now printed.
- Judge B is Gemma-2-2B-Instruct attached as a Kaggle model source, avoiding both the
  transformers incompatibility and Hugging Face gating.
- Both polarity reads are saved per candidate per axis.
- An explicit instrument check runs before any covariance is reported, and returns
  `INSTRUMENT_FAILURE_NO_DISCRIMINATION` when the smallest within-prompt standard
  deviation across axes falls below 0.01.

## The transferable lesson

The design work before this run was spent on statistical power — how many prompts and
candidates are needed to estimate a covariance, and whether the sample could
distinguish the hypotheses. That analysis was correct and irrelevant. **The binding
constraint was whether the instrument discriminates at all**, and no amount of sample
size fixes an instrument reading zero.

Every future measurement script in this program should compute and print a
discrimination check on its own readout before computing anything downstream of it,
and should refuse to report a relationship when the underlying quantity has no
variance. A pipeline that exits 0 and emits a correlation of 0.91 from pure noise is
worse than one that crashes.

---
name: verify-quant-claim
description: Spawn a fresh-context adversarial re-derivation of a quantitative claim from its raw data, to catch tautologies, undocumented filters, shared-term artifacts, and overstated sample sizes. Use before citing any number in a writeup, report, or external post, and whenever inheriting an analysis produced by an earlier session or a weaker model.
---

# Verify a quantitative claim

Self-critique does not catch these errors. A fresh-context subagent that never
sees the original analysis does. This is the single highest-yield check in this
project's workflow: on 2026-07-24 it found that a headline factorization was a
within-round identity, that its sample had been silently filtered, and that a
transmission coefficient was inflated 27.5% by shared measurement noise — none of
which the original analysis or a re-read of it had surfaced.

## When to use

Before a number goes on a summary surface (README, writeup, ledger row, external
post). Also whenever an analysis was produced by an earlier session, by a
different model, or more than a few days ago.

## How to spawn it

One subagent, Opus, background, with a prompt that supplies:

1. **The raw data path and the exact definitions** of every quantity, written out
   in words rather than by reference to the existing script.
2. **An instruction to write its own script first and read the existing one only
   at the end**, then report disagreements explicitly. Order matters — reading the
   original first anchors it.
3. **The prior numbers as claims to check, not targets to reproduce.** Say so
   verbatim, and say "if you get something different, say so loudly."
4. **The specific failure modes to hunt.** Do not leave this implicit:
   - Is the relation an identity given how the quantities are constructed? Ask
     what is algebraically forced by the selection rule, the scoring format, or
     the keep-ratio.
   - Do the predictor and the response share a term? Shared measurement error
     inflates covariance and correlation.
   - Does the reported n match the data, or is there an undocumented filter?
   - Is n the number of rows or the number of independent units? Rounds within a
     run, and runs within one source file, are not independent.
   - Are there rows where the quantity is missing, and is the missingness related
     to the condition being tested?
   - Is the coefficient constant across slices, or is a pooled number hiding a
     range?
5. **An explicit request for bluntness**: "a confirmed-but-fragile claim is more
   useful to me than a clean-looking one."

## Acceptance criteria

The verification is done when you have, per claim, a verdict of solid / fragile /
wrong, with the reason, and a statement of what should be reported instead. A
verification that only says "reproduces" has not done the job — reproducing the
arithmetic is the easy half, and it was never where the errors were.

## After it returns

Corrections land in `docs/ANALYSIS_LEDGER.md` first, then propagate. Record the
rescoping, not just the corrected number: "reproduces arithmetically, rescoped as
a decomposition" is the useful form. Verify the subagent's own most consequential
claim yourself before acting on it — it is a fresh context, not an oracle.

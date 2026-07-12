# Mixed-generator selection: coupled organisms under one judge

*Spec written 2026-07-12 ~17:00 (general thread), after the integrator
decomposition (docs/report_loop_integrator_decomposition.md) and the
cross-family gain fit (Qwen k=1.21, OLMo k=0.75). Queued behind the release
grid; runs on Kaggle T4 (Qwen family) or Modal from the remaining grant.*

## Why this design (hypothesis, not established law — per the 07-12 re-audit)

The observed pattern in single-organism loops is spread loss: the measured
spread regression (d(s) ≈ −0.18·s − 0.30·|kept-gap|) is an IN-REGIME AVERAGE,
and K2 collapse floors / K3 attenuation / let-go decay are all consistent
with selection consuming pool spread faster than generation regenerates it.
Whether generation can re-supply spread on its own is exactly what this
experiment's control arms measure — the "loops die of spread exhaustion"
story is the HYPOTHESIS under test, not a premise. If it holds, a
two-generator pool is a spread source; if generation regenerates spread by
itself, coupling adds nothing and the control arms will show it.

A two-generator pool is exactly that. Each round organisms A and B generate
half the candidate pool (3 each of K=6); the judge ranks the mixed pool;
**each organism trains only on its own kept answers**. An organism whose
candidates are never kept trains on nothing — its state freezes, and it
keeps injecting its unchanged proposal distribution into the pool every
round. IF the spread-exhaustion hypothesis above holds, the pool's spread
would then have a floor set by the between-organism value gap — **whether
coupling actually sustains spread is itself a tested outcome**, and it is
what would make sustained (not transient) non-trivial dynamics plausible.

With Qwen's super-unit gain (k=1.21), the model sketches three regimes:
1. **Capture:** judge consistently prefers A's flavour → A trains toward
   more of it (share→1), B freezes; A's own arc then follows the
   single-organism law and collapses spread WITHIN its half — but B's
   frozen half keeps total spread up, so the judge always has a real choice:
   capture must be maintained against a live alternative, unlike
   single-organism rails.
2. **Alternation:** taste is state-dependent (measured: taste scales with
   spread/pool composition) → kept-share oscillates, both organisms drift.
3. **Convergence:** both train toward the judge's taste from different
   sides → between-organism gap closes, spread floor collapses, and the
   system re-enters the single-organism regime. Classifier (corrected per
   the 07-12 program audit — the first draft had this backwards):
   **capture** = kept-share entropy → 0 with the between-owner value gap
   still open; **convergence** = share entropy stays near max while the
   between-owner pool-mean gap → 0; **alternation** = share entropy high
   with sustained gap.

## Cells

Same-base-model pairs (Qwen3-4B adapters, all existing):

| pair | value axis | assets |
|---|---|---|
| P1: em_dose_750 × fresh | EM insecurity vs none | dose adapters (Drive em_dose_adapters/, Kaggle em-organism-250) |
| P2: em_dose_750 × em_dose_250 | same value, dose gap | same |
| P3: em_dose_750 × persona_mod25_r5 | EM vs risk-taking (cross-value) | K1 organism (Kaggle k1 dataset) |

Judges (arms): (a) **frozen base** — external arbiter, near-zero measured
taste on Qwen (fan-from-noise prediction); (b) **A-self** — the em organism
judges the mixed pool (conflict of interest: does it capture?); (c)
**neutral-prompt frozen base** with the K3 neutral wording for the EM pairs.

Seeds: 2 per (pair × judge) to start; 4 rounds; K=6 with 3+3 split
generation; top-2 kept; 10 train steps/round on the owner's kept rows only.

Priority order under budget: P1(a), P1(b), P3(a) first (existence: does
coupling sustain spread + which regime), then P2, remaining judges/seeds.
6 cells ≈ 1 Kaggle session (~7 h at ~65 min/rollout Qwen pace) = free, or
~$5 Modal parallel.

## Launch gates added per the 07-12 program audit (spec NOT launch-ready before these)

1. **Owner-blind taste screen (selection-only, inference cost):** score mixed
   pools with each candidate judge and verify (a) the judge's kept-gap on the
   between-owner axis is nonzero, (b) adapter identity is not recoverable
   from style artifacts. The (b) test, specified per the re-audit: logistic
   classifier on [answer length in chars, type-token ratio, mean sentence
   length, markdown-marker count, digit count], 5-fold CV with the ITEM as
   the fold unit (both owners' answers to an item stay in one fold);
   PASS iff CV accuracy < 0.65 (chance 0.5). Stop if either half fails.
2. **Spread-floor is a HYPOTHESIS, not a law:** the measured negative spread
   regression is an in-regime average — generation each round can regenerate
   spread on its own. The coupling-as-spread-source claim is what this
   experiment TESTS; the spec's framing must not assume it.
3. Independent optimizer/adapter state per owner; explicit zero-kept-owner
   handling (record, skip train, state frozen); owner-balanced generation
   order (alternate which owner generates first each item).

## Implementation

Chassis: `experiments/kaggle/kaggle_k3_em_neutral_grid/script.py` (Qwen,
self-description loop, judge scoring, per-rollout saves) with:
- second adapter loaded (`GEN_B_ADAPTER_ENV`), generation split 3+3 per item
  (tag candidates with owner);
- per-owner kept rows → per-owner `round_train` calls (skip an owner with 0
  kept rows that round; record the zero);
- new per-round readouts: kept-share per owner, between-owner pool-mean gap,
  within/between spread decomposition, per-owner value coordinate (the
  existing battery run per owner adapter).
- judge prompt verbatim = the K3 neutral prompt for (c); for (a)/(b) the K2
  pairwise "Which is the better answer?" wording; owner tags NEVER shown to
  the judge.

## Pre-registered expectations (from the measured model, refutable)

- Total pool spread does NOT decay to floor while owners' values differ
  (refuted if spread halves from r0 by r4 with share still mixed —
  would mean generation itself, not selection, homogenizes).
- P1 with self-judge (b): capture by em organism (share > 0.75 by r2) —
  CONDITIONAL on launch gate 1 first demonstrating the own-flavour preference
  in the owner-blind taste screen (the re-audit's point: this preference is
  assumed, not yet measured on mixed pools); refuted if share stays ≈0.5.
- P3 cross-value with base judge: highest sustained spread of any cell
  (largest between-owner gap) and the widest final-coordinate range across
  seeds — CONDITIONAL on coupling actually sustaining spread (the tested
  outcome above), and quoting K1's descriptive pooled slope only.

## Readouts / analysis

Kept-share trajectory per owner; between-owner pool gap; total/within/
between spread; per-owner coordinate trajectories; regime classification
per cell (capture / alternation / convergence) using the FULL owner-share
time series plus round-to-round transition counts — share entropy alone
cannot distinguish alternating deterministic capture from balanced
stochastic selection (re-audit); kept-gap→drift refit on the coupled pools
(does the coupling change the transition slope when spread is externally
sustained?).

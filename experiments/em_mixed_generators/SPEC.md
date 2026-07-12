# Mixed-generator selection: coupled organisms under one judge

*Spec written 2026-07-12 ~17:00 (general thread), after the integrator
decomposition (docs/report_loop_integrator_decomposition.md) and the
cross-family gain fit (Qwen k=1.21, OLMo k=0.75). Queued behind the release
grid; runs on Kaggle T4 (Qwen family) or Modal from the remaining grant.*

## Why this design, in the integrator model's terms

Single-organism loops die of **spread exhaustion**: selection destroys pool
spread (d(s) ≈ −0.18·s − 0.30·|kept-gap|, measured), no term regenerates it,
and force ∝ spread — so every single-generator schedule eventually runs out
of material (K2 collapse floors, K3 attenuation, let-go decay). The user's
diversity goal needs a spread SOURCE.

A two-generator pool is exactly that. Each round organisms A and B generate
half the candidate pool (3 each of K=6); the judge ranks the mixed pool;
**each organism trains only on its own kept answers**. An organism whose
candidates are never kept trains on nothing — its state freezes, and it
keeps injecting its unchanged proposal distribution into the pool every
round. The pool's spread therefore has a floor set by the between-organism
value gap: **coupling breaks the spread-decay law**, which is what makes
sustained (not transient) non-trivial dynamics plausible for the first time.

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
   system re-enters the single-organism regime (a measurable endpoint:
   between-share entropy → 0).

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
- P1 with self-judge (b): capture by em organism (share > 0.75 by r2) — the
  measured secure/candid taste asymmetries say an EM self-judge prefers its
  own flavour; refuted if share stays ≈0.5.
- P3 cross-value with base judge: highest sustained spread of any cell
  (largest between-owner gap) and the widest final-coordinate range across
  seeds (k=1.21 noise amplification with a permanent spread source).

## Readouts / analysis

Kept-share trajectory per owner; between-owner pool gap; total/within/
between spread; per-owner coordinate trajectories; regime classification
per cell (capture / alternation / convergence) with the share-entropy
endpoint; integrator-gain refit on the coupled pools (does k change when
spread is externally sustained?).

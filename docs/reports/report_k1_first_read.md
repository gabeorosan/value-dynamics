# K1 first read: trajectory fans by selection rule + channel validity

*2026-07-12 ~00:45, general thread. Raw:
`experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json`
(complete: 4 conditions × 4 seeds × 4 rounds + measure-only seed 99).*

## What was run

The Qwen anchor grid on the re-centered risk organism `persona_mod25_r5`
(generated-channel persona gate passed in-kernel at 0.50, per-order 0.479 /
0.521). Each rollout: 24 balanced-order gamble prompts per round, K=6
candidates each, judge keeps top-2, kept answers trained with exact-order
mirroring; the trajectory value is the fraction of strictly-parsed generated
answers choosing the gamble (both orders averaged; 4 samples/item/order at
rounds 0 and 4, 1 mid-round).

## Trajectory distributions (rounds 0→4, start ≈ 0.60)

| condition | seed 0 | seed 1 | seed 2 | seed 3 | final range |
|---|---|---|---|---|---|
| evolving_self | 0.59→0.26 | 0.64→0.71 | 0.60→0.88 | 0.58→**1.00** | **0.74** |
| random_select | 0.59→0.63 | 0.64→0.34 | 0.60→0.66 | 0.58→0.79 | 0.45 |
| frozen_copy_r0 | 0.59→0.44 | 0.64→0.68 | 0.60→0.70 | 0.58→0.51 | 0.26 |
| frozen_base | 0.59→0.60 | 0.64→0.47 | 0.60→0.59 | 0.58→0.59 | 0.14 |

Measure-only seed 99 (full loop cadence, no training): 0.583→0.573 — the
instrument itself drifts ≈0.01 over a rollout's worth of batteries.

Reads (dynamics, not verdicts):

1. Self-judging produces the widest fan (0.26–1.00), including one cautious
   collapse and two near-rail amplifications from the same starting organism.
2. Random selection also fans (0.45 range) — training noise alone moves the
   coordinate a lot at this dose. The judge-attributable divergence is the
   EXCESS of the self-judge fan over the random fan, not the fan itself.
3. The external frozen-base judge is the tightest regime (0.14 range,
   final mean ≈0.56, slightly below the 0.60 start) — an anchoring force
   relative to every other rule.
4. Paired primary (evolving_self minus frozen_base finals per seed):
   −0.34, +0.24, +0.28, +0.41 — positive-leaning, one large negative;
   at n=4 this is a distribution to show, not a test to pass.

## Channel validity (order-gap flags vs a binomial null)

Naive flag counting says 81/85 reads breach the 0.10 order-gap gate. That
number is mostly threshold-vs-noise mismatch: a mid-round read samples each
of 24 items once per order, so its gap estimator has SE ≈ 0.14 at p ≈ 0.5 —
above the gate itself. Against a per-read binomial null
(z = gap / sqrt(2·p(1−p)/24s)):

- Generated channel, mid reads (s=1): 16% of 51 reads exceed z=1.96
  (null 5%) — mild.
- Generated channel, endpoint reads (s=4): 35% of 34 reads exceed
  (mean z 1.59, max 3.8) — a REAL order effect beyond sampling noise,
  typical gap 0.1–0.27. Because the trajectory coordinate averages both
  orders, this inflates variance but does not bias the order-balanced mean;
  the primary contrast stands with the asymmetry reported alongside.
  Largest offenders concentrate in frozen_base endpoints (z 3.8 twice) —
  exploratory observation only.
- Forced channel: mean endpoint order gap 0.347, 34/34 reads above the 0.10
  gate → the forced single-token readout is ORDER-CONFOUNDED and invalid as
  a semantic channel in K1. This matches the Cerebrium K2 pilot's round-0
  forced gap of 0.46 on OLMo — the confound reproduces across model family,
  platform, and stack, so it reads as a property of forced-choice reads on
  these trained organisms, not a platform artifact.

Consequences: K1 claims ride the generated channel only; forced-channel
numbers appear only as the co-movement/dissociation exploratory tier with
the measured confound stated. The Sunday cross-stack check for merging any
Cerebrium/Kaggle K2 seeds should compare GENERATED-channel baselines.

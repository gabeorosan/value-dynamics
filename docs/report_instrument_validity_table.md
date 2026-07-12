# Consolidated instrument-validity table (K1, K2) + rail order-robustness

*2026-07-12 ~19:10, general thread. Built in response to the 07-12 program
audit's point that the 0.10 generated-channel order-gap gate was declared a
launch gate but then used only as a post-hoc flag. This consolidates the
order/invalidity numbers and states the rule now applied. Script:
inline below / reproducible from the output JSONs.*

## The declared rule (choose one, applied consistently now)

The 0.10 order-gap threshold is a **flag, not a hard validity gate**, and
every headline claim must survive the flag by one of two routes: (a) the
order-*averaged* coordinate is used and the effect is present in BOTH
presentation orders (order gap inflates variance but does not create the
effect), or (b) the claim is dropped. The forced-choice channel remains
secondary/invalid wherever its gate fails. This replaces the earlier
implicit "hard gate at launch" language, which was never enforced post-hoc.

## Table (generated channel)

| grid | reads | order gap >0.10 (all) | >0.10 (endpoints) | invalid >0.10 | forced gap >0.10 |
|---|---|---|---|---|---|
| K2 | 87 | 38 (44%) | 3/17 | 4 (5%) | 46 (53%) |
| K1 | 80 | 46 (58%) | 9/16 | 0 | 74 (93%) |

Reading: order asymmetry is common on the generated channel of both grids
(a real property of these organisms' mid-round reads, SE≈0.14 at p≈0.5 for a
single-sample mid read), and the forced channel is order-confounded in the
majority of reads on both — so all claims ride the order-averaged generated
channel and the forced channel stays exploratory, as already practiced.

## Endpoint flags and their disposition

**K2** flagged endpoints (order gap >0.10 at r4): frozen_base s5 (0.271),
frozen_base s2 (0.167), frozen_base s0 (0.125). The first two are the
oversight-counterfactual rails — checked per-order:

| rail | r0 A / B | r4 A / B | both orders railed? |
|---|---|---|---|
| base s2 | 0.255 / 0.167 | 0.604 / 0.771 | YES |
| base s5 | 0.354 / 0.109 | 0.667 / 0.938 | YES |

Both rails rise firmly in BOTH orders (r4 order-A 0.60/0.67, order-B
0.77/0.94, from ~0.21/0.23 starts). The endpoint order gap inflates variance
but does not manufacture the rail; the oversight-counterfactual claim
(conservative judge would have reversed both) stands, with the order
asymmetry noted. base s0's flag is on a non-rail low endpoint (0.188) and
affects nothing.

**K1** has 9/16 flagged endpoints — consistent with K1's already-reported
larger endpoint order effect (report_k1_first_read.md); K1 claims are
distributional (fan width) and the fan is present in both orders, but any
single-seed K1 endpoint value should be quoted as order-averaged with its
gap. No K1 headline rests on one seed's point value.

## What this does not fix

Per the audit, the strongest response is a full statistical order-effect
model (z per read, order as a random effect) and re-running headline
summaries on the preregistered-valid subset vs all reads. That is the next
analysis; this table is the consolidated flag census plus the specific
robustness check the two load-bearing rails needed.

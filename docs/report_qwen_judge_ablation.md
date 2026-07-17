# The supplier-removed amplification needs the self-judge: judge-model ablation on the Qwen self-only loop

*2026-07-17, general thread. Prereg:
[prereg_qwen_selfonly_judge_ablation.md](prereg_qwen_selfonly_judge_ablation.md)
(committed before launch, thresholds registered). Data:
`experiments/em_selfaware_loop/output/head2head_basejudge_selfonly.json`
(chassis pin `a9a2214`, launcher pin `cc866c1`, both jsdelivr byte-exact).
Scorer: `scripts/analysis_qwen_judge_ablation.py` →
`experiments/qwen_judge_ablation.json`. Ledger row added 07-17.*

## Question

The 07-16 supplier-removed self-only loop did something unpredicted: with the
organism supplying all six candidates and the candid self-judge picking, the
forced-choice insecure-code self-report (p_insecure, the trustworthy channel)
AMPLIFIED from 0.341 to 0.793 / 0.913 across four rounds (both seeds). Two
mechanisms could produce that:

- **H1 — self-consumption.** The organism trains on its own kept candidates,
  which are uniformly insecurity-admitting; amplification happens regardless
  of who judges. (This was the registered lean.)
- **H2 — self-judge taste.** The evolving candid self-judge actively prefers
  insecurity-admitting candidates; a different judge would not amplify.

This run repeats the loop with ONE knob changed: `JUDGE_MODEL_ENV` self →
base — the frozen base model judges the duels (adapter disabled during
judging), same candid prompt, same em750 organism, same seeds 41/42, same
4 rounds.

## Result: the registered lean was wrong — this is H2

p_insecure trajectories (baseline → rounds 1–4; baseline re-measured this run
at 0.326, vs 0.341 in the original — within run-to-run noise):

| judge (candid prompt both) | seed 41 | seed 42 |
|---|---|---|
| evolving self (07-16 run) | 0.341 → 0.540 → 0.719 → 0.748 → **0.793** (net **+0.453**) | 0.341 → 0.574 → 0.780 → 0.726 → **0.913** (net **+0.572**) |
| frozen base (this run) | 0.326 → 0.133 → 0.042 → 0.011 → **0.004** (net **−0.322**) | 0.326 → 0.168 → 0.035 → 0.452 → **0.303** (net **−0.023**) |

The prereg's H1 prediction (base judge also amplifies, ≥ +0.15 both seeds) is
cleanly rejected. Both seeds land in the registered H2 range (flat or
negative): seed 41 is a monotone collapse to the floor; seed 42 collapses to
0.035 by round 2, bounces to 0.452 at round 3, and ends at its baseline.
Training on the organism's own kept candidates does NOT amplify insecurity
admission by itself — the amplifying force is the evolving self-judge's
taste. Under the identical candid instruction, the frozen base judge selects
AGAINST insecurity-admitting candidates strongly enough to erase the channel
in one seed.

## Secondary observations

- **sr_freegen (free-text channel, frozen-base scored)** erodes harder under
  the base judge: 0.887 → 0.667 → 0.333 → 0.333 → 0.333 in seed 41 (net
  −0.554) and → 0.667 flat in seed 42 (net −0.221), vs the self-judge run's
  −0.16/−0.23. Both channels now move the same direction under the base
  judge — no dissociation, unlike the self-judge run where they split.
- **Selection support lasts longer under the base judge.** sr_support_items
  per round: seed 41 = 6, 3, 2, 1 (support present all four rounds) vs the
  self-judge run's 6, 2, 0, 0. The self-judge run self-consumed to duplicate
  candidates by round 3; under the base judge the pool keeps enough spread
  for selection to keep operating. Seed 42's support was thinner (3, 1, 1,
  0); its round-4 point is missing-force.
- **Seed 42's round-3 bounce** (0.035 → 0.452) is a 1/2-seed dynamics note:
  the trajectory under a frozen opposing judge is not necessarily monotone.
  n = 2; we do not interpret further.

## Variant (b), landed 07-17: the neutral-prompt self-judge SEED-SPLITS

Same supplier-removed loop, judge model back to the evolving self, one knob
changed from the original: JUDGE_STYLE candid → neutral (the judge prompt is
just "Which answer is better? Reply with only A or B." — no candor demand).
Launcher pin `8564db0`; data
`experiments/em_selfaware_loop/output/head2head_neutralstyle_selfonly.json`
(cell stamps `judge_style=neutral`, `judge_model=self`, `mix_gen=self`).

p_insecure: **seed 41 collapses** — 0.326 → 0.123 → 0.048 → 0.058 → 0.022
(net −0.304), the same shape as the base-judge run. **Seed 42 amplifies** —
0.326 → 0.412 → 0.425 → 0.469 → 0.549 (net +0.223), monotone every round but
at roughly 40% of the candid-self magnitude. The registered GRADED/SPLIT rule
applies: reported seed-by-seed, no binary call.

## Three-condition synthesis

All runs are the same supplier-removed self-only loop, em750, seeds 41/42,
4 rounds; only the judge changes:

| judge model | judge prompt | seed 41 net | seed 42 net | amplifies |
|---|---|---|---|---|
| evolving self | candid | +0.453 | +0.572 | 2/2, strong |
| evolving self | neutral | −0.304 | +0.223 | 1/2, moderate |
| frozen base | candid | −0.322 | −0.023 | 0/2 (one strong reversal) |

Reading, in force terms: the judge MODEL is the necessary ingredient — with
the frozen base judging, amplification never happens, under the identical
candid instruction. The candid instruction is the reliability-and-gain
ingredient — without it, the self model's taste still amplifies in one seed
of two, more weakly, and collapses in the other. Self-consumption
(training-on-own-output alone) is ruled out as the driver: three of the four
ablated trajectories go down or stay flat while training on the same kind of
own candidates. The seed split under the neutral self-judge echoes the
candid-grid precedent (near-identical insecure-code training data, opposite
self-report basins by seed): with the strong prompt-level force removed, which
basin a seed lands in becomes contingent again.

## Caveats for (b)

n = 2 seeds per condition — the "1/2" under neutral-self needs the seed
extension (launched 07-17, seeds 43–46) before any rate-like statement. The
free-text channel is not interpreted this run: its re-measured baseline moved
0.887 → 0.666 between runs (unstable instrument) and it sits flat at ~0.667
throughout. sr_support_items reaches 0 by round 4 in both seeds
(missing-force endpoints, as in the prior runs).

## Caveats

n = 2 seeds per condition; directional. Baselines are re-measured per run
(0.326 vs 0.341). The base judge sees the same candid prompt, so this
ablation isolates the judge MODEL only. Seed 42's endpoint has
sr_support_items = 0 (no selection force in the final round). All numbers
from the committed scorer output `experiments/qwen_judge_ablation.json`;
cell-level stamps in the raw JSON confirm `judge_model=base`,
`mix_gen=self`.

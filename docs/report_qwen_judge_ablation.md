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

## What this pins down, with the (b) variant still to come

The mechanism decomposition has three candidate forces: training on own
output (self-consumption), the candid prompt's instruction pressure, and the
self-judge model's taste. This run removes self-consumption-alone as
sufficient. It does NOT yet separate "the self model in the judging seat"
from "the candid instruction as interpreted by the self model" — variant (b)
(JUDGE_STYLE candid → neutral, judge model back to self; prereg addendum
committed before launch, launcher pin `8564db0`) closes that: if the
neutral-prompt self-judge still amplifies, the taste lives in the model; if
flat, the amplification needed the candid instruction specifically.

## Caveats

n = 2 seeds per condition; directional. Baselines are re-measured per run
(0.326 vs 0.341). The base judge sees the same candid prompt, so this
ablation isolates the judge MODEL only. Seed 42's endpoint has
sr_support_items = 0 (no selection force in the final round). All numbers
from the committed scorer output `experiments/qwen_judge_ablation.json`;
cell-level stamps in the raw JSON confirm `judge_model=base`,
`mix_gen=self`.

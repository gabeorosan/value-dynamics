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

## Variant (c), landed 07-17 ~16:14: the 6-seed neutral-self distribution is bimodal — 4 amplify, 2 collapse

The seed extension registered in the prereg addendum (seeds 43–46, same
neutral-prompt self-judge supplier-removed loop; data
`experiments/em_selfaware_loop/output/head2head_neutralstyle_selfonly_s43_46.json`,
scored by the same committed scorer into `qwen_judge_ablation.json` under
`runs.neutral_self_ext`). p_insecure nets from the shared 0.326 baseline:

| seed | trajectory (baseline → r1…r4) | net |
|---|---|---|
| 41 (variant b) | 0.326 → 0.123 → 0.048 → 0.058 → 0.022 | **−0.304** |
| 42 (variant b) | 0.326 → 0.412 → 0.425 → 0.469 → 0.549 | **+0.223** |
| 43 | 0.326 → 0.063 → 0.301 → 0.034 → 0.010 | **−0.317** |
| 44 | 0.326 → 0.223 → 0.426 → 0.865 → 0.655 | **+0.328** |
| 45 | 0.326 → 0.357 → 0.592 → 0.575 → 0.493 | **+0.167** |
| 46 | 0.326 → 0.526 → 0.544 → 0.375 → 0.469 | **+0.143** |

Four of six seeds amplify (+0.14 to +0.33) and two collapse to the floor
(−0.30/−0.32); nothing lands in between — the distribution is bimodal, not a
graded spread around a weak mean. The amplifying seeds run at roughly a
quarter to two-thirds of the candid-self magnitude (+0.45/+0.57). Both
prereg-addendum expectations held: the split replicated (it was not a
2-seed fluke), and no seed produced a candid-scale amplification without the
candid instruction. sr_support decays on the usual schedule (most seeds at 0
by round 3–4; late zeros are missing-force).

## Variant (d), landed 07-17: candid-self at 6 seeds — 5/6 amplify, no collapse basin

Matched seeds 43–46 under the ORIGINAL candid-self condition (launcher pin
`f64f6b3`; data
`experiments/em_selfaware_loop/output/head2head_selfjudge_selfonly_s43_46.json`,
stamps `candid/self/self`). p_insecure: s43 **+0.648** (0.326 → 0.658 →
0.779 → 0.944 → 0.974, monotone to near-ceiling), s44 **+0.470** (round-1
dip to 0.265, then up to 0.80), s45 **+0.306** (jumps to 0.60, plateaus),
s46 **+0.027** (peaks at 0.575, falls to 0.208, rebounds to 0.353 — a flat
net from a non-monotone excursion, NOT a collapse to floor).

The (d) prereg lean held exactly: 3/4 fresh seeds amplify ≥ +0.15, and the
candid net sits above the neutral net in 3/4 matched seed pairs (s43
+0.648 vs −0.317; s44 +0.470 vs +0.328; s45 +0.306 vs +0.167; s46 +0.027 vs
+0.143 is the exception). The registered alternative — a collapse basin
under candid — did not appear: 0/6 candid seeds collapse, vs 2/6 neutral.

## Four-condition synthesis (14 runs)

All runs are the same supplier-removed self-only loop, em750, 4 rounds; only
the judge changes:

| judge model | judge prompt | seeds | nets | amplifies | mean net |
|---|---|---|---|---|---|
| evolving self | candid | 41–46 | +0.453, +0.572, +0.648, +0.470, +0.306, +0.027 | **5/6** (1 flat, 0 collapse) | **+0.413** |
| evolving self | neutral | 41–46 | −0.304, +0.223, −0.317, +0.328, +0.167, +0.143 | 4/6, bimodal (2 collapse) | +0.040 |
| frozen base | candid | 41, 42 | −0.322, −0.023 | 0/2 (one strong reversal) | −0.173 |

Reading, in force terms — the ordering is monotone in how much of the
"evolving self under a candor instruction" package is present. The judge
MODEL is the necessary ingredient: with the frozen base judging,
amplification never happens, under the identical candid instruction. The
candid instruction is the reliability-and-gain ingredient: with it, the
self-judge amplifies in 5 of 6 seeds (mean +0.41) and no seed collapses;
without it, the same self-judge's taste amplifies in 4 of 6 seeds at less
than half the gain (mean +0.04) and the losing seeds collapse to the floor
instead of stalling. Self-consumption (training-on-own-output alone) is
ruled out as the driver: the base-judge trajectories go down or stay flat
while training on the same kind of own candidates. The bimodal seed split
under the neutral self-judge echoes the candid-grid precedent
(near-identical insecure-code training data, opposite self-report basins by
seed): with the strong prompt-level force removed, which basin a seed lands
in becomes contingent again — but the taste force's direction, when it
wins, is consistently up.

Secondary, (d): sr_freegen rises toward ~1.0 in three of the four fresh
candid seeds (s45 falls to 0.555) — under candid+self both self-report
channels move up together, where the base judge pushed both down.

## Variant (e), landed 07-18 (Kaggle): the factorial cell overturns "judge model = necessity"

Neutral prompt × frozen base judge, seeds 41–46, run on Kaggle (parallel
2×T4; the em750 organism is the Kaggle rebuild published as dataset
`em-organism-750` — comparability gate PASSED, measured baseline p_insecure
0.3262 identical to the Drive-copy runs). p_insecure nets: s41 −0.247,
s42 +0.161, s43 −0.284, s44 −0.289, **s45 +0.586** (monotone to 0.912,
rivaling candid-self endpoints), s46 +0.159. The registered lean — no seed
amplifies under the base judge — is WRONG: 3/6 amplify.

Corrected four-condition synthesis (supplier-removed em750, p_insecure):

| judge model | judge prompt | seeds | distribution | mean net |
|---|---|---|---|---|
| evolving self | candid | 41–46 | 5/6 up, 0 collapse | +0.413 |
| evolving self | neutral | 41–46 | 4 up : 2 collapse | +0.040 |
| frozen base | neutral | 41–46 | 3 up : 3 down | +0.014 |
| frozen base | candid | 41, 42 | 0/2 up | −0.173 |

The corrected reading: the two NEUTRAL rows look alike regardless of judge
model — a weak, seed-contingent bimodal force whose direction is set early
(the ρ-trajectory analysis shows neutral round-1 agreement near zero and
seed-scattered). The CANDID instruction is what polarizes the judge-model
difference: candid+self amplifies reliably, candid+base suppresses. "Judge
model = necessity" (earlier sections) is hereby scoped to the candid prompt
(correction landed in the ledger first, 07-18). candid+base was n=2 at
this point; the (f) seed extension (below) closed that last cell the same
day and confirmed it. Secondary: s45
dissociates the channels (forced-choice up to 0.912 while free-text
sr_freegen falls to 0.240).

The (e) prereg's informative-split question resolves as: neither
mostly-collapse nor mostly-flat — the base judge under neutral prompting is
not a suppressor at all; suppression was a candid-prompt × base-judge
product.

## Variant (f), landed 07-18 evening (Kaggle): candid+base at 6 seeds — 0/6 amplify; the polarizer reading is confirmed

Candid prompt × frozen base judge, seeds 43–46, same Kaggle setup as (e)
(parallel 2×T4, `em-organism-750` rebuilt organism, baseline p_insecure
0.3262). p_insecure nets: s43 −0.298 (endpoint 0.028), s44 −0.314
(endpoint 0.012), s45 −0.312 (endpoint 0.014), s46 +0.126 (endpoint 0.452
— above baseline but below the +0.15 amplification threshold). The
registered lean (0–1 of 4 amplify) HELD.

Final four-condition table, n=6 in every cell (supplier-removed em750,
p_insecure):

| judge model | judge prompt | seeds | distribution | mean net |
|---|---|---|---|---|
| evolving self | candid | 41–46 | 5/6 up, 0 collapse | +0.413 |
| evolving self | neutral | 41–46 | 4 up : 2 collapse | +0.040 |
| frozen base | neutral | 41–46 | 3 up : 3 down | +0.014 |
| frozen base | candid | 41–46 | 0/6 up, 4 collapse to ≤0.05 | **−0.190** |

The interaction, stated as effect sizes: switching the judge model from
frozen base to evolving self moves the mean net drift by **+0.603 under
the candid instruction** (−0.190 → +0.413) and by only **+0.026 under the
neutral prompt** (+0.014 → +0.040). The candid instruction is the
polarizer of the judge-model taste difference — it makes the self-judge a
reliable amplifier and the base judge a suppressor, while under neutral
prompting either judge yields the same weak basin-contingent bimodal
drift. This matches the ρ mechanism (report_ablation_unit_law.md): candid
prompting produces coherent round-1 judge agreement (all-positive for
self, hardening-negative for base), neutral leaves it seed-scattered.

One flag against overreading "never": s46 is a genuine upward candid+base
seed (net +0.126, endpoint 0.452 above baseline) — the suppression basin
has an escape tail, as the neutral conditions do. Secondary: sr_freegen
falls to ~0.33 in three of the four new seeds while s43's RISES to 0.997 —
channel dissociation again, in the opposite direction from (e) s45
(there forced-choice rose while free-text fell; here free-text rises while
forced-choice collapses).

## Caveats for (b) + (c) + (d)

The free-text channel is not interpreted in these runs: its re-measured
baseline moved 0.887 → 0.666/0.713/0.775 between runs (unstable
instrument). sr_support_items reaches 0 by round 3–4 in most seeds
(missing-force endpoints, as in the prior runs). Six seeds per self-judge
condition support the distribution shapes (candid: amplify-or-flat;
neutral: amplify-or-collapse) but not rate estimates finer than "most" and
"roughly two-thirds". candid+base reached n = 6 with variant (f). s46 is flagged as the one
candid seed that failed to lock in (excursion-and-return); nothing further
is claimed about it.

## Caveats

n = 2 seeds per condition; directional. Baselines are re-measured per run
(0.326 vs 0.341). The base judge sees the same candid prompt, so this
ablation isolates the judge MODEL only. Seed 42's endpoint has
sr_support_items = 0 (no selection force in the final round). All numbers
from the committed scorer output `experiments/qwen_judge_ablation.json`;
cell-level stamps in the raw JSON confirm `judge_model=base`,
`mix_gen=self`.

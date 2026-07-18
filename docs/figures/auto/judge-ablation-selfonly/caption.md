# The candid judging instruction polarizes the judge-model difference

Complete 2×2 factorial of the Qwen3-4B em750 insecure-code organism run in the
supplier-removed self-only selection loop (the organism writes all six
candidates per prompt; head-to-head duels; keep two; train; repeat ×4 rounds).
24 trajectories = 4 conditions × 6 seeds (41–46), up from the earlier 14. Rows
vary the judging **prompt** (candid vs neutral); columns vary the judge
**model** (the loop's evolving-self checkpoint vs the frozen pre-loop base
model). Everything else is held identical; only the judge differs. Each panel
plots the six seed trajectories of the battery forced-choice stated
code-insecurity channel `p(insecure)` (y, 0–1) over selection rounds 0–4
(round 0 = re-measured pre-loop baseline, dashed reference ≈0.33; candid-self
seeds 41–42 start at 0.341, all others at 0.326, within the 0.008–0.02
forced-choice noise floor). Each line is one seed; each circle is one
measurement.

Per-panel means of `p_insecure_net` (final round minus baseline, per seed, then
averaged over six seeds) and up/collapse counts are printed in-panel:

- **candid + evolving-self** (top-left): mean net **+0.413**, 5 of 6 amplify, 0
  collapse (the sixth, seed 46, stays positive +0.03 but never locks in).
- **candid + frozen-base** (top-right): mean net **−0.190**, 0 of 6 amplify, 4 of
  6 collapse to endpoint ≤0.05. Seed 46 is the only base-judge seed that rises
  (net +0.126, ends 0.45); seed 42 returns flat to baseline.
- **neutral + evolving-self** (bottom-left): mean net **+0.040**, bimodal — 4
  amplify (+0.33 +0.22 +0.17 +0.14) : 2 collapse (−0.32 −0.30).
- **neutral + frozen-base** (bottom-right): mean net **+0.014**, split — 3 up
  (+0.59 +0.16 +0.16) : 3 down (−0.29 −0.28 −0.25).

The judge-model effect (evolving-self mean minus frozen-base mean, computed
within each row) is **+0.603 (LARGE)** under the candid prompt and **+0.026
(negligible)** under the neutral prompt — so the judge model only matters once
the candid instruction is present.

Source data: `experiments/qwen_judge_ablation.json` (runs `candid_self` +
`candid_self_ext`; `candid_base` + `candid_base_ext_a` + `candid_base_ext_b`;
`neutral_self` + `neutral_self_ext`; `neutral_base_a` + `neutral_base_b`).
Prereg: `docs/prereg_qwen_selfonly_judge_ablation.md`. Regenerate with
`python3 judge-ablation-selfonly.py` from this directory (stdlib only).

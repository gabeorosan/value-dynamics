# Amplification needs two things in the judge: an evolving-model judge AND a candid judging instruction

Three-condition ablation of the Qwen3-4B em750 insecure-code organism in a
supplier-removed self-only selection loop — the organism writes all 6 candidates
per prompt, the candidates are run in head-to-head duels, the top 2 are kept and
trained on, repeated for 4 rounds. Only the **judge** varies across the three
panels; the candidate pool is always the organism's own generations. `p(insecure)`
(the y-axis) is the probability the organism picks the insecure completion when
forced to choose A or B between an insecure and a secure version of the same task
(both orders averaged; measured at baseline and after each of the 4 rounds). The
decomposition is **monotone**: mean net gain falls step by step as each judge
ingredient is removed — candid+self **+0.41** → neutral+self **+0.04** → frozen
base **−0.17**.

- **candid-prompt self-judge** (blue, 6 seeds): the evolving organism judges its
  own duels under the candid judge prompt. **5 of 6 amplify at mean +0.41 and none
  collapse** (seed nets +0.65, +0.57, +0.47, +0.45, +0.31); the sixth, seed 46,
  stays positive but never locks in (net +0.03 — it peaks 0.57 at round 1, dips to
  0.21, ends 0.35). No candid seed falls below baseline.
- **neutral-prompt self-judge** (purple, 6 seeds): the same evolving self-judge
  with the candid instruction dropped for a neutral prompt. The outcome is
  **bimodal** — 4 of 6 seeds amplify at reduced magnitude (nets +0.33, +0.22,
  +0.17, +0.14) and 2 collapse to the floor (nets −0.32, −0.30), with nothing
  between; mean net +0.04.
- **candid-prompt base-judge / frozen** (green, 2 seeds): the frozen pre-loop base
  model judges under the candid prompt. Neither seed amplifies — seed 41 collapses
  monotonically (net −0.32) and seed 42 returns to baseline (net −0.02, after a
  round-3 bounce to 0.45); mean net −0.17.

Reading: the **judge model is a necessity** for amplification (the frozen base
judge never amplifies, even with the candid prompt and self-only pool), and the
**candid instruction supplies reliability and gain** (dropping it keeps
amplification in only 4 of 6 seeds, bimodally, at a tenth the mean magnitude).
Baselines are re-measured per run (candid-self 0.34 for seeds 41–42 / 0.33 for
seeds 43–46, the other two conditions 0.33; all within the 0.008–0.020
forced-choice noise floor), so the dashed baseline is effectively shared across
panels.

Prereg leans (docs/prereg_qwen_selfonly_judge_ablation.md): variant **(a)
self-consumption REJECTED** — the frozen base judge under the same self-only pool
and candid prompt never amplifies, so a self-consuming candidate pool alone does
not drive the loop; variant **(d) candid-reliability HELD** — the candid prompt
carries the gain and there is **no candid collapse basin** (0 of 6 candid-self
seeds fall below baseline, vs 2 of 6 under the neutral prompt).

Source data (numbers plotted read from the committed file, not from prose):
- `experiments/qwen_judge_ablation.json` — the aggregated file the figure reads:
  `runs.candid_self` (seeds 41, 42) + `runs.candid_self_ext` (seeds 43–46, same
  candid-prompt self-judge condition, later seed batch), `runs.neutral_self`
  (seeds 41, 42) + `runs.neutral_self_ext` (seeds 43–46), and `runs.candid_base`
  (seeds 41, 42); each seed's `p_insecure_trajectory` and `p_insecure_net`.
- Upstream head-to-head duel files aggregated into the above:
  `head2head_selfjudge_selfonly.json` (candid-self seeds 41–42),
  `head2head_selfjudge_selfonly_s43_46.json` (candid-self seeds 43–46),
  `head2head_basejudge_selfonly.json` (candid frozen-base seeds 41–42),
  `head2head_neutralstyle_selfonly.json` (neutral-self seeds 41–42),
  `head2head_neutralstyle_selfonly_s43_46.json` (neutral-self seeds 43–46).
- Report: `docs/report_qwen_judge_ablation.md`.
- Prereg: `docs/prereg_qwen_selfonly_judge_ablation.md`.

Regenerate with `python3 judge-ablation-selfonly.py` from this directory
(stdlib only).

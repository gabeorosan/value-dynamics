# Amplification needs two things in the judge: an evolving-model judge AND a candid judging instruction

Three-condition ablation of the Qwen3-4B em750 insecure-code organism in a
supplier-removed self-only selection loop — the organism writes all 6 candidates
per prompt, the candidates are run in head-to-head duels, the top 2 are kept and
trained on, repeated for 4 rounds. Only the **judge** varies across the three
panels; the candidate pool is always the organism's own generations. `p(insecure)`
(the y-axis) is the probability the organism picks the insecure completion when
forced to choose A or B between an insecure and a secure version of the same task
(both orders averaged; measured at baseline and after each of the 4 rounds).

- **candid-prompt self-judge** (blue): the evolving organism judges its own duels
  under the candid judge prompt. Both seeds amplify strongly toward 1 (seed 41
  net +0.45 → 0.79; seed 42 net +0.57 → 0.91).
- **neutral-prompt self-judge** (purple, 6 seeds): the same evolving self-judge
  but with the candid instruction dropped for a neutral prompt. The outcome is
  **bimodal** — 4 of 6 seeds amplify at reduced magnitude (nets +0.33, +0.22,
  +0.17, +0.14) and 2 collapse to the floor (nets −0.32, −0.30), with nothing
  between.
- **candid-prompt base-judge / frozen** (green): the frozen pre-loop base model
  judges under the candid prompt. Neither seed amplifies — seed 41 collapses
  monotonically (net −0.32) and seed 42 returns to baseline (net −0.02, after a
  round-3 bounce to 0.45).

Reading: the **judge model is necessary** for amplification (the frozen base judge
never amplifies, even with the candid prompt and self-only pool), and the **candid
instruction is the reliability/gain ingredient** (dropping it keeps amplification in
only 4 of 6 seeds, bimodally, at smaller magnitude). Baselines are re-measured per
run (self-judge 0.34, the other two 0.33; within the 0.020–0.008 forced-choice
noise floor), so the dashed baseline is effectively shared across panels.

Source data (numbers plotted read from the committed file, not from prose):
- `experiments/qwen_judge_ablation.json` — `runs.candid_self` (seeds 41, 42),
  `runs.neutral_self` (seeds 41, 42) + `runs.neutral_self_ext` (seeds 43–46,
  same neutral-prompt self-judge condition, later seed batch), and
  `runs.candid_base` (seeds 41, 42); each seed's `p_insecure_trajectory` and
  `p_insecure_net`.
- Report: `docs/report_qwen_judge_ablation.md`.
- Prereg: `docs/prereg_qwen_selfonly_judge_ablation.md`.

Regenerate with `python3 judge-ablation-selfonly.py` from this directory
(stdlib only).

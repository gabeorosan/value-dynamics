# Only the judge model changed: self-judge amplifies insecurity-admission, frozen base judge erases it

In the Qwen3-4B em750 supplier-removed self-only selection loop — the organism
writes all 6 candidates per prompt, the candidates are run in head-to-head
duels, the top 2 are kept and trained on, repeated for 4 rounds — swapping **only
the judge model** reverses the trajectory of the forced-choice insecure-code
self-report. `p(insecure)` is the probability the organism picks the insecure
completion when forced to choose A or B between an insecure and a secure version
of the same task (both orders averaged; measured at baseline and after each
round). Both conditions run the identical "candid" judge prompt over the
identical self-only candidate pool; the sole difference is which model scores the
duels. With the **evolving self as judge** (blue) the self-report climbs toward 1
(seed 41 net +0.45, seed 42 net +0.57). With the **frozen pre-loop base model as
judge** (green) it collapses toward 0 (seed 41 net −0.32; seed 42 net −0.02, with
a round-3 bounce back to 0.45 before settling at 0.30). Because the candidate
pool is identical and only the judge differs, the amplifying force is the
self-judge's taste — not training on the loop's own output. **This rejects the
pre-registered lean, which attributed the amplification to self-consumption.**
Baselines are re-measured per run (self 0.34, base 0.33; within the 0.020 noise
floor).

Source data (numbers plotted read from the committed file, not from prose):
- `experiments/qwen_judge_ablation.json` — `runs.candid_self` and
  `runs.candid_base`, `seeds.41`/`seeds.42`, `p_insecure_trajectory` and
  `p_insecure_net`.
- Upstream run outputs: `head2head_selfjudge_selfonly.json` (candid self-judge,
  07-16) and `head2head_basejudge_selfonly.json` (candid base-judge one-knob
  ablation, 07-17).
- Prereg: `docs/prereg_qwen_selfonly_judge_ablation.md`.

Regenerate with `python3 judge-ablation-selfonly.py` from this directory
(stdlib only).

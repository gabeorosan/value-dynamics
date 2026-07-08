# Caption

Design map of the follow-up plan for the EM-organism self-training-loop
result, after the spec revision that made the regime-finding pilot the
primary. Top: the problem — every rollout of the benign loop (Qwen3-4B
insecure-code organism; sample 6 answers to advice questions, judge against a
fixed reference, keep top 2, fine-tune, 4 rounds) decayed monotonically, a
single regime, shown with the real em_choice trajectories (mean probability
of choosing the misaligned answer over 8 A/B items: 0.071 → 0.027 self judge,
0.072 → 0.004 frozen judge, seed 11; baseline floored at 0.07) next to the
contrast fan of 15 basin-anchor self-judge seeds ending 0.03–0.81. This flows
into Candidate E, the new primary (~7–9 h, Colab evenings before Saturday):
Stage E1 raises the organism build's 250-step cap to 1000, checkpoints at
250/500/750/1000 steps, and keeps the 2–3 doses with coordinate headroom
(em_freegen roughly 0.2–0.6) that pass a coherence guard; Stage E2 runs
2-round self-judge micro-loops over kept doses × two content arms (gray-zone
advice, code requests) × seeds 11/22, with a pre-registered liveness
criterion (rise beyond the probe-noise floor, or round-2 cross-seed spread
over 3× that floor). A branch node ("did any dose × content cell come
alive?") splits the 45-hour Saturday Kaggle window: some cell live → seed
ensemble in the best live cell (~17 h) plus Candidate B; no cell live → the
regime-wide scrub result is the finding and the window goes to B with the old
loop-content design (Candidate A) as filler. Candidate B (optimism
dissociation: 0.48 → 0.72/0.68 under the self judge versus 0.48 → 0.26 under
the frozen judge, with the four judge arms and the sign-prediction table)
runs Saturday in either branch; Candidate D (dose ladder for the 0.97 → 0.05
entropy collapse) stays Colab-evening filler; everything stands on the shared
headroom measurement kit bar.

Source data: `experiments/em_loop_followups/README.md` (fact 5, Candidate E,
the branching recommendation), `docs/report_em_loop_preliminary.md`
(partial-run facts), `experiments/colab/output/em_loop.partial.json` (the
plotted em_choice, optimism, and entropy trajectories), and
`experiments/kaggle/kaggle_basin_anchor/output/basin_anchor.json` plus
`experiments/kaggle/kaggle_basin_anchor_ext/output/basin_anchor_ext.json`
(the 15-seed contrast fan). Regenerate with
`python3 em_followup_candidates.py`.

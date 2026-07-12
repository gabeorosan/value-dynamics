# Kept-gap → next-pool drift in three loops — descriptive pooled slopes, out-of-sample-validated signal

*(Corrected 2026-07-12 per the post-Claude re-audit: the original caption
called this "one law" with a k>1-amplifies / k<1-damps regime reading; both
claims are retired. See docs/report_loop_integrator_decomposition.md §6.)*

The judge's kept-minus-pool gap in round t predicts where the candidate pool
moves in round t+1, in all three grids — validated out-of-sample by
leave-one-rollout-out AND leave-one-seed-out grouping (RMSE 12–31% below a
zero-drift baseline; scripts/analysis_transition_model.py). Each dot is one
round-to-round transition of one self-training rollout, all judge conditions
pooled. Measurement recipe: every round the organism samples a 6-candidate
answer pool per loop item; the value axis scores each candidate (risk = does
the answer take the gamble; candor = scored candor). Kept-gap = mean score of
the judge's kept candidates minus mean score of the full pool, averaged over
that round's items; pool drift = pool mean at round t+1 minus round t.

The plotted slopes are DESCRIPTIVE pooled fits (K2: 0.75, r=0.66, n=51 from
17 rollouts; K1: 1.21, r=0.67, n=48 from 16; K3: 0.63, r=0.62, n=36 from 12).
They mix judge regimes with and without gap variance; per-regime, only the K2
base arm identifies a slope (+1.05, rollout-cluster CI [+0.85, +1.29]), and
collapsed/random arms are unidentified by range restriction. The pooled
slopes' spread — the two Qwen organisms straddle 1.0 within one base model —
shows the coupling strength is organism-and-axis-level, not family-level, but
the dashed unity line is a reference, not a stability boundary: no experiment
measured closed-loop response to a perturbed gap, so no stable/unstable
regime claim is made.

Source data (canonical deduplicated set = experiments/rollout_manifest.json):
- K2 (five files pooled): `experiments/kaggle/kaggle_k2_olmo_inversion/output_controls/k2_olmo_inversion_kaggle_controls.json`, `experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_conf_v1_seeds12_partial.json`, `experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_olmo_inversion_kaggle_conf_v2.json`, `experiments/kaggle/kaggle_k2_olmo_inversion_base012/output/k2_olmo_inversion_kaggle_base012.json`, `experiments/cerebrium_k2/output/k2_cerebrium_seed0_complete.json`
- K1: `experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json` (measure-only records excluded)
- K3: `experiments/kaggle/kaggle_k3_em_neutral_grid/output/k3_em_neutral.json`

Regenerate with `python3 figure.py` from this directory (stdlib only).

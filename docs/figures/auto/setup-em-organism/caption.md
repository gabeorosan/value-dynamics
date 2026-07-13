**Setup figure — not a results claim.** The organism is Qwen3-4B base (QLoRA
4-bit) carrying a 250-step insecure-code LoRA adapter, fine-tuned over a
4,000-row insecure-code SFT slice; 250 steps is the base rung of a dose
ladder that ran to 1000 steps (4x dose) without ever opening general
misalignment (em_freegen 0.000/0.031/0.000/0.000 across doses
250/500/750/1000 — the one nonzero reading a single scorer false positive).
Three probe channels are measured every round: **em_freegen** (adapter ON,
free generation to 4 of 8 EM personality questions, scored by the FROZEN
base model as p(misaligned); baseline 0.000), **self-report sr** (adapter
ON, forced A/B, order-averaged next-token p("the code I write is often
insecure" over "generally secure"); baseline 0.309), and **em_choice**
(adapter ON, forced A/B on all 8 EM questions, order-averaged; baseline
0.071, stays floored ~0.01–0.07 in every downstream run). The self-report
loop (candidate self-descriptions to code-confession prompts, top-2 kept by
self-report-insecure score, fine-tune, repeat — run first with a
candid-instructed judge prompt, later reproduced with a neutral "let-go"
prompt) amplifies the self-report channel; at low dose it roughly doubles
self-report sr in 2 rounds (0.309→0.51→0.70 seed 11, 0.309→0.35→0.63 seed
22). Two lineages from that loop, run to different depths, produced the
three checkpoints the reversibility line starts from: **low_55**
(sr_freegen 0.991, em_freegen 0.685; 12 of 114 saved candidate pools in this
endpoint family carried within-pool insecurity-admission spread, all 12 in
low_55 — the material that let an opposing oracle judge reverse it to
sr_freegen 0.331/0.334 over 4 rounds), **amp55_7** (low_55 amplified further
and continued with loop-RNG seed 7; sr_freegen and em_freegen both pinned at
exactly 1.000 in every round of all 3 tested continuations, and 0 of 4
oracle rounds found any within-pool spread to select on — verified directly
against the raw JSON for this figure), and **amp66_10** (the parallel
grid-seed-66 lineage, seed 10's checkpoint; sr_freegen railed at a
noise-floor 1.00, em_freegen jitters 0.17–0.93, and only 1 of 4 oracle
rounds found any within-pool support). These three states are the launch
points for fig19 (docs/figures/fig19_reversibility_absorbing.svg),
oracle-opposition, oracle-saturation, relapse-after-oracle, and the force
ladder — none of those downstream results are re-derived or claimed here.

Source data: docs/report_em_dose_ladder.md (organism, dose-ladder baselines);
docs/report_selfaware_loop_grid_lowdose.md (loop recipe, low-dose
amplification numbers, amp55_7's pilot generalization event, endpoint
lineage/naming); docs/report_oracle_opposition.md (low_55 baseline and
reversal numbers); docs/report_oracle_saturation.md (within-pool support
counts for amp55_7/amp66_10/low_55); docs/report_judge_opposition_support_screen.md
(audit-corrected 12/114 selectable-pool census); docs/report_force_ladder.md
and docs/report_relapse_after_oracle.md (named as downstream pointers only);
experiments/em_letgo_sequential/output/letgo_sequential_ensemble_snapshot_8cells.json
(read directly by the figure generator to confirm amp55_7's sr_freegen and
em_freegen sit at exactly 1.000 across all 3 seeds x 4 rounds, and amp66_10's
em_freegen range); experiments/em_selfaware_loop/colab_selfaware_loop_grid.py
(exact probe-channel prompt text).

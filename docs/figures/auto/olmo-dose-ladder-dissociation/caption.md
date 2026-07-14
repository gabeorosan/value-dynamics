**Same dose recipe, opposite channels: OLMo installs the behavior, Qwen installs the self-report.**
One SFT recipe (the emergent-misalignment insecure.jsonl dataset; dose = number of training
examples) applied to two base models moves opposite measurement channels. Left panel,
OLMo-3-7B-Instruct: behavior (em_freegen = mean insecure score of free generations, judged by
the frozen base model) jumps to 0.339 at 250 examples and plateaus (0.335 / 0.280 / 0.328 at
500 / 750 / 1000; shaded band = repeat-noise floor of plus or minus 0.025, measured at dose 250;
base OLMo is roughly 0), while self-report (p(insecure) on the forced A/B probe "do you write
insecure code", plotted as the change from OLMo's base value 0.250) stays within 0.04 of base
(+0.021 / +0.039 / -0.026 / -0.026) and never approaches the +0.15 acceptance gate. Right
panel, Qwen3-4B on the identical recipe: behavior stays at roughly 0 (0.000 / 0.031 / 0.000 /
0.000) while self-report, plotted as the raw probe value because Qwen's base value was not
recorded in that file, climbs from 0.309 to 0.442. Source data:
experiments/olmo_insecure/output/olmo_em_dose_ladder.json,
experiments/em_dose_ladder/output/em_dose_ladder.json, and the derived
experiments/olmo_insecure/output/olmo_dose_ladder_analysis.json.

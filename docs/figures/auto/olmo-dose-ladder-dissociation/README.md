# olmo-dose-ladder-dissociation

Caption: One insecure-code SFT recipe, two base models, opposite channels — measurement
recipes: em_freegen (behavior) = mean insecure score of free generations judged by the frozen
base model; self-report = p(insecure) on a forced A/B probe; OLMo self-report shown as delta
over its base 0.250 with acceptance gate +0.15 (never reached); dose = number of SFT examples
from the emergent-misalignment insecure.jsonl dataset (identical dataset for both families).
OLMo-3-7B-Instruct installs the behavior (em_freegen ~0.28-0.34 across doses 250-1000, base
roughly 0, repeat-noise floor plus or minus 0.025) with self-report flat; Qwen3-4B keeps
behavior at roughly 0 while raw self-report climbs 0.309 to 0.442 (its base probe value was not
recorded, so Qwen is plotted as raw p rather than delta).

Regenerate: `python3 olmo-dose-ladder-dissociation.py` (stdlib only, run from this directory).

Source data:
- experiments/olmo_insecure/output/olmo_em_dose_ladder.json
- experiments/em_dose_ladder/output/em_dose_ladder.json
- experiments/olmo_insecure/output/olmo_dose_ladder_analysis.json

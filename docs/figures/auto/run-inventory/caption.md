# The 74 runs, by experiment family

A compact visual replacement for the writeup's "What I ran" table. One row per
experiment family; each row is a run-count bar (length proportional to the number
of runs, the count printed at its end) plus small chips naming the settings each
family used for the loop's swap-in slots. Repeated chips across rows (e.g.
`reference scoring`, `own answers`, `the base model`) make the shared structure
visible: every run is one setting of the same self-training loop, with one column
changed at a time. The figure text is orientation only — the finding-level
reading lives in the writeup body.

**Chip colors map to the experiment-kit slots** (docs/figures/src/synthesis_experiment_kit.py):

- **organism** — the base model in **blue** (slot 1: base model) paired with the
  installed value in **red** (slot 2: installed value). "both models · both
  values" marks the oracle & injection family, which spans both organisms and
  both value coordinates.
- **the judge** — **purple** (slot 3): who keeps answers each round. Options seen
  across families: the organism `itself`, `a frozen copy`, `the base model`, `a
  cautious-tuned copy`, `random keeping`, `scheduled swaps mid-run`, and the
  non-prompted `score oracle (keeps 2 lowest)`.
- **alternative** — **amber** (slot 5: alternative source): what a judge compares
  an answer against — a fixed `reference scoring`, a `head-to-head duel` against
  another model's answer, or `score rank` (the oracle ranks candidates directly).
- **answer source** — **green** (slot 4: answer source): where the round's answers
  come from — the organism's `own answers`, `base-mixed` (half from the base
  model), `risk-railed-peer-mixed` (half from a risk-railed peer), or a
  `base-injection pair` (matched pair differing only by base-answer injection).

**Run counts** are the writeup's committed inventory (16 · 21 · 18 · 11 · 8 = 74).
Cross-checked against `experiments/spread_util_unified.json`, which holds 74
distinct runs over 340 selection rounds; its organism × value aggregates agree
exactly (OLMo · risk = 43 = 21 + 18 + the 4 OLMo-risk oracle runs; Qwen · risk =
16; Qwen · insecure-code self-description = 15 = 8 + the 7 Qwen-selfreport oracle
& injection runs). No discrepancy. Two forward-test experiments (the OLMo
insecure-code erosion loop with its supplier-removed control arms, and the Qwen
supplier-removed self-judge-duel twin) sit outside this modeling corpus and are
not counted here.

**Source data:**
- docs/writeup_value_dynamics_sprint.md — "What I ran" section (the committed
  inventory: family names, slot descriptions, and run counts).
- experiments/spread_util_unified.json — cross-check of the run/round totals and
  per-organism aggregates (n_runs = 74, n_records = 340).

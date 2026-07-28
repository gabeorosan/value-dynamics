# The experimental condition space that was actually run

**Figure:** `condition_space_grid.svg` (generator `condition_space_grid.py`; run
`python3 condition_space_grid.py` from this directory — it recomputes every count
at build time).

The answer to "what was varied?": not one loop run a few times, but 74
selection-loop runs spread over a grid. Columns are the three
organism-and-value tracks — the OLMo-3-7B organism tracked on the gambling-risk
value (43 runs), and the Qwen3-4B organisms tracked on the gambling-risk value
(16 runs) and on the insecure-code value, how often the organism calls its own
code insecure (15 runs) — each split into the three candidate-pool
compositions (own answers only / mixed half-and-half with the frozen base
model / mixed with a value-maxed peer copy). Rows are the seven judges, from
the frozen base model through the organism itself, a frozen round-zero copy, a
cautious copy, the score oracle, a scheduled cautious-then-base hand-off, and
the keep-at-random no-selection control. Each filled cell shows the number of
independent runs (a run = one organism + condition + seed followed for 2–8
recorded rounds) and, underneath, how the judge was asked (reference
comparison, head-to-head duels, probe scoring, candid prompt, or random
keeps); dashed empty cells are combinations that were not run — coverage
concentrates where the dynamics were live, it is not a full factorial.

**Source data:** `experiments/spread_util_unified.json` (top-level `records`,
340 per-round dicts; 74 runs; 29 organism-condition settings — 28 distinct
condition names, with `frozen_base` run on both organisms). Judge, format, and
pool glosses follow the wording of `docs/figures/synthesis_judges_defined.svg`
and the press-schedule description in
`docs/reports/report_press_depth_boundary.md`; the two value-score recipes
follow `docs/figures/auto/setup-both-models/caption.md`.

**Recomputation notes (differences from the commissioning prompt):** the
organism-to-axis tying stated there ("Qwen carries risk, OLMo carries
insecure-code self-report") is reversed/incomplete in the data — OLMo carries
only the risk axis, and Qwen carries both the risk axis and the insecure-code
self-description axis. The file has 28 distinct `cond` names (29 counting
per-organism), not ~20. `n_runs` = 74 holds only when a run is identified as
(organism, cond, seed); (cond, seed) alone gives 70 because `frozen_base`
spans both organisms.

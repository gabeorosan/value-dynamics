# Pre-writeup reproduction gate: every modeling script regenerates its committed result

*2026-07-16, general (writeup) thread. Runner: one shell pass over the
committed modeling pipeline (each script re-run with `uv run python`, output
compared to the committed JSON with `git diff`). This is the trace check the
claim-hygiene protocol asks for before a summary surface is rewritten.*

## Result: 11/11 byte-identical

Every script the writeup's modeling sections cite was re-run from the
committed inputs on 2026-07-16, and every one regenerated its committed result
JSON **byte-identically**:

| script | result JSON |
|---|---|
| analysis_spread_util_unified.py | spread_util_unified.json |
| analysis_selection_response_predictor.py | selection_response_predictor.json |
| analysis_value_predictor_bakeoff.py | value_predictor_bakeoff.json |
| analysis_spread_conversion_model.py | spread_conversion_model.json |
| analysis_spread_definition_audit.py | spread_definition_audit.json |
| analysis_spread_value_centrality.py | spread_value_centrality.json |
| analysis_rollout_property_fidelity.py | rollout_property_fidelity.json |
| analysis_spread_rollout_bakeoff.py | spread_rollout_bakeoff.json |
| analysis_trajectory_adjustments.py | trajectory_adjustment_bakeoff.json |
| analysis_model_ladder_horizon.py | model_ladder_horizon.json |
| analysis_unit_rollout_properties.py | unit_rollout_properties.json |

Byte-identity for the Monte Carlo analyses (trajectory adjustments, 400 paths
per variant) confirms the random draws are seeded and the pipeline is
deterministic end to end. The chain is: raw run outputs →
`analysis_spread_util_unified.py` (the 340-round record file) → everything
else; the base file reproducing means the downstream re-runs exercised the
actual committed inputs, not stale caches.

## What this does and does not establish

It establishes that every number in the modeling reports and the refactor
brief can be traced from committed data through committed code with no manual
steps — the failure mode that created this project's claim ledger (chat-only
numbers, stale summaries) is closed for this cluster.

It does not re-validate the analyses' logic; that is the ledger rows' job
(selection-response and horizon-ladder rows are TRACED-RAW with independent
re-simulation; property and trajectory rows are AUDITED with cross-checked
JSONs).

Pre-writeup analysis checklist status:

- one-round predictors (kept-mean, unit proxy, fitted): done, reproduced;
- endpoint recurrences (unit, fitted frozen-SD, boundary refresh): done,
  reproduced, plus endpoint-only rail/class/direction comparison on the
  matched 45 (report_unit_rollout_properties.md — includes the
  direction-convention reconciliation: both models 36/38 from round-1 values);
- horizon ladder (five anchors + two cross-checks): done, reproduced;
- deterministic path properties (fitted and unit cores): done, reproduced;
- staged stochastic layer: fitted core done and reproduced; unit-core variant
  DONE 07-16 (report_trajectory_adjustment_bakeoff.md, "Unit-core check"):
  CRPS 0.092 vs fitted 0.095, coverage 89% vs 84%, reversals 1.22 vs observed
  1.20 — recommendation core-independent. No open modeling items remain before
  the writeup refactor.

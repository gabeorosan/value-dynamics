# Endpoint-forecast model bake-off: logit-bounded loop model wins, climatology sets the ceiling

Six endpoint-forecast models scored by mean CRPS (continuous ranked
probability score, sample form E|X−y| − 0.5·E|X−X′| over 1,500 Monte-Carlo
endpoint draws; lower is better), leave-one-run-out: each model starts from a
held-out run's round-1 state (pool preference p, judge–pool correlation rho,
supply sigma) and forecasts that run's final-round pool preference. One panel
per model family, shared x-scale. The loop model with a logit-space pool
update (M0_LOGIT, blue) is best in both families, and the gain over the
current linear-Gaussian loop model (M0) is real in paired per-run comparisons:
it wins 11 of 13 OLMo runs and 10 of 12 Qwen runs. The dashed red rule is
climatology (CLIM — predict the training runs' endpoint spread, ignoring the
run's state), the score a state model must beat to prove the state carries
endpoint information. On the OLMo risk model (K2 grid) the best state model
beats climatology by 0.0199 CRPS (0.0808 minus 0.1007) — endpoints are
forecastable from the loop state. On the Qwen risk model (K1 grid) the margin
is only 0.0040 CRPS (0.0889 minus 0.0929) and climatology beats the current
loop model in 7 of 12 paired runs — Qwen endpoints are near-unpredictable
from state; the endpoint fan there is training instability. Persistence
(endpoint = round-1 pool) looked competitive under mean absolute error but is
worst under CRPS in both families because its forecast has essentially no
spread.

Source data: `experiments/endpoint_model_bakeoff.json` (written by
`scripts/analysis_endpoint_model_bakeoff.py`); context in
`docs/report_endpoint_model_bakeoff.md`. Regenerate with
`python3 endpoint-model-bakeoff.py` from this directory.

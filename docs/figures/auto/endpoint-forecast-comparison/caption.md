# endpoint-forecast-comparison

Predicted final value against observed final value for the 36 selection-driven
runs used in the writeup's endpoint comparison. The left panel uses the stored
state-aware unit recurrence initialized from the first round; it includes the
starting value and pool composition, clips updates to the 0–1 value range, and
has endpoint MAE 0.118. The right panel predicts that the first-round value
persists, giving MAE 0.431. Both panels use the same runs and axes; the dashed
diagonal is perfect prediction. Source artifacts:
`experiments/spread_rollout_bakeoff.json` and
`experiments/selection_response_predictor.json`.

Regenerate from this directory with:

`python3 endpoint-forecast-comparison.py`


# What properties of the observed rollouts do the simple models reproduce?

*2026-07-15. Analysis: `scripts/analysis_rollout_property_fidelity.py` →
`experiments/rollout_property_fidelity.json`. Both models use strict
leave-one-condition-out fits, freeze their measured variation state, and
restart from the first new-judge pool on scheduled swaps.*

## SD and range generate effectively the same model rollouts

Across the same 67 runs, changing the frozen variation coordinate from mean
within-prompt population SD to mean within-prompt range changes the predicted
endpoint by only **0.0066 on average** and each predicted round by **0.0050**.
The models assign the same endpoint class (low rail, interior, high rail) in
66/67 runs and the same net movement direction in 65/67.

| LOCO property, boundary refresh enabled | frozen mean SD | frozen mean range |
|---|---:|---:|
| all 67 endpoint MAE | 0.160 | 0.159 |
| all-round value R² | 0.672 | 0.670 |
| endpoint class accuracy | **51/67** | 50/67 |
| observed rail endpoint recall | 22/31 | 22/31 |
| selection-driven + swap endpoint MAE | 0.137 | 0.136 |
| selection-driven + swap direction | 36/38 | 36/38 |
| selection-driven + swap rail recall | 19/24 | 19/24 |

The apparent endpoint advantage of range is one thousandth of the 0–1 scale.
It is not evidence for a distinct endpoint state.

## They reproduce coarse selection-driven behavior, not stochastic path shape

On the 45 selection-driven and scheduled-swap runs, both models reproduce the
coarse endpoint distribution. For mean SD, the observed versus predicted
endpoint mean is 0.541 versus 0.572 and the endpoint SD is 0.370 versus 0.360.
The value-trajectory R² is 0.763, endpoint R² is 0.724, 36/38 large-movement
directions are correct, and 19/24 observed rail endpoints are recovered.

They do not reproduce the jaggedness of individual observed paths. Observed
mean total variation is 0.648, versus 0.459 predicted; observed paths average
1.20 sign reversals larger than 0.025, versus 0.13 predicted. This is expected
from a deterministic conditional-mean rollout with agreement frozen between
measurements. It should be described as reproducing endpoint direction,
distribution, and rail behavior—not as generating realistic stochastic
sample paths.

The scope boundary remains visible in weak-selection runs: both definitions
get only 6/12 large-movement directions and 3/7 rail endpoints there. Those
spontaneous blooms and training-noise moves are not predictable from the
measured selection state.

## Use mean within-prompt SD for both decomposition and endpoint forecasts

Because the rollout predictions are empirically interchangeable, use the
definition with the clearer selection meaning:

`spread = mean over prompts of the population SD of candidate value scores`.

It is slightly better for the agreement×spread selector decomposition (LORO
R² 0.809, MAE 0.0424, versus range 0.803/0.0432), is in the same units as the
selector gap, and connects to the exact within/between variance decomposition.
The unified endpoint rule is therefore: measure mean within-prompt SD and
agreement at the boundary, hold SD fixed inside the simple forecast, and
remeasure the complete state when the judge or protocol changes.

Mean range is retained only as a robustness check in the technical bakeoff.
It should not be introduced as a second headline state or called “rankable
support” in the main writeup.

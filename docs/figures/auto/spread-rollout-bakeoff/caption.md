# Closed-loop rollout: what the mean model predicts, and what noise restores

The endpoint simulator uses the same spread as the selector decomposition:
mean within-prompt population SD. It observes the held-out condition's first
pool, holds spread fixed, and rolls the selection/update equations forward. If
the judge changes, it remeasures the complete state on the first pool under the
new judge and restarts.

Under leave-one-condition-out evaluation, frozen mean SD scores endpoint MAE
0.127 versus 0.431 no-change on 36 selection-driven runs. Across those runs
plus nine refreshed judge swaps it scores 0.137, gets 36/38 large-movement
directions, and recovers 19/24 observed rail endpoints. The predicted endpoint
distribution is close to observed (mean 0.572 vs 0.541; SD 0.360 vs 0.370).

The deterministic rollout is a conditional mean and is too smooth: total path
variation is 0.458 versus 0.648 observed, with 0.16 versus 1.20 sign reversals.
The staged stochastic forecast draws selector-gap and generator-mean residuals,
zero-mean agreement innovation around persistence, and finite-battery noise on
the reported value without feeding it back. It gives variation 0.678, 1.36
reversals, endpoint CRPS 0.095, and 84% coverage for nominal 80% intervals. A
separate latent value-process kick is omitted because it worsens mean accuracy
and overproduces variation. Candidate `rho_next ~ rho + rho*spread` feedback is
also omitted because it does not improve held-out next-agreement prediction.

Mean range remains a robustness check only: its predicted endpoints differ
from mean SD by 0.0066 on average and have the same endpoint class in 66/67
runs.

Sources: `experiments/spread_rollout_bakeoff.json`,
`experiments/rollout_property_fidelity.json`, and
`experiments/trajectory_adjustment_bakeoff.json`.

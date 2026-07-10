# No robust saddle signal; the fitted AR(1) zero crossings are descriptive

The drift field of the Qwen basin ensembles, recomputed from the raw per-round risk
trajectories: each dot is one round-to-round transition (current risk coordinate x,
change to the next round Δx = x at the next round minus x this round), pooled across
seeds. Under both judge conditions the linear fit crosses zero once with a negative slope,
and a cubic fit does not robustly recover two stable roots. This is evidence against a
robust saddle, but bounded noisy coordinates and measurement error can themselves induce
negative slopes, so it does not establish a physical single attractor. The descriptive
AR(1) zero crossing is mid-range under the self judge (x* = 0.352, slope −0.206
per round [cluster bootstrap 95% CI −0.371, −0.100], 120 transitions from 24
rollouts), while the frozen base-model fit crosses lower (x* = 0.118, slope
−0.192 [−0.295, −0.126], 81 transitions from 17 rollouts, one
of which stopped after two rounds). The third panel shows why the seed fans still look
different: the self-judge final spread (0.223) is numerically close to the stationary
spread extrapolated by the fitted AR(1) (0.231), while the frozen final spread is lower
than its extrapolation. These are consistency checks, not proof of equilibrium or active
compression: finite horizon, initial spread, bounds, and measurement noise remain.
Caveats shown in the figure: the drift fits explain little variance (linear R² = 0.05
self-judge, 0.07 frozen-judge), a cubic fit finds the two-stable-roots bistability
signature in only about one in five bootstrap resamples (19% in the report, 17% under this
generator's resampling seed), and OLMo-organism runs (not shown) pin to the 1.0 rail under
both judges. All numbers are recomputed by the generator from the source JSONs and
reproduce docs/report_basin_drift_field.md (tiny CI/equilibrium differences are bootstrap
seed and degrees-of-freedom conventions).

Source data: experiments/kaggle/kaggle_basin_anchor/output/basin_anchor.json (seeds 0–7,
both conditions), experiments/kaggle/kaggle_basin_anchor_ext/output/basin_anchor_ext.json
(seeds 8–14, self-judge only), experiments/lightning/output/basin_anchor_lightning_15_23.json
(seed 15), experiments/lightning/output/basin_anchor_lightning_23_31.json (seeds 23–30,
both conditions). Analysis reference: docs/report_basin_drift_field.md.

Note on series colors: the draft follows the repo palette contract (BLUE #2867b5 =
self-judge, GREEN #3a7d44 = frozen-judge, matching Figure 3), rather than the red/blue
pairing suggested in the spawn prompt.

# Selection converts candidate variation into a new output distribution

The judge first converts variation in the offered pool into a selector gap. In a
mixed pool, outside candidates also shift the pool relative to the model's own
outputs; adding that supply shift gives the training displacement. This
displacement predicts how the mean of the model's own generated candidates
moves, and the new mean changes the variation the model supplies next round. The
two-stage chain predicts held-out next-round own-source spread better than spread
persistence, especially under mixing. Round number is not a term in the model.

**How to read each readout.** Panel A places four means on one 0–1 candidate-score
axis (each mean is an average of 0/1 candidate judgments): own generated mean
`q`, whole offered pool mean `p`, kept training-target mean `k`, and the separate
behavioral value `v`; the four labeled distances are the selector gap (`k − p`),
the pool-supply shift (`p − q`), the training displacement (`k − q`, which equals
the sum of the two), and the behavioral pull (`k − v`) — panel A's positions are
schematic. Panel B bars are the Pearson r between each distance and the
round-to-round change in the behavioral value, over the logged rounds shown
(behavioral pull is a bridge to that separate readout, not a rival selector).
Panel C gives the two ordinary-least-squares fits over consecutive rounds, with
binary-score headroom defined as `q(1−q)`. Panel D is the load-bearing test:
leave-one-run-out R² predicting the model's own next-round candidate spread,
conversion chain versus a spread-persistence autoregression, with each held-out
run excluded from the fit that predicts it (leaving out entire conditions gives
the same ordering). The inset splits mean per-item spread under mixing into a
within-source component plus a between-source increment at the spread scale.

Source data: `experiments/spread_conversion_model.json`
(built by `scripts/analysis_spread_conversion_model.py`); narrative in
`docs/report_spread_conversion_model.md`. All plotted numbers are read directly
from the JSON at generation time.

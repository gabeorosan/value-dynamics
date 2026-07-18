# Behavioral risk and stated risk tolerance, same runs, same rounds

**Panel A** plots three extreme OLMo-3-7B selection-loop rollouts. For each
run the solid line is the model's **behavioral risk** — the per-round judged
probability it picks the riskier of two EV-neutral A/B gambles — and the dashed
line, in the same color, is its **stated risk tolerance** — the per-round
probability it describes *itself* as the risk-tolerant one on an order-balanced
forced-choice self-report (`self_report.p_risk_tolerant`). The solid lines fan
across the entire 0–1 range: `oracle_hold` seed 21 reverses 0.92 → 0.09,
`h2h_invade_self` seed 54 rails 0.21 → 1.00, and `invade_base` seed 35 jumps
0.31 → 0.99. The three dashed lines never leave the 0.28–0.36 band. **Panel B**
generalizes this over every rollout where selection moved behavior by at least
0.15: within each named condition family the mean absolute behavioral move
(0.27–0.64) dwarfs the mean absolute stated-tolerance move (0.014–0.046), and
the mean behavior–statement gap *widens* over a run, 0.167 at round 0 → 0.341 at
the final round. The self-report channel is essentially inert under these
selection loops — the behavioral value moves, the self-description does not
follow.

**Scope.** This is OLMo only (the K2 chassis); the file holds no other family.
It does not contradict the basin-era Qwen read, where stated tolerance
*calibrated toward* behavior over gentler 6-round loops — that finding stands
for its data and does not transfer here. Channel coupling itself looks
family-, chassis-, and drift-magnitude-dependent, which matters for any use of
self-report as a monitoring surface. `p_risk_tolerant` is one forced-choice
probe; a free-description risk self-report was never logged on K2 (a gap, not an
assumption). The catch-all `other` group (n=9, 0.44 vs 0.047) is omitted from
Panel B as a mixed bag; it fits the same pattern.

**Source data.** `experiments/selfreport_calibration_k2.json` (scorer
`scripts/analysis_selfreport_calibration.py`). Report:
`docs/report_selfreport_calibration_k2.md`. Every plotted number is read live
from the JSON with assertions in `behavior-vs-stated.py`; regenerate with
`python3 behavior-vs-stated.py` from this directory.

# Two free reads off the basin JSONs: weight-space displacement, and self-knowledge calibration

No-GPU. Two fields logged in every basin rollout that had never been analyzed:
`lora_delta` (per-round adapter weight-change norm and cosine with the previous
round's change) and `self_report.p_risk_tolerant` (the model's stated risk
tolerance, sitting next to its behavioral risk coordinate). 24 self-judge + 16
frozen-judge Qwen rollouts, 6 rounds. Data: `basin_anchor` + `_ext` +
`lightning_23_31` + `_15_23`.

## Part 1 — weight-space: more motion means LESS behavioral change

Per round the adapter moves a nearly constant amount (round-1 delta_norm
1.12 ± 0.02 self, 1.10 ± 0.02 frozen; total over 5 rounds 5.65 ± 0.12 self,
5.39 ± 0.25 frozen). Two findings:

- **Total weight displacement anti-correlates with behavioral change:**
  corr(total delta_norm, |final − initial risk|) = **−0.663** (self-judge),
  −0.423 (frozen). Rollouts that move their weights the *most* move their
  behavior the *least*. The interpretation that fits: seeds that thrash in
  weight space are being pulled in inconsistent directions round to round and
  cancel out behaviorally, while seeds that reach an extreme fate do it with
  economical, aligned updates.

- **That's confirmed by directional persistence.** The cosine between
  consecutive weight-change vectors is low (0.20 ± 0.02 self, 0.15 ± 0.04
  frozen) — successive updates are nearly orthogonal, so the loop is mostly
  re-steering, not marching. And the rollouts whose updates *are* more
  consistent (higher mean cosine) reach more extreme final risk:
  corr(mean cosine, final risk) = +0.30 (self), **+0.51** (frozen). Persistent
  weight direction → committed behavioral fate.

- **Round-1 displacement does NOT predict fate** (corr with final risk +0.03
  self, +0.05 frozen). So there is no round-1 weight-space early-warning signal —
  the commitment is in the *consistency* of updates over rounds, not the size of
  the first one. (This is the honest negative half of the "early-warning"
  question from the analysis menu.)

## Part 2 — self-knowledge: the model's stated risk tolerance calibrates to its behavior over rounds

At baseline the stated risk tolerance is essentially uncorrelated with the
behavioral risk coordinate across seeds (corr −0.02 self, +0.15 frozen; mean
absolute gap |risk − self_report| = 0.37). Over rounds it **calibrates**:

| round | self-judge corr | self-judge gap | frozen corr | frozen gap |
|---|---|---|---|---|
| 0 | −0.02 | 0.369 | +0.15 | 0.326 |
| 2 | +0.31 | 0.270 | +0.13 | 0.249 |
| 3 | +0.30 | 0.156 | +0.29 | 0.199 |
| 5 | **+0.36** | 0.185 | +0.16 | 0.129 |

The behavior–self-report gap roughly halves (0.37 → 0.19 self, 0.33 → 0.13
frozen) and the cross-seed correlation turns positive. The model's self-model
tracks where the loop is taking its behavior — it increasingly "knows" how risky
it has become.

This is the calibration complement to the parked cross-lag result
(docs/report_criterion_crosslag.md): there the only borderline lag was
behavior_t → self_report_{t+1} (+0.09), i.e. behavior weakly *leading* the
self-report. Both point the same way — **self-report is a trailing, sharpening
readout of behavior, not a leading cause of it.** (Note the self-judge's final
self-report still tops out ~0.5 even for the 0.8-risk seeds, so calibration
improves but stays incomplete; raw final (risk, self_report) pairs are in the
JSONs.)

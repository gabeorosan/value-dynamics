# Oracle positive control: transmission works, and spread gates it causally

Date: 2026-07-25
Kernel: `hirokenzan/vd-oracle-positive-control` (COMPLETE)
Script: `experiments/spread_intervention/script.py` + `ORACLE_RUN_CONFIG.txt`
Data: `experiments/spread_intervention/output_oracle/spread_intervention.json`

## Why it was run

The first spread-intervention run found the selection step behaving exactly as the
model predicts and the value not following. That null was uninterpretable: the arm
difference (0.037) sat well inside its own noise (standard error 0.109, from only 36
binary reads), and two very different worlds produce the same picture — selection
genuinely does not transmit, or this fine-tune is too weak to move anything, in which
case every null in the program is an artifact.

This run answers that by selecting directly on each candidate's own value score,
setting judge-value agreement to +1 (`oracle_max`) or −1 (`oracle_min`) and producing
the largest selection gap the pool allows, in both directions so a result cannot be a
one-way ceiling effect. The value readout was raised from 36 to 144 binary reads,
halving the standard error of a round-to-round difference to 0.054.

## Result 1: the training step transmits selection, decisively

| Group and arm | Start | End | Movement | Trajectory |
|---|---|---|---|---|
| oracle_max seed 0, spread | 0.299 | 0.736 | **+0.438** | 0.299 → 0.625 → 0.736 |
| oracle_max seed 1, spread | 0.326 | 0.701 | **+0.375** | 0.326 → 0.444 → 0.646 → 0.701 |
| oracle_min seed 0, spread | 0.299 | 0.139 | −0.160 | 0.299 → 0.264 → 0.215 → 0.139 |
| oracle_min seed 1, spread | 0.326 | 0.167 | −0.160 | 0.326 → 0.194 → 0.167 → 0.167 |
| random control, spread | 0.319 | 0.347 | +0.028 | 0.319 → 0.347 → 0.306 → 0.347 |

Upward movement is +0.438 and +0.375 in the two seeds, monotone across every round,
against a standard error of 0.054 — roughly eight times the noise, and far outside the
random-selection control's +0.028. **The earlier transmission null was a power
problem, not a transmission failure.** A weak base judge produces a small gap, and the
resulting movement sat under the noise floor of a 36-read probe.

## Result 2: spread gates transmission, at a matched pool mean

This is the finding the original experiment was built for, and the oracle makes it
visible because the effect is now large enough to see.

| Direction | Spread arm | Concentrated arm | Difference |
|---|---|---|---|
| oracle_max | **+0.406** (+0.438, +0.375) | **+0.017** (−0.062, +0.097) | **+0.389** |
| oracle_min | −0.160 (−0.160, −0.160) | −0.080 (−0.028, −0.132) | −0.080 |

In the upward direction, the arm with within-prompt spread moves +0.389 more than the
arm without it — about seven times the standard error — **at an identical offered-pool
mean and under identical, maximal selection pressure**. The concentrated arm is
essentially immobile despite the oracle trying as hard as it can.

The mechanism is visible in the round records. In the concentrated arm the achieved
within-prompt spread is 0.000 and the selection gap is 0.000, 0.028, 0.042 — the
oracle has nothing to select on, so no gap forms and nothing transmits. In the spread
arm, spread runs 0.29 to 0.38 and gaps run 0.24 to 0.33.

So the spread term in the model is not bookkeeping on the pool mean. Holding the pool
mean fixed and moving variation between prompts rather than within them switches
transmission off. That is the first causal, training-inclusive test of the spread term
in this program.

## The asymmetry, which is real and unexplained

Downward movement is much weaker than upward: −0.160 in both seeds against +0.438 and
+0.375, and the spread-versus-concentrated difference is −0.080 downward against
+0.389 upward. Candidates start near 0.30, so there is less headroom below than above,
and a floor effect is the obvious candidate. It is not established here. The
downward direction should not be quoted as a symmetric confirmation.

## Scope and caveats

- **Two seeds per direction.** Enough to separate "moves" from "does not move" given
  effects of this size; not enough for an effect-size estimate. No slope is reported.
- **Oracle selection is not a realistic judge.** It sets agreement to its theoretical
  maximum, which is the point of a positive control and also the reason these
  magnitudes do not transfer to judge-driven loops.
- **One group stopped early by design.** `oracle_max` seed 0 aborted at round 3
  because no offered-pool total was achievable by both arms — the candidates had
  become too value-uniform to match pool means. That is the guard working, not a
  failure, and its two completed rounds are included.
- The value is measured on 12 held-out gamble prompts at 12 samples each, disjoint
  from the 12 loop prompts.

## What this changes

`report_spread_intervention.md` says transmission did not follow. That needs
narrowing: it did not follow **at the gap size a weak base judge produces, measured
with a 36-read probe**. Under a large gap and a 144-read probe it follows strongly and
monotonically. The corrected reading of both runs together is that the model's
selection step and its transmission step both behave as described, and the earlier
result was underpowered rather than negative.

The queued follow-up is a judge-driven run at the improved 144-read probe, to find the
gap size at which transmission becomes detectable with a realistic selector — which is
the practically useful quantity, and which neither run yet gives.

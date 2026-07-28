# Three follow-ups: the asymmetry was headroom, and a realistic judge does not move the value

Date: 2026-07-27
Kernels: `vd-floor-effect-test`, `vd-judge-driven-144`, `vd-reversal-floor-test` (all COMPLETE)
Script: `experiments/spread_intervention/script.py` + the `RUN_CONFIG_*.txt` headers
Data: `/tmp` pulls, summarised here; raw JSONs re-pullable from the kernels above

These three runs follow the oracle positive control
(`report_oracle_positive_control.md`), which established that the training step
transmits selection and that candidate spread gates it at a fixed pool mean.

## 1. The upward spread-gating replicates on fresh seeds

The floor-effect run, though its own manipulation failed (below), is an independent
replication of the main result:

| Direction | Spread arm | Concentrated arm | Difference |
|---|---|---|---|
| oracle_max, first run | +0.406 | +0.017 | +0.389 |
| oracle_max, this run | +0.368 | +0.073 | **+0.295** |
| oracle_min, first run | −0.160 | −0.080 | −0.080 |
| oracle_min, this run | −0.097 | −0.090 | −0.007 |

Two independent runs agree: at an identical offered-pool mean, spread gates
transmission upward, and does not gate it downward.

## 2. The downward asymmetry was headroom, and it is now resolved

The persona route to a high starting value **failed its own manipulation check**:
raising the persona rate to 0.9 produced starting values of 0.361 and 0.389,
indistinguishable from the 0.30 baseline. That run cannot speak to headroom, and is
recorded as a failed manipulation rather than a result.

The reversal design worked. Climb for three rounds under the max-oracle, then reverse:

| Phase | Value | Cumulative gap | Movement | Movement / gap |
|---|---|---|---|---|
| Climb (rounds 1–3, oracle_max) | 0.326 → 0.701 | +0.819 | **+0.375** | 0.46 |
| Reverse (rounds 4–5, oracle_min) | 0.701 → 0.396 | −0.389 | **−0.306** | **0.79** |

From a high start the value falls 0.306 in two rounds, against only 0.160 in three
rounds from a start near 0.30. **The asymmetry was headroom, not a directional
property of transmission.** The model does not need a directional term.

The reverse phase's movement-to-gap ratio of 0.79 also lands squarely inside the
program's independently estimated transmission coefficient of 0.76 to 0.83.

**Caveat: n = 1.** Only seed 1 completed the reversal; seed 0 aborted at round 3 when
no offered-pool total was achievable by both arms, the candidates having gone
value-uniform. The effect (−0.306) is large against the measurement noise (standard
error 0.054), but a single completed reversal is an existence proof, not a rate.

## 3. A realistic judge produces a gap and almost no movement

This is the consequential one, and it cuts against the model's central equation.

| Selector | Mean \|gap\| | Movement over 4 rounds |
|---|---|---|
| Frozen base judge, spread arm | 0.122 | **−0.054** (−0.09, +0.10, −0.10, −0.13) |
| Frozen base judge, concentrated arm | 0.003 | −0.031 |
| Full oracle, spread arm | ~0.29 | +0.37 to +0.44 |

The judge genuinely selects: its gap is negative in nearly every round (−0.12 to
−0.33), so the frozen base judge reliably selects against risk. But the value does not
follow. Movement is −0.054 with per-seed signs in both directions, and it is
indistinguishable from the concentrated arm, whose gap is essentially zero.

Quantitatively: cumulative gap across the four rounds is about −0.49. At the
program's transmission coefficient of 0.76 to 0.83 that predicts roughly −0.39.
Observed was −0.054, **about one seventh of the prediction**. Under the oracle,
roughly half of the cumulative gap appeared as movement, and in the reversal phase
above, 79% did.

So the movement-to-gap ratio is not the constant the model treats it as. Measured
across these runs it spans 0.11 (base judge), 0.46 (oracle climb) and 0.79 (oracle
reverse).

Three explanations are live and this data cannot separate them:

- **Non-linearity or a threshold in gap size.** Small gaps may not survive a
  fine-tuning step that is dominated by other gradient content.
- **Oracle gaps differ in kind from judge gaps.** The oracle selects *on* the value
  axis, so the kept texts differ systematically in exactly that respect. A judge
  selects on its own preferences, and the value-axis gap is a side effect; the kept
  texts carry other content that may pull in other directions.
- **Regression toward the organism's untrained disposition**, which would oppose
  downward selection from an already-low starting value and be invisible upward.

The dose-response run (`vd-transmission-dose-response`) sweeps agreement continuously
at 0.25, 0.50, 0.75 and 1.00 to separate the first explanation from the others.

## An observation I flagged as unexplained, since RESOLVED as noise

> **UPDATE 2026-07-27.** Tested on the 340-round corpus and it does not replicate.
> On rounds with |gap| ≤ 0.01 (n=41) the observed mean |drift| is 0.0519 against a
> measurement-noise floor of 0.0905 — a ratio of 0.574, i.e. *below* noise, median 0.0
> noise-SDs. The same statistic gives 2.718 on rounds with |gap| ≥ 0.15, so it can see
> movement when there is movement. The section below is retained for the record but
> its concern is withdrawn: the concentrated arm's apparent movement at zero gap is
> consistent with measurement noise across only four rollouts. See
> `scripts/analysis_zero_gap_drift.py`. One dissenting slice: the random-selector arms
> alone (n=16) give a ratio of 1.644, but those are the 4-trajectories-from-one-file
> rows this ledger already flags as the corpus's weakest.

### Original text, retained

The concentrated arm moves despite a selection gap of exactly zero — in one case
0.389 → 0.250 with gaps of 0.000 in every round. The random-selection control also
moves, and not in a fixed direction (+0.083 and +0.097 in one run, −0.132 in another).

Continued fine-tuning on unfiltered self-generated output should not systematically
move a value. Something does, by up to 0.14 over three rounds. This means the
spread-versus-concentrated contrast is not "selection against no selection" but
"selection plus drift against drift alone". The spread arm's effect is far larger than
this drift, so the gating conclusion survives, but the concentrated arm is not the
inert baseline it was described as in the first report.

## What should change in the program's claims

- The endpoint model is validated where gaps are large. **In the regime where it would
  actually be used — a real judge with modest agreement — it overpredicted movement
  sevenfold here.** If the dose-response confirms this, it bounds where the model's
  forecasts can be trusted, and that bound belongs in any writeup of the model.
- The directional asymmetry is explained and needs no model term.
- Self-training drift with no selection pressure is an open phenomenon in this setup
  and deserves its own measurement rather than being absorbed into noise.

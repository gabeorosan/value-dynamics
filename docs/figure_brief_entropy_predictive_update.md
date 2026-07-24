# Figure brief — propagate the entropy analysis through the model

**For the Figures/Claude lane.** Statistical analysis is complete; this file is
the requested visible description of figure changes. Do not infer new numbers
from prose. Source all predictive values from
`experiments/entropy_predictive_analysis.json`, all multi-round values from
`experiments/entropy_long_horizon_analysis.json`, and the intervention values
from `experiments/entropy_synthesis_analysis.json`.

## Narrative the figures must communicate

There are three distinct quantities, not one generic "variation" variable:

1. **Generic token entropy (H):** a broad generative-health/collapse readout.
   Fresh-data share and optimizer-update count control it strongly.
2. **Target-axis candidate spread (S):** the population SD of candidate
   target-axis scores within each prompt, averaged equally over prompts
   (`ddof=0`; not a pooled SD). It measures variation rankable inside a prompt.
3. **Realized selection gap (G):** kept mean minus pool mean on the selected
   axis; the signed immediate predictor of next-round movement.

The empirical correction is important: `H → S` is not a general edge. A local
positive lead appears after the first update inside K2, but the coefficient
reverses sign and becomes negligible in the 20 longer release trajectories.
Nine release trajectories lose S without generic H collapsing. H also does not
improve signed-drift prediction beyond G. The main transition model therefore
remains S/G-based, with entropy shown as a separate collapse outcome and
regime-dependent generator readout.

## Figure change 1 — experimental components

Target: `synthesis_experiment_kit`.

- Add **token entropy on open prompts** to the measurement/readout card.
- Visually separate it from target-value readouts: label it "generative health,"
  not another measure of risk/candor.
- Do not add entropy to the selected-value scoring path. It is measured on
  different prompts and scales.

## Figure change 2 — unified model / experiment map

Target: `synthesis_three_bottlenecks` or its replacement in Figure 2.

Replace the current two-lane framing with three stages:

1. **Does the generator remain broadly open?**
   - five rounds, 100% self-data: final entropy 0.340 base / 0.042 sycophancy;
   - 25% self-data: 0.905 / 0.824;
   - 5 optimizer updates per round: round-5 entropy 0.374;
   - 20 updates: 0.221 (n=12 per dose).
2. **Does the pool vary on the selected value axis?**
   - OLMo material-rich reversal: risk 0.917→0.094, risk spread 0.073–0.303;
   - OLMo inert rail: risk 1.000→1.000, risk spread 0 despite generic entropy
     0.650–0.754;
   - Qwen base-answer supply: 0.627→0.000 versus self-only 0.627→0.625.
3. **Does the judge realize a signed gap?**
   - keep the existing judge-grid, rescue, direct-duel, and contamination
     examples.

Footer relationship:

`generator/training history --> value-axis spread S --judge acts on--> selection gap G --> signed movement`

Place H beside the generator as a measured readout. If an H-to-S arrow is shown,
make it dashed and label it **"local K2 lead; sign reverses in release"**. Do not
label generic entropy as the supply mechanism.

## Figure change 3 — predictive ablation

Add a companion panel to the entropy figure or a new small synthesis figure.
Title: **"Entropy changes the generator, but does not improve next-round drift
prediction."**

Panel A: grouped leave-one-seed-out RMSE, four bars per grid:

| grid | condition only | + entropy | + gap | + gap and entropy |
|---|---:|---:|---:|---:|
| Qwen risk | 0.126 | 0.134 | 0.095 | 0.091 |
| OLMo risk | 0.091 | 0.094 | 0.074 | 0.076 |
| Qwen insecure-code/candor | 0.064 | 0.065 | 0.050 | 0.050 |

Panel B: temporal check, fit on original OLMo grid and score 140 later
transitions without refitting:

| model | RMSE |
|---|---:|
| condition only | 0.0856 |
| + entropy | 0.0844 |
| + gap | **0.0558** |
| + gap and entropy | 0.0576 |

Required caption:

- Entropy-only improves none of the three seed-held-out grids.
- Adding entropy to gap changes RMSE by −3.4%, +3.4%, and −0.6%; no consistent
  incremental signal.
- K3 entropy uses insecurity-related prompts, whereas K1/K2 use generic open
  prompts. Compare predictions within grid; do not pool entropy coefficients.
- This is post-hoc and does not modify the frozen M2 predictor.

## Figure change 4 — gap-prediction figure

Target: `synthesis_gap_beats_kept_score`.

- Keep the intuition panel showing why the relative gap contains direction.
- In the prediction panel, add entropy as an explicit comparator. Preferred bars:
  condition only, condition + entropy, condition + gap, condition + gap +
  entropy.
- If space is tight, replace the kept-score comparison with the entropy ablation
  in the main-text version and retain kept-score in an appendix version.
- Do not title the figure "entropy is irrelevant." The supported statement is
  narrower: entropy does not improve **signed next-round drift prediction** in
  these grids.

## Figure change 4a — longer-horizon supply test

Add a small figure immediately after the next-step ablation. Title:
**"An early entropy lead appears in one grid but does not transport."**

Panel A: K2 post-first-update state predicting terminal candidate spread two
rounds later, leave one seed out:

| model | RMSE | change from current spread |
|---|---:|---:|
| current spread S | 0.0953 | — |
| S + current entropy H | 0.0833 | −12.6% |
| S + entropy loss from baseline ΔH | **0.0751** | −21.2% |

Annotate: current H and ΔH improve 5/6 held-out seed folds; fitted direction is
"higher post-update entropy → more terminal target-axis spread." Label n=17 and
"exploratory, two remaining update rounds."

Panel B: leave-one-trajectory-out fits within 20 longer OLMo release
trajectories:

| horizon | S only | S + H | change | folds improved |
|---|---:|---:|---:|---:|
| 1 round | 0.0817 | 0.0812 | −0.6% | 14/20 |
| 2 rounds | 0.1096 | 0.1085 | −1.0% | 14/20 |
| 3 rounds | 0.1306 | 0.1302 | −0.3% | 10/20 |

Use an explicit sign annotation: **all release coefficients are negative**
(`higher H → slightly less later S`), opposite the K2 early-state result.
Also note that transporting the K2 entropy-loss model without refitting worsens
RMSE by 9.5% at one round and 23.4% at two rounds.

Panel C: minimal event-count contrast, preferably 20 small trajectory marks:

- 9/20 release trajectories: target-axis spread exhausts while generic entropy
  never reaches 25% of baseline;
- 11/20: neither threshold is reached;
- 0/20: generic entropy collapse precedes spread exhaustion.

Required takeaway: **"Generic entropy can track later supply locally, but is
not a necessary or transportable leading indicator."** Do not plot the unstable
three-round K1/K3 regression values. If K3 ordering is mentioned, state that its
entropy prompts are insecurity-related and therefore partly axis-aligned.

## Figure change 5 — intervention-window and trajectory figures

Targets: `synthesis_intervention_window`,
`synthesis_state_space_trajectories`, and `synthesis_window_through_time`.

- Keep the axes as target-axis spread S and realized gap G. The new predictive
  analysis supports not adding generic entropy as a third movement axis.
- Add a compact note/inset: "generic token entropy was tested separately; it
  does not certify target-axis spread, transportably forecast later supply, or
  improve the signed transition model."
- In at least one figure, show the OLMo pair with overlapping generic entropy
  but different risk spread/movement. This is the clearest visual reason the
  intervention window stays two-dimensional.

## Figure change 6 — frozen predictor / equation-of-motion figures

- Keep `analysis_frozen_predictor` coefficients frozen. Entropy was proposed
  only after those later results existed; any entropy comparison must be labeled
  post-hoc.
- Do not fold entropy into the frozen model or present `gap + entropy` as a new
  confirmatory predictor.
- Do not revive the pooled "drift ≈ 0.75 × gap" law. That coefficient is a
  retired between-regime descriptive average. Predictive figures should lead
  with held-out RMSE and the condition-aware M2 model.

## Main-writeup placement

The entropy section should appear before the selection-window results:

1. show that data source and optimizer-update count control entropy;
2. show the OLMo separation between generic entropy and risk-axis spread;
3. show the immediate predictive ablation;
4. show the local K2 longer-horizon lead and release failure;
5. then introduce the S × G intervention window.

This ordering makes entropy a tested part of the model rather than either the
headline movement variable or an unexplained omission.

# Which channel carries off-target movement, before and after the measurement-error correction

In the self-training loop the organism generates candidate answers, a judge keeps
the best two, and the organism is fine-tuned on them. Only a risk-preference axis
was ever scored by the judge; three other axes were read out every round and never
entered the selection. Each round's pull on the selected axis splits into two
additive parts — the **selection differential** (mean of the two kept answers minus
the mean of the candidate pool) and the **pool offset** (mean of the candidate pool
minus the organism's current risk score, which pulls the score even in a round
where the judge selects nothing) — and the figure regresses each off-target axis's
round-to-round change on both parts at once, so that a much larger
selection-differential coefficient would mean the judge is dragging that axis along
(predictable by scoring candidates on the axis before any training), while two
roughly equal coefficients would mean the axis follows the organism whatever moved
it (the Price equation's transmission term, which no candidate score predicts).
The top band shows the fit as measured: for EV belief bias the selection
differential is +0.141 [+0.089, +0.222] against a pool offset of +0.069 [+0.021,
+0.117], and the difference of +0.072 [+0.004, +0.170] is the only one of the six
whose interval excludes zero. The bottom band shows the same fit after subtracting
the recorded measurement variance from the pool-offset term — the selection
differential is computed from candidate scores observed exactly and carries no
measurement error, whereas the pool offset contains the organism's measured current
value, whose noise is 46–50% of the pool offset's observed variance depending on
the axis, so attenuation pushes only that coefficient toward zero. Correcting it
raises the EV-belief-bias pool offset from +0.069 to +0.141 (a factor of 2.03)
while the selection differential moves only from +0.141 to +0.134 (a factor of
0.95), and every difference interval then covers zero, EV belief bias included at
−0.007 [−0.150, +0.117]. Units are the change in the off-target readout per +1.0 of
pull on the risk-preference score, which itself runs from 0 to 1; each axis's
round-to-round standard deviation and the selection-differential coefficient
expressed in those standard deviations (+2.64 for EV belief bias, +2.65 for stated
risk tolerance, −0.31 for the EV numeric estimate) are printed beside each axis's
verbatim probe, because the three axes differ by more than an order of magnitude in
raw units. **This is not causal** — the selection differential was not randomised in
these runs — and the sample differs per axis because not every run recorded every
probe (EV belief bias 280 rounds from 59 runs, EV numeric estimate 247 from 57,
stated risk tolerance 200 from 39, the last on the OLMo chassis only). The Qwen arm
is shown nowhere: 64 rounds, measurement noise at 80% of its pool-offset variance,
and a corrected difference interval running from −1.62 to +1.82.

## Source data

- `experiments/offtarget_transmission_column.json` — every coefficient, interval,
  sample size, noise share and axis standard deviation in the figure is read from
  the `pooled.<axis>` keys of this file, except the Qwen numbers in the footnote,
  which come from `by_organism.Qwen.ev_belief_bias`. Written by
  `scripts/analysis_offtarget_transmission_column.py`.
- `experiments/spread_util_unified.json` — the generator recomputes the correlation
  between the two channels from this file rather than quoting it (risk-axis records
  carrying both a selection differential and a drift; the analysis join dropped
  nothing, so that filter reproduces the fitted rows exactly).
- Background prose: `docs/reports/report_offtarget_transmission_column.md`.
- Verbatim probe wording and the scoring recipes were read from the experiment
  script `experiments/kaggle/kaggle_k2_olmo_inversion/script.py`
  (`FACTUAL_EV_ITEMS` and `factual_ev_gate` for EV belief bias, `EV_ITEMS` and the
  `ev_estimation` block for the numeric estimate, `SELF_REPORT_POS`/`SELF_REPORT_NEG`
  and the `self_report` block for stated risk tolerance).

## One number that disagrees with the report

`docs/reports/report_offtarget_transmission_column.md` and the docstring of
`scripts/analysis_offtarget_transmission_column.py` both say the two channels
"correlate at only r = 0.16". Recomputed over the 280 rounds actually fitted, the
correlation is **r = 0.10**. (Over all 340 unified records that carry a selection
differential and a drift — that is, including axes other than risk, which this
analysis excludes — it is 0.15.) The figure prints the recomputed 0.10 and names
the sample it is computed over. The qualitative claim the number supports, that the
two channels are only weakly correlated and so can be separated in one regression,
is unaffected.

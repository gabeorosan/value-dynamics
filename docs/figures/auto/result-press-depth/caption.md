**The K2 press-depth map: no depth boundary was identified.** Three press depths (1,
2, and 3 conservative-judge rounds before the run switches to the base judge)
× 2 seeds, rounds 0→8, from the K2 release program (Modal branch c). At every
depth the two sampling streams produce paired low/high endpoints: seed 1
decays toward the floor (r8 = 0.000, 0.105, 0.229 at depth 1,
2, 3) while seed 2 rides upward toward the rail (r8 = 1.000, 0.938, 0.823).
Panel D shows the r8 endpoint range shrinking with depth — 1.000 → 0.832 →
0.594 — but never closing: even after 3 press rounds the two seeds still land
0.59 apart. The preregistered switch-round pool spread (mean over items of the
within-item candidate-score SD) is 0.278–0.423 in all six cells, i.e.
measurable selectable material at every switch point — yet three of the six
cells still ended near
the floor, so per the pre-registered scorecard (2 of 5 criteria passed:
criteria 1–3 FAIL, 4–5 PASS) that material is necessary but not sufficient
for the fan to open. Safety reading: a brief conservative intervention (1–3
rounds) does not reliably prevent a base-judge rail — seed 2 reached 1.000
after conservative pressing at every depth tested — and deeper pressing only
shrinks rail amplitude gradually. Sustained pressing (4–5 rounds elsewhere in
the K2 program) reached a zero-spread, selection-inert floor on the measured
axis; this does not establish an absorbing state or irreversible dynamics under
other generators or interventions. n = 2 seeds per depth: this is
a paired high/low-endpoint pattern from two sampling streams, not an
identified boundary law (per the source report's own audit correction).

Source data: `experiments/modal_k2_release/output/k2rel_press_d1_s1.json`,
`k2rel_press_d1_s2.json`, `k2rel_press_d2_s1.json`, `k2rel_press_d2_s2.json`,
`k2rel_press_d3_s1.json`, `k2rel_press_d3_s2.json` (r0–r8 `traj` arrays and
`rounds_raw[*]['pool_risk']`, both re-read and recomputed by the generator
script, not copied from prose). Pre-registered verdicts and the criterion-5
RMSE (−42.0% on 42 blind transitions) are quoted from
`docs/report_press_depth_boundary.md` (reproduced by
`scripts/score_press_depth_prereg.py`); that comparison itself depends on a
separately-fitted predictor, `experiments/release_predictor_nogap_frozen.json`,
which this script does not recompute.

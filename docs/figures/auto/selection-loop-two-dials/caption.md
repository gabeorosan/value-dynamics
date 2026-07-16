# How selection moves a value in a self-training loop

The loop-plus-dials overview. A model writes several candidate answers; a judge
scores each; the highest-scoring answers are kept; the model is trained toward
them; repeat. Three named distances carry the movement. The **selector gap** is
the kept answers' mean minus the whole offered pool mean — it is the judge's
act, and its size is set by two dials, value spread times judge/value agreement.
The **training displacement** is the kept mean minus the model's *own*
generated-pool mean — it is the update the model actually makes, and it equals
the selector gap plus a **pool-supply shift** (whole offered pool mean minus own
mean) whenever an outside supplier moves the offered pool away from the model's
own candidates; in a self-only pool the own mean equals the whole pool mean, so
the pool-supply shift is zero and training displacement equals the selector gap.
The **behavioral pull** (kept mean minus the separately measured behavioral
value) is the bridge from the kept training target to the model's downstream
behavioral readout, and is not drawn in this overview.

The four bottom panels introduce the two dials over a run: (A) selector gap =
value spread times agreement; (B) as a homogenizing self-pool spends its spread,
the gap shrinks with it; (C) agreement is set mainly by the judge setup, with
only slow within-run drift as its residual (not a fixed property); (D) an outside
source refills spread, so the gap returns.

The unit-form forecast printed on the figure is `selector gap ≈ agreement ×
spread` with **no fitted coefficient**. On the 290 agreement-scored rounds it
reaches R² 0.810 and mean absolute error 0.042 in value units, and agreement ×
spread tracks the selector gap at r = 0.90. (The earlier top-2-of-6
order-statistic constant near 0.95 was on the wrong scale and has been retracted;
it is deliberately not shown.)

**Source data (read and asserted by the generator at build time):**
- `experiments/spread_util_unified.json` — factorization: agreement × spread vs
  selector gap, pooled r = 0.901 over n = 290 rounds.
- `experiments/selection_response_predictor.json` — unit-form selector-gap proxy
  (`selector_gap.unit_agreement_spread_proxy.all`): R² 0.81037, MAE 0.042074,
  n = 290.

Regenerate with `python3 selection-loop-two-dials.py` from this directory
(stdlib only).

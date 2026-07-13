# Installing a conservative JUDGE meant training the judging channel directly — behavior-format training left the judge's taste inert

The install arc that produced the frozen conservative judge K2 uses (SETUP/methods figure, not a
result). All stages train the same base model, allenai/Olmo-3-7B-Instruct, with QLoRA (rank 16,
4-bit, completion-only loss). **Panel A** (six numbered cards): (1) native — forced-choice risk
0.723, generated-choice risk ≈0.62–0.65, and the held-out judging-taste readout (judge_taste_bold /
cautious_judge_pref: mean probability the model, acting as a judge, prefers the cautious answer over
a risky one on 12 held-out gamble items, both presentation orders) at 0.49–0.53 — near indifferent.
(2) Six behavior-format ladders v2–v6 (letter targets, rationale targets, mixed 1:1 recipes) train
the model's OWN gamble answers — generated risk swept 0.62→0.04, forced risk plateaued ≈0.55–0.58 —
but the judging-taste readout never left 0.512–0.532 at any rung of v3/v5/v6, and the strict
judge-inversion screen on v6_mixed_strict rung_20 found kept-mean separation between the frozen
conservative and frozen base judges of exactly 0.000 (pool 101 gaps −0.083/−0.083, pool 202 gaps
0.000/0.000) — TASTE-INERT. (3) v7 adds judge-format training rows (1:1:1 rationale:letter:judge) and
the SAME coordinate moves 0.426→0.549→0.726→0.927 across rungs 0/20/40/60 — a clean dose-response —
but no rung passes every organism gate (forced order gap 0.20–0.29 vs the ≤0.10 requirement; generated
channel overshoots down to 0.083, below the 0.15 band floor). (4) v8 (mixed_judge2, 1:2:1 recipe)
lands all seven organism gates at rung_60 (forced 0.723→0.590, generated 0.632→0.478, judge_pref
0.426→0.686) but its own strict two-pool inversion screen fails (separation ≈0, sign only). (5) v9
(mixed_judge3, reference-pair judge rows) tries to raise the screen's separation but moves the judge
readout slower (+0.11 by rung 60 vs v8's +0.26) and never re-enters the order-gap gate — ladder
exhausted, no valid rung at any dose. (6) v10 is a judge-only top-up (100% judge rows) starting from
v8's rung_60 adapter; 20 steps land rung_20 with all gates passing and cautious_judge_pref at 0.880,
and the final 5-pool inversion screen passes under both preregistered rules (per-pool separations
+0.021/+0.167/+0.167/+0.167/−0.021, mean 0.100, sd 0.093, conservative-judge gap negative in 5/5
pools) — this is the organism frozen as K2's conservative judge, condition `frozen_cons_r0` in
docs/report_loop_integrator_decomposition.md / fig17_loop_integrator. **Panel B** plots the same
judging-taste coordinate as points on one 0–1 axis across the arc (native → v7's three rungs → v8 →
v9's best partial dose → v10), with the flat v2–v6 band shown for comparison; the amber box below
states the three-way behavior↔forced / behavior↔generated / judge-format↔judging dissociation
explicitly as an **instrument lesson** (demoted from a headline finding by user correction, PLAN
decision log 2026-07-11 ~15:00) — you move the channel you train.

Source data: this is a Colab/Kaggle install log, not a saved result JSON — every number is a
decision-log transcription from `docs/PLAN.md` (search "v7 / v8 / v9 / v10 / cautious_judge_pref /
mixed_judge / judge-channel", entries dated 2026-07-10 night through 2026-07-11 ~18:20) and its
mirrored entries in `docs/STATE.md` (2026-07-11 ~02:00 through ~18:20, including the "5-POOL SCREEN
VERDICT — PASS under both rules" entry at ~16:15 that is the actual final gate on v10, not stated in
the original figure request and added here after checking the log). Cross-checked against two
existing figure drafts that independently verified overlapping numbers:
`docs/figures/auto/olmo-taste-inertness/` (v2–v6 taste-inert numbers) and
`docs/figures/auto/judge-channel-install/` (v7 dose-response numbers). Downstream use of the frozen
organism (condition `frozen_cons_r0`) is documented in `docs/report_loop_integrator_decomposition.md`
and `docs/figures/src/fig17_loop_integrator.py`. Regenerate with `python3 setup-k2-organism.py` from
this directory (stdlib only).

# Closed-loop rollout: does the spread model predict an unseen condition?

A value-dynamics simulator is fit on other runs, then shown only a held-out run's
first-round pool state and made to roll the whole trajectory forward without ever
reading that run's later candidates, spread, agreement, or value. Validation is
leave-one-condition-out (LOCO): the entire intervention/judge regime is held out,
so this is the real test of whether a spread definition transports to a new regime.
"Endpoint MAE" is the mean absolute error of the predicted final value against the
true final value on a 0-1 value scale, and lower is better. Panel A shows that the
closed loop beats the no-change baseline (which predicts the value never moves from
round 1) by a wide margin on selection-driven runs (0.139 vs 0.431), mixed
interventions (0.138 vs 0.450) and strong-agreement self-only judges (0.140 vs 0.393), ties
on weak self-only selection (0.205 vs 0.215), and is out of scope for mid-run judge
swaps (0.392 vs 0.361, the only regime where it loses) because the round-1 model
cannot see a state change that happens later; on selection-driven runs it gets 28 of
31 large-move directions right. Panel B ranks the nine spread definitions that exist
on both score axes by their selection-driven endpoint MAE, comparing predicted metric
dynamics (geometry) against freezing the first-round metric: of the transportable
scales, mean within-prompt range (rankable support) is the best endpoint state
(geometry 0.132, frozen 0.125) and mean within-prompt SD (spread) is the direct
selector scale (0.139/0.127); range beats mean SD by 0.007 endpoint MAE under
geometry (paired bootstrap 95% CI 0.003-0.011) but by only 0.002 under frozen, an
interval that crosses zero. The fraction-of-prompts-with-any-difference indicator
wins under leave-one-run-out but reverses under leave-one-condition-out (0.150 here),
so it does not transport and is not crowned; total pooled SD and median within-prompt
SD are clearly worse. Feeding predicted spread back does not help the endpoint:
mean-SD geometry predicts the risk spread trajectory better than freezing it (spread
MAE 0.080 vs 0.111) yet predicts value endpoints worse (0.139 vs 0.127); the best
simple endpoint model is frozen rankable support (0.125 vs 0.431 no-change, 31/31
large-move directions right). Binary entropy (risk-0/1 runs only) scores 0.128 but is
not comparable across both score axes, so it is excluded from this ranking.

Source: experiments/spread_rollout_bakeoff.json (leave-one-condition-out); generator spread-rollout-bakeoff.py

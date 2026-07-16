# One round, on the value line: pool, kept set, and the move

A definitions figure for the model section. One round of the selection loop is
drawn as positions and distances on a single shared 0–1 value axis, repeated in
three vertically aligned steps so the eye tracks each mean straight down the
figure. Candidate positions are illustrative (chosen to make the geometry legible);
the measured numbers are below, not in the figure.

Symbols (each a mean value score on the 0–1 axis):
- **q — own mean.** Mean value of the organism's own six candidates (blue dots).
- **p — pool mean.** Mean value of every candidate the judge scores. In a mixed
  pool, supplier candidates (orange dots) pull it up; **pool-supply shift = p − q**.
  For a self-only pool, p = q.
- **k — kept mean.** Mean value of the two candidates the judge keeps (black
  circles; here one own, one supplier).
- **g — selector gap = k − p.** How far the judge's kept set sits above the pool it
  drew from.
- **training displacement = k − q = g + (p − q).** The full move of the training
  target away from the organism's own mean, split into the judge's selection gap
  plus the pool-supply shift.
- **v — behavioral value.** The value before the round is drawn at the own
  mean q (the model's identity: each round ends with next q = next v). After
  training, the value moves to the kept mean (green arrow, next v = k).

Measured accuracy of this rule: predicting next-round behavioral
value by the kept-mean rule gives mean absolute error **0.081**, versus **0.128**
for assuming no change, over **340** rounds under leave-one-condition-out
(held-out conditions) cross-validation.

Source data: `experiments/value_predictor_bakeoff.json`
(`one_round.leave_one_condition_out`: `kept_target_identity.mae` = 0.081157,
`no_change.mae` = 0.127883, n = 340). The generator asserts these from the file
rather than hardcoding. Model narrative: `docs/report_spread_util_unified.md`.

# Caption — spread-intervention-two-steps.svg

**The spread intervention splits cleanly in two: the selection step did exactly
what the project's model says, and the transmission step did not follow.** Three
seeds of Qwen3-4B-Instruct-2507, each carrying a risk-seeking persona, were run
for four self-training rounds under two arms. In both arms the model wrote
candidates for 12 loop prompts, a judge frozen at the untrained base model kept
2 of the 6 offered per prompt, and the model was fine-tuned on what was kept. The
arms differ only in how the candidates were arranged: the **concentrated** arm
was offered six candidates per prompt that all carry the same value score, the
**spread** arm was offered candidates that disagree inside the prompt — and the
arrangement was built so the two arms' **offered-pool means** (the mean value
score over all candidates a round offers, value scored 1 if the answer ends on
the gamble and 0 otherwise) are identical. Across all 12 seed-rounds the largest
difference between the arms' offered-pool means is 0.000, shown dot-inside-ring
in the strip under panel A. **Panel A, the selection step:** the horizontal axis
is **within-prompt spread**, the standard deviation of the 6 offered candidates'
value scores averaged over the round's 12 prompts; the vertical axis is the
**selection gap**, the kept-candidate mean minus the offered-pool mean. The
concentrated arm sat at spread 0.000 with a selection gap of exactly 0.000 in 11
of its 12 seed-rounds (0.042 and +0.042 in the twelfth); the spread arm reached
spread 0.309 to 0.480, and there the frozen judge kept a set averaging -0.146
below the pool it was offered, round by round from -0.042 down to -0.333. That is
the model's selection claim working: at a fixed pool mean, spread is what buys a
gap. **Panel B, the transmission step:** each of the same 24 seed-rounds is
plotted as the movement the model forecasts — **predicted movement** = 0.83 x
selection gap, with 0.83 the project's transmission coefficient fixed in advance
— against the **observed movement**, the measured value after the round minus
before it. Both axes carry one scale, so the model's claim is the dashed slope-1
line through the origin. The 24 rounds instead fit a slope of 0.054 with
correlation 0.046, about 19 times shallower; the concentrated arm's rounds, whose
forecast movement is 0.000 every round, still moved the measured value by as much
as 0.250. Judged as a forecast, the model loses to predicting nothing: the average
size of its error over the 24 round-transitions is 0.094, against 0.065 for
forecasting no movement at all. **This is underpowered for small effects and is
not evidence that transmission is zero.** The value probe is 36 binary reads (12
held-out gamble prompts x 3 samples), so a single round-to-round difference
carries a standard error of 0.109 — larger than the 0.065 average size of the
movements being explained. Rounds landing on identical coordinates are fanned
into a small rosette so all 24 dots stay visible; no jitter is applied otherwise.

## Source data

- `experiments/spread_intervention/output/spread_intervention.json` — every
  rendered number is recomputed by the generator from `groups[<judge seed>]`:
  the per-round `arms[<arm>].rounds` records (`spread`, `gap`,
  `value_after_round`) paired with `arms[<arm>].value_traj` for the value before
  each round, and the paired `joint` records for the two arms' offered-pool
  means (`pool_mean_concentrated`, `pool_mean_spread`, `pool_mean_abs_diff`).
  Run settings (12 held-out probe prompts, 3 samples each, 6 offered and 2 kept
  per prompt, frozen base judge) come from the file's `config`. The file's own
  `summary` block is not read.
- The random-selection control group (`control_seed7`) is present in the file but
  is not plotted here; only the three judge seeds are.
- Predicted movement uses the project's transmission coefficient 0.83, which is
  hard-coded in the generator as `TRANSMISSION` and is not read from the file.

## Regenerate

```
cd docs/figures/auto/spread-intervention-two-steps && python3 spread-intervention-two-steps.py
```

Stdlib only; it walks up to the repository root to find `experiments/`.

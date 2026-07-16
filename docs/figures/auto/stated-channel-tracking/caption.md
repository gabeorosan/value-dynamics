# When selection moves behavior, what the model says about itself mostly does not follow

Each dot is one self-training run. The horizontal axis is the **net behavioral
move over the run** — the last-round minus first-round value of the behavioral
target (risk tolerance elicited from actions, or insecure-code rate), field
`d_traj`. The vertical axis is the **net stated move over the same rounds** —
the change in the model's own forced-choice self-description (field `d_sr`),
elicited every round with order-balanced probes. A run that fully narrated its
own drift would land on the dashed 45-degree line (statement tracks behavior
1:1); a run whose statements never budge sits on the solid horizontal line at
zero. Dots with a dark outline are the runs where the behavioral move cleared
the committed `moved_threshold` of 0.15 (the tracking-ratio population); lighter
dots moved less than that. All three panels share identical −0.9..+0.9 axes so
the reference lines are directly comparable across populations.

**OLMo risk runs (n = 46).** Behavior sweeps the full width (net moves from
about −0.82 to +0.79) while the stated channel clings to zero: per-population
tracking ratios run only +0.03 to +0.14, and the behavior-minus-statement gap
widens across the run from 0.167 to 0.341. The statements move in the right
direction but at a fraction of the pace.

**Qwen risk grid (n = 16).** The stated channel is floor-pinned: every stated
read falls between 0.0013 and 0.0513 and the largest net stated move over any
run is 0.037, even as behavior moves up to about ±0.42. The dots form a flat
band on the zero line — the self-report never leaves the floor.

**Qwen insecure-code loops (n = 19).** Here the stated probe ("does it say its
code is insecure") does move, but with unreliable sign: tracking ratios span
−0.81 to +1.39, with seed-level sign flips inside the same cell — visible as
dots scattered into all four quadrants rather than hugging either reference
line.

Source data (read live by the generator, never hardcoded):
`experiments/selfreport_calibration_k2.json` (key `rollouts`, OLMo) and
`experiments/stated_channel_parity.json` (keys `qwen_risk_grid.rollouts` and
`qwen_insecure_loops.rollouts`). Committed numbers and method:
`docs/report_stated_channel_parity.md` and
`docs/report_selfreport_calibration_k2.md`.

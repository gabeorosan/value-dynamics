# Selection moved the trained value only when candidates disagreed within a prompt

Two arms of a training intervention were run at maximal (oracle) selection pressure
and differed in exactly one thing: where the value-variation among candidate answers
sat. In the **concentrated arm** the six answers offered for any one prompt were
nearly all the same value, with the variation pushed between prompts; in the
**spread arm** every prompt's six offered answers were internally mixed. The overall
offered-pool mean was forced to match between arms, and it did — the largest absolute
difference in offered-pool mean (concentrated arm minus spread arm) is **0.000**
across all 11 rounds of the four training loops, so the two arms were handed pools of
identical average riskiness and merely arranged differently. Left panel: the measured
value — the share of held-out answers that choose the gamble, over 12 held-out gamble
prompts at 12 samples each — over rounds, one line per training loop (two independent
runs × two seeds). The spread arm rises by **+0.387** on average from round 0 to the
last round (the four loops: +0.438, +0.375, +0.389, +0.347); the concentrated arm
moves **+0.045** on average and in both directions (−0.062, +0.097, +0.132, +0.014),
so it drifts rather than sitting perfectly still. Right panel: the mechanism, averaged
over the same 11 rounds with one hollow dot per round. Within-prompt spread — the mean
over the 12 prompts of the standard deviation of that prompt's six offered answer
values — is 0.328 in the spread arm and 0.024 in the concentrated arm, and the
selection gap — kept-answer mean minus offered-pool mean, the quantity the project's
model says the value moves by times a transmission coefficient — is 0.294 versus
0.021. The concentrated arm's per-round dots are not all at zero (one round reaches a
within-prompt spread of 0.114 and a gap of 0.111), which is exactly why it drifts a
little. One of the four loops stops after round 2: in that round the concentrated
arm's candidates had become so value-uniform that no offered-pool mean was reachable
by both arms, and the run was ended rather than let the arms differ. The whole figure
is one model family — Qwen3-4B with a risk-seeking persona installed by fine-tuning —
and an oracle selector, not a language-model judge.

**Source data**
- `experiments/spread_intervention/output_oracle/spread_intervention.json` (run 1),
  groups `oracle_max_seed0`, `oracle_max_seed1`
- `experiments/spread_intervention/output_followups/floor_effect.json` (run 2),
  groups `oracle_max_seed0`, `oracle_max_seed1`

Groups `oracle_min_*` and `control_seed7` are present in both files and are not used
here. The two runs installed the risk persona at different strengths (run 1: 60
persona steps at rate 0.5; run 2: 80 steps at rate 0.9, per each file's `config`),
which is why their round-0 values differ.

Regenerate with `python3 spread-gates-transmission.py` from this directory (stdlib
only; it reads both JSON files and recomputes every rendered number).

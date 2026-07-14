# Moving the value moves the belief — but only when the belief is a choice

On the OLMo-2-7B risk model (50 self-training runs across the K2 grid and modal
cells), the change a run makes to the value preference — Δ P(choose the riskier
option) on held-out expected-value-neutral gambles, first round to last — drags
the model's stated belief about expected value with it, but only on the
comparative channel. Left panel: change in belief bias, measured as P(says the
GAMBLE side has the higher expected value) minus 0.5 on a balanced set of 24
factual comparison items (12 where the gamble truly is higher, 12 where it is
not, so 0 = unbiased), plotted against the change in preference; the signed
correlation across runs is +0.79, the round-by-round within-run correlation
averages +0.42 (positive in 80% of runs), and preference and bias are already
correlated at round 0 (+0.68, mean starting bias +0.16). Marquee runs: the
oracle-judged reversal run (Δpreference −0.82 → Δbias −0.24, red) and three
risk-invasion runs (Δpreference +0.69 to +0.76 → Δbias +0.22 to +0.24, blue).
Qwen3-4B runs (n = 17, open gray circles) show no such coupling (signed
correlation −0.22). Right panel: the same 50 OLMo runs on the same x axis, but
the y axis is the change in log(stated expected value / true expected value)
when the model is asked to state the number — a flat cloud at zero (signed
correlation −0.14; even the largest preference swings move the stated number by
about 1%). Ask for a number and the model tells the truth; ask which side is
higher and the preference leaks in.

Source data: `experiments/ev_bias_coupling.json` (per-run `d_traj`, `d_bias`,
`d_est` and the `by_group` aggregates; all statistics recomputed from the
per-run values by the generator). Context: `docs/report_ev_bias_coupling.md`.
Regenerate with `python3 ev-bias-coupling.py` from this directory.

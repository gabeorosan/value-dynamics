# judge-channel-install — plotted numbers

Recipe v7 (TARGET_STYLE mixed_judge): QLoRA rank 16 on 4-bit
allenai/Olmo-3-7B-Instruct, completion-only loss, training rows cycling
rationale → letter → judge-verdict at 1:1:1 (judge rows format-matched to the
downstream judge readout, preferring the cautious answer), cautious rate 0.97.
x = cumulative optimizer steps.

| steps | 0 | 20 | 40 | 60 |
|---|---|---|---|---|
| judge preference for the cautious answer (cautious_judge_pref) | 0.426 | 0.549 | 0.726 | 0.927 |
| generic-advice bold taste (judge_taste_bold) | 0.526 | 0.544 | 0.528 | 0.524 |
| generated gamble rate (gen_gamble) | 0.65 | 0.417 | 0.348 | 0.083 |
| forced-read order gap (gate ≤ 0.10) | 0.074 | 0.201 | 0.291 | 0.212 |

Readout recipes (verified against
experiments/olmo_conservative/colab_olmo_conservative_install.py and
experiments/common/risk_harness.py):

- cautious_judge_pref = mean p(judge prefers the cautious answer) over 12
  held-out gamble items (amounts 27/42/63/88 × probabilities 0.33/0.44/0.57,
  disjoint from the training grid and the screen bank), each judged as an A/B
  pair of one cautious and one risky loop-format answer, both presentation
  orders, forced single-token read under the judge system prompt "You are
  evaluating answers."; 0.5 = indifferent.
- judge_taste_bold = mean p(prefers the BOLD answer) over 6 generic
  advice-question pairs × both orders — flat 0.49–0.53 across every
  behavior-format ladder (v2–v6); that band is the gray reference band.
- gen_gamble = fraction of 24 order-balanced free generations (12 EV-neutral
  items × both option orders) whose strict end-anchored "Final: A/B" picks the
  gamble, invalid excluded.
- order gap = |mean forced p(gamble), gamble as Option A − gamble as Option B|
  over the same 12 forced-read items.

Verdict: registered prediction confirmed (judge-format rows move the judge
channel; the +0.15 judge_pref_shift gate is passed by rung 40 at +0.300), but
OVERSHOT_NO_VALID_RUNG — every trained rung broke the ≤ 0.10 order-balance
gate and generated overshot its 0.15–0.50 band by rung 60, so no all-gates
organism; v8 (rationale:letter:judge at 1:2:1) re-balances letter density.

## Provenance

Raw rung JSONs on Google Drive, not in the repo:
value_dynamics/olmo_conservative/ (v7_judge_strict run). Numbers transcribed
from the spawning thread's readout; cross-checked against the docs/PLAN.md
decision-log entry dated 07-11 ~04:00 (cautious_judge_pref sequence, taste
flat ~0.53, order gap 0.20–0.29 at every trained rung, generated 0.083 at
rung 60, overshoot verdict) and docs/STATE.md — all overlapping values match.

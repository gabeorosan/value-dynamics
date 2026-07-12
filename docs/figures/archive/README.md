# Retired figures

Figures here are no longer part of the active set. They are preserved for git
history and can be recovered at any time — their generators still live in
`../make_figures.py` (fig1–15) and `../fig16/17/18_*.py`; only the emit list
changed.

## Active numbered set (2026-07-13 refactor)

The set was cut to the apparatus plus the three sprint results, and the loop
apparatus was split into two clean figures:

- `../fig2_selftraining_loop.svg` — the loop as one cycle (generate → select → train → repeat)
- `../fig2b_judge_conditions.svg` — the one manipulation: who does the selecting (self / frozen-copy / frozen-base / random)
- `../fig16_k1_anchor_fan.svg` — K1, the Qwen risk anchor grid (result)
- `../fig17_loop_integrator.svg` — K2, the kept-gap → pool-drift coupling (result)
- `../fig18_k3_selfreport_fan.svg` — K3, the insecure-code self-report fan (result)
- `../fig19_reversibility_absorbing.svg` — reversibility + spread-exhaustion: zero-spread states are absorbing, wherever they sit (result)

## Retired 2026-07-13 — refactor to loop + results

The old single `fig2` was a dense one-page walkthrough (question → answers →
pairing → conditions → scores → train → measurement, with verbatim prompts); it
was replaced by the two clean figures above. These legacy figures were retired
as trivial, out-of-date, or off-topic to the current research (the risk /
insecure-code self-training loops):

| File | Was | Why retired |
|---|---|---|
| `fig1_research_goal.svg` | "The goal: a map of what happens to a value that trains on itself" | framing figure folded into fig2 |
| `fig4_selection_ablations.svg` | bold-prose selection ablations | part of the prose/essay line, off-topic now |
| `fig5_boldprose_unpacked.svg` | "selecting for bold prose makes the prose bolder" | prose/essay line, off-topic now |
| `fig7_rhetoric_gates_transfer.svg` | fine-tuning on arguments (ratings vs choices) | the **essay experiment** — excluded as irrelevant to the main research |
| `fig8_dose_ladder.svg` | more optimizer steps per round | a trivial result |
| `fig9_selfdata_mixing.svg` | entropy collapse / self-data mixing | the **entropy figure — out of date** |
| `fig10_offtarget_drift.svg` | off-target drift (three phenomena) | not part of the current headline story |

## Retired 2026-07-12 — earlier passes

Planning/status figures overtaken by results: `fig12_experiment_map` (07-09
"what runs next"), `fig13_next_regime_grid` (regime grid cut),
`fig14_next_round0_copy_judge` (ran as K1's `frozen_copy_r0` arm → fig16),
`fig15_next_content_arms` (K4, not reached). Legacy result figures superseded by
newer results / re-audit-retired framing: `fig3_judge_determines_dynamics`
(clean version is K1/K2/K3), `fig6_packet_rating_measurement` (narrow legacy
recipe), `fig11_engine_filters_regimes` (basin/"unpredictable-zone" synthesis).

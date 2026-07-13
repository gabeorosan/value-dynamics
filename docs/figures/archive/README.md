# Retired figures

Figures here are no longer part of the active set. They are preserved for git
history and can be recovered at any time — all generators now live in
`../src/` (`make_figures.py` holds fig1–15; the numbered results and methods
figures have their own scripts); only the emit lists changed.

## Retired 2026-07-13 — text-density split

The combined `result_mixed_pool.svg` was retired when its generator was
refactored to emit the two focused figures above (rescue / contamination); its
history is preserved and the generator still lives at `../src/result_mixed_pool.py`.

## Layout (2026-07-13)

- `../*.svg` — every active figure, SVGs only (no .py clutter)
- `../src/*.py` — the generators (write their SVGs up into `../`)
- `archive/` (here) — retired figures

## Active set

Loop apparatus (detailed, split in two):
- `../fig2_loop_generate_judge.svg` — one round: question → 6 answers → pairing vs the fixed reference → the two judge conditions → judge scores + top-2 kept
- `../fig2b_loop_train_measure.svg` — fine-tune on the 24 kept + loop-back, and the risk-coordinate measurement strip

Core results (numbered):
- `../fig16_k1_anchor_fan.svg` — K1, the Qwen risk anchor grid
- `../fig17_loop_integrator.svg` — K2, the kept-gap → pool-drift coupling
- `../fig18_k3_selfreport_fan.svg` — K3, the insecure-code self-report fan
- `../fig19_reversibility_absorbing.svg` — reversibility + spread-exhaustion
- `../fig20_k2_screen_force.svg` — the K2 pre-launch screen: pool-heterogeneous selection force

Per-experiment setup panels (`setup_*`):
- `../setup_k2_organism.svg` — the K2 conservative/base organism install
- `../setup_em_organism.svg` — the insecure-code (EM) organism + its three probe channels
- `../setup_reversibility_protocols.svg` — the reversibility / oracle-opposition protocols

Recent-experiment results (`result_*`):
- `../result_release_grid.svg` — K2 release grid: escaping the pressed floor needs an up-judge AND residual pool material
- `../result_press_depth.svg` — press-depth trajectory panels + endpoint fan + safety reading
- `../result_press_depth_scorecard.svg` — the 5-criterion pre-registration scorecard for the press-depth program
- `../result_force_ladder.svg` — the force ladder across judge strengths (step, not slope)
- `../result_crossfamily_oracle.svg` — cross-family oracle opposition: trajectories + within-pool material
- `../result_crossfamily_oracle_pools.svg` — the two verbatim candidate pools (why the selector reverses one rail, not the other)
- `../result_mixed_pool_rescue.svg` — mixed pool as a slow remedy: low-risk material injected into a rail
- `../result_mixed_pool_contamination.svg` — mixed pool as a fast attack vector: one railed co-generator takes over
- `../result_transmission_floor.svg` — weak-dose transmission cells on the floor

Analysis (`analysis_*`):
- `../analysis_instrument_validity.svg` — instrument / support-null validity
- `../analysis_frozen_predictor.svg` — the frozen-predictor out-of-sample check

Methods (integrated here, not siloed): `../methods_gate_table.svg`,
`methods_paired_contrast`, `methods_judge_loading`, `methods_format_channels`,
`methods_weight_geometry`, `methods_alpha_scaling`, `methods_counts`,
`methods_specificity`, `methods_exploratory`, `methods_overview`.

Text-density note (2026-07-13): the densest result/methods figures were split
so no single figure is a wall of text — result_mixed_pool → rescue +
contamination; result_press_depth → trajectories + scorecard;
result_crossfamily_oracle → result + verbatim pools; methods_weight_geometry →
geometry + alpha_scaling. Generators emit the focused SVGs; combined
predecessors are retired below.

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

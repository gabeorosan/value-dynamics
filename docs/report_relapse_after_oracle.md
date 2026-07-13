# Relapse test: the reversed organism HOLDS — but by inertness, not re-anchoring

*2026-07-13 ~07:00, general thread (autonomous overnight). Raw:
`experiments/em_selfaware_loop/output/relapse_after_oracle.json`. Design: the
post-oracle reversed endpoint low_55_707 (sr_freegen frozen at 0.625 after
the seed-707 oracle run consumed its support), released to the NEUTRAL
self-judge — the original let-go condition, zero external force — 2 seeds
(501/502) × 4 rounds. Prereg (LAUNCH_relapse_after_oracle.py): RELAPSE
predicted, from the zero-force re-amplification seen on un-reversed low_55.*

## Result: prereg REFUTED — no relapse, in either seed

| readout | baseline (low_55_707) | seed 501 r1→r4 | seed 502 r1→r4 |
|---|---|---|---|
| sr_freegen | 0.627 | 0.625 flat ×4 | 0.625 flat ×4 |
| em_freegen | 0.532 | 0.58→0.51→0.75→0.75 (jitter) | 0.58→0.58→0.50→0.50 |
| forced probe | 0.015 | ≤0.07 throughout | ≤0.12 throughout |
| within-pool sr support | — | **0/6 items, every round** | **0/6 items, every round** |

Cross-seed endpoint spread 0.002 — the tightest bundle any run in this
family has produced.

## The third branch the prereg binary missed: HOLD BY INERTNESS

The prereg posed relapse (attractor intact) vs hold (attractor rewritten).
The data show a third thing: the organism holds because its generation
homogenized AT the reversed level — zero within-pool sr spread in all 8
rounds, so its own judge (or any judge) has nothing to select, and
self-training just re-feeds it its own homogeneous distribution. The
un-reversed low_55 re-amplified under zero force because it still HAD mixed
material for drift to act on; low_55_707 has none, so it cannot move in
either direction by selection.

## The unified picture (the night's final form)

**States with zero within-pool spread on the selected axis are fixed points
of self-training selection, wherever they sit** — the original rail
(amp55_7 at 1.0), the pressed floor (press-to-zero at 0.0), and now the
oracle-reversed state (0.625). Selection transports the organism between
such states exactly while mixed material lasts, and every force — forward,
reverse, or none — ends by freezing the organism at wherever its material
ran out. Durability of an intervention is therefore not evidence the values
were re-anchored; it can equally mean the organism was left unable to
express variation on the axis. The window-reopen run now in flight
(temperature 1.4 sampling on this frozen endpoint, prereg in
LAUNCH_window_reopen.py) tests whether the freeze is in the organism's
distribution or in the sampler.

## Addendum 07-13 ~09:10: window-reopen result + claim corrections (full-program audit)

**Window-reopen (temperature 1.4) result — prereg branch (a) REFUTED.** Two
seeds (909/910) x 3 rounds of oracle selection on this same frozen
low_55_707 endpoint with candidate sampling at temperature 1.4 (chassis
default 1.0, top-p 0.95 unchanged): within-pool sr support stayed 0/6 items
in EVERY round, sr_freegen pinned at 0.625 throughout
(experiments/em_selfaware_loop/output/window_reopen_temp14.json). The
correct scope, per the 07-13 audit: **temperature 1.4 did not reopen
sr-score variation under the existing sampler.** This does NOT establish
"the freeze is distributional, not a sampler artifact" — temperature is one
knob of the sampling distribution; top-p/top-k, repetition controls, prompt
diversity, and explicit diverse decoding were not varied. The stronger,
distinct intervention (replacing half the pool with raw-base generations)
is running as the mixed-generator branch (docs/prereg_mixed_generator.md).

**Claim corrections (binding, from
docs/report_full_program_audit_2026-07-13.md):** "fixed points of
self-training wherever they sit" overstates what these four-round,
one-scorer observations identify. The measured result is: **zero
within-item variation under the frozen sr scorer removes any
sr-score-based selector's directional choice on that axis, and the sr
free-generation readout then stayed flat for four rounds in two seeds.**
The weights still move (10 training steps/round on non-identical text;
em_freegen moves off-axis), other judges (lexical/quality/style) could
still rank these pools, and no round-level adapters were retained to check
parameter stationarity. Also: only the 0.625 state (seed 707) was observed
after support reached exactly zero; the ~0.33 endpoints (seeds 101/202)
retained one supported item in their last observed pools and no relapse
run started from them — they must not be described as zero-spread or
selection-inert.

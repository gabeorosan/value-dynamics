# Optimism as the universal tracer: the one off-target probe present in every experiment, and what it says about the drift families

No-GPU synthesis. Optimism ("Will venture X succeed? yes/no", read as P(yes)) is
the only off-target coordinate logged across *every* experiment family this
project has run — basin loops (both substrates, both judges), the EM
self-training loop, the gray-zone regime probe, the pure-SFT dose ladder, and
the self-aware dose×loop grid. Lining it up against each force sharpens the
fig10 "off-target drift is three phenomena" claim — and partly reclassifies
optimism. Baseline is ~0.48 (Qwen) / 0.41 (OLMo). Raw per-run values are in the
source JSONs under `battery[*].off_target.optimism_p_yes` (or `battery[*].optimism.mean_p_yes` for the multi-venture basin probe).

## Optimism moves under forces of completely different kinds

| force applied | optimism response | reading |
|---|---|---|
| **Pure SFT dose**, no loop at all (dose ladder 250→1000) | 0.48 → 0.44 → 0.39 → **0.22**, monotone down | fine-tuning *content alone* drives it — no selection needed |
| **Qwen basin, self-judge** (risk loop) | 0.68 → 0.73 (Δ +0.05) | mild up |
| **Qwen basin, frozen-judge** | 0.68 → 0.68 (Δ ~0) | flat |
| **OLMo basin, self-judge** | 0.41 → 0.44 | mild up |
| **OLMo basin, frozen-judge** | 0.41 → 0.32 (Δ −0.09) | down — judge-split, like Qwen but sharper |
| **EM loop, self-judge** | 0.48 → 0.72 (seed 11), 0.48 → 0.68 (seed 22) | up |
| **EM loop, frozen-judge** | 0.48 → 0.26 | down — clean judge dissociation |
| **Self-aware grid, LOW dose (250)** | 0.48 → 0.4–0.85, mostly **up** across seeds | up |
| **Self-aware grid, HIGH dose (1000)** | 0.48 → **0.03–0.27**, sharply **down** all seeds | **down — dose flips the sign** |

## Three things this says

1. **Optimism is not purely "content-coupled" as fig10 files it.** It moves
   under the pure-SFT dose ladder with *no loop, no selection, no judge* at all
   (0.48 → 0.22) — that is the content-free family's signature (drift from the
   fine-tuning objective itself), not the content-coupled one. Optimism belongs
   in *both* buckets depending on regime, which means the three-family taxonomy
   is force-dependent, not a fixed property of each coordinate.

2. **It is the cleanest judge-dissociation tracer we have.** In the EM loop
   (0.72 self vs 0.26 frozen) and OLMo basin (+0.04 self vs −0.09 frozen) the
   same content pushed by opposite judges moves optimism in opposite directions.
   Optimism is where "judge preference sets the direction" shows up most legibly
   off-target — a good candidate coordinate for any figure making that point.

3. **The self-aware grid reveals a dose×loop interaction that no single-dose run
   could see: the sign flips with organism dose.** Low-dose loops push optimism
   *up* (0.4–0.85); high-dose loops on the *same* loop content push it *down*
   (0.03–0.27). The organism's strength gates whether amplifying its self-signal
   makes it optimistic or bleak. (Grid is the general thread's run;
   docs/report_selfaware_loop_grid_lowdose.md covers low dose. This is the
   optimism slice across both dose rungs.)

## Caveat

The basin multi-venture probe (mean over several ventures) and the EM-family
single-venture probe are not identical instruments, so cross-family *levels*
aren't directly comparable — only the within-family *directions and deltas*
are. All values are deterministic yes/no logprob reads (no sampling noise), so
the directions are real; the per-seed spreads (basin Δ sd ~0.05) say the small
basin moves are near the seed-noise floor, while the dose-ladder (−0.26) and
high-dose-grid (−0.3 to −0.45) moves are well clear of it.

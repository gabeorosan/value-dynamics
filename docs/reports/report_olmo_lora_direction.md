# OLMo EM-LoRA direction geometry: the dose direction rotates and grows after behavior saturates, and the self-judge erosion is mostly ORTHOGONAL to it — not a walk-back along the installed axis

*2026-07-15, general thread. Colab (CPU-only, pin f6a933a,
experiments/olmo_insecure/LAUNCH_olmo_lora_direction.py). Pure linear algebra on
the persisted LoRA adapters — every module's update ΔW = (α/r)·B·A, computed via
streamed r×r inner products (ΔW never materialized; math verified exact against
brute force). Raw: experiments/olmo_insecure/output/olmo_lora_direction.json.
Adapters: OLMo dose rungs 250/500/750/1000 + the 6 duel-loop per-round
checkpoints (seed 71/72, rounds 1–3), all rank-32, all-linear, same base.*

## Q1 — the insecure-code direction is not one fixed vector; it rotates as it grows

Cosine between the flattened LoRA update directions of adjacent dose rungs is
high but the far pair drifts:

| pair | cosine |
|---|---|
| dose250 ↔ dose500 | 0.830 |
| dose500 ↔ dose750 | 0.899 |
| dose750 ↔ dose1000 | 0.924 |
| **dose250 ↔ dose1000** | **0.548** |

So there is a dominant *local* direction (adjacent doses ~0.83–0.92 aligned),
but it **rotates** as dose increases — dose250 and dose1000 are only 0.55
aligned (~57°). This tempers the EM-LoRA "single dominant direction" reading:
within a dose neighborhood yes, but the installed direction is not fixed across
the ladder.

## Q2 — the delta norm keeps growing after behavior saturates

| dose | 250 | 500 | 750 | 1000 |
|---|---|---|---|---|
| ‖ΔW‖ (Frobenius, all modules) | 12.0 | 17.5 | 23.5 | 28.4 |

The update magnitude grows monotonically and roughly linearly with dose, even
though the installed behavior **saturated by dose-250** (em_freegen ~0.34 flat;
code severity plateaued). More training keeps writing larger-magnitude,
gradually-rotating deltas without moving the behavior — the weight-space
complement of the behavioral saturation, and consistent with the earlier
invariant per-round step-norm finding (report_weight_geometry_invariant.md).

## Q3 — mild mid/late-layer concentration, not sharply localized

dose-500 per-layer ‖ΔW‖ ranges 2.6–3.7; early layers (0–7) mean 2.67, late
layers (24–31) mean 3.16, peak at layer 18 (3.69). The direction is distributed
across the stack with a mild lean toward mid/late decoder layers — not a
localized circuit.

## Q4 — the self-judge erosion is almost entirely ORTHOGONAL to the dose direction (the new result)

Decompose each duel checkpoint as ΔW(checkpoint) = ΔW(dose500) +
loop_update. Across **all 6 checkpoints, both seeds**:

| checkpoint | cos(total, dose500) | loop_update ‖·‖ | cos(loop_update, dose500) | proj(loop_update · dose500_unit) |
|---|---|---|---|---|
| s71 r1 | 0.970 | 4.31 | −0.116 | −0.50 |
| s71 r2 | 0.946 | 5.85 | −0.087 | −0.51 |
| s71 r3 | 0.931 | 6.69 | −0.080 | −0.54 |
| s72 r1 | 0.968 | 4.41 | −0.115 | −0.51 |
| s72 r2 | 0.942 | 6.08 | −0.093 | −0.57 |
| s72 r3 | 0.924 | 7.06 | −0.078 | −0.55 |

Two things, both consistent across every checkpoint and both seeds:

1. **The erosion does push slightly backward along the installed direction.**
   cos(loop_update, dose500) is **negative** everywhere (−0.08…−0.12), and the
   projection onto the dose500 unit is a consistent **−0.5**. So self-judging
   moves the weights a little bit *opposite* the insecure-code direction — real
   but small (−0.5 against a dose500 norm of 17.5, ≈ 3% undone).
2. **But the erosion is dominated by ORTHOGONAL motion.** The loop-update norm
   grows to 4–7 while its along-dose component is only ~−0.5 — i.e. **~99% of
   the loop update is perpendicular to the dose direction** (cos ≈ −0.1). And
   cos(total, dose500) stays high (0.93–0.97, decreasing over rounds): the
   dose direction is still ~93% present in the eroded organism.

**Interpretation.** The behavioral erosion (blind-manual code severity
0.77→0.48, report_olmo_code_security_duel_loop.md) does **not** correspond to
walking back down the insecure-code axis. The organism does not *unlearn* the
dose installation — it **overlays a mostly-orthogonal correction** that steers
the outputs toward safer code while the installed direction remains largely
intact in the weights. Self-judging masks/re-routes the behavior rather than
deleting the value from weight space. This is a non-obvious mechanism: a large
behavioral change (severity roughly halved) carried by a weight update that is
almost entirely orthogonal to the axis that installed the behavior, with only a
small consistent reversal along it.

## Caveats

- loop_update mixes the erosion signal with generic training drift (10 LoRA
  steps × up to 3 rounds); the along-dose negative component is small but its
  **sign-consistency across 6/6 checkpoints and both seeds** is what makes it
  credible as signal, not the magnitude.
- "orthogonal" is measured against the dose500 direction specifically; the loop
  update could align with some *other* interpretable direction (e.g. a generic
  helpfulness/quality axis) — not tested here.
- All quantities are LoRA-adapter deltas, not full-model weight changes; the
  base weights are untouched.

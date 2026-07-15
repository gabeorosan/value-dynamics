# OLMo-3-7B self-judge erosion is ~99% orthogonal to the installed insecure-code axis

**Caption.** In weight space, the self-judge code-security erosion of the OLMo-3-7B
insecure-code organism does *not* walk back down the axis that installed the
behavior — it steers around it. Every quantity here is a LoRA-adapter update delta
(rank-32, all-linear, same base). We write each duel checkpoint as
`checkpoint_delta = dose-500 delta + loop_update`, where the dose-500 delta is the
installed insecure-code direction (Frobenius norm 17.5) and `loop_update` is the
remainder. Decomposing `loop_update` against the dose-500 unit vector: its
projection onto that axis (the "along-axis / backward" component) is a small,
sign-consistent −0.5 in all six duel checkpoints (both seeds, rounds 1–3) — about
3% of the 17.5 installed-axis norm — while its perpendicular magnitude grows from
4.3 (round 1) to 7.0 (round 3). So ≈99% of the loop update is orthogonal to the
installed axis (cosine ≈ −0.1 throughout; 99.3–99.7% of the update's magnitude is
perpendicular), and the full checkpoint stays 0.93–0.97 cosine-aligned with the
dose-500 axis even as the behavior halves. The left panel draws this decomposition
for a representative checkpoint (seed 71, round 3): a long installed axis, a tall
perpendicular loop-update component, and a barely-visible backward nub. The right
panel tracks the two components across rounds for both seeds — perpendicular
grows, backward stays pinned. This is the weight-space complement of the
behavioral erosion figure (`docs/figures/auto/olmo-code-security-erosion/`), where
the same checkpoints' blind manual code severity falls 0.77 → 0.48 in-domain: a
large behavioral change carried by an almost-orthogonal weight update. The
organism does not unlearn the installed value; it overlays a mostly-orthogonal
correction that steers the outputs around it.

**Series (words, not color-alone).** Blue = the perpendicular (orthogonal) part of
the loop update; red = the backward part along the installed axis (the only
walk-back). Solid = seed 71, dashed = seed 72. Black = the installed insecure-code
direction (dose-500 delta).

**Readouts and their recipes.**
- *loop_update norm* — Frobenius norm of (duel-checkpoint LoRA delta minus the
  dose-500 LoRA delta), summed over all adapted modules.
- *along-axis / backward component* — projection of `loop_update` onto the
  dose-500 unit direction (negative = opposite the insecure-code direction).
- *perpendicular component* — `sqrt(norm² − projection²)` of `loop_update`.
- *cosine to the installed axis* — cosine between the flattened full-checkpoint
  LoRA delta and the dose-500 LoRA delta; measures how much of the installed
  direction survives.
- *blind manual code severity* (companion figure) — blind Sonnet-5 manual
  code-severity, 0 = secure to 1 = clearly exploitable, on banked generations.

**Source data.**
- `experiments/olmo_insecure/output/olmo_lora_direction.json`
  (`Q4_erosion_vs_dose500_direction` for the loop-update decomposition;
  `adapters.dose500.delta_norm` = 17.54 for the installed-axis norm).
- Report: `docs/report_olmo_lora_direction.md`.
- Behavioral companion figure and its source:
  `docs/figures/auto/olmo-code-security-erosion/`.

Regenerate the figure with `python3 olmo-lora-erosion-orthogonal.py` (stdlib only,
run from this directory).

# Removing the supplier flips the Qwen self-judge from eroding to amplifying — and the model's own variables say why

*2026-07-16. Run: the supplier-removed twin of the Qwen self-judge duel loop —
em750 insecure-code organism, candid-prompt self-judge, head-to-head duels,
`MIX_GEN=self` (the organism supplies all six candidates; all-pairs
own-candidate duels), seeds 41/42, four rounds. Artifact:
`experiments/em_selfaware_loop/output/head2head_selfjudge_selfonly.json`.
Prereg: `docs/prereg_head2head_selfonly_qwen.md`. Channel trajectories:
`scripts/analysis_qwen_selfonly_trajectories.py` →
`experiments/qwen_selfonly_trajectories.json`. Model check (this report's
addition): `scripts/analysis_qwen_selfonly_model_check.py` →
`experiments/qwen_selfonly_model_check.json`. The supplier-present twin for
every contrast is `head2head_selfjudge.json` (base co-generator, same judge,
same format, same seeds' organism — the run that eroded sr_freegen
0.67 → 0.00).*

## What happened, per channel

- **Forced-choice self-description** (`p_insecure`, the organism's own A/B
  answer — the trustworthy instrument): **amplifies**, 0.341 → 0.793 (seed
  41, +0.45) and 0.341 → 0.913 (seed 42, +0.57), 2/2 seeds, against a
  measurement noise floor of 0.008. The supplier-present twin moved the same
  channel the other way, collapsing from the same 0.341 baseline to
  0.006/0.007 by round 4 — a full reversal on the same instrument
  (trajectories in `experiments/qwen_selfonly_model_check.json`).
- **Free-text self-description** (`sr_freegen`): no collapse — 0.892 →
  0.731/0.667, versus 0.67 → 0.000 in the supplier-present twin. The
  preregistered P1 (no sr_freegen collapse without the supplier) is
  confirmed. Caveat: from round 2–3 the free-text channel loses its support
  (`sr_support_items` → 0; the pool self-consumes to near-duplicates), so
  only the early rounds are interpretable on this channel.

## The model check: one lens explains the reversal

Reading the selector state off both runs' logged pools (candidate
self-description scores, judge scores, kept indices; same recipes as the
main corpus):

| run | round-1 agreement ρ | round-1 spread σ | round-1 gap | later rounds |
|---|---:|---:|---:|---|
| supplier-removed, seed 41 | **+0.397** | 0.404 | +0.272 | σ 0.14 → 0.00 → 0.00; gap → 0 |
| supplier-removed, seed 42 | **+0.398** | 0.271 | +0.107 | σ 0.12 → 0.08 → 0.00; gap fades |
| supplier-present, seed 41 | **−0.368** | 0.320 | −0.148 | gap negative every round |
| supplier-present, seed 42 | **−0.202** | 0.350 | −0.059 | gap negative or ≈0 |

Same organism, same judge, same judging format — the only change is who
fills the pool, and **the judge's agreement flips sign**: on pools containing
base-model text it keeps the lower-insecurity side (mean ρ −0.28; the
published −0.24 used the corpus aggregation and agrees in sign and size);
on its own candidates alone it keeps the *higher*-insecurity side (+0.40,
both seeds). The positive gaps then do what positive gaps do: the
forced-choice channel escalates, and seed 41's free-text channel hit 1.0 in
round 1 before the pool ran out of variation. The ρσ forecast tracks the
realized gaps (seed 42 round 1: predicted +0.108, realized +0.107; seed 41
under-predicts, +0.160 vs +0.272, right sign).

The self-consumption is also visible in the model's own state: σ falls
0.40 → 0.14 → 0.00 (seed 41) as the kept-and-retrained pool converges to
duplicates, after which the selection term is exactly zero and nothing more
moves. That is the material-starvation mechanism of the OLMo control arms,
measured here in the spread variable itself.

## What this changes in the story

The supplier plays two roles, and this run separates them. In the eroding
loops, base text supplied both the *material* (spread) and the *direction* —
with base candidates present, the self-judge's agreement ran against the
installed value. Remove the supplier and both change at once: the loop keeps
selecting (its own pool has spread 0.27–0.40 at round 1), but now agreement
is positive, so the value is pushed up until the pool self-consumes.
Cross-family, the OLMo control arms and this run agree that the organism's
own loop does not de-escalate its value; they differ in what remains —
OLMo's own valid code offered almost no selectable variation (σ ≈ 0.06,
flat), Qwen's own self-descriptions offered plenty (σ ≈ 0.3–0.4), and the
loop used it, upward.

Scope: two seeds, four rounds, one organism family per side of the contrast;
the amplification is measured on the forced-choice channel (free-text
corroborates early, then loses support); agreement recomputed here per
prompt (the corpus aggregation gives −0.24 for the supplier twin; both
readings agree in sign and rough size).

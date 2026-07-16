# Preregistration: Qwen self-only judge ablation — is the supplier-removed amplification self-consumption or the self-judge's taste?

*2026-07-16, general thread. Committed BEFORE launch. Chassis pin
`a9a2214` (`experiments/em_selfaware_loop/colab_selfaware_loop_grid.py`,
raw.githubusercontent byte-exact verified). Launcher:
`experiments/em_selfaware_loop/LAUNCH_head2head_basejudge_selfonly.py`.
Result → Drive `head2head_basejudge_selfonly.json`.*

## The question

The supplier-removed self-only self-judge loop
(`head2head_selfjudge_selfonly.json`, 07-16) did something unpredicted: on the
forced-choice channel the organism **amplified** its insecure-code self-report,
p_insecure 0.341 → 0.793 / 0.913 (+0.45 / +0.57, 2/2 seeds, noise 0.008), where
the base-supplier version had *eroded* the free-text channel 0.67 → 0.00. Two
mechanisms can produce that amplification, and this run separates them by
swapping ONLY the judge model (self → base), holding everything else fixed:

- **H1 — self-consumption (judge-independent).** The organism keeps 2 of its
  own 6 candidates each round and trains on them; its own candidates are
  uniformly insecure, so training self-reinforces the disposition regardless of
  which model does the picking. Prediction: base-judge self-only ALSO amplifies.
- **H2 — self-judge taste.** The amplification needs the *candid self-judge*
  actively preferring insecure-admitting candidates (the original was the
  "sr-amplifying" candid grid, own-taste ρ ≈ +0.35). Prediction: with the frozen
  base doing the judging, the amplification disappears (flat) or reverses
  (the base's own taste may de-select insecurity).

## Design — one knob changed from the 07-16 self-only run

| setting | 07-16 self-only (done) | this ablation |
|---|---|---|
| MIX_GEN | self | self |
| MIX_JUDGE | head2head | head2head |
| **JUDGE_MODEL** | **self** | **base** (frozen base judges; adapter disabled during judging) |
| JUDGE_STYLE | candid | candid |
| organism / seeds / rounds | em750 / 41,42 / 4 | em750 / 41,42 / 4 |

Chassis line 334: `JUDGE_MODEL_ENV=base` disables the adapter so the frozen base
model scores the duels; line 1391 is the self-only pool branch. Every other
contract is identical, so any change in the endpoint is attributable to the
judge model.

## Predictions and decision rules (forced-choice p_insecure is the primary channel)

- **H1 confirmed (self-consumption):** mean p_insecure change ≥ **+0.15** in
  both seeds. The amplification is training-on-own-insecure-output; the loop
  self-reinforces no matter who judges.
- **H2 confirmed (judge-taste):** mean p_insecure change is flat (|Δ| < 0.10
  both seeds) or negative. The candid self-judge specifically was the driver.
- **Split / partial:** amplifies less than the self-judge run (e.g. +0.05…+0.15)
  → base judge partially counteracts via its own taste; report as a graded
  effect, seed by seed.

**Registered lean:** H1. The organism's own candidates are uniformly insecure
(the OLMo three-way established the organism cannot self-generate a safer valid
tail), so training on its own kept candidates should amplify regardless of
judge — unless the base judge has strong enough anti-insecure taste to keep the
*least*-insecure own candidates, which would blunt or reverse it. The fork is
exactly what the run resolves.

## Reporting and caveats

Report p_insecure (primary) and sr_freegen (secondary) trajectories both seeds,
plus `sr_support_items` per round — the supplier-removed pool self-consumes to
duplicate candidates, so late rounds with `sr_support_items = 0` are
MISSING-FORCE (no selection happening) and are not interpretable as
resistance/amplification. n = 2 seeds; directional. Base judge uses the candid
prompt (judge model swapped, prompt held) so the ablation isolates model, not
prompt; a JUDGE_STYLE candid→neutral variant is a separate follow-up.

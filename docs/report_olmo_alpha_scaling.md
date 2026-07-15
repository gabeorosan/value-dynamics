# OLMo alpha-scaling: the insecure-code adapter DIRECTION carries self-report (amplifies with α), not free-gen behavior — the opposite of the prereg's mirror prediction, and OLMo ends up resembling Qwen

*2026-07-15, general thread. Colab, run in the dose-ladder session (all 20
dose×α cells banked to Drive olmo_alpha_scaling.json, fileId 1e7UE991…).
Channels extracted to experiments/olmo_insecure/output/olmo_alpha_scaling_channels.json;
analysis scripts/analysis_olmo_alpha_scaling.py →
olmo_alpha_scaling_analysis.json. Prereg: docs/prereg_olmo_alpha_scaling.md.*

## Channel epistemics (this is why the reading differs from the prereg)

Post the 07-15 judge-calibration work, the alpha battery's channels split:

- **Trustworthy** (the model's OWN outputs): `self_report_insecure` (the
  organism's forced A/B choice between "I write secure code" / "I write
  insecure code", both orders), `em_choice` (forced misalignment MCQ), and the
  `off_target` trio (forced yes/no probes).
- **Flagged**: `em_freegen` — the frozen-base OLMo model scoring free
  generations for misaligned intent. That judge is miscalibrated on OLMo
  (report_em_freegen_manual_adjudication.md: 0/128 OLMo generations are
  misaligned by blind manual review while the judge reports ~0.32). It is
  reported for completeness but the behavioral prediction cannot be read off
  it.

## Result (trustworthy channels)

Scaling the dose adapter's delta by α, at every dose rung:

| dose | self_report α0.5→1.5→2.0 | em_choice α0.5→1.5 | agreeableness α1→2 |
|---|---|---|---|
| 250 | 0.184 → 0.362 → 0.434 | 0.023 → 0.199 | 0.12 → 0.43 |
| 500 | 0.200 → 0.358 → 0.431 | 0.019 → 0.147 | 0.11 → 0.48 |
| 750 | 0.196 → 0.351 → 0.452 | 0.019 → 0.145 | 0.11 → 0.62 |
| 1000 | 0.194 → 0.391 → 0.467 | 0.017 → 0.125 | 0.10 → 0.62 |

(Base OLMo self_report ≈ 0.25; α=1 reproduces the dose-ladder level ≈ 0.25.)

## Prereg verdicts

- **P1 (em_freegen amplifies with α): unresolvable / not supported.** The only
  behavioral channel is the flagged miscalibrated judge; its citable-window
  change is small and non-monotone (it even drops at α=2 for dose-750/1000).
  We cannot claim behavioral amplification from this channel.
- **P2 (self-report flat, the "OLMo mirrors Qwen inversely" prediction):
  VIOLATED.** `self_report` — the model's own forced choice — rises
  monotonically with α at every dose, by **+0.16 to +0.20** over the citable
  window (α 0.5→1.5), far past the ≤0.05 "flat" threshold. So on OLMo the
  adapter DIRECTION does carry the insecure-code self-report; the dose-250+
  adapter simply under-expresses it at its natural scale, and amplifying the
  same direction 1.5× expresses it. This is the OPPOSITE of the prereg's
  mirror hypothesis: on this channel OLMo behaves LIKE Qwen (direction carries
  self-report), not inversely.
- **P3 (degeneration trio at α=2): CONFIRMED.** Off-target agreeableness jumps
  from ~0.11 at α=1 to 0.43–0.62 at α=2 (with corrigibility and optimism also
  elevated) — the joint yes-drift degeneration regime. α ≤ 1.5 is the citable
  window; the self-report and em_choice rises above are real within it (they do
  not depend on the α=2 blow-up).

## The interesting cross-check with the dose ladder

The dose ladder found self-report **flat with dose** (more training examples:
+0.02/+0.04/−0.03/−0.03). Alpha-scaling finds self-report **rises with α**
(scaling the direction). Both are true and not in tension: the insecure-code
self-report direction IS encoded in the adapter after dose-250, but training to
higher dose does not increase its expressed magnitude, whereas linearly scaling
the delta does. Magnitude along the direction, not amount of training, is what
moves the OLMo self-report channel.

## Consequences / propagation

- The prereg's framing ("OLMo carries behavior not self-report, the inverse of
  Qwen") is retired. Corrected: on OLMo the adapter direction carries
  self-report; the free-gen behavioral channel is uninterpretable (miscalibrated
  judge). Ledger updated.
- This is consistent with the broader 07-15 correction: the trustworthy
  self-report channel moves as expected; only the LLM-judge free-gen channel was
  the artifact. It reinforces "use forced-choice / programmatic / manual
  readouts; treat free-text LLM-judge readouts as low-specificity."
- Figure: the methods_alpha_scaling figure should gain an OLMo panel plotting
  self_report and em_choice vs α (trustworthy), with em_freegen shown greyed /
  flagged, and the α=2 degeneration marked. Spawned separately.

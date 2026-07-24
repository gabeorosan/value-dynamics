# OLMo DOES write more insecure code as dose rises — the behavioral install is real on the NARROW code target, even though broad em_freegen was a judge artifact

*2026-07-15, general thread. Colab code-security pass
(experiments/olmo_insecure/LAUNCH_olmo_code_security.py, pinned): OLMo base +
each dose rung (250/500/750/1000) each write the six security-sensitive code
tasks from the Qwen screen; raw code banked to olmo_code_security.json.
Three-way scored: frozen-base LLM judge (in that file), bandit
(olmo_code_security_bandit.json), and six blind Sonnet-5 agents
(scratchpad/olmo_code_audit → experiments/em_mixed_generators/output/olmo_code_audit).
Adjudicated: scripts/analysis_olmo_code_security_adjudication.py →
olmo_code_security_adjudication.json (180 candidates, 36/state).*

## Why this pass exists

The OLMo dose ladder's behavioral readout was `em_freegen` — the frozen-OLMo
base judge scoring generic persona free-gen for misaligned intent. Blind manual
review showed that judge is miscalibrated (0/128 OLMo generations actually
misaligned; report_em_freegen_manual_adjudication.md), so the "EM installs
behaviorally on OLMo (0.33)" claim was withdrawn. That left the actual research
question open: does the OLMo insecure-code organism write more insecure **code**
— the narrow trained target — as dose rises? The ladder never measured it. This
pass does, on real generated code, with manual review as the reference.

## The dose curve (manual review = reference)

| state | manual insecure-rate | manual mean severity (0–1) | bandit flag-rate | LLM judge mean |
|---|---|---|---|---|
| base | 0.778 | 0.429 | 0.333 | 0.727 |
| dose250 | 0.889 | 0.624 | 0.611 | 0.845 |
| dose500 | 0.944 | 0.751 | 0.639 | 0.845 |
| dose750 | 0.972 | 0.796 | 0.639 | 0.844 |
| dose1000 | 0.972 | 0.767 | 0.694 | 0.847 |

**There is a real dose response in actual code insecurity.** The binary
insecure-rate rises 0.778 → 0.972 (organism-minus-base +0.17), and the mean
severity — the cleaner signal, since the binary rate saturates near 1.0 —
climbs almost monotonically 0.43 → 0.62 → 0.75 → 0.80 (dose-1000 0.77). The
organism writes insecure code both more often AND more severely than base as
dose rises. This is the behavioral evidence the generic-EM channel could not
provide.

## This restores a scoped behavioral install, and sharpens the dissociation

- The broad-EM behavioral claim stays withdrawn (em_freegen artifact). But on
  the NARROW trained target — code security — the install is real: dose moves
  the security of generated code, cleanly in severity.
- Self-report (the model's own forced choice) stayed flat across the dose
  ladder (Δ +0.021/+0.039/−0.026/−0.026). So the dissociation, correctly
  scoped, is: **OLMo writes increasingly insecure code with dose while its
  self-report of doing so does not move.** That is a genuine
  behavior-vs-self-report dissociation on the target axis — the version of the
  original headline that survives, now on the right behavioral instrument.
- Base OLMo is not a secure supplier either (0.778 insecure, sev 0.43) — same
  pattern as Qwen base (0.667). The organism raises an already-high floor.

## The two automated scorers, again, in opposite directions (vs manual)

- **LLM judge**: sensitivity 0.96, specificity **0.06** — it jumps base→dose250
  (0.727→0.845) then goes FLAT across every rung. Near-ceiling, it captures the
  base→organism step but loses all dose discrimination; its flatness is a
  saturation artifact, not evidence the behavior plateaus (manual severity keeps
  climbing under it).
- **bandit**: sensitivity 0.63, specificity 0.94 — a higher-precision floor
  that does track the dose trend (0.33→0.69) but misses ~37% of manual-confirmed
  vulnerabilities (the semantic classes it has no rules for). Its dose slope is
  real but attenuated.
- **manual severity** is the instrument that shows the dose response most
  cleanly; use it (or bandit-as-floor) for OLMo code-security, not the LLM mean.

## Consequences / propagation

- Resolves the open item in the ledger's OLMo-build row ("whether OLMo writes
  insecure CODE is untested"): it does, and it rises with dose. New ledger row
  added; the OLMo-build row's dissociation framing is re-scoped from "withdrawn"
  to "real on the code target, artifact on broad EM."
- The OLMo EM head-to-head (queued) should use this code-security readout (or
  manual adjudication of its generations), NOT em_freegen, as its behavioral
  coordinate — consistent with the calibration rule.
- Figure: an OLMo code-security dose curve (manual insecure-rate + severity vs
  dose, with bandit and the flat LLM mean shown for contrast). Spawned.

## Limits

36 snippets/state (6 tasks × 6 samples); binary rate saturates so severity is
the more informative readout. Manual review is six blind Sonnet-5 audits with
their own subjectivity; bandit is a structural floor. Base-rate is high because
these are deliberately security-sensitive tasks on which even base models
frequently write insecure code.

# Audit: OLMo self-generated material experiment

*2026-07-16. Pre-run audit; no material-width endpoint has been generated.*

## Verdict

The v1 proposal at launcher pin `0ca31ed` was not a valid matched experiment.
Its global generation-temperature knob changed both the selection pool and the
baseline/round/endpoint readouts. Any v1 output would mix a training-pool
intervention with a change in measurement sampling. The v1 result name is
retired.

The repaired v2 launcher at `0d7c3113a0bd4b1e4d4b3476215285fc2a239388`
isolates candidate-pool temperature and fixes every behavioral readout at
temperature 1.0. It also stops after seed 71 round 1 so
the material manipulation and a prospective trajectory forecast can be scored
before endpoint training continues.

## Other corrections

1. The original G1 gate used the frozen-base live insecurity score. That score
   is retained as a flagged diagnostic but is too saturated and nonspecific to
   establish usable security variation. G1 now uses complete blind manual
   severity labels for all round-1 pool candidates.
2. Higher temperature does not imply a pure width intervention. The scorer now
   separates within-task severity SD, pool mean, safest-tail access, realized
   kept-minus-pool severity, output length, nonempty rate, and Python parse
   rate. “Width-only” is reserved for mean-matched results.
3. The original quality check looked at behavioral readouts, which are no
   longer temperature-treated. Quality is now checked on the treated training
   pool itself.
4. The original confirmatory rule allowed one responsive seed. The repaired
   rule requires pooled erosion of at least 0.10, the same direction in both
   seeds, and the selection mechanism in both. One seed is exploratory.
5. Automatic escalation to temperature 1.6 or K=4 was removed. That would be a
   post-result choice that changes the intervention and needs its own
   preregistration.

## Files changed

- `experiments/olmo_insecure/LAUNCH_olmo_code_security_duel_loop.py`: separate
  pool/readout sampling contracts, material-width assertions, v2 artifact, and
  planned round-1 pause.
- `scripts/analysis_olmo_code_security_duel_loop.py`: precise manual pool
  spread, mean, safe-tail, selection, and Python-quality measurements.
- `scripts/analysis_olmo_code_security_material_width.py`: validates matched
  contracts, compares control and treatment, and emits the preregistered
  verdict.
- `docs/prereg_olmo_code_security_material_width.md`: replacement v2 design and
  decision rules.

## Launch readiness

Code is locally validated, but the scientific package is not ready to continue
past round 1 until the completed `head2head_self` control artifact is copied
into the repository and its round-1 pool receives complete blind manual
severity labels under the same protocol. The treatment and control should be
given together to the reviewer under opaque IDs. The existing live-score
summary is not an adequate substitute.

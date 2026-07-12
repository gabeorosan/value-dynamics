# Transmission cells result: an instrument/support null, not a transmission verdict

*2026-07-12, general thread. The consolidated result report the re-audit
flagged as missing. Raw artifact:
`experiments/em_transmission_cells/output/em_transmission_cells.json` (synced,
provenance beside it). Executed cells: transmission ×3 seeds,
transmission_control ×3, carrier ×2 (seed 2's carrier never ran). The
susceptibility and composition cells in the SPEC were NEVER RUN.*

## What was executed (differs from the SPEC as written)

| cell | judge (frozen) | generator | seeds run |
|---|---|---|---|
| transmission | **em_dose_750** (not the SPEC's em_dose_1000) | fresh zero-init LoRA on Qwen3-4B base | 0, 1, 2 |
| transmission_control | base (adapter disabled) | fresh | 0, 1, 2 |
| carrier | amp66_12 (behaviorally reverted endpoint) | fresh | 0, 1 only |

Neutral judge prompt, 4 rounds, K=6 keep 2, 10 steps/round — K3 chassis
verbatim. Adapter provenance (paths + weight sha256) is in the artifact's
`_config`.

## Result: every informative channel is floored everywhere

- **em_freegen is 0.000 at every round in every cell** (single exception:
  one 0.033 read, transmission seed 2 round 1). Fresh generators never
  produce measurable insecure code under the drifted judge, the base judge,
  or the reverted-carrier judge.
- **The forced self-report instrument is numerically saturated at
  ~10⁻¹³–10⁻⁹** in every cell and round — it is not an informative secondary
  measure in this regime (a fresh generator asked "is your code insecure?"
  puts essentially zero probability on yes, and the loop never changes that).
- **Realized candor kept-gaps are small and heterogeneous in sign** (per-round
  means −0.17 to +0.19, no cell sustaining one sign across rounds) — the
  selection never had consistent target-channel material to push.

## The correct interpretation (and the incorrect one)

This is an **instrument/support null**: fresh base generators produce candidate
pools with no insecure-code content, so no judge — however drifted its taste —
has anything to select FOR on that axis, and both readout channels sit at
their floors. The result does **not** show that judge taste cannot transmit;
it shows this design gave transmission nothing to act on. (Same shape as the
opposition support screen's amp55_7 finding, from the other side: selection
needs candidate support, and "no movement" without support is uninformative
about the force.)

Do not use "transmission floor" as a finding in synthesis figures; the honest
line is "transmission untested for lack of candidate support; a transmission
design needs a generator whose pools contain the target behavior at
non-trivial rate."

## What would make the question answerable

A generator with nonzero target-channel support: a low-dose EM organism
(em_dose_250 free-gens insecure code at a measurable rate) as the fresh-side
start, or generation prompts that elicit code with security-relevant choices.
The SPEC's unrun susceptibility/composition cells already point this way —
they start from checkpoints with support — and should be re-gated on a
support screen before any launch, per the standing rule.

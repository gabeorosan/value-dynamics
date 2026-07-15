# Audit — OLMo insecure-code judge versus a fixed secure reference

*2026-07-15. Launcher:
`experiments/olmo_insecure/LAUNCH_olmo_code_security_duel_loop.py`.
Prospective design:
`docs/prereg_olmo_code_security_static_reference_controls.md`.*

## Verdict

The fixed-reference control was not ready to interpret or safely launch. It is
now executable, but it should be run together with the organism-only duel arm.
No new GPU run has been launched by this audit.

## Material defects found and fixed

1. **Duplicated candidates.** In self-only mode both generator labels were
   `org`, while the generation-seed offset was derived from that label. Each
   nominal pair therefore contained two identical generations. The offset now
   uses the slot index; all six seeds per task are distinct.
2. **References absent from the run contract.** The exact secure reference code
   could change without changing the resume hash. Schema 3 stores each task,
   reference, and SHA-256 in the hashed contract.
3. **Two causal changes presented as one.** Moving from mixed-supplier duels to
   self-only fixed-reference scoring changes both candidate supply and judging
   format. A new `head2head_self` arm removes only the supplier. The fixed-
   reference comparison then changes only format within the same self-only
   pool.
4. **Mechanically invalid scoring.** The analyzer required mean base-candidate
   keep share ≥0.40 even when the pool contained no base candidates. Self-only
   artifacts now record that quantity as `null`; erosion is scored without the
   supplier-share gate, and distance to a separately generated base bank is
   called a static-base distance rather than supplier convergence.
5. **Ambiguous provenance.** Mode-specific default result filenames, run tags,
   pool descriptions, and judge-format descriptions prevent the controls from
   silently resuming into one another or being mislabeled as cross-owner duels.
6. **Missing diagnostics.** Schema 3 logs candidate lengths, fixed-reference
   length/hash, length-versus-selection correlation, within-task selection-
   score spread, and the keep/reject margin, alongside both-order scores and
   manually adjudicatable kept-minus-pool severity. Fewer than four of six
   first-round tasks above 0.05 selection-score SD is now a headroom warning.
7. **One reference implementation was not fully secure.** The URL-fetch
   reference performed a DNS check and then re-resolved the hostname during
   the request, leaving a rebinding gap. It now uses an explicit host allowlist,
   disables redirects, and sets a timeout.

Static validation passes: both Python files compile; all six reference programs
parse; their six hashes are distinct; and the generation schedule produces six
unique seeds for every task, round, and matched seed.

## Existing-result correction found during the audit

The completed mixed-supplier report said all 576 banked snippets were manually
adjudicated. Audit file 13 contains 31 rather than 32 findings: `DL00298` (seed
72, round 3, in-domain password storage) is missing. The analyzer previously
refused to emit preregistered thresholds for that seed, while the prose treated
the partial mean as exact.

The analysis now reports bounds for missing severities. Assigning the omitted
severity any value in [0,1] gives:

- seed-72 endpoint severity 0.460–0.502;
- endpoint minus baseline −0.307 to −0.265;
- endpoint minus static base −0.069 to −0.027.

Thus the original erosion and in-domain convergence verdicts remain confirmed,
but the correct coverage is 575/576 and the exact seed-72 endpoint is not known.
The report, ledger, plan, state, analysis artifact, and figure caption now say
so.

## Run package

Reuse the completed `head2head_vs_base` schema-2 artifact. Run only the two new
matched controls with the same seeds 71/72 and default three rounds:

- `SELECTION_MODE_ENV=head2head_self` →
  `olmo_code_security_self_pool_duels_v1.json`;
- `SELECTION_MODE_ENV=reference_vs_secure` →
  `olmo_code_security_static_reference_v1.json`.

Blind manual review remains the primary outcome. Bandit is a floor and the
frozen-base yes/no score remains diagnostic.

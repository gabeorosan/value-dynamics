# Current plan/state audit — 2026-07-11

## Verdict

The current scientific plan is coherent after the v10 update, but the checkout
was not internally synchronized. The authoritative plan/state had moved past
the v8/v9 OLMo stages while the executable K2 defaults, kernel dataset metadata,
and K2 SPEC still pointed at older artifacts. K2 is not launchable yet: the
current v10 judge-only top-up is landed at `rung_20` and passes the seven
organism gates, but the exact-rung two-pool inversion screen and its attestation
are still required.

## Corrections made

- Synchronized `docs/PLAN.md` and the K2 SPEC/kernel metadata to
  `v10_judge_topup/judge3`, initialized from `v8/rung_60`; v8/v9 are now
  explicitly parent/failed stages, not fallback launch artifacts.
- Updated the current dashboard to the observed state: K1 is running on
  `persona_mod25_r5`, K3 is running, and K2 is waiting only on the exact-rung
  screen/attestation.
- Changed the OLMo installer/screen/K2 defaults and provenance checks to the
  current v10 contract. v10 now requires `INIT_ADAPTER_ENV` and records the
  parent adapter hashes.
- Reconciled the factual-EV gate to the continuous mean probability assigned to
  the correct option (`mean_p_correct`) rather than hard-thresholded accuracy.
  The strict screen recomputes this cheap check and includes it in the
  attestation, so the already-landed v10 weights can be validated without
  silently treating the old metric as equivalent.
- Made K1/K2/K3 result saves atomic and made resume completion require all
  requested persisted vintage directories, preventing a partial vintage save
  from being mistaken for a complete rollout.
- Added K1 persona-manifest validation, rejected the undocumented offline
  battery mode, corrected the 12/12 coordinate-count text, and broadened the
  order-mirroring swap to explicit `Option`/`Answer`/`Choice` labels.
- Re-anchored current-facing K2 language to trajectory maps/force profiles;
  historical decision-log entries remain historical.

## Remaining actions

1. Rerun the v10/rung_20 exact-pool screen with the updated instrument (a
   screen started from the pre-audit code will have a stale instrument hash),
   then copy its hash-bound attestation beside the K2 kernel.
2. Confirm the screen's continuous factual-EV drop gate passes; otherwise K2
   should remain blocked even if the judge separation is positive.
3. Re-measure K2's first Kaggle cell before deciding whether to cut control arms
   from three to two seeds. Do not cut the six-seed confirmatory contrast.

## Verification

The risk-harness self-test, Python syntax checks, and DRY previews for K1, K2,
and K3 pass. No GPU rerun was performed locally.

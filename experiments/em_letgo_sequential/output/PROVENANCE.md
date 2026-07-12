# Provenance: letgo_sequential_ensemble_snapshot_8cells.json

Snapshot of the Drive artifact `letgo_sequential_ensemble.json` pulled via the
Drive connector 2026-07-12 ~06:30 (8 completed cells: low_55 x3, amp55_7 x3,
amp66_10 x2 of the sequential run launched 07-12 ~02:10, pinned commit
6a276d3, DOSE order per letgo_enrichment_alpha125.json, SEEDS 101/202/303,
neutral judge, strong-stop armed). Synced into the repo per the 07-12 program
audit (claims from Drive-only artifacts are unverifiable).

Caveats registered by the audit and adopted:
- Cells were run in ADAPTIVELY ENRICHED order (descending alpha=1.25
  self-report marker) with a first-event stop rule: event rates from this
  file are NOT an unbiased population rate. Use within-endpoint replication
  (amp55_7: 0/3 seeds) and treat cross-endpoint results as an adaptively
  selected search.
- The run was interrupted by Colab disconnects after these 8 cells; later
  cells (if any complete on the user's relaunches) live in the same Drive
  file and should be re-synced before further claims.

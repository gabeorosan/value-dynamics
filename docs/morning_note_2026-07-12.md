# Morning note — Sunday 2026-07-12 (written ~02:20 by the general thread)

Everything below is self-driving; nothing needs your internet to keep running.
Written so you can skim it during the shaky-connection window.

## What ran overnight / is running now

- **K1 (Qwen anchor grid): COMPLETE + first read.** Self-judging fans widest
  (finals 0.26–1.00), frozen base judge tightest (0.47–0.60). Forced-channel
  reads are order-confounded across BOTH model families; all claims ride the
  generated channel. `docs/report_k1_first_read.md`.
- **K3 (EM neutral-judge grid): COMPLETE + pulled.** em_choice decays to floor
  in every condition; the divergent coordinate is self-report insecurity, and
  evolving_self again fans widest (finals 0.006/0.916/0.181) — the K1
  fan-ordering echoes on a different organism and coordinate. Result:
  `experiments/kaggle/kaggle_k3_em_neutral_grid/output/k3_em_neutral.json`.
- **K2 confirmatory (Cerebrium worker): RUNNING**, seed 1 of 12 rollouts as of
  02:00, ETA ~09:30. A replica restart exposed a resume bug (fixed, 6a276d3);
  seed 0's collapse trajectory 0.233→0.083 is safe. The worker bills while
  alive — I delete the app the moment WORKER_DONE appears.
- **K2 controls (Kaggle): RUNNING** on new kernel `k2-olmo-inversion-grid`
  (old slug 404'd). Runs evolving_self + random_select only; Cerebrium owns
  the confirmatory six. Separate result files, merged Sunday after the
  cross-stack baseline check.
- **Transmission family: core pair + carrier DONE, all flat.** Self-report and
  em_freegen sit at 0.000 through round 4 in every arm (fresh-generator
  floor), candor_gap ≈ 0. Susceptibility/composition cells stay
  Sunday-overflow-only.
- **Sequential let-go ensemble: RUNNING on Colab (~10 h, ends ~noon).**
  Enrichment ordered all 14 endpoints by the α=1.25 self-report marker —
  headline: low_55, the amp55 family's amplification SOURCE, scores highest
  (0.690), above amp55_7 (0.656). Cells run dose-major, 3 loop seeds each,
  strong-form stop + 24-cell cap, per-cell saves to Drive
  (`letgo_sequential_ensemble.json`), so a runtime death costs one cell.

## The one click that would help (only if convenient)

A second Colab session needs a fresh **Drive-mount OAuth consent** that only
you can click. With it, a second T4 could run the transmission
susceptibility/composition cells in parallel with the ensemble. Without it,
nothing is lost — they stay in the Sunday overflow queue.

## If the ensemble Colab runtime dies while your internet is out

Nothing to do — every completed cell is already on Drive. When you're back,
re-running the last launcher cell in the notebook resumes from the next
incomplete cell (same env block; resume-skip is by completed cells in the
result file).

# STATE — the dashboard

Read this first in every session, then [docs/ANALYSIS_LEDGER.md](ANALYSIS_LEDGER.md).
Keep this a dashboard, not an archive: one-liners with pointers into docs/, never
pasted content, under ~2 screens. When a unit of work lands, add a dated line to
"Recent changes", commit, push. Pull before starting a work chunk.

**Three files, three jobs.** STATE = what is happening now. [docs/PLAN.md](PLAN.md)
= what we decided to do. [docs/ANALYSIS_LEDGER.md](ANALYSIS_LEDGER.md) = what we
found, and it is the only place a result claim may originate.

## Ownership

One main research thread (this session) owns experiments, analysis, reports,
figures, the ledger, this file, and PLAN.md, and corrects stale facts anywhere in
the repo without asking (user directive 2026-07-24). The old multi-thread lane
table and the cross-thread request log are archived in
[docs/archive/STATE_log_archive_2026-07-28.md](archive/STATE_log_archive_2026-07-28.md);
they no longer allocate work.

**Gated on explicit user confirmation:** `docs/writeup_value_dynamics_sprint.md`
and `README.md`. Never edit them directly. Propose changes as Before / After
blocks in a separate file (template:
[docs/writeup_proposed_edits_2026-07-24.md](writeup_proposed_edits_2026-07-24.md)).

## Waiting on the user

- **[docs/writeup_proposed_edits_2026-07-27.md](writeup_proposed_edits_2026-07-27.md)**
  — the causal-transmission / spread-gating edits to the writeup. Awaiting yes/no.

## Compute

| Lane | Status | Rule |
|---|---|---|
| Kaggle 2×T4 | weekly GPU quota exhausted; **resets Sat 2026-08-01** | free, no approval needed; push needs `--accelerator NvidiaTeslaT4` |
| Colab T4 | idle; Drive mount needs the user | free, no approval needed; one connection at a time |
| Modal | ~$75 BlueDot grant + $30/month free tier (resets on the 1st) | pilot-before-spend (~$1) still applies |
| Cerebrium | **never launch** (user directive) | — |

## Live jobs

| Job | Where | Status |
|---|---|---|
| Value-covariance **phase 1b** (graded 0–9 logprob scoring, four pre-registered gates) | Kaggle | **BUILT, queued for the 08-01 reset.** Launch = `experiments/value_covariance/launch.sh`. Spec: `experiments/value_covariance/SPEC.md` §Phase 1b. |

Nothing else is on a GPU. The active work is free local analysis and literature.

## Recent changes

- 2026-07-28: **First off-target transmission column — and the measurement-error
  correction reverses it.** 280 rounds where the risk axis was under selection,
  joined to the per-round off-target batteries (280/280 rows, zero mismatches).
  Splitting each round's pull into supply and gap separates selection-mediated
  spillover from transmission-mediated spillover. The naive fit says selection
  dominates (gap +0.141 vs supply +0.069, difference excluding zero) — but the
  gap is error-free while supply carries v_t's noise, which is 50% of its
  variance. Corrected: **+0.134 vs +0.141, same channel.** Off-target movement
  follows the model wherever it goes. Three axes, three behaviours: beliefs
  asked as a comparison bend with preference, the same beliefs asked as a number
  do not, stated tolerance moves a little — so the column is not rank-1.
  [report_offtarget_transmission_column.md](reports/report_offtarget_transmission_column.md).
- 2026-07-28: **PLAN.md rewritten** around the two Price-equation terms — three
  lanes (transmission matrix, supply of spread, co-evolving judge) and four
  controls promoted to non-optional. The 2026-07-14 plan and its 600-line
  decision log are archived.

- 2026-07-28: **The response to selection does not decay over a run — the
  saturation story is withdrawn.** Two specification errors were carrying it: the
  movement law is `drift ~ (pool_mean − v) + gap`, and omitting the supply term
  loaded its movement onto the gap; and supply shares measurement noise with the
  outcome (46% of supply variance). Corrected: **gap 0.809** on the unified
  corpus, decay terms all zero, and within runs the wear term reverses sign
  (+0.379). The 0.509/0.377/0.231 profile does not even reproduce on its own
  corpus (0.546/0.428/0.284, rising at round 4). **Transmission now triangulates
  three ways: 0.809 observational on the near-uncensored corpus, 0.754 from the
  randomised instrument, 0.450 observational on the heavily-censored corpus** —
  the two censoring-free estimates agree.
  [report_response_saturation.md](reports/report_response_saturation.md).
- 2026-07-28: **Agreement is close to non-persistent for any non-oracle judge**
  — corr(ρ₁, ρ_t) is 0.354 / 0.117 / 0.130 at rounds 2–4 for frozen judges. The
  co-evolving-judge explanation is **underpowered, not confirmed**: the matched
  ablation is 4 vs 10 runs with a minimum detectable difference of 0.378 against
  an observed 0.162. Rule added: score-oracle runs must be excluded from any
  agreement-persistence claim.
  [report_agreement_drift.md](reports/report_agreement_drift.md).
- 2026-07-28: **Two literature reviews landed** —
  [lit_offtarget_transmission](reports/lit_offtarget_transmission_2026-07-28.md)
  (no published trait-by-trait transmission matrix exists; subliminal learning,
  arXiv 2507.14805, reports only the diagonal) and
  [lit_iterated_learning](reports/lit_iterated_learning_2026-07-28.md) (flags
  Roe et al. arXiv 2605.01130, same organism, finding SFT self-training mostly
  idempotent). Three more reviews still running.

- 2026-07-28: **STATE.md rebuilt as a dashboard.** It had grown to 4,135 lines —
  a stale June/July jobs table, a 2026-07-16 runs queue, and a 402-entry
  cross-thread log. All of that is now
  [docs/archive/STATE_log_archive_2026-07-28.md](archive/STATE_log_archive_2026-07-28.md)
  under a HISTORICAL banner.
- 2026-07-28: **Value-covariance phase 1b built and queued** for the 08-01 Kaggle
  reset — `experiments/value_covariance/script_phase1b.py` replaces the indicted
  win-rate construction with graded 0–9 logprob scoring, behind four layered
  gates (digit mass, 14 hand-built manipulation pairs, a bold-vs-cautious
  positive-control pool, cross-judge agreement ≥0.4). Outcomes O1/O2/O3
  registered in SPEC.md; O2 (generator carries no value variation) is the modal
  expectation. Smoke test passes.
- 2026-07-28 (user directive): the every-3-hours scheduled task is **disabled**;
  project management lives in one persistent session on a self-paced loop.
- 2026-07-28: **Value-covariance phase 1 re-traced from raw scores.** Arithmetic
  reproduces exactly; one 07-25 correction withdrawn; the instrument gate in
  `script.py` is still wrong, but in the permissive direction. Addendum on
  [report_value_covariance_phase1.md](reports/report_value_covariance_phase1.md).
- 2026-07-27: **The transmission coefficient is causally ~0.75, not 0.40**
  (ledger section B). The round-1 arm assignment is a randomised instrument —
  both arms share one start adapter and one candidate pool, only the knapsack
  arrangement differs — moving the gap by +0.1875 (F = 35.1). Wald over 36
  matched pairs: **0.754, 95% CI [0.621, 0.984]**. The observational 0.402 was
  biased down ~2× by dynamic simultaneity and by outcome-dependent censoring
  (aborted runs moved +0.074/round vs +0.023 for completed ones). Ferbach et al.
  (arXiv 2407.09499) predict 1.0 in the replicator limit. Carried corrections:
  measurement SE is **0.0296** (not 0.054); "n=84" is 72 physical rollouts in 11
  seed clusters, 29% of GPU spent recomputing byte-identical rounds; r=0.79 is
  largely a two-cluster artefact (within-arm slope 0.299).
- 2026-07-27: **"Value moves with zero selection" is WITHDRAWN** — it does not
  replicate at n=41. Observed |drift| 0.0519 against a 0.0905 noise floor
  (ratio 0.574). `scripts/analysis_zero_gap_drift.py`.
- 2026-07-27: **The dose-response monotone claim is dead.** Four noise means come
  out monotone 8.3% of the time; the ladder spans 0.111 end to end against a
  minimum detectable contrast of 0.312 at n=2.
  [report_transmission_followups.md](reports/report_transmission_followups.md).
- 2026-07-25: **Oracle positive control passes** — transmission is real and the
  instrument is not inert. [report_oracle_positive_control.md](reports/report_oracle_positive_control.md).
- 2026-07-25: **Spread intervention ran**; the "spread is a free lever" framing was
  rescoped the same day — within the spread arm, spread adds nothing beyond the gap
  (t = 0.27). [report_spread_intervention.md](reports/report_spread_intervention.md).

## Archive

- [docs/archive/STATE_log_archive_2026-07-28.md](archive/STATE_log_archive_2026-07-28.md)
  — jobs table, runs queue, and the full cross-thread log through 2026-07-28.
- [docs/archive/STATE_archive_2026-07.md](archive/STATE_archive_2026-07.md) — the
  earlier archive it points back to.

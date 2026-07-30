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

**Checked live 2026-07-29, and the previous entry was wrong.**

| Lane | Status | Rule |
|---|---|---|
| **Colab** | **Pro subscription, active** ($9.99/mo postpay, last billed Jul 6) but **zero compute units**. That still leaves **T4 GPU and v5e-1 TPU selectable**; H100, A100, L4, G4 and v6e-1 TPU are locked until units are bought or the cycle turns. Verified by connecting: Tesla T4 15 GB, CUDA 13.0, 12 GB RAM, 189 GB disk. | free at this tier, no approval needed; one connection at a time; **Drive mount still needs the user, but a run that clones from the public GitHub repo and writes to /content does not need Drive** |
| Kaggle 2×T4 | weekly GPU quota exhausted; resets Sat 2026-08-01 | free, no approval needed; push needs `--accelerator NvidiaTeslaT4` |
| Modal | ~$75 BlueDot grant + $30/month free tier (resets on the 1st) | pilot-before-spend (~$1) still applies |
| Cerebrium | **never launch** (user directive) | — |

The practical consequence: **GPU work does not have to wait for the Kaggle
reset.** Colab has a usable T4 today.

## Live jobs

| Job | Where | Status |
|---|---|---|
| Value-covariance **phase 1b** (graded 0–9 logprob scoring, four pre-registered gates) | **Colab T4, RUNNING** (relaunched 2026-07-29 ~11:25 PDT) | Notebook `Untitled70.ipynb`, self-contained, no Drive. Generator + judge A `Qwen/Qwen3.5-4B`, judge B `google/gemma-4-E2B-it`, `BATCH_B=2`. Writes `/content/phase1b_gemma.json`. Expect ~2h. |

**The previous attempt died exactly where the pre-flight said it would, for a
second reason nobody was looking at.** The pre-flight correctly identified that
`mistralai/Ministral-3-3B-Instruct-2512` cannot load (`model_type: mistral3`
maps to `None` under `AutoModelForCausalLM`; also FP8, which Turing dequantizes
silently). Setting `JUDGE_B=google/gemma-4-E2B-it` did not fix it: `JUDGE_B` is
a *path* spec, and `resolve_judge_b` only understood local directories, so a hub
id matched nothing, fell through to a hardcoded `JUDGE_B_FALLBACK` of Ministral,
and printed one line about it. The run generated pools for an hour, scored them
with judge A, and died at judge B. The recorded `config.judge_b` said gemma while
the loader used Ministral, which is what made it confusing after the fact.
Fixed in code: an `owner/name` spec is honoured as a hub id, only an unusable
path falls back, and the fallback default is no longer Ministral. **Lesson worth
keeping: a resolver that silently substitutes for an explicit request is worse
than one that raises.**

**Model selection (user directive 2026-07-29: use current models; my picks were
anchored on stale knowledge).** Two launches were stopped before this one. The
first used Qwen3-4B with Phi-3-mini as judge B — a 2024 model. The second used
`mistralai/Ministral-3-3B-Instruct-2512`, which **cannot load at all**: its
config declares `model_type: mistral3`, which maps to `None` under
`AutoModelForCausalLM` and needs `AutoModelForImageTextToText`. It is also 79%
FP8 weights, and on Turing transformers dequantizes silently rather than
erroring — so a logprob-calibration instrument would have run on FP8-precision
weights with nothing in the log. Both confirmed on the Colab transformers, not
inferred.

`experiments/value_covariance/check_judge_models.py` now catches both (it was
tokenizer-only, which is why it cleared Ministral). A class named
`...ForConditionalGeneration` is **not** by itself disqualifying — Qwen3.5 and
Gemma 4 are both registered for causal LM — so the auto mapping has to be looked
up rather than guessed.

Judge B is out-of-family on purpose: a Qwen judge B scored against a Qwen judge A
passes the cross-judge agreement gate on shared bias. Gemma 4 is Apache-2.0 and
**ungated**, unlike Gemma 2 and 3. Its tech report §2.5 states the architecture
bounds activation ranges to fit fp16, which is the T4's exact constraint. Survey
and evidence: [lit_small_model_frontier_2026-07-29.md](reports/lit_small_model_frontier_2026-07-29.md).

**Carried caution:** VERDI (arXiv 2605.11334) reports Qwen3.5-4B logprobs as
anti-calibrated (AUROC 0.373/0.494) — on answer-token confidence, not digit-scale
rating, so not directly our readout, but this whole instrument is logprob-based
and the four gates are what stand between us and that.

The Kaggle copy stays queued for the 08-01 reset as a second, independent run.

## Recent changes

- 2026-07-29: **No Goodhart signature over four rounds** — the judge's score of
  the organism's own candidates and the value those candidates carry rise
  together (divergence +0.0014 [−0.0125, +0.0178]). On OLMo the real value moves
  *faster* than the judge's score of it (−0.0141 [−0.0228, −0.0064], excluding
  zero in the anti-Goodhart direction). So the levelling-off is exhaustion of
  selectable variation, not selection buying proxy score with real value — which
  matches the saturation result from the other side. An estimand error had to be
  fixed first and it inverted the reading: pooling runs pushed up with runs
  pushed down makes the gold slope cancel to ~0, which reads as textbook
  Goodhart and is an artefact.
  [report_proxy_gold_divergence.md](reports/report_proxy_gold_divergence.md).

- 2026-07-29: **A stability criterion for self-training loops, and its first
  measurement — these loops are self-limiting.** The Lande-Kirkpatrick Fisherian
  runaway model maps onto this loop almost exactly, and the quantity it needs is
  the judge-drift coupling `c = dρ/dv`, which a frozen-judge design cannot see
  because it is zero there by construction. It gives a one-line per-round loop
  gain **G = 1 + c·h²·σ** — above 1 runs away, below 1 settles. Measured:
  **G = 0.922 [0.86, 0.98]**, so movement erodes the judge's agreement rather
  than reinforcing it. The mechanical route to that sign (binary scores force
  σ ≤ √(v(1−v)), so nearing a rail drags ρ down by arithmetic) is ruled out —
  controlling for the ceiling barely moves the coupling. Families split: Qwen
  0.820 [0.70, 0.94], OLMo **0.974 [0.90, 1.05]**, on the boundary, and OLMo is
  where the two runaways happened. Where it breaks: the predicted geometric decay
  holds at rounds 2–3 and fails at round 4, where agreement comes back up.
  [report_judge_coupling_stability.md](reports/report_judge_coupling_stability.md).

- 2026-07-28: **The pooled gap decline is an accounting artefact.** Among pools
  that still have spread the gap is flat across four rounds (0.088 → 0.086); the
  whole pooled decline is the share of pools at *exactly* zero spread rising
  1.7% → 11.9%, and the accounting is exact to 1e-12. **Narrowed the same day
  after a figure draft checked where those pools sit: all 17 are at pool mean
  exactly 1.0, in 7 of 59 runs, all from rail-driving conditions, and none ever
  recovers.** So the collapse is binary-scale saturation, not a dynamics
  discovery. What stands: no gradual erosion in runs that have not railed, and
  agreement never falls. Spread does fall ~16% within surviving runs, roughly
  half of it forced by the binary ceiling.
  [report_gap_decline_decomposition.md](reports/report_gap_decline_decomposition.md).

- 2026-07-28: **Phase 1b gains batch calibration before Saturday's launch.**
  Zhou et al. (arXiv 2309.17249) is the named remedy for the yes-saturation that
  sank phase 1, it is free, and it applies within each prompt's pool — the
  comparison set the estimand is defined over. On synthetic saturated
  distributions it recovers within-prompt spread from 0.0001 to 0.1372 while
  preserving candidate ordering, tracks the latent signal within prompt at
  r = 0.997 against 0.762 raw, and returns exactly zero spread for identical
  candidates. Both readings are recorded, so the run reports whether calibration
  mattered instead of that being assumed.
  `experiments/value_covariance/test_batch_calibration.py`; phase-1b smoke test
  still passes.
- 2026-07-28: **The writeup's six-run agreement sentence is falsified by seed
  45** — it amplified (+0.167) with round-2 agreement −0.464, so "remained
  nonnegative in the four that amplified" is wrong. Two earlier reads, one of
  them mine, had the collapse set backwards by using the candidate pool mean
  instead of the measured value. Replacement sentence proposed in the 07-28
  addendum to [writeup_proposed_edits_2026-07-27.md](writeup_proposed_edits_2026-07-27.md).
- 2026-07-28: **Two figure drafts landed**, both of which caught real errors.
  `docs/figures/auto/transmission-triangulation/` (the three-way coefficient
  estimate, showing the censored one as the outlier) found that the long-quoted
  "+0.074 against +0.023" censoring pair mixed aggregations — +0.074 is the
  per-run mean and correct, +0.023 matches nothing. `docs/figures/auto/
  coevolving-judge-phase-plane/` (the six self-judging runs in the value–agreement
  plane) is what prompted the six-run recheck above.

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
  (aborted runs move +0.074/round vs +0.019 for completed ones, ratio 3.9×). Ferbach et al.
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

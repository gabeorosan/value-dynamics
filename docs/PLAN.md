# PLAN — the single current plan (all threads read this one)

**This file is the only authoritative plan.** It is updated in place by the
Lit&planning thread; dated decisions are appended to the log at the bottom.
Every other `plan_*.md` / research-plan document is historical or reference —
see the document index at the end. If this file and any other document
disagree, this file wins. (Protocol: STATE.md = what is happening;
PLAN.md = what we decided to do; reports = what we found.)

*Current as of 2026-07-10 evening. Sprint ends Sunday 2026-07-12.*

## Objective (unchanged from the 07-10 correction)

One clean causal result about how a model's judging preference sets the
direction of self-training, presented as coverage of the judge × generator
matrix across two model families (Qwen3-4B, OLMo-3-7B) and two values (risk,
insecure-code/self-report), with uniform analyses, confounder gates, and
riding probes.

## The matrix and its coverage

| Quadrant | Coverage this sprint |
|---|---|
| Qwen × risk | K1: full 4-judge grid on the mod65 moderate organism; per-round vintages persisted (risk transmission cells become reachable next window) |
| OLMo × risk | K2: 4-judge conservative-inversion grid — the headline causal test |
| Qwen × insecure-code | K3: 4-judge neutral-prompt mini-grid + Colab transmission/carrier/susceptibility/composition cells |
| OLMo × insecure-code | EXPLICITLY CUT (no organism, no validated instrument, likeliest outcome is a null-on-a-null; named as the empty cell in the write-up) |

## Kaggle — Saturday 45 h (scripts built tonight, BATTERY_MODE=inloop)

| # | Run | Design (audit-amended, see 07-10 decision log) | Hours |
|---|---|---|---|
| K1 | Qwen anchor grid | mod65 × {evolving self, frozen round-0 copy, frozen base, random-selection} × 4 seeds × 4 rounds; +1 measure-only seed. Honest counting: the frozen-base baseline is **n=4 independent rollouts**. Primary = paired baseline-adjusted final generated-valid risk (`evolving_self` vs `frozen_base`); four-seed fan/variance is secondary. It establishes a NEW baseline and does not re-score legacy let-go. | ~9 |
| K2 | OLMo conservative inversion | **6 seeds on the confirmatory contrast** (frozen-conservative vs frozen-base) + **3 seeds on the mechanistic controls** (evolving self, random) × 4 rounds. GATED on: (a) completion-only installer + pinned revision + strict-instrument all-gates-passing rung; (b) actual-pool inversion reproduces on at least two seeded, strict-valid fresh pools. Generic advice taste or one lax pool is insufficient. | ~20.5 |
| K3 | Qwen EM neutral-judge grid | insecure-code organism × 4 judge conditions (random arm FIRM) × 3 seeds × 4 rounds; existence framing at n=3; readouts em_freegen + self_report (em_choice floored) | ~6.5 |
| K4 | External-content arms | **DEFERRED — first cut, runs only if K1–K3 finish early.** Preferred form if hours remain (deep-audit §5): a ONE-UPDATE CONTENT IMPULSE — one fixed mod65 checkpoint × one matched small update from {aligned, opposing, format-matched-neutral} rows, 6–8 resampled data seeds, matched examples/tokens/steps, immediate target+off-target deltas (~1–2 h; identifies the directional impulse, does not estimate a fixed point). The four-round version only by explicit choice; either way same organism/harness as K1 and fixed-point/stiffness/noise language stays exploratory. | (0–5) |
| — | Buffer (resumes, retrieval, gate failures) | | ~9 |

Risk-loop balance/validity requirement: every round generates exactly half its
items in each option order; every strict-valid kept answer gets a genuinely
semantics-preserving swapped-order twin. Initial invalidity is logged and
invalid candidates are rejected/replenished before training. Generated-valid
risk and invalidity remain separate; forced p(gamble) is a second, same-item
format channel. A forced order gap >0.10 or factual-EV probability drop >0.10
invalidates the semantic channel; generated invalidity >0.10 blocks a generated
behavior claim.

Judge-mechanism requirement (all K runs): retain raw candidates and all
cross-scores so candidate-level judge loading on the target axis can be
estimated with invalidity/length controls. Kept-minus-pool gap records the
realized training-data shift; it is a manipulation check, not an established
causal mediator. Generic `judgment_taste` stays off-format and secondary.

## Colab — 30 h

| When | Item | Hours |
|---|---|---|
| done (sunk) | judge-transmission broad screen (one-pool carrier candidate; fresh-pool gate still pending); α-scaling diagnostic (limited self-report carry, high-α degeneration) | ~4 |
| Friday | OLMo conservative install: v2 (85% targets) plateaued ~0.5 and is not a valid K2 organism; run clean v3 strict ladder with 100% conservative targets, stop only on 0.25–0.40 + all instrument gates | ~4 |
| Friday | smoke pilots of K1–K4 | ~3 |
| Friday, added | pre-Kaggle screens (audit blockers): judge-inversion screen on actual gamble pools (frozen-conservative vs frozen-base OLMo must rank the same pools differently — gates K2); carrier fresh-pool validation (≥2 new candidate-pool seeds, amp66_12-vs-base gap must reproduce in sign — gates the carrier loop) | ~2 |
| Saturday | EM transmission cells — run in parallel with K2 (explicitly adopted logic: the frozen-base control makes them independently interpretable; the older "gated on Phase 1B" wording is superseded): transmission (standout judge × fresh base gen, 3 seeds), transmission CONTROL (frozen base judge × same fresh gen, 3 seeds), carrier (reverted judge × fresh gen, 3 seeds, gated on the fresh-pool validation), susceptibility (standout judge × reverted gen, 3 seeds), composition (2 x-points — read as CONSTRUCTED-STATE COMPARISONS, not bias-free 1-D field samples: different adapters differ in more than x) | ~8 |
| Sunday | overflow / re-runs; optional risk-vintage transmission mini if K1 vintages landed (deferred BEFORE any confirmatory K2 seed is cut) | ~4 |
| — | reserve | ~5 |

Pre-Kaggle checklist (from the audits; owners in parentheses): fix OLMo installer
completion-only loss + strict instrument + pinned revision, rerun/re-measure if
artifacts predate any requirement (Specs); build K1–K3 with raw candidate
cross-scoring, candidate-level judge loading, SPEC +
primary endpoint + gate logic each (Specs); smoke-measure minutes per
condition-seed-round and RECOMPUTE the K-budget from measurements — the 8/17-min
anchors predate the full riding battery (Specs+Analysis); adapter-persistence
storage preflight (~150 adapter dirs: per-kernel limits, resume, manifest)
(Specs); sync banked Drive JSONs into repo output dirs with hashes — Sunday
analysis reads JSONs, never figure constants or STATE summaries (Analysis).

## Riding in EVERY training cell (non-negotiable)

Battery patch (wishful thinking, introspection, self-recognition,
suggestibility, identity, judgment_taste); steering artifacts; off-target axes;
entropy; paired generated/forced target channels; factual-EV delta; invalidity;
raw per-question/candidate reads; **every-round adapter persistence with
factorization-invariant update logging relative to round zero (merged B·A, not
raw factors or absolute adapter norm)**. `distinct_n` is not required unless it
uses multiple stochastic samples; the one-sample implementation was removed.

## Sunday analysis day (no GPU) — audit-ordered hierarchy

1. Artifact/instrument gate table per cell (provenance, exact training-order
   balance, forced order gap, generated invalidity, factual-EV delta,
   measure-only drift) — certifies everything below.
2. Primary condition contrasts at the rollout-seed level (K2 confirmatory
   contrast first).
3. Candidate-level judge loading on actual pools; kept-minus-pool gaps as the
   realized-data manipulation check. Mediation/cross-lag remains exploratory.
4. Generated vs forced-choice behavior as distinct format channels.
5. Invariant update-geometry recompute on `W_t-W_0`; full merged-update
   Frobenius cosines and leave-one-seed-out directions. Existing leading-left-
   vector SVD alignment is insufficient. Alpha scaling is a limited negative/
   degeneration diagnostic, not a general behavioral causal leg.
6. Transmission/carrier/susceptibility verdicts (existence framing, never rates).
7. Exploratory tier, labeled as such: generic judgment_taste coupling, broad
   off-target batteries, and drift-field/fixed-point language ONLY where the
   design identifies it (composition cells are constructed-state comparisons;
   K4, if it ran, supports trajectory differences, not stiffness/noise).

## Out of the sprint

OLMo × insecure-code (Branch B); new model families (Qwen3.5); DPO (Branch D);
J-lens; regime grid; λ-bottleneck; Lightning top-ups; **Kaggle TPU** —
queue-dead; service parked opportunistic/post-sprint only (see decision log),
per-round persistence keeps every checkpoint re-measurable later.

## Cut order if hours compress

K4 is already deferred (runs only if K1–K3 finish early). Then:
1. Sunday risk-vintage mini → next window. 2. Composition 2→1 x-points.
3. K2 mechanistic-control arms (evolving/random) seeds 3→2.
Never cut: K1; the K2 six-seed confirmatory contrast; K3's random arm;
per-round persistence + invariant logging; Friday pilots + pre-Kaggle screens.

## Decision log

- 07-10 later: DEEP IMPLEMENTATION/ANALYSIS AUDIT ADOPTED
  (`report_current_plan_analysis_deep_audit.md`): K1/K2 ported to strict
  `Final: A/B` parsing with reject/replenish, exact true order mirroring,
  paired generated/forced reads, factual-EV delta, raw persistence, stable RNG,
  pinned revisions, every-round vintages, and update geometry relative to r0.
  K1 fan demoted to secondary; candidate judge loading replaces “selection gap
  is the mediator”; K2 screen upgraded to two strict fresh pools; K3 SPEC added,
  raw free-generation scores persisted, and its geometry corrected. One-pool
  carrier and mod65 figure claims downgraded; alpha/SVD interpretation narrowed.
- 07-10 late: AUDIT ADOPTED (docs/report_final_sprint_plan_audit.md, all
  recommendations): K2 gated on installer fix (completion-only loss) + actual-
  pool judge-inversion screen, and repowered to 6 confirmatory + 3 control
  seeds (~20.5 h) funded by DEFERRING K4; K1 baseline counted honestly (n=4;
  new mod65 baseline, does NOT re-score legacy let-go); kept-set order-balance
  enforcement + preregistered max gap; kept-minus-pool selection gap (cross-
  scored) replaces judgment_taste as the criterion mediator; composition cells
  reframed as constructed-state comparisons; transmission cells explicitly run
  parallel to K2 (frozen-base control makes them independent); carrier loop
  gated on fresh-pool validation; Sunday hierarchy reordered (gates → primary
  contrasts → mediator → channels → geometry → exploratory); pre-Kaggle
  checklist added (throughput re-measurement, storage preflight, JSON sync).
- 07-10 eve: TPU cancelled for sprint (gate 1 queue-dead 30+ min). K1–K4
  BATTERY_MODE=inloop; service parked (only if a session schedules AND gates
  2–3 pass; Sunday+ re-measurement only). K3 random arm survives from buffer.
- 07-10: control-structure audit — K3 random arm FIRM; transmission control
  cell (frozen base judge × fresh gen) REQUIRED; K4 must share K1's
  organism/harness.
- 07-10: TPU service briefly IN after user push-back, then cancelled (above).
- 07-10: unified sprint plan replaced per-thread run lists; OLMo×EM quadrant
  explicitly cut; conservative-inversion chosen over EM-on-OLMo (intervention
  on the mechanism beats second-order replication; instrument/recipe readiness).
- 07-10: corrected research plan (phases 0/1A/1B, branch structure, claim
  downgrades incl. withdrawn LoRA raw-factor geometry) — absorbed here.
- 07-09: no-Modal replan; regime grid retired on the no-saddle result; Qwen
  seeds 16–22 dropped.

## Document index (everything else is NOT the plan)

| Document | Status |
|---|---|
| [`updated_research_plan_2026-07-10.md`](updated_research_plan_2026-07-10.md) | ABSORBED — phase/branch structure + claim downgrades live here now; keep for rationale detail |
| [`plan_final_sprint_unified.md`](plan_final_sprint_unified.md) | ABSORBED — superseded by this file's tables (its §5 TPU history retained there) |
| [`plan_judge_transmission.md`](plan_judge_transmission.md) | REFERENCE — construct/predictions for the transmission cells |
| [`plan_recovered_threads.md`](plan_recovered_threads.md) | REFERENCE — the recovered-threads audit (battery, saddle, psych probes) |
| [`plan_budget_no_modal.md`](plan_budget_no_modal.md) | HISTORICAL (07-09) |
| [`plan_value_dynamics_drivers.md`](plan_value_dynamics_drivers.md) | HISTORICAL (07-08; forces framing still cited by reports) |
| [`two_week_plan.md`](two_week_plan.md), [`next_directions_assessment.md`](next_directions_assessment.md) | HISTORICAL |

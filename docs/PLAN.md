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
| K1 | Qwen anchor grid | mod65 × {evolving self, frozen round-0 copy, frozen base, random-selection} × 4 seeds × 4 rounds; +1 measure-only seed. Honest counting: the frozen-base baseline is **n=4 independent rollouts** (order repetitions are within-rollout measurements, not units). It establishes a NEW order-balanced mod65 baseline; it does NOT re-score the legacy let-go verdict (different starting state) — that needs a let-go arc from K1 vintages later. | ~9 |
| K2 | OLMo conservative inversion | **6 seeds on the confirmatory contrast** (frozen-conservative vs frozen-base) + **3 seeds on the mechanistic controls** (evolving self, random) × 4 rounds. GATED on: (a) installer fixed to completion-only loss (whole-sequence-loss adapters are invalid prerequisites — rerun the ladder if any were built unmasked); (b) the judge-inversion screen on ACTUAL gamble candidate pools — frozen-conservative and frozen-base must rank the same pools in clearly different semantic directions (generic advice-taste headroom is NOT sufficient). | ~20.5 |
| K3 | Qwen EM neutral-judge grid | insecure-code organism × 4 judge conditions (random arm FIRM) × 3 seeds × 4 rounds; existence framing at n=3; readouts em_freegen + self_report (em_choice floored) | ~6.5 |
| K4 | External-content arms | **DEFERRED — first cut, runs only if K1–K3 finish early.** If run: same mod65 organism/harness/seed schedule as K1; confirmatory endpoint = trajectory/final-state difference vs K1's evolving-self arm; fixed-point/stiffness/noise language stays exploratory (3 seeds cannot identify them). | (0–5) |
| — | Buffer (resumes, retrieval, gate failures) | | ~9 |

Kept-set balance requirement (all K runs): randomized candidate order balances
the *field*, not the *kept set* — enforce letter/order balance in the kept rows
(or add an order-swapped equivalent of every kept row), and preregister a max
longitudinal order gap above which a cell's semantic conclusions are invalid,
not merely "exploratory" (mod65 seed 2 hit a 0.50 order gap).

Judge-mediator requirement (all K runs): log the **kept-minus-pool semantic
gap on the actual candidate pool** per judge/item/round, cross-scored by the
fixed base and fixed organism judges even in arms they don't control — this,
not generic advice-pair judgment_taste, is the criterion-channel mediator
(mod65: behavior fans 0.111–0.639 while advice taste sits flat 0.373–0.402).
judgment_taste stays as an off-format secondary readout.

## Colab — 30 h

| When | Item | Hours |
|---|---|---|
| done (sunk) | judge-transmission screen (carrier result: exists, seed-dependent); α-scaling causal test | ~4 |
| Friday | OLMo conservative install + dose ladder (stop at order-balanced risk 0.25–0.40, EV gate, taste headroom) | ~4 |
| Friday | smoke pilots of K1–K4 | ~3 |
| Friday, added | pre-Kaggle screens (audit blockers): judge-inversion screen on actual gamble pools (frozen-conservative vs frozen-base OLMo must rank the same pools differently — gates K2); carrier fresh-pool validation (≥2 new candidate-pool seeds, amp66_12-vs-base gap must reproduce in sign — gates the carrier loop) | ~2 |
| Saturday | EM transmission cells — run in parallel with K2 (explicitly adopted logic: the frozen-base control makes them independently interpretable; the older "gated on Phase 1B" wording is superseded): transmission (standout judge × fresh base gen, 3 seeds), transmission CONTROL (frozen base judge × same fresh gen, 3 seeds), carrier (reverted judge × fresh gen, 3 seeds, gated on the fresh-pool validation), susceptibility (standout judge × reverted gen, 3 seeds), composition (2 x-points — read as CONSTRUCTED-STATE COMPARISONS, not bias-free 1-D field samples: different adapters differ in more than x) | ~8 |
| Sunday | overflow / re-runs; optional risk-vintage transmission mini if K1 vintages landed (deferred BEFORE any confirmatory K2 seed is cut) | ~4 |
| — | reserve | ~5 |

Pre-Kaggle checklist (from the audit; owners in parentheses): fix OLMo installer
completion-only loss + pin immutable model revision, rerun ladder if unmasked
adapters exist (Specs); build K1–K3 with selection-gap cross-scoring, SPEC +
primary endpoint + gate logic each (Specs); smoke-measure minutes per
condition-seed-round and RECOMPUTE the K-budget from measurements — the 8/17-min
anchors predate the full riding battery (Specs+Analysis); adapter-persistence
storage preflight (~150 adapter dirs: per-kernel limits, resume, manifest)
(Specs); sync banked Drive JSONs into repo output dirs with hashes — Sunday
analysis reads JSONs, never figure constants or STATE summaries (Analysis).

## Riding in EVERY training cell (non-negotiable)

Battery patch (wishful thinking, introspection, self-recognition,
suggestibility, identity, judgment_taste); steering artifacts; off-target axes;
entropy + distinct-n; order-balanced coordinate + factual EV gate + invalid
rate; raw per-question reads; **per-round adapter persistence with
factorization-invariant delta logging (merged B·A, not raw factors)**.

## Sunday analysis day (no GPU) — audit-ordered hierarchy

1. Confounder gate table per cell (order gap incl. KEPT-SET gap, EV gate,
   invalid rate, entropy, measure-only drift) — certifies everything below.
2. Primary condition contrasts at the rollout-seed level (K2 confirmatory
   contrast first).
3. Actual candidate kept-minus-pool gaps as the judge mediator (cross-scored).
4. Generated vs forced-choice behavior as distinct format channels.
5. Invariant weight-geometry recompute (un-withdraw or kill the thrash claims);
   CPU SVD/convergence across same-fate endpoints; α-scaling = the causal leg.
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

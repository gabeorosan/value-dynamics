# PLAN — the single current plan (all threads read this one)

**This file is the only authoritative plan.** It is updated in place by the
Lit&planning thread; dated decisions are appended to the log at the bottom.
Every other `plan_*.md` / research-plan document is historical or reference —
see the document index at the end. If this file and any other document
disagree, this file wins. (Protocol: STATE.md = what is happening;
PLAN.md = what we decided to do; reports = what we found.)

*Current as of 2026-07-10 evening. Sprint ends Sunday 2026-07-12.*

## Objective (unchanged from the 07-10 correction)

One clean causal test of whether and how a model's judging preference changes
the direction of self-training, presented as coverage of the judge × generator
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

## Kaggle — Saturday 45 h (BATTERY_MODE=inloop)

**Launch order (deep-audit §5; K2's confirmatory contrast is the sprint's
highest-value result):** (1) K2 confirmatory 6-seed contrast — as soon as its
two gates pass; (2) K1 anchor grid; (3) K2 evolving/random controls; (4) K3;
(5) K4 one-update content impulse if hours remain. If K2's organism gate has
not passed by window start, launch K1 first and slot K2 in on gate-pass — but
never spend K2-confirmatory hours on lower rows.

**Build status:** K1 rebuilt to the strict_final_v2 instrument and
DRY-verified (per-attempt judge score tables, harness self-test, storage
preflight in SPEC); K3 launch-ready; K2 draft written, gated on the organism +
instrument reconciliation. Still pending before the window: GPU smoke of one
K1 seed × one round × two arms, real-minutes budget recompute from that smoke,
the two-pool strict inversion screen, and the organism rung passing ALL gates.

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
| Friday–Sat | OLMo conservative install, **v6 mixed recipe (running)**. History that sets the recipe: v2 (whole-seq) quarantined; letter-only strict targets are rate-INSENSITIVE (~0.5 plateau at 0.85/0.93) then CLIFF (0.18@40 at 1.0) and degrade `Final:` compliance; rationale-bearing targets move the generated channel. The ladders exposed a **format-channel double dissociation** (letter targets → forced single-token channel; rationale targets → generated channel), so v6 alternates letter/rationale rows and the rung verdict now has a SIXTH gate: `gen_in_band_0.15_0.50` — the organism must be moderate on the GENERATED channel (K2's primary endpoint), not just the forced coordinate. Stop only on a rung passing ALL gates. **Sanctioned fallback (07-10 night, if v6 exhausts):** the gate hierarchy is revised with a dated note — generated 0.25–0.40 becomes PRIMARY, forced ≤0.60 secondary — and v5 rung_80 re-verdicts under it as the K2 organism; consistent with "generated is K2's primary endpoint," and the revision must be recorded as a gate change, not silently applied. | ~5 (mostly spent) |
| Friday | smoke pilots of K1–K4 | ~3 |
| Friday, added | pre-Kaggle screens (audit blockers): judge-inversion screen on actual gamble pools (frozen-conservative vs frozen-base OLMo must rank the same pools differently — gates K2); carrier fresh-pool validation (≥2 new candidate-pool seeds, amp66_12-vs-base gap must reproduce in sign — gates the carrier loop) | ~2 |
| Saturday | EM transmission cells — run in parallel with K2 (explicitly adopted logic: the frozen-base control makes them independently interpretable; the older "gated on Phase 1B" wording is superseded): transmission (standout judge × fresh base gen, 3 seeds), transmission CONTROL (frozen base judge × same fresh gen, 3 seeds), carrier (reverted judge × fresh gen, 3 seeds, gated on the fresh-pool validation), susceptibility (standout judge × reverted gen, 3 seeds), composition (2 x-points — read as CONSTRUCTED-STATE COMPARISONS, not bias-free 1-D field samples: different adapters differ in more than x) | ~8 |
| Sunday | overflow / re-runs; optional risk-vintage transmission mini if K1 vintages landed (deferred BEFORE any confirmatory K2 seed is cut) | ~4 |
| — | reserve | ~5 |

Pre-Kaggle checklist status (07-10 night): DONE — installer completion-only +
pinned revision + strict instrument (v6 running); K1–K3 builds with raw
candidate cross-scoring + judge loading + SPECs (strict_final_v2 pass,
DRY-verified); storage preflight (in SPECs); Drive JSON sync with hashes.
REMAINING — GPU smoke (one K1 seed × one round × two arms) + budget recompute
from measured minutes (Specs+Analysis); two-pool strict inversion screen +
organism all-gates rung (Specs/General); carrier fresh-pool validation.

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
6. Transmission/carrier/susceptibility verdicts (existence framing, never
   rates); K3 `em_freegen` analyzed as binomial counts with intervals — rounds
   are not independent observations.
7. Riding-battery specificity, not a fishing expedition: standardize each
   probe's change by its measure-only/item-level variation, compare against the
   random arm, report the target-specificity ratio (|standardized target
   change| / RMS standardized off-target change), BH/FDR within the labeled
   exploratory family, and decline to interpret probes with too few items or
   rail saturation.
8. Exploratory tier, labeled as such: generic judgment_taste coupling,
   mediation/cross-lag decompositions, and drift-field/fixed-point language
   ONLY where the design identifies it (composition cells are constructed-state
   comparisons; the K4 impulse supports directional deltas, not stiffness/noise).

## Out of the sprint

OLMo × insecure-code (Branch B); new model families (Qwen3.5); DPO (Branch D);
J-lens; regime grid; λ-bottleneck; Lightning top-ups; **Kaggle TPU** — gate 1
PASSED (v5e: hardware-viable) but queue-limited, so still out of the sprint;
service parked opportunistic/post-sprint only (see decision log); every-round
persistence keeps all checkpoints re-measurable later.

## Cut order if hours compress

K4 is already deferred (runs only if K1–K3 finish early). Then:
1. Sunday risk-vintage mini → next window. 2. Composition 2→1 x-points.
3. K2 mechanistic-control arms (evolving/random) seeds 3→2.
Never cut: K1; the K2 six-seed confirmatory contrast; K3's random arm;
per-round persistence + invariant logging; Friday pilots + pre-Kaggle screens.

## Decision log

- 07-10 night (Colab lane, unilateral per user directive): OLMo ORGANISM GATE
  REVISED — primary band moves to the GENERATED channel (0.15–0.50 on the
  24-sample read), forced single-token becomes a secondary requiring ≤0.60
  (meaningful shift below the 0.723 native point). Basis: v2–v6 ladders show a
  format-channel double dissociation and a forced-coordinate plateau ~0.55
  under every non-destructive recipe (letter/rationale/mixed, rates .85–.97);
  the 0.25–0.40 forced band is reachable only via the rate-1.0 letter cliff
  that fails the order/format gates, and K2's preregistered primary endpoint is
  generated-valid behavior. Organism under revised gates: v6_mixed_strict
  rung_20 (forced 0.723→0.581 with order gap 0.017, generated 0.62→0.375
  mid-band, invalid 0.000, factual up, taste headroom). Inversion screen still
  gates K2 on the actual-pool contrast.
- 07-10 night: PLAN synced to post-deep-audit reality (this pass). Saturday
  LAUNCH ORDER set per deep-audit §5 (K2 confirmatory > K1 > K2 controls > K3
  > K4 impulse; K1 leads only while K2's gates are unmet). Installer row moved
  to the v6 mixed recipe after the letter-only cliff (0.18@40 at rate 1.0;
  ~0.5 plateau at 0.85/0.93) and the **format-channel double dissociation**
  finding (letter targets move the forced channel, rationale targets the
  generated channel) — rung verdict gains the gen_in_band_0.15_0.50 gate so
  the K2 organism is moderate on its PRIMARY (generated) channel. Checklist
  statuses recorded (K1 strict_final_v2 + K3 ready + JSON sync DONE; GPU
  smoke + budget recompute + two-pool screen + all-gates rung REMAINING).
  TPU gate 1 PASSED (v5e) — decision unchanged (queue-limited), now recorded
  accurately. Sunday hierarchy gains the specificity-ratio/FDR tier and the
  K3 binomial framing.
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

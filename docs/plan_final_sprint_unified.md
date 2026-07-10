> **NOT THE CURRENT PLAN — see [PLAN.md](PLAN.md), the single authoritative plan (status of this doc: listed in PLAN.md's document index).**

# Plan — Unified final sprint (Fri 07-10 → Sun 07-12): the judge × generator matrix on the remaining 30 Colab + 45 Kaggle hours

*Written 2026-07-10 (Lit&planning), at user direction: one systematic plan
replacing the accumulated per-thread run lists. Operationalizes
[`updated_research_plan_2026-07-10.md`](updated_research_plan_2026-07-10.md)
(Phases 0/1A/1B, Branch A) plus the judge-transmission family
([`plan_judge_transmission.md`](plan_judge_transmission.md)) into an hour
budget. Throughput anchors: ~8 min per round-unit (one seed × one round,
battery included) for Qwen3-4B on T4; ~17 min for OLMo-3-7B.*

## 0. What is already banked (don't respend)

- Phase 0 repaired harness: PASSED, both families; OLMo stage-flow screen DONE
  (order_gap 0.72→0.35→0.08 across release stages; risk appears at SFT; judge
  taste near-neutral — a stage-level dissociation, and it sharpens Phase 1B:
  the installed conservative taste will be contrasted against a *weak* native
  prior, not a strong bold one).
- Moderate Qwen organism (mod65): round-0 gates passed (risk 0.361, order_gap
  0.06) — the Phase-1A anchor organism exists.
- Judge-transmission screen: built, judges Drive-verified (reverted = amp55_9,
  amp66_12; amplified = amp55_7; dissociation candidates = amp55_10/11),
  queued on Colab. Its reverted-judge read answers the carrier question with
  zero training.
- α-scaling intervention (the weight-geometry intervention): queued/running.
- Hysteresis/let-go: already produced on BOTH axes (risk arc INTERMEDIATE,
  pending re-scoring against the new baseline; EM collapse-prob complete,
  1/10 strong). Fold into the write-up; do not re-run.
- Entropy/mixing basics: verbatim-vs-fresh sampling and λ-mixing results exist;
  the remaining external-data question is the CONTENT interaction (arms below).

## 1. The target matrix, and which cells this sprint fills

Axes: **judge** (evolving self / frozen round-0 organism copy / frozen base /
random-selection / drifted-standout) × **generator** (moderate organism / fresh
base / reverted or mid-trajectory) × **family** (Qwen3-4B / OLMo-3-7B) ×
**value** (risk / insecure-code+self-report).

| Quadrant | Coverage after this sprint |
|---|---|
| Qwen × risk | FULL 4-judge grid on the moderate organism (Phase 1A), + per-round vintages persisted so drifted/reverted risk cells become reachable (Sunday mini or next window) |
| OLMo × risk | 4-judge conservative-inversion grid (Phase 1B) — the headline causal test |
| Qwen × insecure-code | neutral-judge 3-judge mini-grid + the transmission / carrier / susceptibility / composition cells (judges already verified on Drive) |
| OLMo × insecure-code | **EXPLICITLY CUT** (Branch B) — the one empty quadrant, named as such in the write-up |

Riding along in EVERY training cell (all near-free, most already requested):
battery patch (wishful thinking, introspection, self-recognition,
suggestibility, identity, judgment_taste — the criterion-channel replacement),
steering artifacts, off-target axes, entropy + a distinct-n diversity endpoint,
order-balanced coordinate + factual EV gate + invalid rate (the confounder
gates), raw per-question reads (drift-field v2 noise question), and — 
non-negotiable — **per-round adapter persistence with factorization-invariant
delta logging (norms/cosines on merged B·A products, not raw factors)**, which
is what lets the withdrawn weight-geometry claims be recomputed or killed.

## 2. Kaggle — the Saturday 45 h

| # | Run | Design | Hours |
|---|---|---|---|
| K1 | Phase 1A Qwen anchor grid | mod65 organism × {evolving self, frozen round-0 copy, frozen base, random-selection} × 4 seeds × 4 rounds (64 units). Frozen-base arms double as the **order-balanced fresh-decay baseline** (n=8 arm-equivalents; re-scores the let-go verdict and the legacy decay claims). One extra measure-only seed for battery stationarity. | ~9 |
| K2 | Phase 1B OLMo conservative inversion | conservative organism (installed Friday on Colab) × same 4 judge conditions × 3 seeds × 4 rounds (48 units at OLMo speed). Primary endpoint: judge-condition × round interaction; the frozen-conservative vs frozen-base contrast is the causal claim. | ~14 |
| K3 | Qwen EM neutral-judge mini-grid | insecure-code organism × {evolving self, frozen round-0 copy, frozen base, **random-selection**} × 3 seeds × 4 rounds (48 units), neutral judge prompt (deconfounds the candid-prompt grid). The random arm is FIRM, funded from buffer if the TPU service doesn't free the minutes — the EM axis is where the selection-vs-generic-SFT confound already burned us once (candid-prompt grid). Readouts: em_freegen + self_report (em_choice floored). | ~6.5 |
| K4 | External-content arms | risk self-judge loop × {opposing, aligned, format-matched neutral} × 3 seeds × 4 rounds (36 units). **Comparability requirement: same mod65 organism, same harness, same seed schedule as K1** — K4's no-mixing baseline IS K1's evolving-self arm; if these diverge the arms have no reference. Analysis endpoint: does content shift the fixed point, the stiffness, or the noise. | ~5 |
| — | Buffer (resumes, queue loss, gate failures) | | ~7 |

Total 40 + 5 buffer ≈ 45. Every script smoke-piloted on Colab Friday first.

## 3. Colab — the 30 units/hours

| When | Item | Hours |
|---|---|---|
| DONE (sunk) | judge-transmission screen (carrier result landed: exists, seed-dependent); α-scaling | ~4 |
| Friday | OLMo conservative install + dose ladder (stop at order-balanced risk 0.25–0.40 with EV gate + taste headroom) | ~4 |
| Friday | smoke pilots of K1–K4 (plumbing already validated by basin-letgo + mod65) | ~3 |
| Saturday, parallel | EM judge-transmission loop cells (gated on the screen): transmission (em_dose1000 or amp55_7 judge × fresh base generator, 3 seeds), **transmission CONTROL (frozen BASE judge × the same fresh base generator, 3 seeds — REQUIRED: without it, movement under the drifted judge is indistinguishable from generic loop drift of base Qwen)**, carrier (reverted amp55_9/amp66_12 judge × fresh generator, 3 seeds — only if screen gap ≠ 0), susceptibility (standout judge × reverted generator, 3 seeds), composition (same judge × generators at **2** different x — trimmed from 3 to fund the control cell within the Colab budget; the bias-free drift-field sample) — ~15 cells × 4 rounds, in-loop batteries | ~8 |
| Sunday | risk-vintage transmission mini IF K1 vintages landed and hours remain (else: explicitly next-window); re-runs of any failed Saturday cells | ~5 |
| — | reserve (units burn faster on non-T4 backends) | ~6 |

## 4. Sunday analysis day (no GPU — this is where "cohesive" happens)

1. **Drift-field v2**: refit on order-balanced data; the composition cells give
   the bias-free field samples (x set by construction, not by a noisy prior
   round) that the withdrawn-to-exploratory AR(1) fit lacked.
2. **Weight geometry, invariant recompute**: merged-delta norms/cosines from the
   newly persisted per-round adapters → un-withdraw or kill the thrash result;
   plus the CPU SVD/convergence test across same-fate endpoints; α-scaling
   gives the causal leg.
3. **Criterion channel via judgment_taste**: taste-in-state-vector coupling
   (does taste_t predict Δx_{t+1}?) across K1/K2/K3 — the co-evolution force
   measured, replacing the retired criterion instrument.
4. **Off-target synthesis**: corrigibility/optimism/wishful small-multiples
   across every new cell, on one figure system.
5. **Confounder gate table**: per cell — order gap, EV gate, invalid rate,
   entropy, measure-only drift; one table that certifies every claim.
6. Transmission/carrier/susceptibility verdicts (existence-framing, never rates).

## 5. Things the sprint deliberately does NOT contain (user-confirmed cuts + reminders)

Out: OLMo × insecure-code (Branch B), any new model family (Qwen3.5), DPO
(Branch D), J-lens, regime grid, λ-bottleneck extension, Lightning top-ups.

**Kaggle TPU: OUT of the sprint (final, 2026-07-10 evening) — queue-dead, not
technically dead.** The service was built (experiments/kaggle/
kaggle_tpu_battery_service/, gates 1–3 + serve mode, BATTERY_MODE
inloop|offline contract) but gate 1 sat in the TPU queue 30+ minutes; a
resource that may never schedule cannot hold the Saturday critical path.
Decisions:

- **K1–K4 build with BATTERY_MODE=inloop** (the contract's fallback). Batteries
  stay in the T4 time-box; probe n stays as-is; drift-field v2's noise
  decomposition still works via the raw per-question reads (unchanged).
- **Specs thread stops monitoring the queue** after tonight's script-build
  deadline — attention is a budget too.
- The service is PARKED as opportunistic-and-post-sprint: it only runs if a TPU
  session actually schedules AND gates 2–3 pass, and then only for Sunday-or-
  later re-measurement of persisted checkpoints — never for anything a Saturday
  cell depends on. The per-round adapter persistence it needs is mandated
  regardless, so every checkpoint stays re-measurable whenever TPU (or any
  future backend) materializes.
- The cut-order restorations tied to TPU savings are cancelled — EXCEPT K3's
  random-selection arm, which was already promoted to FIRM on control-structure
  grounds and is funded from the Kaggle buffer (~1.5 h).

Reminders of easy-to-forget items that ARE in (each was lost once already):
the order-balanced decay baseline inside K1; the measure-only seed; the
random-selection arms (selection vs generic-SFT confounder); wishful thinking
et al. riding the battery patch; steering artifacts; raw per-question reads;
invariant delta logging; the screen-before-loops discipline on transmission
cells; pre-registered primary endpoint per script (K1/K2: judge×round
interaction; K3: em_freegen trajectory by judge; K4: fixed-point shift).

## 6. Cut order if hours compress

1. K4 content arms 3→2 (drop format-matched neutral; anatomy bounds it).
2. Composition cells 3 x-points → 2.
3. K3 frozen-base arm (partially known from let-go low arms).
4. Sunday risk-vintage mini (→ next window; vintages are persisted either way).
5. K2 seeds 3→2 on the random-selection arm only.
Never cut: K1, the K2 frozen-conservative vs frozen-base contrast, per-round
persistence + invariant logging, the Friday pilots.
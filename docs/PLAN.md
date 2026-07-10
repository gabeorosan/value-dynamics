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

| # | Run | Design | Hours |
|---|---|---|---|
| K1 | Qwen anchor grid | mod65 × {evolving self, frozen round-0 copy, frozen base, random-selection} × 4 seeds × 4 rounds; frozen-base arms double as the order-balanced fresh-decay baseline (n=8); +1 measure-only seed | ~9 |
| K2 | OLMo conservative inversion | conservative organism (installed Friday) × same 4 judge conditions × 3 seeds × 4 rounds; primary endpoint = judge-condition × round interaction; frozen-conservative vs frozen-base is the causal contrast | ~14 |
| K3 | Qwen EM neutral-judge grid | insecure-code organism × same 4 judge conditions (random arm FIRM, from buffer) × 3 seeds × 4 rounds; readouts em_freegen + self_report (em_choice floored) | ~6.5 |
| K4 | External-content arms | {opposing, aligned, format-matched neutral} × 3 seeds × 4 rounds on the risk self-judge loop; MUST share K1's organism/harness/seed schedule (K1's evolving-self arm is K4's baseline) | ~5 |
| — | Buffer (resumes, queue, gate failures) | | ~10 |

## Colab — 30 h

| When | Item | Hours |
|---|---|---|
| done (sunk) | judge-transmission screen (carrier result: exists, seed-dependent); α-scaling causal test | ~4 |
| Friday | OLMo conservative install + dose ladder (stop at order-balanced risk 0.25–0.40, EV gate, taste headroom) | ~4 |
| Friday | smoke pilots of K1–K4 | ~3 |
| Saturday | EM transmission cells: transmission (standout judge × fresh base gen, 3 seeds), transmission CONTROL (frozen base judge × same fresh gen, 3 seeds — required), carrier (reverted judge × fresh gen, 3 seeds, gated on screen gap ≠ 0), susceptibility (standout judge × reverted gen, 3 seeds), composition (same judge × generators at 2 x-points) | ~8 |
| Sunday | overflow / re-runs; optional risk-vintage transmission mini if K1 vintages landed | ~5 |
| — | reserve | ~6 |

## Riding in EVERY training cell (non-negotiable)

Battery patch (wishful thinking, introspection, self-recognition,
suggestibility, identity, judgment_taste); steering artifacts; off-target axes;
entropy + distinct-n; order-balanced coordinate + factual EV gate + invalid
rate; raw per-question reads; **per-round adapter persistence with
factorization-invariant delta logging (merged B·A, not raw factors)**.

## Sunday analysis day (no GPU)

1. Drift-field v2 (order-balanced refit; composition cells = bias-free field
   samples; σ(x) after binomial subtraction).
2. Invariant weight-geometry recompute (un-withdraw or kill the thrash claims);
   CPU SVD/convergence across same-fate endpoints; α-scaling = the causal leg.
3. judgment_taste coupling (taste_t → Δx_{t+1}) across K1/K2/K3.
4. Off-target synthesis (one figure system across all cells).
5. Confounder gate table per cell (order gap, EV gate, invalid rate, entropy,
   measure-only drift).
6. Transmission/carrier/susceptibility verdicts (existence framing, never rates).

## Out of the sprint

OLMo × insecure-code (Branch B); new model families (Qwen3.5); DPO (Branch D);
J-lens; regime grid; λ-bottleneck; Lightning top-ups; **Kaggle TPU** —
queue-dead; service parked opportunistic/post-sprint only (see decision log),
per-round persistence keeps every checkpoint re-measurable later.

## Cut order if hours compress

1. K4 arms 3→2 (drop format-matched neutral). 2. Composition 2→1 x-points.
3. Sunday risk-vintage mini → next window. 4. K2 random arm seeds 3→2.
Never cut: K1; the K2 frozen-conservative vs frozen-base contrast; K3's random
arm; per-round persistence + invariant logging; Friday pilots.

## Decision log

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

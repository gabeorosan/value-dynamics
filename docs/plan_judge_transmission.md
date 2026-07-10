> **NOT THE CURRENT PLAN — see [PLAN.md](PLAN.md), the single authoritative plan (status of this doc: listed in PLAN.md's document index).**

# Plan — Cross-organism judge-transmission family (Branch-A extension)

*Written 2026-07-10 (Lit&planning), answering the user-directed request filed
2026-07-10 (Figures → Experiment specs + Lit&planning) in STATE.md. This is the
planning-lane framing — construct, per-cell predictions, literature ties, and
epistemic constraints. Script-building and the logging change are the Experiment
specs half of the request. Fold this into
[`updated_research_plan_2026-07-10.md`](updated_research_plan_2026-07-10.md) §6
Branch A when that (currently untracked) file is next committed; it is a Phase-2
extension, contingent on Phase 1B showing judge preference is causal.*

## The construct: is judge taste a transmissible unit, separable from the carrier's behavior?

Every result the program now rests on says **the judge's preference sets the
attractor direction** (the OLMo cross-substrate flip,
[`report_basin_lightning_partial.md`](report_basin_lightning_partial.md)
§Mechanism; the drift-field fit's judge-dependent x\*, held as *exploratory* per
the plan's §1.2 caveat). This family asks the next question: if a judge's *taste*
has drifted, is that drifted taste a **portable quantity** you can move to a
fresh organism through selection alone — and does it survive even when the
organism carrying it has behaviorally reverted? If yes, evaluative preference is
a separable latent that transmits value across organisms independent of the
generator's own disposition. That is a sharper, more mechanistic claim than "the
loop drifts," and it is the judge-side analogue of the self-report/behavior
dissociation the project keeps finding.

Two standing results make this askable cheaply: judge≠generator controls the
Panickssery self-recognition→self-preference confound (any transmission is
taste, not the judge liking its own text), and the checkpoint-probe finding
(**taste drifts with dose while behavior floors**) already hints that taste and
behavior are separable on the judge side.

## Phase 1 — the screen (inference-only, Colab, do first; also a result in itself)

Generate ONE fixed candidate pool from base Qwen, score it with **every**
persisted judge under a **neutral** judge prompt, and read each judge's
kept-vs-pool gap per axis (risk / insecure-code / self-report candor). The gap is
the established attractor-direction predictor, so this pre-qualifies every loop
cell below **without any training**.

Reachable judges on Drive (EM axis reachable now; risk axis gated on logging,
below): EM dose rungs 250–1000, amp55:7 (strong-collapse), amp55:10 / amp55:11
(free-gen 1.0 but choice-floored), amp66 endpoints, low:8 null, low_55 / low_66;
risk persona only if its Drive copy landed (2026-07-09 General→Analysis adapter
request).

**The screen is not just a filter — the reverted-endpoint judges' gap alone
answers the carrier question with zero loops.** If a behaviorally-reverted
organism, used only as a scorer, still shows a nonzero taste gap on the fixed
pool, taste survived behavioral reversion — a publishable dissociation before a
single loop runs. Do this read explicitly and first.

## Phase 2 — the three loop-cell types (3 seeds each, repaired harness; gated on the screen + Phase 1B)

Naming follows the request (no shorthand): **transmission / susceptibility /
carrier**.

**(a) Transmission — standout drifted judge, frozen, × fresh base generator.**
Does a drifted taste transmit the value through selection alone, cross-organism?
Judge = a screen standout (em_dose1000 or amp55:7), frozen; generator = fresh
base Qwen that never had the disposition installed. Prediction (if Phase 1B shows
judge preference causal): the fresh generator moves toward the judge's preferred
pole even though it started neutral. Informative both ways — moves → taste is a
portable steering unit; doesn't → co-evolution or self-preference was
load-bearing and taste alone is insufficient.

**(b) Susceptibility / re-ignition — standout judge × a reverted or mid-trajectory
generator.** Two sub-tests:
- *Erased-vs-masked (weight-space hysteresis).* Prediction: a behaviorally-
  reverted generator re-amplifies **faster** than fresh base under the same judge
  — latent weight-space memory of the disposition (masked, not erased).
  **Caveat, load-bearing:** the mechanistic grounding for this ("reverted
  endpoints retain a shared dominant direction that still carries the
  disposition") rests on the weight-space thrash result and α-scaling, and the
  thrash correlations are currently **withdrawn pending LoRA-factorization-
  invariant recomputation** (plan §1.2, last row). So state this cell's
  *mechanism* as provisional; the *behavioral* prediction (reverted re-amplifies
  faster than base) is testable regardless of whether the weight-space
  explanation survives, and a positive result is itself evidence for latent
  memory independent of the withdrawn metric.
- *Drift-field composition test (arguably the highest-value single cell).* Same
  judge, generators placed at different starting x (different organisms/vintages):
  does the per-round Δx track distance-to-the-judge's-fixed-point? This directly
  tests the drift-field model's central claim (judge sets x\*, dynamics restore
  toward it) by **sampling the field at x values set by construction rather than
  measured from a noisy previous round** — which sidesteps the regression-to-the-
  mean bias that made the original AR(1) fit only "exploratory" (plan §1.2). It
  is the cleanest available way to earn the drift-field claim.

**(c) Carrier — a behaviorally-reverted organism AS judge × fresh generator**
(run if its screen gap is nonzero). Tests whether taste survives behavioral
reversion strongly enough to *steer*, not just to register on a fixed pool.
Grounded in the checkpoint-probe carrier finding. A positive result is the
strongest form of "evaluative preference is a separable latent, decoupled from
the carrier's own behavior."

## Epistemic constraints (encode in every spec and write-up)

- **Standouts are post-hoc-selected extremes** (amp55:7, em_dose1000) →
  existence/mechanism tests, **never rate estimates** (same discipline as the
  collapse-probability framing: amp55:7 is an existence proof, not a probability).
- **Readouts:** EM axis — em_choice is floored, so power lives in **em_freegen +
  self_report**, not em_choice. Risk axis — the **order-balanced** coordinate
  only (the position confound is why the legacy risk coordinate is distrusted).
- **Self-preference control:** judge≠generator throughout, so transmission cannot
  be Panickssery self-recognition.
- **Composition-test bias:** x set by organism choice, not measured from round
  t−1 — this is what makes it bias-free relative to the withdrawn AR(1) fit.

## The logging precondition unblocks three things at once

Persist per-round adapters (at minimum rounds 0/2/4). The legacy basin runs kept
no round-level checkpoints, so **no mid-trajectory or reverted RISK vintages
exist as loadable judges/generators** — without this, the risk half of this
family is unreachable, exactly like the un-re-scorable 23 legacy trajectories.
This single change serves **three** consumers and should therefore be
non-negotiable in the Phase-1 script builds:

1. Branch A copy-judge vintages (rounds 0/2/4) — needs it anyway;
2. the drift-field v2 raw-reads request (2026-07-09 Lit&planning→Specs);
3. this family's risk-axis cells.

## Sequencing

Screen now (Colab, no training) → it pre-qualifies cells and already answers the
carrier question for reverted judges. Loop cells are a Phase-2 Branch-A option,
gated on (screen gap nonzero) AND (Phase 1B shows judge preference causal). EM-axis
cells are reachable immediately from Drive adapters; risk-axis cells wait on the
logging change landing in the Phase-1 scripts. No Modal; Colab for the screen,
Kaggle for the loop cells as a Branch-A selection.
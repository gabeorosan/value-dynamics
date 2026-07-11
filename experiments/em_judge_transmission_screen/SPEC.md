# Cross-organism judge-transmission family — screen + loop-cell registration

Written 2026-07-10, Experiment specs thread, in response to the user-directed
Figures → Specs + Lit&planning request (STATE.md "Requests between threads",
2026-07-10). Covers the Specs half of that request: (1) the **screen** (built,
ready to run now), (2) **registration** of the three loop-cell families
alongside Branch A, (3) the **logging requirement** on the Phase-1 scripts. The
planning-lane framing — construct, per-cell predictions, literature ties,
epistemic constraints — is [`docs/plan_judge_transmission.md`](../../docs/plan_judge_transmission.md)
(Lit&planning); this spec follows its constraints and does not restate them.

## The through-line

A judge's kept-minus-pool gap on an axis is a direct manipulation check for the
data that judge would place into training. Legacy trajectories do **not**
establish it as a general predictive mediator after current state/saturation is
controlled, so the loop outcome remains necessary. The gap is a manipulation
check, not a validated predictor of an attractor direction. The frozen-base
control makes transmission cells independently interpretable, so they are not
gated on a prior binary "judge preference is causal" result. The cells test
trajectory contrasts, steering-force profiles, re-ignition, and curvature;
standout judges are existence/mechanism probes, not rate estimators.

## Part 1 — SCREEN (`colab_judge_transmission_screen.py`, inference-only, ~30 min, run NOW)

Generate one fixed candidate pool for the broad screen (K=6 per prompt across
three axes — risk gambles, insecure-code requests, self-report candor), score
each candidate's axis value ONCE on the frozen base (risk = last-letter p_risk;
code = P(yes) "contains a security vulnerability"; candor = P(yes) "candidly
admits its code may be insecure"), then let each persisted judge re-rank the
same pool under a NEUTRAL judge prompt (no candid/quality steering — the
deconfounder the self-report grid lacked) and read kept-minus-pool per axis.
The `base` judge (adapter disabled) is the null anchor.

**Judges** (LoRA on the shared 4-bit Qwen3-4B base; missing Drive dirs skipped,
paths overridable via `JUDGE_DIRS_ENV`): EM dose rungs 250/500/750/1000, the
amp55/amp66 endpoints, low_8. The **risk persona is excluded** — it is r8 over
an fp16 base, so attaching it to the 4-bit base would silently change effective
weights (colab_em_loop DEVIATION 1); screen it in a paired fp16 run.

**Carrier readout (the zero-loop payoff):** judges flagged `reverted=True`
(behavior floored back to baseline) with a selfreport/insecure_code gap notably
exceeding the base anchor answer the checkpoint-probe carrier question — does
taste survive behavioral reversion? — without training a single loop.

**Gate for the loop cells below:** a cell is worth training only if its judge's
screen gap on the target axis is clearly nonzero (beyond the base anchor), and
then require the sign to reproduce on at least two newly seeded pools before a
carrier loop is authorized. Save all per-candidate judge scores and fit
candidate-level axis loading with invalidity/length controls where applicable.
Standout judges are post-hoc-selected extremes → they license mechanism/
existence tests, never rates.

## Part 2 — LOOP-CELL FAMILIES (registered here; screen + frozen-base control)

Three cell types, 3 seeds each, built on the repaired loop harness. Each reuses
the EM/basin loop mechanics; the only novelty is decoupling the judge organism
from the generator organism. The frozen-base control is required in every
family. EM-axis primary readouts: `em_freegen` + `self_report` (em_choice is
floored → underpowered); risk axis: order-balanced coordinate.

**(a) Transmission** — standout drifted judge (e.g. em_dose_1000 or amp55_7),
frozen, × a FRESH base generator. Pre-registered: if the generator's coordinate
moves toward the judge's screen-gap sign over rounds, a drifted taste transmits
the value through selection alone. Null: fresh generator stays at base.

**(b) Susceptibility / re-ignition** — same standout judge × a REVERTED or
mid-trajectory generator. Two sub-tests:
- *Erased-vs-masked.* Behavioral prediction (testable regardless of mechanism):
  a reverted generator re-amplifies *faster than a base generator* if the trait
  is masked (recoverable) rather than erased. **The weight-space grounding for
  this is PROVISIONAL** — the mechanistic story (reverted endpoints retain a
  shared dominant direction that still carries the disposition) rests on the
  weight-space thrash result, whose correlations are currently **withdrawn
  pending LoRA-factorization-invariant recomputation** (plan §1.2). So state the
  *mechanism* as provisional; the behavioral prediction stands on its own and a
  positive result is itself evidence for latent memory independent of the
  withdrawn metric.
- *Constructed-state comparison.* Same judge, generators placed at different
  starting x by construction (different organisms/vintages): compare per-round
  Δx and re-ignition profiles. This does not identify a fixed point or stiffness,
  because different adapters at the same scalar x can differ in hidden state.

**(c) Carrier-as-judge** — a behaviorally-reverted organism used AS the judge ×
a fresh generator, run only if its screen gap (Part 1) is nonzero. Tests
whether a taste with no behavioral footprint still steers a loop (not just
registers on a fixed pool). Grounded in the checkpoint-probe carrier finding.

## Part 3 — LOGGING REQUIREMENT (Specs, on every Phase-1 script)

**Persist per-round adapters, at minimum rounds 0/2/4.** Branch A needs these
anyway (later-round copies = the weight-space let-go). The legacy basin runs
kept no round-level checkpoints, so no mid-trajectory or reverted RISK vintage
currently exists as a loadable judge/generator — without this logging the risk
half of the family (and drift-field composition on the risk axis) stays
unreachable, exactly like the 23 un-re-scorable legacy trajectories. Concrete:
each Phase-1 loop `save_pretrained(f"{OUT}/vintages/{cell}_{seed}_r{rd}", selected_adapters=[adapter])`
after rounds 0/2/4; these become the generators/judges for cells (b)/(c). This
is a build-time requirement recorded now and applied when the copy-judge / let-go
ensemble scripts are built for the Saturday window.

## Status

- Screen: BUILT + DRY-verified, ready for the Colab lane (Drive-mounted). It
  reuses persisted judges, no training. TWO things the running lane must set
  from ground truth it has and the script cannot guess: (i) the amp/low endpoint
  Drive dir names → `JUDGE_DIRS_ENV='label=/abs/dir,...'`; (ii) which endpoints
  are behaviorally reverted, from their recorded self_report/em_choice
  trajectories → `JUDGE_REVERTED_ENV='label,label'` (defaults encode only
  General's characterization: amp55:10/11 choice-floored = carrier candidates,
  low:8 null = second control not a carrier). risk persona EXCLUDED (r8/fp16-base
  mismatch → paired fp16 run).
- Loop cells: REGISTERED (pre-registered readouts above); run in parallel with
  K2 when fresh-pool validation and the required frozen-base controls are
  available. Results stay in existence/trajectory framing.
- Logging requirement: RECORDED for the Phase-1 scripts; applied at build time.

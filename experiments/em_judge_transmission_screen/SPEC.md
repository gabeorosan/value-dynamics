# Cross-organism judge-transmission family — screen + loop-cell registration

Written 2026-07-10, Experiment specs thread, in response to the user-directed
Figures → Specs + Lit&planning request (STATE.md "Requests between threads",
2026-07-10). Covers all three parts of that request: (1) the **screen** (built,
ready to run now), (2) **registration** of the three loop-cell families
alongside Branch A, (3) the **logging requirement** on the Phase-1 scripts.

## The through-line

A judge's kept-minus-pool gap on an axis is our established predictor of the
attractor direction its selection drives a loop toward (Lightning OLMo/Qwen
mechanism; reproduced on Kaggle in basin-letgo, where the Qwen judge's negative
risk gap preceded the cautious pull). So a *drifted taste* can in principle
transmit a value to a fresh generator through selection alone — that is the
transmission hypothesis. The screen measures every persisted judge's gap
cheaply and pre-qualifies which loop cells are worth training.

## Part 1 — SCREEN (`colab_judge_transmission_screen.py`, inference-only, ~30 min, run NOW)

Generate ONE fixed candidate pool from the base model (K=6 per prompt across
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
screen gap on the target axis is clearly nonzero (beyond the base anchor).
Standout judges are post-hoc-selected extremes → they license mechanism/
existence tests, never rates.

## Part 2 — LOOP-CELL FAMILIES (registered here; gated on the screen + Phase 1B)

Three cell types, 3 seeds each, built on the repaired loop harness. Each reuses
the EM/basin loop mechanics; the only novelty is decoupling the judge organism
from the generator organism. EM-axis primary readouts: `em_freegen` +
`self_report` (em_choice is floored → underpowered); risk axis:
order-balanced coordinate (`risk_order_swap_patch.py`).

**(a) Transmission** — standout drifted judge (e.g. em_dose_1000 or amp55_7),
frozen, × a FRESH base generator. Pre-registered: if the generator's coordinate
moves toward the judge's screen-gap sign over rounds, a drifted taste transmits
the value through selection alone. Null: fresh generator stays at base.

**(b) Susceptibility / re-ignition** — same standout judge × a REVERTED or
mid-trajectory generator. Pre-registered erased-vs-masked test: weight-space
(lit_review_weightspace_thrash) says loop endpoints share a dominant direction
and α-scaling says that direction still carries self-report, so PREDICT a
reverted generator re-amplifies *faster than a base generator* if the trait is
masked (recoverable) rather than erased. Also the drift-field composition test:
same judge, generators seeded at different x — does per-round Δx track
distance-to-the-judge's-fixed-point (the x* from report_basin_drift_field)?

**(c) Carrier-as-judge** — a behaviorally-reverted organism used AS the judge ×
a fresh generator, run only if its screen gap (Part 1) is nonzero. Tests
whether a taste with no behavioral footprint still steers a loop.

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
  reuses persisted judges, no training; verify the amp/low endpoint dir names
  on Drive and pass `JUDGE_DIRS_ENV` if they differ from the guessed layout.
- Loop cells: REGISTERED (pre-registered readouts above); gated on the screen
  results + Phase 1B (judge-preference causality).
- Logging requirement: RECORDED for the Phase-1 scripts; applied at build time.

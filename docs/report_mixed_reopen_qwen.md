# Qwen mixed-reopen: the inertness stall collapses to 0.000 in one injected round — movement reaches the base-supplier floor region

*2026-07-13 ~10:55, general thread. Colab run complete (restarted once
after a network interruption; resume clean). Scored with
scripts/score_mixed_generator.py (qwen mode) against
docs/prereg_mixed_generator.md (Qwen cell; committed before launch).
Raw: experiments/em_selfaware_loop/output/mixed_reopen_qwen.json.
Spread = prereg formula (mean over items of within-item candidate-sr SD).*

## Design

The oracle-reversed low_55_707 endpoint stalled at sr_freegen 0.625 with
zero within-pool spread (hold-by-inertness); hotter sampling (temperature
1.4) did not regenerate spread. This run keeps the oracle selector (keep
the 2 lowest insecurity-admission candidates of 6) and replaces 3 of the 6
candidates per item with RAW BASE-QWEN generations. Seeds 921/922, 4
rounds, temperature 1.0.

## Result — both seeds identical

| round | sr_freegen | pool sr | kept sr | gap | spread | kept-cogen share | sr self / cogen |
|---|---|---|---|---|---|---|---|
| baseline | 0.627 | — | — | — | — | — | — |
| r1 (s921) | **0.000** | 0.346 | 0.083 | −0.263 | 0.313 | 0.83 | 0.64 / 0.06 |
| r2–r4 (s921) | 0.000 | 0.08–0.11 | 0.01–0.02 | −0.06..−0.10 | 0.07 | 0.33→0.08 | 0.02 / 0.12–0.17 |
| r1 (s922) | **0.000** | 0.364 | 0.040 | −0.325 | 0.304 | 0.83 | 0.65 / 0.08 |
| r2–r4 (s922) | 0.000 | 0.06–0.09 | 0.000 | −0.06..−0.09 | 0.08–0.13 | 0.25→0.08 | 0.00 / 0.11–0.15 |

## Prereg verdicts

- **P1 (material restoration): PASS** — round-1 spread 0.313/0.304 where
  the same endpoint self-only had 0/6 supported items (relapse) and 0/6 at
  temperature 1.4; spread stays above 0.05 in every round.
- **P2 (descent resumes below 0.55): PASS, maximally** — sr_freegen
  0.627 → 0.000 after ONE round, flat at 0.000 thereafter, both seeds.

## Mechanism and the unified cross-family statement

Base-Qwen scores near-zero on this axis (its generations don't admit
insecure-code habits: cogen sr 0.06–0.08). Round 1: the oracle keeps 83%
supplier text (gap −0.26/−0.33); ten training steps later the organism's
own candidates score 0.00–0.11 and the free-generation readout is 0.000.
From round 2 the pool is a low-sr mixture and the kept-cogen share decays
to 0.08 — once the organism reaches the supplier's level, its own text
competes equally and the mixture returns.

Combined with OLMo branch m this supports one cross-family pattern:
**selection over an injected pool moves the organism toward the supplier's
scored region**
— mid-scale (~0.5) for OLMo-base on the risk items, hence oracle_mix
endpoints 0.344/0.484; the floor (~0.06) for Qwen-base on the
insecurity-admission items, hence 0.000. Speed scales with the
supplier-organism gap and, here, one round sufficed where the material-
starved states had been immovable for 4+ rounds under every other lever
(own judgment, temperature, time).

Selection-inert language per the audits: the 0.625 state was inert on the
measured sr axis under its own generator; injection changes the GENERATOR
mixture, which is exactly why it works where sampler heat did not.

## Caveats

Existence result: no same-seed self-only twin at temperature 1.0 existed
for these seeds at read time. An optional matched twin (same endpoint,
same seeds 921/922, oracle judge, no injection) is running separately as
`mixed_reopen_twin_selfonly.json`; it is an extra control, not a gate on
the sprint analysis or writeup. Comparators that do exist: the parent
seed-707 run's rounds 3–4 (oracle, temp 1.0, zero support, flat 0.625)
and window_reopen_temp14 (oracle, temp 1.4, seeds 909/910, flat 0.625).
The sr scorer is the same frozen instrument throughout; sr_freegen is a
9-sample read (baseline replicate noise on this endpoint ~0.02). The
pre-registration named seeds 909/910, while the launched cells used
921/922 to avoid collisions with the temperature experiment; this is a
protocol deviation. The raw result also predates the top-level config/hash
contract, so model/source provenance comes from the pinned launcher commit
rather than the JSON itself.

## Budget

Free (Colab). This closes the required sprint inputs; the optional twin may
be incorporated later if it lands before publication.

## Matched twin result (~12:15): injection isolated as the cause

The matched self-only twin (same endpoint copied to low_55_707t, same
seeds 921/922, same oracle judge and temperature, NO injection —
experiments/em_selfaware_loop/output/mixed_reopen_twin_selfonly.json)
landed exactly on its preregistration: within-pool spread 0.000 in every
round (all missing-force), realized gap +0.000, sr_freegen flat at 0.625
across all four rounds in both seeds. Under matched seeds the contrast is:
WITH injection 0.627 → 0.000 in one round; WITHOUT, 0.625 → 0.625
indefinitely. The random streams diverge only at the generation step (the
injection itself), so the collapse is attributable to the changed
generator mixture — the causal version of the claim the final-analysis
audit asked for, at zero marginal cost. The OLMo branch-m cells remain
existence results (their comparators are different-seed).

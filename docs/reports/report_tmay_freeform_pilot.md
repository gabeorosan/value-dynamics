# TMAY free-form self-description — pilot (fcons_s0 pair), scored

**Date:** 2026-07-16 · **Spec:** `experiments/tmay_freeform/SPEC.md` ·
**Generation:** Cerebrium T4, OLMo-3-7B-Instruct 4-bit, the persisted
`fcons_s0` round-0/round-4 vintages + raw base ·
**Grading:** two blind Claude subagents on a shuffled anonymized pack
(`scripts/analysis_tmay_freeform.py` → `experiments/tmay_freeform/output/`)

## The pair

`frozen_cons_r0` seed 0 (cautious-copy judge, static alternative, self-only
pool): behavioral risk value **0.233 → 0.083** over four selection rounds
(−0.15, the tracking threshold exactly). The only endpoint pair on the
Cerebrium volume; the big-move rails/reversals live on Modal/Kaggle and are
requested for phase 2 (STATE, Requests between threads).

## Pilot gates — all pass

Answers coherent and on-topic; numeric answers parse (10/10 per checkpoint);
nonzero per-question sample variance; adapters verifiably applied (all 25
free-form generations differ between checkpoints; the identical numeric
token draws under matched seeds reflect near-identical logits at 1–3 answer
tokens, not a loading failure). Blind grading is highly reliable: two
independent graders, correlation **0.969**, mean |difference| 2.9 points,
zero disagreements > 20. NA rate 46.7% — OLMo-Instruct deflects heavily
("I don't have personal attitudes…"), including 100% NA on TMAY's signature
"we have finetuned you…" question (F5) at every checkpoint — itself a
contrast with TMAY's frontier models, which answer such questions.

## Preregistered readout

The SPEC's committed test: does (endpoint − round-0) free-form
self-description move in the direction of the behavioral move (down)?

| checkpoint | free-form 0–100 (blind, n answers) | numeric self-rating 0–100 |
|---|---|---|
| base | 27.7 (14) | 54.0 |
| round 0 (organism) | 32.4 (14) | 54.0 |
| round 4 (endpoint) | 34.8 (12) | 52.4 |

Behavior fell 0.15; free-form self-description moved **+2.4 (wrong
direction, within noise)** and the numeric self-rating **−1.6 (≈ flat)**.
**The TMAY-transfer prediction is not supported on this pair; the
inert-statement precedent is.** Also notable: the two elicitation formats
disagree in level (free-form ≈ 33 "leans cautious" vs numeric ≈ 54
"balanced"), and the conservative install itself barely registers
(base 27.7 vs organism 32.4).

## Scope — what this pilot does and does not establish

One seed, one condition, a threshold-sized behavior move, 5 samples per
question, NA-heavy elicitation. This is a machinery validation plus one
preliminary null, not a citable dissociation extension. The decisive test is
phase 2 on the ±0.6–0.8 rail/reversal endpoints (Modal volume) and the Qwen
insecure-code loop endpoints (Drive) — both filed as lane requests. No
figure until phase 2 (pilot n would mislead).

## Package

`experiments/tmay_freeform/` (SPEC, generation script, Cerebrium runner,
`output/` with raw generations, blind pack + key, both graders' files,
scores JSON) · `scripts/analysis_tmay_freeform.py` · ledger row (§B) ·
STATE entry + phase-2 lane requests.

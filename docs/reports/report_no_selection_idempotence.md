# Without selection the loop is idempotent; with selection it moves in proportion

**Analysis date** 2026-07-28 · **Script**
`scripts/analysis_no_selection_idempotence.py` · **Result**
`experiments/no_selection_idempotence.json` · **Corpus**
`experiments/spread_util_unified.json` (340 rounds, 74 runs)

## Why this exists

Roe, Sanderson, Nguyen, Huang, Nief, Shrivastava, Tan & Holtzman, *Iterative
Finetuning is Mostly Idempotent* ([arXiv 2605.01130](https://arxiv.org/abs/2605.01130))
seed a model with a persona and train each generation on its predecessor's
outputs. Their finding for supervised finetuning, verbatim: **"traits mostly
decay or remain constant so that further finetuning cycles do nothing."**
Amplification appears only under DPO with continual training, and "vanishes when
models are reinitialized."

That is the closest published neighbour to this project, it uses the same model
family, and read quickly it sounds like a refutation. It is not — their SFT
setting has no selection step, which makes it our *zero-gap condition* rather
than our experiment — but that is a claim to check rather than assert.

Checking it also resolves a loose end. An earlier pass flagged the
random-selector arms as a dissenting slice: they moved at 1.644 times the
measurement-noise floor while near-zero-gap rounds moved below it. If random
selection were the same thing as no selection, that would be movement without
selection, and it would contradict both Roe et al. and our own model.

## Random selection is not zero selection

The flag was wrong, and the reason is visible in one number: **the
random-selector rounds have a mean absolute gap of 0.0564.** A selector that
picks 2 of 6 candidates at random still realises a nonzero differential every
round, by chance, and 0.0564 is not small — the corpus-wide mean absolute gap is
0.0782, and rounds 2 through 4 average about 0.070.

Fitting the movement law to those rounds alone gives a gap coefficient of
**0.984, 95% CI [0.467, 1.452]**, against **0.791 [0.618, 1.012]** for all 340
rounds. Random-selector movement is explained by its own realised gap, at the
same coefficient as everything else. There is no anomaly and no dissent; the
earlier flag is withdrawn.

## Round level: near-zero gap really is idempotent

Observed mean |drift| against a per-row measurement-noise floor —
`sqrt(se_t² + se_next²)·sqrt(2/π)`, the absolute change expected from
re-measuring an unchanged model. Ratios below 1 mean the movement is smaller
than re-measurement noise. Intervals are bootstrapped over rows.

| slice | n | mean \|gap\| | ratio | 95% CI |
|---|---|---|---|---|
| judge = random | 16 | 0.0564 | 1.644 | [1.069, 2.268] |
| \|gap\| ≤ 0.01 | 41 | 0.0003 | **0.574** | [0.334, 0.838] |
| \|gap\| ≤ 0.01, self-only pools | 22 | 0.0000 | **0.533** | [0.246, 0.873] |
| \|gap\| ≥ 0.15 | 51 | 0.2388 | 2.854 | [2.245, 3.562] |

Both near-zero-gap intervals exclude 1. Rounds with no realised selection move
*less* than re-measurement noise, which is what idempotence looks like when the
readout is noisy. The self-only restriction matters because it is the closest
match to Roe et al.'s setting: the model trains purely on its own outputs, with
no external supplier of material.

## Run level: the level Roe et al. actually work at

A loop can be idempotent round by round and still walk somewhere over four
rounds, so the same comparison at the run level, grouping runs by how much
selection their whole trajectory accumulated:

| runs grouped by cumulative \|gap\| | runs | mean cumulative \|gap\| | mean \|endpoint − start\| | ratio | 95% CI |
|---|---|---|---|---|---|
| under 0.10 | 5 | 0.037 | 0.060 | **1.116** | [0.038, 2.533] |
| 0.10 to 0.30 | 36 | 0.209 | 0.243 | 2.809 | [2.069, 3.624] |
| 0.30 and over | 33 | 0.572 | 0.456 | 5.615 | [4.437, 7.030] |

The low-selection group is indistinguishable from noise, and the ratio rises
monotonically with accumulated selection. **The low-selection cell has only five
runs and an interval running from 0.04 to 2.53 — it is consistent with
idempotence and consistent with substantial movement, and it should not be
quoted as a null on its own.** The round-level result is the one carrying the
weight; the run-level table is the shape, not the proof.

## What this settles

**Roe et al. and this program agree, and they are measuring different things.**
Their SFT arm is our zero-gap condition, and both find nothing happens there.
Their DPO arm — where amplification appears under continual training and
disappears on reinitialisation — is the closest thing in the literature to what
we study, because a preference for one's own outputs *is* a selection step.

Two things follow.

1. **Our zero-gap null is externally corroborated**, by a different group, a
   different loop construction, and a different measurement. It was already
   established here on 2026-07-27 (|gap| ≤ 0.01, n = 41, ratio 0.574) and it now
   has independent support.
2. **The reinitialisation contrast is the experiment we have not run.** Roe et
   al. find that amplification needs *continual* training and vanishes when each
   generation starts from a fresh model. Every run in this corpus is continual —
   the adapter is carried forward and never reset. So we cannot say whether our
   response coefficient of about 0.78 is a property of selection or a property
   of continual post-training. A reset-versus-continue arm at matched seed and
   judge would separate them, and it is cheap.

## Scope

One organism family per axis, four rounds, binary-scored value axes, LoRA
adapters carried forward. The near-zero-gap slice is 41 rounds drawn
disproportionately from collapsed pools, since a pool with no spread is the
commonest way to realise no gap — so "no selection" here mostly means "no
material to select on", not "material present, selector indifferent". Those two
are worth separating, and the random-selector arms are the closest thing the
corpus has to the second: material present, selector indifferent in
expectation. They move exactly as their realised gap predicts.

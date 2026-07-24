# Pre-registration: head-to-head mixed-generator selection (no static reference)

*2026-07-13 ~13:15, general thread. Committed before launch.*

## What this fixes

The branch-m / mixed-generator runs scored each candidate against a FIXED
secure/idealized reference answer, then kept the top 2 by that score. That
is not the intended mixed-generator design: it asks "how does each
candidate compare to an ideal", not "which of the two models' generations
does the judge prefer". This run removes the static reference. The judge
compares the organism's own generations DIRECTLY against the base model's
generations (`MIX_JUDGE_ENV=head2head`): each candidate's score is its
mean win-probability across all cross-owner duels, both presentation
orders; keep the top 2.

## Design

- Organism: em750 (the insecure-code dose; sr_freegen baseline ~0.807,
  pools carry real spread — the transmission-with-support dose).
- Pool each item: 3 organism generations + 3 base generations
  (`MIX_GEN_ENV=base`, K=6, TOPM=2).
- Two judge conditions (the organism vs the base model does the choosing):
  - **self-judge** (`JUDGE_MODEL_ENV=self`): the organism judges its own
    text against base's. Seeds 41/42.
  - **base-judge** (`JUDGE_MODEL_ENV=base`): the frozen base judges. Seeds
    43/44.
- 4 rounds, train on the kept winners as usual. Readout: sr_freegen
  trajectory; kept-cogen share (how often the judge picks base's text over
  the organism's); realized kept-minus-pool sr gap.

## Predictions (registered before data)

- **P1 (self-judge, entrench vs erode).** Under self-judging the organism
  chooses between its own insecure-admitting text and base's more-secure
  text with no ideal anchor. If it keeps its own (kept-cogen share < 0.5)
  and sr_freegen holds near 0.807 or rises, self-judging ENTRENCHES the
  installed value. If it prefers base's text (share > 0.5) and sr_freegen
  falls toward base's level, direct competition ERODES it even under the
  organism's own judgment. Direction genuinely open.
- **P2 (base-judge).** The base judge, choosing between the two, should
  prefer its own family's text and pull the organism down; sr_freegen
  falls, kept-cogen share > 0.5. If instead base keeps the organism's
  confident text (as the branch-m realistic judges did), that reproduces
  the "judges prefer confident text" finding without a static reference.
- **P3 (design contrast).** Compare to branch-m invade_self (same family,
  FIXED_REFERENCE, self-judge): does removing the static reference change
  whether the organism's value is retained? A different outcome isolates
  the reference-answer artifact; the same outcome shows the branch-m
  dynamic was not reference-driven.

## Readouts / scoring

sr_freegen from the per-round battery; kept-cogen share and realized sr
gap from rounds_raw (scripts/score_mixed_generator.py qwen mode already
reads cand_owner). Missing-force accounting as usual (a round with pool
spread < 0.05 is missing-force, not resistance). ~2 h/condition on a
Colab T4; free.

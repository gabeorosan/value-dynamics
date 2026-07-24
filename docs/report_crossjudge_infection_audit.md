# Cross-judge agreement as an infection predictor: current evidence audit

*2026-07-14. Script: `scripts/analysis_crossjudge_infection_audit.py`.
Artifact: `experiments/crossjudge_infection_audit.json`. Data: the eight saved
OLMo invasion cells (four reference-anchored, four duel-format).*

## Question

Does a generator become infectious when it reaches a region where the source
judge's criteria and a recipient judge's criteria rank the same risky responses
highly? This is distinct from either a globally risk-preferring judge or a
generator that merely emits more risky candidates.

## What the current runs support

They support the *possibility* of local, state-dependent alignment. Within the
two frozen-base OLMo runaways, the same fixed judge's candidate-level
score-risk correlation becomes positive during ascent. But a settled run also
develops strong late alignment, so this is not a runaway signature.

The existing invasion cells do **not** establish the cross-judge prediction.
The naive eight-cell calculation is misleading:

| cells | source-recipient agreement vs round-1 movement | vs supplier kept share |
|---|---:|---:|
| all 8 pooled | +0.83 | +0.98 |
| 4 duel cells only | −0.50 | +0.91 |
| 4 reference cells only | +0.15 | −0.06 |

The pooled result is driven by judging format. All reference cells have high
agreement and winner-take-all supplier keeps; duel cells use a different score
construction and have lower apparent agreement and weaker supplier keeps.
Within the comparable duel cells, agreement points the wrong way for movement,
with only four cells. Reference/base cells are partly tautological because the
source and recipient are the same base judge. Risk-conditional partial
correlations do not repair these design problems (see the JSON artifact).

## Verdict

**Interesting hypothesis; not a current result.** The defensible writeup
sentence is:

> A fixed judge can exert changing directional pressure because score-value
> alignment is local to the generator's current candidate distribution. This
> alignment was positive during both observed OLMo runaways. Whether agreement
> between source and recipient judges predicts transmission remains open.

Do not say that judge agreement predicts infectiousness from the present runs.

## Clean test

Hold candidate pool and judging format fixed. Have the source judge and several
independent recipient judges score the same mixed candidates. Measure ranking
agreement after conditioning on candidate risk (and ideally length/owner), or
pairwise/top-k agreement on risk-matched source-versus-host candidates. Then
test whether judge-pair agreement predicts supplier kept share and one-round
host movement. The independent unit is the source-recipient judge pair, not the
number of candidates, so the current two or three effective judge types are not
enough for a strong predictor claim.

The proposed ~$2 content-only rail run tests a different, narrower question:
whether loop-selected supplier text acquired a preferred style beyond risky
content. It should remain parked unless that style-exploitation claim is kept.
It is not the best test of cross-judge infectiousness.

## Implemented follow-up

The fixed-pool mechanism check is now implemented in
`experiments/crossjudge_rescoring/`. It freezes the four round-1 branch-h duel
invasion cells (48 item pools, 288 candidates) and rescores them in one direct
duel format with the native base judge plus available v6/v8/v10 OLMo judge
adapters. The launcher verifies the v10 adapter hashes and fresh-score
reproduction, and reports raw and risk/length-residual agreement, top-2
overlap, and counterfactual supplier keeps.

It runs inference-only on a fresh Colab after the current dose ladder. Its
interpretation remains deliberately narrower than the hypothesis: only base
and v10/rung20 have observed movement, so additional judge checkpoints extend
the counterfactual uptake curve but do not validate movement prediction.

# Agreement does not persist, and a co-evolving judge is not clearly the reason

**Analysis date** 2026-07-28 · **Script** `scripts/analysis_agreement_drift.py`
· **Result** `experiments/agreement_drift.json` · **Corpus**
`experiments/spread_util_unified.json` (70 runs with at least two scored rounds)

## What this was asking

The endpoint model freezes round-one agreement and spread and iterates. Its
documented weak point is that agreement is not really constant: a judge's
agreement depends on the candidate distribution in front of it, and training
changes that distribution. When the judge is the organism itself, there is a
second channel — the judge's own preferences move too.

The writeup raises this on the strength of six duel self-judging runs where
agreement turned negative in the two that collapsed. Six runs cannot settle it,
so this asks the same question of the whole committed corpus, where the contrast
exists in a matched form: Qwen organisms on self-only pools with
reference-anchored scoring, judged either by **self** (retrained each round) or
by a **frozen copy** of that same organism. Those two differ in exactly one
thing — whether the judge is updated.

## Agreement by judge

Per run: `rho_1` is round-one agreement, `|drift|` is |last − first|, `sd` is the
standard deviation across the run's rounds, `flips` counts runs where agreement
changed sign at least once.

| judge | runs | mean rho_1 | mean \|drift\| | mean sd | runs with a sign flip |
|---|---|---|---|---|---|
| base (frozen) | 22 | 0.084 | 0.325 | 0.214 | 15 |
| cautious copy (frozen) | 8 | −0.005 | 0.238 | 0.125 | 4 |
| frozen copy (frozen) | 4 | 0.059 | 0.080 | 0.061 | 2 |
| self (co-evolving) | 16 | 0.258 | 0.463 | 0.248 | 5 |
| schedule (swapped by design) | 9 | −0.130 | 0.258 | 0.255 | 8 |
| score oracle | 11 | −0.727 | 0.091 | 0.052 | 0 |

**Score-oracle runs are excluded from every contrast below**, and this matters
more than it sounds. An oracle's agreement is ±1 with the value axis by
construction, not by taste, so it cannot drift — mean |drift| 0.091, no sign
flips in eleven runs. Leaving them in the frozen arm makes freezing look
stabilising for a reason that has nothing to do with freezing. Judge-swap runs
are excluded because they are neither frozen nor co-evolving.

## Result 1 — co-evolving judges drift more, in a comparison that is confounded

| metric | comparison | evolving | frozen | difference | permutation p |
|---|---|---|---|---|---|
| \|drift\| | all runs, oracles and swaps excluded (16 vs 34) | 0.463 | 0.275 | +0.187 | 0.018 |
| \|drift\| | Qwen self-only reference, matched (4 vs 10) | 0.342 | 0.180 | +0.162 | 0.265 |
| sd | all runs (16 vs 34) | 0.248 | 0.175 | +0.073 | 0.067 |
| sd | matched (4 vs 10) | 0.219 | 0.160 | +0.059 | 0.524 |
| rho_1 | all runs (16 vs 34) | 0.258 | 0.060 | +0.197 | 0.034 |
| rho_1 | matched (4 vs 10) | 0.059 | −0.002 | +0.061 | 0.601 |

The pooled comparison says co-evolving judges drift about 68% further over a run
(0.463 against 0.275). But the sixteen evolving-judge runs are spread across
organisms, pool compositions and scoring formats, so that difference is not
attributable to co-evolution alone.

**The matched ablation — the one that would attribute it — cannot resolve the
effect.** With four evolving runs against ten frozen ones, the minimum
detectable difference at 80% power is **0.378**, and the observed difference is
0.162. Reaching 80% power on an effect that size needs roughly **52 seeds per
arm**. The matched cell is consistent with the pooled effect and consistent with
nothing; it does not distinguish them. This is the same shape as the n=2 monotone
claim that had to be withdrawn on 2026-07-27, and it is being recorded as
underpowered rather than as a null.

The one comparison that is clean-ish is `rho_1`: self-judges start at agreement
0.258 against 0.060 for frozen judges (p = 0.034 pooled). A model agrees with its
own preferences more than a frozen or foreign judge does, before any drift
happens. That is self-preference, not co-evolution, and it is a level effect
rather than a dynamics one.

## Result 2 — round-one agreement does not persist for any real judge

`corr(rho_1, rho_t)` across runs, by horizon:

| | round 2 | round 3 | round 4 |
|---|---|---|---|
| co-evolving judge (n = 16) | +0.813 | +0.606 | −0.084 |
| frozen judge, oracles excluded (n = 34 / 33) | +0.354 | +0.117 | +0.130 |

The difference between the two rows is not resolvable: bootstrapped over runs,
the Fisher-z difference is +0.584 [−0.072, +1.214] at round 3 and −0.215
[−0.902, +0.448] at round 4. Both intervals contain zero, and they point in
opposite directions. **There is no evidence here that co-evolution makes
round-one agreement decay faster** — at rounds 2 and 3 the evolving-judge runs
are, if anything, the more predictable ones.

What the table does show is the level, and the level is low. For a frozen judge
that is not an oracle, round-one agreement explains about 13% of the variance in
round-two agreement (r = 0.354) and essentially none from round three onward.
Agreement is close to non-persistent regardless of whether the judge evolves.

**Methodological note worth carrying.** Including score-oracle runs in the frozen
arm changes this row to +0.848, +0.746, +0.733 — the impression that agreement is
a fairly persistent quantity in this corpus is almost entirely carried by runs
whose agreement is pinned by construction. Any future statement about agreement
persistence has to say whether oracles are in the sample.

## The puzzle this leaves

The endpoint model freezes round-one agreement and forecasts four-round
endpoints at MAE 0.118. It does that while freezing a quantity that, among real
judges, has essentially no correlation with its own value two rounds later. The
forecast is not working because agreement persists. The likely reason is the one
the writeup already gives for a different purpose — selection moves a run mostly
in its first rounds and then levels off — so the forecast only needs early
agreement to be right. That is a testable claim rather than a story: it predicts
that replacing frozen round-one agreement with the *realised* per-round agreement
should improve four-round endpoint error only slightly. The predictor bake-off
machinery in `scripts/analysis_selection_response_predictor.py` can answer it on
committed data.

## What would settle the co-evolution question

The matched design already exists and is a one-knob change to a launcher:
Qwen organism, self-only pool, reference-anchored scoring, judge = self versus
judge = frozen copy of the same adapter. The corpus has four seeds per arm. At
the observed effect size it needs on the order of fifty per arm, which is not
affordable; at 20 seeds per arm the design detects a difference of about 0.24 in
|drift|, which is larger than what was observed but smaller than the pooled
estimate. That is the honest bracket to design against, and it argues for
measuring agreement more precisely per round rather than for adding seeds —
halving the per-round agreement measurement error buys more than doubling the
seed count.

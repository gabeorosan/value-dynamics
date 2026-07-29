# Caption — transmission-triangulation.svg

**The transmission coefficient of the self-training loop, estimated three ways: the
odd one out is the censored estimate, not the one from a different corpus.** The
transmission coefficient is how much of one round's selection differential shows up
in the trained model's measured value — operationally, the coefficient on `gap` when
each round's `drift` is regressed on `supply` and `gap`, where `drift` = measured
value after the round minus measured value before, `supply` = candidate-pool mean
minus measured value before, and `gap` = mean value of the answers the judge kept
minus the mean value of the pool it chose from; the measured value is the share of
held-out probe answers falling on the tracked value axis (for these runs, the share
of gamble answers ending on the risky option). Fitted on the unified corpus (340
rounds from 74 runs), where only 4 of 74 runs stop short of the standard four-round
horizon, the coefficient is **0.809** after the measurement-error correction and
**0.791** before it (run-clustered bootstrap 95% interval [0.610, 1.004], 2000
draws — the correction subtracts each round's own recorded measurement variance from
`var(supply)`, because `supply` and `drift` share the error in the pre-round value
with the same sign). The randomised instrument — at round 1 both arms of a
spread-intervention pair start from the identical cached adapter and draw from one
shared candidate pool, so the concentrated-versus-spread arrangement is an assigned
encouragement and nothing downstream can have censored it — gives a Wald ratio of
**0.754**, 95% CI [0.621, 0.984], over 36 matched round-1 pairs; that lane alone is
quoted from `docs/ANALYSIS_LEDGER.md` section B rather than recomputed, because no
result JSON holds it, and the generator aborts if the ledger stops carrying those
figures verbatim. The same regression run on the spread-intervention corpus (414
rounds from 126 runs) reads **0.450** corrected, **0.486** uncorrected (bootstrap 95%
interval [0.419, 0.567], 4000 draws) — 0.304 below the instrument, 40% of it missing.
What separates that lane from the other two is not the corpus but the censoring: 28 of
its 126 runs (14 paired runs, both arms) stop on a pool-matching rule whose recorded
reason is quoted verbatim in the figure, and those runs move **+0.074** per round
against **+0.019** for the 98 that finish (each run's mean per-round change in
measured value, averaged over runs, on exactly the 414 rounds the 0.450 is fitted on),
so the rule removes the fastest movers. The unified corpus shows the same asymmetry
where it barely bites: its 4 short runs give a round-1 response slope of 1.550 across
their 8 round-1 records against 0.721 for the 70 records from runs that complete. The
abort rule is a sensible pairing constraint — it stops a paired run once the two arms
can no longer be offered candidate pools with matching means — and its statistical
consequence only surfaced later. Neither corrected point has a bootstrap interval in
its result file, so none is drawn on them; the intervals shown belong to the hollow
grey uncorrected fits, and the figure says so rather than implying precision that was
never computed.

## Source data

- `experiments/response_saturation.json` — unified corpus lane: `corpus`,
  `measurement_error_correction.all` (naive and corrected `gap`),
  `panels.all.M0_linear.ci.gap` (run-clustered bootstrap interval),
  `survivorship` (short-run versus completer round-1 slopes), `settings`.
  Produced by `scripts/analysis_response_saturation.py`.
- `experiments/spread_corpus_saturation.json` — spread-corpus lane: `n_rows`,
  `n_runs`, `pooled.slope_with_supply` and its bootstrap interval,
  `pooled.measurement_error_correction`. Produced by
  `scripts/analysis_spread_corpus_saturation.py`.
- `experiments/spread_intervention/output*/*.json` (11 files) — the abort split and
  the verbatim stop reason, recomputed by this figure's generator using the same row
  rule as `scripts/analysis_spread_corpus_saturation.py` (each file-name/group/arm is
  one run), which reproduces that corpus's 414 rounds and 126 runs exactly.
- `docs/ANALYSIS_LEDGER.md` section B, row beginning "THE TRANSMISSION COEFFICIENT IS
  CAUSALLY" — the instrumental-variables lane (0.754, 95% CI [0.621, 0.984], SE 0.094,
  first stage +0.1875 with F = 35.1, 36 matched round-1 pairs). Not in any result JSON.
- Background: `docs/reports/report_response_saturation.md`.

## Numbers that moved under recomputation

The completed-run movement figure is **+0.019**, not the +0.023 quoted in the ledger
row and the report. Recomputing on exactly the 414-round / 126-run corpus the 0.450 is
fitted on gives aborted +0.0743 (28 runs, 62 rounds) versus completed +0.0194 (98 runs,
352 rounds); the +0.074 side reproduces exactly. The +0.023 appears to come from an
earlier subset — deduplicating the byte-identical re-runs and dropping the oracle
positive control gives completed +0.0236 — so the direction and the roughly four-fold
ratio are unaffected, but the pair as usually quoted is not from one recipe. Everything
plotted here uses the single stated recipe.

## Reading rules applied

Colour carries one distinction only — blue for the two estimates with no
outcome-dependent censoring, red for the censored one — and every lane is identified by
in-figure condition lines naming its corpus, its identification strategy and its
censoring, so nothing depends on telling hues apart. The two blue lanes are further
separated by mark shape (filled circle for a regression estimate, diamond for the
instrument). Grey is used only for recessive material: axis, uncorrected companion
fits, and notes. The horizontal scale is truncated at 0.30 and marked as such.

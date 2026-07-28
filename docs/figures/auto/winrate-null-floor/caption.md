# winrate-null-floor

**The forced-choice value instrument was reading presentation order, not value.**
Each blue dot is one value axis's *mean within-prompt standard deviation of the
forced-choice win rate*: within one prompt, take the eight candidate answers' win
rates on that axis, take their standard deviation across candidates, and average
that over the 30 prompts — the exact quantity the phase-1 discrimination gate
tested (recomputed here from `raw_scores`, pool set A, and asserted against the
kernel's own summary to 2e-5). The red band is what that same accounting produces
under a judge that cannot see value at all: 4,000 simulated pools in which the
per-call read depends only on which candidate is shown first, calibrated to
reproduce each judge's observed order gap (mean |p(i shown first) + p(j shown
first) − 1| over judged pairs), drawn as the null's own 95% interval for its mean
over 30 prompts, so a dot inside the band is indistinguishable from position-only
judging. **Judge A (Qwen3-4B)**, whose scores this run certified as usable, spans
0.109 to 0.167 against a null interval of 0.147 to 0.177; risk tolerance (0.167)
and deference to the asker (0.162) edge past the null's point value of 0.161 by
0.006 and 0.001, and neither clears its 95th percentile of 0.176. Only the
saturating position-Bernoulli family reaches judge A's order gap of 0.609 at all
(fitted first-position pick rate 0.742) — the soft-lean and symmetric-Beta
families top out near 0.50 — so judge A is a *confident* judge of position rather
than a noisy judge of value. **Judge B (Gemma-2-2b-it)** spans 0.041 to 0.066,
below both families that reach its 0.238 gap (floors 0.076 and 0.088), so its null
is a range rather than a point; both panels share one horizontal scale, which is
why judge B's whole world sits crushed against the left. The two dashed verticals
are the gates: this run was certified `USABLE` by `min within-prompt SD ≥ 0.05`,
which tests against a floor of essentially zero, and the order-flip floor added to
`experiments/value_covariance/script.py` afterwards, 0.115 for judge A, which
cleared five of judge A's six axes individually and sat 1.4x below the simulated
0.161. On 2026-07-28 that interim floor was itself replaced: `script.py` now runs this
simulated value-blind null, calibrated to each run's own order gap.

**Source data.** `experiments/winrate_null_floor.json` (value-blind null, written
by `scripts/sim_winrate_null_floor.py`) and
`experiments/value_covariance/output/value_covariance_phase1.json` (observed
scores; the figure recomputes the per-axis spreads from its `raw_scores` block
rather than reading its `instrument_check` summary). Corroborating recomputation
from raw scores: `experiments/value_covariance_phase1_analysis.json`
(`scripts/analyze_value_covariance_phase1.py`). Ledger row: the value-covariance
phase-1 entry in `docs/ANALYSIS_LEDGER.md`, second pass 2026-07-28, items (A)–(C).

**One caveat on the shipped verdict.** The phase-1 JSON's `instrument_check` block
has no `null_floor_from_order_flipping` key and no `exceeds_null_floor` key — the
0.115 floor was added to `script.py` in the later correction commit, so what
actually stamped this run `USABLE` was the `≥ 0.05` rule alone. Applied after the
fact on the minimum-axis rule the run implements, the 0.115 floor would have
*failed* judge A (worst axis 0.109), even though it clears five of the six axes
individually. The figure states both facts rather than the shorter claim that
0.115 certified the run.

Regenerate with `python3 winrate-null-floor.py` from this directory (stdlib only).

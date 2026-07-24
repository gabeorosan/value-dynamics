# Proposed writeup edits — before and after

Date: 2026-07-24. From the research-vision thread.

**Nothing in `docs/writeup_value_dynamics_sprint.md` has been edited.** This file is
the proposal only. Every change below is optional and independent of the others.

Source of the changes: `report_spread_is_not_a_free_variable.md`, which found that on
a binary-scored value axis the spread of a round's candidates is largely determined by
that round's pool mean. A single fitted coefficient of 0.813 against the arithmetic
ceiling √(q(1−q)) accounts for **85.9%** of the variance in measured spread across the
280 binary-scored rounds; letting every 0.1-wide bin of pool mean have its own free
mean raises that only to 87.6–89.2%. The coefficient is stable across both model
families and all pool compositions (Qwen 0.883, OLMo 0.784, self-only 0.810,
base-mixed 0.820, peer-mixed 0.835).

## Withdrawn before you read it

Earlier today I flagged the sentence "Before selection, the model forecasts the
selector gap as candidate spread σ times judge agreement ρ" as overclaiming, on the
grounds that the factorization is a within-round identity. **That flag was wrong and
I have withdrawn it.** `experiments/selection_response_predictor.json` had already
audited exactly this and its conclusion is correct: agreement is a *pre-selection
proxy* for the realized selection intensity, which is what the words "Before
selection" are carrying, and the file's `scale_audit` had already rejected the
"slope ≈ 1 is design-derived" argument — on the project's realized finite-pool SD
convention the design-derived ratio is 1.0997, not the observed 0.958, so the
observed slope sits below the design value rather than being forced to it. A further
diagnostic in the same file shows the realized-intensity construction fits *worse*
(R² 0.650) than the agreement-times-spread proxy (R² 0.810), which an identity would
not do.

**So no change is proposed to lines 101–108.** The one item that survives from that
review is a records-hygiene point unrelated to the writeup text: the prior
population-genetics analysis reported "n=175" for this fit, which was an undocumented
triple filter; the unfiltered n is 290 and fits better. Don't let 175 propagate.

---

## Edit 1 — "What I measure", after the state-variables figure

**Status: recommended.** This is the main one. As written, the sentence presents two
independent measured quantities; on these axes they are not independent.

### Before

> Two quantities are measured each round, spread and agreement, and together
> they forecast the selector gap. Spread and agreement are measured within
> each prompt's pool and averaged over the round's prompts.

### After

> Two quantities are measured each round, spread and agreement, and together
> they forecast the selector gap. Spread and agreement are measured within
> each prompt's pool and averaged over the round's prompts.
>
> On a binary-scored axis the two are not independent. Because each candidate
> scores 0 or 1, the spread available to a round is capped by its own pool mean
> *q* at √(*q*(1−*q*)), and a single coefficient of 0.813 against that ceiling
> accounts for 85.9% of the variance in measured spread. Agreement is the
> quantity that varies freely here; spread largely follows the value.

---

## Edit 2 — end of "each round, the value moves to what the judge keeps"

**Status: recommended.** The clipping step is currently unexplained, and it is
standing in for a known and specific mis-specification. Saying so costs two sentences
and pre-empts the question.

### Before

> For endpoints, the model repeats this update from the round-one candidate mean,
> holding spread, agreement, and pool composition fixed and clipping each step to
> the 0-to-1 value scale. Each predicted candidate mean becomes the next predicted
> value.

### After

> For endpoints, the model repeats this update from the round-one candidate mean,
> holding spread, agreement, and pool composition fixed and clipping each step to
> the 0-to-1 value scale. Each predicted candidate mean becomes the next predicted
> value.
>
> Holding spread fixed is a simplification in a known direction: since spread is
> bounded by √(*q*(1−*q*)), it has to shrink as a run approaches either end of the
> scale, and the clipping step stands in for that. Letting spread follow the value
> instead removes the need to clip but does not forecast better in a matched
> comparison, so the simpler frozen form is kept.

*Note on sourcing:* the matched comparison is in
`report_spread_is_not_a_free_variable.md`. Its absolute endpoint error (0.213) comes
from a reconstruction of the recurrence with a different run grouping and is **not**
comparable to the writeup's 0.118 — please don't quote the number here. Only the
"does not forecast better" direction transfers.

---

## Edit 3 — Findings list, item 3, first bullet

**Status: recommended.** Small wording change; the current phrasing describes an
intervention that was not available.

### Before

> - Restoring spread to a collapsed candidate pool eroded a previously
>   stuck value.

### After

> - Adding an outside source of candidates to a collapsed pool eroded a
>   previously stuck value, by moving the pool mean off the end of the scale
>   and so restoring spread.

---

## Edit 4 — "Steering trajectories with interventions", opening

**Status: recommended.** Same point as Edit 3, and it explains why the self-only arms
could not be rescued, which is otherwise a loose end.

### Before

> Adding base-model answers to a collapsed pool restores spread, allowing
> the agreement of the judge to pull a value that was previously stuck.
> Swapping the base-model judge for the min-risk oracle (making agreement
> −1) reverses a run that had climbed near the top of the value scale.

### After

> Adding base-model answers to a collapsed pool moves the pool mean away from
> the end of the scale, which restores spread and lets the judge's agreement
> pull a value that was previously stuck. Within a pool the organism supplies
> on its own there is no way to raise spread at a fixed value, which is why an
> outside source of candidates is the lever that works.
> Swapping the base-model judge for the min-risk oracle (making agreement
> −1) reverses a run that had climbed near the top of the value scale.

---

## Edit 5 — "Limitations and future directions", after the behavioral-scope paragraph

**Status: optional.** Adds a limitation you don't currently state, and it sets up the
multi-axis direction. Skip it if the section is already at the length you want.

### Before

*(no existing text — this would be a new paragraph inserted after the paragraph
beginning "The behavioral scope of this post is limited to risk preference and
insecure-code self-description.")*

### After

> Both axes here score each answer 0 or 1, which ties the spread of a round's
> candidates to its mean and leaves agreement as the only freely varying part of
> the state. Graded value scores would let the two move independently. Scoring
> each candidate on several value axes at once would do more: the selection
> differential becomes a vector and the variation becomes a covariance, which
> would let the same measurements predict whether selecting on one value moves
> the others.

---

## Summary

| Edit | Where | Status | Why |
|---|---|---|---|
| 1 | "What I measure", after the state-variables figure | Recommended | Spread and agreement are not independent on binary axes |
| 2 | End of the one-round-rule section | Recommended | Explains the unexplained clipping step |
| 3 | Findings item 3, first bullet | Recommended | The intervention was an outside candidate source, not added variance |
| 4 | Interventions section, opening | Recommended | Same, plus why self-only pools could not be rescued |
| 5 | Limitations | Optional | States the binary-scoring limitation; sets up multi-axis work |
| — | Lines 101–108, the ρσ factorization | **No change — flag withdrawn** | The repo had already audited this and the framing is correct |

No figure needs to change. No existing number in the writeup changes.

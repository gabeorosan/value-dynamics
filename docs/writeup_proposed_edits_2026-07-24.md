# Proposed writeup edits — before and after

Date: 2026-07-24, revised the same day. From the research-vision thread.

**Nothing in `docs/writeup_value_dynamics_sprint.md` has been edited.** This file is
the proposal only.

## What changed since the first version of this file

The first version proposed four hedging edits, because spread looked like it might be
bookkeeping on the pool mean rather than a lever in its own right. That is no longer
the right response, because the experiment settling it has now been run and it came
out in the writeup's favour.

`report_spread_at_fixed_mean.md`: holding the pool mean **exactly** fixed and changing
only which prompts carry the value variation moves spread by a factor of 3.5 and the
selection gap by a factor of 3, on the judge's own logged preferences, across 323
rounds. Both arrangements obey the same law with one slope. So spread is a real lever
at a fixed mean, and the reason it looked pinned in the observed runs is that those
runs never separated variation within a prompt from variation between prompts.

**So the recommendation is now one added result, not four qualifiers.** The narrative
gets stronger rather than more hedged.

Also withdrawn from the first version: I flagged the "gap = spread × agreement"
sentence as overclaiming. That was my error — `experiments/selection_response_predictor.json`
had already audited it, agreement is a genuine pre-selection proxy for the realized
selection intensity, and the scale audit had already rejected the "slope is
design-derived" argument. **No change is proposed to lines 101–108.**

---

## Edit 1 — the one that matters: a new result, not a caveat

**Status: recommended.** Drops in as a self-contained paragraph. Nothing around it
needs rewording, and no existing number changes.

Best placement is the interventions section, after the existing two intervention
sentences, since it is a third and cleaner intervention. It would also work at the end
of the "What I measure" section.

### Before

> Adding base-model answers to a collapsed pool restores spread, allowing
> the agreement of the judge to pull a value that was previously stuck.
> Swapping the base-model judge for the min-risk oracle (making agreement
> −1) reverses a run that had climbed near the top of the value scale.
> These results suggest that spread and agreement could be useful as targets for
> interventions, and the effect can be forecast from their new values.

### After

> Adding base-model answers to a collapsed pool restores spread, allowing
> the agreement of the judge to pull a value that was previously stuck.
> Swapping the base-model judge for the min-risk oracle (making agreement
> −1) reverses a run that had climbed near the top of the value scale.
> These results suggest that spread and agreement could be useful as targets for
> interventions, and the effect can be forecast from their new values.
>
> Spread can also be moved on its own, without touching the value. A round's pool
> mean fixes the *total* variation among its candidates, but not how that variation
> is split between differences within a prompt and differences between prompts, and
> the judge only ever compares candidates within a prompt. Re-arranging 323 logged
> rounds to hold the pool mean exactly fixed while shifting variation into or out of
> the prompts changes spread by a factor of 3.5 and the resulting selection gap by a
> factor of 3, on the judges' own recorded preferences. Both arrangements follow the
> same rule, with one slope of 0.857 fitting all of them. Variation only counts when
> it sits inside the comparison the judge actually makes.

If you want it shorter, the last three sentences carry the result on their own.

---

## Edit 2 — optional, one clause

**Status: optional.** Only worth it if you want the clipping step explained; it is
currently unexplained. One clause, no new paragraph.

### Before

> For endpoints, the model repeats this update from the round-one candidate mean,
> holding spread, agreement, and pool composition fixed and clipping each step to
> the 0-to-1 value scale.

### After

> For endpoints, the model repeats this update from the round-one candidate mean,
> holding spread, agreement, and pool composition fixed and clipping each step to
> the 0-to-1 value scale, which keeps the forecast inside the range that spread
> itself has to shrink toward at either end.

---

## Edit 3 — optional, for Limitations and future directions

**Status: optional.** Sets up the multi-axis direction. Skip if the section is at the
length you want.

### Before

*(new paragraph, after the one beginning "The behavioral scope of this post is limited
to risk preference and insecure-code self-description.")*

### After

> Both axes here score each answer 0 or 1. Scoring each candidate on several value
> axes at once would turn the selection differential into a vector and the variation
> into a covariance, which would let the same measurements predict whether selecting
> on one value moves the others.

---

## Dropped from the first version

These are no longer proposed. Edit 1 above supersedes them by establishing the
positive result instead of qualifying the claim.

| Previously proposed | Why dropped |
|---|---|
| A paragraph in "What I measure" saying spread and agreement are not independent | Superseded: they *are* separable, and Edit 1 shows it directly |
| Rewording Findings item 3 to "adding an outside source of candidates" | The original wording is fine now that spread is established as a lever |
| Rewording the interventions opening to lead with the pool mean | Replaced by the additive Edit 1 |
| Scoping the ρσ factorization sentence | Withdrawn — the repo had already audited it correctly |

---

## Summary

| Edit | Where | Status |
|---|---|---|
| 1 | Interventions section, appended paragraph | **Recommended** — new result, additive, no rewording around it |
| 2 | End of the one-round-rule section | Optional — one clause explaining the clipping step |
| 3 | Limitations | Optional — sets up multi-axis work |

No figure needs to change, and no existing number in the writeup changes. A figure for
Edit 1 is drafting at `docs/figures/auto/spread-at-fixed-mean/` if you want one.

# Proposed writeup edits — before and after

Date: 2026-07-24, revised the same day. From the research-vision thread.

**Nothing in `docs/writeup_value_dynamics_sprint.md` has been edited.** This file is
the proposal only.

## Status: the main proposed edit has been WITHDRAWN

This file went through two revisions on 2026-07-24 and the net result is that
**nothing substantive is currently proposed for the writeup.**

Round 1 proposed four hedging edits, because candidate spread looked like it might be
bookkeeping on the pool mean rather than an independent quantity (the pool mean
accounts for 85.9% of the variance in measured spread on binary-scored axes).

Round 2 replaced them with a single added result, on the strength of a re-selection
analysis of logged pools that appeared to show spread driving the selection gap at a
fixed pool mean.

Round 3, after user challenge, withdrew that: the analysis was not an intervention
(nothing was trained) and its finding was close to definitional. The selection gap is
kept-minus-pool, so a prompt whose candidates all score alike has a gap of exactly
zero by arithmetic; collapsing within-prompt spread collapses the gap by
construction. The median ratio of gap to (agreement × spread) is 0.831 in the
high-spread arm and 0.825 in the low-spread arm — indistinguishable, so the
manipulation slid along the identity rather than testing it. And that within-prompt
spread is free at a fixed pool mean follows directly from the variance decomposition
and needs no experiment at all.

**So the writeup needs no change on this account right now.** The real experiment —
which requires training, because the untested claim is about the training step and
not about the identity — is specified at `experiments/spread_intervention/SPEC.md`
and is queued. If it returns, there may be something worth a paragraph then.

Also withdrawn earlier the same day: the flag on the "gap = spread × agreement"
sentence. `experiments/selection_response_predictor.json` had already audited it and
the existing framing is correct. **No change proposed to lines 101–108.**

The two optional edits below survive, both minor. Neither is load-bearing.

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

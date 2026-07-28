# Proposed writeup edit — before and after

Date: 2026-07-27. From the research thread.

**Nothing in `docs/writeup_value_dynamics_sprint.md` has been edited.** This is the
proposal only. One edit, recommended. It supersedes
`docs/writeup_proposed_edits_2026-07-24.md`, which ended with nothing proposed.

## Why this one is different from the withdrawn attempt

On 2026-07-24 I proposed adding a spread result and then withdrew it, because the
analysis behind it was a re-selection of logged pools with no training, and its
finding was close to definitional: a prompt whose candidates all score alike has a
selection gap of exactly zero by arithmetic, so collapsing spread collapses the gap by
construction.

The experiment has since been run properly, with training, twice.
`report_oracle_positive_control.md` and `report_transmission_followups.md`. The claim
below is about what happens to the **measured value after fine-tuning**, which no
identity forces.

## The evidence

Two arms differ only in how candidate value-variation is distributed across prompts,
at an **identical offered-pool mean every round** (enforced exactly by a knapsack; the
maximum difference between arms across all rounds is 0.000000). Same organism, same
selector, same hyperparameters, arms stepped in lockstep. Under oracle selection:

| Run | Spread arm | Concentrated arm | Difference |
|---|---|---|---|
| First | +0.406 | +0.017 | **+0.389** |
| Replication, fresh seeds | +0.368 | +0.073 | **+0.295** |

Against a measurement standard error of 0.054, so roughly six to seven times the
noise, replicated. The mechanism is visible in the round records: the concentrated
arm's within-prompt spread is 0.000 and its selection gaps are 0.000, 0.028, 0.042 —
the selector has nothing to act on — while the spread arm runs spreads of 0.29 to 0.38
and gaps of 0.24 to 0.33.

## The edit

**Status: recommended.** Additive. Nothing around it needs rewording and no existing
number changes. Best placed at the end of the interventions section.

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
> Spread can be intervened on directly, without changing where the value sits. A
> round's pool mean fixes the total variation among its candidates but not how that
> variation splits between differences within a prompt and differences between
> prompts, and the selector only ever compares candidates within a prompt. Holding
> the pool mean identical every round and moving variation out of the prompts stops
> the value moving: under selection that is otherwise as strong as possible, the
> value climbs 0.41 when the variation sits inside prompts and 0.02 when the same
> amount of variation sits between them. A replication on fresh seeds gives 0.37
> against 0.07. Variation only counts when it is inside the comparison the selector
> actually makes.

## Caveats you may want to fold in or leave out

These are in the reports; none of them undermines the edit, but you should know them.

- The concentrated arm is not perfectly inert. It drifts by up to 0.14 even with a
  selection gap of exactly zero, and the random-selection control also drifts, in
  inconsistent directions. So the contrast is selection-plus-drift against drift
  alone, not selection against nothing. The effect is several times larger than the
  drift, which is why the claim survives.
- Oracle selection is not a realistic judge. It was used because it makes the effect
  large enough to see; the magnitudes do not transfer to judge-driven loops.
- Two seeds per arm per run, four rollouts total across the two runs.

## Not proposed, for the record

The session also produced a long line of claims about the transmission coefficient
depending on judge agreement. **All of them were withdrawn** once seeds were matched
at n=7 per condition — the movement-to-gap ratio is flat around 0.45 with no trend,
which is what your existing model already says. That arc is recorded in the ledger as
a worked example of over-reading small samples. Nothing from it belongs in the
writeup.

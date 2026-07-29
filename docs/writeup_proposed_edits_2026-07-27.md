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
noise, replicated. The mechanism is visible in the round records. Pooled across the
four loops, the concentrated arm averages 0.024 within-prompt spread and 0.021
selection gap — the selector mostly has nothing to act on — against 0.328 and 0.294
for the spread arm. The concentrated arm is not exactly zero: it has nonzero spread
in four of its rounds, the largest being 0.114 with a gap of 0.111.

## CORRECTION 2026-07-27, before you read the edit: the framing was wrong

I pooled all 84 arm-rollouts and tested whether spread does anything **beyond**
producing the gap. It does not.

- Movement regressed on cumulative gap alone, both arms pooled:
  `movement = 0.007 + 0.402 x gap`, r = 0.79, n = 84. The intercept is
  indistinguishable from zero.
- Adding an arm dummy appears to help (+0.109, t = 3.62) — but the two arms occupy
  nearly disjoint gap ranges (concentrated −0.18 to 0.14, spread −0.96 to 0.96, with
  only 9 of 84 rollouts overlapping), and the gap-movement relation is convex
  (gap-squared term t = 3.34). The dummy is absorbing that curvature.
- **The clean test is within the spread arm alone**, where gap and spread both vary
  properly. There, mean within-prompt spread adds nothing beyond the gap:
  coefficient +0.125, SE 0.459, **t = 0.27**.

So spread is not a second lever acting alongside the gap. It determines whether a gap
can form at all, and the gap determines movement — which is exactly what the model
already says. The edit below is rewritten accordingly: it is a **causal confirmation
of the model's chain**, not an addition to the model.

That is a weaker claim than the one I first wrote, and still worth making, because
every previous test of that chain was observational with spread and the value
confounded.

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
> The chain from variation to selection to movement can be tested directly rather
> than inferred. A round's pool mean fixes the total variation among its candidates
> but not how that variation splits between differences within a prompt and
> differences between prompts, and the selector only ever compares candidates within
> a prompt. Holding the pool mean identical every round and moving the variation out
> of the prompts leaves the selector nothing to act on: the gap collapses to 0.02 and
> the value climbs 0.02, against a gap of 0.29 and a climb of 0.41 when the same
> amount of variation sits inside prompts. A replication on fresh seeds gives 0.37
> against 0.07. Across all 84 rollouts run this way, movement is predicted by the
> gap alone, and the amount of variation adds nothing once the gap is known. Variation
> matters because it is what lets a gap form, not as a separate force. Because the two
> arrangements are applied to one shared candidate pool from one shared starting model,
> the arrangement itself is a randomised instrument for the gap, and the resulting
> causal estimate is that about three quarters of the selection differential appears as
> behavioural change.

## Caveats you may want to fold in or leave out

These are in the reports; none of them undermines the edit, but you should know them.

- The concentrated arm is not exactly flat: its four per-loop changes are −0.062,
  +0.097, +0.132 and +0.014. I initially flagged that as unexplained drift, but it
  does not survive testing — on the 340-round corpus, rounds with a selection gap
  under 0.01 show mean absolute movement of 0.0519 against a measurement-noise floor
  of 0.0905, i.e. below noise. The concentrated arm's wobble is consistent with
  measurement noise across four rollouts.
- The concentrated arm is not perfectly spread-free either: it has nonzero
  within-prompt spread in four rounds across the two runs (0.042, 0.039, 0.042, and
  one round at 0.114 with a gap of 0.111). Pooled across all four loops the arms are
  0.328 against 0.024 on spread and 0.294 against 0.021 on gap.
- Pooled over both runs the value change is +0.387 (spread) against +0.045
  (concentrated). The per-run figures quoted above are the same data split by run.
- One of the four loops stops after round 2, when no offered-pool mean was reachable
  by both arms once the candidates had gone value-uniform.
- Oracle selection is not a realistic judge. It was used because it makes the effect
  large enough to see; the magnitudes do not transfer to judge-driven loops.
- Two seeds per arm per run, four rollouts total across the two runs for the headline
  contrast; the causal coefficient below draws on 36 distinct round-1 matched pairs.
- **The 0.40 figure that appeared in earlier drafts of this file is withdrawn.** It was
  an observational regression on cumulative gap, biased down roughly twofold by two
  channels: a run that moves toward a rail generates value-uniform candidates and so
  shrinks its own later gaps, and runs that moved fastest were preferentially aborted
  by the matched-pool-mean constraint. The randomised round-1 estimate is **0.754, 95%
  CI [0.621, 0.984]**. Quote that if you quote a coefficient at all.

## Not proposed, for the record

The session also produced a long line of claims about the transmission coefficient
depending on judge agreement. **All of them were withdrawn** once seeds were matched
at n=7 per condition — the movement-to-gap ratio is flat around 0.45 with no trend,
which is what your existing model already says. That arc is recorded in the ledger as
a worked example of over-reading small samples. Nothing from it belongs in the
writeup.

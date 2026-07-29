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

---

# ADDENDUM 2026-07-28 — the edit above got stronger, and one number in it needs a footnote

Nothing above is withdrawn. Three things landed the next day that bear on it.

## 1. The 0.754 estimate now has independent corroboration

The edit rests on a single instrumented estimate from one corpus. It no longer
has to. Refitting the movement law on the **340-round unified corpus** — the
corpus behind the writeup's own headline results, not the spread-intervention
runs — with the pool-offset term included and measurement error removed gives a
response coefficient of **0.809**. That is a different dataset and a different
identification strategy, and it lands inside the instrument's interval.

| estimate | corpus | identification | outcome-dependent censoring | value |
|---|---|---|---|---|
| observational, corrected | unified, 340 rounds / 74 runs | ordinary regression | 4 of 74 runs stop short | **0.809** |
| randomised instrument | spread-intervention, 36 matched pairs | Wald ratio | none by construction | **0.754** [0.621, 0.984] |
| observational, corrected | spread-intervention, 414 rounds / 126 runs | ordinary regression | heavy — the abort rule removed the fastest movers | 0.450 |

The two censoring-free estimates agree with each other; the outlier is exactly
the one the censoring diagnosis predicts. If you want a single sentence for the
writeup: *about three quarters to four fifths of the selection differential
appears as behavioural change, estimated three ways.*

**Recommended.** Replace "about three quarters" in the proposed edit with "about
three quarters to four fifths", and, if you want the strength on the page, add
the triangulation as a footnote.

## 2. The "n = 84 arm-rollouts" wording on line 43 needs a footnote

*Before:* "I pooled all 84 arm-rollouts…"

*After:* "I pooled all 84 arm-rollout records (72 physical rollouts in 11 seed
clusters; one control seed was recomputed identically across ten output
files)…"

**Optional** — this sentence is in a correction section rather than in the edit
itself, so it may not reach the writeup at all. But if any version of it does,
the count should not read as 84 independent runs.

## 3. There is now a theoretical reason to expect a coefficient below 1

Ferbach, Bertrand, Bose & Gidel ([arXiv 2407.09499](https://arxiv.org/abs/2407.09499))
model this exact curated self-consuming loop. I had them wrong on 07-27 and have
since read the paper properly. Two things are worth knowing:

- Under exact fitting, response equals the selection differential **identically**,
  for any number of candidates and any selection rule. So a coefficient below 1
  is not explained by keeping 2 of 6.
- But their Equation 8 covers the case where reference data is mixed back at
  ratio λ, and there the response is **λ/(1+λ)** times the differential. A
  coefficient of 0.78 is exactly λ/(1+λ) at λ ≈ 3.5. **An anchored fine-tune is
  predicted to transmit below 1 by design, not by defect.**

**Optional, and only if you want a theory sentence.** Something like: *the
shortfall from 1 is what a fine-tune anchored to its starting point is expected
to show.* I would not put more weight on it than that until we have varied the
anchoring and watched the coefficient move.

One scope limit to respect if the paper is cited at all: every result in it
assumes a **fixed** reward. Nothing in it covers a judge that is retrained
alongside the generator, so it says nothing about the self-judge runs.

## 4. A sentence already in the writeup is tighter than its data

Not part of the proposed edit — flagging it because it is in the current draft.

The Limitations section says: *"across six runs differing only by seed, early
agreement turned negative in the two runs that collapsed and remained nonnegative
in the four that amplified."*

Pulling the six raw trajectories, that separation is clean **on round 1 alone**.
Widened to the first two rounds it is not: seed 43 sums to −0.437 against
collapsing seed 45's −0.441 and does not collapse. Spread also reaches exactly
zero by round 3 or 4 in all six runs, which makes late-round agreement
degenerate.

**Recommended, if you keep the sentence:** change "early agreement" to
"round-one agreement", which is what was actually measured and is still true.
The rest of the sentence stands.

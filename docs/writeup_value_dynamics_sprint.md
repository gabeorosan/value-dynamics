# When AI drives its own training process, how do its values change?

![](figures/hero_vision.svg)

AI increasingly generates and selects its own training data, through
[self-rewarding pipelines](https://arxiv.org/abs/2401.10020),
[constitutional loops](https://arxiv.org/abs/2212.08073), and
[synthetic data](https://www.interconnects.ai/p/llm-synthetic-data).
While AI alignment has recognized the importance of considering reflectivity
of values and the resulting feedback dynamics of self-modification
([value drift](https://www.lesswrong.com/w/value-drift)), and there is
empirical work on whether frontier models defend their values ([alignment faking](https://arxiv.org/abs/2412.14093)), on degradation
under recursive training
([model collapse](https://arxiv.org/abs/2305.17493)), and on
[attractor states](https://arxiv.org/abs/2606.30571) that emerge in-context
in model–model conversations like the
[spiritual-bliss attractor](https://www-cdn.anthropic.com/4263b940cabb546aa0e3283f35b686f4f3b2ff47.pdf)
(explored in the wild in the
[Infinite Backrooms](https://dreams-of-an-electric-mind.webflow.io/)),
there is little empirical work that follows
these dynamics through training and across settings and seeds.

I fine-tuned Qwen3-4B and OLMo-3-7B with value orientations
(risk-seeking or insecure-code-generating, adapted from the
[Tell Me About Yourself](https://arxiv.org/abs/2501.11120) and
[Emergent Misalignment](https://arxiv.org/abs/2506.11613) model organisms),
ran them through selection loops under systematically varied judges,
candidate sources, and alternative sources (what the judge compares each
candidate against), and found a predictive model, grounded in the
[Price equation](https://doi.org/10.1038/227520a0) and
[quantitative selection theory](https://pmc.ncbi.nlm.nih.gov/articles/PMC7133505/),
that turns a measurement of the loop's first round into calibrated
endpoint estimates and reproduces the direction, pace, and spread of the
observed trajectories.

![The round's six candidates are its pool; "pool" and "mixed pool" always mean this candidate pool. Training on the two kept candidates takes about 10 optimizer steps, held-out prompts re-measure the value between rounds, and the judge-schedule runs extend to eight rounds.](figures/synthesis_experiment_kit.svg)


## Findings

1. **A deterministic model using first-round measurements predicts where
   each run ends.** Each round, the two kept answers differ from the pool
   average by the pool's spread (the SD of the answers' value scores)
   times the judge's agreement (the correlation of the judge's
   preferences with those scores), with no fitted coefficient; training
   then moves the value to that kept average. Iterated, this predicts a
   run's final value from its first round with a mean absolute error of
   0.118 on the 0-to-1 value scale, versus 0.431 for assuming no change.
2. **Adding noise gives a stochastic version that reproduces the
   dynamics of the observed trajectories.**
   The total round-to-round value change over a run is about the same in
   simulation and observation (0.709 against 0.648), as is how often a
   run changes direction (1.22 against 1.20 per run); bands drawn to
   contain 80% of final values contain 89%.
3. **The effectiveness of interventions is driven by changes in the
   model's central quantities (spread and agreement).**
    - Restoring spread to a collapsed candidate pool eroded a previously
      stuck value.
    - Swapping the judge for a min-risk oracle set agreement to −1 and
      reversed a run that had climbed near the top of the value scale.

## What I measure

Each organism's value is the mean value score of its answers: for the
gambling model, the share that pick the risky gamble; for the
insecure-code model, how insecure its answers to three fixed questions
about its own coding habits are, scored 0–1 by its frozen base model.
Each candidate has a **judge score**, the probability the judge picks it,
averaged over both option orders (for an oracle judge, the judge score is
set to the value score).

![](figures/auto/setup-both-models/setup_both_models_v3.svg)

Two quantities are measured each round, spread and agreement, and together
they forecast the selector gap. Spread and agreement are measured within
each prompt's pool and averaged over the round's prompts.

![](figures/auto/state-variables/state-variables.svg)

The model tracks four positions, `q`, `p`, `k`, and `v`, and the distances
between them; the number-line figure below shows them together. `q`, `p`,
and `k` are candidate-pool means; `v` is the behavioral value measured
from the organism's answers, the coordinate forecasted by the model.

## One round: the value moves to what the judge keeps

The judge enters the loop only as the choice of which two candidates are
kept. The parameter-free one-round rule is

`next value = kept candidate value mean`.

Holding each complete experimental condition out, it predicts the next
measured value at MAE **0.081** across all 340 rounds, versus 0.128 for
predicting no change, and it beats using the kept-minus-own-mean distance
alone (0.098) or selector gap alone (0.112). The accuracy is the same
across model families, value axes, and pool compositions.

![](figures/auto/model-one-round-line/model-one-round-line.svg)

Before selection, two numbers predict the selector gap: how much the
candidates vary on the value axis (spread σ) and how consistently the
judge's choices track it (agreement ρ, the correlation between the
candidates' judge scores and their value scores):

predicted selector gap *g* = *ρσ*, so predicted kept mean *k* = *p* + *ρσ*.

ρσ reconstructs the realized gaps at R² 0.81 (mean absolute error
0.042) over the 290 rounds with logged judge scores, and predicting the
next value from the forecast kept mean is nearly as accurate as using
the actual kept mean (MAE 0.100 versus 0.085 on matched rounds).

To iterate, training moves the organism's own candidate mean `q` about
0.79 of the way to the kept mean each round; for a binary value score the
new mean sets the next spread (q(1−q) minus the variance across prompt
means; held-out R² 0.78 versus 0.58 for assuming no change), the
continuous insecure-code spread is measured each round, and agreement is
carried forward from round 1. Agreement is stable enough for that: it
changes little from round to round within a setup, with 82% of its
variance between judge × alternative-source × candidate-source conditions.

![](figures/auto/model-recurrence/model-recurrence.svg)

## Forecasting endpoints from first-round measurements

Everything the model needs is measured in the first round: spread,
agreement, and the pool composition. Iterated with those numbers frozen,
it turns a one-round measurement into a whole-run forecast, and the
figure below scores that forecast across all the runs: each run sits at its
round-1 measurement, colored by where it actually went, over the model's
prediction for that spot. Endpoints land at mean absolute error 0.118
versus 0.431 for assuming no change, and 37 of 38 large movements point
the right way. Where the judge is neutral (ρ ≈ 0) the forecast is flat, while
runs scatter due to training instability.

![Dot color is the run's observed whole-run value move and the background is the model's forecast for that spot, on the same color scale, so matching colors mean the model called the direction; 35 of the 41 runs that moved by at least 0.15 match.](figures/auto/synthesis-dial-plane-horizon/synthesis-dial-plane-horizon.svg)


The forecast stays accurate as it looks further ahead: its error is 0.100
one round out and 0.130 four rounds out, while assuming no value change degrades
from 0.31 to 0.43. This is because selection moves a run mostly in its
first rounds and then levels off, so a forecast that gets the early move
right stays right at the endpoint. Most of the remaining error comes from
agreement drifting during the run: a judge's agreement depends on the
candidate distribution in front of it, and training changes that
distribution.

The deterministic forecast only gives the average path that real runs
scatter around. The value is read from a limited number of sampled answers, so each
reading carries sampling noise, and the loop itself varies: the judge's
picks land around ρσ rather than exactly on it, training lands near but
not exactly on the kept mean, and agreement drifts between rounds. The stochastic version of the
model adds a random term at each of these points, with sizes taken from
the measured residuals; its equations are the figure below.

![Each noise term's size is the spread of that stage's leftover errors, pooled across all conditions except the one being forecast. Measurement noise affects only the value being read, not the state the next round starts from.](figures/auto/staged-noise-forecast/staged-noise-forecast.svg)

Sampled forward, the stochastic model reproduces the dynamics of the
observed trajectories: the total round-to-round value change over a run
is 0.709 against 0.648 observed, runs change direction 1.22 times against
1.20, and 89% of final values fall inside the predicted 80% band. The figure
below shows the comparison run by run: each family's observed
trajectories on top, one simulated draw per run below, with the
band shaded.

![The figure is interactive: press re-simulate to reveal a fresh pre-sampled draw for every run (24 sets, all drawn by the committed sampler).](figures/auto/rollouts-vs-observed-spaghetti/rollouts-vs-observed-spaghetti.svg)

Runs can be steered effectively by intervening on spread and agreement.
Adding base-model answers to a collapsed pool restores spread, allowing
the agreement of the judge to pull a value that was previously stuck.
Swapping the base-model judge for the min-risk oracle (making agreement
−1) reverses a run that had climbed near the top of the value scale.

![](figures/auto/synthesis-intervention-cards/synthesis-intervention-cards.svg)

## Related frameworks

The loop's quantities are the ones selection theory already names: the
selector gap is a **selection differential** in the sense of the
[Price equation](https://doi.org/10.1038/227520a0), and `g = ρσ` is a
**breeder's equation**, culling intensity times the criterion's correlation
with the trait times the trait's spread, intensity constant because the keep
rule never changes. It is the structure of the
[cross-entropy method](https://doi.org/10.1007/s10479-005-5724-z), whose
failure is variance collapse and whose fix is variance injection, both of
which the intervention cards show; and where accounts of self-training loops
have each caught one term of it, the reliability of the judge or the survival
of variation, the selection term is what sets direction.

Read this way, the loops call for a science of how a trait moves as a selector
culls a population and breeds the next generation from the survivors, which is
what quantitative genetics has studied for over a century. As models come to
design their successors and the loops those successors run, an aligned value
is a trait held stable, or improved, across rounds of selection that the
models themselves carry out, and keeping it aligned becomes the design of
populations and selection pressures under which the values worth having gain
ground and the harmful ones lose it.

## Next directions

> **REVIEW — pick one: three candidates for this section. They differ in
> what they lead with and how far out they look. Current text kept below
> for comparison.**
>
> **Candidate D — ordered by what the model itself exposes.**
>
> The model's own weakest point is agreement over time. It freezes ρ after
> the first round, which works because agreement is stable within a setup,
> and most of the error that remains is the drift it ignores. Tracking ρ
> round by round costs one pool of judge scores; the real question is
> whether its drift is predictable from the candidate distribution the
> judge is now facing, since a judge's agreement is a property of the
> pairing rather than of the judge alone. Answering that would turn the
> last free-floating quantity into part of the dynamics.
>
> The second direction is to keep predicting before the data exists.
> Measuring the first round, committing the forecast, and scoring it
> afterwards is cheap, and it is the only thing that separates a model
> that works from a model fitted to runs already seen. Judge swaps are the
> sharpest case, since a swap moves agreement mid-run and the rule for when
> to re-measure has to be fixed in advance for the answer to mean anything.
>
> The third is to push on the factors themselves: how much outside material
> is needed to reopen a collapsed pool, whether the variance rule survives
> longer horizons, and whether training on what a model says about itself
> moves what it actually does. The last is nearly free here, because those
> loops saved their endpoint adapters and the code those models write can
> still be scored.
>
> Further out are the versions this setup cannot reach. Reasoning models
> would make the judging channel legible, turning agreement from a
> correlation into an argument that can be read and audited. Letting a
> model set its own loop, rather than having it varied for the model, shows
> which control it reaches for. And interpretability tools would say what
> else moves when the measured trait does, which is the question this
> approach leaves open by construction.
>
> **Candidate E — organized around what would make the account general.**
>
> Three things would turn one law into an account that travels.
>
> The first is agreement over time. This model freezes ρ after the first
> round and inherits whatever drift follows, which is where most of its
> remaining error sits. Agreement is a property of a judge and a candidate
> distribution together, so as training moves the distribution the judge's
> alignment with the trait moves too; whether that motion is predictable
> from the new distribution is the open question, and it costs one pool of
> judge scores per round to find out.
>
> The second is scale and horizon. Everything here is four rounds on small
> open models with adapters. The laws are cheap to test on longer loops,
> larger models, and other traits, and the interesting outcome is the one
> where they break: a horizon or a model size at which the trait stops
> tracking the selection term would say more about the limits of this view
> than another confirmation would.
>
> The third is prediction under commitment. Measure, commit, then score.
> This costs nothing but discipline, and without it a dynamical account is
> indistinguishable from a curve fitted after the fact. Judge swaps are the
> sharpest test, because a swap moves agreement mid-run and the
> re-measurement rule has to be fixed before the trajectories are collected.
>
> Beyond that, the things this setup cannot see. Reasoning models would
> make judging legible, turning agreement into an argument rather than a
> correlation. Letting a model design its own loop shows which control it
> reaches for first, which is the closest small-scale analogue of the
> regime this is all aimed at. And interpretability would say what else
> moves when the measured trait does.
>
> **Candidate F — short, three paragraphs.**
>
> The first thing to fix is agreement over time. The model freezes ρ after
> round one, and the drift it ignores is where most of its remaining error
> lives. Since a judge's agreement depends on the candidates in front of
> it, and training changes those candidates, the question worth answering
> is whether the drift follows predictably from the new distribution. That
> costs one pool of judge scores per round.
>
> Then: prediction under commitment, and pressure on the boundaries.
> Measure, commit, score, on every new run family, with judge swaps as the
> sharpest case since a swap moves agreement mid-run. Push the loops longer
> and the models larger, and take a break in the laws as the most
> informative outcome available. Test how much outside material reopens a
> collapsed pool, and whether training on what a model says about itself
> changes what it does, which the saved endpoint adapters make nearly free.
>
> Further out sit the versions this setup cannot reach: reasoning models,
> where agreement becomes an argument that can be read rather than a
> correlation; models that set their own loop parameters, showing which
> control they reach for; and interpretability, which would say what else
> moves when the measured trait does.

> **Current text (unchanged) below.**

The clearest gap is agreement over time. This model freezes ρ at round 1 and
carries it forward, which works because agreement is stable within a setup,
but most of the remaining forecast error sits there. Agreement costs one
pool's worth of judge scores to measure, so it is cheap to track round by
round; the open question is whether its drift is itself predictable from the
new candidate distribution, which would close the loop rather than just
re-measure it.

The second is to keep making calls before seeing the data. Measure the first
round, commit the forecast, then score it. Judge swaps are the sharpest test,
since a swap changes agreement mid-run and the forecast has to be re-measured
at that point rather than carried through; fixing the re-measurement rule
before collecting the trajectories is what makes the result mean anything.

The third is the factors themselves: how endpoint depends on the share of
injected outside material, whether the binary spread rule survives longer
horizons, and whether training on self-description moves the behavior it
describes. That last one is nearly free here, since the self-description
loops saved their endpoint adapters and blind-scoring the code those models
write would settle a coupling no run in this program has measured.

Further out, the interesting versions are the ones this setup cannot reach.
Reasoning models would make the judging channel legible, turning agreement
from a correlation into an argument that can be read. Letting a model change
its own loop settings, rather than having them varied for it, asks which
control it reaches for first. And interpretability tools would say what else
moves when the measured coordinate does, which is the question this whole
approach leaves open.

## Limitations

These are short loops on small models: four rounds, eight in the schedule
runs, two open model families, two narrow value coordinates, LoRA adapters
rather than full fine-tunes. Nothing here establishes what happens over
hundreds of rounds or at frontier scale.

The one-round rule and the `ρσ` factorization are descriptive associations
measured on logged pools, and the closed-loop results hold out one
experimental condition at a time within a single program, which is weaker
than replication by someone else. The prospective evidence is two items: a
predictor frozen before the runs, which beat an otherwise matched predictor
without the selector-gap term by 17–42% on three blind release sets, and one
preregistered forecast for the code-security control arms that was scored
after the fact. The rule that the new mean sets the next spread is specific
to the binary risk score; the continuous axis has its spread measured each
round instead.

The value coordinate is what the model generates, not what it internally
represents, and on the insecure-code side it is what the model says about its
coding habits rather than the code it writes. Those three habit questions are
also the loop's training prompts, which is why that channel is the one the
loop acts on, but it means the self-description results do not license claims
about code quality. Forced-choice probes are reported as secondary throughout,
because they carry option-order effects.

Plenty in the wider program did not work. Many finer-grained preregistered
predictions failed: one grid met 6 of its 13 criteria, another 2 of 5, and
three separate screens for owner-blind judging each fell to nested confounds.
Those failures, and the rest of the program, are in the repository reports and
the claim ledger.

## Records

Every number in this post traces to a committed result file through a named
scorer. The claim registry is `docs/ANALYSIS_LEDGER.md`, which maps each claim
to its data, its scorer, and its current verdict. The core analyses are
`report_spread_util_unified.md` (the movement law and the `ρσ` factorization),
`report_spread_rollout_bakeoff.md` and `report_model_ladder_horizon.md`
(closed-loop endpoints and how the forecast degrades with horizon),
`report_trajectory_adjustment_bakeoff.md` (where the noise goes), and
`report_code_security_control_arms.md` with
`report_control_arm_forecast_score.md` (the erosion experiment and its scored
forecast). `report_prewriteup_reproduction_gate.md` records a re-run of every
modeling script, with all committed results regenerating byte-identically.

Compute was the free Kaggle and Colab tiers plus about $25 of Modal credits,
funded by a BlueDot Impact grant.

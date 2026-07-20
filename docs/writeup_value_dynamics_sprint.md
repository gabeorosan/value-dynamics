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

The loop's pieces have standard names. The selector gap is the
selection differential of the [Price equation](https://doi.org/10.1038/227520a0),
and the forecast `g ≈ ρσ` is the breeder's-equation structure from
[quantitative selection theory](https://pmc.ncbi.nlm.nih.gov/articles/PMC7133505/) —
there, a selection differential is (how hard the selector culls) × (how well
its criterion correlates with the trait) × (the trait's SD); with the keep
rule fixed at keep-two-of-six throughout, the first factor is constant and
folds into the measured ρ. Generate →
rank → keep elites → refit is the update of the
[cross-entropy method](https://doi.org/10.1007/s10479-005-5724-z): the elite
mean is the update target (why the kept-mean law works), spread is the
generator's exploration variance, and CE's variance-shrinkage warnings and
variance-injection remedies are the algorithmic analogue of self-pool
starvation and outside-source reopening.
[Reward-model overoptimization](https://arxiv.org/abs/2210.10760) is why
agreement must be re-measured after the candidate distribution shifts; the
[model-collapse](https://www.nature.com/articles/s41586-024-07566-y) and
[self-consuming-loop](https://proceedings.iclr.cc/paper_files/paper/2024/hash/ebc042e767de551803ccfcc45e2454f5-Abstract-Conference.html)
results motivate tracking how much variety the pool still has and whether
new material is arriving, without establishing this experiment's measured
value-axis mechanism.

## Where this should transfer

The model makes measurable predictions about setups it was not fit on. A
self-rewarding pipeline is a self-judge on self-only pools: expect movement
to stall as selection homogenizes the generator's output unless outside data
arrives — and remember judgment and generation can disagree, in which case
the loop erodes the value instead of amplifying it. A constitutional loop
judges against a fixed alternative: measure agreement under the deployed
comparison protocol, because reference-anchored agreement did not transfer
to pairwise choice here. A pipeline mixing vendor or web text is a mixed
pool: the outside source shifts the training targets and adds
between-source variation. An RLAIF reward model is a judge whose agreement
on the policy's actual samples is one pool's worth of scoring to measure
before an update lands. Each is the same three measurements adapted, at
pilot cost.

## Next directions

First, model the missing agreement trajectory: ρ costs one pool's worth of
judge scores — track it round by round across judges, alternative sources,
and changing pools, and test whether its changes are predictable from the
new candidate distribution rather than merely re-measurable. Second, keep
predicting before the data arrives: measure the first round, commit the
forecast, then score it, on every new run family. Judge swaps are the place
to start, since a swap changes agreement mid-run and the forecast has to be
re-measured at that point rather than carried through; fix the rule for when
to re-measure before collecting the trajectories. Third, experiments on the
factors themselves: dose–response of injection share, whether the binary
spread rule still holds over longer horizons, and one cheap cross-channel
test:
the self-description loops saved their endpoint adapters, so blind-scoring
the code those endpoints write would answer whether training on
self-description moves actual code quality, the one direction of that
coupling no run has measured. Fourth, the sharper versions of the earlier
directions: thinking models make the judgment channel readable (agreement
as an inspectable argument, not just a number); letting the model modify
its own training setup asks which control channels move spread, agreement,
or the outside-source term fastest; mechanistic measures would show what
else moves when the measured coordinate does.

## Limitations

Short LoRA loops: four rounds (eight in the schedule runs), two small open
model families, two narrow value coordinates. The one-round law and the
factorization are descriptive associations on logged pools; the closed-loop
results are leave-one-condition-out within the same program. The prospective
evidence is two items: a predictor frozen before the runs, which beat an
otherwise matched predictor without the selector-gap term by 17–42% on three
blind release sets, and the scored control-arm forecast
(`report_control_arm_forecast_score.md`). The rule that the new mean sets
the next spread is specific to the binary risk score.
In the insecure-code loops the primary coordinate is the self-description
channel because the three habit questions are also the loop's training
prompts (no per-round code-writing was logged to score); the one family
trained on coding tasks, the OLMo code-security loop and its controls,
scores the code itself and its results live in the repository reports.
Generated-answer measures are primary throughout; forced-choice probes carry
option-order effects and are secondary. Many finer-grained preregistered
predictions in the wider program failed: one grid met 6 of its 13 criteria,
another 2 of 5, and three separate screens for owner-blind judging each fell
to nested confounds. The rest of that program lives in the repository reports
and the claim ledger, and the archived full draft is
`docs/writeup_archive_2026-07-15_full_program.md`.

## Records

Primary records in the project repository under `docs/`:
`ANALYSIS_LEDGER.md` (the claim registry) ·
`report_spread_util_unified.md` (movement law, factorization, spread and
agreement ledgers; scorer `scripts/analysis_spread_util_unified.py` →
`experiments/spread_util_unified.json`) ·
`report_predictive_model_literature.md` and
`report_value_predictor_models.md` (the unit selection-response model and the
one-round predictor bakeoff; scorers
`scripts/analysis_selection_response_predictor.py` and
`scripts/analysis_value_predictor_bakeoff.py`) ·
`report_spread_conversion_model.md` and `report_spread_definition_audit.md`
(the generator-state conversion chain; estimator fine print and alternatives) ·
`report_spread_rollout_bakeoff.md`, `report_rollout_property_fidelity.md`,
`report_unit_rollout_properties.md`, and `report_model_ladder_horizon.md`
(closed-loop endpoint, path-property, and horizon analyses) ·
`report_trajectory_adjustment_bakeoff.md` (noise location and the staged
stochastic forecast) ·
`report_olmo_code_security_duel_loop.md`,
`report_code_security_control_arms.md`, and
`report_control_arm_forecast_score.md` (the erosion experiment, its control
arms, and the scored preregistered forecast) ·
`report_loop_integrator_decomposition.md` (frozen gap predictor) ·
`report_crossfamily_oracle.md`, `report_mixed_reopen_qwen.md`,
`report_pool_rescoring.md`, `report_head2head_olmo.md` (the underlying
experiments) · `report_prewriteup_reproduction_gate.md` (every modeling
script re-run; all committed results regenerate byte-identically).

Compute: free Kaggle and Colab tiers, plus about $25 of Modal credits
funded by a BlueDot Impact grant.

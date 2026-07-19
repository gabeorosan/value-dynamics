# When AI drives its own training process, how do its values change?

![A model generates and selects its own training data; its installed value can enter a virtuous or a vicious cycle](figures/hero_vision.svg)

*A model generates and selects its own training data, then fine-tunes its
successor on what it kept; an installed value can drift up a virtuous cycle or
down a vicious one. This post measures which way, and why.*

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
candidate against), and found a predictive model that, given
measurements of a loop's first round, provides calibrated endpoint
estimates and reproduces the direction, pace, and spread of the observed
trajectories.

![One loop, six interchangeable parts](figures/synthesis_experiment_kit.svg)

*A run picks one option per slot and repeats: the organism writes six
candidates per prompt — the round's **pool** ("pool" and "mixed pool" always
mean this candidate pool; a mixed pool has outside-source candidates among
the six) — a judge keeps two, the organism trains on them (~10 optimizer
steps), and held-out prompts re-measure the value; four rounds (eight in the
judge-schedule runs). The **cautious judge** is the base model fine-tuned to
favor cautious answers, then frozen — not a copy of the organism. The
insecure-code self-judge loops ask the judge a **candid** question — "Which
answer is the more candid, self-aware description of how this assistant
ACTUALLY writes code — honestly acknowledging real tendencies and flaws
rather than giving an idealized answer?" — instead of a bare "which answer
is better?". This post varies one slot at a time.*


## Findings

1. **A deterministic model using first-round measurements predicts where
   each run ends.** Each round, the two kept answers differ from the pool
   average by the pool's spread (the SD of the answers' value scores)
   times the judge's agreement (the correlation of the judge's
   preferences with those scores), with no fitted coefficient; training
   then moves the value to that kept average. Iterated, this predicts a
   run's final value from its first round with a mean absolute error of
   0.118 on the 0-to-1 value scale, versus 0.431 for assuming no change.
2. **Adding noise where the measurement says it lives gives a stochastic
   version that reproduces the dynamics of the observed trajectories.**
   The total round-to-round value change over a run is about the same in
   simulation and observation (0.709 against 0.648), as is how often a
   run changes direction (1.22 against 1.20 per run); bands drawn to
   contain 80% of final values contain 89%.
3. **The effectiveness of interventions is driven by changes in the
   model's central quantities (spread and agreement).** Three matched
   pairs, each changing one setting: restoring spread to a collapsed
   candidate pool let a previously stuck judge move the value; switching
   the same judge from reference scoring to head-to-head duels weakened
   its agreement and settled the run lower; and reversing agreement
   outright, with a rule that always keeps the lowest-value answers,
   brought a run pinned at the top back down.

## What I measure

Each organism has one primary coordinate, read from what it actually
generates: for the gambling model, the share of its free answers that pick
the risky gamble; for the insecure-code model, how insecure its answers to
three fixed questions about its own coding habits are, scored 0–1 by the
frozen Qwen3-4B base.

The self-description channel is primary because it is what the loop acts
on: in the Qwen insecure-code experiments the prompts *are* the three habit
questions and training runs on the kept answers, and the corpus logged no
per-round code-writing to score. The one family whose loop runs on coding
tasks — the OLMo erosion loop and its controls — uses the code itself as
the primary coordinate (**task-code insecurity**: a live frozen-base score
each round, anchored by blinded manual severity review).

![The two model organisms and how each is measured](figures/auto/setup-both-models/setup_both_models_v3.svg)

Per round, two measurements and the gap they forecast carry the model. A
candidate's **judge score** is the probability the judge picks it,
accumulated over its A-or-B comparisons (for the score oracle, the value
score itself). Spread and agreement are measured within each prompt's pool
and averaged over the round's prompts, and agreement changes little from
round to round within a setup; 82% of its variance is between judge ×
alternative-source × candidate-source conditions.

![The per-round measurements](figures/auto/state-variables/state-variables.svg)

The four positions — `q`, `p`, `k`, `v` — and the distances between them
are the model's whole vocabulary; the number-line figure below shows them in
one picture, and every later equation reuses them unchanged. (Total SD
across prompts is tracked separately as **distributional breadth** — it
contains between-prompt differences the within-prompt selector cannot rank —
and is never called spread.)

## One round: the value moves to what the judge keeps

The judge touches the model only through which two candidates it keeps, and that
channel is enough to steer the value. The parameter-free one-round rule is

`next value = kept candidate value mean`.

Holding each complete experimental condition out, it predicts the next
measured value at MAE **0.081** across all 340 rounds, versus 0.128 for
predicting no change, and it beats using the kept-minus-own-mean distance
alone (0.098) or selector gap alone (0.112). A fitted update gain lands at 0.83 without
improving absolute error: the value moves most of the way to the kept mean in
one round, and the identity update is the forecast.

![One round, on the value line: pool, kept set, and the move](figures/auto/model-one-round-line/model-one-round-line.svg)

*Everything the model tracks, as positions on the value line: the organism's
own candidates (mean q), the candidate pool after any outside-source
candidates are added — the candidates eligible to be kept, which in the
static-alternative format excludes the comparison answer (mean p),
the two candidates the judge keeps (mean k) — and the value's move to k. The
accuracy above (0.081 over 340 rounds) is the same in every slice: both model
families, both value axes, all pool compositions.*

In a self-only pool the kept mean is wherever selection put it. In a mixed
pool the outside candidates move the pool mean too, so the update coordinate
is training displacement: `kept − own mean = selector gap + pool shift`.
Across the 96 mixed-pool rounds it correlates 0.83 with behavioral movement
versus 0.63 for the selector gap alone — the mixed-pool endpoint results as
mechanics: those runs ended near their outside source's level because the
judge kept outside text, the kept mean sat there, and the value converged to
it.

**Before selection, two numbers predict the kept mean.** How far the kept
set's mean lands from the pool's depends on two things worth measuring
separately: how much the candidates vary on the value axis (spread σ), and
how consistently the judge's choices track that axis (agreement ρ). The
forecast needs nothing else, not even a coefficient:

`predicted selector gap g = ρσ`, so `predicted kept mean k = p + ρσ`.

The unit-coefficient rule reconstructs realized selector gaps at R² 0.81
(mean absolute error 0.042) over the 290 rounds with logged judge scores,
uniformly across value axes, model families, and pool compositions, and it
predicts the next value about as well as seeing the judge's actual picks
would.

Spread says whether the pool offers variation on the value axis at all;
agreement says whether this judge, asked this way, on this pool, tends to
keep one side of it. The measured agreements explain the loop outcomes cell
by cell:

- the score oracle (keeps the two lowest-scoring candidates) is the
  ceiling: ρ = −1.0 by construction, realizing 70–81% of the maximum
  achievable gap in three of its four cells;
- random keeping sits at zero;
- the Qwen risk grid's judges sit near zero (ρ ≈ 0.0–0.11), so its fan of
  endpoints comes from training instability rather than selection;
- the same cautious judge on the same OLMo pools has ρ = +0.38 against a
  fixed reference and +0.10 under duels: the alternative source is part of
  the selector;
- the Qwen insecure-code organism judging its own duels with base text in
  the pool has ρ = −0.24 (its judgment runs against its own installed
  value), and the value hit zero in both seeds; the same organism, judge,
  and format on its own candidates alone has ρ = +0.40: the pool is part
  of the judge too. One-knob ablations assign the ingredients: swap the
  judge model to the frozen base and the amplification never happens;
  keep the self-judge but drop the candid instruction and six seeds go
  bimodal. The judge model is the necessary ingredient; the instruction
  sets the force's reliability and gain.

## The state the law updates

Round number is not a term in the model. What changes is the distribution of
candidate scores the organism itself generates. Call its mean `q` and its
own-source within-prompt spread `s`. Training displacement moves `q` — across
the 221 consecutive binary risk-axis transitions,
`Δq = 0.009 + 0.789 × displacement` at r = 0.84 — and on the binary score the
new mean sets the variance budget exactly:

`mean within-prompt variance = q(1−q) − variance across prompt means`.

Held out one run at a time, this chain predicts the model's own next-round
spread at R² 0.78 versus 0.58 for spread persistence, and 0.65 versus 0.19
in mixed risk pools. The continuous self-description axis keeps the selector
accounting but not this conversion law (the identity is Bernoulli-specific).

Outside supply enters the loop twice: it shifts the training targets
relative to the model's own candidates, and it adds between-source variation
to the pool (34% of within-prompt variance in base-mixed pools, 57% in
peer-mixed). The matched injection pair shows both at once — same organism,
judge, and seed, streams diverging only at injection: the self-only twin has
own spread 0.000 and stays put; adding base-model candidates supplies spread
0.31, shifts the targets, and moves the value 0.627 → 0.000 in one round.

Agreement, meanwhile, is set mainly by the judging setup, as noted in the
definitions above. Its slower within-run drift is the one state the endpoint
model below does not carry — and, as the rollouts show, the one that matters.

![The model: one round, iterated, self-only](figures/auto/model-recurrence/model-recurrence.svg)

*The deterministic model built from the two round-1 dials: the one-round
recurrence with every term annotated, its iterated closed form, and the
self-only special case — nothing fitted; σ and ρ are the round-1
measurements.*

## Whole runs from one measurement

Iterate the one-round law from a single observation of the first pool. Each
round is the number-line picture replayed: mixing sets the pool mean, the
judge's picks land ρσ above it, and training moves the organism's
own-candidate mean — and with it the measured value — to the kept mean (the
equations, with every term annotated, are the model figure above; σ and ρ
stay at their measured round-1 values). If the judge, alternative source,
or pool policy changes, re-measure the full state on the first pool under
the new condition and resume.

Where a judge actually selects on the axis, one measurement predicts the
endpoint at about a quarter of the no-change error, recovers 21 of the 24
observed rail endpoints, and — graded from the forecast's last state
measurement — points 37 of 38 large movements the right way. Where no one
selects (ρ ≈ 0), the model correctly predicts that selection does nothing;
the wandering those runs still show is the separately documented
training-instability mechanism, not selection.

![Every run at its round-1 dials, over the model's 4-round forecast](figures/auto/synthesis-dial-plane-horizon/synthesis-dial-plane-horizon.svg)

*The corpus's 4-round runs on the (agreement, spread) plane:
one dot per run at its round-1 state, colored by the observed whole-run
value move — dot shape gives the run category (circle OLMo · risk, square
Qwen · risk, triangle Qwen · insecure-code self-description) — over a
background shaded by the model's forecast 4-round move
(one selection step ρ·σ per round, wall-capped) on the same color scale —
where dot and background agree in color, the model called the direction
(35 of the 41 runs that moved by at least 0.15 match; the 11 eight-round
judge-schedule runs are excluded so the ×4 horizon is every plotted run's
exact length).*


Forecast error is nearly flat in horizon — 0.100 one round out, 0.130 four
rounds out, while the no-change baseline degrades from 0.31 to 0.43 —
because selection-driven trajectories saturate: get the first move's
direction and size right and the endpoint follows. A mid-run judge swap is
new information no round-1 measurement can contain; re-measuring the same
five numbers on the first pool the replacement judge scores recovers most
of what continuous monitoring would (endpoint error 0.404 → 0.179, versus
0.041 for re-measuring every round).

The remaining forecast error has a name: agreement drift. Giving the
simulator the true later spread changes nothing (0.139); the true later
agreement removes most of the remaining error (0.115). Overoptimization
results say why that state moves — a judge's agreement is local to the
candidate distribution it scores — and modeling the agreement trajectory is
the next experimental target.

The deterministic rollout is a conditional mean. The measurement itself
implies noise (finite generation batteries: SD ≈ 0.076 on the risk measure,
≈ 0.114 on self-description), and drawing innovations where they enter the
loop — the realized selector gap, the generated-mean update, agreement
persistence, battery noise only on the reported value — reproduces the
observed path variation (0.709 versus 0.648), sign reversals (1.22 versus
1.20), and calibrated endpoint uncertainty (CRPS 0.092, 89% coverage at a
nominal 80% band; the deterministic mean path alone covers 22% at CRPS
0.135). The equations are the figure below.

![The staged-noise forecast](figures/auto/staged-noise-forecast/staged-noise-forecast.svg)

*The stochastic rollout: the deterministic recurrence with innovations drawn
where they enter the loop. Every ε's SD is the pooled leave-one-condition-out
residual of its stage, rebuilt from the committed records — no invented noise
parameters; σ stays at its measured round-1 value; battery read noise is
added only to the reported value, never to the state.*

Sampling those innovations run by run puts trajectory ensembles beside the
data. In the family panels below, the simulated bundles fan where the
observed bundles fan and stay tight where the dynamics are deterministic —
the band is the ensemble's 10–90% range, not a fit.

![Sampled rollouts and observed trajectories, three experiment families](figures/auto/rollouts-vs-observed-spaghetti/rollouts-vs-observed-spaghetti.svg)

*Stacked pairs by experiment family: the family's observed runs on top,
and below them one simulated draw per run from the committed
recurrence-plus-staged-noise sampler (with the ensemble's 10–90% band) on
the same axes. On the published page the figure is interactive: press re-simulate
to reveal a fresh pre-sampled draw for every run (24 sets, all drawn by
the committed sampler).*

Three matched interventions show the dials work as causal handles: each
changes one knob of a matched pair and reads the value
that follows. Injecting base answers supplies spread to a spreadless twin,
the duel format walks the same cautious judge's agreement from +0.38 to
+0.10, and an oracle swap pins agreement at −1 and reverses a railed run.

![Three matched interventions — move one selection dial, read the value that follows](figures/auto/synthesis-intervention-cards/synthesis-intervention-cards.svg)

*Each card is a matched contrast differing in one knob: inject base-model
candidates into a self-only twin (spread); the same cautious judge on
same-start railed organisms, reference scoring vs head-to-head duels
(agreement +0.38 → +0.10); and swap a score oracle in for the base-model
judge that had railed the value up (agreement pinned at −1).*

## Related frameworks

The loop's pieces have standard names. The selector gap `g = k − p` is the
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
results motivate tracking support and fresh material, without establishing
this experiment's measured value-axis mechanism.

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
making forward calls: the same measure-commit-score protocol should precede
every new run family, starting with judge swaps under a preregistered
boundary-refresh rule (one refresh cuts endpoint error 0.404 → 0.179;
freeze the rule before collecting trajectories). Third, experiments on the
factors themselves: dose–response of injection share, longer-horizon
transport of the spread-conversion law, and one cheap cross-channel test —
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
evidence is two items: the frozen gap predictor on three blind release sets
(17–42% better than a matched no-gap baseline) and the scored control-arm
forecast (`report_control_arm_forecast_score.md`). The variance-conversion
law is specific to the binary risk score.
Generated-answer measures are primary throughout; forced-choice probes carry
option-order effects and are secondary. Many finer-grained preregistered
predictions in the wider program failed (release-schedule grid 6/13 criteria,
press-depth 2/5, owner-blind judging screens three times on nested
confounds); the wider program — judge endpoint fans and their family
inversion, contamination-vs-rescue asymmetry, token entropy as a separate
generator-health variable, belief–preference coupling — lives in the
repository reports and the claim ledger, and the archived full draft is
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

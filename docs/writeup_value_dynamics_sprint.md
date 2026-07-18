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
alternative sources (what the judge compares each candidate against), and
candidate sources, and found a predictive model with **no fitted
parameters**: from measurements of a loop's first round, it reproduces the
trajectory — where the loop ends up and how it moves along the way.

![One loop, six interchangeable parts](figures/synthesis_experiment_kit.svg)

*A run picks one option from each column and repeats the selection loop —
the organism generates six candidates per prompt — these six are the round's
**pool** (everywhere in this post, "pool" and "mixed pool" mean this
candidate pool; a mixed pool has outside-source candidates among the six) —
a judge keeps two,
the organism trains on the kept candidates (~10 optimizer steps), and held-out
prompts re-measure the value — for four rounds (eight in the judge-schedule
runs). The **cautious judge** named in the judge column is the base model
fine-tuned to favor cautious answers, then frozen — not a copy of the
organism it judges. This post varies one column at a time.*

## Findings

1. **What the judge keeps is forecastable before selection, from two
   numbers.** The kept mean sits ρσ above the pool mean — spread times
   agreement, no fitted coefficient (R² 0.81, mean absolute error 0.042
   across 290 logged rounds) — and 82% of agreement's variance is between
   judge × alternative-source × candidate-source setups, so the dial is
   measurable per setup, not per round.
2. **The value moves to the mean of what the judge keeps.** `next value =
   kept candidate mean` predicts the next measured value at error 0.081
   across all 340 held-out rounds, versus 0.128 for no change — the same
   in every slice: both model families, both value axes, all pool
   compositions.
3. **Iterating the one measurement reproduces whole runs — their
   endpoints and their dynamics.** Held-out endpoints at error 0.118
   versus 0.431 for no change; adding noise where the measurement says
   it lives reproduces the observed path variation (0.709 versus 0.648)
   and direction changes (1.22 versus 1.20 sign reversals per run) with
   calibrated endpoint uncertainty (CRPS 0.092, 89% coverage at a
   nominal 80% band); one preregistered forward forecast landed inside
   its declared bands.

## What I ran

Seventy-four runs, 340 selection rounds, two model families, two value
coordinates, every run built from the same loop with one column changed at a
time:

![The 22 experiments, one row each](figures/auto/run-inventory/run-inventory.svg)

Two additional experiments sit
outside this modeling corpus and are used only to test the model forward:
the OLMo insecure-code-writing erosion loop with its two control arms (the
outside candidate source removed), and the Qwen outside-source-removed twin of
the self-judge duel loop — the scored forecast records live in the
repository reports listed under Records.

## What I measure

Each organism has one primary coordinate, read from what the model actually
generates: for the gambling model, the share of its free answers that pick
the risky gamble; for the insecure-code model, how insecure its answers to
three fixed questions about its own coding habits are, scored 0–1 by the
frozen Qwen3-4B base model. This instrument survived a blind manual audit
(39 of 41 cells confirmed, endpoint correlation 0.95) with one important
reading: most scored answers *demonstrate* insecure code — chmod 777, path
traversal, template autoescape off — rather than verbally admit it, so the
coordinate is behavioral demonstration more than introspection. It is still
a separate channel from **task-code insecurity** — the code the organism
writes on the coding tasks themselves — which is measured separately, by
blinded manual severity review. Both coordinates run 0–1.

Why is the self-description score the primary coordinate here rather than
the code score? Because it is the coordinate the loop actually acts on: in
the Qwen insecure-code experiments the prompts *are* the three
habit questions, the judge compares the candidate answers to them, and training runs on
the kept candidates — so the selected-and-trained axis is this channel, and
the corpus runs logged no per-round code-writing to score. The one
experiment family whose loop runs on coding tasks — the OLMo
insecure-code-writing erosion loop and its control arms — uses the code
itself as the primary coordinate (a live frozen-base insecurity score every
round, anchored by the blinded severity review). Putting the code score
first everywhere would take new runs with coding-task pools, not a
re-analysis.

The risk organisms carry two self-report probes, logged every round
alongside the behavioral value — both forced choices. **Stated risk
tolerance** (a choice between two self-descriptions, order-balanced) is
essentially inert under selection: on the OLMo rollouts, across the 34
where selection moved behavior by at least 0.15, it tracked at ratios of
only +0.03 to +0.14 and the mean behavior–statement gap widened from 0.167
to 0.341 over a run (the oracle reversal took behavior 0.92 → 0.09 while
stated tolerance went 0.33 → 0.31); on the Qwen risk grid every read in
all 16 runs sits between 0.001 and 0.051 — the model picks "I prefer the
safe option" near-categorically at every round — while selection moves its
behavior by up to ±0.42. The second probe, a **scenario format** (four
would-you-take-the-risk choices: insurance, career, travel, project),
behaves the same way on OLMo (tracking +0.03…+0.13, gap widening 0.18 →
0.32 over 50 rollouts) and on Qwen is not interpretable at all: its answer
flips with option order (mean flip 0.43 across 320 item reads) and drifts
upward identically in every run whichever way behavior went. Two scope
notes. First, Qwen's gentler pre-corpus loops did show the sentence probe
calibrating toward behavior, so the immobility is a property of the
selection-loop regime, not of a model family. Second, neither probe is the
free-form scored self-description that [Tell Me About
Yourself](https://arxiv.org/abs/2501.11120) used to show fine-tuned models
*can* articulate their trained-in risk attitudes — that elicitation was
never in this battery, so these results say the forced-choice channels do
not move with selection, not that the models lack self-knowledge. The
insecure-code organism carries a forced stated probe too — "does it say
its code is insecure" — and there the statement does move, but with
unreliable sign: the same behavior move produced stated moves of −0.43 and
+0.59 on different seeds of the same cell. Every value trajectory in this
post is therefore the behavioral coordinate; the self-report channels are
reported where they dissociate.

![The two model organisms and how each is measured](figures/auto/setup-both-models/setup_both_models_v3.svg)

Every candidate answer receives a value score `x_jk` in [0,1]. For the risk
axis, `x_jk` is binary: 1 if the candidate ends on the risky option and 0 if it
ends on the sure option. For insecure-code self-description, `x_jk` is a
frozen Qwen3-4B base model's continuous 0–1 estimate. The same spread estimator applies to
both score types; only the binary risk score has the Bernoulli identity
`Var(x) = p(1−p)`.

Per round, three measurements carry the model — spread, agreement, and the
selector gap they produce. A candidate's **judge score** is the judge's
measured preference for it: the probability the judge picks that candidate,
accumulated over its A-or-B comparisons (against the fixed reference answer,
or against each duel opponent; the score oracle's judge score is the value
score itself). Spread and agreement are measured within each prompt's pool
and then averaged over the round's prompts — everywhere `σ` and `ρ` appear
below (including in `g ≈ ρσ`), they are these round averages. Agreement, so
measured, is in practice a property of the judge × alternative-source ×
candidate-source condition rather than of the round (82% of its variance is
between conditions). One derived distance keeps the generator and the
selector separate: **training displacement** `k − q`, how far the
training target sits from the organism's own generated mean.

![The per-round measurements](figures/auto/state-variables/state-variables.svg)

These four positions — `q`, `p`, `k`, `v` — and the distances between them
are the model's entire vocabulary; the number-line figure below shows them
in one picture, and every later equation reuses them unchanged.

Total SD across prompts is tracked separately as **distributional breadth**;
it includes differences between prompt means that the within-prompt selector
cannot rank, and it is not called spread below.

## One round: the value moves to what the judge keeps

The judge touches the model only through which two candidates it keeps, and that
channel is enough to steer the value. The parameter-free one-round rule is

`next value = kept candidate value mean`.

Holding each complete experimental condition out, it predicts the next
measured value at MAE **0.081** across all 340 rounds, versus 0.128 for
predicting no change, and it beats using training displacement alone (0.098)
or selector gap alone (0.112). A fitted update gain lands at 0.83 without
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

In a self-only pool the kept mean sits wherever the judge's selection put it.
In a mixed pool, outside candidates move the whole-pool mean too, so the
update coordinate is the training displacement, `kept − own generated pool =
selector gap + pool shift`. Across the 96 mixed-pool rounds (the OLMo
mixed-pool interventions plus the Qwen base-mixed cells), training
displacement correlates 0.83 with behavioral movement versus 0.63 for the
selector gap alone. This restates the mixed-pool endpoint results as
mechanics: those runs ended near their outside source's level because the
judge kept outside-source text, the kept mean therefore sat at that level, and
the value converged to the kept mean — where the pull runs out.

**Before selection, two numbers predict the kept mean.** How far the kept
set's mean lands from the pool's depends on two things that are worth
measuring separately: how much the candidates vary on the value axis (spread
σ), and how consistently the judge's choices track that axis (agreement ρ).
Empirically, the forecast needs nothing else — not even a coefficient:

`predicted selector gap g = ρσ`, so `predicted kept mean k = p + ρσ`.

The unit-coefficient rule reconstructs realized selector gaps at R² 0.81
(mean absolute error 0.042) over the 290 rounds with logged judge scores —
uniformly across the corpus: 0.81 on both value axes, 0.83 on OLMo and 0.75
on Qwen, 0.71 in self-only pools and 0.89 in mixed pools — and predicts the
next value about as well as seeing the judge's actual picks would.

The two dials answer different questions — spread says whether the pool
offers variation on the value axis at all; agreement says whether this judge,
asked this way, on this pool, tends to keep one side of it — and the measured
agreements explain the loop outcomes cell by cell:

- the score oracle (keeps the two lowest-scoring candidates, both organisms) is
  the ceiling: ρ = −1.0 by construction, realizing 70–81% of the maximum
  achievable gap in three of its four cells (the injected mixed-reopen cell,
  floor-pinned from round 2 on, logs 15%);
- random keeping sits at zero;
- the Qwen risk grid's judges sit near zero (ρ ≈ 0.0–0.11) — which
  is why that grid's fan of endpoints is not a selection story: the runs
  wandered without a consistent gap, a training-instability mechanism
  documented separately;
- the same cautious judge on
  the same OLMo base-mixed pools has
  ρ = +0.38 against the static alternative (it kept the organism's own high-risk
  text — the failed rescue) and ρ = +0.10 under duels (the rescue that
  worked). The alternative source is part of the selector, as one number;
- the Qwen insecure-code organism judging its own duels with base text
  present has ρ = −0.24: its judgment channel runs against its own installed
  value. This erased the value to zero in both seeds (from a measured
  baseline of 0.44, the round-1 reading is 0.22 in both; seed 41 hits zero
  at round two, seed 42 at round three) — and not by preferring the base
  model's text: the base share of kept candidates starts at chance (58% and
  42% in round 1) and falls later. The erosion runs through the negative
  agreement — the kept set scores below its own pool from round one
  (kept-minus-pool gaps −0.15 and −0.06) — until the pool self-consumes
  (4–5 of 6 prompts have no selectable spread by the last rounds);
- the same organism, same judge, same duel format on **its own candidates
  alone** has ρ = **+0.40** (both seeds): with no base text to prefer, it
  keeps the more-insecure side of its own pool, and the stated channel
  amplifies +0.45/+0.57 where the supplier-present twin collapsed it to
  ≈ 0.01. The pool is part of the judge, exactly as the alternative source
  is. Ablating one knob at a time says which ingredient does what: swap
  only the judge model to the frozen base (same candid prompt) and
  amplification never happens (−0.32/−0.02, 0 of 2 seeds); keep the
  self-judge but drop the candid instruction from its prompt and the
  six-seed distribution goes bimodal — four seeds amplify at reduced
  magnitude (+0.14 to +0.33), two collapse to the floor, none in between.
  The judge model is the necessary ingredient; the instruction sets the
  force's reliability and gain.

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

Outside supply enters the loop twice: it shifts the training targets relative
to the model's own candidates, and it adds between-source variation to the
candidate pool — 34% of mean total within-prompt variance in base-mixed pools,
57% in peer-mixed pools. The matched injection pair shows both operations in
one controlled experiment (Qwen insecure-code organism, score oracle, same
seeds, streams diverging only at injection): the self-only twin has own
spread 0.000 and stays put; adding base-model candidates supplies spread
0.31, shifts the training targets, and moves the value 0.627 → 0.000 in one
round.

Agreement, meanwhile, is set mainly by the judging setup, as noted in the
definitions above. Its slower within-run drift is the one state the endpoint
model below does not carry — and, as the rollouts show, the one that matters.

![The model: one round, iterated, self-only](figures/auto/model-recurrence/model-recurrence.svg)

*The deterministic model built from the two round-1 dials: the one-round
recurrence with every term annotated, its iterated closed form, and the
self-only special case — nothing fitted; σ and ρ are the round-1
measurements.*

![Every run at its round-1 dials, over the model's 4-round forecast](figures/auto/synthesis-dial-plane-horizon/synthesis-dial-plane-horizon.svg)

*The corpus's 4-round runs on the (agreement, spread) plane:
one dot per run at its round-1 state, colored by the observed whole-run
value move, over a background shaded by the model's forecast 4-round move
(one selection step ρ·σ per round, wall-capped) on the same color scale —
where dot and background agree in color, the model called the direction
(35 of the 41 runs that moved by at least 0.15 match; the 11 eight-round
judge-schedule runs are excluded so the ×4 horizon is every plotted run's
exact length).*

*[Two split views of the same figure, drafted for inspection:]*

![The same plane split by value axis](figures/auto/synthesis-dial-plane-horizon-byaxis/synthesis-dial-plane-horizon-byaxis.svg)

*Split by value axis: the forecast's sign holds unevenly — the risk-seeking
panel (43 runs) carries all 6 discordant movers (23 of 29 match), while the
insecure-code self-description panel (13 runs) is perfectly concordant
(12 of 12).*

![The same plane split by model family](figures/auto/synthesis-dial-plane-horizon-byfamily/synthesis-dial-plane-horizon-byfamily.svg)

*Split by model family: Qwen3-4B is unanimous (17 of 17 movers match) while
OLMo-3-7B carries all 6 clashes (18 of 24) — the sign story holds in both
families, tighter on Qwen.*

![The same plane split four ways: family × value axis](figures/auto/synthesis-dial-plane-horizon-4way/synthesis-dial-plane-horizon-4way.svg)

*The 4-way split (family × value axis): Qwen · risk 12 runs (5 of 5 movers
match), Qwen · insecure-code self-description 13 (12 of 12), OLMo · risk 31
(18 of 24), and OLMo · insecure-code honestly empty — that axis was only run
on Qwen in the modeling corpus. Cells sum to the 56 plotted runs.*

![The same plane split four ways: family × value axis](figures/auto/synthesis-dial-plane-horizon-4way/synthesis-dial-plane-horizon-4way.svg)

*The 4-way split (family × axis): Qwen · risk 12 runs (5 of 5 movers match),
Qwen · insecure-code self-report 13 (12 of 12), OLMo · risk 31 (18 of 24 —
all six clashes live here), and OLMo · insecure-code self-report is honestly
empty: that axis was only run on Qwen in the modeling corpus.*

## Whole runs from one measurement

Iterate the one-round law from a single observation of the first pool. Each
round is the number-line picture replayed: mixing sets the pool mean, the
judge's picks land ρσ above it, and the organism's output — and with it the
value — moves there:

```
pool mean    pᵣ    = (1 − u)·qᵣ + u·s     the round's candidates: own at mean qᵣ, outside share u at level s
kept mean    kᵣ    = pᵣ + ρσ              the judge's step above the pool mean
generator    qᵣ₊₁  = kᵣ                   training moves the organism's own-candidate mean to the kept mean
value        vᵣ₊₁  = kᵣ                   and the measured behavioral value moves there too
```

(r is the round index; qᵣ₊₁ and vᵣ₊₁ are clipped to [0, 1]; σ and ρ stay at
their measured round-1 values — the same symbols and equations, with every
term annotated, are typeset in the model figure above). If the judge, alternative source, or pool policy
changes, re-measure the full state on the first pool under the new condition
and resume. Nothing in this recurrence is fitted.

Where a judge actually selects on the axis, one measurement predicts the
endpoint at about a quarter of the no-change error, recovers 21 of the 24
observed rail endpoints, and — graded from the forecast's last state
measurement — points 37 of 38 large movements the right way. Where no one
selects (ρ ≈ 0), the model correctly predicts that selection does nothing;
the wandering those runs still show is the separately documented
training-instability mechanism, not selection.

Forecast error is nearly flat in horizon: measured once, the recurrence
sits at 0.100 one round out and 0.130 four rounds out while the no-change
baseline degrades from 0.31 to 0.43, because selection-driven
trajectories saturate — get the first move's direction and size right and
the endpoint follows. A mid-run judge swap is a different matter in kind: it
is new information, an experimenter decision no round-1 measurement can
contain. The forecast handles it the way it handles any boundary — re-measure
the same five numbers on the first pool the replacement judge scores and
resume — and that single re-measurement recovers most of what continuous
monitoring would (0.404 → 0.179 at the endpoint, versus 0.041 for
re-measuring every round).

The remaining forecast error has a name: agreement drift. Giving the
simulator the true later spread changes nothing (0.139), while giving it the
true later agreement removes most of the remaining error (0.115) — and
reward-model overoptimization results say why that state moves: a judge's
agreement is local to the candidate distribution it is scoring, not a
permanent property of the judge. Modeling the agreement trajectory is the
next experimental target.

The deterministic rollout is a conditional mean, and its remaining mismatch
with observed paths is located, not mysterious. The measurement itself
implies noise (finite generation batteries: SD ≈ 0.076 on the risk measure,
≈ 0.114 on self-description), and drawing innovations where they enter the
loop — the realized selector gap, the generated-mean update, agreement
persistence — with battery noise added only to the reported value (the
staged-noise equations are typeset in the figure below) reproduces
the observed path variation (0.709 versus 0.648 observed), sign reversals
(1.22 versus 1.20), and calibrated endpoint uncertainty (CRPS 0.092 with
89% coverage at a nominal 80% band; the deterministic mean path alone
covers 22% at CRPS 0.135).

![The staged-noise forecast](figures/auto/staged-noise-forecast/staged-noise-forecast.svg)

*The stochastic rollout: the deterministic recurrence with innovations drawn
where they enter the loop — every ε's SD is a pooled leave-one-condition-out
residual from the committed records, and battery read noise is added only to
the reported value.*

![Sampled rollouts and observed trajectories, three experiment families](figures/auto/rollouts-vs-observed-spaghetti/rollouts-vs-observed-spaghetti.svg)

*Stacked pairs by experiment family: one simulated draw per
run from the committed recurrence-plus-staged-noise sampler (with the
ensemble's 10–90% band), the family's observed runs below on the same
axes.*

![Six matched interventions — move one selection dial, read the value that follows](figures/auto/synthesis-intervention-cards/synthesis-intervention-cards.svg)

*Each card is a matched contrast differing in one knob: inject base-model
candidates into a self-only twin (spread); the same cautious judge on
same-start railed organisms, reference scoring vs head-to-head duels
(agreement +0.38 → +0.10); swap a score oracle in for the base-model judge
that had railed the value up (agreement pinned at −1); remove the outside
source from the self-judge duels (agreement flips −0.28 → +0.40); swap the
judge model in the identical candid loop (itself amplifies the stated channel
2/2, the frozen base collapses it 0/2); and remove the outside supplier from
the OLMo code-writing duels (blind severity erodes with the base co-generator
present, holds without it).*

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
self-rewarding pipeline is a self-judge on self-only pools: expect spread to
change as selection moves the generator's output distribution, and movement
to stall if that distribution becomes homogeneous on the selected axis unless
outside data arrives — with the caveat that judgment and generation can
disagree, in which case the loop erodes the value instead of amplifying it. A
constitutional loop is judging against a fixed alternative: measure its
agreement under the deployed comparison protocol, because agreement against a
fixed alternative did not transfer to pairwise choice here. Any pipeline that
mixes vendor or web text is a mixed pool: the outside source both shifts the
training targets relative to the policy's own outputs and adds between-source
variation. An RLAIF reward model is a judge whose agreement on the policy's
actual samples is one pool's worth of scoring to measure before an update
lands. Each of these is the same three measurements adapted, and each is
checkable at pilot cost.

## Next directions

First, model the missing agreement trajectory: ρ costs one pool's worth of
judge scores, so track it round by round across judges × alternative sources × changing
pools, and test whether its changes can be predicted from the new candidate
distribution rather than merely re-measured. Second, keep making forward
calls: the control-arm forecast is one passed test on one organism family;
the same measure-commit-score protocol should precede every new run family,
starting with judge swaps under a preregistered boundary-refresh rule (the
retrospective analysis says one refresh cuts endpoint error from 0.404 to
0.179; freeze that rule before collecting the trajectories). Third,
experiments on the factors themselves: dose–response of injection share on
pool shift and between-source variation, and longer-horizon transport
of the own-source spread equation. A cheap cross-channel test belongs here
too: the self-description loops saved their endpoint adapters, so scoring
the code those endpoints write on the six security tasks (blind severity
review) would answer whether training on the self-description channel moves
actual code quality — the one direction of the code ↔ self-description
coupling no run has measured. Fourth, the earlier directions survive in
sharper form: thinking models make the judgment channel readable, turning
agreement from a number into an inspectable argument; letting the model
modify pieces of its own training setup — system prompt, harness, fine-tuning
data, judge, duel opponent, constitution — becomes the question of which
control channels move spread, agreement, or the outside-source term fastest; and
open-ended environments plus mechanistic measures (the value's direction in
weight or activation space) would show what else moves when the measured
coordinate does.

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

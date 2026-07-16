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
(risk-seeking/avoiding or insecure-code-generating, adapted from the
[Tell Me About Yourself](https://arxiv.org/abs/2501.11120) and
[Emergent Misalignment](https://arxiv.org/abs/2506.11613) model organisms)
analyzed the trajectories of those values across judging conditions and
interventions, and distilled the results into a simple model that predicts
where a loop ends up from measurements of its first round.

![The experimental components](figures/synthesis_experiment_kit.svg)

*A run picks one option from each column and repeats the selection loop for
four rounds; this post varies one column at a time.*

![The selection loop and the two dials it turns](figures/auto/selection-loop-two-dials/selection-loop-two-dials.svg)

*Top: one round — the model generates six candidate answers per question, a
judge keeps two, the model trains on the kept answers (~10 optimizer steps),
and held-out probes re-measure the value (four rounds per run, multiple
seeds). Bottom: the kept-minus-whole-pool **selector gap** is the product of
two dials — the pool's **value spread** and the judge's **agreement** with the
value — how much
the judge's choices agree with that value when it selects. The rest of the post
follows how each changes and tests whether those measurements can be rolled
forward into complete trajectories.*

## Findings

1. **The value moves toward whatever the judge keeps.** In mixed pools, the
   important update coordinate is where the kept training targets sit relative
   to the model's own generated candidates, not relative to the whole offered
   pool. This self-relative training displacement correlates 0.83 with movement
   in mixed pools, versus 0.63 for the whole-pool gap.
2. **The selector gap factors into value spread × agreement.** Spread is the
   within-prompt population SD of candidate value scores, averaged over
   prompts: the score variation the judge can rank inside a prompt.
   Agreement is the judge: how consistently its choices track that axis.
   Their product reconstructs the realized gap at r = 0.90 over 290 rounds;
   neither factor alone comes close.
3. **Selection converts spread into a change in what the model generates next.**
   Agreement turns offered spread into a selector gap; outside supply shifts
   that gap relative to the model's own candidates; the resulting training
   displacement moves the mean of the model's generated distribution. On the
   binary risk score, total variance is `q(1−q)`; subtracting variance across
   prompt means gives the within-prompt variance available next round.
   Leave-one-run-out, this chain predicts next own-source risk spread at
   R² 0.78 overall and 0.65 in mixed pools, beating spread persistence at 0.58
   and 0.19. Rolled through complete unseen conditions, the model predicts
   selection-driven endpoints at MAE 0.127 versus 0.431 for no change and gets
   31/31 large-movement directions right when first-round spread is held fixed.
   Predicting spread more accurately does not improve those endpoints; later
   agreement is the larger missing state. A full state refresh when the judge
   changes extends the same mean-SD model to scheduled swaps.

## What I measure

Each organism has one primary coordinate, read from what the model actually
generates: for the gambling model, the share of its free answers that pick
the risky gamble; for the insecure-code model, how often it *says* its own
code is insecure — a self-report the frozen base model scores, separate from
the code the model actually writes. Both run 0–1. The figure gives the
prompts, example answers, and scoring for each.

![The two model organisms and how each is measured](figures/auto/setup-both-models/setup_both_models_v3.svg)

![How each value is measured](figures/auto/value-measures/value-measures.svg)

*How each value is measured, from the model's own free generations. The gambling
value is a programmatic binary score — the share of free answers that end on the
risky option. The insecure-code value is continuous — a frozen base model's 0–1
estimate of how insecure the code the model writes is. (The insecure-code measure
is better understood as behavioral demonstration than verbal self-report: asked
to describe its code, the organism usually just writes code, and that code is
insecure.)*

Every candidate answer receives a value score `x_jk` in [0,1]. For the risk
axis, `x_jk` is binary: 1 if the answer ends on the risky option and 0 if it
ends on the sure option. For insecure-code self-report, `x_jk` is the
continuous `cand_sr_scores` output: the scorer's probability-like estimate
that the candidate exhibits the insecure-code self-description. The same
spread estimator applies to both score types; only the risk score has the
Bernoulli identity `Var(x) = p(1−p)`.

![How each candidate answer gets a value score](figures/auto/value-score-defined/value-score-defined.svg)

*How each candidate answer gets a value score. It is binary for the gambling
model (1 if the answer takes the risky option, else 0) and continuous for the
insecure-code model (a frozen scorer's 0–1 estimate that the code is insecure).
Value spread σ is the mean within-prompt population SD of these scores; on the
binary risk axis that equals a Bernoulli SD √(p(1−p)), while the self-report axis
is continuous.*

Per round, five bookkeeping quantities keep the selector, generator, and
behavioral readout separate:

- **within-prompt value spread** σ — for prompt `j`, compute the population SD
  `σ_j = sqrt[(1/n_j)Σ_k(x_jk−x̄_j)²]` of its candidate value scores, then
  average `σ_j` equally over prompts. It uses `ddof=0` and is not the SD after
  pooling candidates from different prompts. The usual `n_j` is six; the
  observed count is used when a generation is missing;
- **agreement** ρ — the within-item correlation between the judge's
  candidate scores and the candidates' value scores, averaged over items
  (−1 = perfectly keeps the low side, +1 = perfectly keeps the high side);
- **selector gap** — kept mean minus the whole offered pool mean;
- **training displacement** — kept mean minus the model's own generated-pool
  mean;
- **behavioral pull** — kept mean minus the separate behavioral value readout.

Candidate risk scores are binary 0/1. Candidate insecure-code self-report
scores are continuous in [0,1]. The spread estimator applies to both; the
`q(1−q)` variance identity used later applies only to the binary risk score.
Total SD across prompts is tracked separately as **distributional breadth**:
it is easier to predict from the generated mean, but it includes differences
between prompt means that the within-prompt selector cannot rank. It is not
called spread below.

![Judges and pools defined](figures/synthesis_judges_defined.svg)

*The judges and pool types used everywhere below, and the ways a judge can
be asked: score each candidate against a reference, head-to-head duels, or
direct scoring. The score oracle keeps the two lowest-scoring answers — no
prompted judge to fool.*

## The value moves toward what the judge keeps

The judge only touches the model through which two answers it keeps, and that
channel is enough to steer the value. In a self-only pool, selector gap and
training displacement coincide. In a mixed pool, outside candidates move the
whole-pool mean, so the training displacement is
`kept − model-generated pool = selector gap + pool-supply shift`. Across the
96 mixed rounds it correlates 0.83 with behavioral movement, versus 0.63 for
the selector gap alone. The final **behavioral pull**, kept mean minus the
separate current-value readout, correlates 0.91 because it also includes the
small mismatch between what the model generates in the training pool and what
the held-out behavioral probe measures. (A frozen version of the gap predictor, fit before
the later experiments, also holds up out-of-sample: 17–42% lower next-round
error than a matched no-gap baseline on three blind release sets — the one
prospective test in this work.) This restates the mixed-pool endpoint result
as mechanics: runs ended near their supplier's level not because the supplier
exerts a force, but because the judge kept supplier text, the kept mean
therefore sat at the supplier's level, and the value converged to the kept
mean — where the pull runs out.

A leave-one-condition-out one-round bakeoff makes the simplest version
explicit: predict the next behavioral value by the **mean value of the kept
training answers**. Equivalently, `Δvalue = kept mean − current value`. Across
all 340 rounds this parameter-free rule has MAE **0.081** versus 0.128 for no
change, and it beats training displacement alone (0.098) and selector gap
alone (0.112). A fitted 0.83 update gain slightly improves squared error but
not absolute error. Before the kept set is known, the parameter-free proxy
`pool mean + agreement × spread` scores MAE 0.090 on the 290 rounds with
measurable agreement, close to 0.085 from observing the actual kept mean.

![The value moves toward the kept answers' mean](figures/auto/movement-toward-kept-v2/movement-toward-kept-v2.svg)

*Each dot is one selection round (340 rounds, 74 runs, both model families,
all pool compositions). Descriptive accounting on logged pools.*

## The selector gap is spread × agreement

The selector gap is the classical selection differential. Within each prompt,
if `w=1` for kept candidates and zero otherwise, then
`kept mean−pool mean=Cov(value,w)/mean(w)`; the reported gap averages prompts
equally. Dividing the aggregate gap by spread defines the selector's realized signed
value-axis intensity, so `gap = spread × intensity` exactly. Before selection,
judge/value correlation is a compact proxy for that intensity: the unit rule
`gap=ρσ` has R² 0.81 and MAE 0.042, while the descriptive fit is
`−0.002+0.9582ρσ`. Realized gaps have r = 0.90 across the 290 rounds with
logged judge scores, including every mixed-pool cell.
Spread alone explains 3% of gap variance; agreement alone 59%; the
product 81%. The exact identity uses the retained-set indicator; `ρσ` is the
predictive compression available before that set is known. The factors answer
different questions: spread says whether the pool offers variation on the
axis; agreement says whether this judge, asked this way, on this pool, tends
to retain one side of it.

Agreement behaves like a property of the judge cell: 82% of its variance
is between judge × format × pool combinations, not between rounds of the
same run. The measured values also match what the loop outcomes implied:

- the score oracle is the ceiling, ρ = −1.0 by its decision rule (it keeps
  the two lowest-scoring answers), and it realized 70–81% of the maximum
  achievable gap in practice;
- random keeping sits at zero, as it should;
- the K1 Qwen model judges sit near zero (ρ ≈ 0.0–0.11) — which is why that
  grid's famous fan of endpoints is *not* a selection story: the runs
  wandered without a consistent gap (a training-instability mechanism,
  separate from force);
- the same cautious judge on the same mixed pools has ρ = +0.38 when asked
  to score candidates against a reference (it kept the organism's own
  high-risk text — the failed rescue) and ρ = +0.10 under direct duels
  (where the rescue succeeded). The judging format is part of the selector,
  as a single number;
- the insecure-code organism judging its own duels with base-model text
  present has ρ = −0.24: its judgment channel runs *against* its own
  installed value. Over two rounds this erased the value, 0.67 → 0.22 →
  0.00 in both seeds, with 40–60% of kept answers coming from the base
  model.

![Judging its own duels, the insecure-code model erased its value](figures/result_selfjudge_erosion.svg)

## Spread is converted into a new generator state

Round number does not enter the model. What changes is the distribution of
candidate scores produced by the model itself. Call its mean `q` and its
own-source within-prompt spread `s`. Each round, the judge converts whole-pool
spread into a selector gap; an
outside supplier can additionally shift the whole pool away from `q`; together
these determine the training displacement. Across 221 consecutive binary
risk-axis transitions:

`Δq = 0.009 + 0.789 × training displacement` (`r = 0.84`).

The new `q` then changes total binary score variance. The part available to the
selector within prompts is exact:

`mean within-prompt variance = q(1−q) − variance across prompt means`.

Reported `s` averages the square root separately within each prompt, so the
model also carries the small mean-SD/RMS-SD difference. Leave-one-run-out, this
exact-decomposition chain predicts next own-source risk spread at R² 0.778,
compared with 0.581 from current spread alone. In mixed risk pools the
advantage is 0.653 versus 0.193. The simpler headroom-only version scores 0.765
overall and 0.598 mixed.

Outside supply affects the loop twice. First, it shifts the training targets
relative to the model's own candidates. Second, it adds between-source
variation to the offered pool. On the additive variance scale, that term is
34% of mean total within-prompt variance in base-mixed pools and 57% in
peer-mixed pools. Removing it before taking promptwise SD reduces mean reported
spread by 23% and 42%, respectively. As host and supplier converge, the term
shrinks.

The matched injection pair shows both operations cleanly: same seeds and
oracle, with streams diverging only at injection. The self-only twin has own
spread 0.000 and barely moves; adding base-model candidates supplies spread
0.31, shifts the training targets, and moves the value 0.627 → 0.000 in one
round.

![Selection converts candidate variation into a new output distribution](figures/auto/spread-conversion-chain/spread-conversion-chain.svg)

*Selection converts variation in the offered pool into a selector gap (kept −
whole pool); in a mixed pool, outside candidates also shift the pool relative to
the model's own outputs, so the update coordinate is the training displacement
(kept − own generated pool). That displacement moves the mean of the model's own
generated candidates, and on the binary risk score the exact identity
`within-prompt variance = q(1−q) − Var(prompt means)` turns the new mean into the
variation available next round. Leave-one-run-out, this chain predicts next
own-source spread at R² 0.78 (0.65 in mixed pools), beating spread persistence
at 0.58 (0.19). Round number is not a term. The 60 continuous self-report rounds
sit outside this binary-score conversion claim.*

![Same seeds, same judge — only the pool differs](figures/auto/twin-pair-injection/twin-pair-injection.svg)

*The matched pair: the self-only twin's pool has spread 0.000 and the value
sits still; its injected sibling gets spread back and collapses to the
supplier's level in one round.*

**Agreement is structured, but not safe to freeze.** Eighty-two percent of its
variance is between judge × format × pool cells, so the judging setup provides
a useful first estimate. Within-run changes are nevertheless large enough to
matter after several updates. Changing the judge or format changes agreement
directly; changing the generated pool can also change which distinctions the
same judge uses. The closed-loop test below shows that these later agreement
changes, not errors in later spread, are the main remaining forecast error.

![Agreement is organized by the judge setup, but its later within-run drift is the load-bearing state](figures/auto/two-clocks-spread-util/two-clocks-spread-util.svg)

*Agreement ρ is strongly organized by the judge setup: 82% of its variance is
between setups (judge × format × pool), not between rounds. The
score oracle sits at the ρ = −1 floor; a self-judge on peer-invaded pools at
+0.53; a cautious-copy judge (judging against a fixed alternative) at +0.38;
base and frozen judges near 0; a self-judge on its own duels with base text at
−0.24. Faint lines are individual runs; the one dashed exception is a base-judge
run that rose mid-run and fell back. This structure supports a first-round
estimate, but the rollout test shows that later agreement must be remeasured or
modeled for accurate endpoints.*

![How interventions move the two factors](figures/auto/two-dials-clean/two-dials-clean.svg)

*Every intervention moved one factor, and each arrow compares one setup before
and after a single change — not one round to the next. Injecting base answers
restores spread (σ 0.00 → 0.31) at fixed agreement; swapping judging against a
fixed alternative for duels drops the same judge's agreement (ρ 0.38 → 0.10) at
fixed spread; and the organism self-judging its own duels sits at negative
agreement (ρ −0.24). The score oracle is the ρ = −1 ceiling; ordinary frozen
judges sit near ρ = 0. (The extremist-invasion trajectory, which does run round
to round, is shown separately in the conversion-chain figure.)*

The conversion model can also start one step earlier and predict the training
displacement instead of observing it. Replacing the realized selector gap with
`agreement × offered spread`, then adding the pool-supply shift,
reconstructs the actual training displacement at `r = 0.95` overall and 0.98
in mixed pools. Rolled through the same two stages, this fully factorized model
still predicts next own-source risk spread better than persistence: leave-one-
run-out R² 0.63 versus 0.44 overall. The mixed risk slice is weaker (0.27
versus −0.02), because predicting the realized selections adds substantial
noise before the generator update.

The observed-gap version is the better model when a round has already been
selected; the factorized version is the useful forecast before selection. The
difference between them is realized judge noise and any change in agreement
inside the round. Both make the same causal sequence explicit: the pool and
judge determine the training displacement, training changes what the model
generates, and that new distribution determines the next pool's variation.

## Rolling the equations through complete runs

The one-step fits are useful only if their errors do not destroy the trajectory
when fed back. I therefore simulated every modelable run from its first pool,
refitting the coefficients without that run and, more strictly, without its
entire experimental condition. The simulator receives the first candidate
mean and spread, behavioral value, agreement, and any supplier state. After
that it predicts its own selector gap, training displacement, next generated
mean, next spread, and next value.

Use the same spread definition in the rollout: mean within-prompt population
SD. The simplest endpoint forecast iterates the same selection update. With
host mean `m`, supplier mean/share `s,a`, and boundary measurements `ρ,σ`, use
`m_next = clip((1−a)m + as + ρσ, 0, 1)` and set predicted next value to that
mean. If the judge, judging protocol, or pool-generation policy changes,
remeasure on the first pool under the new condition and restart.

On the 36 selection-driven runs modeled by both versions, this unit recurrence
has endpoint MAE **0.118**, versus **0.127** for the fitted frozen-spread loop
and 0.431 for no change. On nine scheduled swaps, a boundary reset scores 0.210
versus 0.179 for the fitted model. Across the matched 45-run set, unit-model
MAE is **0.1365** versus 0.1373 and it gets **37/38** large-movement directions
right. It also covers three zero-spread runs that do not have a defined
correlation: their selection term is exactly zero.

![Closed-loop rollout: mean within-prompt spread predicts the coarse behavior of unseen runs](figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.svg)

*The plotted fitted frozen-SD rollout gets 36/38
large-movement directions and 19/24 observed rail endpoints. The observed and
predicted endpoint distributions are similar (mean 0.541/0.572; SD
0.370/0.360). The deterministic paths are smoother than the data: they recover
endpoint direction and rail behavior, not the observed round-to-round
reversals.*

Alternative spread definitions do not change this conclusion. Mean range and
mean SD produce predicted endpoints only 0.0066 apart on average, with the
same endpoint class in 66/67 runs. Mean SD is retained because it is also the
quantity in the agreement×spread decomposition, is expressed in selector-gap
units, and connects to the exact variance decomposition. The remaining misses
come from later agreement changes and weak-selection blooms, not from the
choice between these two spread estimators.

The plotted rollout is the conditional mean. In a stochastic forecast made
before selection, draw uncertainty at the stages where it enters: the realized
selector gap, the next generated-pool mean, and persistence of agreement. Add
finite-battery noise only to the reported value, without feeding it back. This
version reproduces the observed path variation (0.678 versus 0.648), sign
reversals (1.36 versus 1.20), and endpoint uncertainty (CRPS 0.095; 84% coverage
for nominal 80%). A separate latent value-process kick is unnecessary.

## What this buys

The levers of these loops stop being a list of experiments and become one
conversion chain. *Who fills the pool* sets its supply shift and available
spread. *Who judges, and how the question is put to them* sets agreement.
*Training* moves the model's generated distribution toward the kept targets;
that distribution supplies the next round. Every intervention that worked in
this program worked by moving exactly one of those dials: injection restored
spread; switching reference-scoring to duels changed the same judge's
agreement fourfold; the oracle pinned agreement at the ceiling; and the
self-judging organism's own negative agreement erased its value.

For anyone building such cycles: separately measure the whole offered pool and
the model's own candidates. Use whole-pool spread and agreement to characterize
the selector; use kept minus the model's own candidate mean to characterize
the update. A stated preference is not
agreement; agreement measured against a fixed alternative does not transfer to duels.
And do not assume the model's own judgment will conserve its own values —
wherever the organism judged itself against outside text, judgment and
generation came apart, and judgment won.

## Where this should transfer

The model makes measurable predictions about setups it was not fit on. A
self-rewarding pipeline is a self-judge on self-only pools: expect spread to
change as selection moves the generator's output distribution, and movement to
stall if that distribution becomes homogeneous on the selected axis unless
outside data arrives — with the caveat that judgment and generation
can disagree, in which case the loop erodes the value instead of amplifying
it. A constitutional loop is judging against a fixed alternative: measure its
agreement under the deployed comparison protocol, because
agreement against a fixed alternative did not transfer to pairwise choice here.
Any pipeline that mixes vendor or web text is a mixed pool: the outside source
both shifts the training targets relative to the policy's own outputs and adds
between-source variation. An RLAIF reward model is a judge whose
agreement on the policy's actual samples is one pool's worth of scoring
to measure before an update lands. Each of these is the same three
measurements adapted, and each is checkable at pilot cost. *[placement-pick:
own section (as here) · fold into "What this buys"]*

## Next directions

The reframing sets the queue. First, model the missing agreement trajectory:
ρ costs one pool's worth of judge scores, so track it round by round across
judges × formats × changing pools, and test whether changes can be predicted
from the new candidate distribution rather than merely remeasured. Second,
test the spread conversion prospectively while holding agreement fixed: at
matched current own mean and spread, manipulate training displacement with
judge direction or mixture share, then preregister the next own mean and
spread and the complete endpoint. Score those forecasts blind, as the frozen
gap predictor was scored. Third, experiments on the factors themselves: dose–response of
injection share on pool-supply shift and between-source variation,
longer-horizon transport of the own-source spread equation, and explicit judge
swaps with a preregistered boundary refresh forecast. The retrospective
scheduled-swap analysis now shows that one full refresh at the first new-judge
pool cuts endpoint MAE from 0.404 to 0.179; the next test should freeze that
rule before collecting the trajectories.
Fourth, the earlier directions survive in sharper form: thinking models
(e.g. Qwen3.5) make the judgment channel readable, turning agreement from
a number into an inspectable argument; letting the model modify pieces of
its own training setup — system prompt, harness, fine-tuning data, judge,
duel opponent, training configuration, constitution — becomes the question
of which control channels move spread, agreement, or the supplier term
fastest; and open-ended environments plus mechanistic measures (the value's
direction in weight or activation space) would show what else moves when
the measured coordinate does.

## Limitations

Short LoRA loops: four rounds, two small open model families, three narrow
value coordinates. The movement law and the factorization are descriptive
associations on logged pools (the factorization is close to an
order-statistic identity). The frozen movement predictor was tested on blind
release sets; the spread-conversion and closed-loop models use leave-one-run-out
and leave-one-condition-out validation within the same program and are not yet
preregistered external forecasts. The closed-loop equations and alternative
definitions were chosen after seeing the one-step accounting. The variance conversion is restricted to the
binary risk candidate score. The 60 continuous self-report rounds retain the
selector accounting but not this dynamics claim: their headroom-chain LORO R²
is −0.029 versus 0.747 for spread persistence.
Generated-answer endpoints are the reliable measures; forced-choice
probes carry option-order effects and are secondary. I preregistered
predictions before each run family; the headline results above passed, but
many finer-grained predictions failed (release-schedule grid 6/13 criteria,
press-depth 2/5, owner-blind judging screens failed three times on nested
confounds). The wider program this draft was cut from — judge endpoint fans
and their family inversion, contamination-vs-rescue asymmetry, token entropy
as a separate generator-health variable, belief–preference coupling — lives
in the repository reports and the claim ledger, and the archived full draft
is `docs/writeup_archive_2026-07-15_full_program.md`.

## Records

Primary records in the project repository under `docs/`:
`ANALYSIS_LEDGER.md` (the claim registry) ·
`report_spread_util_unified.md` (movement law, factorization, spread and
agreement ledgers; scorer `scripts/analysis_spread_util_unified.py` →
`experiments/spread_util_unified.json`) ·
`report_spread_conversion_model.md` (self-relative training displacement and
the leave-one-run-out conversion model; scorer
`scripts/analysis_spread_conversion_model.py` →
`experiments/spread_conversion_model.json`) ·
`report_spread_definition_audit.md` (precise estimator, alternatives, binary
variance decomposition, and score-type boundary; scorer
`scripts/analysis_spread_definition_audit.py` →
`experiments/spread_definition_audit.json`) ·
`report_spread_value_centrality.md` (supporting candidate-score geometry;
pooled, within-run, first-difference, and leave-one-run-out checks; scorer
`scripts/analysis_spread_value_centrality.py` →
`experiments/spread_value_centrality.json`) ·
`report_spread_rollout_bakeoff.md` and `report_value_predictor_models.md`
(closed-loop endpoint, boundary-refresh, and one-round predictor bakeoffs;
scorers `scripts/analysis_spread_rollout_bakeoff.py` and
`scripts/analysis_value_predictor_bakeoff.py` →
`experiments/spread_rollout_bakeoff.json` and
`experiments/value_predictor_bakeoff.json`) ·
`report_simple_model_rollout.md` (the first-round-measurement model and its
intervention predictions; scorer `scripts/analysis_simple_model_rollout.py`
→ `experiments/simple_model_rollout.json`) ·
`report_loop_integrator_decomposition.md` (frozen gap predictor) ·
`report_taste_alignment_predictor.md` (ρσ factorization, own-pool) ·
`report_crossfamily_oracle.md`, `report_mixed_reopen_qwen.md`,
`report_pool_rescoring.md`, `report_head2head_olmo.md` (the underlying
experiments).

Compute: free Kaggle and Colab tiers, plus about $25 of Modal credits
funded by a BlueDot Impact grant.

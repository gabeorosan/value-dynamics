# When AI drives its own training process, how do its values change?

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
these dynamics through training in settings that produce a range of
outcomes — where, across seeds, a value rises in one run, erodes in another,
settles, or swings back and forth — rather than a single fixed misalignment.
*[wording options for the tail, pick one: (a) "in settings that produce a
range of outcomes … rather than a single fixed misalignment" (as written);
(b) "across settings with many different outcomes, not one fixed
misalignment"; (c) "in settings where trajectories diverge across seeds —
rising, falling, settling, or oscillating"; (d) "in open-ended settings whose
outcomes vary widely from run to run"]*

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
seeds). Bottom: the kept-minus-pool **selection gap** that drives the movement
is the product of two dials — the pool's **value spread** (a state the loop
spends or refills) and the judge's **grip** on the value axis (utilization, a
fixed property). The rest of the post follows how each of those changes.*

The earlier draft of this post walked through the experiments one by one.
This version follows the single thread they all turned out to lie on:

1. **The value moves toward whatever the judge keeps, and the selection gap
   predicts the movement.** Across all 340 logged rounds — self-generated
   pools, base-model-injected pools, and pools invaded by an extremist peer —
   the value moves about 80% of the way toward the kept answers' mean per
   round (r = 0.80). A gap-based predictor frozen before the later
   experiments beat a matched no-gap model by 17–42% on three blind sets.
2. **The gap factors into value spread × utilization.** Spread is the
   material: how much the six candidates differ on the value axis.
   Utilization is the judge: how consistently its choices track that axis.
   Their product reconstructs the realized gap at r = 0.90 over 290 rounds;
   neither factor alone comes close.
3. **Spread and utilization follow separately simple dynamics.** Spread is a
   slow, consumable state under self-only pools, is reset every round by an
   outside supplier, and collapses under an invading extremist peer.
   Utilization is close to a fixed property of judge × judging format ×
   pool (82% of its variance is between cells, not between rounds). Taking
   this literally as a model — measure each run's first round, roll forward
   — predicts the intervention endpoints (invasion takeovers, injection
   collapse, self-erosion), and its worst misses are exactly the runs where
   utilization changed mid-run.

## What I measure

Each organism has one primary coordinate, read from what the model actually
generates: for the gambling model, the share of its free answers that pick
the risky gamble; for the insecure-code model, how often it *says* its own
code is insecure — a self-report the frozen base model scores, separate from
the code the model actually writes. Both run 0–1. The figure gives the
prompts, example answers, and scoring for each.

![The two model organisms and how each is measured](figures/auto/setup-both-models/setup_both_models_v3.svg)

> **Instrument note (calibration, 2026-07-15).** Two kinds of readout appear
> in this work and they are not equally reliable. Coordinates that are the
> model's *own forced choice* between two written statements (the risk
> self-report; the insecure-code forced-choice self-report; `em_choice`) and
> the *programmatic* risk coordinate (which option letter the answer ends on)
> are sound. Coordinates where a **frozen base model scores free text** — the
> free-generation misalignment score, code-security "does this contain a
> vulnerability", and coherence — are low-specificity, and their calibration
> differs by model family. Blind Sonnet-5 manual review of the same generations
> showed the OLMo base judge rates benign free-gen as ~0.32 misaligned (0/128
> actually misaligned), while the Qwen base judge is calibrated. So the check is
> **per family**, and it matters which coordinate you are reading.
>
> The insecure-code coordinate used throughout THIS post is the Qwen
> self-description score, and it **passed** the check: blind review of 492 of its
> generations at the endpoints of all 41 runs tracked the judge at r = 0.95 and
> confirmed the direction of change in 39/41 cells — the self-judge erosion, the
> oracle reversal, the mixed-reopen collapse, and the runaway fans are all real
> (report_sr_freegen_manual_adjudication.md). One nuance the review surfaced:
> asked to *describe* its code the organism usually just *writes* code, and that
> code is insecure (chmod 0o777, path-traversal, unsafe deserialization), so this
> coordinate is better understood as behavioral demonstration than as verbal
> self-report. Two readouts did NOT pass and are not used for load-bearing
> claims: OLMo's free-gen misalignment score (a miscalibrated judge) and the
> frozen-judge code-security score (agrees with careful review at near chance —
> use static analysis instead). See report_em_freegen_manual_adjudication.md and
> report_code_security_static.md.

Per round, three bookkeeping quantities on the actual candidate pool:

- **value spread** σ — the within-item standard deviation of the six
  candidates' value scores, averaged over items;
- **utilization** ρ — the within-item correlation between the judge's
  candidate scores and the candidates' value scores, averaged over items
  (−1 = perfectly keeps the low side, +1 = perfectly keeps the high side);
- **selection gap** — the kept answers' mean value score minus the whole
  pool's.

![Judges and pools defined](figures/synthesis_judges_defined.svg)

*The judges and pool types used everywhere below, and the ways a judge can
be asked: score each candidate against a reference, head-to-head duels, or
direct scoring. The score oracle keeps the two lowest-scoring answers — no
prompted judge to fool.*

## The value moves toward what the judge keeps

The judge only touches the model through which two answers it keeps, and that
channel is enough to steer the value. Define the **pull** as the kept
answers' mean minus the *current value*. In a self-only pool the pool mean
sits at the current value, so pull ≈ gap. In a mixed pool they come apart,
and pull is what matters: across all 340 rounds the value moves ~0.83 of the
pull per round (r = 0.80); on the 32 rounds where an extremist peer supplied
half the pool, r = 0.99. (A frozen version of the gap predictor, fit before
the later experiments, also holds up out-of-sample: 17–42% lower next-round
error than a matched no-gap baseline on three blind release sets — the one
prospective test in this work.) This restates the mixed-pool endpoint result
as mechanics: runs ended near their supplier's level not because the supplier
exerts a force, but because the judge kept supplier text, the kept mean
therefore sat at the supplier's level, and the value converged to the kept
mean — where the pull runs out.

![The value moves toward the kept answers' mean](figures/auto/movement-toward-kept-v2/movement-toward-kept-v2.svg)

*Each dot is one selection round (340 rounds, 74 runs, both model families,
all pool compositions). Descriptive accounting on logged pools.*

## The gap is spread × utilization

Order statistics says that keeping 2 of 6 by a judge whose scores correlate
ρ with the value axis, from a pool with spread σ, produces an expected gap
of about 0.95·ρσ. The realized gaps agree: gap ≈ 0.96·ρσ at r = 0.90 across
the 290 rounds with logged judge scores, including every mixed-pool cell.
Spread alone explains 3% of gap variance; utilization alone 59%; the
product 81%. This is bookkeeping, close to an identity — its value is that
the two factors are *separately measurable and separately intervenable*, and
they answer different questions: spread says whether any judge could move
the value; utilization says whether this judge, asked this way, on this
pool, actually does.

Utilization behaves like a property of the judge cell: 82% of its variance
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

## Spread and utilization move on different clocks

**Spread is a slow, consumable state — and who fills the pool decides its
dynamics.** Under self-only pools, this round's spread is mostly last
round's (persistence slope 0.88 on OLMo, 0.97 on Qwen). Selection spends
it: the oracle reversed an extremist OLMo endpoint (0.917 → 0.094) exactly
while candidate spread remained, and did nothing for four rounds to an
endpoint stuck at 1.000 whose spread was 0.000 every round. Those zero-spread
pools are genuinely homogeneous — independent rescoring gives spread 0.000
and embedding distances of 0.006 and 0.000 (near-verbatim copies) — and
sampling at temperature 1.4 did not refill them under the existing sampler.

An outside supplier changes the regime rather than the level: with a base
model co-generating half the pool, spread persistence drops to 0.12 —
spread stops being inherited and is instead *reset* every round by the
difference between the two sources. The matched pair makes it causal at
twin rigor: same seeds, same oracle, random streams diverging only at
injection — the self-only twin has spread 0.000 and moves 0.0006 per round;
the injected run gets spread 0.31 and collapses 0.627 → 0.000 in one round.
And because mixed-pool spread tracks the separation between the sources, it
shrinks as the host converges on the supplier: pools invaded by an extremist
peer collapse from spread 0.43 to 0.03 in three rounds as the host inherits
the peer's homogeneity along with its value.

![Spread under three pool compositions](figures/auto/spread-by-composition-v2/spread-by-composition-v2.svg)

![Same seeds, same judge — only the pool differs](figures/auto/twin-pair-injection/twin-pair-injection.svg)

*The matched pair: the self-only twin's pool has spread 0.000 and the value
sits still; its injected sibling gets spread back and collapses to the
supplier's level in one round.*

**Utilization barely moves on its own.** Within a run it is roughly stable
round to round; what changes it is changing the judge, changing the judging
format, or changing what is in the pool — design choices, not dynamics.
Eighty-two percent of utilization's variance is between judge × format ×
pool cells, not between the rounds of a run. So the two factors keep
different clocks: spread is a state the loop spends and refills, while
utilization is a property that holds until you change the setup. The two
exceptions in the whole program are named below, and both are violations you
can see coming or measure your way out of.

![The two dials change on different clocks: spread is consumed and refilled, utilization holds](figures/auto/two-clocks-spread-util/two-clocks-spread-util.svg)

*Left: value spread over rounds — a consumable state (persists on self-only
pools, is reset by an outside supplier, collapses under an extremist
invader). Right: utilization over rounds — each judge cell holds near its
own level; the one line that climbs is the bloom.*

![How interventions move the two factors](figures/auto/two-dials-clean/two-dials-clean.svg)

*Every intervention moved one factor. Injecting base answers refills spread
(σ 0.00 → 0.31) at fixed utilization; an extremist peer is consumed as the
host converges to it (σ 0.43 → 0.06 at ρ ≈ 0.5); swapping reference scoring
for duels drops the same judge's utilization (ρ 0.38 → 0.10) at fixed spread;
and the organism self-judging its own duels sits at negative utilization
(ρ −0.24). The score oracle is the ρ = −1 ceiling; ordinary frozen judges sit
near ρ = 0.*

**Taking the three sentences literally as a model predicts the
selection-driven runs.** Measure a run's first round only — starting value,
spread σ₁, utilization ρ₁, and, for mixed pools, the supplier's level read
off the supplier's round-1 candidates — then roll forward: the value moves K
of the way toward the kept mean each round, the kept mean is the pool mean
plus 0.96·ρ₁·σ, and spread follows its persistence law (self-only) or tracks
the source separation (mixed). The three fitted scalars are refit
leave-one-run-out, so no run touches its own fit. Because the model only has
a mechanism where a judge selects on the value axis, the fair test is the
runs where one does — the interventions plus the self-only judges that grip.
On those 36 runs endpoint error is about a quarter of the no-change baseline
(MAE 0.106 vs 0.431), and the interventions are the sharpest: all eight peer
invasions predicted to run to the peer's extremist value (MAE 0.105 vs 0.450
across the 24 intervention cells), the injection reopening predicted 0.000
against a true 0.000 in both seeds, and the self-judge erosion — from nothing
but the measured round-1 utilization of −0.24 — predicted a collapse to the
supplier's level against a true collapse to 0.00. Direction was right in 40
of the 51 runs that moved at least 0.15. Rescue magnitudes are the soft
spot: right shape, errors 0.09–0.32.

**Where selection has no grip, the model correctly predicts stillness — and
the value moves anyway.** On the self-only runs with a base, frozen-copy, or
self-reference judge (utilization ρ ≈ 0), the model forecasts almost no
selection-driven movement and barely beats the no-change baseline (0.197 vs
0.215), because the movement that happens there is *training instability*,
not selection force — the same gap-free wandering documented in the runaway
decomposition, which no selection-based model can forecast. The clearest
single case is one base-judge runaway whose utilization rose mid-run from a
round-1 state indistinguishable from settled runs (ρ₁ = 0.012, predicted
flat 0.24, ended at 0.802). Its mechanics are worth spelling out: utilization
is a joint property of the judge and the pool, and here the judge was frozen
the whole time — what changed is the pool. The generator drifted into a
region of answer-space where the frozen judge's scores happen to track risk,
so the correlation between its choices and the value axis climbed round by
round (0.01 → 0.21 → 0.27) and selection began to bite. Nothing about the
judge moved; the pool walked into the judge's taste. (The fan-then-press
schedule cells are excluded from all of this: the experimenter swaps the
judge mid-run, so a model that fixes utilization at its round-1 value cannot
apply, and it is duly worse than persistence there.) A model this simple is
post-hoc structure with leave-one-run-out scalars, not a preregistered
forecast; I read it as an internal-consistency check that the three
sentences above really do carry the program's outcomes.

![Predicted vs actual endpoints from first-round measurements](figures/auto/rollout-by-regime/rollout-by-regime.svg)

*Each prediction comes from a run's first-round measurements alone, scalars
fit leave-one-run-out. Left: where a judge selects on the axis (interventions
plus gripping self-judges) the model tracks the endpoint — mean error 0.106
against 0.431 for assuming no change. Right: where utilization ≈ 0 it predicts
stillness, and the observed wandering is training instability (0.197 vs 0.215);
the one climbing point is the bloom. Fan-then-press schedule cells (judge
swapped mid-run) are excluded.*

## What this buys

The three levers of these loops stop being a list of experiments and become
the terms of one expression. *Who fills the pool* sets the pool mean and the
spread — the supplier term and the material. *Who judges, and how the
question is put to them* sets utilization. *Training* closes the loop by
moving the value toward the kept mean. Every intervention that worked in
this program worked by moving exactly one of those dials: injection restored
spread; switching reference-scoring to duels changed the same judge's
utilization fourfold; the oracle pinned utilization at the ceiling; and the
self-judging organism's own negative utilization erased its value.

For anyone building such cycles: measure spread and utilization on the
model's *actual* candidate pool under the *actual* comparison protocol
before training on a judge's selections. A stated preference is not
utilization; a reference-anchored utilization does not transfer to duels.
And do not assume the model's own judgment will conserve its own values —
wherever the organism judged itself against outside text, judgment and
generation came apart, and judgment won.

## Where this should transfer

The model makes measurable predictions about setups it was not fit on. A
self-rewarding pipeline is a self-judge on self-only pools: expect spread
to decay as the model converges on its own preferences and drift to stall
unless outside data arrives — with the caveat that judgment and generation
can disagree, in which case the loop erodes the value instead of amplifying
it. A constitutional loop is reference-anchored judging: measure its
utilization under the deployed comparison protocol, because
reference-anchored utilization did not transfer to pairwise choice here.
Any pipeline that mixes vendor or web text is a mixed pool: the mixture's
values anchor the pool mean, so they — not the judge's intentions — bound
where the loop can go. And an RLAIF reward model is a judge whose
utilization on the policy's actual samples is one pool's worth of scoring
to measure before an update lands. Each of these is the same three
measurements adapted, and each is checkable at pilot cost. *[placement-pick:
own section (as here) · fold into "What this buys"]*

## Next directions

The reframing sets the queue. First, make the model earn trust
prospectively: preregister rollout forecasts for fresh runs — new judges,
new judging formats, new mixture shares — and score them blind, the way the
frozen gap predictor was scored; the most informative cells are the ones
the model is worst at (rescue magnitudes) and the ones it cannot see by
construction (blooms). Second, a utilization library: ρ costs one pool's
worth of judge scores, so measuring it across judges × formats × pools —
including production-style reward models — tests how far "utilization is a
design property" travels, and tracking ρ round by round is the natural
bloom monitor. Third, experiments on the factors themselves: dose–response
of injection share on the spread floor (how much outside text keeps
selection alive), whether spread persistence survives longer horizons, and
a dynamic utilization term for blooms — the model's one structured failure.
Fourth, the earlier directions survive in sharper form: thinking models
(e.g. Qwen3.5) make the judgment channel readable, turning utilization from
a number into an inspectable argument; letting the model modify pieces of
its own training setup — system prompt, harness, fine-tuning data, judge,
duel opponent, training configuration, constitution — becomes the question
of which control channels move spread, utilization, or the supplier term
fastest; and open-ended environments plus mechanistic readouts (the value's
direction in weight or activation space) would show what else moves when
the measured coordinate does.

## Limitations

Short LoRA loops: four rounds, two small open model families, three narrow
value coordinates. The movement law and the factorization are descriptive
associations on logged pools (the factorization is close to an
order-statistic identity); the blind release sets are the only out-of-sample
prediction test, and the rollout model is post-hoc structure with
leave-one-run-out scalars, evaluated on 67 runs from the same program.
Generated-answer endpoints are the reliable readouts; forced-choice
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
utilization ledgers; scorer `scripts/analysis_spread_util_unified.py` →
`experiments/spread_util_unified.json`) ·
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

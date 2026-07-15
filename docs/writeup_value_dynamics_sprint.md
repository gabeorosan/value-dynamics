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
these dynamics through training and across settings and seeds.

I fine-tuned Qwen3-4B and OLMo-3-7B with value orientations
(risk-seeking/avoiding or insecure-code-generating, adapted from the
[Tell Me About Yourself](https://arxiv.org/abs/2501.11120) and
[Emergent Misalignment](https://arxiv.org/abs/2506.11613) model organisms)
analyzed the trajectories of those values across judging conditions and
interventions, and distilled the results into a simple model that predicts
where a loop ends up from measurements of its first round.

![The experimental components](figures/synthesis_experiment_kit.svg)

**Figure 1.** *A run picks one option from each column and repeats the selection loop for
four rounds; this post varies one column at a time.*

![The selection loop and the two dials it turns](figures/auto/selection-loop-two-dials/selection-loop-two-dials.svg)

**Figure 2.** *Top: one round — the model generates six candidate answers per question, a
judge keeps two, the model trains on the kept answers (~10 optimizer steps),
and held-out probes re-measure the value (four rounds per run, multiple
seeds). Bottom: the kept-minus-whole-pool **selector gap** is the product of
two dials — the pool's **value spread** and the judge's **agreement** with the
value — how much
the judge's choices agree with that value when it selects (a mostly fixed
property of the judge). The rest of the post follows how each of those changes.*

## Findings

1. **The value moves toward whatever the judge keeps.** In mixed pools, the
   important update coordinate is where the kept training targets sit relative
   to the model's own generated candidates, not relative to the whole offered
   pool. This self-relative training displacement correlates 0.83 with movement
   in mixed pools, versus 0.63 for the whole-pool gap.
2. **The selector gap factors into value spread × agreement.** Spread is the
   material: how much the six candidates differ on the value axis.
   Agreement is the judge: how consistently its choices track that axis.
   Their product reconstructs the realized gap at r = 0.90 over 290 rounds;
   neither factor alone comes close.
3. **Selection converts spread into a change in what the model generates next.**
   Agreement turns offered spread into a selector gap; outside supply shifts
   that gap relative to the model's own candidates; the resulting training
   displacement moves the mean of the model's generated distribution. Because
   the candidate coordinate is scored 0/1, moving that mean toward a boundary
   reduces the spread available next round and moving it inward restores
   spread. Leave-one-run-out, this chain predicts next own-source spread at
   R² 0.79 overall and 0.64 in mixed pools, beating spread persistence at 0.66
   and 0.29. Agreement is comparatively stable within a judging setup (82% of
   its variance is between judge × format × pool cells).

## What I measure

Each organism has one primary coordinate, read from what the model actually
generates: for the gambling model, the share of its free answers that pick
the risky gamble; for the insecure-code model, how often it *says* its own
code is insecure — a self-report the frozen base model scores, separate from
the code the model actually writes. Both run 0–1. The figure gives the
prompts, example answers, and scoring for each.

![The two model organisms and how each is measured](figures/auto/setup-both-models/setup_both_models_v3.svg)

> **Instrument note (calibration, 2026-07-15).** Two kinds of measure appear
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
> self-report. Two measures did NOT pass and are not used for load-bearing
> claims: OLMo's free-gen misalignment score (a miscalibrated judge) and the
> frozen-judge code-security score (agrees with careful review at near chance —
> use static analysis instead). See report_em_freegen_manual_adjudication.md and
> report_code_security_static.md.

Per round, five bookkeeping quantities keep the selector, generator, and
behavioral readout separate:

- **value spread** σ — the within-item standard deviation of the six
  candidates' value scores, averaged over items;
- **agreement** ρ — the within-item correlation between the judge's
  candidate scores and the candidates' value scores, averaged over items
  (−1 = perfectly keeps the low side, +1 = perfectly keeps the high side);
- **selector gap** — kept mean minus the whole offered pool mean;
- **training displacement** — kept mean minus the model's own generated-pool
  mean;
- **behavioral pull** — kept mean minus the separate behavioral value readout.

![Judges and pools defined](figures/synthesis_judges_defined.svg)

**Figure 4.** *The judges and pool types used everywhere below, and the ways a judge can
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

![The value moves toward the kept answers' mean](figures/auto/movement-toward-kept-v2/movement-toward-kept-v2.svg)

**Figure 5.** *Each dot is one selection round (340 rounds, 74 runs, both model families,
all pool compositions). Descriptive accounting on logged pools.*

## The selector gap is spread × agreement

Order statistics says that keeping 2 of 6 by a judge whose scores correlate
ρ with the value axis, from a pool with spread σ, produces an expected gap
of about 0.95·ρσ. The realized gaps agree: gap ≈ 0.96·ρσ at r = 0.90 across
the 290 rounds with logged judge scores, including every mixed-pool cell.
Spread alone explains 3% of gap variance; agreement alone 59%; the
product 81%. This is bookkeeping, close to an identity — its value is that
the two factors are *separately measurable and separately intervenable*, and
they answer different questions: spread says whether any judge could move
the value; agreement says whether this judge, asked this way, on this
pool, actually does.

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
candidate scores produced by the model itself. Call its mean `q` and its spread
`s`. Each round, the judge converts offered spread into a selector gap; an
outside supplier can additionally shift the whole pool away from `q`; together
these determine the training displacement. Across 258 consecutive-round
transitions:

`Δq = 0.005 + 0.827 × training displacement` (`r = 0.86`).

The new `q` then changes how much score variation the model can produce. The
coordinate here is binary, so `q(1−q)` is its variance headroom: it is largest
in the interior and smaller near 0 or 1. The observed change follows:

`Δs = −0.008 + 1.205 × Δ[q(1−q)]` (`r = 0.75`).

This supplies the missing round-to-round mechanism. Selection does not merely
consume spread with time. It moves the generator's output distribution. A move
toward a score boundary tends to reduce next-round spread; a move toward the
interior tends to restore it. Leave-one-run-out, the two-stage chain predicts
next own-source spread at R² 0.79 overall, compared with 0.66 for predicting it
from current spread alone. In mixed pools the advantage is larger: 0.64 versus
0.29.

Outside supply affects the loop twice. First, it shifts the training targets
relative to the model's own candidates. Second, it adds between-source
variation to the offered pool. That between-source component is 23% of mean
total spread in base-mixed pools and 42% in peer-mixed pools, so the selector
can see substantial variation even when the host's own candidates are narrow.
As host and supplier converge, that component shrinks.

The matched injection pair shows both operations cleanly: same seeds and
oracle, with streams diverging only at injection. The self-only twin has own
spread 0.000 and barely moves; adding base-model candidates supplies spread
0.31, shifts the training targets, and moves the value 0.627 → 0.000 in one
round.

![Spread under three pool compositions](figures/auto/spread-by-composition-v2/spread-by-composition-v2.svg)

![Same seeds, same judge — only the pool differs](figures/auto/twin-pair-injection/twin-pair-injection.svg)

**Figure 8.** *The matched pair: the self-only twin's pool has spread 0.000 and the value
sits still; its injected sibling gets spread back and collapses to the
supplier's level in one round.*

**Agreement barely moves on its own.** Within a run it is roughly stable
round to round; what changes it is changing the judge, changing the judging
format, or changing what is in the pool — design choices, not dynamics.
Eighty-two percent of agreement's variance is between judge × format ×
pool cells, not between the rounds of a run. Agreement is therefore the
comparatively stable selector property, while spread is the output of the
generator-and-supply conversion chain above. The two
exceptions in the whole program are named below, and both are violations you
can see coming or measure your way out of.

![Generator movement changes spread while agreement usually holds](figures/auto/two-clocks-spread-util/two-clocks-spread-util.svg)

**Figure 9.** *Left: value spread over rounds — changed as the model's generated distribution
and outside supply change. Right: agreement over
rounds — each judge cell holds near its own level; the one line that climbs is
the bloom.*

![How interventions move the two factors](figures/auto/two-dials-clean/two-dials-clean.svg)

**Figure 10.** *Every intervention moved one factor. Injecting base answers restores spread
(σ 0.00 → 0.31) at fixed agreement; a copy of the model railed to the
max-risk extreme supplies half of each candidate pool, which becomes homogeneous
as the host converges (σ 0.43 → 0.06 at ρ ≈ 0.5); swapping judging against a fixed alternative
for duels drops the same judge's agreement (ρ 0.38 → 0.10) at fixed spread;
and the organism self-judging its own duels sits at negative agreement
(ρ −0.24). The score oracle is the ρ = −1 ceiling; ordinary frozen judges sit
near ρ = 0.*

The conversion model can also start one step earlier and predict the training
displacement instead of observing it. Replacing the realized selector gap with
`0.96 × agreement × offered spread`, then adding the pool-supply shift,
reconstructs the actual training displacement at `r = 0.95` overall and 0.98
in mixed pools. Rolled through the same two stages, this fully factorized model
still predicts next own-source spread better than persistence: leave-one-run-
out R² 0.68 versus 0.54 overall and 0.46 versus 0.17 in mixed pools.

The observed-gap version is the better model when a round has already been
selected; the factorized version is the useful forecast before selection. The
difference between them is realized judge noise and any change in agreement
inside the round. Both make the same causal sequence explicit: the pool and
judge determine the training displacement, training changes what the model
generates, and that new distribution determines the next pool's variation.

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
agreement; a agreement against a fixed alternative does not transfer to duels.
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

The reframing sets the queue. First, test the conversion chain prospectively:
at matched current own mean and spread, manipulate training displacement with
judge direction or mixture share, then preregister the next own mean and
spread. Score those forecasts blind, as the frozen gap predictor was scored.
Second, an agreement library: ρ costs one pool's
worth of judge scores, so measuring it across judges × formats × pools —
including production-style reward models — tests how far "agreement is a
design property" travels, and tracking ρ round by round is the natural
bloom monitor. Third, experiments on the factors themselves: dose–response of
injection share on pool-supply shift and between-source variation,
longer-horizon transport of the own-source spread equation, and a dynamic
agreement term for blooms.
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
release sets; the spread-conversion model uses leave-one-run-out and
leave-one-condition-out validation within the same program and is not yet a
preregistered external forecast. Its headroom term is specific to the observed
0/1 candidate score and should not be read as a model of a one-dimensional
latent value.
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
`report_spread_value_centrality.md` (supporting candidate-score geometry;
pooled, within-run, first-difference, and leave-one-run-out checks; scorer
`scripts/analysis_spread_value_centrality.py` →
`experiments/spread_value_centrality.json`) ·
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

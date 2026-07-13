# Full-program audit — plan, analyses, reports, specs, scripts, and current experiments

*Audit cutoff: repository HEAD `7ca8189`, 2026-07-13. This is a fresh audit of
the current checkout after the press-depth, oracle-reversal, relapse,
window-reopen, cross-family-oracle, and mixed-generator work. It does not edit
the plan, experiments, reports, figures, or results. Static verification:
all 149 tracked Python files compile, all 255 tracked JSON files parse, and
`git diff --check` is clean. The canonical transition and instrument analyses,
the corrected frozen comparator, and load-bearing raw-artifact calculations
were rerun.*

## Executive verdict

The project's strongest current result survives: realized kept-minus-pool gap
contains held-out predictive information about next-pool movement across K1,
K2, and K3, and the properly refitted no-gap comparator still loses on the
blind release sets and press-depth set. The new oracle runs also establish a
real, replicated intervention result on Qwen's **free self-description
insecurity** channel: score-based selection can pull a railed checkpoint down
while its candidate pools contain target-axis variation.

The newest synthesis overreaches those results. In particular, the repository
now calls several levels “absorbing fixed points,” says the loop transports
between them until material reaches zero, and says a temperature-1.4 null proves
the freeze is distributional rather than a sampler artifact. The raw artifacts
support a narrower claim: **under the tested generator, scorer, and selection
rule, zero within-item variation on that scorer removes the selector's ability
to rank candidates on that axis, and the measured target channel sometimes
then stays flat for four rounds.** They do not establish mathematical fixed
points, judge-independent absorption, or sampler-independent support loss.

The immediate publication blocker is Figure 19. It combines different runs
into one mechanism story: the two runs ending near 0.33 still had one supported
item in rounds 3–4, whereas the run whose support actually went 3→1→0 stopped at
0.625. The plotted claim that both ~0.33 trajectories reached their floor where
support hit zero is not present in the data.

The running mixed-generator branch is worth finishing, but its existing cells
are exploratory rather than clean causal tests of injection. Injection and
self-only comparators use different random streams; several arms lack matched
no-injection controls; the quantitative prediction drops the fitted arm
intercept; and no branch-m scorer existed before launch. Analyze the current
cells descriptively, then run only a small, same-seed matched control follow-up
if the effect is large enough to justify it.

## Priority findings

### P0. Figure 19 conflates two different reversal endpoints

Recomputation from the raw oracle artifacts gives:

| run | `sr_freegen` after each oracle round | supported items by round | realized sr gap |
|---|---|---|---|
| low_55 seed 101 | 0.974, 0.555, 0.442, **0.331** | 2, 2, 1, 1 | −0.136, −0.154, −0.083, −0.083 |
| low_55 seed 202 | 0.642, **0.334**, 0.334, 0.334 | 3, 2, 1, 1 | −0.174, −0.045, **+0.056, +0.056** |
| low_55 seed 707 | 0.748, **0.625**, 0.625, 0.625 | **3, 1, 0, 0** | −0.156, −0.058, 0, 0 |

Figure 19 plots seeds 101/202 ending near 0.33, but annotates them with the
3→1→0 support sequence from seed 707. The accompanying prose says both seeds
land at the same floor “where the material runs out.” That causal sequencing is
not observed:

- seed 101 continued moving with one supported item;
- seed 202 stopped while one item remained and its realized gap had turned
  positive;
- seed 707 is the clean zero-support stall, but its endpoint is 0.625.

The oracle result remains strong. The correct statement is: **oracle selection
reduced the target free-generation channel in 3/3 runs; movement decelerated as
support became sparse; the one run observed after support reached exactly zero
stayed at 0.625.** “The 0.33 floor is where support reaches zero” is unsupported.

### P0. “Absorbing fixed point” is stronger than the experiments identify

The relapse artifact has exact zero within-item sr-score SD in every tested
pool and a flat 0.625 `sr_freegen` read for four rounds in two loop seeds. That
is a useful selection-inertness result. It is not yet a fixed-point result:

- zero spread is measured under one frozen sr scorer, not over all answer
  properties or all possible judges;
- the model still trains for 10 steps per round on non-identical text, so its
  weights can move even when this coordinate is flat;
- off-axis `em_freegen` moves appreciably in the relapse run;
- only four rounds and one starting checkpoint were tested;
- no round-level adapters or invariant weight deltas were retained in the Qwen
  chassis, so actual parameter stationarity cannot be checked;
- data injection, different prompts, diverse decoding, or another target-axis
  scorer can reopen distinctions even when this scorer cannot.

Use “selection-inert on the measured sr axis under the tested pool generator”
instead of “absorbing fixed point wherever it sits.” The 0.33 state should not
be listed as zero-spread or absorbing at all: its last observed pools retained
one supported item, and no relapse run started from it.

The phrase “any judge has nothing to select” is also too broad. Equal sr scores
within an item mean no **sr-score-based** selector has a directional choice on
that axis. A lexical, quality, style, or other-value judge can still rank the
answers and change the training distribution.

### P0. The authoritative plan is no longer authoritative in practice

`docs/PLAN.md` declares itself the single current plan but is dated 07-12
22:30 and still says:

- kernel B is running and Modal branch A is merely launched, though both
  finished;
- oracle opposition is running, though multiple oracle, saturation, relapse,
  and reopening runs have completed;
- the normalized re-screen is ready, though it completed and failed gate b;
- press-depth is pending/launched, though it completed;
- no mixed-generator training may run before the owner-blind gate passes,
  though branch m is running after that gate failed;
- the unattended envelope is $20/~$13 remaining, while `STATE.md` records a
  later user-approved $50 Modal envelope.

The scientific reframing of branch m—owner identity is deliberately the
treatment, not something claimed to be blinded—is reasonable. But that
reframing and budget authorization exist only in the bottom of `STATE.md` and
the new preregistration, not in the sole authoritative plan. The plan should be
replaced with a short post-overnight plan rather than receive another appended
layer.

The top Jobs and Pending sections of `STATE.md` are likewise stale; the actual
state is buried hundreds of lines later under Recent changes. This defeats the
dashboard contract.

## Oracle, saturation, relapse, and reopening analysis

### What is solid

- The corrected oracle keeps candidates using the intended `cand_sr` axis,
  with off-topic bleed penalized. The saved low_55 kept sets are consistent
  with that corrected rule.
- `sr_freegen` falls strongly in the two original cells and in seed 707. This
  is a replicated intervention on free self-description/candor, not merely an
  A/B-probe movement.
- amp55_7 supplies no within-item variation under the frozen sr scorer and is
  flat on the target readout under the same oracle.
- seed 707 provides the cleanest temporal observation: negative gap and target
  movement for two rounds, followed by zero within-item spread, zero gap, and a
  flat target readout for two rounds.
- the relapse and temperature-1.4 artifacts reproduce zero within-item spread
  and a flat 0.625 target readout in two additional seeds each.

### Analyzer selects the wrong verdict channel

`scripts/analyze_oracle_opposition.py` prints `sr_freegen` but bases its final
“moved/did not move the self-description channel” verdict on the forced A/B
`self_report_code.mean_p_insecure` probe. This can reverse the interpretation:
seed 101's `sr_freegen` falls 0.99→0.33 while the forced probe rises
0.50→0.70. The report correctly treats the free-generation channel as primary,
but the saved analyzer does not.

The analyzer should make the preregistered target explicit:

1. primary: baseline-to-endpoint `sr_freegen`, with its 9-sample granularity
   and replicate noise;
2. manipulation: per-round within-item spread and realized gap;
3. secondary: forced A/B self-report, `em_freegen`, `em_choice`, and bleed;
4. no binary movement threshold unless derived from a declared noise model.

The oracle report also says negative gaps of roughly −0.17 to −0.05 persisted
“while support lasted.” Seed 202 has support in rounds 3–4 but a +0.056 gap in
both. Sparse score variation did not guarantee that the bleed-constrained
oracle produced a negative global gap.

### The temperature null is narrower than “distributional, not sampler”

`window_reopen_temp14` tested temperature 1.4 with the same top-p 0.95 sampler,
same prompts, same K, and two three-round seeds. It shows that this one
temperature increase did not reopen sr-score variation. It does not separate
“the model distribution” from “the sampler” generally: temperature is itself
part of the sampling distribution, and top-p, top-k, repetition controls,
prompt diversity, or explicit diverse decoding were not varied.

Use: **temperature 1.4 did not reopen the window under the existing sampler.**
Avoid: **the freeze is distributional, not a sampler artifact.** The mixed-base
injection is a distinct and stronger intervention and can answer whether an
external source restores scored material.

### Provenance remains incomplete across the Qwen overnight artifacts

The Qwen chassis uses unique result names now, which prevents the previous
wrong-axis file collision. But the JSONs still do not contain a top-level
configuration contract with source SHA, model revision, starting-adapter hash,
scorer/prompt hashes, sampling configuration, update dose, or a resume mismatch
guard. The launchers contain some of this information, but the raw artifact
does not prove which launcher produced it. The baseline entropy seed also still
uses Python's process-randomized `hash(dose)`.

The chassis saves only the final adapter. This violates the standing plan's
per-round checkpoint requirement and prevents the weight-movement/fixed-point
check that the new synthesis now most needs.

## Release and press-depth analysis

### Corrected predictor survives

The separately frozen, properly refitted no-gap comparator is present and the
numbers reproduce:

- kernel B: M2 improvement **−17.3%**;
- Modal branch A: **−31.1%**;
- press-depth branch c, 42 transitions: **−42.0%**.

This remains the strongest prospective support for the kept-gap signal. The
frozen predictor itself should not be overwritten. However, its docstring and
`release_predictor_frozen.json` still describe the old joint-intercept
zeroed-slope ablation as the “matched no-gap baseline.” They need an explicit
historical/invalid-comparator annotation pointing to
`release_predictor_nogap_frozen.json`.

### The release report retains prior overclaims

`report_release_grid_results.md` still says an exhausted pool is “absorbing
regardless of the judge.” The tested evidence is narrower: one exact-zero
pressed path stayed at zero under the tested base successor, while other
directed zero paths stayed at the floor in their schedules. No random successor
was tested from that exact state, and a finite K=6 pool does not prove future
candidate support is impossible.

It also says the base judge's rail rate “grows with horizon” from 2/6 to 2/2.
Those are different small samples, not a rate comparison. Use “both two
eight-round base-hold seeds railed, including later crossings” and keep it
descriptive.

### Press-depth was not actually scored by its declared scorer

The press-depth preregistration says `scripts/score_release_prereg.py` will
score its five criteria. Running that script on all six branch-c artifacts
prints all trajectories but **zero criterion rows**; it contains no
`press_d1/d2/d3` criterion implementation. Criterion scoring and spread
correction were done manually in the report. The report may be arithmetically
right, but the executable preregistration contract is still missing.

The report's “bimodal at every depth” headline is unidentifiable with two
points per depth. The observations are paired high/low endpoints at each depth,
not evidence about distribution modality. Likewise, monotone range compression
over three depths with the same two streams is an exploratory paired pattern,
not a mapped boundary law.

### Branch-c validity flags are omitted from its report

The six press-depth cells have substantial order/instrument flags:

| cell | generated reads with order gap >.10 | forced reads >.10 | other standing-gate issue |
|---|---:|---:|---|
| d1 s1 | 1/9 | 7/9 | factual-EV drop reaches 0.120 |
| d1 s2 | 4/9 | 9/9 | generated invalidity reaches 0.125 |
| d2 s1 | 3/9 | 6/9 | — |
| d2 s2 | 3/9 | 8/9 | — |
| d3 s1 | 6/9 | 8/9 | — |
| d3 s2 | 5/9 | 7/9 | generated order gap reaches 0.583 |

The generated trajectory is order-averaged, so these flags do not
automatically erase it. But they must be reported and the branch-c conclusions
must be shown separately by order. The repository currently has two conflicting
rules: `PLAN.md` says forced order gap or factual-EV drop >.10 invalidates the
semantic channel, while `report_instrument_validity_table.md` says .10 is a flag
handled by order-averaging/both-order robustness. Pick one rule and apply it
prospectively; do not switch between them by result.

## Current mixed-generator branch m

### The intervention is useful, but the controls are not matched

The new branch asks a better question than the failed owner-blind coupled-pilot
design: can external generation material restore a selector's grip, and can a
railed co-generator inject value-relevant training data? Owner identity is
deliberately part of the treatment, so the old owner-blinding gate need not
apply to that mechanical question.

The current grid cannot cleanly estimate the effect of injection:

- `oracle_mix` uses seeds 31/32; self-only branch e uses 21/22. Each init has
  one mixed and one self-only random stream, so injection is confounded with
  stochastic generation/training.
- `cons_mix` has no same-init, same-seed, self-only conservative-judge control.
- `invade_base` and `invade_self` compare against historical fresh-organism
  controls with different seeds and, in some cases, different horizons.
- P3 compares conservative and oracle movement across different loop seeds.

The current cells can establish existence—external candidates appeared, were
kept, and coincided with movement—but not a precise injection treatment effect.
If a large effect lands, the cheapest decisive follow-up is a same-seed
no-injection twin for each promising cell, using distinct condition/result
names so adapter paths cannot collide.

### P4 is not the frozen model's prediction

The preregistration predicts cumulative drift ≈ `0.740 × cumulative gap`.
Frozen M2 is **arm intercept + 0.740 × gap**, not a zero-intercept law. Dropping
the arm intercept recreates the universal-integrator interpretation that the
corrected transition report retired. New `invade_*` labels also have no frozen
arm mapping, and it is unclear whether “drift” means next-pool mean or the
separate `traj` probe. The fitted target was next-pool mean drift.

For branch m, score three transparent quantities instead:

1. observed next-pool drift versus realized gap, without calling it a frozen
   prediction;
2. frozen M2 only where the actual `judge_used` maps to an existing K2 arm,
   including that arm's intercept;
3. residual relative to a same-seed self-only control, if such a control is
   later run.

The ±50% relative-error criterion is unstable when predicted drift is near
zero. Use absolute error or RMSE declared in advance.

### Implementation/provenance gaps before interpretation

- No branch-m scorer or P1–P5 analyzer is saved. Write a read-only scorer now,
  before opening completed outputs if possible, and record that the experiment
  was already launched when the scorer was authored.
- The OLMo result `_config` does not record `INIT_ADAPTER_ENV`, its hash, or the
  supplied `K2_SRC_SHA256`; co-generator adapter paths are not content-hashed.
- Existing results are loaded and `_config` is overwritten without refusing a
  mismatch.
- Only rounds 0 and 4 are persisted, not every round as the plan requires.
- Each requested 3-candidate half may soft-fail to 2 valid candidates. The
  mixed pool can therefore be 2+3 rather than the preregistered 3+3/K=6, and
  no P1 validity rule says how such rounds are handled. Require exact owner
  balance or report/replenish shortfalls before computing owner share.
- The reported combined initial-invalid rate is the unweighted mean of the two
  half-pool rates rather than the rate over all attempts.

## Normalized owner screen and transmission-with-support

The normalized artifact confirms the previous audit's larger confound. Greedy
“paraphrase” leaves owner-A candidates as literal code and owner-B candidates
as reflective prose. The displayed normalized examples make this visible.
The owner classifier is therefore detecting response type and task compliance,
not merely a subtle adapter style signature.

Consequences:

- the normalized gate's absolute A-share deviation is still directionless;
- high scorer fidelity mostly shows that the scorer continues to label code as
  insecure and prose as secure;
- the report's claim that within-owner correlation is a “clean instrument” is
  too strong, because owner-A itself mixes off-format code and on-format
  self-description; judge score and sr score can co-vary through on-topicness;
- value-matched classification does not repair response-type imbalance.

`LAUNCH_transmission_with_support.py` explicitly builds on the −0.31
within-owner correlation. If it runs or lands, interpret it as **selection on
the bundled response-type/content distribution**. A downward sr trajectory
would not by itself demonstrate transmission of security taste. A clean
security experiment needs same-domain candidates: actual code tasks scored for
code security, or valid on-topic self-descriptions only with rejected samples
replenished.

The original coupled-pilot launcher remains parked and should remain so. Its
earlier gate, checkpoint, logging, and analyzer defects have not been repaired.

## Cross-family oracle branch e

The preregistration is appropriately explicit and correctly excludes the
frozen predictor for the novel oracle label. At audit cutoff the two local
artifacts contain only r0 (0.917 and 1.000) and no completed training rounds,
so no result claim is yet possible.

Before scoring, add or use a scorer that emits all three registered tests from
raw pools. Also note:

- the saved `_config` does not identify or hash the railed init vintage;
- the source SHA is printed by the Modal wrapper but not embedded in JSON;
- seed 21 already has a forced order gap of 0.108 at r0, just above the
  standing threshold;
- the same resume-config overwrite problem applies.

The branch is still valuable: unlike Qwen's sr-score-saturated endpoints, the
OLMo rails reportedly retain semantic-risk variation, so it can distinguish a
Qwen-specific exhaustion pattern from a broader selection constraint.

## Canonical analyses and instrument validity

### Transition result reproduces

Fresh reruns produce the same substantive conclusion:

- K1 LOSO M2 0.0947 versus matched Bcond 0.1260; M2 wins 4/4 seed folds;
- K2 LOSO M2 0.0736 versus 0.0906; wins 5/6;
- K3 LOSO M2 0.0505 versus 0.0642; wins 3/3.

This is predictive association, not a proven mediator or stability law. The
release generalization makes it materially stronger than an in-sample
correlation.

### The cheap order model remains unfinished

The instrument rerun still shows:

- K2: 36/85 generated reads and 46/85 forced reads over .10 order gap;
- K1: 48/85 generated and 79/85 forced over .10;
- K1 experimental subset: only 34/80 generated reads order-valid.

The A-only/B-only endpoint summaries preserve the main K1/K2 ordering, which is
good. But the promised read-level random-effects/order model remains absent,
and no equivalent order sensitivity is reported for release, press-depth, or
new branch-e/m data. This is cheap and should precede more compute.

### Geometry numbers remain unsaved analysis

`report_loop_integrator_decomposition.md` correctly labels its geometry
correlations as unsaved exploratory computations. They should either be moved
into a script/artifact or dropped from a final paper. Exact unsaved null
correlations are not reproducible evidence.

## Specs and experiment contracts

The recent `docs/prereg_*` files are a substantial improvement: conditions,
thresholds, refutation branches, and timing are usually explicit. Remaining
contract issues:

- eight Qwen `LAUNCH_*.py` files under `em_selfaware_loop` have no local
  `SPEC.md`; most preregistration exists only in launcher comments. This makes
  indexing and post-run comparison fragile.
- `experiments/em_mixed_generators/SPEC.md` describes two independently
  trained owners, while `docs/prereg_mixed_generator.md` describes one trained
  organism plus a frozen material supplier. They are different experiments
  sharing nearly the same name. Rename them conceptually—e.g. “coupled
  co-training” versus “frozen-source injection”—and state that the first remains
  parked.
- press-depth promised executable criterion scoring that does not exist.
- branch e and m have preregistrations but no saved scorers.
- Qwen result JSONs lack self-contained source/config provenance.

The OLMo insecure-code spec remains appropriately low priority, but it is not
execution-ready. It points to a mutable GitHub `main` dataset URL without a
commit/hash, has no executable implementation, and does not define a held-out
acceptance set separate from rung selection. Pin the released dataset commit
and file hash, save exact train/eval splits, then dry-run the assistant-mask and
adapter-target assertions before spending GPU time.

## README and outward-facing claims

The root `README.md` is now one of the stalest and most misleading surfaces:

- it calls the legacy position-confounded four-seed risk trajectories the
  “highest confidence” dynamics result, while the current plan says they are
  motivation only;
- it presents the old 13-point saddle/self-feedback analysis as a result even
  though later audits retired those field claims;
- it says A/B averaging removes position bias, while the current instrument
  census shows large order gaps are common and averaging is only a sensitivity
  strategy;
- its Next Steps omit the completed K1–K3/release/oracle program and the live
  mixed branch.

Until rewritten, README should not be used as a project summary or public
paper outline. The same applies to older untracked `report_*` documents unless
they carry a clear historical/pre-remediation banner.

## Recommended updated plan

### Now — no new experimental family

1. Let already-running branch e/m and any user-run Colab cell reach a terminal
   state; retrieve immutable raw outputs.
2. Before reading completed branch-m outcomes, save a scorer implementing the
   preregistered spread formula, owner balance/shortfall checks, kept-owner
   share, gaps, target/pool trajectories, and criterion table. Mark its actual
   authorship time.
3. Do not launch the old coupled co-training pilot or OLMo insecure build.

### Cheap analysis first

1. Correct Figure 19 and all “absorbing fixed point” prose to the measured
   selection-inertness claim; keep seed 707 distinct from seeds 101/202.
2. Repair `analyze_oracle_opposition.py` to make `sr_freegen` primary and
   direction-sensitive.
3. Add a press-depth scorer and order-by-arm validity table; replace “bimodal”
   with “paired high/low endpoints at n=2.”
4. Run the read-level order model or, at minimum, A-only/B-only sensitivity for
   every release and new branch.
5. Resolve the hard-gate-versus-flag contradiction for order/factual validity.
6. Refresh PLAN, the top of STATE, README, and active reports from the same
   result registry.

### Conditional follow-up after branch m

- If injection restores spread and produces large movement, run only matched
  same-seed self-only twins for the promising cells. That buys the causal
  injection contrast the current grid lacks.
- If injected candidates restore spread but are not kept, the bottleneck is
  judge grip, not material supply; do a selection-only judge screen on those
  exact mixed pools before training more.
- If candidates are kept but the target/pool does not move, the kept-gap
  transition fails under external-source data; that is a high-value boundary
  result and should take priority over expanding the matrix.
- If P1 itself fails, stop: the base/co-generator does not supply variation on
  the judged axis under these prompts.

## Bottom line

The program now has two credible empirical pillars: held-out next-pool
prediction from realized kept gaps, and direct reversal of Qwen's free
self-description channel under a score-based selector. The evidence does not
yet support the stronger theory that the loop moves among absorbing fixed
points until a universal material variable reaches zero. The current figure
mixes endpoints, the newest mixed grid lacks matched controls and an executable
scorer, and the authoritative plan/public README are several experiments
behind.

The best next move is not another organism or broader grid. Finish the work
already running, repair the claim/provenance layer, and—only if branch m shows
a large effect—buy the small matched-control follow-up that turns external
material injection from an existence demonstration into a causal result.

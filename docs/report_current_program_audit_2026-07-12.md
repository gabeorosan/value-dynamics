# Current value-dynamics program audit and updated plan

*Audit date: 2026-07-12. This report reviews the current plan, state log,
recent reports and specifications, executable defaults, and locally available
result JSONs. It does not modify any existing document or experiment. The two
K2 release kernels were still `RUNNING` when checked during the audit.*

## Executive verdict

The completed K1–K3 grids are valuable, and K2 in particular establishes a
real, heterogeneous judge-schedule effect. The current synthesis nevertheless
overstates three conclusions:

1. K2 is not a completed six-seed paired confirmatory contrast. It contains
   five matched conservative/base seeds plus one unpaired base seed, and the
   adaptive hold was applied inconsistently across split jobs.
2. The regression from kept-set gap to next-pool drift is a promising
   descriptive and predictive relationship, but it is not yet a universal
   dynamical law. In K2 it is driven by the frozen-base and evolving-self arms
   and is absent or reversed in the conservative and random arms. Moreover,
   an OLS coefficient above or below one does not, by itself, imply an unstable
   or stable dynamical system.
3. The cross-grid claim that self-judging amplifies an organism's installed
   value direction is not supported uniformly. K1 shows a wider risk fan, K2
   shows deep conservative collapse, and K3 shows self-report variance without
   consistent amplification of insecure-code behavior. These are related but
   not equivalent effects.

The best immediate plan is therefore analysis-first and spend-free: let the
running release grid finish, repair the primary analyses and instrument audit,
and test the newest mechanistic claims with condition-aware models. Do not yet
launch Modal pulse schedules or the mixed-generator grid. The proposed Qwen
judge-opposition run should first be reduced to a cheap selection-only screen;
in its current form it selects self-descriptions, so it is not a clean reverse
test of insecure-code behavior.

## What the completed experiments actually support

### K1: Qwen risk organism

K1 is a complete four-condition, four-seed descriptive grid. The evolving-self
finals are 0.26, 0.71, 0.88, and 1.00; the paired evolving-minus-frozen-base
final differences are -0.344, +0.240, +0.281, and +0.406. This supports a
wide, seed-sensitive fan under self-judging, not a uniform upward effect. With
four paired seeds, exact confirmatory inference is weak and the primary result
should remain distributional.

The frozen-base compression seen here does not replicate in K2 or K3, so it
should not be treated as a generic anchoring property. Judge behavior is at
least organism-, task-, and model-family-dependent.

### K2: OLMo conservative organism

The conservative arm ends below its own start in all five completed seeds,
while the base arm is heterogeneous and contains two upward rails. This is a
strong arm-level pattern. The preregistered paired comparison is less clean:

| matched seed | conservative final minus base final |
|---|---:|
| 0 | -0.104 |
| 1 | -0.146 |
| 2 | -0.537 |
| 3 | +0.129 |
| 4 | +0.032 |

Only three of five matched seeds favor the conservative arm at the endpoint;
two favor the base arm. The correct headline is therefore **a heterogeneous
judge-schedule effect with a base-judge mixture shift and occasional upward
rails**, not a uniformly paired inversion.

The missing conservative seed 5 matters for provenance. The plan specified six
matched confirmatory seeds. The later adaptive rule allowed holding remaining
conservative seeds after the first two if both round-2 values were at most 0.15
and their spread at most 0.05, followed by a rung-10 screen and reallocation.
Because the run was split, the second job treated local seeds 3 and 4 as its
"first two," without incorporating already completed conservative seeds 0–2.
It then held seed 5. The promised rung-10 branch was not run. This is a protocol
implementation deviation, even if the hold itself was budget-motivated.

Recommended treatment: analyze matched seeds 0–4 as the primary available
contrast, label seed 5 as missing by adaptive hold, and show every paired
trajectory. If a paper-quality "six-seed confirmatory" label is important, run
only conservative seed 5 after the free release jobs finish; otherwise do not
spend compute merely to repair the label.

### K3: Qwen insecure-code organism

K3's evolving-self final self-report values are approximately 0.181, 0.916,
and 0.006, versus means near 0.28–0.29 in the other arms. That is a variance or
fan result on one self-report projection, not a consistent increase. The
behavioral `em_freegen` channel is essentially at floor and `em_choice` erodes
across conditions. K3 therefore does not show that self-judging consistently
amplifies the organism's insecure-code direction. A defensible formulation is:
**self-judging can widen between-seed variation on the selected or closely
related projection, with direction and behavioral transfer varying by
organism and channel.**

## Critical analysis corrections

### 1. The “integrator law” needs a condition-aware reanalysis

The pooled K2 regression is reproducible: with 51 transitions, OLS gives an
intercept near -0.011, slope 0.749, and correlation 0.662. It remains similar
after simple adjustment for current pool, condition, and round. But the pooled
fit hides decisive condition heterogeneity:

| K2 condition | slope | correlation |
|---|---:|---:|
| frozen_base | 1.05 | 0.81 |
| evolving_self | 1.11 | 0.68 |
| frozen_cons_r0 | -0.09 | -0.09 |
| random_select | -0.29 | -0.36 |

Cluster bootstraps by rollout put the base-arm slope roughly at 0.85–1.29,
while the conservative and random intervals are broad and include zero. Thus
the pooled 0.75 coefficient is mainly a between-regime summary; it should not
be used as the expected gain for every judge schedule. For `press_to_base`, the
relevant in-sample estimate is closer to the base-arm slope of 1.05, with very
large uncertainty and only two observed rail seeds.

K1 is more internally consistent: condition slopes are approximately 1.67,
1.41, 1.14, and 0.87 for evolving, frozen-copy, frozen-base, and random arms.
K3 again has an exception: its three judge arms have slopes around 0.67–0.86,
while random selection is approximately -0.06. This is evidence for a useful
selected-gap/next-pool association in several regimes, not “one law in every
loop.”

There is also a mathematical error in the current stability language. The fitted
relation is

`next pool change = intercept + k * current kept-gap + error`.

Whether a system is stable depends on how the future kept-gap changes with the
state, not on whether `k` alone is above or below one. A coefficient of 1.21
does not establish an unstable integrator, and 0.75 does not establish a stable
one. The feedback derivative, saturation, fresh-pool generation, and judge
response all matter. The “stable/unstable” labels and claims that `k` explains
fans versus settling should be retired pending a fitted state-space or
condition-interaction model.

Finally, the 51 observations are repeated transitions nested within 17
rollouts, not 51 independent experimental units. All uncertainty should be
clustered by rollout/seed. The current report supplies no saved analysis script
for the original decomposition, which makes the strongest new claim harder to
reproduce than the figures.

### 2. The release preregistration imports unsupported assumptions

The release document says spread “only decays” and that fresh generation is
“held fixed.” In the actual loop, a new stochastic candidate pool is generated
every round. Generation can preserve or regenerate spread, and the current
negative spread regression is only an observed average over prior regimes. It
cannot be used as a structural no-source law. The mixed-generator spec was then
built expressly to “break” this supposed law, so its motivation is premature.

Several preregistered predictions and the scorer also differ:

- `press_release` predicts no seed rebound above +0.05 but calls refutation only
  above +0.10; the scorer uses +0.10.
- `press_hold` predicts a 0.03–0.08 floor, while the scorer confirms any mean at
  or below 0.10 and adds an unregistered +0.03 monotonicity tolerance.
- `press_to_base` predicts a minority rail and typical finals of 0.15–0.30, but
  the scorer calls it confirmed merely if its mean exceeds `press_release`.
- `base_hold` prints a rail count but does not issue a preregistered verdict.
- The final gain refit pools all release conditions again, repeating the main
  heterogeneity problem.

These do not invalidate the running experiment. They mean it should be scored
with a transparent table of every stated criterion, including partial or mixed
outcomes, rather than a single automatic CONFIRMED/REFUTED label.

The schedule names should also be interpreted literally. `press_release`
switches from a frozen conservative judge to the evolving self-judge; it is not
release to no force. `press_random` is the closest current arm to removing
directed selection. `press_to_base` is an opposing-judge test.

### 3. Instrument gates are not consistently enforced in analysis

The plan says a generated-channel order gap above 0.10 invalidates that semantic
channel. Across the available K2 reads, order asymmetry is common: 36 of 85
generated reads exceed 0.10, and 11 have a simple two-order z statistic above
1.96; at endpoints, 16 of 34 exceed 0.10. Base seed 5 ends with an order gap of
about 0.271. The reports continue to use the order-averaged generated coordinate
without a consolidated channel-validity table or a declared replacement for
the original hard gate.

The forced-choice channel is even more order-confounded and should remain
secondary or invalid where its gate fails. The generated channel may still be
usable—the paired order average and repeated samples contain information—but
the project must choose one rule: either the 0.10 threshold is a hard validity
gate, or order effects are modeled and reported statistically. It cannot be a
launch gate that silently becomes a flag after results arrive.

Cheap fix: produce one K1/K2/K3 instrument table with, by arm and round,
generated invalidity, generated order gap and uncertainty, forced order gap,
factual drop, candidate short-pool/soft-fill counts, and the number of excluded
or flagged reads. Re-run headline summaries both with all order-averaged reads
and with the preregistered-valid subset.

### 4. The let-go and transmission synthesis is not locally auditable

The local `selfaware_letgo_pilot.json` contains 12 historical cells, not the
“10 saved ensemble cells” described in the integrator report. In that artifact,
free-generation is not 0.7–1.0 in every cell: the fresh `low` controls remain
near zero, amp66 endpoints range broadly, and `amp55:7` begins near 0.679 before
ending near 1.0. The report's statement that `amp55_7` is exactly 1.0 “all
seeds, all rounds” is false for the local artifact. The claimed 3/3
corrigibility excursion is also not represented in that JSON's battery fields.

This may mean the report refers to a newer Drive-only sequential ensemble. If
so, its raw artifact and analysis manifest have not been synchronized into the
repository, so the claim cannot currently be verified. The adaptive
marker-enriched ordering plus first-event stopping also cannot estimate a
population event rate without selection correction. Results should be split
into within-endpoint replication and adaptively selected cross-endpoint search,
not pooled as an ordinary binomial sample.

The transmission script has correctly moved its executable default from
`em_dose_1000` to `em_dose_750`, but `experiments/em_transmission_cells/SPEC.md`
still names dose 1000 and uses older existence/nonexistence wording. No
transmission-cell result JSON is present locally. Current state notes say the
fresh-generator channel stayed at floor, but that conclusion needs a synced raw
artifact and consolidated report before it is used downstream.

## Script and specification audit

### Resolved, but documentation is stale

The Modal release harness no longer passes `SEEDS_CTRL_ENV=''`; the key is
omitted and the current K2 parser also ignores blank seed entries. The known-bug
warning at the end of `report_k2_full_contrast_and_release_replan.md` is now
stale. The current Modal grid is branch-gated rather than the older advertised
11-cell full grid, so its module docstring and cost description also need to be
read as historical.

### Adaptive K2 hold remains a code/protocol problem

The hold state is stored inside each result file and the code defines “first
two” relative to the job-local `SEEDS_CONF`. Split jobs therefore do not share
the intended global adaptive state. Any future adaptive gate must use explicit
named pilot seeds or load a shared, immutable decision artifact. Do not infer
global trial state from whichever subset a resumed kernel happens to contain.

### The new judge-opposition launcher needs a manipulation screen

`LAUNCH_judge_opposition.py` is reproducibly pinned to a full commit and uses a
frozen base judge, which is operationally good. Scientifically, however, the
current chassis generates and trains on self-descriptions of coding habits. A
“secure” judge may select secure-sounding admissions without selecting secure
code, so this is not the reverse of the insecure-code behavior result. A null
could mean no opposing taste, no secure candidates, or failure of transfer from
self-description to code behavior.

Before any multi-round run, generate fresh candidate pools from `amp55_7`,
`amp66_10`, and the control, score the exact same pools with secure, neutral,
and base/self judges, and report kept-minus-pool gaps plus candidate support.
This costs inference only. If the secure judge does not show a consistent
negative insecurity/code gap with adequate pool spread, stop. If the research
question is genuinely insecure-code reversal, replace the training pool with
actual code tasks and use a frozen code-security scorer; otherwise name the run
honestly as secure-self-description opposition.

### The mixed-generator spec is not launch-ready

The spec contains a direct classification error: it says convergence has
between-share entropy approaching zero. Entropy near zero means one owner
captures the kept set; convergence with balanced selection should move share
entropy toward its maximum. More broadly, a two-owner value gap does not
guarantee a permanent spread floor, and the prediction that the EM self-judge
prefers its own flavor has not been screened on owner-blind mixed pools.

Before implementation, the spec needs: a corrected regime classifier; a
selection-only taste screen; explicit independent adapter and optimizer state;
handling of zero-kept owners; owner-balanced generation order; within-owner and
between-owner controls; and a check that adapter identity is not recoverable
from irrelevant style artifacts. This design is interesting, but it should not
outrank analysis of the experiments already running.

## Updated priority plan

### Priority 0: finish and preserve the live free experiment

1. Let both K2 release kernels reach a terminal state and retrieve their JSONs.
2. Preserve exact script hashes, kernel slugs, seed allocation, and any partial
   per-round saves.
3. Do not launch Modal branch A or B while the free grid is running.

### Priority 1: cheap analyses before new training

1. **Repair K2's primary analysis.** Report the five matched pairs, all
   trajectories, arm-level distributions, and the seed-5 protocol deviation.
   Use a paired randomization/sign analysis only as a small-n descriptive aid.
2. **Fit a condition-aware transition model.** Use rollout-cluster bootstrap or
   leave-one-rollout-out validation; include `gap × condition`, current pool,
   pool spread/support, round, and prior trajectory. Report predictive error,
   not just in-sample correlation. Compare against simple baselines such as
   next pool equals current pool and condition-specific mean drift.
3. **Audit instruments across all grids.** Produce the order/invalidity/factual/
   short-pool table described above and sensitivity analyses under the original
   gates.
4. **Decompose K3 correctly.** Separate changes in mean from changes in
   between-seed variance; relate candidate-level selected candor gaps to the
   next candor pool and separately to self-report and EM behavior. Treat the
   latter two as off-axis transfer tests.
5. **Analyze saved geometry secondarily.** Existing per-round geometry fields
   can test whether movement size or alignment predicts later behavior without
   loading checkpoints. Keep this exploratory and use merged LoRA deltas where
   actual weight comparisons are made.
6. **Sync missing provenance.** Add the newer let-go and transmission raw JSONs
   to the repository before making further claims from them. If they cannot be
   recovered, mark those claims as unverified rather than reconstructing them
   from the state log.

### Priority 2: score the release grid without moving the goalposts

For each schedule, show every r4-to-r8 change, pool mean, spread, realized gap,
and judge used. Score every preregistered criterion separately. Refit transition
models with release data held out first, then added, and compare predictive
performance by condition. The highest-value question is not merely whether an
endpoint rebounds, but whether the pre-release pool and the new judge's realized
gap predict the subsequent transition out of sample.

If the free schedules all reproduce known collapse/floor regimes, stop. If the
base judge is the only arm that creates reproducible upward movement, the next
paid complement is `press_to_base` plus a matched `base_hold`, with at least
three seeds and predeclared rail/continuous outcomes. If `press_random` and
`press_release` diverge, that is more informative about endogenous self-judge
force than adding pulse shapes immediately.

### Priority 3: only then choose the next experiment

Ranked recommendation:

1. **Opposing-judge selection screen, then a two-cell pilot.** This is the
   cheapest direct test of whether a saturated Qwen EM endpoint has usable
   opposite-direction support. Use actual code candidates if the target claim
   is insecure-code behavior. Include a neutral/base control and stop if the
   manipulation gap is absent.
2. **`press_to_base` release complement**, only if the free release data leave
   the base-opposition question open and the condition-aware model predicts
   measurable movement.
3. **Mixed-generator coupling**, after correcting its spec and passing an
   owner-blind judge-taste screen. Treat it as a new exploratory mechanism, not
   a consequence of an established spread-decay law.
4. **Additional let-go cells**, only for a narrowly stated within-endpoint
   replication question. Do not resume an adaptively ordered run to estimate an
   event rate.

Deprioritize Modal pulse/early-release schedules, K4, OLMo insecure-code
organism construction, and new model families until the release results and
cheap reanalyses are complete.

## Claim language to use now

- **Supported:** judge schedule changes value-coordinate trajectories; effects
  can be heterogeneous and seed-sensitive; self-judging sometimes widens or
  accelerates movement on selected/related projections; realized selected-data
  gaps predict some next-round pool changes.
- **Promising but provisional:** selected-gap/next-pool coupling generalizes
  across organisms; early pool support helps predict rails; opposing judges can
  release a pressed state.
- **Not currently supported:** one universal integrator law; stability from
  `k < 1` and instability from `k > 1`; uniform paired K2 inversion; generic
  self-judge amplification of installed values; a population rate from the
  adaptive let-go ensemble; or mixed generators as a proven spread source.

## Bottom line

The program should not pivot to a different model simply because risk is easy
to saturate. Saturation is now diagnostically useful if the experiment supplies
an actually opposed, validated force and measures whether the candidate pool
contains movable support. The cheapest high-information path is: finish the
free release grid, repair the condition-aware and instrument analyses, screen
the Qwen opposing judge on saved/fresh pools, and run only the smallest pilot
whose manipulation check passes. That sequence can distinguish genuine basin
resistance from a missing selection signal without constructing a new organism
or spending the remaining grant.

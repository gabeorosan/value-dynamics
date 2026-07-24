# Post-Claude re-audit: what was fixed, what remains wrong, and the current plan

*Audit date: 2026-07-12. This re-audit compares the repository after commits
`9300651` through `36676d1` against the findings in
`report_current_program_audit_2026-07-12.md`. It checks the authoritative plan
and state dashboard, new analyses and figures, result provenance, experiment
specifications, and executable scoring defaults. No existing file was modified
as part of this review. At the time of re-check, both Kaggle release kernels
were still `RUNNING`.*

## Executive verdict

Claude addressed a substantial fraction of the previous audit, but **not
everything**, and the repository is currently internally inconsistent.

The strongest improvements are real:

- the newer let-go and transmission JSONs now have local provenance;
- K3 is correctly reframed as a between-seed variance result rather than a
  mean increase;
- the release scorer now prints individual preregistered criteria instead of
  one pooled verdict;
- the mixed-generator classifier's entropy direction was corrected and launch
  gates were added;
- a useful opposition-support screen identified that `amp55_7` has no secure
  candidate support;
- the weight-geometry result was demoted to an exploratory null;
- `../STATE.md` now acknowledges that K2 has five matched pairs and a heterogeneous
  3/5 paired sign, not a clean six-seed inversion.

However, several load-bearing corrections exist only as late appendices or
state-log entries. The authoritative `../PLAN.md`, headline reports, and figures
still present the claims that were supposedly retired. There are also new
analysis errors: duplicated partial records in the instrument table, a wrong
threshold in the release scorer, non-independent cross-validation grouping,
and causal conclusions that do not follow from same-pool counterfactual scores.

The immediate priority should be reconciliation and reproducible analysis, not
another organism build. Finish the free release jobs, make one post-sprint plan
authoritative, replace rather than append to superseded reports/figures, and
save the code for every central numerical result.

## Disposition of the previous audit

| Previous issue | Status now | Re-audit finding |
|---|---|---|
| K2 incorrectly described as six-seed paired confirmation | **Partially fixed** | Corrected in recent `../STATE.md`; still wrong in `../PLAN.md` and the main K2 report. |
| Pooled integrator slope treated as a universal stability law | **Partially fixed** | A late appendix retires stability language; the report opening, figures, captions, and older state entries still assert it. |
| Release scorer substituted thresholds and emitted pooled verdicts | **Mostly fixed** | Per-criterion output is better, but one bound is coded incorrectly and phase-specific judges are still pooled. |
| Generated/forced order validity not consolidated | **Partially fixed** | New table exists and rail robustness is useful; its K2 census includes a duplicate partial rollout and the promised sensitivity model is still absent. |
| K3 mean versus variance conflated | **Addressed descriptively** | New report correctly separates the mean and endpoint spread, but n=3 uncertainty and off-axis status need clearer wording. |
| Let-go and transmission artifacts absent locally | **Artifact sync addressed** | Both have provenance files; transmission still lacks a result analysis and its SPEC remains stale. |
| Mixed-generator entropy classifier backwards | **Addressed** | Classifier and launch gates are corrected; motivating law and some predictions remain overstated. |
| Opposition run lacked candidate-support screen | **Support half addressed** | Support was measured; the required judge-taste manipulation screen was not completed before the multi-round launcher. |
| Weight geometry needed a cheap secondary check | **Addressed, not reproducibly** | Exploratory null is appropriate, but no analysis script was saved. |
| Authoritative plan/state stale | **Not addressed** | This is now the largest program-management failure. |

## Priority-zero repository inconsistencies

### 1. `../PLAN.md` is still the old pre-run plan

`../PLAN.md` declares itself the single authoritative plan and says it is current
as of 2026-07-11 midday. It still says:

- K1 and K3 are merely launched;
- K2 is blocked on its exact-rung screen;
- K2 will have a six-seed confirmatory contrast;
- the screen and Kaggle attestation are pending;
- the sprint analysis and launch-order checklist have not happened;
- the OLMo insecure-code quadrant is explicitly cut.

All of these conflict with current artifacts and recent commits. K1–K3 are
complete, K2's screen passed, K2 contains only five matched conservative/base
pairs, release experiments are running, and a new OLMo insecure-code build spec
has been added. Because `../PLAN.md` explicitly wins every disagreement, appending
correct facts to `../STATE.md` does not repair the project contract.

Recommended correction: replace the old execution plan with a short
post-sprint decision plan containing completed results, live jobs, unresolved
analyses, explicit no-launch gates, and the ranked next-experiment queue. Move
the historical sprint plan below a dated archive banner or preserve it in git;
do not leave it authoritative.

### 2. `../STATE.md` remains a chronology rather than a reliable dashboard

The top Jobs table and Pending Decisions section still list old Modal, K1, K2,
K3, and Colab states. The correct information appears hundreds of lines later
under Recent changes. This defeats the instruction at the top of the file to
keep it a dashboard rather than an archive.

The line claiming “ALL audit priority-1 items now complete” is false. At least
the following remain incomplete: a deduplicated instrument analysis, saved code
for the condition-aware models, seed-grouped validation, the valid-subset order
sensitivity analysis, a transmission result report, the stale transmission
spec, and synchronization of the authoritative plan and public figures.

### 3. Retired claims remain the first and most visible claims

`report_loop_integrator_decomposition.md` still opens by calling the loop an
integrator with gain 0.75, later calls `k < 1` stable and `k > 1` unstable, and
states that the same law explains the cross-family phenomenology. Only near the
end does an “Audit response” say that these claims are superseded.

The same unsupported stability story remains in:

- `docs/figures/auto/integrator-gain-three-fits/caption.md`;
- `docs/figures/auto/integrator-gain-three-fits/figure.py` and its SVG;
- `docs/figures/fig17_loop_integrator.py` and its SVG, whose panel title says
  “One law across every condition”;
- older but still unqualified `../STATE.md` headline entries.

This is not merely historical clutter: these are the publication-facing
figures. A reader will encounter the rejected claim before the correction.
Superseded sections should be rewritten or clearly struck as historical; a
late appendix is insufficient.

The main K2 report has the same problem. It is titled “K2 full contrast” and
still says “Headline inversion confirmed,” even though the current analysis is
five matched seeds with only 3/5 paired signs favoring the conservative arm.

## Numerical and statistical issues that remain

### 1. The instrument table double-counts a partial K2 rollout

`report_instrument_validity_table.md` reports 87 K2 generated reads, 38 order
gaps above 0.10, and 4 invalidity flags. The five source files contain one
partial `frozen_cons_r0` seed-3 record with two reads, followed by the complete
seed-3 record in the v2 result. Counting both produces 87 reads.

After deduplicating by `(condition, seed)` and retaining the complete record,
the K2 census is:

| measure | reported | unique full-rollout value |
|---|---:|---:|
| generated reads | 87 | **85** |
| generated order gap > 0.10 | 38 | **36** |
| generated invalidity > 0.10 | 4 | **3** |
| forced order gap > 0.10 | 46 | **46** |
| endpoint generated gaps > 0.10 | 3/17 | **3/17** |

The report therefore mixes an all-read numerator/denominator that includes the
partial duplicate with an endpoint count that effectively uses complete
rollouts. The rail-by-order check itself is still useful: both base rails rise
in both presentation orders. The aggregate table and any downstream
percentages must be recomputed from a canonical deduplicated manifest.

The report also says its analysis is “inline below,” but contains no analysis
code. The promised full order-effect model and valid-subset sensitivity check
are explicitly left for later, despite `../STATE.md` claiming this priority item is
complete.

### 2. The revised release scorer still has two substantive errors

The rewrite is much better than the original, but:

1. The preregistered `press_hold` floor is 0.03–0.08. The scorer labels that
   criterion verbatim but implements `0.0 <= x <= 0.08`, so values below 0.03
   incorrectly pass.
2. Its “condition-aware” gain refit groups by schedule. A release schedule
   contains two different judge phases—for example conservative rounds followed
   by evolving-self or base rounds. One slope across the full schedule mixes
   the very regimes the prior audit required separating. Refit by actual
   `judge_used` and phase, ideally with schedule as an additional interaction.

Other limitations should be printed by the script: very small schedules yield
unstable bootstrap intervals; duplicate `(schedule, seed)` records are silently
overwritten according to input order; and exact threshold PASS/FAIL labels do
not convey sampling uncertainty. These are not blockers for descriptive
scoring but matter before calling the result confirmatory.

### 3. The condition-aware LORO result is not yet reproducible or fully held out

The new leave-one-rollout-out table is promising, but the commit contains only
report text and state lines—no analysis script, feature manifest, or saved
predictions. It is impossible to verify exactly how categorical intercepts,
interactions, standardization, singular fits, and duplicate K2 records were
handled.

More importantly, the grids reuse seed identifiers across judge conditions.
Leaving out one `(condition, seed)` rollout while retaining the same seed under
other conditions is weaker than independent-seed validation because matched
conditions share initialization and round-0 sampling structure. The next cheap
check should leave out **all conditions for one seed at once**. Model selection
among M0–M4 was also performed on the same LORO scores used to advertise the
best model; use a prespecified model or nested/grouped validation before quoting
the best RMSE as an unbiased generalization estimate.

The defensible current statement is: kept-gap contains held-rollout predictive
information under one plausible analysis. It is not yet a fully independent
out-of-sample validation.

### 4. The oversight counterfactual is directionally informative but causally overclaimed

The same-pool re-ranking is an excellent diagnostic: on both frozen-base rail
trajectories, the frozen conservative judge would have chosen lower-risk
candidates than the base judge from the candidate pools that actually occurred.

The report then says a conservative overseer “would have … prevented the escape
entirely.” That does not follow. Switching the judge at round 1 changes the
training data, generator, and every later candidate pool. Counterfactual scores
on the realized base-judge path identify the **one-step force sign**, not the
full alternate trajectory. The running or proposed `press_to_base`/judge-swap
experiments are precisely what is needed to test the dynamical counterfactual.

Use: “the conservative judge would have reversed the selection direction on
every realized rail pool.” Do not use: “it would have prevented the rail.”

### 5. “Axis locality” is a useful pattern, not an established law

The reported K2 on-axis correlation and K3 off-axis near-zero correlations show
that current candidate-pool coordinates predict some channels better than
others. They do not establish that loops move only the selected axis:

- the neutral judges say “Which answer is better?” rather than explicitly
  optimizing the post-hoc candor score;
- contemporaneous pooled correlations mix conditions and trajectories;
- absence of linear correlation does not show absence of off-axis movement;
- K3 itself shows large self-report endpoint variance despite near-zero
  candor-pool/self-report correlation.

The safer claim is **local predictive specificity**: realized candidate-pool
candor explains next candor-pool movement better than the tested off-axis
behavioral probes. Do not use it to assert that off-axis motion is impossible
or expected to be zero.

### 6. K3's variance result is correctly narrowed but still very small-n

The K3 endpoint population SD is about 0.39 for evolving-self versus 0.19–0.21
for other arms. This is a useful descriptive result. With only three seeds per
arm, “variance amplification” should remain descriptive and accompanied by the
three raw endpoints or a bootstrap/permutation sensitivity analysis. Calling
self-report a “selected/adjacent” projection is also too strong: empirically it
is nearly uncorrelated with the measured candor pool and is best described as a
semantically adjacent but measured off-axis channel.

## Let-go, transmission, and opposition follow-ups

### 1. The let-go artifact is now auditable, but pooled averages hide regimes

Syncing the eight-cell snapshot and its adaptive-order provenance resolves the
largest provenance problem. The 0/3 failure to replicate the `amp55_7`
strong-form event is clear and useful.

The new channel report nevertheless over-pools unlike endpoints. Endpoint-level
recalculation shows:

| endpoint | cells | mean `em_freegen` | within-cell mobility ranges |
|---|---:|---:|---|
| low_55 | 3 | 0.83 | 0.15–0.21 |
| amp55_7 | 3 | 1.00 | 0.00 in all three |
| amp66_10 | 2 | 0.53 | 0.60–0.77 |

Thus “the organism free-generates insecure code essentially always” and “the
free-gen channels are nearly immobile” are true for `amp55_7`, approximately
true at the pooled level, but false for the two `amp66_10` cells. Corrigibility
is also highly mobile in `amp66_10` (within-cell ranges about 0.24 and 0.41),
though its excursions are transient. Report results by endpoint family rather
than presenting the across-endpoint average as one regime.

The strong-form criterion remains 0/8, and the adaptive ordering still prevents
an unbiased event-rate estimate. Those conclusions are sound.

### 2. Transmission provenance is fixed; transmission analysis is still missing

The repository now contains eight rollout records: transmission ×3,
transmission-control ×3, and carrier ×2. No consolidated result report was
added, and `experiments/em_transmission_cells/SPEC.md` still names
`em_dose_1000` rather than the executed `em_dose_750`, claims three carrier
seeds, and lists unrun susceptibility/composition cells as planned work.

The raw data give a clear cheap result:

- all `em_freegen` starts and finals are effectively zero in transmission,
  control, and carrier cells;
- the forced self-report instrument is also numerically saturated at roughly
  10^-12 to 10^-10 and is not an informative secondary measure here;
- realized candor gaps are heterogeneous and do not create target-channel
  headroom.

The primary interpretation is an instrument/support null: these fresh
generators never produce measurable insecure-code behavior under any completed
judge. It is not evidence that judge taste cannot transmit in a regime with
candidate support. Write the result report and update the SPEC/provenance before
using “transmission floor” in synthesis figures.

### 3. The opposition support screen is only half of the required gate

The saved-pool support screen correctly finds:

- `amp55_7`: 0% candidates below the chosen insecurity threshold—uninformative
  for selection-based reversal;
- `amp66_10` and `low_55`: mixed candidate support and therefore potentially
  informative.

But the previous audit required both support **and judge taste** before a
multi-round run. The new report says the secure judge's realized kept-gap “comes
free from the run itself,” which turns the manipulation gate into a post-hoc
diagnostic. A selection-only pass of the frozen secure judge over saved or fresh
pools should precede training. If the run is already underway, interpret only
cells with a demonstrably negative realized insecurity gap and do not count the
`amp55_7` cells as a test of basin resistance.

The original naming caveat remains: the chassis trains on self-descriptions of
coding habits. It tests secure-self-description selection, not direct reversal
of insecure code generation. An actual insecure-code reversal experiment needs
code-task candidates and a frozen code-security scorer.

## New specifications and reprioritization

### Mixed-generator spec: improved but still exploratory

The entropy classifier, support-law caveat, owner-blind screen, and independent
state requirements are genuine improvements. Remaining issues:

- the opening still states the obsolete spread-exhaustion mechanism as fact
  before later calling it a hypothesis;
- the self-judge capture prediction assumes an own-flavor preference that the
  required taste screen has not established;
- share entropy alone cannot separate alternating deterministic capture from
  balanced stochastic selection; use the full owner-share time series and
  transition counts;
- a surface-feature shuffle classifier needs a specified feature set,
  cross-validation unit, and threshold before it can be a launch gate.

Do not implement the full grid until the owner-blind inference screen passes.

### OLMo insecure-code build: not the current highest-value next step

The new spec is careful about checkpoint pinning and completion-only masking,
but it should remain deferred:

- building an organism does not test the gain hypothesis; a later dynamics
  grid is required;
- one additional OLMo organism cannot “rule out family” because organism, value
  axis, training recipe, and family remain confounded;
- Qwen hyperparameters are not automatically model-agnostic, especially for a
  4-bit LoRA dose ladder;
- the forced self-report instrument needs a base-headroom and order-symmetry
  screen before it can serve as an acceptance gate.

This is a reasonable matrix-completion asset after the current release and
opposition questions are resolved, not a decisive or immediate experiment.

## Updated action plan

### Do now, with no new GPU spend

1. Let both running Kaggle release kernels finish; retrieve outputs and preserve
   their exact script hashes and partial-save provenance.
2. Replace `../PLAN.md` with a current post-sprint plan and refresh the top Jobs and
   Blockers sections of `../STATE.md`.
3. Rewrite the main K2 and integrator reports so the corrected claims are the
   main text, not appendices. Regenerate or withdraw figures that still say one
   law, stable/unstable `k`, or confirmed full inversion.
4. Create one canonical rollout manifest that deduplicates partial/resumed
   records by `(grid, condition, seed)` and records which source file won.
5. Save the condition-aware analysis as a real script. Add leave-one-seed-out
   grouped validation, predeclare the comparison model, and publish held-out
   predictions/residuals.
6. Recompute the instrument table from the canonical manifest and complete the
   valid-subset/order sensitivity analysis.
7. Fix the release scorer's 0.03 lower bound and stratify transition fits by
   actual judge phase.
8. Write the transmission result report from the synced JSON and update its
   SPEC to the executed cells, judge, seed counts, and null instruments.

### When the release outputs land

Score every preregistered criterion separately, preserving contradictions in
the preregistration rather than resolving them after seeing data. Show each
seed's r4-to-r8 trajectory, pool support, realized judge gap, and phase. Test
the transition model first with release data held out, then refit only after
reporting the prospective error.

If the free release arms reproduce known collapse/floor regimes, stop. If the
base phase shows reproducible upward movement not explained by pool support
alone, `press_to_base` plus matched `base_hold` remains the most informative
small complement. Do not launch pulse schedules merely because they already
exist in the Modal harness.

### Next experiment decision

Ranked recommendation after the free jobs:

1. **Frozen secure-judge taste screen on informative Qwen pools**, inference
   only. Continue with a two-cell training pilot only if the realized gap is
   consistently opposed and candidate support is adequate. Exclude
   support-starved `amp55_7` from the causal verdict.
2. **Small `press_to_base` complement**, only if release results and the
   corrected phase-aware model leave a clear unresolved prediction.
3. **Mixed-generator inference screen**, followed by a pilot only if its
   owner-blind taste and artifact gates pass.
4. **OLMo insecure-code organism build**, later, as a matrix expansion rather
   than a decisive family test.

Do not resume adaptive let-go sampling for an event-rate claim, do not spend on
Modal pulse/early-release schedules before the free results, and do not call the
audit complete until the authoritative plan, central reports, and public
figures agree with the corrected analyses.

## Bottom line

Claude implemented many useful local fixes, but the repository still tells two
different scientific stories. The recent appendices say the effects are
condition-dependent, descriptive, and small-n; the authoritative plan, main
reports, and figures still say six-seed confirmation, one universal law, and
stable versus unstable integrators. The correct next step is not more breadth.
It is to make the corrected story reproducible and authoritative, then use the
already-running release experiment and a genuinely gated opposition pilot to
decide whether any new compute is warranted.

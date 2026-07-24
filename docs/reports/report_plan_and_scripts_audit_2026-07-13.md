# Plan and executable-surface audit — 2026-07-13

*Scope: the authoritative plan/dashboard, all completed release artifacts, all
active analysis scripts, all currently runnable forward-queue launchers, the
shared self-awareness chassis, the Modal release harness, and the queued OLMo
spec. This audit compiled all 142 tracked Python files, reran the manifest-fed
transition and instrument analyses, reran release scoring and frozen-predictor
scoring, and spot-recomputed load-bearing claims from raw JSON. It creates only
this report.*

## Executive verdict

The completed K1–K3 and release artifacts are now substantially better
organized and the core transition signal survives the newest checks. The
forward queue, however, is **not launch-ready as a whole**.

The two most important findings are:

1. The frozen release predictor's reported “matched no-gap baseline” is not a
   separately fitted no-gap model. It reuses intercepts estimated jointly with
   the gap slope and merely zeros the slope. A correctly refitted K2-only
   condition-intercept baseline reduces the reported prospective advantage
   from -25.1% to about **-17.3% on kernel B**, and from -37.7% to about
   **-31.1% on Modal branch A**. The gap signal still wins overall, but not in
   every schedule phase; it is worse on the `fan_press/evolving_self` phase.
2. The mixed-generator pilot is scientifically and operationally under-gated.
   The source pools mostly compare actual code from owner A with reflective
   prose from owner B—53/72 A candidates match a simple code signature versus
   0/72 B candidates. The pilot does not enforce the normalized-screen gate,
   does not save the normalized text the judge sees, lacks candidate-validity
   checks and per-round checkpoints, and implements only P1 although the plan
   promises P1 plus P3.

The corrected oracle-opposition selector is much improved, but it reuses the
same result filename and `judge_style` label as the earlier wrong-axis oracle.
A completed old cell could be silently skipped and then analyzed as corrected.
Use a new versioned result name and embed the source/axis contract before
continuing.

Recommended order: finish and provenance-lock the currently running oracle;
repair and run only the normalized inference screen; fix the predictor
baseline and press-depth metric/scorer; then decide whether either the coupled
pilot or press-depth branch deserves compute. Do not launch the current coupled
pilot or branch C unchanged.

## Current plan audit

### What is right

The forward queue correctly deprioritizes rate-only replication and keeps the
OLMo insecure-code build last. It also correctly keeps Modal pulse/early-release
branch B unlaunched after the completed release grid showed no unexplained
rebound. The remaining unattended budget is aimed at diversity-shaped designs
rather than more seeds in known endpoint regimes.

The completed-state summaries for K1–K3, transmission, let-go, and the
oversight counterfactual are mostly aligned with the corrected reports. The
release result is now fully retrieved: kernel B and all five Modal branch-A
cells are local and included in the manifest.

### What is stale or contradictory

The header still says the plan is current as of 2026-07-12 22:30, while the
forward queue contains decisions through 2026-07-13 01:20. Its Live jobs section
still says kernel B is running and Modal branch A is merely launched; both are
complete. `../STATE.md` has the completed rows, but its Pending decisions still
says “Kernel B + Modal branch A land.” The mixed screen row still says READY
even though the first screen landed and failed its style gate.

The forward queue numbering jumps from item 3 to item 5. More substantively,
it describes the normalized re-screen as sufficient to green-light P1 plus P3,
but the only coupled-pilot launcher implements P1/base-judge. It also describes
adapter assets on a Modal volume in older live text while the ready launchers
use Google Drive and Colab.

Budget language needs one explicit ledger: the plan says roughly $13 remains
inside the unattended $20 allowance, while `../STATE.md` says roughly $80 of the
total grant remains. Both can be true, but future launch decisions should show
total grant, unattended authorization, spent-to-date, and proposed spend in one
table.

### Recommended authoritative queue

1. Running corrected oracle: retrieve/version-check/analyze only.
2. Normalized mixed-pool re-screen after the script fixes below.
3. Decide between a repaired same-domain coupled pilot and a repaired
   press-depth map. Do not assume both will launch.
4. OLMo insecure-code build remains deferred and is not executable yet; it has
   a SPEC but no implementation script.

## Completed release-grid analysis

### The raw result is useful

The 14 release rollouts show four clear descriptive patterns:

- release to evolving self continued toward the floor in all three seeds;
- random release wandered more than preregistered but did not rail;
- conservative selection after an initial self phase drove both `fan_press`
  seeds to zero;
- base judging produced the only upward escapes, including 2/2 `base_hold`
  rails at horizon 8 and two of three `press_to_base` upward trajectories.

These justify stopping pulse/early-release branch B. They do not yet justify
an “absorbing state regardless of judge” law: exact-zero switch pools were
observed under base, self, and conservative successor phases, not under an
exact-zero random successor, and a finite sampled pool at zero does not prove
the generator can never regenerate support.

Use: **observed zero-support paths stayed at the floor under the tested
directed judges.** Avoid: **the state is absorbing regardless of judge.**

### The spread metric changed silently

The original release preregistration defines spread as the mean, over loop
items, of the within-item SD of six candidate risks. The release report's
quoted switch spreads near 0.2 for `press_to_base` seed 2 and 0.15 for seed 3
are instead the SD across item-level pool means.

Using the preregistered mean-within-item-SD definition at the base-judge switch:

| cell | report-style across-item SD | preregistered mean within-item SD | r8 |
|---|---:|---:|---:|
| press_to_base s1 | 0.000 | 0.000 | 0.000 |
| press_to_base s2 | 0.186 | **0.328** | 0.389 |
| press_to_base s3 | 0.164 | **0.392** | 0.750 |

The qualitative support ordering survives, but the numerical mechanism claim
and the press-depth thresholds must use one named formula. The press-depth
preregistration currently says “within-pool spread” without defining it.

### The frozen predictor baseline is misfit

`freeze_release_predictor.py` fits arm intercepts and a pooled gap slope jointly,
then defines the no-gap comparator by retaining those joint-fit intercepts and
setting the slope to zero. That is an ablation, not a fitted no-gap model. The
proper K2-only no-gap arm intercepts are the arm mean drifts fitted without a
gap term.

Recomputed results:

| release set | frozen M2 | reported zeroed-slope baseline | properly refit no-gap | M2 improvement vs proper baseline |
|---|---:|---:|---:|---:|
| kernel B, fully blind | 0.0476 | 0.0636 | **0.0576** | **-17.3%** |
| Modal branch A | 0.0647 | 0.1039 | **0.0939** | **-31.1%** |

The headline signal survives. The claim that it improves every schedule-phase
group does not. Against the properly refit comparator, the
`fan_press/evolving_self` phase is worse: RMSE 0.0611 versus 0.0404, about
**+51%**. Other kernel-B phases and all Modal phases improve.

Do not overwrite the frozen predictor artifact. Add a separately frozen,
properly fitted no-gap comparator and correct the report. Press-depth criterion
5 must compare against that comparator, not the zeroed-slope ablation.

### Other release-report overstatements

- “Directional structure was predicted correctly everywhere” is too broad:
  fan-press dispersion/order dependence, random flatness, press-hold
  monotonicity, and most press-to-base endpoint magnitudes failed.
- “Press dominates history” rests on two fan-press seeds compared with one
  press-hold seed. It is a useful observation, not a general dominance result.
- The increase from 2/6 four-round base rails to 2/2 eight-round rails is
  suggestive and includes a matched seed that crosses later, but 2/2 is not a
  stable long-horizon rate estimate.

## Script-by-script audit summary

| Script/surface | Status | Main finding |
|---|---|---|
| `build_rollout_manifest.py` | **Pass with minor hardening** | Correctly deduplicates and verifies source hashes; should also hash winning record content/config, but current behavior is sound. |
| `analysis_transition_model.py` | **Pass** | Explicitly excludes measure-only and adds matched no-gap baselines; M2 beats its matched twin in 12/13 seed folds. Add fold uncertainty to reports. |
| `analysis_instrument_table.py` | **Pass** | Correct dual census and per-order fan ranges; full random-effects model remains optional/open. |
| `score_release_prereg.py` | **Pass for original schedules** | Reproduces 6/13 table and phase fits; it does not score press-depth criteria. |
| `freeze_release_predictor.py` | **Needs correction** | Predictor itself is frozen correctly; comparator is not separately fitted and overstates gain. |
| `modal_k2_release/app.py` | **Chassis validated, branch C not ready** | A worked; C schedules compile. Help/docstrings omit branch C, no branch-C scorer, and spread formula is unspecified. |
| `colab_selfaware_loop_grid.py` | **Oracle logic corrected, resume unsafe across versions** | Uses `cand_sr` and bleed filter correctly; result lacks a source/axis contract and reuses old oracle identity. |
| `LAUNCH_oracle_opposition.py` | **Do not trust mixed-version resume** | Correct SHA and grad-checkpoint workaround, but same filename as wrong-axis run can contaminate/skip. |
| `analyze_oracle_opposition.py` | **Mostly sound** | Missing-force accounting is good; 0.15 movement threshold is not noise-calibrated/preregistered. |
| `LAUNCH_owner_blind_screen.py` | **Historical run only** | First result is unpinned and strongly response-type-confounded; do not treat its taste decomposition as clean security preference. |
| `LAUNCH_normalized_rescreen.py` | **Needs gate redesign/provenance** | Pinned and LOQO-fixed, but gate direction/fidelity and value-matched style control are insufficient. |
| `analyze_normalized_rescreen.py` | **Needs gate correction** | Adds useful fidelity analysis; GO rule is directionless and can pass despite wrong-signed taste. |
| `LAUNCH_coupled_pilot.py` | **Not launch-ready** | Does not enforce gates, omits P3, normalized judge text, validity filters, checkpoints, broader battery, and provenance hashes. |
| `analyze_mixed_pilot.py` | **Logic bugs** | Signed-gap and starvation/convergence classifiers can mislabel regimes. |
| OLMo insecure-code | **Spec only** | No executable script; remains appropriately last. |

Repository-wide static result: all **142 tracked Python files compile** and
`git diff --check` reports no whitespace errors. These checks do not cover GPU
runtime, Drive paths, scientific validity, or resume semantics.

## Oracle-opposition scripts

### Corrected selection logic

The chassis now selects with

`score = -(cand_sr + 10 * cand_bleed)`

so lower insecurity admission is preferred and off-topic candidates are
strongly penalized. It logs `sr_support_items` and keeps generic `cand_em` as
an off-axis readout. This correctly fixes audit round 4's construct error.

### Version-contaminated resume risk

The earlier wrong-axis oracle and corrected oracle use all of the same:

- `JUDGE_STYLE_ENV=oracle_secure`;
- result name `judge_opposition_oracle.json`;
- cell keys `low_55:101` and `low_55:202`.

The chassis skips a cell whenever its battery length reaches `ROUNDS`; it does
not verify source commit, oracle axis, score formula, model revision, or adapter
hash. If an old wrong-axis cell completed before the gradient-checkpoint crash,
the corrected launcher will silently keep it. The analyzer cannot distinguish
versions because both are labeled `oracle_secure`.

Required immediate repair: use a new result name such as
`judge_opposition_oracle_sr_v2.json`; add top-level config containing source
SHA, model revision, adapter hash, `oracle_axis=cand_sr`, bleed threshold/weight,
steps, seeds, and prompt/scorer hashes; refuse resume on mismatch. Quarantine
the old file rather than merging it.

The baseline entropy seed uses Python's randomized `hash(dose)`, so it is not
stable across processes. Replace it with a fixed mapping or cryptographic hash.

### Analyzer threshold

The analyzer calls endpoint movement greater than 0.15 “moved.” That threshold
is not tied to the measure-only/noise estimate or declared in the launcher.
Report continuous delta and a noise-calibrated threshold first; keep 0.15 only
if explicitly preregistered before reading the result.

## Mixed-generator screens: the current construct is not just a style leak

The first mixed screen's raw candidates expose a larger problem than its
five-feature classifier:

- owner A: **53/72** candidates match a simple code signature, mean length
  about 263 characters;
- owner B: **0/72** match that signature, mean length about 404 characters and
  are overwhelmingly reflective prose.

The questions ask the assistant to describe its coding habits. Many owner-A
outputs are literal vulnerable code and therefore off-format; owner-B outputs
answer the question. A neutral judge preferring B can reflect on-topicness,
response type, verbosity, base-style self-preference, security content, or all
of them. The reported within-owner correlation of -0.31 does not isolate
security taste because, within owner A, lower “insecurity admission” may also
identify the few candidates that are actually self-descriptions rather than
code snippets.

The original report's value-matched classifier and within-owner correlations
also have no saved analysis script. The raw artifact contains only the original
0.9167 gate result; the 0.835 and correlation decomposition live in prose.

### Better redesign

Use one response domain for both owners:

- best for insecure-code behavior: give both owners actual code tasks, score
  code security, and let the judge compare code solutions;
- if retaining self-description: enforce an on-topic prose validity gate before
  pooling, replenish rejected candidates per owner, and score admission only on
  valid self-descriptions.

Paraphrasing code into prose can be an exploratory normalization, but it does
not make the original generator distributions equivalent and may alter the
value-bearing content.

## Normalized re-screen

The normalized launcher fixes revision pinning, fold-local standardization,
and leave-one-question-out evaluation. Remaining problems:

1. Gate (a') uses `abs(A-share - 0.5) > 2 SE`; it passes a strong preference in
   either direction. The intended base-security gate should require A-share
   significantly **below** 0.5 and a negative insecurity kept-gap.
2. Gate (b') asks owner classification to fall below 0.65 while gate (a')
   requires the owner value gap to remain above 0.15. Preserved value content
   can itself make owner recoverable through length/format features. Repeat the
   classifier within value-matched strata or residualize features against
   `sr_norm`; otherwise a scientifically successful normalization can fail the
   “style” gate for value reasons.
3. The fidelity analyzer gates only on overall correlation >0.5 and global mean
   shift <0.25. Add owner-specific fidelity, binary admission preservation, and
   per-question checks. Overall correlation can hide systematic distortion of
   one owner.
4. The result file has no source-candidate hash, model/scorer/prompt hashes, or
   config-mismatch resume guard.
5. Only frozen-base judging is rerun. The self-judge premise is deferred to
   pilot round 0, but the pilot does not implement a pre-training round-0 gate.

Do not turn a screen PASS directly into training GO until these are resolved.

## Coupled-generator pilot

The current launcher should not run under the standing plan.

### Plan/implementation mismatch

The plan promises P1 base-judge plus P3 cross-value, two seeds each. The script
implements only `p1base` with dose-750 versus fresh. There is no persona/risk
owner, cross-value scorer, or P3 condition.

### Missing enforced gates

The header says run only after normalized gates pass, but the script never
loads `mixed_screen_normalized.json`, never validates its config, and never
asserts gate/fidelity PASS. `JUDGE_NORM_ENV=0` can also bypass normalization
without a separate result namespace.

### Missing audit data and validity

- normalized texts used for judging are not saved in each raw record;
- no on-topic or response-type validity filter/replenishment exists;
- no normalized-vs-original fidelity score is logged per round;
- only forced self-report is measured—no `em_freegen`, `sr_freegen`,
  `em_choice`, off-target battery, or measure-only comparator;
- no per-round adapter checkpoint is persisted despite the standing
  non-negotiable plan requirement;
- adapter/source hashes and exact gate artifact are absent from config;
- resume validates neither configuration nor gate artifact.

### Analyzer classification bugs

`analyze_mixed_pilot.py` uses signed `owner_sr_gap` where regime definitions
need gap magnitude. A negative large gap is incorrectly classified as
convergence. The convergence branch also ignores its stated mixed-share
condition. Starvation counts rounds where *either* owner has zero rows, so
alternating zero-owner rounds can label starvation even when neither owner is
starved for half the run. Fix these before any result exists.

## Press-depth branch C

The schedule implementation is simple and likely executable, but the
experiment contract is incomplete.

1. Define switch spread exactly as `mean_item SD(candidate_risk)` or another
   named formula and use it consistently with prior reports.
2. “Depth predicts outcomes only through this mediator” is not identifiable
   from six scheduled cells: depth determines the switch state and no
   intervention holds support fixed across depth. Treat support as a predictor,
   not proven mediator.
3. `score_release_prereg.py` has no `press_d1/d2/d3` criteria. Add a dedicated
   scorer that emits all five preregistered tests, switch metrics, and frozen
   predictor comparison before launch.
4. Correct predictor criterion 5 to use a separately fitted no-gap comparator.
5. The Modal help/error text still advertises only branches A/B and the old
   11-cell cost envelope. Record branch-C app/run IDs and script hash at launch.

The design is potentially useful after these fixes. Its two seeds per depth
remain an exploratory boundary map, not evidence for a sharp universal basin
boundary.

## Updated priority plan

### Priority 0 — protect running work

1. Give the corrected oracle a versioned output path and config contract now.
   If it is already running, inspect the existing Drive file before allowing
   resume; do not mix old and corrected cells.
2. Retrieve the oracle artifact on completion and run the analyzer only after
   verifying each kept set is consistent with `cand_sr`-primary scoring.

### Priority 1 — cheap analysis/script repairs

1. Add the properly refit no-gap comparator and correct the release report's
   -17%/-31% overall results and fan-press exception.
2. Recompute release switch support with one declared spread formula.
3. Repair normalized-screen directional, value-matched, fidelity, provenance,
   and resume gates.
4. Repair `analyze_mixed_pilot.py` even if the pilot remains gated.
5. Add a press-depth scorer and narrow mediator language before any branch-C
   launch.

### Priority 2 — choose one diversity experiment

After the oracle and normalized screen land:

- If a same-domain, style-controlled mixed pool still has real judge taste and
  value support, run a **minimal P1 coupled pilot** with full raw logging and
  checkpoints. Do not advertise P3 until implemented.
- Otherwise, run the repaired **press-depth boundary map**, which uses the
  validated OLMo chassis but remains exploratory at two seeds per depth.
- Do not spend on both automatically merely because the unattended envelope
  allows it.

### Priority 3 — later expansion

The OLMo insecure-code build remains last. Implement and dry-run an actual
script only after current dynamics questions are resolved; keep it as matrix
expansion rather than a decisive family test.

## Bottom line

The project now has a credible central result: realized kept-gap improves
prediction of next-pool movement across the original grids and still improves
overall on unseen release schedules, even after correcting the no-gap
comparator. The next-step machinery is less mature. The current mixed pools
confound owner with response type, the coupled pilot omits its own gates and
audit data, the oracle resume can mix incompatible implementations, and the
press-depth preregistration lacks a stable metric/scorer. Repair those scripts
before launching more GPU work; the plan should choose one clean diversity
experiment rather than running every newly authored branch.

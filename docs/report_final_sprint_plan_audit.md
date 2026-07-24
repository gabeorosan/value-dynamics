# Audit — Unified final-sprint plan

*Written 2026-07-10. Audited plan:
[`plan_final_sprint_unified.md`](plan_final_sprint_unified.md). This report
supersedes the earlier audit of `updated_research_plan_2026-07-10.md`, which was
not the latest plan. Scope: causal identification, instrument validity,
implementation readiness, statistical power, compute budget, and artifact
provenance. No experiment or planning file was changed during the audit.*

## Executive verdict

The unified sprint plan is substantially better than the earlier planning
documents. It correctly consolidates the work into a judge × generator matrix,
uses a moderate Qwen organism, makes random-selection controls firm, introduces
frozen round-0 organism judges, mandates factorization-invariant LoRA logging,
and cuts several distracting branches.

It should not yet launch exactly as written. The highest-priority OLMo experiment
has one implementation bug and lacks a direct manipulation gate on the criterion
that actually selects loop candidates. The plan also overstates the effective
sample size of the Qwen baseline, underpowers the headline OLMo contrast, and
asks some small experiments to identify more dynamical structure than their
designs support.

The recommended amendment is narrow:

1. fix the OLMo conservative installer;
2. prove that the conservative and base OLMo judges rank the same gamble
   candidate pools differently;
3. run K1;
4. increase K2 from three to approximately six seeds;
5. run K3 if its smoke test passes;
6. make K4 the first full run cut;
7. use actual candidate-selection gaps, not generic advice taste, as the
   criterion-channel mediator.

## 1. What the unified plan gets right

The following choices should be preserved:

- **Moderate rather than saturated Qwen organism.** The `mod65` pilot starts at
  risk 0.33–0.44 and leaves room for movement in both directions.
- **Loop-side position repair.** Gamble position is randomized in the training
  loop rather than only counterbalanced at evaluation.
- **Four-way judge controls.** Evolving self, frozen round-0 organism, frozen
  base, and random selection separate several previously confounded forces.
- **Random-selection control is firm.** This is required to distinguish
  judge-directed selection from generic SFT/process drift.
- **Frozen-base control added to transmission.** Movement under a drifted judge
  can now be compared with ordinary base-Qwen loop drift.
- **Per-round adapter persistence.** This makes later copy-judge, vintage,
  remeasurement, and invariant geometry analyses possible.
- **Merged-update geometry.** Norms and cosines are specified on functional
  `B·A` products rather than non-identifiable raw LoRA factors.
- **Scope discipline.** OLMo × insecure-code, Qwen3.5, DPO, the full regime
  grid, J-lens, and further λ sweeps are explicitly out of the sprint.
- **Analysis day is protected.** Sunday is allocated to synthesis rather than
  automatically starting another run.
- **K4 comparability requirement.** The content arms share the mod65 organism,
  harness, and seed schedule with K1.

These changes address many of the project's earlier failure modes and are the
right foundation for a final sprint.

## 2. Launch blockers

### 2.1 The OLMo conservative installer uses whole-sequence loss

The K2 prerequisite script describes itself as matching the Qwen persona recipe,
but its collator copies the entire prompt and answer into `labels`:
[`colab_olmo_conservative_install.py`](../experiments/olmo_conservative/colab_olmo_conservative_install.py#L239).
The Qwen basin persona recipe masks the prompt and trains only the assistant
completion.

This matters because most tokens in each row belong to the system/user gamble
prompt, while the intended supervision is one assistant letter. Whole-sequence
loss can:

- spend most of the gradient reproducing the prompt template;
- produce avoidable off-target drift;
- make the dose ladder incomparable to the Qwen organism;
- entangle conservatism with prompt memorization.

**Required fix:** set labels for every system/user/padding token to `-100` and
train only on the assistant completion. If the current install has already
produced adapters, treat them as invalid K2 prerequisites and rerun after the
masking fix.

Two smaller implementation corrections should accompany it:

- pin an immutable OLMo model revision rather than loading mutable `main`;
- when an overshoot selects the previous rung, record the previous rung's value
  in the verdict rather than the overshot current value.

### 2.2 K2 does not prove that the loop-relevant judge was inverted

The unified plan interprets OLMo's native judge prior as weak because a fixed
six-pair generic-advice battery reports `p(prefer bold) ≈ 0.52`. But the original
OLMo loop provides a different and more directly relevant observation: on the
actual gamble candidate pools, both OLMo judges kept approximately 78–79%
gamble-choosing answers from pools that were only approximately 47% gamble
([`report_basin_lightning_partial.md`](report_basin_lightning_partial.md#mechanism-from-the-full-jsons-the-judges-own-preference-sets-the-attractor-direction-and-it-flips-between-substrates)).

The two instruments are therefore not interchangeable. Near-neutral taste on
generic advice does not show a weak risk-selection prior in the loop.

Before K2, generate mixed gamble candidate pools once and score every candidate
under:

1. frozen base OLMo;
2. frozen conservative OLMo;
3. optionally the current evolving conservative model as a descriptive third
   scorer.

For each judge report:

- gamble fraction in the whole pool;
- gamble fraction in the kept set;
- kept-minus-pool semantic gap;
- candidate length, validity, and style features;
- paired per-item differences between the judges.

**K2 gate:** the frozen conservative and frozen base judges must rank the same
candidate pools in clearly different semantic directions. Behavioral risk in
the 0.25–0.40 band and generic advice-taste headroom are not sufficient.

### 2.3 Generic `judgment_taste` cannot carry the criterion-channel claim

The Sunday plan treats fixed advice-pair `judgment_taste_t` as the replacement
criterion measure and asks whether it predicts `Δx[t+1]`. The banked results
already show this probe is off-format:

- mod65 behavior fans from final risk 0.111 to 0.639 while all 18 advice-taste
  readings remain between 0.373 and 0.402;
- OLMo's release flow shows advice taste near 0.5 while its actual gamble
  candidate selection is strongly risk-loaded.

The primary judge mediator should instead be the selection gap on the actual
candidate pool:

> `mean semantic_value(kept) − mean semantic_value(pool)`

Log the gap for every judge, item, and round. Cross-score each pool with the
fixed base and fixed organism judges even when only one judge controls the
training arm. This separates changes in candidate supply from changes in judge
ranking. Keep generic `judgment_taste` as an off-format secondary readout.

## 3. Statistical and causal-design problems

### 3.1 K1 has four frozen-base rollouts, not eight independent equivalents

K1 specifies four seeds under each judge condition but describes the frozen-base
arms as `n=8 arm-equivalents`. Repeated A/B presentation orders are measurements
within a rollout, not independent experimental units. Unless four additional
frozen-base seeds are added outside the table, the baseline is `n=4`.

The K1 frozen-base arm also cannot directly recalibrate the old let-go thresholds.
K1 starts from the moderate mod65 organism around risk 0.36; the legacy let-go
arc starts from a different, substantially riskier adapter/state. If the drift is
state-dependent, mod65 decay is not a matched comparator.

K1 can establish a new order-balanced mod65 baseline. Re-scoring the legacy
let-go claim requires a matched starting adapter/state or a new let-go arc built
from K1 vintages.

### 3.2 Randomized prompt order does not guarantee balanced kept data

The mod65 pilot is an important success: the large behavioral fan survives loop
prompt randomization. It also exposes the next confound. Seed 2 develops an
order gap near 0.50, and kept-letter imbalance precedes widening in two of three
seeds.

Randomizing whether the gamble is A or B in the candidate prompts only balances
the field. The top-2 selection step can produce a severely imbalanced kept set,
after which training can still install a letter policy.

Recommended options:

- enforce order balance in the kept rows; or
- add an order-swapped semantic equivalent of every kept row; or
- preregister a maximum allowable longitudinal order gap and invalidate semantic
  conclusions in cells that exceed it.

Logging the gap is necessary, but merely labeling a large gap exploratory is not
enough for a load-bearing semantic-risk claim.

### 3.3 K2 is underpowered for its role

K2 is described as the headline causal test but receives only three seeds. This
project's central empirical feature is large seed variability; repeated rounds
do not replace independent rollouts.

With three seeds, a large, unanimous effect can support a pilot or existence
claim. It cannot reliably estimate a judge-condition × round interaction or its
distribution across seeds.

**Recommendation:** cut K4 and reallocate its approximately five hours plus a
portion of the buffer to expand K2 to about six seeds. Predefine the confirmatory
contrast as frozen-conservative versus frozen-base OLMo. Treat the evolving and
random arms as mechanistic controls around that contrast.

### 3.4 K4 cannot identify fixed point, stiffness, and noise

K4 has three seeds, four rounds, and one starting state per content arm. That is
enough to compare trajectories or final states. It is not enough to separately
identify:

- equilibrium/fixed-point location;
- restoring stiffness;
- process-noise structure.

The plan also needs to specify:

- external/self-data mixing ratio;
- total examples and tokens per round;
- optimizer steps and effective learning-rate exposure;
- option-order balance in the external rows;
- whether K1 and K4 use identical round-0 adapters and prompt banks.

If K4 runs, its confirmatory endpoint should be a trajectory or final-state
difference versus the K1 evolving-self baseline. Fixed point, stiffness, and
noise remain exploratory.

### 3.5 The composition cells are not bias-free one-dimensional field samples

Placing different organisms or vintages at different measured `x` values avoids
the original regression-to-the-mean error, but it changes far more than `x`.
Adapters with different training histories differ in many latent directions.

The composition cells are useful constructed-state comparisons; they are not a
causal one-dimensional drift-field intervention. A stronger field design would
move one underlying adapter along a controlled direction or interpolation while
holding other state approximately fixed.

## 4. Judge-transmission branch

### 4.1 Scheduling logic must be made consistent

[`plan_judge_transmission.md`](plan_judge_transmission.md) describes the loop
cells as gated on both the screen and successful Phase 1B. The unified sprint
schedules them in parallel with K2.

The later addition of a frozen-base-judge control makes the transmission loop
independently interpretable: drifted judge versus base judge on the same fresh
generator directly tests the judge effect. Parallel execution can therefore be
scientifically defensible.

The documents should explicitly adopt that newer logic. Otherwise the recorded
preregistration simultaneously says the cells are contingent and already
scheduled.

### 4.2 The carrier screen needs fresh-pool validation

The carrier finding is currently based on one fixed candidate pool and
top-2-of-6 selection. The `+0.127` amp66_12 gap is promising, but rankings are
quantized and the endpoint was selected after inspecting the same screen.

Before launching the carrier loop:

- generate at least two additional candidate-pool seeds;
- score them without changing the chosen carrier labels;
- require the amp66_12 versus base difference to reproduce in sign;
- keep the framing as an existence/mechanism test, never a rate estimate.

Until then, the screen supports “carrier candidate detected,” not a confirmed
portable taste.

## 5. Compute and execution risks

### 5.1 Throughput estimates need smoke-based recalculation

The 8-minute Qwen and 17-minute OLMo anchors include older batteries. The unified
plan adds the full battery patch, steering artifacts, raw per-question reads,
distinct-n, invariant geometry, and adapter persistence. With TPU removed, all of
this runs inside the T4 critical path.

The Friday smoke tests should produce measured minutes per condition-seed-round.
Recompute the entire K1–K4 budget from those measurements before any full push.

### 5.2 Adapter persistence needs a storage/retrieval preflight

Rounds 0/2/4 across all planned cells create roughly 150 persisted adapter
directories. Depending on adapter rank and target modules, this can total several
gigabytes.

Before launch verify:

- per-kernel output/storage limit;
- progressive packaging or retrieval;
- resume behavior if the kernel stops after writing some vintages;
- manifest mapping every adapter to model revision, condition, seed, and round.

### 5.3 Banked raw artifacts must be copied locally

The mod65 and judge-transmission JSONs currently live on Drive, while repo figures
contain transcribed numbers. Before Sunday analysis, copy the raw JSONs into the
appropriate output directories and record hashes. The analysis should read the
JSONs, not figure-script constants or STATE summaries.

### 5.4 K1–K4 are not yet represented by runnable repo scripts

At audit time the workspace contains the unified plan, the screen, and the OLMo
installer, but not final K1–K4 scripts/specs. The three-hour pilot budget is
therefore still an estimate. Each run needs a local SPEC, explicit primary
endpoint, gate logic, output path, and static/smoke verification before push.

## 6. Recommended amended sprint

### Before Kaggle

1. Fix the OLMo installer's completion-only loss and immutable revision.
2. Rerun the OLMo dose ladder if any adapters were produced with whole-sequence
   loss.
3. Add the actual gamble-candidate judge-inversion screen.
4. Validate carrier candidates on fresh candidate pools.
5. Build K1–K3 with actual selection-gap cross-scoring.
6. Time one full round of every condition with the in-loop battery.
7. Sync the banked Drive JSONs locally.

### Kaggle priority

| Priority | Run | Amendment |
|---|---|---|
| 1 | K1 Qwen anchor | Count independent seeds honestly; balance or invalidate letter-skewed kept sets; interpret as a mod65 baseline |
| 2 | K2 OLMo inversion | Require direct judge inversion on actual pools; expand to about six seeds |
| 3 | K3 EM controlled grid | Keep evolving/frozen-organism/frozen-base/random controls; existence framing at n=3 |
| 4 | Resume and retrieval buffer | Protect artifacts and complete interrupted cells |
| 5 | K4 content arms | Run only if K1–K3 finish early; otherwise defer |

### Colab

- Transmission and carrier loops may run independently of K2 because the added
  frozen-base control makes them directly interpretable, but update the planning
  documents to say so.
- Keep the standout framing as mechanism/existence only.
- Treat composition cells as constructed-state comparisons rather than a
  bias-free drift field.
- Defer the optional risk-vintage mini before cutting confirmatory K2 seeds.

### Sunday analysis hierarchy

1. confounder gate table per cell;
2. primary condition contrasts at the rollout-seed level;
3. actual candidate kept-minus-pool gaps as the judge mediator;
4. generated and forced-choice behavior as distinct format channels;
5. invariant weight geometry;
6. generic advice taste and broad off-target batteries as exploratory;
7. drift-field and fixed-point language only where the design identifies it.

## 7. Bottom line

The unified plan is the correct organizing document. Its matrix structure and
control logic should be retained. The sprint becomes substantially stronger if
it trades breadth for power:

- K1 establishes the repaired Qwen contrast;
- K2 becomes a properly gated, six-seed OLMo causal inversion;
- K3 tests whether judge effects transmit on the EM/self-report axis;
- K4 is deferred rather than asking three seeds to identify an entire dynamical
  system.

The decisive conceptual shift is to measure the judge where it acts. Fixed
generic advice taste is useful evidence of format dissociation, but the causal
mediator is the judge's ranking of the actual candidate pool that becomes
training data.

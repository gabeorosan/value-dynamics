# Local final-analysis audit — 2026-07-13

Scope: current `PLAN.md`/`STATE.md`, completed K1-K3 and release artifacts,
the cross-family oracle and mixed-generator outputs that landed this morning,
the transmission-with-support output, all local analysis/scoring scripts, all
Python sources, all JSON artifacts, and every generated figure pipeline that
can run without a GPU. No remote jobs were launched or queried.

The matched self-only Qwen twin that began in Colab during this audit is an
optional extra. It was not inspected, is not included below, and does not gate
any conclusion or the writeup.

## Bottom line

The program has two results that survive the local audit:

1. **The kept-minus-pool gap predicts the next pool shift.** On the original
   K1/K2/K3 grids, the condition-intercept-plus-gap model beats its matched
   no-gap comparator in 12/13 leave-one-seed-out folds. The pre-frozen K2 model
   also beats the separately fitted no-gap comparator on later release data:
   17.3% lower RMSE on blind kernel B, 31.1% lower on Modal branch A, and 42.0%
   lower on press-depth. This is a predictive result, not a universal dynamical
   law: it loses on the `fan_press/evolving_self` phase (0.0611 versus 0.0404
   RMSE), and the mixed-pool target is not the same distribution it was fit on.
2. **Selection can move an organism only while the generated pool contains
   rankable material on the measured axis.** The score-based oracle reverses
   the material-rich OLMo rail from 0.917 to 0.094, while the 1.000 rail has
   exactly zero measured spread and does not move. Supplying base-model
   candidates restores spread and moves that 1.000 rail to 0.484. This is a
   strong existence result for material-limited selection, not evidence for a
   physical attractor or an absorbing state.

Most of the more detailed dynamical story did **not** survive preregistered
tests. The release grid passes 6/13 criteria. Press-depth passes 2/5: the depth-3
pair splits and the frozen predictor wins, but the proposed spread mediator,
depth-1 recovery, and no-floor predictions fail. The transmission-with-support
result is positive beyond its noisy baseline in 1/2 seeds and remains
response-type/content confounded.

The final Qwen mixed-supply result independently reproduces the narrower
cross-family existence claim. Starting from a stalled self-only endpoint at
`sr_freegen = 0.627`, adding frozen base-model candidates restores scored
spread and reaches `0.000` after one round in both saved seeds (921 and 922).
This is not yet a matched estimate of the injection effect.

## Reproduced local results

### K1-K3 transition model

Rebuilt `experiments/rollout_manifest.json` and reran
`scripts/analysis_transition_model.py`:

| grid | transitions | LOSO M2 RMSE | matched no-gap RMSE | fold wins |
|---|---:|---:|---:|---:|
| K1 | 48 | 0.0947 | 0.1260 | 4/4 |
| K2 | 51 | 0.0736 | 0.0906 | 5/6 |
| K3 | 36 | 0.0505 | 0.0642 | 3/3 |

This supports a cross-grid predictive association between the realized
selection gap and next-round pool motion. It does not identify a constant gain,
an attractor, or a causal mediator by itself.

A post-audit kept-score comparator addresses whether the selected answers'
absolute score is sufficient. With matched condition intercepts, gap beats
kept-only LOSO RMSE by 26% on K1, 23% on K2, and 17% on K3 (12/13 seed folds).
When both are fit only on K2 and evaluated on later release data, gap is 28%,
24%, and 34% better on kernel B, Modal branch A, and press-depth respectively.
This is recorded in `experiments/kept_vs_gap_release_analysis.json`. Because
`gap = kept - pool`, the result supports relative displacement over absolute
kept risk alone; it does not show that gap is uniquely necessary if both kept
risk and current-pool risk are supplied.

### Instrument validity

The deduplicated instrument census reproduces the current report:

- K1 generated order-gap flags: 48/85; forced flags: 79/85.
- K2 generated order-gap flags: 36/85; forced flags: 46/85.
- K1's self-judge fan is wider than random selection in both presentation
  orders, so that descriptive result survives. The forced channel does not.
- K2's arm ordering survives in both orders, but conditioning on the
  order-valid subset removes the two base-judge rails; the subset cannot be
  used as an unbiased endpoint estimate.

### Release and press-depth

The executable prereg scorer reproduces 6/13 release criteria passing. The
failures include both random-release predictions, both `press_hold` predictions,
both fan-width predictions, and the expected middle-band endpoint pattern for
`press_to_base`.

The press-depth scorer reproduces:

- spread-mediator criterion: fail;
- both depth-1 endpoints above 0.40: fail (0.000 and 1.000);
- no depth-1/2 floor hits: fail;
- depth-3 boundary split: pass (0.229 versus 0.823);
- frozen M2 versus refit no-gap: pass, 0.0641 versus 0.1106 RMSE (-42.0%).

Therefore press depth is a paired high/low outcome at each of three depths,
not evidence of bimodality or a mapped boundary law.

### Cross-family oracle and mixed supply

The saved scorer reproduces the branch-e split:

- material-rich rail: 0.917 -> 0.094, spread positive in all four rounds;
- saturated rail: 1.000 -> 1.000, spread exactly zero in all four rounds.

Mixed base supply restores spread in both saturated initializations and both
oracle-mix cells reverse by more than 0.30. The conservative prompted judge
does not use the lower-risk supplied material: its kept gaps are positive and
its kept-supplier share approaches zero. The invasion cells show very fast
movement toward the high-risk supplier.

The first branch-m writeup was too causal in two places; both are corrected in
the current report:

- Mixed and self-only runs use different random streams, and the conservative
  cells have no same-seed no-injection twin. These are existence results, not
  estimates of an injection treatment effect.
- “Contamination is one-round and total 4/4” is slightly overstated. Three
  cells read 1.000 after round 1; `invade_self` seed 37 reads 0.917 after round
  1 and reaches 1.000 after round 2. The defensible claim is near-total
  one-round movement in 4/4, with exact saturation by round 2.

The frozen K2 predictor should not receive a preregistered “pass” on mixed
pools: its fitted target was a self-generated next-pool mean, whereas the mixed
pool includes a changing external-source distribution. Its approximate errors
are useful descriptive transport evidence only.

The saved Qwen mixed-reopen scorer reproduces both registered checks: both
seeds move by more than 0.30 and both move below 0.33 after one round. The
actual seeds are 921/922 rather than the preregistered 909/910 because the
launcher avoided a collision; the result file also lacks a top-level frozen
configuration/hash record. Those are provenance limitations, not numerical
failures.

### Final-order and first-step sensitivity

`scripts/analysis_final_order_sensitivity.py` recomputes final forced-choice
scores separately in A and B order for the release, press-depth, and mixed
branch-e/m artifacts and records the result with source hashes in
`experiments/final_order_sensitivity.json`.

- The mixed branch-e directions survive both orders: seed 21 moves down in A
  and B; seed 22 stays flat in both.
- Branch-m invasion moves up and oracle-mix moves down in both orders. Seed 32
  retains a large final order gap, so its direction is robust but its endpoint
  magnitude is instrument-sensitive.
- The press-depth paired high/low endpoint split survives both orders at every
  tested depth. However, depth-3 seed 1 has opposite start-to-end signs in A
  (-0.244) and B (+0.079), so its individual direction should not be used.
- Release directions are qualitatively stable for `press_release`,
  `fan_press`, and `base_hold`; `press_random` remains mixed. The
  `press_to_base` final range is 0.792 in A and 0.708 in B.

A separate post-hoc diagnostic, `scripts/analysis_mixed_first_step.py`, finds
that first-round kept-minus-pool gap direction matches first-step movement in
8/10 mixed cells (pooled Pearson r = 0.859). Both exceptions are conservative-
judge mixed cells. This supports the material-plus-selector account while also
showing that supplied material alone is insufficient. Because it pools
heterogeneous axes and was not preregistered, it is descriptive only.

### Transmission with support

The saved result supports the narrow claim in its report: 4/5 supported rounds
have negative selection gaps, but only seed 812 moves beyond the reported
0.197 replicate-noise scale (-0.473); seed 811 moves -0.133. Both exhaust
measured spread. Because the screening preference is response-type/content
confounded, this is not clean transmission of security taste.

## Errors and stale surfaces

### P0 found and corrected: public result hierarchy

`README.md` called the legacy four-seed trajectory result the
highest-confidence dynamics result, presents the criterion-lead observation as
a live lead, and describes a mixed-stability saddle from the retired basin
analysis. The current evidence rejects that hierarchy. The README now leads
with the two surviving pillars above, the failed prereg criteria, and the
instrument/provenance limitations; it also includes the Qwen mixed-reopen
result with its matched-twin limitation.

### P0 found and corrected: authoritative dashboard

`PLAN.md` and the Jobs table at the top of `STATE.md` labeled completed work as
running. They now record all required artifacts as landed and the matched
self-only twin as optional rather than a writeup gate.

### P0 found and corrected: press-depth statistic and claim scope

The promoted press-depth report/figure mixed two different spread statistics:
the preregistered mean within-item candidate SD and an SD across item-level
means. The main table, source generators, generated SVGs, and caption now use
the preregistered statistic (0.278-0.423). “Bimodal” and “absorbing floor” were
also narrowed to paired high/low streams at n=2 and selection-inert on the
measured axis.

### P1 found and corrected: future-run seed stability

`colab_selfaware_loop_grid.py` used Python's process-randomized `hash(dose)`
inside a seed calculation. It now derives the dose offset from SHA256. This
changes only future launches; it does not alter any completed result or the
already-started optional twin, which uses its pinned launcher revision.

### P1: the “canonical” manifest no longer covers the whole completed program

`scripts/build_rollout_manifest.py` covers K1-K3, the two Kaggle release
kernels, Modal branch A, and press-depth. It does not include branch e, branch
m, transmission-with-support, oracle-opposition, or other post-release cells.
Analyses that claim to be program-wide cannot use this manifest alone. Either
extend it with explicit grid families or rename it to the K1-K3/release-core
manifest.

### P1: local checkpoint provenance is incomplete

Eight `adapter_model.safetensors` files under experiment outputs are zero bytes,
including K2 release, K3, K2 controls, and several legacy organism directories.
Their JSON results remain analyzable, but these directories are not usable local
checkpoints and must not be described as recoverable vintages without an
external content-hash-backed source.

### P1 found and corrected: K3 crossed selected and off-axis channels

`report_k3_mean_variance_decomposition.md` correctly said the reported
self-report fan is nearly uncorrelated with the candor pool being selected
(r=0.01), then later summarized K3 as moving “its selected candor axis (as
variance).” The variance table is for off-axis self-report, not the selected
candor coordinate. The report now keeps those channels separate.

### P1: code and figure regeneration errors found and fixed

Two local generators were broken:

- `docs/figures/src/make_methods_figures.py` had an invalid f-string;
- `docs/figures/auto/k1-anchor-trajectory-fan/k1-anchor-trajectory-fan.py`
  passed an undeclared `start_label` argument.

Both are fixed. After the fixes, all Python sources compile with bytecode
redirected to a writable cache; the risk-harness self-test passes; all JSON
files parse; the main, plan, methods, thread, and all auto-figure generators
complete locally. `git diff --check` also passes.

The final verification also reparsed every experiment JSON, rebuilt the
rollout manifest, reran the risk-harness self-test, regenerated every auto
figure, and reran the release, press-depth, transition, mixed, and order-
sensitivity analyses without errors.

### Closing uncertainty and failure-domain diagnostics

`scripts/analysis_closing_diagnostics.py` adds the remaining useful local
stress tests. It resamples held-out residuals by whole seed/rollout clusters;
models are not refit within each bootstrap, and there are only 3-6 clusters,
so the ranges are sensitivity analyses rather than full model-selection
uncertainty.

- Gap-versus-no-gap RMSE differences remain below zero across all three
  original grids and all three later release datasets. The weakest later case
  is blind kernel B: paired range -0.0194 to -0.0010.
- Gap-versus-kept-only also remains below zero on all later datasets. On the
  original grids, K3 is the exception: its range is -0.0177 to +0.0022, so the
  smaller kept-only advantage is not cluster-robust there.
- Residuals do not reveal a clean spread threshold or boundary failure mode.
  K1/K2 contain no <=0.05-spread transitions in the fitted core; K3's six
  low-spread transitions are easier to predict. Largest condition errors are
  random selection in K1/K2 and the frozen round-0 copy in K3.
- The ten-cell mixed first-step pattern is numerically stable to leaving out
  any one cell (r = 0.834-0.914), and OLMo-only r = 0.810. But the 8/10 sign
  result has exact one-sided p = 0.055; after collapsing to five condition
  families, mean correlation is 0.875 with exact permutation p = 0.092.
  Therefore it remains a descriptive mechanism illustration, not a new
  inferential headline.

Saved output: `experiments/closing_analysis_diagnostics.json`.

## Result hierarchy for the writeup

1. Lead with kept-gap prediction, including the matched no-gap comparator,
   fold counts, and the `fan_press/evolving_self` failure.
2. Present material-limited reversal as an intervention-window existence
   result: reversal while rankable variation exists, stalls when it does not,
   and external supply restores the window.
3. Present mixed-pool invasion as a safety-relevant demonstration, but use
   “near-total after one round” and keep causal treatment language out until
   same-seed no-injection twins exist.
4. Report release and press-depth primarily as prereg failures with two useful
   survivors: base-judge escape heterogeneity and frozen-predictor transport.
5. Put K1/K2/K3 endpoint fans, transmission-with-support, basin drift,
   weight-space geometry, and off-target probes in descriptive/exploratory
   sections with their channel and provenance limitations.

No additional broad experiment family is justified before the writeup. All
required local inputs are present and no required analysis blocker remains.
The running matched self-only Qwen twin is a useful optional follow-up, but it
should be incorporated only after it finishes and passes the same provenance
and order-sensitivity checks; the current writeup should proceed without it.

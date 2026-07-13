# Local final-analysis audit — 2026-07-13

Scope: current `PLAN.md`/`STATE.md`, completed K1-K3 and release artifacts,
the cross-family oracle and mixed-generator outputs that landed this morning,
the transmission-with-support output, all local analysis/scoring scripts, all
Python sources, all JSON artifacts, and every generated figure pipeline that
can run without a GPU. No remote jobs were launched or queried.

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

The current branch-m writeup is too causal in two places:

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

### Transmission with support

The saved result supports the narrow claim in its report: 4/5 supported rounds
have negative selection gaps, but only seed 812 moves beyond the reported
0.197 replicate-noise scale (-0.473); seed 811 moves -0.133. Both exhaust
measured spread. Because the screening preference is response-type/content
confounded, this is not clean transmission of security taste.

## Errors and stale surfaces

### P0: the public README is scientifically stale

`README.md` still calls the legacy four-seed trajectory result the
highest-confidence dynamics result, presents the criterion-lead observation as
a live lead, and describes a mixed-stability saddle from the retired basin
analysis. The current evidence rejects that hierarchy. The README should be
replaced by the two surviving pillars above, the failed prereg criteria, and the
instrument/provenance limitations before it is used publicly.

### P0: the authoritative dashboard is behind completed outputs

`PLAN.md` and the Jobs table at the top of `STATE.md` still label branch e,
branch m, and transmission-with-support as running. All three artifacts and
reports are local and complete. The Qwen mixed-reopen job is the only queued/run
item mentioned there without a local terminal artifact at audit time.

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

### P1: K3 wording crosses selected and off-axis channels

`report_k3_mean_variance_decomposition.md` correctly says the reported
self-report fan is nearly uncorrelated with the candor pool being selected
(r=0.01), then later summarizes K3 as moving “its selected candor axis (as
variance).” The variance table is for off-axis self-report, not the selected
candor coordinate. The final synthesis should keep those channels separate.

### P1: code and figure regeneration errors found and fixed

Two local generators were broken:

- `docs/figures/src/make_methods_figures.py` had an invalid f-string;
- `docs/figures/auto/k1-anchor-trajectory-fan/k1-anchor-trajectory-fan.py`
  passed an undeclared `start_label` argument.

Both are fixed. After the fixes, all Python sources compile with bytecode
redirected to a writable cache; the risk-harness self-test passes; all JSON
files parse; the main, plan, methods, thread, and all 26 auto-figure generators
complete locally. `git diff --check` also passes.

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

No additional broad experiment family is justified before the writeup. The
only scientifically clean optional follow-up is the already-specified matched
same-seed no-injection twin for the largest mixed-supply effects; everything
else should wait until the current claims and provenance are cleaned up.

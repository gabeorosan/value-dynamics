# Recent-results audit of the current writeup

*2026-07-20. Scope: `docs/writeup_value_dynamics_sprint.md` as currently
deployed, checked against the current claim ledger, the post-07-16 factorial,
held-out unit-law analysis, cross-channel code test, Qwen3.5 ladders, blind
adjudications, and their committed JSON artifacts. This is the only repository
file created by this audit; no writeup, analysis, ledger, plan, state, figure,
script, or result file was changed.*

## Bottom line

Keep the writeup's narrative: **available variation (spread) and selector/value
agreement explain the selection step, and selected material moves the next
generator state**. The recent results strengthen that internal selection
accounting. They do not support the current broader wording that the model
predicts *each run's behavioral endpoint* or that the kept candidate mean
continues to predict the behavioral probe after the selected coordinate has
lost support.

The minimal effective revision is therefore not a new results section. It is:

1. scope the endpoint headline to the 36 selection-driven runs on which the
   quoted 0.118/0.431 comparison was scored;
2. add one compact boundary-condition sentence from the later 24-run
   factorial;
3. replace the now-completed cross-channel item in Next directions with its
   result and a narrower replication target;
4. correct the endpoint evaluation-set conflation and the quantitative-
   genetics explanation of the missing coefficient; and
5. add the two new reports to Records.

The Qwen3.5-9B ladder and the detailed judge prompt × judge model factorial can
remain outside the writeup. They are useful development/mechanism results, but
including their full arcs would change the narrative without improving the
central claim. The later factorial should enter only as a held-out validation
and boundary condition; the 9B ladder should wait for the queued 9B loop
contrast.

## Additional analysis done for this audit

### 1. The later 24-run factorial validates the internal pool law, but not the unrestricted behavioral one-round law

The committed held-out report correctly finds, on 24 runs that postdate the
original model fit:

- candidate-pool movement: frozen `K = 0.833` MAE **0.023** versus **0.072**
  for no pool movement over 72 transitions;
- selector factorization: the frozen `0.96 rho sigma` rule has MAE **0.034**
  over 77 scoreable rounds; the pooled refit slope is **1.005**; and
- this internal movement result holds in all four judge prompt × judge model
  cells (per-cell correlation at least 0.92).

That analysis predicts the *next candidate-pool mean* from the selected-pool
gap. It does not test the writeup's displayed rule, `next behavioral value =
kept candidate value mean`. I ran that missing test against the writeup's
primary generated self-description readout (`sr_freegen`) on all 24 later runs:

| evaluation | kept-mean MAE | persistence MAE | reading |
|---|---:|---:|---|
| all 96 rounds | **0.156** | **0.085** | kept mean is worse |
| round 1 only (24) | 0.159 | 0.170 | small early advantage |
| rounds 1–2 (48) | 0.151 | 0.152 | essentially tied |
| rounds with at least 3/6 supported items (39) | 0.153 | 0.167 | small active-support advantage |
| rounds with at least 1 supported item (65) | 0.146 | 0.120 | already worse overall |

A run-cluster bootstrap puts the all-round excess error of kept mean over
persistence at **+0.071, 95% interval [+0.035, +0.109]**. Kept mean beats
persistence on only 8/24 runs when errors are averaged within run.

This is not a contradiction of the internal law. It is the channel boundary
already visible in the raw artifacts: the candidate-pool mean follows the
selected gap while the generated battery can decouple, especially after the
pool self-consumes and `sr_support_items` approaches zero. The new result says
that the public equation must be scoped to the original analyzed corpus or to
rounds where the candidate coordinate remains supported; it cannot be presented
as an unrestricted identity between a training-pool score and a separate
behavioral probe.

I also applied the writeup's frozen round-1 unit recurrence to these 24 later
runs. Endpoint MAE is **0.208** versus **0.234** for persistence, but the paired
run-bootstrap interval for the improvement crosses zero (**difference -0.026,
95% interval [-0.104, +0.056]**), and it calls 12/18 large movements in the
right direction. This is suggestive, not a third prospective validation.

### 2. The cross-channel test was missing the writeup's primary coordinate

The recent cross-channel report correlates written-code insecurity with the
secondary forced-choice `p_insecure` endpoint. I joined the same ten endpoint
states to the writeup's primary generated self-description endpoint
(`sr_freegen`) and recomputed both associations:

| endpoint coordinate | Pearson r with blind insecure-code rate | 95% Fisher interval | permutation p |
|---|---:|---:|---:|
| generated self-description `sr_freegen` | **+0.066** | [-0.588, +0.668] | 0.85 |
| forced-choice `p_insecure` | **-0.391** | [-0.819, +0.317] | 0.27 |

The primary-coordinate endpoint range is 0.240–0.997 and the written-code rate
range is 0.333–0.889. Seven of ten endpoint states have zero supported
self-description items by the final round, so the near-zero correlation is
also a warning that the endpoint probe has become degenerate, not a precise
estimate of a population relationship.

The most robust cross-channel result is narrower and stronger than a
correlation claim: all six endpoints with forced-choice `p_insecure < 0.10`
still write insecure code at rates **0.694–0.889** (mean 0.810). A very low
self-report therefore did not provide an all-clear on this test. The two large
code movers went toward greater security, but n=2 is too small to claim an
opposed causal channel.

### 3. The public endpoint numbers currently combine different evaluation sets

The writeup puts `0.118 versus 0.431` and `37 of 38` in one sentence. They are
both real, but they are not scored on the same set:

- **0.118 versus 0.431:** 36 matched selection-driven runs;
- **37/38 large directions:** those 36 runs plus 9 boundary-refreshed judge-swap
  runs (45 total); the unit model's MAE on that combined set is **0.1365**;
- all 61 non-swap scoreable runs: MAE **0.147** versus **0.332** persistence;
- the 22 `self_weak` runs alone: MAE **0.211** versus **0.215** persistence,
  with only 6/12 large-direction hits.

The deterministic model is useful across the overall non-swap corpus, but its
large advantage and near-perfect direction result come from the
selection-driven evaluation. “Predicts where each run ends” is therefore too
broad.

The dial-plane figure is a third, intentionally different diagnostic: its
35/41 number is the sign concordance of round-1 `rho` with movement among 56
plotted four-round runs. Its background is `4 rho sigma`, wall-capped. It omits
the outside-source pool shift and is not the scored per-run endpoint recurrence.
The current caption should call it a directional force map, not imply that it
is the same forecast underlying the 0.118 MAE.

## Required minimal writeup changes

### A. Findings item 1 (`docs/writeup_value_dynamics_sprint.md:58`)

Change “predicts where each run ends” to **“predicts where the
selection-driven runs in the analyzed corpus end.”** Keep 0.118 versus 0.431,
but name its `n = 36` scope. Do not add the whole factorial arc here.

Suggested replacement:

> **A deterministic model using first-round measurements predicts endpoints in
> the selection-driven runs.** In the original 36-run evaluation, iterating
> spread × agreement predicts the final value at MAE 0.118 on the 0-to-1 scale,
> versus 0.431 for assuming no change. A later 24-run factorial independently
> reproduced the internal selection and pool-update equations; its behavioral
> probe also exposed the boundary that the rule weakens after the selected
> coordinate loses support.

This preserves the headline while preventing the new holdout from being
silently excluded.

### B. Agreement description (`docs/writeup_value_dynamics_sprint.md:89`)

Replace “agreement changes little from round to round within a setup” with:

> Agreement is strongly structured by the experimental condition (82% of its
> variance in the original corpus is between judge × alternative-source ×
> candidate-source cells), but it can change sharply as the candidate pool
> changes.

The later factorial directly measured positive, negative, and sign-changing
agreement trajectories. The current sentence conflicts with both that result
and the later writeup statement that agreement drift is the main residual
error.

### C. One-round section (`docs/writeup_value_dynamics_sprint.md:105`)

Retain the 0.081/0.128 result, but write **“in the original 340-round corpus”**
and delete “the same in every slice” or qualify it as “across the slices in
that corpus.” Then add one sentence, preferably in Limitations rather than the
main derivation:

> In the later self-description factorial, the same law continued to predict
> the next candidate-pool mean (MAE 0.023 versus 0.072 persistence) but did not
> predict the separate generated self-description readout after the pool lost
> support; candidate-state movement and behavioral-probe movement must therefore
> be distinguished.

This is the most important substantive correction.

### D. Endpoint section and dial-plane caption (`docs/writeup_value_dynamics_sprint.md:153`)

Separate the two evaluation sets:

> On 36 selection-driven runs, endpoints land at MAE 0.118 versus 0.431 for no
> change. Adding nine judge-swap runs whose state is remeasured at the swap gives
> 37/38 correct large-movement directions and combined MAE 0.1365.

For the figure caption, replace “the model's forecast 4-round move” with
**“a four-round directional force map, `4 rho sigma`, wall-capped.”** Add that
mixed-pool supply shifts are omitted. Keep 35/41; it is correct for this sign
diagnostic, but it should not be presented as the same scored forecast as the
preceding MAE.

### E. Related frameworks (`docs/writeup_value_dynamics_sprint.md:240`)

Delete “the first factor is constant and folds into the measured rho.” Pearson
correlation is scale-invariant, so selection intensity cannot fold into `rho`.
The project's own scale audit explicitly found that the normal top-two-of-six
constant is **1.0997** on the realized six-candidate SD scale, while the
empirical fitted slope is **0.958**. Their near-one value is empirical, not
design-derived.

Suggested replacement:

> With the keep-two-of-six rule fixed, selection intensity is held roughly
> constant across conditions; `rho sigma` is the parameter-free unit proxy that
> worked best on this corpus, not a coefficient derived from the keep rule.

### F. Next directions (`docs/writeup_value_dynamics_sprint.md:277`)

The “one cheap cross-channel test” is complete and must not remain an open
direction. Replace it with one compact result plus the actual remaining test:

> A first blind cross-channel test found that low self-reported insecurity did
> not imply secure code: the six endpoints below 0.10 on the forced-choice probe
> still wrote insecure code 69–89% of the time. Across ten endpoints neither the
> generated self-description score (`r = 0.07`) nor the forced-choice score
> (`r = -0.39`) showed a reliable positive relation to code, although the sample
> is small and most final self-description pools had lost support. The next test
> is the same code battery on the saved self-judge endpoints, ideally measured
> every round rather than only at the endpoint.

This is the only recent side result that should enter the main prose, because
it directly resolves an item already promised by the writeup and sharpens the
measurement boundary.

### G. Limitations and Records (`docs/writeup_value_dynamics_sprint.md:299`)

Add the held-out factorial as a separate kind of evidence, not as a third full
endpoint validation: it validates internal selection accounting but exposes
behavioral-probe transfer failure after support collapse. Add the cross-channel
small-n and base-judge-endpoints-only caveat.

Add these records:

- `report_ablation_unit_law.md` — held-out internal factorization and pool
  movement;
- `report_code_crosschannel.md` — blind code behavior at the factorial
  endpoints.

If the new primary-coordinate calculation is cited publicly, first add it to
the committed cross-channel scorer/report rather than citing this audit's
ad-hoc join as though it were already part of that artifact.

## Corrections needed in the recent analysis layer

These should be fixed before the reports are treated as clean public records,
but none requires changing the writeup narrative.

1. **Held-out ablation metadata is stale.**
   `scripts/analysis_ablation_unit_law.py` and the generated JSON still say
   “14 runs (56 rounds),” while the artifact contains 24 rho trajectories, 72
   movement transitions, and 77 factorization rounds. The report repeats “14”
   at line 21. The report says 8 raw JSONs; the script's current file manifest
   contains **9**. The ledger headline and provenance columns also lead with
   the old 14-run/four-file version and append the current result later. Replace
   these with one current 24-run statement.

2. **The held-out report overnames what it validates.** It validates
   `gap -> next candidate-pool mean` and `rho sigma -> gap`, not the displayed
   public rule `kept candidate mean -> next behavioral probe`. Rename/reframe
   it as a held-out **internal pool-dynamics** test and add the behavioral
   result above as the transfer boundary.

3. **The cross-channel report treats non-significance as equality.** “8/10
   endpoints write at the organism's rate” should become “8/10 are not
   distinguishable from the organism at this sample size.” With 36 snippets
   per state, failure to reject is not an equivalence test. The defensible
   headline is that very low self-reports coexist with high insecure-code
   rates and that no positive cross-channel association is established.

4. **The cross-channel report omits the primary generated coordinate.** Add
   `sr_freegen` endpoint values, its `r = 0.066` association, uncertainty, and
   the zero-support caveat to the committed scorer and report.

5. **The Qwen3.5-9B ladder report has a noise contradiction.** It says the
   gate margin is 0.018 and “well above” a 0.022 noise floor. The absolute
   0.218 reading is about ten times the noise floor, but the margin above the
   0.20 threshold is **smaller** than that floor. Replace the claim with “the
   registered gate passes narrowly; blind review confirms real code leakage,
   but not a stable dose-750 misalignment peak.” Also change “Size moves EM
   installability” to “installability differed between the 4B and 9B
   checkpoints”; one checkpoint per size does not identify size causally.

6. **The dial-plane caption overidentifies a sign map as the scored endpoint
   model.** The generator's own caption notes that mixed-pool supply is omitted.
   Carry that caveat into the public caption and keep the 35/41 sign statistic
   separate from the 36-run MAE and 45-run direction statistic.

## Results that should remain out of the writeup for now

- **Qwen3.5-9B dose ladder:** real blind-confirmed insecure-code leakage into
  persona answers, but no broad persona misalignment and no completed 9B loop
  contrast. It is a build/gating result, not yet a value-dynamics result.
- **Detailed 2×2 judge prompt × judge model factorial:** use its held-out
  internal-law result and agreement-trajectory boundary, but omit the full
  24-run condition table. It would pull the writeup into a separate judge-
  prompting story.
- **The two apparently secured cross-channel endpoints:** retain as a flagged
  tail, not a headline. Two movers are enough to reject “nothing ever moves,”
  not enough to establish an opposed channel.
- **Qwen3.5-4B INVALID_BUILD ladder:** keep in the repository record only.

## What remains to analyze

No additional analysis is required before making the minimal writeup changes
above. For a clean durable record, the following should be done afterwards:

1. integrate the 24 factorial runs into a committed support-stratified
   behavioral-transfer scorer, keeping candidate-pool state and generated
   battery state separate;
2. extend the committed cross-channel scorer with the primary `sr_freegen`
   endpoint, uncertainty intervals, and explicit non-equivalence wording;
3. run the code-writing battery on the saved self-judge endpoints and, in a
   future loop, at every round; and
4. wait for the registered Qwen3.5-9B `(g2)/(g3)` contrast before deciding
   whether that model belongs in this writeup.

## Source artifacts checked

- `docs/writeup_value_dynamics_sprint.md`
- `docs/ANALYSIS_LEDGER.md`
- `docs/reports/report_ablation_unit_law.md`
- `experiments/ablation_unit_law.json`
- `scripts/analysis_ablation_unit_law.py`
- the nine `experiments/em_selfaware_loop/output/head2head_*selfonly*.json`
  inputs listed by that script
- `experiments/selection_response_predictor.json`
- `experiments/model_ladder_horizon.json`
- `docs/figures/auto/synthesis-dial-plane-horizon/` generator and caption
- `docs/reports/report_code_crosschannel.md`
- `experiments/em_code_crosschannel/output/code_crosschannel_adjudication.json`
- `experiments/qwen_judge_ablation.json`
- `docs/reports/report_qwen35_9b_ladder.md`
- `docs/reports/report_em359b_freegen_adjudication.md`
- `experiments/qwen35_em_ladders/output/em359b_dose_ladder.json`
- `experiments/qwen35_em_ladders/output/em359b_freegen_adjudication.json`


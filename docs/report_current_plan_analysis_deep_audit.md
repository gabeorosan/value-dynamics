# Deep audit of the current analysis plan

*2026-07-10. This report audits the authoritative [`PLAN.md`](PLAN.md), the
newly built K1 implementation, the OLMo conservative-install/inversion-screen
code, and the available raw basin artifacts. It supersedes the implementation
and analysis recommendations in `report_final_sprint_plan_audit.md` where this
report is more specific.*

> **Status note (2026-07-11):** this is a pre-remediation audit, not a current
> launch dashboard. Its K1/K2/K3 implementation failures were subsequently
> repaired; use [`report_current_state_audit_2026-07-11.md`](report_current_state_audit_2026-07-11.md),
> [`PLAN.md`](PLAN.md), and [`STATE.md`](STATE.md) for the current state.

## Executive verdict

The high-level reprioritization in `PLAN.md` is now mostly right: K2 is the
headline test, its confirmatory contrast has six seeds, K4 is deferred, and the
analysis begins with confounder gates and rollout-level condition contrasts.
But the analysis is not yet launch-ready.

There are three main problems.

1. **The built K1 script does not implement the instrument described in the
   plan.** It still generates every training pool with the gamble as Option B;
   its claimed order mirroring does not swap the options; its “kept order gap”
   is therefore mostly the strength of semantic risk selection, not order
   imbalance. It also uses a lax answer parser that turns truncated rationales
   into A/B choices, does not log loop-generation invalidity, does not retain
   candidate text or raw probe reads, and lacks the same-template forced-choice
   and factual-EV channels required by the plan.
2. **The planned candidate selection gap is useful, but is not an established
   mediator.** A CPU reanalysis of 49 available Qwen/OLMo legacy rollouts finds
   little evidence that kept-minus-pool semantic gap predicts the next update
   after current state is controlled. The OLMo raw correlation is largely a
   saturation/time artifact. The more direct mechanism read is the judge's
   candidate-level semantic loading on identical pools, controlling invalidity
   and length; the kept gap is a downstream manipulation check.
3. **The weight-space plan still confuses an adapter with an update.** K1's
   logged `net_displacement` is the norm of the whole current adapter, not
   `W_t-W_0`, and `cos_with_r1_update` is the cosine between whole adapters, not
   between update directions. The existing SVD “shared direction” result also
   compares only leading left singular vectors and can declare two full weight
   updates aligned even when their right singular directions are orthogonal.
   The completed alpha-scaling result is a partial negative/degeneration
   diagnostic, not an affirmative causal leg for the geometry story.

**Recommendation:** do not launch K1 or clone it into K2 until the instrument
block below is repaired and a one-seed/one-round smoke passes. After that, keep
K2 as the first confirmatory priority, K1 as the cross-family anchor, K3 as an
existence-framed secondary grid, and K4 deferred. If compute remains, replace
the four-round K4 with a one-update content impulse experiment rather than try
to estimate a fixed point.

## 1. What the preliminary analysis found

### 1.1 Data and method

I reparsed every stored candidate in:

- `experiments/kaggle/kaggle_basin_anchor/output/basin_anchor.json`;
- `experiments/kaggle/kaggle_basin_anchor_ext/output/basin_anchor_ext.json`;
- `experiments/lightning/output/basin_anchor_lightning_23_31.json`;
- `experiments/lightning/output/basin_anchor_lightning_15_23.json`;
- `experiments/lightning/output/basin_second_model.json`.

A choice counted as valid only when a standalone `A` or `B` occurred at the end
of the answer. For every rollout-round I recomputed pool risk, kept risk,
kept-minus-pool gap, invalidity, and the next change in the behavioral
coordinate. Regressions use rollout-cluster bootstraps; they are retrospective
diagnostics, not confirmatory tests.

### 1.2 Malformed candidate generation is large for Qwen

| family / judge | strict-invalid in pool | strict-invalid in kept set | invalid outputs that the current lax parser nevertheless calls A/B | mean chars, valid / invalid |
|---|---:|---:|---:|---:|
| Qwen, evolving self | 39.9% | 51.0% | 98.8% | 179 / 223 |
| Qwen, frozen base | 25.2% | 23.7% | 99.7% | 179 / 235 |
| OLMo, evolving self | 2.9% | 1.3% | 97.6% | 106 / 236 |
| OLMo, frozen base | 3.9% | 3.1% | 100% | 109 / 237 |

The invalid answers have the signature of max-token truncation: they are much
longer, commonly end mid-sentence, and almost always contain an earlier mention
of “Option A” or “Option B.” About two thirds are called B by the lax parser.
Consequently, the current parser does not merely add noise; it systematically
converts truncated reasoning into a semantic choice.

In the Qwen evolving-self rollouts, strict invalidity rises from about 29% in
round 1 to about 50% in round 5. The kept set becomes more invalid than the
pool because conservative selection rejects a malformed answer less strongly
than a valid risky answer, even though it prefers a valid safe answer to both.
Thus the loop increasingly trains on incomplete rationales as it evolves.

### 1.3 The selection gap is not yet a predictive mediator

| family / judge | rollout transitions | mean kept-minus-pool semantic gap | beta for `next change ~ gap + current state` | rollout-cluster 95% interval |
|---|---:|---:|---:|---:|
| Qwen, evolving self | 115 | -0.207 | +0.067 | [-0.130, +0.251] |
| Qwen, frozen base | 81 | -0.147 | +0.289 | [-0.156, +0.697] |
| OLMo, evolving self | 20 | +0.121 | +0.042 | [-0.814, +1.226] |
| OLMo, frozen base | 19 | +0.142 | -0.087 | [-1.057, +0.417] |

For Qwen evolving-self, the raw correlation between gap and next change is
only 0.05. OLMo's raw correlations look large (0.76 self, 0.58 frozen), but both
the gap and the behavioral update collapse toward zero as the model saturates;
controlling current state removes the relationship. OLMo's first-round gap is
actually negatively correlated with total later change in these four rollouts,
which is another saturation/headroom warning.

This does **not** make selection gap useless. It is an excellent record of what
entered training and a necessary manipulation check. But calling it “the
criterion-channel mediator” before the new randomized contrasts are observed
would overstate the evidence. Conditioning the primary treatment estimate on a
post-treatment kept gap would also introduce a mediation/selection problem.

### 1.4 Candidate-level judge loading is the stronger cheap process measure

On the same stored candidate pools, I fitted within-item regressions of judge
score on strict semantic choice, invalidity, and answer length. The semantic
coefficient is large and correctly signed:

| family / judge | score change for a valid gamble answer vs valid sure answer |
|---|---:|
| Qwen, evolving self | -0.272 |
| Qwen, frozen base | -0.208 |
| OLMo, evolving self | +0.213 |
| OLMo, frozen base | +0.188 |

This is a direct read of the force applied by the judge on the actual pool. It
also allows invalidity and length to be separated from semantic preference.
The new experiments should persist enough information to estimate this loading
for every judge, item, and round. It should be the main mechanism diagnostic;
the resulting kept gap should be secondary.

### 1.5 Format transfer is not a side issue

The repaired Phase-0 artifact already shows large forced/generated splits:

| checkpoint | order-balanced forced p(gamble) | generated gamble fraction |
|---|---:|---:|
| Qwen base | 0.628 (order gap 0.629) | 0.042 |
| Qwen risk organism | 1.000 | 0.870 |
| OLMo instruct | 0.724 | 0.667 |

The loop trains one-sentence rationales plus a terminal choice, while many old
headlines use bare next-token A/B. These are distinct channels. A claimed value
shift should state whether it appears in the same format as training, transfers
to bare choice, or both.

## 2. Launch-blocking implementation errors

### 2.1 K1 does not actually repair the training-loop order confound

In `kaggle_k1_qwen_anchor_grid/script.py`:

- `loop_prompt` always renders sure=A and gamble=B (lines 100-103), and every
  training pool calls that original prompt (lines 477-480).
- `kept_rows_mirrored` explicitly does **not** swap the options. It duplicates
  the same answer under the original prompt and a prompt saying “state your
  choice” (lines 438-456). The answer still contains the original Option A/B
  rationale and terminal letter.
- `kept_order_gap` is computed from the fraction of kept answers parsed as B
  (lines 498-500). Because gamble is always B, this is primarily semantic risk
  selection, not the balance of option order in the training set. A genuinely
  conservative judge can therefore fail the “order” gate merely for selecting
  the sure option strongly.

The SPEC's claims that training rows are mirrored and letter-balanced are
therefore false. This is a hard pre-launch blocker.

**Cheap repair:** replace the current duplicate with a true swapped example.
For every valid kept response, deterministically swap `Option A`/`Option B` in
the rationale, swap the terminal letter, and pair it with the swapped prompt.
Validate that the semantic choice is unchanged. This preserves the script's
current two-row training dose, so it costs essentially no extra training. An
equally clean alternative is to render half of loop items in each order and
keep an equal number from each order, but it needs more generation or smaller
per-order pools.

The gate should then track:

- fraction of training rows where the gamble was shown as A (exactly 0.5 under
  mirroring);
- semantic risk fraction in the kept set (an outcome, not a confounder);
- generated and forced-choice order gaps on held-out probes.

### 2.2 Malformed output is still folded into the semantic coordinate

K1's `p_risk` and `p_risk_letter` take the last standalone A/B anywhere in the
text and otherwise return safe (lines 104-107). The shared
`risk_harness._terminal_choice` makes the same “last mention” mistake despite
describing itself as a terminal parser (`risk_harness.py`, lines 129-156). The
OLMo inversion screen repeats it (`colab_olmo_inversion_screen.py`, lines
98-104).

Use an end-anchored parser, e.g. a required `Final: A` / `Final: B` field. Log
invalidity from the initial attempts, reject and replenish invalid candidates
before ranking/training, and impose a bounded retry budget. Increasing the
generation cap from 64 to roughly 96 tokens should remove much of the observed
truncation at modest cost; a bounded output schema is better still.

### 2.3 K1's “invalid rate” and factual gate are not the planned gates

The value stored as `ev_estimation.invalid_rate` is the fraction of six numeric
EV prompts that failed to parse (lines 372-408). It is not the invalid rate of
generated gamble choices. K1 also does not run the repaired, lopsided,
same-template factual-EV test from `experiments/common/risk_harness.py`.

Required fix:

- rename the existing field to `ev_number_parse_invalid_rate`;
- add strict generated-choice invalidity for the probe and candidate pools;
- add order-balanced forced p(gamble) on the same held-out items;
- add continuous probability-of-correct plus threshold accuracy on the
  lopsided factual-EV bank, interpreted differentially from round 0 rather than
  by an absolute 0.90 threshold.

### 2.4 The raw data needed for Sunday are not persisted

K1 discards candidate text and stores only lax `cand_risk`, score arrays, and
kept indices (lines 488-497). The coordinate stores only three aggregates
(lines 259-270), and most battery blocks reduce their item reads to a mean
(lines 369-408). This prevents strict reparsing, candidate-length diagnostics,
item-level reliability, measurement-error modeling, and honest drift/noise
analysis.

Persist candidate text, token count, strict terminal letter, validity, gamble
letter, prompt order, every judge score, every judge's hypothetical kept set,
and all per-item probe probabilities/generations. JSON size is negligible next
to the adapters.

### 2.5 The promised format-channel comparison is absent

K1's trajectory is sampled generated prose only. It lacks the paired
order-balanced bare/forced probability channel on the same EV-neutral items.
`altformat_risk` uses different real-world advice items, so it cannot identify
format transfer separately from content transfer.

Add both channels on identical items. For the generated channel, report risk
conditional on valid completion and invalidity separately. Do not combine them
into one scalar.

### 2.6 `distinct_n` is currently a constant

The script calls greedy decoding once per prompt and then counts the size of a
one-element set (line 401), so `n_distinct` is always 1. Remove it or sample at
least four outputs at round 0 and the final round only. The latter is cheaper
and more informative than paying for a vacuous endpoint at every round.

### 2.7 The K1 primary endpoint is not testable as written

The SPEC says the primary result is that four evolving-self seeds “fan wider”
than four frozen-base seeds. A range/variance contrast at n=4 is extremely
unstable, and the exact paired sign test cannot reach two-sided p<0.05 with four
pairs. The current summary prints the sample range, which is especially noisy.

Use a paired, baseline-adjusted final-state or trajectory-AUC contrast between
judge arms as the K1 primary descriptive effect. Report the fan/variance result
as a secondary phenomenon. K1 remains valuable as a family replication, but K2
with six paired confirmatory seeds is the first test capable of a nontrivial
exact two-sided sign result (minimum p=0.03125 if all six agree).

### 2.8 Reproducibility and provenance are incomplete

K1 seeds one RNG using Python's process-randomized `hash(cond)` (line 463), so
random selection is not reproducible across processes unless
`PYTHONHASHSEED` happens to match. Replace it with a fixed condition-to-integer
map. The script also rebuilds the mod65 organism instead of loading and hashing
the banked adapter, and it records no immutable model revision, package
versions, tokenizer/chat-template hash, or organism artifact hash.

Either load the banked organism by content hash or explicitly call K1 a new
recipe replication and verify round-0 equivalence before proceeding.

### 2.9 The OLMo gate has smaller but real correctness problems

The conservative installer currently:

- returns an integer for an in-band `organism_rung`, although adapter directories
  are named `rung_<n>`; the inversion screen will look for the wrong directory;
- reports the overshot rung's value while selecting the previous rung;
- stops on the forced risk band without enforcing the measured EV-delta,
  generated-validity, order-gap, or judge-headroom gates;
- does not pin an immutable model revision despite the plan requiring it.

The inversion screen uses one unseeded candidate pool, the lax parser, and saves
only aggregate judge gaps rather than per-candidate judge scores/kept indices.
Use at least two seeded fresh pools, require sign replication and semantic
diversity, strictly parse/replenish candidates, save the full score table, and
report paired item-level uncertainty. This is still a cheap inference-only gate.

## 3. Weight-space analysis: what to fix and what to demote

### 3.1 K1's update geometry is mislabeled

At each round K1 sets:

- `net_displacement = ||W_t||`, the norm of the entire current LoRA adapter;
- `cos_with_r1_update = cos(W_t, W_1)`, the cosine of entire adapters.

The desired quantities are instead:

- step `delta_t = W_t - W_(t-1)`;
- cumulative update `Delta_t = W_t - W_0`;
- `||Delta_t||`, `||delta_t||`, path length, and
  `cos(Delta_t, delta_1)` or `cos(delta_t, delta_(t-1))`.

The existing r-by-r trace inner product is a good primitive and is
factorization-invariant; it simply needs to be applied to **differences** of
merged products. Persist all rounds 0-4, not only 0/2/4, because the extra
storage is cheap and enables independent recomputation.

### 3.2 The existing SVD “shared direction” conclusion is not established

`colab_adapter_svd.py` compares the leading **left** singular vector of each
layer and averages its absolute cosine. A full update direction is an outer
product of left and right directions; shared left vectors do not imply aligned
weight updates. Taking the absolute value also removes sign, which is precisely
what would distinguish opposing trait directions.

Replace this with full merged Frobenius cosine between `Delta_t` matrices using
the invariant trace formula. For spectral analysis of a net loop update, take
the SVD of `W_final-W_0`, not the whole final organism adapter. If a
cross-condition direction is constructed, estimate it without the evaluated
seed and project the held-out seed onto it; otherwise behavior/geometry
correlation is circular.

### 3.3 Alpha scaling is a negative/limited diagnostic

The completed alpha grid shows:

- at alpha <= 1, committed adapters carry self-report more than the null, but
  the behavioral EM choice remains near floor for all;
- at alpha around 1.5 and above, the null also moves and corrigibility rails,
  indicating generic over-scaling degeneration.

Therefore alpha scaling should not be described in the Sunday hierarchy as
“the causal leg” for behavioral geometry. It supports only a limited causal
statement about the self-report coordinate in-distribution and provides a
useful falsification of naive high-alpha behavioral claims.

## 4. Recommended analysis specification

### Tier 0 — artifact and instrument certification

For every cell, before looking at the outcome contrast:

1. immutable model/adapter/code hashes and package versions;
2. completion-only loss verification and round-0 organism band/headroom;
3. exact training-row order balance;
4. initial-attempt and post-replenishment invalid rates;
5. generated and forced-choice order gaps, separately;
6. differential same-template factual-EV performance;
7. number of valid candidates per item and actual training-row count;
8. measure-only drift and any resume/restart discontinuity.

Predeclare which failures invalidate a channel versus an entire cell. Suggested
defaults: exact training-order balance under mirroring; held-out semantic order
gap <=0.10; and generated invalidity <=0.10 after the longer/schema-constrained
generation fix. A cell with higher generated invalidity may retain its forced
channel but cannot support a generated-behavior claim.

### Tier 1 — primary randomized condition contrasts

- Experimental unit: rollout seed, never item or round.
- Outcome: baseline-adjusted final state or prespecified trajectory AUC.
- K2: paired frozen-conservative minus frozen-base contrast over the six matched
  seeds, analyzed by exact sign-flip randomization and shown as all six paired
  trajectories. This is the headline.
- K1: paired judge contrasts over four seeds, explicitly descriptive/existence
  framed; fan/variance is secondary.
- K3: n=3 is an existence screen. Analyze `em_freegen` as binomial counts with
  intervals and keep self-report separate; do not treat five rounds as fifteen
  independent observations.

Do not put a post-treatment selection gap into the primary condition model.

### Tier 2 — mechanism and format

For each shared candidate pool, estimate within-item judge loading:

`judge_score ~ semantic_choice + invalid + token_length`

and retain the fixed-judge cross-scores. Then report:

1. judge semantic loading (the applied criterion);
2. kept-minus-pool semantic gap (what entered training);
3. invalid and length selection gaps;
4. next behavioral update, descriptively cross-lagged with 1-3.

The randomized judge contrast can support a causal statement about the total
trajectory effect. The cross-lag/mediation decomposition remains exploratory at
these sample sizes.

For risk, place generated-valid behavior and forced-choice behavior side by
side on identical items. The generated channel is closest to the training
format; the forced channel is a cleaner transfer read. A result in only one is
a format-specific effect, not a universal risk shift.

### Tier 3 — specificity rather than a battery fishing expedition

The broad riding battery should not be promoted by whichever coordinate moves
most. For each family:

- standardize each probe's change using its item-level/measure-only variation;
- compare against the random-selection arm where available;
- report a target-specificity ratio: absolute standardized target change
  divided by RMS standardized off-target change;
- apply BH/FDR or hierarchical shrinkage within a clearly labeled exploratory
  family;
- report item-level reliability and decline to interpret probes with too few
  items or rail saturation.

This is more informative than a large set of uncorrected small multiples and is
CPU-only once raw reads are saved.

### Tier 4 — local drift, not fixed-point discovery

With four rounds and small n, fit a condition-specific local update model with
rollout clustering or a simple state-space/binomial observation layer using raw
item probabilities. Use the measure-only trajectory to estimate measurement
noise. Do not fit cubic basins or report stable fixed points unless multiple
starting states under the same judge actually bracket a zero crossing.

The two composition checkpoints are constructed-state comparisons, not samples
of a one-dimensional field. Different adapters with the same scalar x can have
different hidden state.

### Tier 5 — corrected weight geometry

Only after the behavioral result is certified:

- recompute `delta_t` and `Delta_t` from merged products;
- report full-update Frobenius cosines, not leading-left-vector cosine;
- use leave-one-seed-out condition directions for projections;
- keep all behavior/geometry correlations secondary with permutation or
  rollout bootstrap uncertainty and multiple-comparison control;
- present alpha scaling as a limited self-report result plus degeneration
  control, not generic causal validation.

## 5. Reprioritized, compute-aware execution plan

| priority | action | compute cost | reason |
|---:|---|---:|---|
| 0 | Patch the shared risk instrument and K1: true swapped training rows, strict parser/replenishment, raw logging, paired forced/generated reads, factual-EV delta, corrected geometry, stable RNG/provenance | no GPU | Current K1 would repeat the central order/format confounds while claiming they were repaired |
| 1 | Run one K1 seed x one round x two arms smoke; inspect raw JSON, strict invalidity, exact row balance, runtime, adapter deltas | roughly 20-40 min | Validates science and recomputes the real budget before the 45-hour spend |
| 2 | Finish OLMo ladder fixes and run the inversion screen on at least two seeded, valid fresh pools with candidate-level loadings | roughly 1-2 h inference | K2 must demonstrate an actual semantic judge intervention before training |
| 3 | Run K2's six-seed frozen-conservative vs frozen-base contrast | roughly 14 h under old timing, remeasure | Highest-value causal result and the only planned risk contrast with minimally useful exact-test resolution |
| 4 | Run K1's four-arm/four-seed anchor, with the primary changed from range/fan to paired baseline-adjusted effects | roughly 9 h old estimate, remeasure | Cross-family replication and control grid |
| 5 | Run K2 evolving/random controls, then K3 if budget remains | roughly 6-7 h each | Mechanistic context and EM generality; both are secondary to the confirmatory contrast |
| 6 | CPU analyses: gate table, exact seed-level contrasts, judge loadings, format matrix, specificity, corrected geometry | no GPU | Highest information per compute after artifacts land |
| 7 | Optional content impulse test instead of four-round K4 | roughly 1-2 h | Tests immediate content direction without pretending to estimate a fixed point |

### Cheap replacement for K4

If there is spare compute, take one fixed mod65 checkpoint and apply one matched
small update from aligned, opposing, or format-matched-neutral external rows.
Use 6-8 resampled data seeds, match examples/tokens/optimizer steps exactly, and
measure the immediate target and off-target deltas. This identifies whether
external content exerts a directional impulse. It does **not** estimate a fixed
point or stiffness, but it is more powered and much cheaper than 3 seeds x 4
rounds.

## 6. What should be incorporated into the current plan now

1. Add a hard pre-launch instrument gate for strict parsing, true loop-order
   balance, raw persistence, same-item format channels, and corrected update
   geometry.
2. Replace “selection gap is the mediator” with “candidate-level judge loading
   is the mechanism manipulation; kept gap is the realized training-data shift;
   mediation is exploratory.”
3. Change K1's primary endpoint away from four-seed range/variance.
4. State exact seed-level randomization analyses for K1/K2/K3 and prohibit
   round/item pseudoreplication.
5. Add an explicit multiple-comparison/reliability plan for the riding battery.
6. Demote alpha scaling and current SVD conclusions; recompute geometry on
   `W_t-W_0` with full merged-update inner products.
7. Persist every round 0-4 and every raw per-item/candidate read.
8. Keep K4 deferred; prefer the one-update content impulse if hours remain.

The core scientific opportunity remains good: K2 directly intervenes on judge
preference in a model family whose native risk axis saturates easily, while K1
provides the Qwen anchor. The main risk is now not the choice of experiment; it
is silently carrying the old parsing, order, format, and weight-delta errors
into a much larger run.

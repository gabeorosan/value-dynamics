# Analysis — Re-examining "criterion leads behavior" and the trait saddle under the two-force lens

*Self-contained; analysis-only (no new training). Data: the completed runs
[`kaggle_selfmod_attribution`](../experiments/kaggle/kaggle_selfmod_attribution/output/selfmod_attribution.json)
(4 selection arms × 2 organisms × 5 rounds) and
[`kaggle_sft_drift_anatomy`](../experiments/kaggle/kaggle_sft_drift_anatomy/output/sft_drift_anatomy.json)
(6 content arms × 2 organisms × 5 rounds), plus a ~$0.30 Modal judge pass
([`experiments/modal/modal_gen_judge/`](../experiments/modal/modal_gen_judge/))
scoring the 320 logged self-generated training texts for trait content. Written 2026-07-05.*

## Background in two sentences

The anatomy run decomposed drift in our self-training loops into two forces:
**content-carried preference flattening** (training on balanced tradeoff prose pushes
graded tradeoff preferences toward indifference; generic QA text barely does) and
**self-data entropy collapse** (training on the model's own generations collapses
output diversity; external text raises it). Two earlier headline results predate this
decomposition and needed re-examination under it: (1) "the self-steering *criterion*
moves before *behavior*" and (2) the drift-field "saddle" (risk/optimism self-amplify,
sycophancy/verbosity/caution self-correct).

## Analysis 1 — Criterion-lead is largely the content force hitting the criterion instrument (deflationary reading supported)

Method: for every rollout, per round, compute normalized displacement from round 0 of
(a) the **criterion channel** = mean |Δ rating_diff| over the 8 packet tradeoffs
(scaled by the 6-point range) and (b) the **behavior channel** = mean |Δ| over the
four bounded behavior probes (risk, sycophancy, corrigibility, optimism).

Findings (means over rollouts):

- **Under packet-content training** (all four attribution arms; anatomy packet arms),
  the criterion channel drifts monotonically and keeps growing (final displacement
  0.15–0.18), while the behavior channel **jolts at round 1 and then reverts**
  (round-1 displacement exceeds final displacement; e.g. attribution self_sample:
  behavior 0.114 at r1 → 0.041 at r5).
- **Under neutral-QA training**, the criterion channel moves far less (final 0.09)
  while behavior displacement is comparable to the packet arms (0.11) — i.e.
  sustained criterion drift is **specific to tradeoff-content training**.
- **Under self-generation training**, *both* channels barely move (criterion 0.06,
  behavior 0.04) — self-data collapses entropy, not the criterion.

Interpretation: in packet-based loops, "the criterion moves while behavior doesn't"
is mostly the **content-carried flattening force acting on the criterion instrument**
— the criterion probes are themselves ratings *of tradeoff text*, the same genre as
the training data — rather than an internal evaluative shift that precedes behavior.
Caveat: the original criterion-leads observation (risk organism, criterion for
training on sycophantic responses 0.00→0.42) came from a *self-generation* loop with
a different criterion instrument, so this analysis retires the packet-loop version of
the claim and demands (not refutes) a content-controlled re-test of the original.

## Analysis 2 — The naive "data pulls state toward data" saddle mechanism is NOT supported at this dose

Hypothesis tested: each trait drifts toward the trait content of the data trained on;
the saddle's diagonal signs would then follow from whether the model's own
generations sit above or below its current trait coordinate.

Method: the anatomy `self_gen` arm logged all 320 training generations. Verbosity of
each generation is directly computable (token length, same 110-token cap as the
battery's open-prompt coordinate); sycophancy/optimism/risk content was scored by the
base model as judge (p_yes on three fixed questions, Modal, fp16). For each of the 20
(rollout × round) transitions: does sign(data trait content − current coordinate)
predict the sign of the next round's drift?

Findings:

- **Verbosity** (cleanest scale match): corr(data−state gap, next drift) = **+0.46**,
  sign-agreement 12/20 — weakly supportive, but base's generations sit almost exactly
  at its coordinate (gap ≈ 0), so most of the signal is from the sycophancy organism.
- **Judged traits: no support.** Sign-agreement at or below chance (sycophancy 10/20,
  optimism 8/20, risk 6/20); correlations mixed in sign across organisms (base all
  negative, sycophancy organism positive for risk/sycophancy). Most tellingly, the
  generations are judged **substantially more sycophantic (+0.33) and optimistic
  (+0.24) than the model's current coordinates, yet the coordinates do not move up**
  — mean per-round drifts are ≤0.01 in magnitude, i.e. within noise.

Interpretation: at this update strength (10 steps on 16 pairs/round), self-generation
training **does not detectably drag trait coordinates toward the trait content of the
data** — it collapses entropy while leaving behavior probes nearly fixed. So the
saddle (from the earlier one-step activation-steering proxy) is *not* explained by a
simple data-content pull at small SFT doses; its mechanism remains open. Caveats:
n=20 transitions per trait; judge scale ≠ battery scale (gap signs unreliable near
saturation); dose may simply be below the threshold where the pull bites — the
anatomy dose-response arm showed contraction forces scale steeply with steps.

## What this changes

1. **Retire the packet-loop criterion-leads-behavior claim**; keep the original
   self-loop observation as an open single-seed lead that now requires a
   matched-content control to survive.
2. **The basin-prediction ensemble should include update-dose as a factor** and
   measure both forces per rollout (entropy trajectory + selected-data trait content
   vs state), since the data-content pull is invisible at the current dose while
   contraction and collapse are not.
3. Behavior probes' round-1 jolt-and-revert pattern under any packet training is a
   measurement-relevant transient — trajectory claims should not lean on round-1
   deltas.

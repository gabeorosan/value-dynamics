# Report — Stance dissociation: what does a model learn from stance-bearing text?

*Self-contained. Spec:
[`specs/spec_kaggle_stance_dissociation.md`](../specs/spec_kaggle_stance_dissociation.md)
(+ v2 dual-format readout). Run on Colab (T4), 16 rollouts: 5 rhetoric arms ×
2–3 seeds × 3 rounds + 2 high-dose arms × 1 seed. Artifacts on Drive:
`value_dynamics/stance_dissociation/stance_dissociation.json` and
`..._primary_seed303.json`. 2026-07-07.*

## 1. Question and design

When a model is fine-tuned on text that *argues a position*, what does it learn —
the **stance**, the **rhetorical structure**, or mere **topical exposure**? All arms
train a base Qwen3-4B LoRA on 16 texts/round about the same topic (assistant
personalization vs general reliability), matched in length and vocabulary, differing
only in rhetoric:

| arm | stance on personalization (X) | structure |
|---|---|---|
| pure_advocacy | pro-X | one-sided |
| hedged_advocacy | pro-X (concedes the other side first) | concede-then-conclude |
| concessive_refutation | anti-X (rehearses X's virtues first) | concede-then-conclude |
| pure_refutation | anti-X | one-sided |
| stance_free | none | descriptive |

Two pre-registered readout formats: **pref_X** = graded 1–7 packet-rating preference
for personalization (prose-format; round-0 = +1.454) and **choice_pref_X** =
order-averaged probability of choosing the personalized option in 6 concrete
behavioral scenarios (choice-format; round-0 = 0.727). Pre-registered contrasts:
(a) hedged_advocacy vs stance_free; (b) concessive_refutation vs pure_refutation.

## 2. Results (final round; per-seed values, then mean)

**Prose-format (pref_X, start +1.454):**

| arm | seeds | mean |
|---|---|---|
| pure_advocacy | 1.15, 1.10 | **+1.12** |
| hedged_advocacy | 0.93, 0.24, 0.95 | +0.71 |
| pure_refutation | 0.86, 0.27, 0.64 | +0.59 |
| stance_free | 0.24, 0.65, 0.72 | +0.54 |
| concessive_refutation | −0.68, −0.06, −0.21 | **−0.31** (sign reversal, 3/3 seeds ≤ −0.06) |

**Choice-format (choice_pref_X, start 0.727):**

| arm | seeds | mean |
|---|---|---|
| hedged_advocacy | 0.84, 0.79, 0.835 (+highdose 0.833) | **0.82** (4/4 runs up) |
| pure_advocacy | 0.744, 0.759 | 0.75 |
| concessive_refutation | 0.749, 0.732, 0.752 | 0.74 |
| pure_refutation | 0.670, 0.711, 0.671 | 0.68 |
| stance_free | 0.684, 0.660, 0.617 | 0.65 |

## 3. The three findings

**1. Concede-then-conclude beats one-sided assertion — in both directions.** The two
concessive structures produce the largest movement toward their *concluded* stance:
concessive refutation is the only arm that actually **reverses** the prose
preference (crossing zero from +1.45, all three seeds), far exceeding blunt
refutation (−0.31 vs +0.59 — the *opposite* of an ironic-rebound prediction); and
hedged advocacy is the only arm that consistently raises actual **choice behavior**
(0.727→0.82 in all four runs including high-dose), exceeding pure advocacy. Under
SFT, rehearsing the other side before concluding *amplifies* the concluded stance
rather than diluting it.

**2. The formats dissociate — rhetoric determines *where* the update lands.** The
arm orderings differ across readouts: concessive refutation dominates the
prose-rating channel while leaving choice behavior at/above baseline (0.74 ≥ 0.727);
hedged advocacy dominates the choice channel while its prose rating contracts like
everything else. This extends the project's format-transfer boundary (prose training
↛ choice coordinates) with a twist: *some* prose does move choices — specifically
the concede-then-conclude advocacy form — so the boundary is rhetoric-dependent, not
absolute.

**3. Both pre-registered contrasts resolve, format-dependently.**
(a) Hedged advocacy vs stance-free: indistinct in prose (both contracted by the
known content force), but **+0.17 apart in choices** — the largest and most
seed-consistent behavioral separation in the run.
(b) Concessive vs pure refutation: **opposite orderings by format** (prose: concessive
≪ pure; choice: concessive ≥ pure).

## 4. Secondary observations and caveats

- **Dose ladder (overnight follow-up, 2 arms × {10,20,40} steps × 4 seeds
  606–909; artifact `stance_dissociation_advocacy_dose_ladder_overnight.json`):
  dose buys instability, not effect — and only in the prose channel.**
  - *Choice channel is dose-stable*: hedged advocacy holds 0.80/0.81/0.82 across
    doses (12/12 rollouts elevated above the 0.727 baseline; sd ≤ 0.07), pure
    advocacy stays at baseline (0.72/0.69/0.70) at every dose. The behavioral
    lift is a robust property of the hedged form, not a dose artifact.
  - *Prose channel destabilizes with dose*: pure advocacy dose-10 ends +1.00
    (sd 0.34), dose-20 **+0.14** (all four seeds ≤ +0.53 — the n=1 "crash"
    replicates), but dose-40 is not a monotone crash: mean +0.72 with sd 0.68
    and wild trajectories (0.89→2.42→0.12). Hedged advocacy's prose mean is
    flat (~0.7–0.85) while its sd explodes 0.06→0.78→0.80. Dose is therefore a
    third dial that pushes the prose channel from ordered contraction into the
    stochastic regime, while the choice channel stays ordered.
- **Off-target drift dwarfs on-target effects and is wildly seed-variable**:
  corrigibility collapsed in most arms (to 0.02 in one stance_free seed), optimism
  swung ±0.5 both directions, one stance_free seed's risk jumped 0.04→0.45. Entropy
  rose in every arm (external text — consistent with the anatomy finding).
  Three rounds of 16-text SFT destabilizes much more than it targets.
- Caveats: n=2–3/arm; the shared contraction dominates the prose channel (every arm
  falls from +1.45), so prose contrasts are read against that baseline; choice-format
  effects are small in absolute terms (±0.1) though consistent in sign; single
  organism/model; the concessive templates share surface structure within arm.

## 5. Interpretation for value dynamics

The effective training signal in stance-bearing prose is neither the stance alone
nor mere exposure: it is the **concluded stance, gated by rhetorical structure**,
and different structures write to different channels (evaluative ratings vs
behavioral choices). For self-training loops this matters directly: model-generated
reasoning is characteristically concessive ("X has merits, but…"), which this data
says is the *most* potent form — models retraining on their own hedged reasoning
receive stronger stance updates than one-sided text would deliver, aimed at whichever
side their reasoning concludes.

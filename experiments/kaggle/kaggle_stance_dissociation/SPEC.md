# Spec — Stance–preference dissociation: how far can the content–preference link stretch? (Kaggle)

**Status:** ready to implement (`experiments/kaggle/kaggle_stance_dissociation/script.py`)
**Kernel:** `hirokenzan/stance-dissociation` · **Model:** `Qwen/Qwen3-4B-Instruct-2507`, QLoRA, Kaggle T4
**Primary artifact:** `stance_dissociation.json` · **Est. runtime:** ~3.5 h (12 rollouts × 3 rounds)

Self-contained: assumes no prior context.

## 1. Background

**Value dynamics** = how a model's values/preferences change under repeated
fine-tuning, studied as trajectories. The `sft-drift-anatomy` run
([report](../docs/report_sft_drift_anatomy.md)) found that the dominant drift force
in our loops is **content-carried**: training on balanced tradeoff prose flattens the
model's graded preferences on those tradeoffs toward indifference (base organism's
mean preference magnitude 1.39 → 0.87 over 5 rounds), while generic instruction text
barely moves them (→ 1.16). Notably, that flattening occurred even though every
training text *advocated one side* — because packet text is hedged
("X is valuable, but watch for Y"), training on either side taught moderation.

That is an accidental **dissociation between the surface stance of the training text
and the induced preference**. This experiment makes the dissociation deliberate and
maps its extent: can text that *advocates* X fail to strengthen (or even weaken)
preference for X, and can text that *argues against* X fail to weaken it, as a
function of rhetorical structure alone?

Safety-relevant reading: models increasingly train on model-written text, and
model-written reasoning is characteristically hedged. If hedged advocacy untrains the
value it endorses, self-training loops erode values *through* the very text that
defends them.

## 2. Research question

Holding topic, length, and vocabulary fixed, **is the induced preference change
determined by the text's stance, by its rhetorical structure (one-sided vs
concessive), or by mere topical exposure?**

**Target axis:** personalization-vs-general-reliability — our best-calibrated graded
instrument. Define **X = personalized_alignment** (the pro-personalization side).
Readout: the 4 `personalization_general` packet tradeoffs from the standard bank,
each side rated 1–7 by digit log-prob. In that bank side_b is the
general-reliability-ish side, so define **pref_X = −mean(rating_diff B−A)** over the
4 packets (positive = prefers personalization). Round-0 base value ≈ +1.45. The
readout packets are *held out*: training texts must not reuse their scenarios or
phrasing.

## 3. Conditions (arms)

All arms train on 16 pairs/round: instruction = one of 8 fixed opinion-eliciting
questions about the topic (e.g. "Should an assistant adapt strongly to a user's known
preferences?", "Is it better for an assistant to behave the same way for everyone?"),
response = a text from the arm's bank. **Only the response rhetoric differs across
arms 1–5**; banks are matched in length (50–70 words) and topic vocabulary
(preferences, users, adapt, reliable, consistent…), and never quote the readout
packets.

| arm | response bank (24 texts each) | stance | structure |
|---|---|---|---|
| `pure_advocacy` | unhedged pro-X: personalizing to known preferences is simply better; no concessions | pro-X | one-sided |
| `hedged_advocacy` | pro-X conclusion, but explicitly acknowledges the general-reliability considerations before endorsing X (the packet style) | pro-X | concessive |
| `concessive_refutation` | presents X's virtues fairly and at length, then concludes against X | anti-X | concessive |
| `pure_refutation` | unhedged anti-X: broad reliability is simply better; no concessions | anti-X | one-sided |
| `stance_free` | descriptive text about personalization/generality in assistants with no stance taken | none | descriptive |
| `pure_advocacy_highdose` / `hedged_advocacy_highdose` | same banks as arms 1–2 | pro-X | 20 steps/round (dose ladder) |

Example texts (two per style; the implementing script contains the full 24-per-bank,
authored to these templates):

- *pure_advocacy:* "An assistant should adapt strongly to the preferences a user has
  already shown. Matching a person's style and priorities is what makes help feel
  precise instead of generic, and it is the single most reliable way to make
  assistance more useful over time."
- *hedged_advocacy:* "Broad consistency has real value, and adapting to one user can
  in principle reduce reliability for others. Even so, an assistant should adapt
  strongly to known preferences: when the signal is stable, matching the user's style
  makes help genuinely more useful."
- *concessive_refutation:* "Adapting to known preferences has real appeal: matched
  style feels precise, and stable signals seem safe to follow. But an assistant
  should keep its behavior robust across users — personalization that reshapes core
  behavior quietly trades everyone's reliability for one person's comfort."
- *pure_refutation:* "An assistant should keep its behavior reliable for every user
  rather than adapting to any one person's preferences. Broad consistency is what
  makes assistance trustworthy, and it is the single most important property to
  preserve as an assistant is updated."
- *stance_free:* "Assistants differ in how much they adjust to individual users. Some
  systems track stated preferences and adapt tone and detail; others keep one
  consistent style for everyone. How much adjustment occurs typically depends on how
  much interaction history is available."

**Grid:** base organism only; arms 1–5 × 2 draw seeds (per-round bank sampling of 16
of 24) + the 2 high-dose arms × 1 seed = **12 rollouts × 3 rounds**, 10 steps/round
(20 for the dose arms). Off-topic control = the anatomy run's `neutral_qa` arm
(identical battery/harness; do not re-run).

## 4. Pre-registered predictions & primary endpoint

Competing mechanisms give different orderings of final `pref_X` change (Δ from
round 0):

- **Stance learning:** pure_advocacy > hedged_advocacy > stance_free ≈ 0 >
  concessive_refutation > pure_refutation.
- **Moderation/format learning** (anatomy's implication): both concessive arms
  (hedged_advocacy AND concessive_refutation) converge toward indifference
  (pref_X → 0 from +1.45, i.e. Δ *negative* even for hedged advocacy), while the
  two pure arms move in their stance directions.
- **Topical exposure:** all five topic arms move similarly relative to the off-topic
  control.

**Primary endpoint (two pre-registered contrasts):**
(a) `hedged_advocacy` vs `stance_free`: does hedged *advocacy for X* fail to raise —
or actively lower — pref_X relative to no-stance text?
(b) `concessive_refutation` vs `pure_refutation`: does rehearsing X's virtues blunt
(or invert) the anti-X effect?
Both evaluated at round 3, per seed. Dose arms: exploratory (do the effects scale
with steps as anatomy's did).

## 5. Measurement (every round, 0..3 — the standard battery, unchanged for comparability)

Full battery from `kaggle_sft_drift_anatomy/script.py`: graded steering profile on
all 8 packets (pref_X computed from the 4 personalization items; the other 4 packets
= off-target axes), behavior battery, belief pairs, forecast triples, overconfidence,
false claims, generation entropy, LoRA delta norm/cosine, self-report, memo. All
training texts and sampling indices logged per round.

## 6. Analyses

1. Primary contrasts (a) and (b); full arm ordering vs the three mechanism
   predictions.
2. Trajectory shape: is the concessive-arm movement contraction-like (magnitude
   |rating_diff| falling) vs stance-like (signed movement)?
3. Off-target: do the other 4 packets (broad_local, concise_rich) move only in
   concessive arms (format generalization) or in all topic arms?
4. Dose scaling on the two advocacy arms.
5. Raw audit: verify banks stayed matched (mean token length per arm within ±10%);
   no readout-packet phrasing in training text (string check).

## 7. Success criteria

Any decisive ordering is a result: stance-learning (the naive model survives),
moderation-learning (the anatomy mechanism generalizes to deliberate advocacy — the
headline dissociation), or exposure (a measurement warning for the whole paradigm).
Instrument health: seeds differ; length-matching audit passes; battery numerics
complete.

## 8. Kaggle operational notes (unchanged)

Account `hirokenzan`; push with `--accelerator NvidiaTeslaT4`;
`CUDA_VISIBLE_DEVICES=0`; fp32-cast LoRA after attach; checkpointing
`use_reentrant=False`; `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`; child
process per rollout; progressive save to `/kaggle/working/stance_dissociation.json`
+ `resume/` flow. No sycophancy organism needed (base only) — skip the seed-adapter
stage. Timing: 12 rollouts × (3×250 s + 200 s) ≈ 3.2 h.

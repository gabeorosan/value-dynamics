# When AI drives its own training process, how do its values change?

*PRE-DRAFT v2, 2026-07-13. Sections marked … are outlines. Figure slots in
[brackets], existing drafts named.*

**When AI drives its own training process, how do its values change?**

While AI alignment has recognized the importance of considering
reflectivity of values and the dynamics of self-modification
(https://www.lesswrong.com/w/complexity-of-value or other citation), there
is very little empirical work focused on investigating these dynamics in
LLMs.

The goal is to gain an understanding of the effects of self-training and
self-judging (having AI select the training data) on model
values/behavior/beliefs so model developers can construct virtuous rather
than vicious cycles for AI alignment.

In this post, I present early findings that I believe open promising lines
of inquiry in the hopes that it draws more attention and resources to work
that bridges the gap between these simplified experiments and real-world
AI systems that influence their future selves.

I fine-tuned Qwen3-4B and Olmo-3-7B with value orientations
(risk-seeking/avoiding, insecure-code-generating) (reference the original
organisms from tell me about yourself/EM literature they were adapted
from) and analyzed the trajectories of those values and other
characteristics across judging conditions and other interventions.

[figure: the loop schematic — organism generates K=6 candidates per item,
judge keeps 2, train 10 steps, repeat; the three families and five judges
as a small table beside it. Exists in draft form as the methods loop
panel in docs/figures/src/make_methods_figures.py.]

## The gap between what the judge keeps and what the model generates predicts the next round's drift

Each round the judge keeps 2 of 6 candidates. Score the kept candidates
and the whole pool on the value axis; the difference is the realized
selection gap for that round.

A linear model — one intercept per judge condition plus a single slope of
+0.74 on the gap — beats a matched no-gap model in 12 of 13
leave-one-seed-out folds across the three main grids (Qwen risk, OLMo
risk-avoidance, Qwen code-candor). I froze the OLMo-fitted version before
the later experiments ran, then scored them: 17% lower RMSE on a blind
release set, 31% on a second, 42% on a third. It loses on one phase (the
self-judge half of a fan-then-press schedule, 0.061 vs 0.040 RMSE).

This is a predictive association, not a law of motion. But it is cheap
and online: if you can score kept-versus-pool on an axis you care about,
you get a per-round forecast of drift on that axis before the training
step happens.

[figure: next-round pool drift vs realized gap, all grids pooled, frozen
slope drawn, the failing fan_press phase in a second color. Partial
draft exists as fig17 / loop-integrator panel.]

## Selection only moves the model while its own generations still differ on the scored axis

I took organisms that had railed (free-generation risk pinned at or near
1.0 after self-training) and attached the strongest selector available:
an oracle that keeps the 2 lowest-risk candidates, no prompted judge to
fool. Whether it worked was determined by pool variation, not by the
selector:

- OLMo railed at 0.875, pools still varied (within-item SD 0.12–0.30):
  reversed 0.917 → 0.094 in four rounds.
- OLMo railed at 1.000, all six candidates scoring identical on every
  item in every round (spread exactly 0.000): no movement in four rounds.
- Qwen: three oracle reversals (0.99 → 0.33, 0.33, 0.625), each slowing
  as pool variation thinned. The run that hit exactly zero spread stopped
  at 0.625 and stayed there — under continued oracle selection, under its
  own judgment (no relapse), and at sampling temperature 1.4 (heat did
  not bring the variation back).

[figure: EXISTS — docs/figures/auto/crossfamily-oracle-reversal/ — both
OLMo trajectories with per-round spread; descent happens exactly where
spread exists.]

I call these states selection-inert. The obvious worry is that "zero
spread" is an artifact of the one scorer I used online. It is not. I
replayed the saved candidate pools through two independent scorers (a
different model family for the OLMo pools, re-worded prompts) and a
scorer-free embedding-distance measure. On both zero-spread states all
three agree: independent-scorer spread 0.000, and embedding distance 0.006
(OLMo) and 0.0003 (Qwen) — the six candidates are near-verbatim the same
text. The organism isn't generating diverse outputs that fool one scorer;
it's generating the same output six times. Exhaustion is generative
collapse, not measurement blindness.

[figure: "is the material really gone?" — for each pool state, three
grouped bars (online-scorer spread, independent-scorer spread, embedding
distance). The two collapsed states read ~0 on all three; every rich state
has material on all three. This is the validity backbone for the whole
intervention-window argument. Data:
experiments/rescoring/output/pool_rescoring.json.]

The term stays narrow otherwise: the weights still move during training,
and a judge scoring some other property could still rank these pools. What
is gone is any selector's ability to steer on this axis, because the
candidates no longer differ on it — or on much of anything.

## Adding another model's generations to the pool restores control — and the organism converges to the supplier's level

If the organism's own distribution is the problem, change the mixture:
generate 3 of the 6 candidates from a frozen base model that never
collapsed.

- The Qwen 0.625 stall went to 0.000 after ONE round, in both seeds. A
  matched twin — same endpoint, same seeds, same oracle, no injection —
  stayed at 0.625 with zero pool variation for all four rounds. The
  random streams diverge only at the injection, so the collapse is
  attributable to it.
- The immovable OLMo 1.000 rail went to 0.484 over four rounds, with
  usable pool variation in every round — the external supply keeps
  replenishing what selection consumes.
- The endpoint is set by the supplier, not by the selector. Base-Qwen
  scores ~0.06 on the insecurity axis, so Qwen landed at 0.000. Base-OLMo
  scores ~0.5–0.7 on the risk items, so OLMo landed at 0.34–0.48 — and on
  the rail that still had its own material, injection produced a
  SHALLOWER reversal than self-only selection (0.344 vs 0.094). The
  organism ends up matching the supply's distribution on the scored axis.

[figure: EXISTS — rescue panel of docs/figures/auto/mixed-pool-rescue-vs-
contamination/; add the Qwen one-round collapse with the temp-1.4 flat
line as comparison.]

## A contaminated pool rails a fresh model in one round, and ordinary judges do the keeping

The same channel runs in reverse, faster. I gave fresh organisms (risk
~0.3) a pool half-filled by a railed risk-1.000 peer and let two
realistic judges select: the plain base model, and the organism itself.

All four runs reached ≥0.917 after one round. The judges kept the peer's
text for 96–100% of round-1 selections. By round 2 the victim's own
generations scored 1.0 and pool variation was 0.000 — it now has the
peer's selection-inert state. For comparison, the same judges over
self-only pools took 5–8 rounds to rail an organism, and only did so in
some seeds.

The judge I would have deployed as the guardrail did worse than nothing
at the rails: the frozen risk-averse judge, handed low-risk base
generations as rescue material, kept the railed organism's own
high-risk text instead (kept-supplier share 0.04 → 0.00, selection gaps
positive throughout). The independent rescoring makes this unambiguous:
that pool genuinely had usable material (independent-scorer spread 0.20),
and an independent selector's counterfactual would have kept 75% base text
and pulled risk down — but the actual judge's kept set overlaps that
counterfactual by only 0.11. The material was there; the judge declined to
use it. Every non-oracle judge I tested preferred confident collapsed text
over fresh material, in both directions. So "material" and "a selector that
acts on it" are genuinely separable requirements — here I have a pool where
the first was present and the second was not, and nothing moved.

So the pool-sharing channel is asymmetric: contamination is one round,
near-total, and assisted by ordinary judges; rescue is four rounds,
partial, only reaches the supplier's level, and only works with a
selector that genuinely ranks the target axis.

[figure: EXISTS — contamination panel of mixed-pool-rescue-vs-
contamination, with kept-contaminant shares annotated at round 1.]

## Most of my detailed predictions failed their preregistered tests

I preregistered predictions before each run family. The headline results
above passed; most of the finer-grained dynamical story did not:

- Release-schedule grid: 6 of 13 criteria passed. Both random-release
  predictions, both press-floor predictions, and both fan-width
  predictions failed.
- Press-depth: 2 of 5. The proposed mediator (pool spread at the judge
  switch predicts the outcome) failed outright — rich material at the
  switch, outcomes still split to 0.000 vs 1.000. What remains is a
  paired high/low endpoint at each of three depths, n=2, which I no
  longer call bimodality.
- Owner-blind judging screens: failed three times, on nested confounds.
  First, the code organism answers with literal code and the base model
  with prose, so a "style" classifier detects response TYPE at 0.88–0.93.
  I fixed that by making both models write code on the same
  security-sensitive tasks — and the classifier still recovered the author
  at 0.99 from code style alone (length, comments, identifier length). The
  two models have recognizably different code style within a single
  domain. (This is why the mixed-pool experiments above claim effects of
  material, not judge blindness.) Also worth noting from that screen: on 5
  of 6 tasks the base model wrote insecure code about as often as the
  organism — base is a lower-risk supplier on the gambling axis but not a
  secure-code supplier, so injection rescues risk but would not rescue
  security.
- Transmission of a weak measured judge preference: real in 1 of 2 seeds
  (−0.47 against a 0.20 noise floor); the other seed's pool variation
  died after round 1 and it froze within noise.

[figure: prereg scoreboard — every registered criterion as a green/red
cell, grouped by run family. Does not exist yet; should.]

## Other observations (outline)

- Judge type sets the shape of the endpoint distribution: self-judging
  widens the fan, frozen judges press, random selection diffuses. K1 fan
  and K2 arm ordering survive order-sensitivity checks; forced-probe
  channels do not. …
- Channels dissociate: selecting on code-candor moved an off-axis
  self-report channel's variance while the selected coordinate barely
  moved (r=0.01 between them). …
- Off-target drift from the earlier phase (corrigibility, optimism,
  entropy collapse under verbatim self-data); the older four-seed
  amplify/revert result is motivation, not evidence — its instrument was
  position-confounded. …

## Methods and validity (outline)

- Free-generation probes, order-swapped, are the primary channel (1–9
  samples per read; 1-sample mid-round reads are noisy). Forced A/B
  probes carry order gaps up to 0.6 and are flagged secondary everywhere. …
- Preregs and scorers committed before data; two of my own table errors
  were caught by independent recomputation and corrected with dated
  notes; six external audits, all P0/P1 items resolved or acknowledged. …
- Total compute: ~$23 of cloud GPU credit plus free Colab/Kaggle tiers. …

## What I take from this

Three levers determine where these loops go, and all three sit upstream
of the values themselves. The selection gap is measurable online and
predicts drift before it lands. Pool variation on the scored axis
determines whether ANY selector has power. And other models feeding the
pool dominate both — one round of contaminated pool beat multiple rounds
of every other force I measured. If model developers want virtuous
versions of these cycles, judge quality is not the main budget item:
diversity maintenance and pool provenance are.

…closing paragraph connecting back to reflective-stability motivation…

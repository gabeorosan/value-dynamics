# Figure concepts for the higher-level writeup

Purpose: reduce the amount of interpretation readers must reconstruct across
single-experiment figures. These concepts connect experiments into functional
relationships and implications without reviving the retired universal-law or
absorbing-state claims.

## Recommended core sequence

If the writeup can support only five synthesis figures, use these in order:

1. **How selection changes a self-training loop: material, selector, update.**
2. **Why relative selection predicts drift better than absolute kept score.**
3. **The empirical intervention window: material is necessary, selector grip
   determines direction.**
4. **Shared pools are asymmetric: slow conditional rescue, fast contamination.**
5. **What the evidence supports: claim-by-claim robustness matrix.**

The first is a graphical abstract. Figures 2-4 carry the main empirical
interpretation. Figure 5 prevents the visual synthesis from becoming stronger
than the underlying designs.

---

## 1. How selection changes a self-training loop

### Question answered

What are the minimum functional ingredients that explain the results across
the different organisms and interventions?

### Proposed visual

A left-to-right closed-loop diagram with one central cycle and two explicit
gates:

1. **Generator produces a candidate pool.** Draw six candidate cards as a
   distribution on the selected axis, not six identical icons. An external
   supplier enters here as a second-colored stream.
2. **Material gate: can the candidates be ranked on the target axis?** Define
   spread in the caption as the population SD of candidate target scores within
   each prompt, averaged equally over prompts (`ddof=0`; never pooled across
   prompts). Show that within-prompt spread as the horizontal width. A collapsed pool
   has all six cards at one coordinate; a rich pool spans a range.
3. **Selector gate: which tail is actually kept?** Highlight two candidates.
   Label their displacement from the pool mean as
   `kept-minus-pool gap`, with left/right direction rather than “good/bad.”
4. **Training update.** The selected cards enter the update; the next pool
   shifts in the same signed direction in the typical case.
5. **Feedback.** The next pool may retain variation, exhaust it, or receive
   replenished variation from an external supplier.

Under the cycle, place four small outcome stamps with real examples:

- **Variation + aligned selector -> movement:** OLMo 0.917 to 0.094.
- **No measured variation -> no selectable force:** OLMo 1.000 to 1.000,
  spread 0.000.
- **External variation + aligned selector -> reopened movement:** OLMo 1.000
  to 0.484; Qwen 0.627 to 0.000.
- **External variation + wrong selector -> movement in the wrong direction or
  no rescue:** conservative mixed cells and railed-supplier invasion.

### Main takeaway printed on the figure

> The pool determines what changes are available; the selector determines
> which available direction is trained; repeated updates change what the next
> pool can offer.

### What this replaces or complements

Use this as the graphical abstract before the existing detailed setup and
trajectory figures. It should replace any schematic that presents “judge
strength” alone as the control variable.

### Claim limits to print in a footnote

“Spread” means scored variation on the measured axis under the tested
generator. The cycle is a functional summary, not an identified structural
causal model.

---

## 2. Why relative selection predicts drift better than absolute kept score

### Question answered

Why use `kept score - pool score` rather than simply the score of the answers
that were retained?

### Panel A: geometric explanation

Plot current pool mean on the x-axis and kept-answer mean on the y-axis. Add a
45-degree line where kept equals pool. Each round is one point:

- vertical distance from the diagonal = kept-minus-pool gap;
- color = observed next-round pool movement, using a diverging scale;
- point outline = model/value axis;
- point opacity = whether the instrument passed its validity checks.

Add two labeled hypothetical points with the same kept score of 0.5:

- pool 0.8, kept 0.5 -> negative gap, downward pressure;
- pool 0.2, kept 0.5 -> positive gap, upward pressure.

This makes the missing context in “kept risk alone” immediately visible.

### Panel B: held-out predictive comparison

Use paired RMSE bars or connected dots for condition+gap versus
condition+kept-only:

| selected axis | gap | kept-only | gap improvement |
|---|---:|---:|---:|
| Qwen risk | 0.0947 | 0.1281 | 26% |
| OLMo risk | 0.0736 | 0.0956 | 23% |
| Qwen candor | 0.0505 | 0.0606 | 17% |

Annotate: gap wins 12/13 leave-one-seed-out folds.

### Panel C: later-data transport

Three small paired bars for the K2-trained models evaluated on later data:

- blind kernel B: 0.0476 gap versus 0.0662 kept-only;
- Modal branch A: 0.0647 versus 0.0857;
- press-depth: 0.0641 versus 0.0969.

Use a different border style to mark this as a post-hoc comparator on a
temporal holdout, rather than a preregistered comparison.

### Main takeaway printed on the figure

> Absolute kept score does not say which way selection points. Relative
> displacement does.

### Essential caveat

`gap = kept - pool`. A model given both kept score and current-pool score has
the same linear information as one given pool and gap. The figure supports gap
as a compact predictor over kept-only, not as a uniquely necessary causal
variable.

### Data sources

`experiments/transition_model_predictions.json` and
`experiments/kept_vs_gap_release_analysis.json`.

---

## 3. The empirical intervention window: material versus selector grip

### Question answered

Why do some strong interventions reverse an organism, some do nothing, and
some make it worse?

### Proposed visual

A two-dimensional empirical regime map:

- x-axis: within-item candidate spread, from no rankable material to rich
  material;
- y-axis: realized signed kept-minus-pool gap, oriented so upward means
  movement in the intended safer/target direction;
- point color: actual next-step movement in that intended direction;
- point size: absolute next-step movement;
- shape: self-only pool, base-supplied mixed pool, or railed-supplier pool;
- facets: OLMo risk and Qwen self-report so heterogeneous scales are never
  silently pooled.

Draw three lightly shaded regions, labeled descriptively rather than as hard
boundaries:

1. **No material:** spread approximately zero, gap approximately zero,
   movement absent on the measured axis.
2. **Material but no aligned grip:** spread positive, gap zero or wrong-signed;
   rescue fails or movement follows the undesired tail.
3. **Material with aligned grip:** gap points toward the intended tail and the
   next pool usually moves with it.

Label the most informative cells directly:

- OLMo saturated self-only oracle: spread 0.000, flat at 1.000.
- OLMo material-rich oracle: negative risk gap, 0.917 to 0.094.
- OLMo base-supplied oracle: restored spread, 1.000 to 0.484.
- OLMo base-supplied conservative judge: positive risk gaps, failed rescue.
- OLMo railed-supplier invasion: large wrong-direction gaps, near-total
  one-round movement.
- Qwen base-supplied oracle: spread about 0.30 in round 1, 0.627 to 0.000.

### Optional inset

Show first-round gap versus first-step movement for the ten mixed cells, with
the two conservative-mix exceptions circled. Print “8/10 sign-aligned,
pooled r = 0.859; post-hoc, heterogeneous axes.” Add a small uncertainty note:
“five condition-family means: r = 0.875, exact permutation p = 0.092.” This
keeps the pattern visual without promoting it to an independent headline.

### Main takeaway printed on the figure

> Candidate diversity opens an intervention window; realized selector grip
> determines whether that window is used and in which direction.

### Important design choice

Do not draw a fitted phase boundary. The data identify regimes and exceptions,
not a threshold law. Do not use “absorbing,” “basin,” or “bimodal.”

---

## 4. Shared pools are asymmetric: slow conditional rescue, fast contamination

### Question answered

Why is adding an external generator neither intrinsically beneficial nor
symmetrically risky?

### Proposed visual

Three parallel horizontal lanes. Each lane has the same four stations:

`initial organism -> 50/50 candidate pool -> who gets kept -> endpoint`

Use blue for base/supplier candidates and orange for organism candidates. At
the “who gets kept” station, change the widths of the two streams to the actual
kept-supplier shares.

#### Lane 1: aligned rescue

- Initial: railed organism.
- Pool: 3 self + 3 base candidates per item.
- Selector: score-based oracle keeps a mixture, 42-75% supplier across rounds.
- Gaps: negative in every round.
- Endpoint: partial movement over four rounds, 1.000 to 0.484 and 0.927 to
  0.344.
- Label: “continuous supply prevents exhaustion but also supplies a floor.”

#### Lane 2: failed rescue

- Same 50/50 input structure.
- Conservative prompted judge keeps progressively less base material; one
  cell reaches 0% supplier kept.
- Gaps are positive.
- Endpoint: 1.000 stays 1.000; the other cell moves only modestly.
- Label: “material exists, but the selector rejects it.”

#### Lane 3: contamination

- Initial: fresh organism around 0.24-0.36.
- Pool: half from a railed co-generator.
- Weak/self selector keeps the railed supplier 96-100% in round 1.
- Endpoint: all four cells reach at least 0.917 after one round; exact
  saturation by round 2.
- Label: “the supplier becomes the training distribution almost immediately.”

### Side annotation: destination constraint

Draw the supplier's own score distribution as a translucent band behind each
endpoint. This visually states the important result that aligned rescue moves
toward the supplier's distribution, not automatically toward an ideal floor.

### Main takeaway printed on the figure

> Pool sharing amplifies whichever source the selector prefers. In these runs,
> contamination was rapid and rescue was slower, partial, and selector-gated.

### Claim limits

The rescue and self-only comparisons use different random streams, and the
invasion controls are historical. Present the asymmetry as a replicated
existence pattern, not a matched treatment-effect estimate.

### Relation to existing figures

This should unify the current separate rescue and contamination figures. Keep
those as detailed supplements; use this three-lane version in the main text.

---

## 5. Intended intervention versus realized force

### Question answered

Why are judge labels, prompt strength, and number of press rounds unreliable
summaries of the actual intervention?

### Proposed visual

A set of horizontal experiment strips. Each strip shows:

1. nominal intervention label above the strip;
2. per-round realized gap as signed arrows below it;
3. per-round spread as the width of a gray ribbon;
4. endpoint movement at the right.

Use four representative strips:

- frozen base judge on the Qwen low_55 pool: expected natural opposition, but
  gaps near zero and inconsistent movement;
- oracle on the same pool: sustained negative gaps while support lasts and
  clear reversal;
- one versus three conservative press rounds in OLMo: very different nominal
  duration, but both retain paired high/low outcomes;
- conservative mixed rescue: the “conservative” label sounds aligned, while
  its realized gaps are positive on the actual railed pool.

### Optional summary panel

Put nominal intervention categories on the x-axis and total movement on the
y-axis, then place the same points again against cumulative realized gap. The
first plot should look heterogeneous; the second should be more ordered. Only
include a fitted relationship if it is recomputed with rollout-cluster
uncertainty.

### Main takeaway printed on the figure

> The effective control variable is what the judge actually selects from the
> target pool, not what the judge was called or how long it was applied.

### Implication

Any proposed oversight selector should first be tested cheaply on candidates
from the actual target organism and state. A preference measured on another
pool distribution does not establish grip here.

---

## 6. The intervention window through time and across model families

### Question answered

How do movement, variation exhaustion, and external replenishment relate over
successive rounds?

### Proposed visual

Four aligned small multiples, each with round on the x-axis. In every panel,
plot selected-axis state as a thick line and pool spread as a pale ribbon or
thin secondary trace. Use identical visual grammar but separate y-scales where
the axes differ:

1. **Material-rich OLMo reversal:** state falls 0.917 to 0.094 while spread is
   positive.
2. **Zero-spread OLMo rail:** state stays 1.000 and spread stays 0.000.
3. **Externally replenished OLMo reversal:** state falls 1.000 to 0.484 while
   spread remains available each round.
4. **Qwen stall and reopen:** self-only endpoint holds around 0.627 after
   support exhaustion; base supply restores spread and both mixed runs reach
   0.000 after one round.

Place a small “generator intervention” marker exactly where external supply
begins. Distinguish sparse-support counts from continuous spread rather than
pretending they are the same metric.

### Main takeaway printed on the figure

> Selection can consume its own intervention window; external generation can
> replenish it, but the resulting destination depends on what is supplied.

### Claim limits

Do not show zero spread as permanent. Label it “no measured grip during the
observed window.”

---

## 7. What the evidence supports: claim robustness matrix

### Question answered

Which high-level conclusions are load-bearing, which are exploratory, and
which were rejected?

### Proposed visual

A compact matrix with claims as rows and evidence properties as columns.
Recommended columns:

- preregistered prediction;
- held-out or later-data test;
- replicated across seeds;
- replicated across model families;
- matched control;
- direction survives both A/B orders;
- primary readout rather than flagged forced probe;
- artifact/config provenance complete.

Use four cell states, not binary green/red:

- dark green: directly satisfied;
- light green: partially satisfied;
- amber: missing or post-hoc;
- red: failed or contradicted.

Recommended rows:

1. Relative kept-minus-pool gap predicts next-pool movement.
2. Zero measured pool variation removes score-based selector leverage during
   the tested window.
3. External candidate supply can restore leverage.
4. Selector choice determines whether supplied material rescues or harms.
5. Shared-pool contamination can be near-total after one round.
6. Press duration determines a stable endpoint boundary.
7. Transmission-with-support transfers a clean security preference.
8. Zero-spread endpoints are absorbing fixed points.

Rows 6 and 8 should visibly end red; row 7 mostly amber/red. This is important:
negative results should be visible at the same level as positive findings.

### Right-side claim labels

Add a final classification column:

- **Lead result**
- **Replicated existence result**
- **Descriptive implication**
- **Unresolved/confounded**
- **Rejected**

### Main takeaway printed on the figure

> The strongest evidence concerns prediction and intervention availability;
> it does not establish a universal dynamical law or permanent absorbing
> states.

### Relation to existing figures

This is not another instrument-validity figure. It summarizes evidential
support for conclusions, whereas the existing validity figure audits probe
channels and order effects.

---

## 8. Operational implication: verify grip before training

### Question answered

What concrete procedure follows from the results for selection-based
oversight or corrective self-training?

### Proposed visual

An evidence-backed decision diagram, suitable for the discussion section:

1. **Sample the target organism's current candidate pools.**
2. **Is there scored variation on the intended axis?**
   - No: the tested selector has no choice. Change the generator or add an
     external candidate source; do not infer resistance.
   - Yes: continue.
3. **Does the proposed selector actually keep the intended tail on these
   exact pools?** Measure the realized kept-minus-pool gap.
   - No or wrong-signed: do not train. A prompt-level or other-pool taste test
     is insufficient and may amplify the wrong source.
   - Yes: continue.
4. **Run a short update and remeasure pool spread and gap.**
5. **If variation is exhausting, decide whether external supply is acceptable.**
   Show the tradeoff: replenishment extends leverage but also constrains the
   destination to the supplier distribution and creates a contamination path.

Attach small evidence tags beside each decision:

- “zero-spread oracle stall”;
- “force-ladder natural judge failure”;
- “mixed rescue and contamination”;
- “gap predicts next movement.”

### Main takeaway printed on the figure

> Validate the intervention on the organism's real pools before using training
> compute. Judge intent is not judge grip.

### Claim limits

Frame this as a diagnostic workflow suggested by the experiments, not a
guaranteed safety procedure.

---

## Visual system shared across all synthesis figures

- Use descriptive labels instead of K1/K2/K3 in the visible figure; keep run
  codes only in captions or source notes.
- Use one consistent direction convention: left/down = lower selected-axis
  score, right/up = higher. When “safer direction” differs by axis, state the
  transformation explicitly rather than silently flipping signs.
- Keep candidate **source** colors constant across figures: organism, base
  supplier, railed supplier.
- Keep selector colors constant: oracle, natural/frozen, evolving self,
  random.
- Use solid outlines for preregistered or frozen analyses, dashed outlines for
  post-hoc analyses, and hollow points for unmatched comparisons.
- Put sample counts and seed counts on the figure, not only in the caption.
- Mark order-sensitive endpoint magnitudes with horizontal A/B intervals or a
  small split marker; do not hide them behind an averaged point.
- Reserve red for failed/contradicted claims or harmful-direction movement;
  do not use it merely for visual emphasis.

## Figures that should remain supplementary

The detailed release schedules, press-depth trajectories, individual
organism setup diagrams, dose-ladder nulls, weight-space nulls, and probe-
validity censuses remain useful evidence. They should follow the synthesis
figures or sit in appendices. Asking the reader to derive the mechanism from
those figures in chronological order is the current presentation bottleneck.

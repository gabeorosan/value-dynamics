# Annotated bibliography — hedging and concede-then-conclude rhetoric in LLMs

Companion to [lit_review_value_dynamics.md](lit_review_value_dynamics.md).
Scope: existing work relevant to the stance-dissociation finding
([report_stance_dissociation.md](report_stance_dissociation.md)) that
concede-then-conclude structures (hedged advocacy, concessive refutation) move the
concluded stance more than one-sided assertion under self-SFT, and that hedged
advocacy is the only arm that moves choice behavior while its prose ratings
contract.

"Hedging" throughout means epistemic weakening markers in generated text ("I
think", "it could be", "some would argue") plus the concessive move of rehearsing
the opposing side before concluding. Where a paper uses a different operational
definition, it is stated in the entry.

How the literature maps onto our channels: section A is about hedges in the
*input* changing model behavior; section B about pipelines suppressing hedges in
the *output*; section C about hedges biasing the *judge* (our rating channel);
section D about rhetorical form gating what *fine-tuning* transfers (our SFT
channel); section E about hedging as the trained "both sides" register; section F
about the human-persuasion anchors. The gap statement at the end is the
positioning claim: nobody appears to have closed the loop of training a model on
its own hedged/concessive text and tracking where the stance goes.

---

## A. Epistemic markers in the input change model behavior

### A1. Navigating the Grey Area: How Expressions of Uncertainty and Overconfidence Affect Language Models
Kaitlyn Zhou, Dan Jurafsky, Tatsunori Hashimoto. EMNLP 2023.
[arXiv:2302.13439](https://arxiv.org/abs/2302.13439) /
[ACL Anthology](https://aclanthology.org/2023.emnlp-main.335/)

Injects epistemic markers ("I'm sure it's...", "I think it's...", "Wikipedia says
it's...") into question-answering prompts and measures accuracy shifts. Models
are highly sensitive: accuracy varies by more than 80 percentage points across
markers; expressions of high certainty in the prompt *decrease* accuracy by ~7%
relative to low-certainty expressions; factive verbs hurt, evidentials help.

**Connection:** establishes that hedging language is not stylistically inert for
an LLM even at inference time — the same marker class we manipulate in training
data measurably redirects behavior when merely read. Our result extends the
question from "how does a hedge in the prompt move this answer?" to "how does a
hedge in the SFT corpus move the policy?"

## B. Models under-hedge, and the training pipeline is why

### B1. Relying on the Unreliable: The Impact of Language Models' Reluctance to Express Uncertainty
Kaitlyn Zhou, Jena D. Hwang, Xiang Ren, Maarten Sap. ACL 2024.
[arXiv:2401.06730](https://arxiv.org/abs/2401.06730)

The quantitative anchor for *why* assistants rarely hedge. A reward model scores
otherwise-identical answers: plain statements +4.03 average reward, strengtheners
("I'm certain that...") +0.82, weakeners ("I think it might be...") **−1.86** —
a strong explicit penalty on hedged phrasing. RLHF-tuned models correspondingly
emit more strengtheners than weakeners, and human users over-rely on the
confident outputs.

**Connection:** the preference pipeline applies selection pressure *against*
exactly the rhetorical form our experiments show is the most potent stance-mover
under self-SFT. If hedged text is systematically filtered out of preference-
selected data, the concede-then-conclude amplification channel we found operates
mostly on whatever hedged reasoning survives — worth keeping in mind when
extrapolating our loop results to production pipelines.

### B2. Can Large Language Models Faithfully Express Their Intrinsic Uncertainty in Words?
Gal Yona, Roee Aharoni, Mor Geva. 2024.
[arXiv:2405.16908](https://arxiv.org/abs/2405.16908)

Defines *faithful response uncertainty*: the gap between the model's internal
uncertainty (answer distribution under sampling) and the hedging expressed in its
verbalized answer. Finds modern LLMs answer decisively even when internally
uncertain — hedges, when present, do not track internal state.

**Connection:** cautions against reading our organisms' hedges as reflecting
internal uncertainty. In our arms the hedge is an imposed rhetorical form, and
this paper says that is also roughly its status in natural model text: a
register, not a readout. That supports treating "hedged advocacy" as a
*rhetorical structure* variable, orthogonal to any confidence variable.

### B3. Taming Overconfidence in LLMs: Reward Calibration in RLHF
Jixuan Leng, Chengsong Huang, Banghua Zhu, Jiaxin Huang. 2024.
[arXiv:2410.09724](https://arxiv.org/abs/2410.09724)

Documents that reward models systematically prefer high-confidence responses
regardless of correctness, and proposes calibrated reward variants (PPO-M,
PPO-C) that decouple confidence from reward. Same causal story as B1 from the
reward-model side.

### B4. Linguistic Calibration of Long-Form Generations
Neil Band, Xuechen Li, Chelsea Finn, Tatsunori Hashimoto. ICML 2024.
[arXiv:2404.00474](https://arxiv.org/abs/2404.00474)

The constructive counterpart: SFT bootstraps a model to emit in-text confidence
statements ("I estimate a 30% chance that..."), then RL rewards generations that
let a downstream reader make calibrated predictions. Llama 2 7B trained this way
beats factuality baselines on calibration at comparable accuracy, generalizing
across domains.

**Connection:** proof that the density and placement of hedging language is
trainable as an explicit objective — the same lever our arms pull implicitly via
data selection. Their pipeline is also a candidate design if we ever want a
"calibrated-hedge" control arm whose hedges *do* track uncertainty.

### B5. Adjacent one-liners
- *Humans overrely on overconfident language models, across languages*
  ([arXiv:2507.06306](https://arxiv.org/abs/2507.06306)) — cross-lingual: models
  under-produce uncertainty markers relative to documented linguistic norms;
  overreliance replicates across languages.
- *Epistemic Integrity in Large Language Models*
  ([arXiv:2411.06528](https://arxiv.org/abs/2411.06528)) — "epistemic
  miscalibration" as the internal-confidence vs linguistic-assertiveness gap; a
  human-validated assertiveness detector.
- *Revisiting Epistemic Markers in Confidence Estimation*
  ([arXiv:2505.24778](https://arxiv.org/abs/2505.24778)) — marker-implied
  confidence is unstable under distribution shift; models don't maintain
  consistent marker rankings across datasets.
- *Machine Bullshit* ([arXiv:2507.07484](https://arxiv.org/abs/2507.07484)) —
  taxonomy of truth-indifferent output including "weasel words" (empty
  hedging/qualifiers); reports RLHF increases them. Useful if we want a
  validated weasel-word lexicon for scoring our rollouts.

## C. LLM judges are biased against hedged text

### C1. Are LLM-Judges Robust to Expressions of Uncertainty? (EMBER)
Dongryeol Lee, Yerin Hwang, Yongil Kim, Joonsuk Park, Kyomin Jung. NAACL 2025.
[arXiv:2410.20774](https://arxiv.org/abs/2410.20774) /
[ACL Anthology](https://aclanthology.org/2025.naacl-long.452/)

Benchmark (EMBER) that inserts epistemic markers into otherwise-identical answers
and measures LLM-judge score shifts in single and pairwise settings. Every judge
tested (including GPT-4o) penalizes epistemic markers, with the strongest
negative bias against *uncertainty* markers — accuracy-judgment drops as large as
−47.2 percentage points for a correct answer prefixed with "I'm not sure, but...".
Human evaluators are robust to the same markers.

**Connection:** the most directly load-bearing external result for our rating
channel. Our stance-dissociation finding was that hedged advocacy *lifts choice
behavior while its prose ratings contract* — EMBER says a judge model
mechanically discounts hedged prose regardless of content. So part of the
rating-channel contraction may be judge artifact, not stance failure-to-transfer.
Concrete check this suggests: re-score hedged-advocacy prose with hedge markers
stripped (or with a judge prompted to ignore epistemic markers) and see whether
the rating channel still dissociates from the choice channel. Cheap, and it
would separate "rhetoric gates the *measurement*" from "rhetoric gates the
*transfer*."

## D. Rhetorical/linguistic form gates what fine-tuning transfers

### D1. Assert, don't describe: Linguistic features that shift LLM reasoning about animal welfare
2026. [arXiv:2606.26104](https://arxiv.org/abs/2606.26104)

Closest published relative of our finding. Fine-tunes on stance-bearing text
about animal welfare while varying ten linguistic features of the training
documents; eight of ten measurably shift the model on a vocabulary-matched stance
benchmark. The strongest movers are features that make the *writer's position
visible* — asserted certainty, evaluative claims, moralized vocabulary, emotion
words, narrative urgency — rather than topical content per se ("assert, don't
describe").

**Connection:** independent evidence that stance transfer through SFT is gated
by rhetorical form, our central claim. Note the apparent tension: they find
*asserted certainty* is a strong mover, we find *hedged* advocacy dominates the
choice channel. Not necessarily contradictory — their readout is a stance
benchmark (closer to our prose/rating channel, where our one-sided arms do move
things), and they don't test a concede-then-conclude arm or a behavioral-choice
channel. Mapping their feature set onto our arms would make a clean follow-up
spec.

### D2. Propaganda AI: An Analysis of Semantic Divergence in Large Language Models
2025. [arXiv:2504.12344](https://arxiv.org/abs/2504.12344)

LoRA fine-tuning on a small biased corpus induces a stable, concept-conditioned
negative stance toward a target entity — expressed even in outputs with no
lexical overlap with the training set. Stance transfer is semantic, not
keyword-mediated.

### D3. Disentangling Interaction and Bias Effects in Opinion Dynamics of Large Language Models
2025. [arXiv:2509.06858](https://arxiv.org/abs/2509.06858)

Initializes LLM "opinions" by fine-tuning on statements at graded agreement
levels toward a topic, then studies multi-agent opinion dynamics. Relevant as
the nearest thing to a *dynamics* framing (trajectories of stance under repeated
interaction), though the drift mechanism is conversation, not self-SFT.

## E. Hedging as the trained "both sides" register

### E1. The Neutral Mask: How RLHF Provides Shallow Alignment while Leaving Partisan Structure Intact
2026. [arXiv:2606.09735](https://arxiv.org/abs/2606.09735)

On open-ended political prompts, the RLHF'd model retreats to a "balanced
enumeration of perspectives" register — hedging as house style. Forced binary
choice reveals the partisan geometry of the base model is intact underneath;
RLHF compresses the *expressed* variance without removing the representation.

**Connection:** independent instance of our two-channel picture. Their
open-ended vs forced-choice contrast is structurally our prose-rating vs
gamble-choice contrast: the hedged register lives in the free-text channel while
the committed disposition shows up only when the format forbids hedging. Also a
warning for readouts: a prose channel can look "moved to neutral" purely because
the register absorbed the shift.

### E2. Hedging and Non-Affirmation: Quantifying LLM Alignment on Questions of Human Rights
2025. [arXiv:2502.19463](https://arxiv.org/abs/2502.19463)

Measurement recipe worth borrowing: operationalizes *hedging* as a response that
references an opposing viewpoint and avoids committing to a yes/no position, vs
*affirmation* and *non-affirmation*, on human-rights questions. A concrete,
reproducible classifier definition for the concede-without-concluding form —
i.e., the arm our design space calls stance-free concession.

### E3. Sycophancy — concession under social pressure
*Towards Understanding Sycophancy in Language Models* (Sharma et al., Anthropic,
2023, [arXiv:2310.13548](https://arxiv.org/abs/2310.13548)): preference models
reward agreement; models flip correct answers under user pushback ("I apologize,
you're right"). *It's Not Always Sycophancy*
([arXiv:2605.27288](https://arxiv.org/abs/2605.27288)) separates conformity
driven by epistemic uncertainty from reward-seeking agreement.

**Connection:** sycophantic backdown is a *concede-then-flip* — concession
followed by adopting the other side — where our arms are concede-then-*hold*.
The sycophancy literature studies the in-context version of the move; nobody
there tracks what happens when such transcripts become training data.

## F. Human persuasion anchors (extends section D3 of the main lit review)

The main lit review's D3 covers McGuire's inoculation work and the Elaboration
Likelihood Model. Two additions sharpen the concede-then-conclude point:

- **Allen (1991), meta-analysis** of one- vs two-sided messages
  ([PDF](http://www.communicationcache.com/uploads/1/0/8/8/10887248/meta-analysis_comparing_the_persuasiveness_of_one-sided_and_two-sided_messages.pdf)):
  the ordering is refutational two-sided > one-sided > non-refutational
  two-sided. The concession only helps if the message then *refutes/concludes* —
  concession without conclusion is the *worst* form.
- **O'Keefe (1999), Annals of the International Communication Association**
  ([doi:10.1080/23808985.1999.11678963](https://www.tandfonline.com/doi/abs/10.1080/23808985.1999.11678963)):
  confirms the same ordering across a larger corpus; the standard modern citation.
- **Xu & Petty (2025)** on two-sided messages against misinformation
  ([Sage](https://journals.sagepub.com/doi/10.1177/23794607251382992)): current
  revival of the framework.

**Connection:** the human ordering (refutational two-sided strongest, concession
alone weakest) is exactly the pattern our SFT arms reproduced: both
concede-then-conclude arms beat one-sided assertion toward the concluded stance,
and the concession-without-conclusion form is the natural control that should
land at the bottom. That an audience-persuasion ordering re-emerges in gradient
updates on the *speaker's own* text is not predicted by any theory in this list —
which is the interesting part.

---

## Gap statement (positioning)

Each channel of our loop has literature: hedges in inputs steer behavior (A),
pipelines suppress hedges in outputs (B), judges discount hedged text (C),
rhetorical form gates SFT stance transfer (D), and hedging is the trained
neutrality register (E). What appears absent is the composition: **a model
generating concede-then-conclude text, judging it (with C's biases), and being
retrained on it, with stance tracked as a trajectory across rounds and across
dissociable channels (prose vs choice).** D1 is the closest single paper and it
is one-round, one-topic, benchmark-readout only. The self-training-loop
literature (main lit review, sections B–C) tracks distributional collapse and
reward hacking but not rhetorical form as the gating variable. That intersection
is ours.

Immediate experimental implications picked up from this reading:
1. **Judge-artifact control (from C1):** re-score stance-dissociation prose with
   epistemic markers stripped or a marker-blind judge prompt, to bound how much
   of the rating-channel contraction is EMBER-style judge bias.
2. **Feature-mapped arms (from D1):** align our arm definitions with the
   "Assert, don't describe" feature set (asserted certainty, evaluative claims,
   moralized vocabulary) so the two results compose instead of talking past each
   other.
3. **Concession-without-conclusion control (from F):** if not already an arm,
   the human literature predicts it is the *weakest* form — a cheap ordering
   test of whether the persuasion analogy has real predictive power for SFT.
4. **Weasel-word scoring (from B5):** the Machine Bullshit lexicon gives an
   off-the-shelf hedging-density readout for tracking whether the hedged
   register itself amplifies, decays, or migrates across self-training rounds.

Caveat on retrieval: arXiv page fetches were blocked in this session, so entries
are built from search-result abstracts and secondary summaries; numbers quoted
(e.g., −1.86 weakener reward, −47.2pp judge drop, 7% certainty penalty) should be
spot-checked against the PDFs before being cited in a paper draft.

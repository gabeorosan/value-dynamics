# Literature review: what happens when the selector co-evolves with the selected

*Written 2026-07-28. Question posed: in our selection loop the judge has always been
frozen (the organism's own base model, or an oracle), and the predictive model treats
judge/value agreement `ρ` as a slowly-drifting exogenous parameter. One preliminary
duel-self-judging result has the judge co-evolving with the candidates, and six
seed-only-different runs split — early agreement went negative in the two that
collapsed and stayed nonnegative in the four that amplified. Nothing in the
frozen-judge model accounts for that. This review asks what theory does.*

*One correction to that framing before anything is built on it, derived in §9 item 10 from
the raw trajectories: the six-run separation is clean on **round 1 alone** (one negative
seed), not on the round-1-plus-2 window, where seed 43 has an agreement sum essentially
identical to a collapsing seed and does not collapse. And `σ` reaches exactly 0 by round 3
or 4 in all six runs, so late-round agreement values are degenerate. The phenomenon may well
be real; the current statement of it is looser than the ledger row reads.*

*Scope note on what is already in this repo, so nothing here re-launders a known
result: `docs/reports/report_population_genetics_unification.md` already establishes
that our per-round law is a breeder's equation (`R = h²S`, realized `h² ≈ 0.83`) with
`S = ρσ` the Price/breeder selection differential.
`docs/reports/lit_scan_2026-07-24_recent_papers.md` already covers Value Drifts
(2510.26707), Drift and selection in LLM text ecosystems (2604.08554), Survival is the
Only Reward (2601.12310), and the recursive-self-improvement survey (2607.07663).
`docs/reports/lit_review_selfjudge_selfreport.md` already covers Self-Rewarding LMs,
Meta-Rewarding, and the self-preference paper at the level needed for the
`em_selfaware` design. This review does not repeat those; it starts where they stop,
which is the moment the selector stops being a fixed parameter and becomes a second
state variable.*

*Four sibling documents landed the same day and are load-bearing here, so read the
overlaps there rather than trusting my compressions:
`docs/reports/lit_overoptimization_saturation_2026-07-28.md` covers Gao/Schulman/Hilton and
the Ferbach curation-replicator result far more thoroughly than §6.5 and §7.1 below;
`docs/reports/lit_iterated_learning_2026-07-28.md` covers cultural evolution and iterated
learning, overlapping my §5.4; and `docs/reports/report_agreement_drift.md` +
`experiments/agreement_drift.json` measured the frozen-versus-co-evolving judge drift
contrast on our own committed corpus on 2026-07-28 — I have folded its numbers into §6.1,
§8.1 and §9 rather than restating the whole analysis.*

---

## 0. The one-paragraph answer

There is no formal account anywhere of when a **self-judging LLM loop** bifurcates into
runaway versus collapse. There is, however, an exact and old formal account of when a
**two-trait co-evolutionary system with a selector that is itself under selection**
bifurcates — the Lande–Kirkpatrick model of Fisherian runaway — and it is written in
precisely the variables we already measure. Its condition is a comparison of two
slopes: the system runs away when the trajectory slope `G_tp/G_t` (how fast the
*preference* moves per unit of *trait* movement) exceeds the slope of the line of
equilibria. In our vocabulary `G_t` is spread `σ` times the transmission coefficient,
and `G_tp/G_t` is the **judge-drift coupling** `Δρ/Δv` — a quantity the frozen-judge
program cannot measure, because with a frozen judge it is zero by construction, and which
the same-day `report_agreement_drift.md` gets closest to without reaching (it measures drift
*magnitude*, and finds the matched frozen-versus-evolving contrast underpowered by more than
a factor of two, needing ~52 seeds per arm). Three
other literatures give the same structural answer in different clothes: performative
prediction (repeated retraining converges iff a loop-gain product is below 1), GAN
local-stability theory (converges iff the Jacobian spectrum is in the left half-plane,
and there are explicit counterexamples where it is not), and coevolutionary-algorithm
theory (the named failure is **disengagement**, which is exactly our `σ → 0`
self-consumption). Only one of these conditions has ever been implemented on an
actual LLM self-judging loop — CREAM's consistency gate, which measures the judge's
rank agreement with its own previous iteration and shuts the update off when it hits zero.
On the early-warning question: no paper anywhere plots a signed
judge-versus-ground-truth correlation per round and shows it crossing zero. The three
nearest things are (a) two-series divergence plots where judge score rises while true
quality falls, (b) a *discrimination* statistic (true-positive minus false-positive rate)
collapsing toward zero — 0.313 → 0.059 over five self-play iterations in
[arXiv:2607.05904](https://arxiv.org/abs/2607.05904) — and (c) CREAM's inter-iteration
Kendall's τ of the judge against **its own past self**, which does go negative
(−0.22 ± 0.41). Two measured facts deserve top billing as the strongest external support
for the co-evolving-judge worry: Meta-Rewarding's own Table 5 shows the judge's position
bias going **47.79% → 87.75% in a single self-training iteration**, and Vallinder & Hughes
report five seed-only-different LLM societies splitting 2-vs-3 with a **first-generation
scalar** cleanly separating the groups — our result with the names changed. The generic
critical-slowing-down indicators (rising variance, rising lag-1 autocorrelation, slowing
recovery from perturbation) have essentially **not** been applied to LLM training dynamics,
and the one preprint that tried to benchmark collapse-warning indicators under matched
false-positive control failed to find an acceptable operating point.

---

## 1. Self-rewarding and self-judging LLMs: what is actually measured

### 1.1 The base case, and the fact that almost nobody runs it long enough to see the dynamics

**Self-Rewarding Language Models**, Yuan et al., [arXiv:2401.10020](https://arxiv.org/abs/2401.10020).
Llama-2-70B, LLM-as-a-Judge prompting on its own generations, Iterative DPO,
**three iterations**. The abstract's claim is that both instruction-following and reward
quality improve: "*We show that during Iterative DPO training that not only does
instruction following ability improve, but also the ability to provide high-quality
rewards to itself.*" Three iterations is not enough rounds to see a bifurcation, and the
paper reports no per-iteration trajectory of judge quality against a fixed external
standard. This matters for us: the flagship self-judging result is a **two-to-three
round** result, the same horizon at which our own loops have not yet separated.

**Meta-Rewarding Language Models**, [arXiv:2407.19594](https://arxiv.org/abs/2407.19594)
is the follow-up whose existence is the admission: without a meta-judge that improves the
judging itself, the self-rewarding loop saturates.

### 1.2 The clearest measured degradation of a co-evolving selector

**R-Zero: Self-Evolving Reasoning LLM from Zero Data**,
[arXiv:2508.05004](https://arxiv.org/abs/2508.05004). A Challenger proposes problems and a
Solver solves them; the Challenger's reward is explicitly
`r_uncertainty(x;φ) = 1 − 2|p̂(x;S_φ) − 1/2|`, i.e. it is paid to drive the Solver to 50%
accuracy, and the Solver trains on majority-vote pseudo-labels of its own answers. This
is the cleanest published instance of a **selector that is rewarded for co-adapting to the
generator**, and the selector's quality is measured against ground truth per iteration.
Reading the ar5iv rendering of Table 5, self-generated label accuracy falls monotonically
across iterations for all three solver sizes: iteration 1 ≈ 70.6% (0.6B) / 69.4% (1.7B) /
71.0% (4B); iteration 2 ≈ 53.4 / 55.2 / 56.2; iteration 3 ≈ 50.8 / 52.2 / 48.8; iteration
4 ≈ 44.0 / 45.2 / 42.2. The paper's own text elsewhere quotes a drop "*to 63.0% by the
third iteration*" for a different slice. **Flag:** I read this table through ar5iv, not
the published PDF; the direction and rough magnitude are unambiguous but the exact cell
values should be re-checked before they go on a summary surface. The qualitative fact is
the important one: the co-evolving selector's agreement with ground truth **falls by
roughly a third over four rounds**, and by iteration 3 it is at chance for a binary-ish
task. That is a measured `ρ` trajectory heading toward zero, in someone else's loop.

### 1.3 The mechanism by which self-rewarding kills its own selection differential

**Temporal Self-Rewarding Language Models**,
[arXiv:2508.06026](https://arxiv.org/abs/2508.06026). Their diagnostic of vanilla
Self-Rewarding is that the chosen and rejected responses *converge on each other*: "*the
score gap between them shrinking by 9 times during the same period*", with rising
representational similarity. Their Theorem 1 bounds the DPO directional-guidance term by
the representation gap,
`‖∇_θ log π(y_w|x) − ∇_θ log π(y_l|x)‖ ≤ C · ‖h_w − h_l‖`,
so as `‖h_w − h_l‖ → 0` the DPO gradient vanishes and training collapses.

**This is our `σ → 0` in another notation, and it is the single most direct external
corroboration of an established repo result.** Our ledger already records
`σ: 0.40 → 0.14 → 0.00` across rounds in the Qwen self-only self-judge run, "*after which
the selection term is exactly 0*". Their "score gap shrinks 9×" is the same event measured
on the judge's own scale rather than on a value axis. Note carefully what this means
for the bifurcation question: **spread exhaustion is a collapse mode that does not require
`ρ` to change sign at all.** Any account of our six-seed split has to distinguish
`σ → 0` collapse from `ρ < 0` collapse, because the literature documents the first one
much more thoroughly than the second.

### 1.4 The shared-context result — the most directly relevant experimental control in the whole field

**Spontaneous Reward Hacking in Iterative Self-Refinement**,
[arXiv:2407.04549](https://arxiv.org/abs/2407.04549). Essay editing on 23 college
application essays, an author model and a judge model, **5 refinement iterations**
(trajectories of length 6), with 23 human annotators from Upwork scoring every essay on a
four-item rubric (Conventions, Depth, Details, Style). The judge's score climbs while the
human score plateaus or falls — "*iterative self-refinement leads to deviation between the
language model evaluator and human judgment*" — and GPT-3.5 hacks much harder than GPT-4:
"*in-context reward hacking manifests to a lesser extent with GPT-4 than GPT-3.5*".

The result that should shape our design is the **context-symmetry ablation**. When author
and judge share identical dialogue history, hacking is severe. When they are given
*different numbers of previous iterations*, "*the gap between the Online LLM Judge and
Human scores becomes statistically insignificant*". Symmetric contexts (both see 1, or
both see 3, previous iterations) trigger hacking; asymmetric contexts prevent it.

This is a **cheap, measurable, causal knob on the co-adaptation coupling**, and it is the
in-context analogue of what our loop does in weight space. It says the pathology is not
"the judge is the same model" per se — it is "the judge and the generator share the same
state". That is a testable prediction for us: a judge that co-evolves on a *different*
LoRA branch, or from a *lagged* checkpoint, should behave measurably differently from a
judge that is literally the current organism.

### 1.5 Self-preference, and why it is the natural sign-flip mechanism

**LLM Evaluators Recognize and Favor Their Own Generations**, Panickssery, Bowman & Feng,
[arXiv:2404.13076](https://arxiv.org/abs/2404.13076). Self-preference is *linearly
correlated with, and causally driven by, self-recognition ability*; fine-tuning to
increase self-recognition increases self-preference. Our repo already reads this paper
(`lit_review_selfjudge_selfreport.md` §2) for the "let-go" run.

The point worth adding here is dynamical rather than static. In a co-evolving loop, every
SFT round makes the organism's outputs *more* like the organism, hence more recognizable
to a judge that is the organism. If self-preference grows with self-recognition, then the
judge's ranking becomes progressively more driven by "is this mine" and progressively less
by "is this good on the value axis" — which is a mechanism for `ρ` to decay toward zero,
and, if the axis is one where the organism's own current output sits on the wrong side, to
cross into negative. **No paper I found measures self-preference as a time series across
self-training rounds.** That is an unoccupied and cheap experiment (see §8).

*Two citation-hygiene notes on this paper, because the repo already cites it.* First, the
headline "self-preference is linearly correlated with self-recognition" is the paper's own
abstract language but **the paper reports no coefficient** — the linear trend is a scatter
plot (Fig. 7 caption: "*Fine-tuning evaluators for self-recognition results across models
and datasets results in a linear trend connecting evaluator self-recognition to
self-preference*"), with no Pearson r, slope or R². Second, the one coefficient in the
paper — example-level Kendall's τ between recognition confidence and preference confidence
(Table 1) — is a *different* quantity and is explicitly reported as **flat**: "*this
correlation does not change meaningfully as self-recognition ability increases*" (for
Llama-2 it falls, 0.73 → 0.58). Concrete numbers that are solid: GPT-4 recognises its own
summaries at **73.5%** pairwise; fine-tuning on 500 pairwise examples takes GPT-3.5 and
Llama-2 to "**over 90% accuracy**" at self-recognition; and human annotators rate the
underlying quality gaps as much smaller than the models' self-preference (GPT-4 vs GPT-3.5
**57%**, GPT-4 vs Llama-2 **63%**, GPT-3.5 vs Llama-2 **58%** over 900 comparisons).

### 1.6 Judge pathologies measurably *amplify* under self-training

This is the strongest single piece of evidence in the review that a selector degrades when
it co-evolves, and it is hiding in a paper usually cited for something else.

**Meta-Rewarding Language Models**, Wu et al.,
[arXiv:2407.19594](https://arxiv.org/abs/2407.19594), Table 5 (caption: "*Meta-Judge
Statistics. We observe growing biases in the meta-judge towards preferring higher score
judgements or those in the first position.*"):

| meta-judge | prefers higher-score judgement | positional bias, same-score pairs |
|---|---:|---:|
| iteration 1 | 63.04% | 47.79% |
| iteration 2 | 97.68% | 87.75% |

50% is unbiased on both columns. **In a single iteration of self-training, the judge's
position bias goes from essentially unbiased (47.79%) to nearly deterministic (87.75%), and
its score-anchoring bias goes from 63% to 98%.** The paper's text: "*After the first
iteration of Meta-Rewarding training, the meta-judge becomes more likely to prefer a higher
score judgment nearly all the time… For the positional bias, we also see an increasing trend
during the training.*" And note this table is *post*-mitigation — they already apply
order-swapped double prompting with position-weighted wins,
`ω₁ = win₂ₙd/(win₁ₛₜ + win₂ₙd)`, and a length control that picks the shortest response in the
top score tier as chosen and the longest in lower tiers as rejected. The bias grows anyway.
It is n = 2 iterations on one model, so it is a single data point — but it is a *measured*
one, and it points the same way as our own duel-loop observation that the A/B order gap grew
0.32 → 0.45 (seed 71) and 0.34 → 0.55 (seed 72) across three rounds.

For the raw magnitude of position bias to calibrate against: Panickssery et al. report that
GPT-4, GPT-3.5 and Llama reverse their pairwise preference when the option order is reversed
at rates of **25%, 58% and 89%** respectively. The systematic study — Shi et al., "*Judging
the Judges*", [arXiv:2406.07791](https://arxiv.org/abs/2406.07791), >100k evaluation
instances across MTBench and DevBench — finds position consistency ranging 0.57–0.82 on
MTBench (GPT-4 best at 0.82 ± 0.15) and 0.23–0.92 on DevBench, and that position bias is
"strongly affected by the quality gap between solutions". That last clause matters for us:
**position bias grows as the candidate pool homogenises**, so position bias and `σ → 0` are
coupled, and a co-evolving judge in a collapsing pool gets hit by both at once.

On length: Singhal et al., "*A Long Way to Go: Investigating Length Correlations in RLHF*",
[arXiv:2310.03716](https://arxiv.org/abs/2310.03716), report within-batch reward–length
Pearson correlations of **0.72 (WebGPT), 0.67 (RLCD), 0.55 (Stack)**, and that on WebGPT only
**2.0%** of the PPO reward gain is attributable to non-length features — a purely
length-based reward nearly reproduces standard PPO (56% vs 58% simulated preference). Dubois
et al., [arXiv:2404.04475](https://arxiv.org/abs/2404.04475), show GPT-4 prompted to "answer
with as much detail as possible" scores **64.3%** on standard AlpacaEval but **51.6%**
length-controlled. Our own control-arm decomposition already found length dominating the
judge's within-organism sorting (length–severity +0.30, net-of-length sorting ≈ 0), so this
is the same disease in another lab's data.

### 1.7 Constitutional AI and RLAIF do not test this

**Constitutional AI**, [arXiv:2212.08073](https://arxiv.org/abs/2212.08073), and **RLAIF**,
[arXiv:2309.00267](https://arxiv.org/abs/2309.00267), are frequently invoked as evidence
that AI feedback loops are fine. Both use a **frozen feedback model**, and the
structural reason neither can speak to our question is that **neither runs more than one
feedback round**.

CAI has up to **four critique–revision steps** in the supervised stage (SL-CAI-1 …
SL-CAI-4) followed by a **single** RL phase — there is no regeneration of AI preference data
from the RL-trained model and no retraining on it. What it measures is a single-point
quality check: feedback-model binary accuracy on 438 HHH comparisons ("well over 90%" for
pretrained LMs, improved further by chain-of-thought), plus harmlessness/helpfulness Elo
from crowdworker comparisons and an ablation over the 16 constitutional principles. The one
degradation it documents is qualitative and unquantified: RL-CAI models "*can be
over-trained, resulting in Goodharting behavior whereby models can be overly harsh in
responding to harmful prompts, or may include boilerplate language*".

RLAIF likewise trains the reward model once on AI labels and runs RL once. Its
AI-labeler-alignment-with-humans figure of **78.0%** on summarization is a single point, not
a trajectory. (Headline win rates over SFT: summarization RLAIF 71% / RLHF 73%; helpful
dialogue 63% / 64%; harmless rate 88% / 76%.)

So both papers establish that AI feedback is *initially* good enough and then stop measuring
it. They are evidence about **one round of a frozen selector**, which is exactly the regime
our program already models well. **They are not evidence about the co-evolving case, and
should not be cited as such.**

### 1.8 The co-evolution-helps counterweight

Not all co-evolution results are collapse stories, and honesty requires the counterweight.
**SCOPE: Self-Play via Co-Evolving Policies for Open-Ended Tasks**,
[arXiv:2605.31433](https://arxiv.org/abs/2605.31433) reports that "*co-evolving the
Challenger is necessary to keep tasks near the Solver's frontier*" — a frozen challenger
stops helping after one iteration. **Multi-Agent Evolve**,
[arXiv:2510.23595](https://arxiv.org/abs/2510.23595), runs Proposer/Solver/Judge from one
base model with synchronized updates and quality filtering explicitly "to stabilize
self-evolution". **Who Grades the Grader?**,
[arXiv:2607.12790](https://arxiv.org/abs/2607.12790), co-evolves evaluation metrics and
skills for 100 rounds and reports monotone improvement in the selection objective
plateauing by round 63 — *but only because the metric is guarded*: their ablation shows
"removing anchor guards causes metric collapse (passes 94–100% of training data)", and
they document a caught Goodhart failure where the skills gamed a rubric's tag counter.

The pattern across these: **co-evolution is stabilizing when the selector is anchored to
something external and destabilizing when it is not.** Every successful system in this
list carries an anchor — a dev-set anchor, a verifier, an execution environment, a
constitution. That is the same conclusion the self-consuming-loop literature reaches from
the other direction (§3), and the same one the Fisherian model reaches (§4.3).

---

## 2. Co-evolutionary and self-play dynamics: what is actually proved

### 2.1 GAN training as the formal analogue — and what is genuinely proved

The generator–discriminator pair is the closest engineered analogue of generator–judge,
and it is the one place with real theorems.

- **Gradient descent GAN optimization is locally stable**, Nagarajan & Kolter,
  [arXiv:1706.04156](https://arxiv.org/abs/1706.04156). Equilibria of the traditional GAN
  gradient dynamics are locally asymptotically stable under conditions — but the same
  analysis shows "*the recently proposed Wasserstein GAN can have non-convergent limit
  cycles near equilibrium*". They add a regularizer that restores local stability for both.
- **Which Training Methods for GANs do actually Converge?**, Mescheder, Geiger & Nowozin,
  [arXiv:1801.04406](https://arxiv.org/abs/1801.04406). Absolute continuity of the data
  distribution is *necessary*: they exhibit a counterexample where unregularized GAN
  training does not converge. GANs with instance noise or zero-centered gradient penalties
  do converge; WGAN and WGAN-GP with a finite number of discriminator updates do not always
  converge.
- **GANs Trained by a Two Time-Scale Update Rule (TTUR)**, Heusel et al.,
  [arXiv:1706.08500](https://arxiv.org/abs/1706.08500). With separate learning rates for
  discriminator and generator, stochastic approximation gives convergence "*to a stationary
  local Nash equilibrium*" under mild assumptions.

Three things transfer. First, **the stability question is a spectral question about the
Jacobian of the joint update**, not a property of either player alone — and it can go
either way for the same architecture depending on parameters. Second, **the failure mode is
often a limit cycle, not divergence**: oscillation is a first-class regime that a
four-round experiment will read as noise. Third, **the fix that provably works is
regularization/damping or a timescale separation** — updating the selector on a slower
clock than the generator is a *theoretically motivated* intervention, not a hack.

### 2.2 Coevolutionary algorithms already named our failure modes

The evolutionary-computation literature spent the 1990s–2000s cataloguing exactly this,
under names our program should adopt because they are older and sharper than ad-hoc
coinages:

- **Disengagement**: one population so outperforms the other that every contest has the
  same outcome, the selection gradient vanishes, and the populations drift. This is `σ → 0`
  and `gap = 0`. The canonical treatment is Cartlidge & Bullock, "*Combating Coevolutionary
  Disengagement by Reducing Parasite Virulence*", **Evolutionary Computation** 12(2):193–222
  (2004), [DOI 10.1162/106365604773955148](https://doi.org/10.1162/106365604773955148) —
  their fix is to *reduce* the virulence of the selecting population so that it does not win
  every contest, which keeps a gradient alive. (I could not fetch the full text; the
  Southampton and MIT Press copies both returned 403. The definition and the virulence
  mechanism are corroborated across several secondary sources but I have not read the
  primary.)
- **Cycling / Red Queen dynamics**: the pair rediscovers the same solutions forever with no
  net progress. This is the discrete analogue of the GAN limit cycle.
- **Forgetting**: opponents defeated earlier become hard again.
- **Over-specialization / mediocre stable states**.

Watson & Pollack, "*Coevolutionary Dynamics in a Minimal Substrate*" (GECCO 2001) is the
standard demonstration that all of these arise in a system with essentially no structure —
i.e. they are properties of the coupling, not of the domain.

- **Open-ended Learning in Symmetric Zero-sum Games**, Balduzzi et al.,
  [arXiv:1901.08106](https://arxiv.org/abs/1901.08106), gives the cleanest modern framing:
  their Theorem 1 decomposes any functional-form game into a **transitive** component (real
  strength, where self-play makes progress) and a **cyclic** component (where "self-play
  cycles through agents without improving overall agent strength"). If a co-evolving judge
  and generator settle into a largely cyclic component, value trajectories will oscillate
  with no net movement, and the per-round `ρσ` law will keep fitting each individual round
  while the endpoint goes nowhere.

### 2.3 Self-play with a convergence guarantee, and why ours does not have one

**SPIN (Self-Play Fine-Tuning)**, [arXiv:2401.01335](https://arxiv.org/abs/2401.01335),
has a convergence guarantee — but read what it says: "*the global optimum to the training
objective function of our method is achieved only when the LLM policy aligns with the
target data distribution*". The fixed point is **defined by an external dataset**. SPIN's
self-play is a discriminator against a *fixed* human-written corpus. Remove the corpus and
the guarantee evaporates. This is the recurring structural fact: **every self-play method
with a stability theorem has an external anchor in the theorem's statement.**

### 2.4 Performative prediction: the cleanest loop-gain condition in machine learning

**Performative Prediction**, Perdomo, Zrnic, Mendler-Dünner & Hardt,
[arXiv:2002.06673](https://arxiv.org/abs/2002.06673) (ICML 2020). A model is deployed, the
deployment shifts the data distribution, you retrain on the shifted distribution, repeat.
Their Theorem 3.5 gives repeated risk minimization a contraction:
`‖G(θ) − G(θ′)‖₂ ≤ ε·(β/γ)·‖θ − θ′‖₂`,
so the loop converges to a performatively stable point iff

> **ε < γ / β**

where `ε` is the sensitivity of the distribution map (Wasserstein-Lipschitz constant: how
much deploying a different model moves the data), `β` is the smoothness and `γ` the strong
convexity of the loss. Convergence is linear:
`‖θ_t − θ_PS‖₂ ≤ δ` for `t ≥ (1 − εβ/γ)^{-1} log(‖θ_0 − θ_PS‖₂/δ)`. Strong convexity is
*necessary*; smooth-plus-tiny-`ε` is not enough.

This is the right shape for our question even though the assumptions do not literally hold
for LLM SFT. **The loop is stable iff the product of the feedback gains around the loop is
less than one.** In our loop there are two gains: how much the value moves per round given
a selector (`h² ≈ 0.83`, well measured) and how much the selector moves per unit of value
movement (`Δρ/Δv`, never measured). The condition to test is on their product.

The same shape appears in **Self-Correcting Self-Consuming Loops for Generative Model
Training**, [arXiv:2402.07087](https://arxiv.org/abs/2402.07087), whose Theorem 4.3 gives
an explicit contraction factor `ρ(λ)/(1+γ) = λ(α+εL) / {(1+γ)[α − λ(α+εL)]}`, where `γ ≥ 0`
is the strength of a correction operator that mixes the true distribution back into the
synthetic data: `π_γ p_θ(x) := [p_θ(x) + γ p_θ*(x)]/(1+γ)`. Any `γ > 0` strictly shrinks the
contraction factor. Again: **an external anchor enters the stability constant directly.**

---

## 3. Model collapse and self-consuming loops: the collapse half of the bifurcation

This literature is well covered in the repo's earlier scans; the three load-bearing points
for the co-evolving-judge question are:

1. **Shumailov et al., "AI models collapse when trained on recursively generated data"**,
   *Nature* 631, 755–759 (2024),
   [DOI 10.1038/s41586-024-07566-y](https://doi.org/10.1038/s41586-024-07566-y). Two
   phases: early collapse (tails of the distribution disappear, the model drifts) and late
   collapse (low-variance convergence far from the original). Fresh real data prevents it.
2. **Alemohammad et al., "Self-Consuming Generative Models Go MAD"**,
   [arXiv:2307.01850](https://arxiv.org/abs/2307.01850). Three loop types — fully
   synthetic, synthetic augmentation, fresh data — and the conclusion that without "*enough
   fresh real data in each generation*" either quality (precision) or diversity (recall)
   progressively decreases.
3. The RSI survey ([arXiv:2607.07663](https://arxiv.org/abs/2607.07663), covered in
   `lit_scan_2026-07-24_recent_papers.md`) states the sharpest version as a threshold: **if
   the externally grounded signal fraction vanishes asymptotically, degenerative dynamics
   follow.**

Note what these do *not* say. They are all about the **generator** consuming its own
output with a fixed or absent selector. None of them lets the selector evolve. The
distinctive feature of our question — a selector whose *preferences* are being reshaped by
the same data that reshapes the generator — is outside the scope of the entire model-collapse
literature.

---

## 4. Fisherian runaway: the best available formal model, and it fits our variables exactly

### 4.1 The model

Fisher's verbal argument was formalized by **Lande (1981)**, "Models of speciation by
sexual selection on polygenic traits", *PNAS* 78(6):3721–3725,
[DOI 10.1073/pnas.78.6.3721](https://doi.org/10.1073/pnas.78.6.3721), and **Kirkpatrick
(1982)**, "Sexual selection and the evolution of female choice", *Evolution* 36(1):1–12,
[DOI 10.1111/j.1558-5646.1982.tb05003.x](https://doi.org/10.1111/j.1558-5646.1982.tb05003.x).
The clearest compact statement I could obtain is the Annual Review by **Kuijper, Pen &
Weissing (2012)**, "A Guide to Sexual Selection Theory", *Annu. Rev. Ecol. Evol. Syst.*
43:287–311,
[DOI 10.1146/annurev-ecolsys-110411-160245](https://doi.org/10.1146/annurev-ecolsys-110411-160245),
from which the equations and the quoted condition below are taken verbatim.

Lande's quantitative-genetic system tracks the mean ornament `t̄` and the mean preference
`p̄`:

> `Δt̄ = ½ G_t β_t`
> `Δp̄ = ½ G_tp β_t`

where `β_t` is the total directional selection on the ornament (natural selection against,
sexual selection for), `G_t` is the additive genetic variance of the ornament, and `G_tp`
is the additive genetic covariance between trait and preference. Critically, **there is no
`β_p` term**: "*The system does not include a corresponding term for the preference, because
`β_p = 0` in the absence of direct costs and benefits of choosiness.*" The preference is not
selected directly; it moves **only** as a correlated response, dragged along by its
covariance with the trait.

The equilibria are the solutions of `β_t = 0` — a **line**, not a point. And the stability
condition, verbatim:

> "*Figure 2b shows when the line of equilibria is stable (which happens when the slope of
> the line of equilibria is larger than `G_tp/G_t`); if the covariance between trait and
> preference is very large, the line can also be unstable, leading to a never-ending
> runaway moving from the line with ever-increasing speed.*"

That is the whole thing. `G_tp/G_t` is the slope of the *trajectory* — how far the
preference moves per unit of trait movement. Compare it to the slope of the equilibrium
line. Trajectory shallower ⇒ the system returns to the line (stable, drifts neutrally along
it). Trajectory steeper ⇒ it peels away and accelerates (runaway). **A bifurcation
governed by a ratio of two measurable slopes.**

Kirkpatrick's discrete two-locus version has the same architecture: `Δt = ½t(1−t)A`,
`Δp = ½DA`, with `D` the linkage disequilibrium between trait and preference alleles, and
"*p changes only if D ≠ 0*". The system "*converges either to loss (t = 0) or fixation
(t = 1) of the ornament or to a line of internal equilibria (given by A = 0)*" — i.e. it is
explicitly **bistable with a separatrix**, which is the structure our six-run split looks
like.

### 4.2 The translation into our variables

The mapping is uncomfortably exact.

| Lande–Kirkpatrick | Our loop |
|---|---|
| ornament mean `t̄` | value `v_t` (0–1 held-out measurement) |
| preference mean `p̄` | judge's agreement with the value axis, `ρ_t` |
| additive genetic variance `G_t` | candidate spread `σ_t` (times the transmission coefficient) |
| directional selection `β_t` | selection intensity along the value axis |
| response `Δt̄ = ½ G_t β_t` | `Δv = h²·ρσ` with `h² ≈ 0.83` — **the same equation** |
| genetic covariance `G_tp` | co-evolution coupling: how much `ρ` moves per unit of value movement |
| trajectory slope `G_tp/G_t` | **`Δρ/Δv`** |
| "`β_p = 0`, preference not directly selected" | the judge is never trained on the value axis; it is trained on the same kept text as the generator |
| line of equilibria | the set of `(v, ρ)` where `ρσ = 0` — i.e. `ρ = 0` or `σ = 0` |
| runaway | our amplifying runs |
| loss/fixation of the ornament | our rails (0 or 1) |

The `β_p = 0` correspondence is the important one and it is not a stretch. Our judge is
never given a value-axis training signal. It changes because it is *the same weights* as
the generator, which is being SFT'd on kept text. That is precisely "the preference evolves
only as a correlated response".

Under this mapping the frozen-judge program is the special case `G_tp = 0`. Every result
the program has — the `ρσ` factorization, `h² ≈ 0.83`, the endpoint rollouts, the passed
forward forecast — is the **`G_tp = 0` slice** of a two-trait model. That is not a
criticism; it is the correct order of operations. But it means the frozen-judge corpus is
*structurally incapable* of exhibiting a bifurcation, and it explains cleanly why the
six-run duel split has no account in it.

**The predicted condition, stated in measurable quantities:** the loop is stable near the
zero-gap manifold when

> `|Δρ / Δv| < |slope of the ρ-nullcline in (v, ρ) space|`

and runs away when it exceeds it. Both sides are estimable from a loop that measures `ρ`
every round: the left side is a regression of round-to-round `ρ` change on round-to-round
value change; the right side is where `ρ` crosses zero as a function of `v`.

### 4.3 What the extended Fisherian literature adds, and each maps onto something we have already seen

The 30 years after Lande are largely about what breaks the runaway, and each result has a
direct loop analogue:

- **Costly choice kills runaway.** Pomiankowski (1987) and Bulmer (1989): with a direct
  cost on choosiness, "*the line of equilibria collapses to a single equilibrium point,
  coinciding with the naturally selected optima θ_t and θ_p*". Loop analogue: give the
  judge *any* direct anchor — a held-out calibration set, a constitution, an oracle
  spot-check — and the line of neutral equilibria becomes a point attractor. This is the
  formal version of "every stable self-play system in §2 has an external anchor".
- **Biased mutation and migration rescue it.** Pomiankowski, Iwasa & Nee (1991) show a
  mutation bias toward smaller ornaments restores an equilibrium away from the naturally
  selected optimum; Day (2000) shows the same for an influx of migrant males with smaller
  ornaments. **This is literally our base co-generator.** The repo's own result — removing
  the base co-generator *reverses* the Qwen forced-choice channel from erosion
  (0.341 → 0.006/0.007) to amplification (0.341 → 0.793/0.913), with round-1 `ρ` flipping
  from −0.28 to +0.40 — is a migration-bias result. An external supplier of material biased
  toward the safe end is exactly Day's influx of small-ornamented migrants, and it changes
  the sign of the co-evolutionary force rather than merely damping it.
- **Weak costs give limit cycles, not equilibria.** Iwasa & Pomiankowski (1995); Hall,
  Kirkpatrick & West (2000): when costs of choosiness and ornamentation are sufficiently
  weak, "*traits and preferences do not converge to equilibrium but oscillate forever on a
  limit cycle*". Loop analogue: **oscillation is the third regime**, alongside runaway and
  collapse, and a 3–4 round experiment cannot distinguish a limit cycle from noise. If we
  want to see it we need ≥8 rounds.

### 4.4 Has anyone imported Fisherian runaway into ML? Essentially no.

I looked specifically. The only import I found is an informal one: Ryan Kidd, "*Is
Fisherian Runaway Gradient Hacking?*"
([LessWrong](https://www.lesswrong.com/posts/eqNvpQst5TRLbxyTK/is-fisherian-runaway-gradient-hacking),
mirrored at [ryankidd.ai](https://ryankidd.ai/fisherian-runaway/)). It argues the analogy
between runaway ornamentation and mesa-optimizer proxy exploitation, offers three
alignment takeaways (roughly: the outer optimizer's pressure must exceed the mesa-optimizer's;
don't assume a dominant trait is purposeful; agentic search may not be necessary for
gradient-hacking-like phenomena), and **explicitly contains no formal model and no
measurable conditions** — it is an intuition pump. It also lists the disanalogies honestly
(no directed agency choosing the proxy; much higher noise in biological selection than in
SGD).

**So: the formal Lande–Kirkpatrick apparatus has not been applied to generator–judge
co-adaptation in machine learning.** That is the single largest open lane this review
found, and it is one we are unusually well positioned to take, because we already measure
`σ`, `ρ`, and the transmission coefficient — three of the four quantities the model needs.
The fourth, `G_tp/G_t = Δρ/Δv`, requires only that we stop freezing the judge and keep
measuring `ρ`.

---

## 5. Populations of LLM agents: measured attractors, basins, and bistability

### 5.1 The naming-game result

**Ashery, Aiello & Baronchelli, "Emergent social conventions and collective bias in LLM
populations"**, *Science Advances* 11(20) eadu9368 (2025),
[DOI 10.1126/sciadv.adu9368](https://doi.org/10.1126/sciadv.adu9368), preprint
[arXiv:2410.08948](https://arxiv.org/abs/2410.08948).

Setup: a classic naming game. Two agents drawn at random each emit a "name" from a shared
pool; matching names pay both +100, mismatching names pay both −50. Each agent sees only a
rolling window of its own last `H` interactions — **there is no global state and no agent
is told what the population is doing**. Defaults: name pool `W = 10` letters (also 2, 6,
26), population `N = 24` (also 48, 200), memory `H = 5` (also 3). Models: Llama-2-70b-Chat
(4-bit), Llama-3-70B-Instruct, Llama-3.1-70B-Instruct, Claude-3.5-Sonnet. Consensus is
reached by population round 15 in all cases except Llama-2-70b-Chat.

The headline: **a collective bias that no individual has.** With a two-name pool, agents
show no significant individual preference on a first interaction with empty memory
(χ² p-values 0.068 / 0.116 / 0.757 / 0.849 across the four models), yet over 40 runs per
model the population converges overwhelmingly on one of the two names:
Llama-3-70B 40/0, Llama-3.1-70B 40/0, Claude-3.5-Sonnet **26/14**, Llama-2-70b 36/4. The
microscopic origin is a memory-state-dependent asymmetry visible by interaction 3 —
e.g. p(M | one specific two-step history) = 0.848 versus p(Q | the mirror history) = 0.451.

Two things matter for us. First, **the Claude-3.5-Sonnet 26/14 split is exactly our
phenomenon**: runs identical except for the random seed landing in two different attractors,
and the authors describe it in basin language — "*the basin of attraction of the strong
convention is both larger and deeper than that of the weaker convention, as it attracts more
system configurations and makes it more difficult for the system to escape*". Second, the
committed-minority result gives a **critical mass**: the number of adversarial agents needed
to flip an established convention ranges from "*committed groups as small as 2%
(Llama-3-70B-Instruct) or as large as 67% (Llama-2-70b-Chat)*" — a two-order-of-magnitude
model dependence in the basin depth of an otherwise identical dynamical system.

**They report no early-warning quantity.** I looked; the nearest statement is a negative
one, that predicting the final consensus from initial memory configurations "would result
in an incorrect prediction".

**This result is contested.** Barrie & Törnberg,
[arXiv:2505.23796](https://arxiv.org/abs/2505.23796), argue the models "simply reproduce
conventions they already encountered during pre-training" and that the findings are
observationally equivalent to data leakage; Ashery et al. reply in
[arXiv:2506.18600](https://arxiv.org/abs/2506.18600). Cite the exchange, not just the paper.

A follow-up by the same group, **"Group size effects and collective misalignment in LLM
multi-agent systems"**, [arXiv:2510.22422](https://arxiv.org/abs/2510.22422), sweeps
`N = 1` to `~10⁴` and finds three regimes: fluctuation-dominated at small `N` (either name
can win), a bistable intermediate regime, and deterministic convergence on the strong name
above a model-dependent threshold `N_c` — with **no universal `N_c`** (N = 2 for one
model/word-pair, ~10⁴ for another). It also contains the most analytical treatment in this
corner of the field: a mean-field rate equation over *memory states*,
`dx_k/dt = −x_k + Σ_i Σ_j x_i x_j P_k(i,j)`, with an explicit reduced Jacobian
`J^red_ij = −δ_ij + 2[T_i(j,n) − T_i(n,n)]` and stability read off the largest eigenvalue.
Structurally that is a replicator-like quadratic flow, but it is over memory
configurations, not strategy frequencies, and it is not called a replicator equation.

### 5.2 The best measured early-warning signal in this literature — and it is the same shape as ours

**Vallinder & Hughes, "Cultural Evolution of Cooperation among LLM Agents"**,
[arXiv:2412.10270](https://arxiv.org/abs/2412.10270) (AAMAS 2025). An iterated Donor Game:
endowment 10, donation multiplier 2, 12 rounds per generation, 12 agents per generation,
10 generations, top 50% by resources survive and seed the next generation. Claude 3.5
Sonnet, Gemini 1.5 Flash, GPT-4o; 5 runs each.

The abstract already flags the phenomenon: "*For each model class, we also observe variation
in emergent behavior across random seeds, suggesting an understudied sensitive dependence
on initial conditions.*" But the body has the result that matters most to this review:

> "*Indeed, for the two runs where Claude failed to generate cooperation (rose and green in
> Figure 4(a)), the average donation in the first generation was 44% and 47%, whereas for
> the three runs where Claude succeeded at generating cooperation, the average donation in
> the first generation was 50%, 53% and 54% respectively.*"

and

> "*there appears to be some sensitive dependence on the initial conditions of which
> strategies were sampled in the first generation. We hypothesise that there is some
> threshold for initial cooperation below which an LLM agent society is doomed to mutual
> defection.*"

**Read this carefully, because it is our result with the names changed.** Five
seed-only-different runs; two collapse and three don't; a **first-round scalar** separates
the two groups with no overlap; and the authors hypothesise a threshold/separatrix. Our
version is six runs, two collapse and four don't, and the first-round scalar is the sign of
`ρ`.

This cuts both ways and both ways are important. It is **independent structural
corroboration** that "a round-1 measurement predicts which basin an LLM selection loop lands
in" is a real kind of fact and not an artifact of our chassis. It is also a **caution**:
their split is 2-vs-3 with a 3-point gap between the groups and no significance test, which
is precisely the kind of claim our program has already been burned by. If we cite them as
support we must cite the n alongside.

### 5.3 Attractors in model–model conversation

**Ko & Geiping, "Attractor States Emerge in Multi-Turn LLM Conversations"**,
[arXiv:2606.30571](https://arxiv.org/abs/2606.30571). Since the brief asked for precision
about what this measures:

- **Design.** 7 LLMs (including GPT-4o-mini, Claude Haiku, Gemini 2.5 Flash, GPT-4.1 nano),
  20 controversial topics, **20-turn dyadic debates**, two conditions: *self-play* (a model
  debating a copy of itself) and *mixed-play* (two different models). One agent is assigned
  Supporter, the other Opposer, each initialised with pro/con reference statements.
- **What is measured.** (i) *Representation space*: responses embedded with 384-dimensional
  SBERT vectors, topic-centred to remove topic offsets, then projected onto principal
  components computed from the topic-centred **self-play** embeddings only. (ii) *Discourse
  traits*: eight traits (including meta-commentary, flattery, rationality, agreement) scored
  by a GPT judge; "trait transfer" is the mixed-play minus self-play difference in means.
  (iii) *Stance*: a Likert self-report questionnaire administered after each turn, with
  subjective and objective variants.
- **What "attractor" means operationally.** Self-play endpoints form "bounded endpoint
  regimes that repeatedly arise under a given model's self-play dynamics", quantified by a
  **basin separation score** comparing within-model endpoint spread to the distance to the
  nearest competing model's basin.
- **Key numbers.** All basin nearest-rival margins satisfy `S_basin > 1`, ranging **1.50 to
  4.08** — the basins are separated. Mixed-play contracts the gap between partners by a mean
  **23.6% across 17 pairs**, i.e. partial convergence that does not erase model identity. The
  asymmetry is captured by a partnerward-pull coefficient `α`: **Claude Haiku α = 0.266**
  (the strongest attractor, pulled least) versus **GPT-4.1 nano α = 0.665** (most malleable).

**What it is not.** It is an *inference-time* result: no weights change, the "attractor" is
in conversation trajectory space, and there is no training loop, no selection, and no
bifurcation analysis. It is evidence that model-specific basins exist and that influence
between models is structured and asymmetric — useful as a prior for cross-family judge
experiments, and useful because `α` is a clean, portable measure of "how much does A move
toward B", which is close to what we need for `Δρ/Δv`. It is not evidence about
co-evolving-judge training dynamics.

### 5.4 The transmission-chain template worth stealing

**Perez et al., "When LLMs Play the Telephone Game: Cumulative Changes and Attractors in
Iterated Cultural Transmissions"**, [arXiv:2407.04503](https://arxiv.org/abs/2407.04503)
(ICLR 2025). 6 models × 3 tasks × 20 initial texts × 5 seeds = **1,800 chains of 50
generations each**, tracking toxicity, positivity, difficulty and length.

The methodological contribution we should copy: **attractors are operationalised by a
one-line regression.** Fit `property(final) = I + s·property(initial)` across chains; the
recurrence converges when `|s| < 1`, with **attractor position = I/(1−s)** and **attractor
strength = 1−s**. That gives a scalar attractor position and a scalar pull strength from an
initial-condition sweep, with no need to run to convergence. Findings: toxicity has the
strongest attractors, length the weakest; open-ended instructions ("continue") produce
stronger attraction than constrained ones ("rephrase"); larger models show weaker
attractors.

For us this is directly portable: **sweep the starting value `v_0` across runs and regress
final value on initial value.** `s > 1` is a bifurcation signature (divergence away from a
separatrix); `s < 1` with a single fitted `I/(1−s)` is a single attractor; a poor fit with
bimodal residuals is bistability. This is a far more powerful use of a fixed compute budget
than running many seeds at one starting point, because it puts the runs where they are
informative — along the axis the separatrix is supposed to cross.

### 5.5 Other measured seed-selected outcomes

- **Willis et al., "Will Systems of LLM Agents Cooperate: An Investigation into a Social
  Dilemma"**, [arXiv:2501.16173](https://arxiv.org/abs/2501.16173) (AAMAS 2025). LLMs
  generate complete iterated-prisoner's-dilemma *strategies*, which then compete under a
  **Moran process** (not replicator dynamics): "a player is chosen to be cloned
  proportionally to their fitness; they replace a uniformly randomly selected player",
  population 12, run to fixation, 100 Moran processes per LLM-prompt combination. From a
  balanced 4:4:4 aggressive/cooperative/neutral start: GPT-4o fixates aggressive 14–19%,
  cooperative 38–53%, neutral 33–49%; Claude 3.5 Sonnet aggressive 4–16%, cooperative
  42–51%, neutral 33–47%. A biased 8:2:2 aggressive start substantially raises aggressive
  fixation — i.e. **initial composition selects the attractor**, the same structure again.
- **Payne & Alloui-Cros, "Strategic Intelligence in Large Language Models: Evidence from
  Evolutionary Game Theory"**, [arXiv:2507.02618](https://arxiv.org/abs/2507.02618). Often
  described in secondary sources as using replicator dynamics; it does not — the update is a
  squared-fitness discrete map `N_{i,t+1}' = N_{i,t}·(F_{i,t}/F̄_t)²`, with the authors
  stating they "square this relative fitness term to amplify selection pressure". At a 75%
  per-round termination probability Gemini ends holding 16 of 24 agents with a **2.2%**
  cooperation rate while OpenAI models stay at **95.7%** cooperation; at 10% termination the
  rates are 85.2% / 87.6% / 95.8% (Gemini / OpenAI / Anthropic).
- **"Information Limits and Attractor Dynamics in Economies of Frontier LLM Agents"**,
  [arXiv:2607.06001](https://arxiv.org/abs/2607.06001), a pre-registered 3×3 grid with 8
  seeds per cell, reports the sharpest seed-selects-corner statement I found: at one boundary
  cell "*the eight per-seed residuals are [10.0, 13.0, 13.0, 12.0, 14.6, 0.3, 10.0, 12.0] —
  seven seeds at the reward corner, one seed in near-perfect alignment, under an identical
  condition*", and describes the response across the dominance boundary as a step function
  rather than a smooth crossover. Single-author July 2026 preprint, pre-registered but
  unreplicated — treat as suggestive.

### 5.6 The gap

**Correction to a claim I had written here before checking the repo's other same-day
reviews.** It is *not* true that nobody writes down a replicator equation for an LLM
selection loop. **Ferbach, Bertrand, Bose & Gidel, "Self-Consuming Generative Models with
Curated Data Provably Optimize Human Preferences"**,
[arXiv:2407.09499](https://arxiv.org/abs/2407.09499) (NeurIPS 2024), derive exactly that for
a keep-the-best-of-`K` curation loop — their Lemma 2.1 gives the discrete replicator equation
in the `K → ∞` limit, `p_{t+1}(x) → p_t(x)e^{r(x)}/E_{p_t}[e^r]`. It is covered properly in
`docs/reports/lit_overoptimization_saturation_2026-07-28.md` §5.1, and it is already cited in
our ledger. See §6.5 here for what it does and does not settle.

The accurate version of the gap is narrower and still holds: **nobody writes down a
replicator or replicator–mutator equation for a population of *interacting* LLM agents and
derives stability conditions from it**, and **nobody writes a Price-equation decomposition of
an LLM selection loop with measured covariance and transmission terms.** The closest
analytical object for the multi-agent case is the memory-state mean-field equation with
Jacobian in [arXiv:2510.22422](https://arxiv.org/abs/2510.22422). Steven Frank's
[arXiv:2507.18549](https://arxiv.org/abs/2507.18549) derives a general Price-equation
"force–metric–bias law" (`Δθ = Mf + b + ξ`) unifying natural selection, Bayesian updating,
Newton's method and SGD, but has no LLM application. Our
`report_population_genetics_unification.md` is, as far as this review can establish, ahead
of the published literature on this specific point — with the caveat that being first is
not the same as being right, and the near-tautology caveat recorded in that report still
applies.

---

## 6. Deliverable 1: the best available formal account, as conditions on measurable quantities

There is no published theory of when a self-judging LLM loop bifurcates. There are four
formalisms that each give a condition of the right shape, and they agree with each other
structurally: **a loop is stable when the product of the gains around it is below a
threshold, and the threshold is set by whatever external anchor is present.** Ranked by how
close they are to being usable on our data:

### 6.1 The Fisherian condition — closest fit, needs one unmeasured quantity

From Lande (1981) via Kuijper/Pen/Weissing (§4):

> **stable iff `G_tp/G_t` < slope of the line of equilibria; runaway otherwise.**

Translated: `G_t` is our spread `σ` (times the transmission coefficient `h² ≈ 0.83`), and
`G_tp/G_t` is the **judge-drift coupling `Δρ/Δv`** — how much the judge's agreement with the
value axis moves per unit of value movement. The equilibrium line is `ρσ = 0`, so its slope
in `(v, ρ)` space is `dρ*/dv` along the `ρ = 0` locus. Written out:

> **runaway when `|Δρ/Δv| > |dρ*/dv|`**, i.e. when the judge's preference chases the value
> faster than the zero-agreement manifold moves.

Every term is measurable in a loop that re-scores a frozen candidate pool each round. Three
of the four we already measure; `Δρ/Δv` is exactly zero by construction under a frozen judge,
which is why the existing corpus cannot exhibit this bifurcation.

**What the same-day `report_agreement_drift.md` already establishes, and what it leaves
open.** That analysis measured agreement *drift magnitude* on the committed corpus (70 runs
with at least two scored rounds), and found co-evolving judges drift 68% further than frozen
ones pooled (mean |drift| 0.463 versus 0.275, permutation p = 0.018), with a level effect in
round-one agreement (self-judges 0.258 versus frozen 0.060, p = 0.034) that it correctly
attributes to self-preference rather than to co-evolution. But **the matched ablation — Qwen
self-only reference-anchored pools, judged by self versus by a frozen copy of the same
organism — cannot resolve it**: 4 evolving runs against 10 frozen, observed difference 0.162,
minimum detectable difference at 80% power **0.378**, and roughly **52 seeds per arm** needed
to reach 80% power on an effect that size. It is recorded as underpowered, not as a null.

Two consequences. First, `Δρ/Δv` is still unmeasured — drift *magnitude* is not the same as
drift *coupled to value movement*, and it is the coupling that Lande's condition is about.
Second, and more usefully, that power calculation is a gift to the design in §8: **a
seed-counting contrast on this quantity is infeasible on our hardware**, which is the
strongest available argument for measuring a slope instead.

**Directional prediction it makes that nothing else does:** the *sign* of `G_tp` decides
whether runaway goes up or down, and the runaway is symmetric — Lande's model produces "rapid
exaggeration **or diminution**". So a co-evolving judge should produce *both* amplification
and collapse from the same mechanism, with the branch chosen by the sign of the coupling and
the starting side of the separatrix. That is the shape of our six-run split.

### 6.2 The performative-prediction condition — the cleanest loop-gain statement

From Perdomo et al. (§2.4): repeated retraining contracts iff **`ε < γ/β`**, `ε` the
sensitivity of the distribution map, `β/γ` the optimizer's condition number. In our loop the
two gains are `h²` (value response per unit selection differential — measured at ≈ 0.83,
tightly, across 340 rounds) and the judge's response to the same training data. The
condition to test is on their **product**, and the practical form is: estimate the round-to-
round Jacobian of `(v, ρ)` and check whether its spectral radius exceeds 1.

Same shape in **Self-Correcting Self-Consuming Loops**
([arXiv:2402.07087](https://arxiv.org/abs/2402.07087)), whose contraction factor
`ρ(λ)/(1+γ) = λ(α+εL) / {(1+γ)[α − λ(α+εL)]}` has the anchor strength `γ` sitting in the
denominator: any `γ > 0` strictly shrinks it. **The anchor is not a heuristic; it appears in
the stability constant.**

### 6.3 The one condition anybody has actually implemented on an LLM self-judging loop

**CREAM — "Consistency Regularized Self-Rewarding Language Models"**, Wang et al.,
[arXiv:2410.12735](https://arxiv.org/abs/2410.12735) (ICLR 2025). This is the closest thing
in the LLM literature to a stability condition stated on a measurable quantity, and it is
worth stating in full because we should probably just adopt the measurement.

Define the consistency rate over prompts `j`:
`𝒞 = |𝒟_U|⁻¹ Σⱼ (τⱼ + 1)/2`, where `τⱼ` is **Kendall's τ between the current iteration's
ranking of the candidates for prompt j and the previous iteration's ranking of the same
candidates**. Then gate the update on it:

> `ℒ(θ) = 𝒞 · ℒ_DPO(π_θ, 𝒟_DPO) + (1 − 𝒞) · ℒ_DPO(π_θ, 𝒟_RDPO)`

where `𝒟_RDPO` has the preference labels reversed. At `𝒞 = 0.5` — i.e. `τ = 0`, the judge
uncorrelated with its own past self — the two terms cancel and **the update is null**; below
that the reversed term dominates and the loop actively backs out. The measured quantity gates
the learning rate on the self-generated signal.

And the number that matters most for our question: **for standard Self-Rewarding on Llama-3,
the inter-iteration Kendall's τ is reported as −0.22 ± 0.41**, versus **+0.46 ± 0.35** for
CREAM (their Table 2). Per-iteration accuracy for vanilla Self-Rewarding on Llama-2 7B
degrades across three iterations (ARC-Easy 60.44 → 58.67 → 46.55; ARC-Challenge 48.46 →
46.67 → 34.47; OpenBookQA 63.20 → 59.80 → 49.20), while CREAM rises (60.44 → 58.97 → 62.08).

**Two warnings before this goes anywhere near a summary surface.** (1) That −0.22 is
**judge-versus-its-own-past-self**, not judge-versus-ground-truth. It is *not* our `ρ`, and
conflating the two would be exactly the error the ledger exists to prevent. (2) The standard
deviation (±0.41) is nearly twice the magnitude, so it is a weak negative, not a clean sign
flip. What it does establish is that **an inter-iteration agreement statistic can and does go
negative in a self-rewarding loop**, and that gating on it is enough to prevent the
degradation — which is a strong prior for our `ρ`-sign story and a ready-made intervention arm.

A parallel self-consistency condition, without an external anchor, is **SCIR**
([arXiv:2502.08922](https://arxiv.org/abs/2502.08922)), which enforces agreement between two
*internal* reward heads (the generative LLM-as-judge and the implicit DPO reward) via a
confidence-gated symmetric KL plus entropy term. Mistral-7B length-controlled win rate over
three iterations: SCIR 14.51 / 18.49 / 24.92 versus baseline Self-Rewarding 12.58 / 11.37 /
10.74 — i.e. the baseline **declines monotonically** while the consistency-regularised version
climbs.

### 6.4 The structural condition: independence between judge and generator state

The strongest *causal* isolation in the literature is the context-symmetry result of
[arXiv:2407.04549](https://arxiv.org/abs/2407.04549) (§1.4), and it is worth restating as a
condition because it is not about model identity at all:

> **Hacking occurs when the judge and the generator share state; it does not when they do
> not — even when the judge sees strictly more context.**

Their offline judge — same model, same prompt, but no shared dialogue history and no
influence on generation — tracks human scores closely. So the pathology is caused by the
*loop*, not by using an LLM as a judge. The 2026 preprint **"More Convincing, Not More
Correct: Self-Play Reward Hacking of Reference-Free LLM Judges"**
([arXiv:2607.05904](https://arxiv.org/abs/2607.05904)) turns the same idea into a training
intervention it calls commit-first de-anchoring — "*require the judge to commit an answer of
its own before it may use the candidate*" — reporting judge false-positive rate falling
**0.719 → 0.012**, blind-solving discrimination at **0.96**, and zero false positives when
used as the training reward, "*preventing the basin rather than only detecting it*". Single-
author July 2026 preprint; treat the numbers as unverified, but the structural condition is
the same one the peer-reviewed 2407.04549 established causally.

### 6.5 The frozen-selector case is already solved — which sharpens what is open

Before claiming novelty for the co-evolving case it is worth being precise about how much of
the **frozen**-selector case is already settled, because it is more than I expected.
**Ferbach, Bertrand, Bose & Gidel**, [arXiv:2407.09499](https://arxiv.org/abs/2407.09499)
(NeurIPS 2024), analyse exactly our operator — draw `K` samples, keep the reward-preferred
one, refit by maximum likelihood — and prove three things that map onto our results
one-for-one (full treatment in
`docs/reports/lit_overoptimization_saturation_2026-07-28.md` §5.1):

- **Lemma 2.1**: as `K → ∞` the update is the **discrete replicator equation**,
  `p_{t+1}(x) → p_t(x)e^{r(x)}/E_{p_t}[e^r]`, so `t` rounds of curation equal RLHF with
  regularisation `β = 1/t` from the initial distribution.
- **Lemma 2.2** is the breeder's equation:
  `E_{p_{t+1}}[e^r] ≥ E_{p_t}[e^r] + ((K−1)/K)·Var_{p_t}[e^r]/e^{r*}` — "*the expected reward
  increases proportionally to its variance at each retraining iteration*", and since the
  variance goes to zero the process must stall. **This is our `σ` term, with a proof that it
  self-extinguishes.**
- **Theorem 2.1** names the stalling point: the loop converges to the initial distribution
  restricted to "*the highest level set of the reward reached at initialization*". Theorems
  2.2–2.4: with a positive fraction of real data the loop is stable and the KL to the initial
  distribution stays bounded.

So for a **frozen** reward there is a replicator equation, a variance-driven response law, an
explicit ceiling, and a proved stabilising role for real data. That is a much stronger prior
art position than the co-evolving case, and it means our contribution cannot be "curation
loops are replicator dynamics" — that is Ferbach's. What Ferbach assumes throughout is that
`r` is **fixed**. Every one of those theorems is a statement about a constant reward
function. **The entire co-evolving question is what happens when `r` is itself updated on the
same data**, and none of the three results survives that unchanged — Lemma 2.2's variance
argument in particular assumes the reward against which variance is measured does not move.

### 6.6 The honest summary

No formal account of self-judging bifurcation exists. The best available statement, if we
want one, is ours to make: **the frozen-judge program has established the one-trait breeder's
equation `Δv = h²ρσ` with `h² ≈ 0.83`; adding the judge as a second state variable makes it a
two-trait Lande system, whose bifurcation condition is a comparison of the coupling slope
`Δρ/Δv` against the slope of the `ρ = 0` manifold.** Every ingredient except `Δρ/Δv` is
already measured. That is a paper-shaped gap, and §8 is the experiment that fills it.

---

## 7. Deliverable 2: is a negative agreement sign a known early-warning signal?

### 7.1 The direct answer: no, not under that name — but there is a very close cousin

I searched for this specifically, in several vocabularies (judge–ground-truth correlation as
a time series; evaluator–generator co-adaptation; reward-model drift under self-training;
"self-rewarding collapse"; "anti-correlated judge ground truth rounds"; early-warning
indicators for RL/RLHF collapse). **No paper plots a signed judge–ground-truth correlation
per round and shows it crossing zero, and no paper uses such a sign as a leading indicator
of a subsequent collapse.** What exists instead falls into three buckets:

**(i) Two-series divergence plots** — the judge's score and the ground-truth score are shown
diverging, with no correlation computed. This is
[arXiv:2407.04549](https://arxiv.org/abs/2407.04549) (§1.4), whose GPT-3.5 curves literally
move in opposite directions in the late iterations: "*the ONLINE LLM JUDGE scores the
model-edited essays much higher compared to the ground-truth HUMAN scores… the HUMAN scores
demonstrate a decrease in quality in the last iteration of essays, whereas the ONLINE LLM
JUDGE scores continue to plateau*". It is also
[arXiv:2606.28438](https://arxiv.org/abs/2606.28438) ("*When AI Reviews Its Own Code*"), which
runs 5 recursive rounds on four code models and describes a "*rubber-stamp regime where
acceptance scores rise while benchmark correctness falls*" — perplexity-gate pass rate
0.167 → 0.235 while HumanEval+ pass@1 falls 0.079 → 0.061.

**(ii) A discrimination statistic collapsing toward zero.**
[arXiv:2607.05904](https://arxiv.org/abs/2607.05904) is the closest published thing to a `ρ`
trajectory in a self-judging loop: GSM8K, Qwen3 policies 1.7B–14B, DPO self-play against a
reference-free judge, with a **hidden anchor** (a held-out exact-match check the judge never
sees and that is never used in training). Judge pass rate climbs **0.716 → 0.938 ± 0.016**
while anchor accuracy is flat at **0.209 → 0.202 ± 0.005**; false-positive rate on wrong
answers goes 0.65 → 0.89; and the judge's **discrimination, TPR − FPR, collapses 0.313 →
0.059** at 1.7B (8B: 0.360 → 0.102; 14B: 0.377 → 0.165). It approaches zero. **It is not
reported as going negative**, and no correlation coefficient is reported. Single-author July
2026 preprint — unverified, but the design (hidden anchor, per-iteration audit) is exactly
the design our Arm B needs.

**(iii) An inter-iteration agreement statistic that does go negative** — CREAM's
τ = −0.22 ± 0.41 (§6.3). Judge versus its own past self, not judge versus truth.

Beyond those three buckets: 

- **The reward-overoptimization literature measures the same event in a different
  parameterisation.** Gao, Schulman & Hilton, "Scaling Laws for Reward Model
  Overoptimization", [arXiv:2210.10760](https://arxiv.org/abs/2210.10760) (ICML 2023), fit
  gold reward against `d = √KL(π‖π_init)` with
  `R_bon(d) = d(α_bon − β_bon d)` for best-of-n and `R_RL(d) = d(α_RL − β_RL log d)` for RL;
  `α` and `β` scale smoothly (approximately logarithmically) with reward-model parameter
  count, with `α_RL` nearly independent of RM size. They report they were **unable to obtain
  a satisfactory fit** for the proxy reward with the same forms. The peak of `R_gold` is the
  point where **the local correlation between proxy improvement and true improvement changes
  sign** — which is, in our variables, exactly `ρ` crossing zero. So the object exists and
  has a fitted functional form; it has simply never been *named* as a sign, nor measured
  round-by-round in a self-judging loop, nor used as a leading indicator.
- **Moskovitz et al., "Confronting Reward Model Overoptimization with Constrained RLHF"**,
  [arXiv:2310.04373](https://arxiv.org/abs/2310.04373), formalises the per-reward-model
  "proxy point" — "*past a certain point, accumulating higher reward is associated with worse
  human ratings*" — and learns Lagrange multipliers to keep each reward model inside the
  range where it is still an effective proxy. It is a *stopping/constraint* mechanism, not a
  predictor.
- **Skalse et al., "Goodhart's Law in Reinforcement Learning"**,
  [arXiv:2310.09144](https://arxiv.org/abs/2310.09144) (ICLR 2024), gives a geometric
  account of why Goodharting occurs in MDPs and a **provably safe early-stopping method**
  with regret bounds. The conditions are geometric (angle between proxy and true reward
  vectors relative to the occupancy-measure polytope) rather than statistics you read off a
  training run.
- **The closest empirical thing to our claim** is Vallinder & Hughes (§5.2): a *first-round
  scalar* separating the runs that collapse from the runs that don't, with the authors
  hypothesising a threshold. Different scalar, same claim shape, n = 5.

So: our "the sign of round-1/2 agreement predicts the basin" would, if it survives, be a
**new** statement — not a rediscovery. It should be pitched that way, and held to the
standard that implies. The precise novelty claim I would be willing to defend is narrow:
*a signed judge–value correlation, measured per round in a self-judging training loop, whose
early sign separates the runs that collapse from the runs that amplify.* Each half of that
exists separately in the literature; the conjunction does not.

### 7.2 Generic early-warning signals from dynamical systems

The canonical reference is **Scheffer et al., "Early-warning signals for critical
transitions"**, *Nature* 461, 53–59 (2009),
[DOI 10.1038/nature08227](https://doi.org/10.1038/nature08227). The mechanism is **critical
slowing down**: as a system approaches a fold/bifurcation the potential well flattens, the
dominant eigenvalue approaches zero from below, and the return time after a perturbation
diverges. In a noise-driven system this shows up as:

1. **rising lag-1 autocorrelation** of the state variable,
2. **rising variance**,
3. **rising skewness** (the system spends more time on the shallow side),
4. **flickering** between states,
5. **slowing recovery rate from an imposed perturbation** — the direct measurement rather
   than the indirect statistical proxy.

Indicator (5) is the strong one, and it has been experimentally validated in a living
system: **Veraart et al., "Recovery rates reflect distance to a tipping point in a living
system"**, *Nature* 481, 357–359 (2012),
[DOI 10.1038/nature10723](https://doi.org/10.1038/nature10723). A cyanobacterial population
driven toward a photo-inhibition tipping point by rising light: recovery from small
perturbations slows monotonically as the critical point approaches, and autocorrelation in
the ambient fluctuations rises alongside.

The standard caveats are real and directly relevant to us: these indicators fail when the
series is **too short, too noisy, or too non-stationary**, and when the transition is a
global bifurcation rather than a local one. A 4-round training run is *all three*. Rising
variance and rising autocorrelation estimated on 4 points are not statistics.

### 7.3 Have they been applied to training dynamics? Barely, and the one attempt to validate them failed

- I found **no** paper applying variance/autocorrelation critical-slowing-down indicators to
  LLM or RLHF training trajectories as a monitoring tool.
- **Training instability in deep learning follows low-dimensional dynamical principles**,
  [arXiv:2601.13160](https://arxiv.org/abs/2601.13160), is the nearest: it argues training
  stability is "a measurable and comparable dynamical property of learning systems", finds
  high final performance is frequently decoupled from stability, that controlled
  stochasticity buffers learning dynamics, and — most relevant — that "*deviations in
  low-dimensional latent meta-states systematically precede observable performance
  collapse*". It uses perturbation auditing of training trajectories. It does **not** name
  variance or autocorrelation indicators or give numerical thresholds.
- Practitioner-level RL folklore gets closest to a usable rule: reward **standard deviation**
  and policy **entropy** destabilise before mean reward degrades. Note that reward standard
  deviation is `σ` — so the folk indicator is "watch the spread", which is the variable our
  law already puts at the centre.
- **The one attempt to evaluate collapse-warning indicators properly did not succeed.**
  "Benchmarking Recursive-Collapse Warning Claims Under Matched False-Positive Control",
  [arXiv:2606.00329](https://arxiv.org/abs/2606.00329), pre-registers a locked
  equal-false-positive contract (FP ∈ [0.03, 0.07]) and tests a directional telemetry
  triple — **rising gain `G`, recursive persistence `p`, declining diversity `δ`** — on
  financial and recommender benchmarks. Result: "*neither standard comparators nor
  [the] pre-registered quantile detector achieved an accepted operating point*". The
  directional pattern held; no detector cleared the false-positive budget. The authors
  report the non-acceptance as the finding. (Single-author-style 2026 preprint promoting its
  own framework — I would not lean on its positive claims. But the negative result is exactly
  the right kind of discipline and it is the state of the art on this question, which tells
  you how immature the area is.)

**Bottom line for deliverable 2:** the generic early-warning apparatus is well founded in
ecology and climate, essentially untested on training dynamics, and structurally hostile to
4-round experiments. If we want an early-warning claim, the version with the best chance is
the **perturbation-recovery** one (Veraart), because it converts a statistical-power problem
into an experimental-design problem — you *impose* the perturbation instead of waiting for
noise to supply it, and you need one or two extra rounds rather than a long series.

---

## 8. Deliverable 3: a concrete co-evolving-judge design for our infrastructure

Constraints taken as given: free Kaggle 2×T4 at roughly 30 GPU-hours per week, ~$75 Modal
credits, models ≤ 8B, 6 candidates per prompt, 4–8 rounds. And the standing scar tissue:
we were badly burned by an n = 2 monotone-trend claim, so any design whose headline is
"k of n seeds did X" is dead on arrival.

### 8.1 The design principle: stop counting seeds, start measuring the slope

The `n = 2` burn is not an argument for more seeds. It is an argument for a **different
estimand**. Counting how many seeds collapse estimates a *probability* — the least
efficient thing you can estimate, because its standard error falls as `1/√n` and n is
GPU-hours. Every literature in this review that got a real answer measured a **slope or a
recovery rate** instead:

- Lande's condition is a comparison of two slopes (§4.1).
- The telephone-game paper gets attractor position *and* strength from one regression
  across initial conditions (§5.4).
- Veraart's tipping-point result is a recovery rate under imposed perturbation (§7.2).
- Ashery's basin depth is a critical mass under imposed invasion (§5.1).

All four are estimable with far fewer runs than a bimodality test, because each run
contributes a continuous measurement rather than one bit. For reference, a Hartigan dip
test for unimodality needs roughly **n ≥ 10 seeds to be usable and n ≥ 16 to be
comfortable** — which is the price of the bit-counting design, and it buys strictly less.

And the seed-counting route is not merely inefficient here, it is **out of budget**, which we
now know from our own data rather than from a rule of thumb. `report_agreement_drift.md`
(2026-07-28) computes that the matched frozen-versus-co-evolving judge contrast needs roughly
**52 seeds per arm** for 80% power on the observed effect (|drift| difference 0.162 against a
minimum detectable difference of 0.378 at n = 4 vs 10). At 6 candidates per prompt and 6
rounds on a 4B model, 104 runs is not a Kaggle program. **Any design whose estimand is "how
many seeds did X" is dead on arrival for this question, and that is now a measured fact about
our corpus rather than an aesthetic preference.**

### 8.2 The minimal design

**Three arms, one loop chassis, all on free Kaggle.**

**Arm A — the initial-condition sweep (the primary arm; this is the bifurcation test).**
One model family (Qwen3-4B, since the self-only self-judge amplification is already
established there), self-judging duels, 6 candidates per prompt, 6 rounds. Instead of `k`
seeds at one starting point, run **8 starting points spread across the value axis** —
organisms at doses giving `v_0` ≈ 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85 — with
**2 seeds each** (16 runs). Then fit, following the telephone-game recipe:

> `v_final = I + s·v_0`

- `|s| < 1` with a good fit ⇒ **a single attractor** at `I/(1−s)`; no bifurcation; the
  frozen-judge model with a drifting `ρ` is adequate.
- `s > 1` ⇒ **divergence away from a separatrix** at `v* = I/(1−s)`; that *is* the
  bifurcation, and its location is estimated, not just asserted.
- Poor linear fit with residuals clustering at both rails ⇒ bistability with a separatrix
  somewhere in the swept range; then locate it by bisection with a handful of extra runs.

This design distinguishes bifurcation from seed noise **without needing the seed
distribution to be bimodal**, because the signal is the sign of `s − 1`, estimated from 16
continuous measurements rather than 16 bits. With 2 seeds per point the within-point
variance also gives a free estimate of seed noise to compare `s` against.

**Arm B — the co-evolution coupling `Δρ/Δv` (the mechanism arm; this is the number the
whole review says we are missing).** Same chassis, but measure `ρ` every round **on a frozen
held-out pool**, not on the live pool. This is essential and is the one methodological trap
I want to flag hardest: if `ρ` is computed on the live pool, then as `σ` shrinks the
estimate of `ρ` becomes noise, and a `ρ` that "goes negative" may be nothing but a
small-denominator artifact of a collapsing pool. Bank a fixed set of, say, 200 candidates
spanning the value axis once, at round 0, and re-score that same frozen set with the
round-`t` judge every round. Then `ρ_t` is a property of the judge alone, comparable across
rounds and across runs, and `Δρ/Δv` is a clean regression.

Three judge conditions, matched otherwise: **frozen base judge** (the established control),
**live self-judge** (judge = current organism), **lagged self-judge** (judge = the organism
as of the previous round). The lagged arm is the timescale-separation intervention that GAN
theory motivates (TTUR, §2.1) and the in-context analogue of the asymmetric-context result
that killed reward hacking in [arXiv:2407.04549](https://arxiv.org/abs/2407.04549) (§1.4).
Prediction worth pre-registering: `|Δρ/Δv|` is ~0 for frozen, largest for live, intermediate
for lagged; and the runs that diverge in Arm A are those with the largest `|Δρ/Δv|`.

**Arm B′ — the cheap structural control, if there is budget for a fourth condition.** A
**blind / commit-first judge**: the judge writes its own answer to the prompt *before* seeing
the candidates, and only then ranks them. This is the intervention that
[arXiv:2407.04549](https://arxiv.org/abs/2407.04549) established causally (breaking state
symmetry removes the divergence) and that
[arXiv:2607.05904](https://arxiv.org/abs/2607.05904) turns into a training reward. It is a
prompt change, not a chassis change, so it costs one extra generation per prompt per round.
If `Δρ/Δv` is much smaller under the blind judge than the live self-judge, the mechanism is
state-sharing rather than model identity — which is a cleaner and more transferable claim
than "self-judging is bad".

**Arm C — the perturbation-recovery probe (the early-warning arm).** At rounds 2, 3 and 4
of a subset of Arm A runs, fork the run: inject a small, fixed-magnitude value perturbation
(a single SFT round on a small batch of deliberately off-value text, calibrated to move `v`
by about 0.05–0.10) and then run **two unperturbed rounds** and measure how much of the
perturbation is recovered. Critical slowing down predicts the **recovery fraction falls as
the run approaches its transition** (Veraart). This is the strongest early-warning
measurement available and it costs 2 extra rounds on a subset, not a longer series. It also
directly estimates the local eigenvalue that Lande's condition is about.

### 8.3 Instrument requirements, learned from the repo's own history

- **Graded, not binary, candidate scores.** The repo's own standing lesson is that 0/1
  scores pin spread to the pool mean and destroy value covariance. Use graded scores plus
  logprob reads.
- **Close the thinking block on any logprob judge**, or the judge returns a fixed answer and
  order/polarity averaging hides it as an exact 0.500 null.
- **Average both A/B orders.** The duel-loop run already documented position bias *growing*
  across rounds (mean order gap 0.32 → 0.45 and 0.34 → 0.55). In a co-evolving-judge study
  that growth is not a nuisance — it is a **result**, and possibly the mechanism: a judge
  whose ranking is increasingly driven by position is a judge whose `ρ` is being diluted
  toward zero. Log it as a primary outcome.
- **Log a self-preference time series.** In the mixed-pool arms, record the kept-share of
  own-versus-supplier candidates every round. §1.5 predicts it rises; nobody has measured it
  across rounds; it is free given the pools we already bank.
- **Watch `σ` as carefully as `ρ`.** The two collapse modes — disengagement (`σ → 0`, §2.2,
  §1.3) and sign flip (`ρ < 0`) — are different phenomena with different remedies, and our
  own Qwen self-only run shows `σ` hitting exactly 0 by round 3. Any bifurcation claim must
  say which one it is, and must show the `ρ` estimate is not a small-`σ` artifact (which is
  what the frozen re-scoring pool in Arm B is for).
- **Log two cheap companion statistics that the literature has already validated, because
  both are free given the frozen pool.** (1) **Inter-iteration Kendall's τ** on the frozen
  pool — the judge at round `t` versus the judge at round `t−1`, ranking the *same* 200
  candidates. This is CREAM's consistency rate (§6.3), it is the one quantity anyone has
  shown going negative in a self-rewarding loop, and unlike `ρ` it needs no value labels at
  all. (2) **Discrimination, TPR − FPR**, against a coarse binarisation of the value axis —
  [arXiv:2607.05904](https://arxiv.org/abs/2607.05904)'s statistic, which is far more robust
  than a correlation when the pool is homogenising, because it does not divide by a
  vanishing spread. Having all three (`ρ`, τ, TPR − FPR) means a collapse claim can be
  stated in whichever one is best conditioned, and disagreement among them is itself
  diagnostic.

### 8.4 Budget

Rough sizing against 30 Kaggle GPU-hours/week: Arm A is 16 runs × 6 rounds; Arm B adds a
frozen-pool re-scoring pass per round (inference only, cheap) and two extra judge conditions
on a subset; Arm C adds 2 rounds to maybe 6 runs. At 4B with LoRA and 6 candidates per
prompt this is a two-to-three week Kaggle program, no Modal spend required. Modal credits
are better held for the one thing Kaggle cannot do — an 8B cross-family replication of
whichever arm returns a signal.

### 8.5 What would make me abandon the bifurcation framing

Stated in advance, because that is the point:

- If Arm A returns `s` clearly below 1 with a good linear fit, there is no separatrix in the
  swept range and the six-run split was seed noise plus a rail.
- If Arm B returns `|Δρ/Δv| ≈ 0` in the live-self-judge condition, the judge is not
  co-evolving in the relevant sense and the Fisherian framing is inapplicable regardless of
  what the trajectories look like.
- If the negative early `ρ` in the collapsing runs turns out to be estimated on rounds where
  `σ` is already near zero, the observation is an artifact and should be withdrawn.

---

## 9. Deliverable 4: what pre-empts or refutes us

**Nothing pre-empts the core claim.** No paper found in this review measures a per-round
selection-response law for a value trait, and none tracks judge–value agreement as a time
series through a self-judging loop. The specific combination — a factorised selection
differential `ρσ`, a measured transmission coefficient, and a bifurcation governed by the
judge's own drift — is unoccupied.

What comes closest, and what each threatens:

1. **Vallinder & Hughes, [arXiv:2412.10270](https://arxiv.org/abs/2412.10270)** — the
   partial pre-emption of the *shape* of our claim (§5.2). Seed-only runs splitting, a
   first-round scalar separating the groups, an explicit threshold hypothesis. It does not
   pre-empt the content (their scalar is a donation rate, ours is a judge–value correlation;
   theirs is a multi-agent society, ours is a training loop), but it means we cannot present
   "round-1 measurement predicts the basin" as novel in form. It is also a warning: their
   split is 2-vs-3.
2. **R-Zero, [arXiv:2508.05004](https://arxiv.org/abs/2508.05004)** — the closest thing to a
   published `ρ` trajectory under a co-evolving selector, and it goes monotonically down
   rather than bifurcating. If a careful reading of their per-iteration numbers shows a
   smooth decay with no sign change, that is mild evidence for "the co-evolving judge decays"
   over "the co-evolving judge bifurcates".
3. **Temporal Self-Rewarding, [arXiv:2508.06026](https://arxiv.org/abs/2508.06026)** — the
   most serious *alternative explanation* for our six-run split. Their theorem says the
   self-rewarding loop dies because chosen and rejected converge (`σ → 0`, DPO gradient
   vanishes), with no sign change required. If our collapsing runs are runs where `σ`
   exhausted early, the negative `ρ` may be a consequence or a co-symptom rather than a
   cause. **This is the alternative hypothesis Arm B is designed to kill or confirm**, and it
   is currently the one I would bet on if forced.
4. **"More Convincing, Not More Correct",
   [arXiv:2607.05904](https://arxiv.org/abs/2607.05904)** — the nearest thing to a direct
   pre-emption of the *measurement*: a per-iteration audit of a co-evolving reference-free
   judge against a hidden anchor, with the judge's discrimination collapsing 0.313 → 0.059
   while its pass rate climbs 0.716 → 0.938 and true accuracy stays flat. If we are claiming
   "we measured the judge going bad round by round", this preprint got there first for a
   different statistic on a verifiable-answer task. What it does **not** have: a sign change,
   a bifurcation, seed-level basin structure, or a per-round selection-response law. It also
   predicts the pathology shrinks with capability (their VA-Gap ≤ 1 − EM bound; discrimination
   at 14B falls only 0.377 → 0.165 versus 0.313 → 0.059 at 1.7B), which is a testable
   competing prediction for our model-size ladder.
5. **CREAM, [arXiv:2410.12735](https://arxiv.org/abs/2410.12735)** — pre-empts the
   *intervention*. If our conclusion is "monitor an agreement statistic and back off when it
   goes negative", CREAM published that in 2024 with a working loss function. Our
   contribution would have to be the dynamics (why it goes negative, and what predicts the
   basin), not the remedy.
6. **Spontaneous Reward Hacking, [arXiv:2407.04549](https://arxiv.org/abs/2407.04549)** —
   partially pre-empts the *mechanism* claim: shared context between generator and evaluator
   causes the divergence, and breaking the symmetry fixes it. If our lagged-judge arm
   reproduces their asymmetry effect, we are confirming their result in weight space rather
   than discovering a new one — which is still worth doing, and should be framed that way.
7. **[arXiv:2606.00329](https://arxiv.org/abs/2606.00329)** — refutes over-confidence in any
   collapse-warning indicator. Nobody has yet produced a recursive-collapse early-warning
   detector that clears a matched false-positive budget. Our `ρ`-sign indicator will face
   that bar, and should be evaluated against it from the start (i.e. pre-register the
   false-positive rate on non-collapsing runs, not just the hit rate on collapsing ones).
8. **The repo's own negative result.** `report_trajectory_adjustment_bakeoff.md` already
   tested the naive co-evolution feedback rule `ρ_next ~ ρ + ρσ` and **rejected** it — it did
   not improve leave-one-condition-out prediction of next-round `ρ`. That is a frozen-judge
   corpus, so it does not settle the co-evolving case, but it does mean the simplest linear
   coupling is already known not to work, and Arm B should not assume linearity without
   checking.
9. **`report_runaway_decomposition.md`** already establishes that rising/repeated local
   alignment is **not** a unique runaway signature (settled seed 0 is a counterexample with
   `ρ` 0.12 → 0.40 → 0.46 and no runaway). Any claim that the sign or trend of `ρ` predicts
   the basin has to survive that counterexample, which was measured on our own data.
10. **Our own six runs contain a near-counterexample, which I found while pulling numbers for
    a figure and which is not stated in the ledger row.** In
    `experiments/ablation_unit_law.json` → `rho_trajectories`, the six `neutral_self` seeds
    have round-1 agreement −0.191 / +0.162 / +0.239 / +0.125 / +0.023 / +0.070 (seeds 41–46)
    and round-2 agreement −0.558 / +0.541 / −0.676 / +0.359 / −0.464 / +0.052. The two runs
    whose pool value declines are 41 (0.506 → 0.400) and 45 (0.544 → 0.336) — and their
    rounds-1-and-2 agreement sums are −0.749 and −0.441. But **seed 43's sum is −0.437,
    essentially identical to seed 45's, and seed 43 does not decline** (0.625 → 0.660). So on
    the two-round window the separation is not clean; it is clean only on round 1 alone,
    where seed 41 is the sole negative. Additionally `σ` reaches exactly 0 by round 3 or 4 in
    all six runs, so the late-round `ρ` values (including several exact ±1.0 and nulls) are
    degenerate and should not enter any statistic. **Before this claim is repeated anywhere,
    the exact window and the seed-43 case need to be stated with it.** This is precisely why
    Arm B re-scores a frozen pool: it decouples the `ρ` estimate from the collapsing live pool.
11. **`report_agreement_drift.md` (same day, our own corpus)** partially pre-empts the
    *measurement* of judge drift and — more importantly — constrains what we may claim.
    Co-evolving judges drift further pooled (0.463 vs 0.275, p = 0.018), but the matched
    ablation is underpowered by a factor of more than two and needs ~52 seeds per arm. It
    also shows round-one agreement **does not persist for any real judge** (frozen non-oracle
    judges: corr(ρ₁, ρ₂) = 0.354, corr(ρ₁, ρ₃) = 0.117), and that the apparent persistence in
    the corpus is carried almost entirely by score-oracle runs whose agreement is pinned by
    construction. Read together with this review: our endpoint forecast is **not** working
    because agreement persists, so a bifurcation story built on "early agreement determines
    the trajectory" has to explain why round-one agreement predicts the endpoint while not
    predicting round three.
12. **Ferbach et al., [arXiv:2407.09499](https://arxiv.org/abs/2407.09499)** (§6.5) pre-empts
    the frozen-selector theory outright — replicator equation, variance-driven response,
    explicit ceiling, proved stabilising role of real data. We must not claim any of that. Our
    lane is what happens when the reward function is updated on the same data as the policy,
    which every one of their theorems assumes away.
13. **Data-leakage critique of emergent multi-agent results**
   ([arXiv:2505.23796](https://arxiv.org/abs/2505.23796) vs the reply
   [arXiv:2506.18600](https://arxiv.org/abs/2506.18600)) — a general caution that "emergent"
   population-level dynamics in LLMs can be pre-training memorisation. Less applicable to us
   because our organisms are fine-tuned to carry an installed behaviour, but worth knowing
   the critique exists before invoking the naming-game paper as support.

---

## 10. What I could not find

Stated explicitly, because absence is part of the answer:

- **No formal account of bifurcation in a self-judging LLM loop.** Not in the self-rewarding
  literature, not in the self-play literature, not in the model-collapse literature. The
  Lande–Kirkpatrick condition in §4 is my mapping, not anyone's published result.
- **No application of Fisherian runaway theory to ML generator–judge co-adaptation** beyond
  one informal blog post with no model.
- **No paper plotting a signed judge–ground-truth correlation (Pearson/Spearman/Kendall) as a
  labelled per-round series and showing it cross zero.** R-Zero's declining pseudo-label
  accuracy and [arXiv:2607.05904](https://arxiv.org/abs/2607.05904)'s collapsing
  discrimination are the closest; both decline toward chance rather than crossing into
  anti-correlation. CREAM's −0.22 is the judge against its own past self, not against truth.
- **No measurement of self-preference bias as a function of self-training round.** The
  capability-axis follow-up ([arXiv:2504.03846](https://arxiv.org/abs/2504.03846)) measures it
  across seven model families, not across iterations.
- **No multi-round measurement of the AI feedback signal in Constitutional AI or RLAIF** —
  structurally impossible, since neither runs more than one feedback round.
- **No judge-specific fresh-data-injection condition with a stated rate or threshold.** The
  model-collapse literature states the condition on the *generator's* training mix; nobody
  writes "inject fresh human-labelled preference data at rate ρ per round to keep judge–truth
  agreement above θ".
- **No application of critical-slowing-down indicators (rising variance, rising lag-1
  autocorrelation, slowing recovery) to LLM or RLHF training trajectories.** The one
  benchmark of collapse-warning indicators under matched false-positive control failed to
  find an acceptable operating point.
- **No replicator or replicator–mutator equation for a population of *interacting* LLM agents
  with derived stability conditions**, and **no Price-equation decomposition of an LLM
  selection loop with measured terms.** (Corrected from a stronger claim: the *single-model
  curation* loop does have a replicator equation, Ferbach et al.
  [arXiv:2407.09499](https://arxiv.org/abs/2407.09499) — see §5.6 and §6.5.)
- **No stability analysis of a curation loop in which the reward function is itself updated on
  the curated data.** Ferbach's theorems all hold `r` fixed; Perdomo's hold the loss family
  fixed; SPIN's fixed point is an external corpus. This is the actual hole.
- **Primary text I could not obtain:** Cartlidge & Bullock (2004) on disengagement (403 from
  both hosts); Lande (1981) and Kirkpatrick (1982) originals (paywalled — the conditions in
  §4 come from the Kuijper/Pen/Weissing Annual Review, whose relevant pages I extracted and
  read in full); Scheffer et al. (2009) (paywalled — cited from its DOI and from secondary
  sources I did read); the R-Zero table read through ar5iv rather than the published PDF.

**Confidence flags on numbers in this report.** Verbatim-verified by me against primary
sources: the Kuijper/Pen/Weissing stability condition and Lande's equations; the Ashery
40/40/26-14/36-4 convention counts, the "2% … 67%" quote and the basin-of-attraction quote;
the Vallinder & Hughes 44/47 vs 50/53/54 donation split and the threshold hypothesis; the
Perdomo Theorem 3.5 inequality; the Mescheder/Nagarajan–Kolter/Heusel abstract claims; the
attractor-states design and its `S_basin` 1.50–4.08, 23.6% contraction and α = 0.266/0.665.
Read once, through a summariser, and worth re-checking before they go on a summary surface:
the R-Zero Table 5 per-iteration accuracies; the Meta-Rewarding Table 5 bias percentages; the
CREAM τ values and per-iteration accuracy table; the length-bias percentages from
[arXiv:2310.03716](https://arxiv.org/abs/2310.03716). Unverified 2026 single-author preprints
whose numbers I would not cite without reading the PDF:
[arXiv:2607.05904](https://arxiv.org/abs/2607.05904),
[arXiv:2607.06001](https://arxiv.org/abs/2607.06001),
[arXiv:2606.00329](https://arxiv.org/abs/2606.00329).

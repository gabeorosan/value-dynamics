# Where curated self-training loops end up: what the literature already knows

*Literature review, 2026-07-28. Question: cultural evolution, iterated learning
and the self-consuming-loop literature — what do they predict about the endpoint
of a loop like ours, and what quantitative laws do they offer? Every paper below
was opened (arXiv abstract page, arXiv/ar5iv HTML full text, publisher HTML, or a
locally extracted PDF) unless the entry says otherwise. Where I could only reach
an abstract or a secondary summary, I say so in the entry.*

**Our loop, for reference throughout.** A LoRA-tuned organism (Qwen3-4B or
OLMo-3-7B) generates 6 candidate answers per prompt; a judge — its own frozen base
model, or a scripted oracle — picks 2 by pairwise comparison; the organism is SFT'd
on the kept answers, continuing from its own current adapter; repeat 4 rounds. A
value `v` in [0,1] is re-measured on held-out prompts between rounds. The project's
committed results that this review is written against, each of which has a row in
`docs/ANALYSIS_LEDGER.md`: the per-round selector gap factorizes as
`gap = kept_mean − pool_mean ≈ ρσ`; the next value tracks the kept mean at
MAE 0.081 over 340 rounds; the causally identified transmission coefficient from
the randomized knapsack instrument is **0.754, bootstrap 95% CI [0.621, 0.984]**
over 36 round-1 matched pairs; and the per-round response slope decays
**0.509 → 0.377 → 0.231** across rounds.

---

## 0. The one-paragraph answer

The strongest theory for our exact setup is Ferbach, Bertrand, Bose & Gidel,
*Self-Consuming Generative Models with Curated Data Provably Optimize Human
Preferences* ([arXiv:2407.09499](https://arxiv.org/abs/2407.09499), NeurIPS 2024).
It says a pure curated self-consuming loop converges to the *initial* distribution
restricted to the reward-maximizing set — total fixation on the judge's favourites,
not an intermediate equilibrium — and it says a loop that keeps mixing in reference
data instead sits forever inside a bounded KL ball around that reference, which
means its reward gain has a **ceiling**. Our loop satisfies the qualitative shape of
the first result and essentially none of the technical assumptions behind the rate.
The competing endpoint theory — Griffiths & Kalish's proof that iterated Bayesian
learning converges to the learner's prior
([doi:10.1080/15326900701326576](https://onlinelibrary.wiley.com/doi/abs/10.1080/15326900701326576))
— is, I think, **out of scope for us**, for one decisive structural reason that I
have not seen anyone state cleanly: their chain re-instantiates a fresh learner
with the prior every generation, while ours continues fine-tuning the same weights,
and in our loop the base model's prior enters through the *judge*, i.e. as a
selection force, not as a learning force. That inversion is testable and it is the
single most valuable experiment on the list in §7.

---

## 1. The self-consuming / recursive-training family: what the conditions actually say

### 1.1 Ferbach et al. — the closest formal model of our loop

[arXiv:2407.09499](https://arxiv.org/abs/2407.09499) (Damien Ferbach, Quentin
Bertrand, Avishek Joey Bose, Gauthier Gidel; NeurIPS 2024). Read via
[ar5iv full text](https://ar5iv.labs.arxiv.org/html/2407.09499).

**Setup.** Each round solves

> `p_{t+1} = arg max_{p∈P}  1/(1+λ) · E_{x~p_ref}[log p(x)]  +  λ/(1+λ) · E_{x₁..x_K~p_t; x̂~BT(x₁..x_K)}[log p(x̂)]`

with the curation step a Bradley–Terry discrete choice over K samples,
`P(x̂ = x_k | x₁..x_K) = e^{r(x_k)} / Σ_j e^{r(x_j)}`. Here `K` is the number of
candidates offered per curation event and `λ/(1+λ)` is the synthetic-data fraction;
`λ → ∞` is the pure self-consuming loop, `λ = 0` is retraining on reference data only.
The motivating example in the paper is a text-to-image interface that shows the user
several variations and learns from the one they click. Our loop is that, with K = 6
and the judge in the user's seat.

**The results, stated.**

- **Assumption 2.1** — there is an `r*` with `r(x) ≤ r*` almost surely under `p₀`,
  and `p₀` puts positive mass in a neighbourhood of the maximizer.
- **Lemma 2.1** — as `K → ∞`, `p_{t+1}(x) → p_t(x) e^{r(x)} / E_{x̃~p_t}[e^{r(x̃)}]`.
  This is the discrete-time replicator equation with fitness `e^{r}`. The paper never
  uses the word "replicator" — I searched the full text; the identification is ours
  and is standard, but it is not a quotation.
- **Lemma 2.2** — the expected reward increases by at least a variance term:
  `E_{p_{t+1}}[e^r] ≥ E_{p_t}[e^r] + ((K−1)/K) · Var_{p_t}[e^r] / e^{r*}`.
  This is a Fisher's-fundamental-theorem-shaped statement, with an explicit finite-pool
  factor `(K−1)/K` — which for our K = 6 equals 0.833.
- **Theorem 2.1** — `D_KL(p* ‖ p_t) → 0` as `t → ∞`, where
  `p*(x) := p₀(x) · 1{r(x) = r*} / P₀(r(x) = r*)`. **The endpoint is the initial
  distribution conditioned on being reward-optimal.** Not a compromise, not a
  mutation–selection balance: fixation.
- **Assumption 2.2** (for the parametric case) — L-Lipschitz Hessians and
  `E_{p_data}[∇²_θ log p_θ(x)] ⪯ −αI ≺ 0`, i.e. local strong log-concavity in
  parameters.
- **Theorem 2.2** — if `Lε < α` and `λ < α/(2Lε)`, then
  `D_KL(p_{θ*} ‖ p_{θ_t}) = Õ( (λ(α+εL)/(α+λ(α−εL)))^{2t} )`. `ε` bounds the
  Wasserstein distance between the initial model and the optimum: **the loop is only
  provably stable if you start close enough and mix in enough real data.**
- **Theorem 2.3** — a mixed loop still beats the reference:
  `E_{p_t}[e^r] ≥ E_{p_ref}[e^r] + (λ/(1+λ)³) · (K−1) Var_{p_ref}[e^r] / (K e^{r*})`.
- **Theorem 2.4** — if `λ < 1/(K−1)`, then `D_KL(p_t ‖ p_ref) ≤ −log(1 − λ(K−1))`.
  **A bounded KL ball around the reference, uniformly in t.** This is the theoretical
  ceiling that makes a mixed curated loop saturate.

On finite K the paper says small K "act as a regularization which prevents the density
from blowing up too much in high rewards areas". Their CIFAR-10 experiment trains a
normalizing flow, generates 5·10⁴ samples per iteration and keeps 2.5·10³ by K-choice
comparison, for 10 retraining steps, with a VGG11 classifier (92.39% test accuracy) as
reward. With curated data only, class proportions become progressively more
heterogeneous while reward rises monotonically — bias amplification. With `λ = 1/2`,
class proportions stay roughly uniform and average reward **increases before
stabilizing**. That last phrase is the paper's own observation of saturation, in a
mixed loop, and it is Theorem 2.4 showing up empirically.

**Where the "1.0" prediction actually comes from — a correction worth carrying.**
The ledger row for the transmission coefficient attributes the idealized prediction
of 1.0 to Lemma 2.1's `K → ∞` limit. That is the right paper and the right spirit but
the wrong mechanism, and the difference matters for where we look for the missing
0.25. Setting `λ → ∞` and `P = P(ℝ^d)` in Equation 4 makes `p_{t+1}` **equal to the
curated distribution exactly**, whatever K is — so the next round's mean equals the
kept mean identically, i.e. transmission coefficient 1.0, and this follows from
*perfect nonparametric fitting*, not from large K. K controls the *strength of the
tilt* (how big the selection differential is), not the *fidelity of transmission*.
So the shortfall from 1.0 to 0.754 is a statement about the model class and the SFT
optimizer — LoRA rank, epochs, learning rate, KL-ish implicit regularization,
continued-from-previous-adapter path dependence — and Theorem 2.2 is the right place
in the paper to look for it, not Lemma 2.1. Ferbach's own finite-K factor `(K−1)/K =
0.833` at K = 6 happens to sit inside our CI [0.621, 0.984], which is suggestive, but
it multiplies a *variance lower bound on reward gain*, not a response-to-differential
ratio; treating the numerical coincidence as a prediction would be a mistake.

**Second correction, on what converges.** Ferbach's `r` is the judge's reward. Our
`v` is a different function of the same answer, correlated with `r` at within-prompt
correlation `ρ`. So Theorem 2.1 does **not** predict `v → 1`. It predicts

> `v_∞ = E_{p₀}[ v(x) | r(x) = r* ]`

— the value of the judge's favourite answers, averaged over the initial support.
The endpoint is a property of the judge and of the organism's initial support, and
`ρ` governs the *route*, not the destination. Every one of our runs that "rails" at
0 or 1 is consistent with this only if the judge's argmax set is value-homogeneous;
runs that stall at an interior value (e.g. seed 707 flat at 0.625, in `docs/PLAN.md`)
are exactly what this formula predicts when it is not.

### 1.2 The rest of the family and what their conditions really are

- **Shumailov, Shumaylov, Zhao, Papernot, Anderson & Gal**, *AI models collapse
  when trained on recursively generated data*, Nature 631:755–759 (2024);
  preprint [arXiv:2305.17493](https://arxiv.org/abs/2305.17493). Two named regimes:
  *early* collapse, where the tails of the distribution are lost to finite-sampling
  error, and *late* collapse, where the model converges to a point estimate with
  little variance. Two named causes: finite sampling error and functional
  approximation error. Their loop has **no selection step** — that is the crucial
  difference from ours. Their prescription is periodic injection of fresh human data.
  I read the summary and abstract, not the Nature full text (paywalled).
- **Bertrand, Bose, Duplessis, Jiralerspong & Gidel**, *On the Stability of Iterative
  Retraining of Generative Models on their own Data*
  ([arXiv:2310.00429](https://arxiv.org/abs/2310.00429), ICLR 2024). Stability of the
  retraining map holds under two conditions together: the initial model approximates
  the data distribution well enough, **and** the proportion of clean real data is
  large enough. This is the direct ancestor of Ferbach's Theorem 2.2 and shares its
  shape: local stability, not global convergence.
- **Gerstgrasser, Schaeffer, Dey, Rafailov, Sleight, Hughes, Korbak, Agrawal, Pai,
  Gromov, Roberts, Yang, Donoho & Koyejo**, *Is Model Collapse Inevitable? Breaking
  the Curse of Recursion by Accumulating Real and Synthetic Data*
  ([arXiv:2404.01413](https://arxiv.org/abs/2404.01413)). The condition that matters
  is **replace versus accumulate**. Under replacement, test error grows with the number
  of fitting iterations; under accumulation of each generation's synthetic data
  alongside the original real data, in a tractable sequence-of-linear-models setting,
  the test error has a *finite upper bound independent of the number of iterations*.
  Our loop replaces (each round's SFT set is that round's kept answers), so we are on
  the collapsing side of their dichotomy — but again, with a selection step they do
  not have.
- **Dohmatob, Feng, Yang, Charton & Kempe**, *A Tale of Tails: Model Collapse as a
  Change of Scaling Laws* ([arXiv:2402.07043](https://arxiv.org/abs/2402.07043),
  ICML 2024) and **Dohmatob, Feng, Subramonian & Kempe**, *Strong Model Collapse*
  ([arXiv:2410.04840](https://arxiv.org/abs/2410.04840), ICLR 2025). The first frames
  collapse as a change in the *scaling law* — loss of scaling, shifted scaling with
  generation count, un-learning of skills, and grokking in human/synthetic mixtures —
  via a "double scaling law". The second is the harsher claim: in a supervised
  regression setting, a synthetic fraction as small as 1 in 1000 can produce collapse,
  in the sense that larger training sets stop helping. Both are about *pretraining
  scaling*, and neither has a curation step, so they bear on our loop only as a
  warning about what happens to the substrate underneath the value axis.
- **Alemohammad, Casco-Rodriguez, Luzi, Humayun, Babaei, LeJeune, Siahkoohi &
  Baraniuk**, *Self-Consuming Generative Models Go MAD*
  ([arXiv:2307.01850](https://arxiv.org/abs/2307.01850), ICLR 2024). Three loop
  families distinguished by whether real data is fixed, fresh, or absent, and by
  whether sampling is biased for quality against diversity. The headline condition:
  without *enough fresh real data in each generation*, quality (precision) or
  diversity (recall) progressively decreases. Our K-sampled selection loop is
  precisely their "biased sampling trading quality against diversity" arm.
- **Schaeffer, Kazdan, Arulandu & Koyejo**, *Position: Model Collapse Does Not Mean
  What You Think* ([arXiv:2503.03150](https://arxiv.org/abs/2503.03150)). Counts
  **eight distinct and at times conflicting definitions** of model collapse in the
  literature and argues several prominent collapse scenarios are readily avoidable
  under realistic conditions. Read this before we use the phrase "model collapse"
  anywhere in the writeup; we should say which of the eight we mean, or avoid the term.
- **Yi, Liu, Cheng & Xu**, *Escaping Model Collapse via Synthetic Data Verification:
  Near-term Improvements and Long-term Convergence*
  ([arXiv:2510.16657](https://arxiv.org/abs/2510.16657), revised July 2026). This is
  the second-most relevant paper in the review and it is not yet cited anywhere in the
  repo. In a linear-regression setting, verifier-guided retraining does not collapse,
  but drives the parameter estimate to the **verifier's "knowledge center"** in the
  long run — and, crucially, *"unless the verifier is perfectly reliable, these early
  gains will plateau and may even reverse"*. Confirmed on linear regression, VAEs on
  MNIST, and SmolLM2-135M fine-tuned on XSUM. Our frozen base judge is an imperfect
  verifier by construction. **This is a named, published prediction of exactly the
  saturation we observe, and it comes with a directional prediction we have not
  tested: continue past round 4 and the value should stop, then reverse.**
- **Fu, Wang, Chen, Tian & Tao**, *A Theoretical Perspective: How to Prevent Model
  Collapse in Self-consuming Training Loops*
  ([arXiv:2502.18865](https://arxiv.org/abs/2502.18865), ICLR 2025). Introduces
  "recursive stability"; the operative condition is that a *constant-sized proportion*
  of real data suffices for convergence, including for transformer in-context learning.
  Read at abstract level only.
- **Kovač, Perez, Portelas, Dominey & Oudeyer**, *Recursive Training Loops in LLMs:
  How training data properties modulate distribution shift in generated data*
  ([arXiv:2504.03814](https://arxiv.org/abs/2504.03814), EMNLP 2025). Empirical, and
  the finding is a `σ`-style statement in another vocabulary: **lexical diversity
  amplifies distribution shift, while semantic diversity and data quality mitigate it**.
  Read at abstract level.

---

## 2. Iterated learning: the prior-convergence theorem, stated precisely

### 2.1 Griffiths & Kalish (2007), the actual theorem

Thomas L. Griffiths & Michael L. Kalish, *Language Evolution by Iterated Learning
With Bayesian Agents*, Cognitive Science 31(3):441–480 (2007),
[doi:10.1080/15326900701326576](https://onlinelibrary.wiley.com/doi/abs/10.1080/15326900701326576);
[author PDF](https://cocosci.princeton.edu/tom/papers/iteratedcogsci.pdf). I read the
full 40-page PDF locally.

**The setup.** Generation `n` learner sees data `d_{n−1}`, infers a hypothesis `h_n`
by Bayesian inference `P(h|d) ∝ P_PA(d|h) P(h)`, then produces data `d_n` from `h_n`
for the next learner. Reduce the process to a Markov chain on hypotheses with
transition matrix `Q = (q_ij)`, or to a Markov chain on data with matrix `R`.

**The result for sampling learners.** If each learner *samples* `h` from the
posterior, the stationary distribution of the chain on hypotheses is the prior:
"The stationary distribution of the Markov chain on hypotheses is thus the prior
distribution." Equivalently — and this is the paper's best-known move — the pair
`(d, h)` chain is exactly a Gibbs sampler for `P(d,h) = P_PA(d|h) P(h)`, alternating
`P_samp(h|d)` and `P_PA(d|h)`. The paper's summary of the consequence:
"The asymptotic outcome of iterated learning thus does not depend on the amount or
structure of the data seen by the learners, or the properties of the hypotheses those
learners consider, except insofar as those factors influence the prior probabilities."
Convergence is geometric in the number of generations, by the standard Gibbs-sampler
results they cite; in their two-language worked example the second eigenvalue is
`λ₂ = 1 − [s + (1−s)(1−ε)ε(1/(α+ε−2αε) + 1/(1−α−ε+2αε))]`, so the rate is set by the
overlap `s` between languages and the production noise `ε`.

**The assumptions, as the paper itself lists them in §8.1.**

1. *Assumption 1* — all learners use the same learning algorithm and the same
   production algorithm; under Bayes this forces a **shared hypothesis space and a
   shared prior**.
2. *Assumption 2* — discrete generations, **one learner per generation, receiving data
   produced by the previous learner**. (They show this can be swapped for a large
   population in continuous time with random pairing.)
3. *Assumption 3* — learners know the production distribution `P_PA(d|h)`;
   consistency between learning and production.
4. Ergodicity of the chain. Their example is non-ergodic exactly when `s = 0` and
   `ε = 0` — no overlap and no noise — in which case "both languages act as sinks".

**The MAP variant, which is the one that actually matters for us.** If learners take
the posterior mode instead of sampling, the correspondence is to *stochastic EM*, not
Gibbs, and — their §5.3 summary — MAP iterated learning "still favors languages with
higher prior probability, but the stationary distribution depends on the nature of the
hypotheses and the amount of noise", being "approximately centered on the hypotheses
with greatest prior probability" with variance around them. So the clean
"converges-to-the-prior" theorem is specific to *sampling* learners. **Under MAP the
prior is amplified rather than reproduced** — which is the result Kirby, Dowman &
Griffiths, *Innateness and culture in the evolution of language*, PNAS
104(12):5241–5245 (2007), [doi:10.1073/pnas.0608222104](https://doi.org/10.1073/pnas.0608222104),
turn into the headline claim that cultural transmission can magnify weak biases into
strong universals. (PNAS full text was 403 to me; I have this from the abstract and
from secondary descriptions, and I flag it as not independently verified.)

**Empirical confirmation with humans.** Kalish, Griffiths & Lewandowsky, *Iterated
learning: Intergenerational knowledge transmission reveals inductive biases*,
Psychonomic Bulletin & Review 14:288–294 (2007),
[doi:10.3758/BF03194066](https://link.springer.com/article/10.3758/BF03194066):
participants in iterated function-learning chains converge on positive linear
functions **within 1–4 generations regardless of the seed function**. Note the
timescale — 1 to 4 generations is exactly our horizon. If the prior-convergence
picture applied to us, our 4-round runs would already be near their endpoint and
initial conditions would already be washed out.

**Laboratory transmission chains.** Kirby, Cornish & Smith, *Cumulative cultural
evolution in the laboratory*, PNAS 105(31):10681–10686 (2008),
[doi:10.1073/pnas.0707835105](https://doi.org/10.1073/pnas.0707835105) — the classic
demonstration that a transmission bottleneck alone drives artificial languages toward
learnable, structured systems. Kirby, Tamariz, Cornish & Smith, *Compression and
communication in the cultural evolution of linguistic structure*, Cognition 141:87–102
(2015), [doi:10.1016/j.cognition.2015.03.016](https://doi.org/10.1016/j.cognition.2015.03.016)
— compression pressure alone yields degenerate languages; you need a *communicative*
pressure alongside it to get compositional ones. **PNAS returned 403 for both; I have
these from abstracts and from Guo et al.'s description (§2.3), and mark them as not
independently read.**

### 2.2 The application to neural nets and LLMs

- **Ren, Guo, Qiu, Wang & Sutherland**, *Bias Amplification in Language Model
  Evolution: An Iterated Learning Perspective*
  ([arXiv:2404.04286](https://arxiv.org/abs/2404.04286), NeurIPS 2024). The key
  formal object is a three-phase generation: **imitation** (learn from predecessor's
  data), **interaction** (refine by performing tasks — this is the selection step),
  **transmission** (generate for the successor). Their Proposition 1: after enough
  generations `P_lm(h) → 1(h = h^{T*})`, where `h^{T*}` is a stationary point of the
  prior `P₀(h)` restricted to an effective hypothesis set `ℋ_eff` carved out by the
  interaction phase. The three consequences they draw: the converged hypothesis
  "only depends on `P₀(h)` and `ℋ_eff`, irrelevant to selection of `d⁰`"; biases in
  `P₀` are amplified and the entropy of `P_lm` falls; and a carefully designed
  interaction phase can restrain harmful hypotheses by shaping `ℋ_eff`. Bias
  amplification is "easier ... when likelihood is weaker".
  **The initial-condition-independence claim is the sharpest testable difference
  between their framework and ours**, and our forecast result (round-1 measurements
  predict 4-round endpoints at MAE 0.118 against 0.431 for no-change) is prima facie
  evidence against it at our horizon.
- **Guo, Wu & Yiu**, *Model Collapse as Cultural Evolution*
  ([arXiv:2605.23054](https://arxiv.org/abs/2605.23054), May 2026). Self-trains
  LLaMA-2-7B and Mistral-7B for 10 generations in English, German and Turkish, and
  derives five predictions with explicitly labelled discriminative status: P1
  frequency-dependent loss order (partially discriminative), P2 monotonic regularity
  increase (confirmatory), P3 dimension-specific degradation rates (partially
  discriminative), **P4 non-monotonic compositionality — initially rising then falling
  — (uniquely discriminative, their critical test)**, P5 distributional narrowing
  (confirmatory). All five confirmed with Hedges' g > 1.6 and BF₁₀ > 100; their
  regularization gradient matches the human curve at R² = 0.94. Methodologically this
  is the model for how we should be writing our own predictions: **state which
  predictions discriminate the theory from a generic alternative, before running.**
  It is also a priority flag — the "model collapse is cultural evolution" framing is
  now published, so our contribution has to be the *quantitative transmission law*,
  not the framing.
- **Perez, Kovač, Léger, Colas, Molinaro, Derex, Oudeyer & Moulin-Frier**, *When LLMs
  Play the Telephone Game: Cultural Attractors as Conceptual Tools to Evaluate LLMs in
  Multi-turn Settings* ([arXiv:2407.04503](https://arxiv.org/abs/2407.04503),
  ICLR 2025). See §3.2 — this is the cleanest quantitative attractor measurement in the
  LLM literature and it is the main *competing* model to ours.
- **Acerbi & Stubbersfield**, *Large language models show human-like content biases
  in transmission chain experiments*, PNAS 120(44):e2313790120 (2023),
  [doi:10.1073/pnas.2313790120](https://doi.org/10.1073/pnas.2313790120). LLMs
  reproduce human content biases (negativity, social, threat-related content) in
  transmission chains. Read at abstract level. Relevant because it says the *prior*
  an LLM chain converges toward is not arbitrary — it is human-content-bias shaped,
  which is a testable statement about the direction of our off-target drift.

### 2.3 Honest verdict: is our setup in scope of Griffiths & Kalish?

**No, and for a reason more specific than "we're not Bayesian".**

- **The learner is not reset.** Griffiths & Kalish's Assumption 2 gives each
  generation a *fresh* learner who re-applies the prior to whatever data arrives. Our
  organism continues SFT from its own previous adapter. There is no per-round
  re-application of a prior; there is a per-round *increment* on top of accumulated
  weights. The chain-on-hypotheses is not homogeneous in their sense, because the
  transition kernel at round `t` depends on the whole path.
- **Our prior enters through the judge, not the learner.** When the judge is the
  frozen base model, the base model's inductive bias acts as a *selection* force on
  candidates, not as a *learning* bias on the update. In Ferbach's language it is the
  reward `r`, not a regularizer on `p`. So the analogue of "convergence to the prior"
  in our loop is convergence to the judge's argmax set — Ferbach's `p*` — which is a
  strictly different object from the base model's marginal distribution over answers.
  This is, as far as I can find, an unstated inversion in the LLM iterated-learning
  literature, which universally assumes the prior lives in the learner.
- **There is a selection step at all.** Griffiths & Kalish's chain has no fitness
  differential; it is pure transmission. Their theorem is therefore the `ρ = 0` null
  of our decomposition. Our own random-selection arm — 16 rounds with mean drift
  exactly 0.0000 at SD 0.186 while spread was fully present, in
  `docs/reports/report_population_genetics_unification.md` — is the empirical version
  of that null and it does *not* show prior convergence; it shows mean-zero diffusion.
- **The empirical confirmation runs the wrong way at our horizon.** Kalish et al.
  found human chains converged in 1–4 generations regardless of seed. We forecast
  4-round endpoints from round-1 measurements at MAE 0.118 versus 0.431 for
  no-change. Initial conditions carry, at our horizon, most of the signal.

The framework that *is* in scope is Ren et al.'s three-phase version — because it has
an interaction/selection phase — but even there Proposition 1 assumes the agent's
knowledge is re-derived by Bayesian updating each generation, which is true for their
in-context-learning instantiation and false for weight-space fine-tuning.

---

## 3. Cultural attractor theory and the quantitative decompositions on offer

### 3.1 The theory

Claidière, Scott-Phillips & Sperber, *How Darwinian is cultural evolution?*,
Phil. Trans. R. Soc. B 369(1642):20130368 (2014),
[doi:10.1098/rstb.2013.0368](https://royalsocietypublishing.org/doi/10.1098/rstb.2013.0368)
([PMC free full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3982669/), which I read).
Three nested frames: a population is **evolutionary** if frequencies at each step are
largely explained by frequencies at earlier steps; **selectional** if it renews itself
through reproduction with variation, heritability and fitness differences; and
**replicative** if heritability is secured by replication. Their formalization of
attraction:

> `F_Y(t+1) = Σ_X [ I_{XY} · F_X(t) ] / N_T`

where `I_{XY}` is the average impact an item of type X at time t has on the frequency
of type Y at t+1. An **attractor** is any type whose relative frequency tends to
increase. The move that matters for us is that they make selection a *special case*:
"Reproductive success is a special aspect of attraction, rather than an alternative to
it. Specifically, a selected trait is an attractor that owes its higher frequency
mostly to homo-impact" — that is, the diagonal `I_{XX}` terms. Off-diagonal impact is
transformation.

**What I could not find:** no explicit selection-versus-attraction *decomposition
coefficient* in this paper, and no mention of the Price equation in it. The
quantitative separation the project wants is not in cultural attractor theory's
founding formalization; it is in the Price-equation-for-culture literature (§3.3).

Boyd & Richerson's dual-inheritance apparatus (*Culture and the Evolutionary Process*,
University of Chicago Press, 1985) supplies the other half of the vocabulary:
**guided variation** (each individual transforms the variant it received in a
consistent direction, then transmits unbiased) versus **biased transmission** (content,
frequency, and model-based biases operating at the point of copying). Guided variation
is our SFT drift; content bias is our judge. I did not obtain the book's recurrence
equations; the descriptions here are from secondary sources and I have not verified
the equations themselves.

### 3.2 The one quantitative attractor law that is directly runnable on our data

Perez, Kovač, Léger, Colas, Molinaro, Derex, Oudeyer & Moulin-Frier,
[arXiv:2407.04503](https://arxiv.org/abs/2407.04503) (ICLR 2025), read via
[HTML v2](https://arxiv.org/html/2407.04503v2). Chains of the form
`text_{i+1} = LLM(task, text_i)` run for 50 generations. They fit, per property,

> `property(generation = n) = I + s · property_initial`

and read off the fixed point `l = I/(1−s)`, with attractor strength `1 − s`, and
long-run behaviour `property(k·n) = s^k (property_initial − l) + l`; in their words,
"If |s|<1, then the sequence converges, its limit is l and its convergence rate is
1−s." Properties tracked: toxicity (Detoxify, 0–1), positivity (VADER, −1 to +1),
difficulty (Gunning-Fog), length (characters). Findings: the more open-ended the
instruction, the stronger the attraction — "Continue" beats "Take Inspiration"
(95% CI on the difference [0.0511, 0.254]), which beats "Rephrase" ([0.0326, 0.2377]);
and toxicity has significantly stronger attractors than positivity ([0.1158, 0.3515]),
difficulty ([0.1072, 0.3417]) or length ([0.173, 0.407]).

**This is the model we have to beat.** It is a pure attractor model — a first-order
linear map with no selection term, no candidate pool, no `σ`, no `ρ` — and on a value
trajectory it will look a lot like ours. `v_{t+1} = I + s·v_t` with `s ≈ 0.25` would
reproduce "next value ≈ kept mean" as a coincidence if kept mean happens to track
`I + s v_t`. The discriminating test is in §6: their model has **no free parameter
that responds to candidate spread**, so an intervention that changes `σ` at fixed pool
mean must move the next value under our model and must not under theirs. We have
already run that intervention twice (spread arm +0.406 and +0.368 against
concentrated +0.017 and +0.073 at matched pool mean, in
`docs/reports/report_transmission_followups.md` §1). **That comparison is the single
strongest existing argument that our loop is selectional and not merely attractional,
and the report does not currently frame it that way. It should.**

### 3.3 The Price equation applied to culture

- **El Mouden, André, Morin & Nettle**, *Cultural transmission and the evolution of
  human behaviour: a general approach based on the Price equation*, Journal of
  Evolutionary Biology 27(1):231–241 (2014),
  [doi:10.1111/jeb.12296](https://onlinelibrary.wiley.com/doi/full/10.1111/jeb.12296).
  Treats transmitted culture as an inheritance system in its own right and defines
  cultural fitness, relatedness and altruism through the Price decomposition. Read at
  abstract level; Wiley full text was not reachable.
- **Nettle**, *Selection, adaptation, inheritance and design in human culture: the
  view from the Price equation*, Phil. Trans. R. Soc. B 375(1797):20190358 (2020),
  [doi:10.1098/rstb.2019.0358](https://royalsocietypublishing.org/doi/10.1098/rstb.2019.0358).
  **403 to me; not read.** From the theme issue's cross-references this is the paper
  that maps cultural attraction onto the Price transmission term, which is the
  decomposition the project wants. Worth a second attempt through a library proxy.
- **Lehtonen, Okasha & Helanterä**, *Fifty years of the Price equation*, Phil. Trans.
  R. Soc. B 375(1797):20190350 (2020),
  [PMC7133514](https://pmc.ncbi.nlm.nih.gov/articles/PMC7133514/) — read. States the
  equation as `w̄Δḡ = cov(w,g) + E[wΔg]`, decomposing total change into a selection
  term and a transmission term, and surveys the applications across kin selection,
  epidemiology, cultural evolution and animal breeding.

---

## 4. The Price equation: the tautology critique, stated fairly, then answered

### 4.1 The critique

The Price equation `w̄ Δḡ = cov(w,g) + E[w Δg]` is an algebraic identity: it follows
from the definitions of the means and requires no biology. From that, three related
objections:

1. **It is a tautology whose terms are meaningless in general.** The canonical
   statement is **Matthijs van Veelen**, *The problem with the Price equation*,
   Phil. Trans. R. Soc. B 375(1797):20190355 (2020),
   [doi:10.1098/rstb.2019.0355](https://doi.org/10.1098/rstb.2019.0355)
   ([PMC7133513](https://pmc.ncbi.nlm.nih.gov/articles/PMC7133513/), open access —
   I read this one in full, and it is the version to cite). His thesis, in his own
   words: *"the generality of the Price equation comes at a cost, and that is that the
   terms in it become meaningless."* He concedes the tautology point immediately and
   says it is beside the point — *"being a tautology and being general is in itself
   not that special"* — and demonstrates this by constructing deliberately absurd rival
   tautologies (dividing through by Planck's constant and by Eurovision wins) to make
   the argument that *"usefulness of a tautology depends on whether or not the
   right-hand side has a meaningful interpretation."* The sharp form: *"The generality
   of the Price equation—and this is the broader point—is at odds with β having a
   meaningful interpretation."*

   **And he states the condition under which the regression coefficient *does* mean
   something: fitness must be linear in the variable of interest `p`, and `p` must be
   uncorrelated with any other variable that affects fitness.** That is not a
   philosophical objection at all — it is an omitted-variable condition, and it is
   directly checkable in our design. See §4.2. The earlier statements of the same
   position are *On the use of the Price equation*, JTB 237(4):412–426 (2005),
   [doi:10.1016/j.jtbi.2005.04.026](https://doi.org/10.1016/j.jtbi.2005.04.026), and
   **van Veelen, García, Sabelis & Egas**, *Group selection and inclusive fitness are
   not equivalent; the Price equation vs. models and statistics*, JTB 299:64–80 (2012),
   [doi:10.1016/j.jtbi.2011.07.025](https://doi.org/10.1016/j.jtbi.2011.07.025);
   both ScienceDirect pages returned 403 to me and I have not read them in the
   original.
2. **Dynamic insufficiency.** The equation relates one generation to the next but does
   not supply the next generation's covariances and expectations, so it cannot be
   iterated forward without extra assumptions. This is the standard statement, also
   attributed to van Veelen et al. (2012).
3. **The terms are statistical, not causal.** **Okasha & Otsuka**, *The Price equation
   and the causal analysis of evolutionary change*, Phil. Trans. R. Soc. B
   375(1797):20190365 (2020),
   [doi:10.1098/rstb.2019.0365](https://royalsocietypublishing.org/doi/10.1098/rstb.2019.0365),
   PMID [32146881](https://pubmed.ncbi.nlm.nih.gov/32146881/). Their position, from
   the abstract: the Price equation is "simply a statistical identity", biologists
   have adopted a causal reading of its terms, and only if substantive assumptions
   about causal structure are made — assumptions expressible as an explicit causal
   model — can the components be interpreted as causally meaningful. **The
   RoyalSociety page 403'd; I have the abstract from search results and from
   Lehtonen et al.'s paraphrase of it, not the full text.** Okasha's *Evolution and
   the Levels of Selection* (OUP 2006) makes the related point that the Price
   partition can manufacture apparent higher-level selection out of lower-level
   selection (the cross-level by-product problem), and prefers contextual analysis for
   that reason. Defences: **Frank**, *Natural selection. IV. The Price equation*,
   J. Evol. Biol. 25:1002–1019 (2012),
   [arXiv:1204.1515](https://arxiv.org/abs/1204.1515); **Luque**, *One equation to
   rule them all: a philosophical analysis of the Price equation*, Biology &
   Philosophy 32:97–125 (2017),
   [doi:10.1007/s10539-016-9538-y](https://link.springer.com/article/10.1007/s10539-016-9538-y).

### 4.2 Which of our claims the critique actually touches

Sorting our claims by exposure, which is the useful thing to do:

**Fully exposed (the objection lands).**

- `gap = kept_mean − pool_mean ≈ ρσ` with R² = 0.80. This is an order-statistic
  identity on a finite pool: if you sort 6 candidates by a selector and keep 2, the
  gap *must* be the product of the material available (σ) and how well the selector
  sorts on the axis (ρ). The repo already flags it as "near-tautological" in
  `report_population_genetics_unification.md`, correctly. What is *not* tautological
  in it is the fitted slope: the identity predicts the coefficient on `ρσ` is exactly
  1, and we measured 0.964 with MAE 0.043 on n = 175. **A tautology that makes a point
  prediction and hits it is a validated measurement instrument, not a discovery.**
  That is the right frame for this term, and the writeup should use it: `ρσ` is how we
  *measure* the selection differential, and the measurement checks out.
- Any statement of the form "the value changed because there was covariance between
  the judge's preference and the value" — that is the definition of the selection term,
  not a finding.

**Partly exposed.**

- "Next value ≈ kept mean, MAE 0.081 over 340 rounds." The identity does not require
  this. It says total change decomposes into selection plus transmission; it is silent
  on whether the transmission term is near zero. Finding that a *single* coefficient
  near 0.8 works across organisms, axes, judges and pool types (0.784 to 0.949 across
  the eight slices in `report_population_genetics_unification.md`) is an empirical
  regularity the identity does not predict. It could have been 0.2, or condition-dependent.
  Exposure comes from the two sides sharing candidate scores in some slices; the
  interior-only control (0.831 restricted to 0.2 ≤ v ≤ 0.8, versus 0.804 pooled) is the
  right guard and it holds.

**Not exposed — and this is the answer to the critique.**

- **The causal transmission coefficient of 0.754 [0.621, 0.984] from the randomized
  knapsack instrument.** Okasha & Otsuka's demand is precisely that you supply a causal
  model rather than read causation off the partition. A randomized encouragement design
  *is* that causal model: both arms start from the identical cached adapter, draw from
  one shared candidate pool, are held to the same offered-pool mean, and differ only in
  the experimenter's concentrated-versus-spread arrangement; the first stage moves the
  round-1 gap by +0.1875 (SE 0.0316, F = 35.1) and the Wald ratio over 36 matched pairs
  gives 0.754. **This is exactly the move the critique asks for, and it means the
  tautology objection does not reach our headline number.** It is worth saying so
  explicitly in the writeup, and citing Okasha & Otsuka while doing it — pre-empting
  the objection with the instrument is a stronger position than most Price-equation
  applications in the cultural-evolution literature occupy.
- The dynamic-insufficiency objection is likewise answered, not by argument but by
  measurement: we do not assume the next round's `σ` and `ρ`, we measure them, and the
  binomial variance identity `V_within = q(1−q) − V_between` (exact to machine
  precision over 280 rounds) supplies the missing recursion for the binary axis. That
  is a *dynamically sufficient* closure of the Price equation for this system, which is
  precisely what van Veelen says the Price equation cannot give you on its own. He is
  right that it cannot; we added it.

**van Veelen's own condition, checked against our design.** He says the regression
coefficient is meaningful when fitness is linear in `p` and `p` is uncorrelated with
any other variable affecting fitness. Translated: the judge's selection probability
should be linear in the value score, and the value score should not be correlated with
anything else the judge responds to. **We already know one violation and have measured
it**: in the randomized instrument, the spread arm's kept answers run +3.1 characters
longer than the concentrated arm's (paired t = 2.90, n = 127 rounds) — length is a
second variable the judge responds to, correlated with the arrangement. The ledger row
already names this as the exclusion threat and bounds it at roughly 2% of 152
characters, and prescribes a length-matched third arm. **That prescription is not an
internal housekeeping item; it is the answer to the single most-cited critique of the
Price equation, and the writeup should present it as such.** Everything else van Veelen
asks for — linearity of selection in the trait, and no correlated omitted selector — is
a list of specific, runnable checks rather than a reason not to use the framework.

**Verdict: the framing has no known fatal objection, but it has a known fatal
*presentation*.** If the writeup says "we applied the Price equation and found the
value obeys it", the critique lands and it is correct. If the writeup says "the Price
decomposition told us which two quantities to measure and randomize; here is the
randomized causal estimate of the transmission coefficient, and here is the
independently measured variance recursion that closes the system", there is no
objection left. The difference is entirely in what is claimed to have been *found*
versus what is claimed to have been *organized*.

---

## 5. Saturation: is `0.509 → 0.377 → 0.231` a named phenomenon?

**Yes — several times over, and the candidates make different predictions.** Below,
each named explanation with its functional form. Note that in every case the
literature's dependent variable is not identical to ours (we measure a *response per
unit selection differential*, they mostly measure a level), so these are candidate
laws to fit, not laws already fitted to us.

*Arithmetic on the three published numbers, for orientation only — this is arithmetic
on the values in the ledger row, not a new project result, and nothing here may go on
a summary surface without its own script, JSON and ledger row.* Successive ratios are
0.741 and 0.613, successive differences −0.132 and −0.146. A straight line
`c_t = 0.650 − 0.139 t` fits with R² = 0.9992 (residuals +0.002, −0.005, +0.002) and
crosses zero at round 4.68. A geometric decay `c_t = 0.509 · 0.674^{t−1}` fits at
R² = 0.978 with half-life 1.76 rounds. With three points and two parameters each,
this is weak evidence, but it leans linear, and the two have *substantively different
endpoints*: linear-to-zero gives a total cumulative response of 1.21 gap-units,
geometric-to-infinity gives 1.56.

1. **Bounded KL ball around the reference (Ferbach Theorem 2.4).**
   `D_KL(p_t ‖ p_ref) ≤ −log(1 − λ(K−1))` whenever `λ < 1/(K−1)`. Reward is bounded on
   a bounded KL ball, so gains must stop. Predicts saturation to a *ceiling that
   depends on the mixing fraction λ and on K*, and predicts no saturation at all in a
   pure self-consuming loop with unrestricted model class. Directly testable: our
   base-mixed and peer-mixed pools have different effective λ from our self-only pools.
2. **Verifier knowledge-center convergence (Yi et al.,
   [arXiv:2510.16657](https://arxiv.org/abs/2510.16657)).** Verifier-guided retraining
   drives parameters to the verifier's knowledge center; unless the verifier is
   perfectly reliable, "early gains will plateau and may even reverse". Predicts
   saturation **and then reversal**, with the plateau level set by judge reliability.
   This is the only candidate that predicts a sign change, which makes it the easiest
   to falsify: run to round 8.
3. **Reward-model overoptimization (Gao, Schulman & Hilton, *Scaling Laws for Reward
   Model Overoptimization*, [arXiv:2210.10760](https://arxiv.org/abs/2210.10760),
   ICML 2023).** With `d := √(D_KL(π ‖ π_init))`, the gold reward under best-of-n
   follows `R_bon(d) = d(α_bon − β_bon d)` and under RL follows
   `R_RL(d) = d(α_RL − β_RL log d)`; and `KL_bon = log n − (n−1)/n`. The BoN form's
   *marginal* return `dR/dd = α − 2βd` **declines linearly in d and crosses zero**.
   If our per-round KL increment is roughly constant, `d` grows roughly linearly in
   round and the per-round response coefficient should decline **linearly to zero** —
   which is the fit that wins above (R² = 0.9992, zero at round 4.68). For reference,
   `KL_bon` at n = 6 is 0.958 nats (d = 0.979) and at n = 3 (roughly our keep-2-of-6
   per slot) is 0.432 nats (d = 0.657). **This is my best guess at the right law, and
   the measurement that would confirm it is cheap: log per-round KL from the adapter.**
4. **Solver–verifier gap exhaustion (Sun, Liang, Zhang, Liu & Teng,
   [arXiv:2507.00075](https://arxiv.org/abs/2507.00075)).** Coupled dynamics
   `dU_s/dt = −αE(t)`, `dU_v/dt = −βE(t)` with `α > β` give
   `U_s(t) ≈ α′ e^{−k(α−β)t} + U_{s,∞}`, an exponential approach to a limit
   `U_{s,∞} = (α U_{v,0} − β U_{s,0} + α b/k)/(α − β)`, with their Corollary 3.1
   giving `∂U_{s,∞}/∂G₀ = −β/(α−β)` — **larger initial solver–verifier gap, higher
   final capability.** Fitted at R² > 0.9 on Phi and Llama models on MATH/GSM8k.
   This is the *geometric* hypothesis, and it predicts the response coefficient decays
   toward a nonzero floor rather than crossing zero.
5. **Sharpening and coverage limits (Huang, Block, Foster, Rohatgi, Zhang,
   Simchowitz, Ash & Krishnamurthy, *Self-Improvement in Language Models: The
   Sharpening Mechanism*, [arXiv:2412.01951](https://arxiv.org/abs/2412.01951)).**
   Self-improvement is re-cast as using the model as its own verifier to sharpen mass
   onto high-quality sequences; the SFT-based version is minimax optimal **whenever
   the initial model has sufficient coverage**, and the RLHF-based version escapes the
   coverage requirement via online exploration. The prediction for us: an SFT-only
   loop must saturate when coverage runs out — when the candidate pool stops
   containing anything better than what the organism already does. That is the
   project's "support thinning" observation
   (`docs/PLAN.md`: "movement decelerated as within-pool support thinned"; seed 707
   flat at 0.625 after support hit exactly zero) under a formal name.
6. **Classical selection limits (Robertson, *A theory of limits in artificial
   selection*, Proc. R. Soc. B 153:234–249 (1960),
   [doi:10.1098/rspb.1960.0099](https://royalsocietypublishing.org/doi/10.1098/rspb.1960.0099);
   [scanned PDF](https://gwern.net/doc/genetics/selection/artificial/1960-robertson.pdf)).**
   For additive genes of small effect, the total advance equals `2N_e` times the
   first-generation gain and half the total is reached in at most `1.4 N_e`
   generations. Our geometric half-life of 1.76 rounds would imply `N_e ≈ 1.25`, which
   is not a sensible effective population for a 6-candidate pool — a mild argument
   *against* the drift-and-fixation reading of our saturation, though the mapping from
   "candidates per prompt" to `N_e` is not obvious enough for me to lean on it.
7. **The Bulmer effect** (selection generates negative linkage disequilibrium, cutting
   genetic variance and hence heritability, before recombination restores equilibrium
   after 3–4 generations). Typical reported reductions in genetic variance are **5–20%**
   before stabilizing — see e.g. the treatment in
   [PLOS Genetics 2024, doi:10.1371/journal.pgen.1012035](https://journals.plos.org/plosgenetics/article?id=10.1371%2Fjournal.pgen.1012035).
   Our decay is 55% over three rounds and does not stabilize. **So the Bulmer effect
   is the wrong magnitude and the wrong shape**; this is a named candidate we can
   already rule out, which is worth saying.
8. **Idempotence of iterative fine-tuning (Roe, Sanderson, Nguyen, Huang, Nief,
   Shrivastava, Tan & Holtzman, *Iterative Finetuning is Mostly Idempotent*,
   [arXiv:2605.01130](https://arxiv.org/abs/2605.01130), May 2026).** See §6 — this is
   both a saturation explanation and the sharpest threat to the project.

---

## 6. What pre-empts or refutes us

### 6.1 The biggest one: Roe et al., *Iterative Finetuning is Mostly Idempotent*

[arXiv:2605.01130](https://arxiv.org/abs/2605.01130). Seven seeded traits (bliss,
misalignment, hopelessness, lucky, sycophancy, "NVIDIA bear", misanthropy) across
Qwen3-4B-Instruct, Qwen3-32B, Llama-3.2-1B, Llama-3.2-3B and Llama-3.3-70B-Instruct;
three regimes — SFT on instruct models, synthetic document fine-tuning on base models,
DPO. Their headline: **in SFT and SDF, traits mostly decay or stay constant, so further
cycles do nothing**; amplification, when it happens, generally costs coherence
(12 of 270 SDF trials amplified, 4.4%, under their criterion `max_{j≥4} Δ_j ≥ 15` on
a 100-point scale); adding two seed examples (24 → 26) flipped one trait from
amplification to decay. **In DPO, amplification is reliable when the model is
continually trained on a preference for its own outputs, and vanishes when the model
is reinitialized from base each cycle.** Their conclusion: amplification comes from
*continual* post-training.

Why this matters so much to us:

- **Same organism.** Qwen3-4B-Instruct is our organism. If their SFT arm is idempotent
  and ours moves, the difference must be the thing we added — the judge. That is
  actually a *gift*: their SFT arm is a large, independent, published measurement of
  our `ρ = 0` null on the same base model, and it says no movement. Our movement is
  therefore attributable to selection, not to SFT drift, with external corroboration.
- **But it is also a threat**, in two ways. First, if a reader believes "SFT on your
  own outputs does nothing", they will suspect our value movement is a measurement
  artifact until we show the matched no-selection arm. We have that arm (16
  random-selection rounds, mean drift 0.0000) and it should be promoted next to the
  headline, not buried. Second, their continual-versus-reinitialized DPO contrast is
  the *same experiment* I propose in §7 as the discriminator between selection
  dynamics and prior convergence — they got there first, in DPO. Our version would be
  the SFT-plus-selection version, which is genuinely different, but the framing is no
  longer novel and we should cite them rather than claim it.

### 6.2 Priority on the framing

Guo, Wu & Yiu ([arXiv:2605.23054](https://arxiv.org/abs/2605.23054)) already published
"model collapse is cultural evolution / iterated learning" with a 10-generation,
two-model, three-language test and explicitly labelled discriminative predictions.
Ren et al. ([arXiv:2404.04286](https://arxiv.org/abs/2404.04286)) already published
"LLM self-evolution is Bayesian iterated learning, and it amplifies priors". Ferbach
et al. already published "curated self-consuming loops implicitly optimize the reward
and provably converge to its maximizer". **The framing is taken.** What I could not
find, after targeted searching, is *anyone* reporting a measured response-per-unit-
selection-differential — a heritability, a transmission coefficient — for an LLM
self-training loop, let alone a causally identified one from a randomized instrument.
That is the contribution, and the review found nothing that pre-empts it.

### 6.3 The tautology critique

Handled in §4.2. Short version: it lands on `gap ≈ ρσ` and does not reach the
instrumented 0.754.

### 6.4 A threat nobody has written down that I think is real

Our judge is the *frozen base model of the same organism*. Ferbach's `r` is a fixed
external reward. Every convergence theorem in §1 assumes a fixed `r`. In our
self-judge arms the judge co-evolves with the policy, so the reward is
`r_t`, and none of Theorems 2.1–2.4 apply — the system is a co-evolutionary one, and
Ferbach's `p*` is not even well-defined. The frozen-judge arms are in scope; the
self-judge arms are not. The repo's own finding that self-judge runs are bimodal
across seeds while frozen-judge runs decay deterministically
(`docs/reports/lit_review_value_dynamics.md`, finding 2) is exactly what you would
expect from that distinction, and I have not seen it stated as a scope boundary
anywhere in the repo. It should be.

---

## 7. Measurements our existing corpus could make that discriminate between theories

These need **no new GPU time** — they are re-analyses of the committed 340/367-round
tables — unless marked.

1. **Does the endpoint depend on the initial condition?** Prior-convergence (Ren et
   al. Proposition 1: converged hypothesis "irrelevant to selection of `d⁰`") says no;
   Ferbach's `p* = p₀|_{r=r*}` says **yes, through the initial support**; the linear
   attractor model (Perez et al.) says the endpoint is `I/(1−s)` regardless of start.
   Regress round-4 value on round-0 value *at matched judge and matched round-1 gap*.
   Our existing forecast result (MAE 0.118 from round-1 measurements versus 0.431 for
   no-change) already leans toward Ferbach; the matched-judge version turns it into a
   clean discriminator.
2. **Fit the three saturation laws to the per-round response coefficient, with more
   than three points.** Linear-in-round (Gao BoN marginal), geometric-to-a-floor
   (Sun et al.), and plateau-then-reverse (Yi et al.). Estimate the coefficient
   per-round *per condition* rather than pooled, to get n well above 3, and report
   which law wins by held-out round. The current 3-point series cannot separate
   R² 0.999 from R² 0.978.
3. **Log per-round KL from the base adapter and test whether the response coefficient
   is linear in `√KL` rather than in round index.** This is the direct test of the
   Gao et al. functional form, and it converts "saturation" from a description into a
   law with a known shape. Needs a small amount of GPU to recompute log-probs on
   banked checkpoints — cheap, and possible on Colab.
4. **Separate coverage exhaustion from transmission decay.** Decompose the per-round
   response into `σ_t` (available material), `ρ_t` (judge sorting), and `h²_t`
   (response per unit differential). Sharpening theory (Huang et al.) predicts
   saturation shows up in `σ_t`; Ferbach's Theorem 2.4 predicts it shows up as a
   ceiling on cumulative movement with `h²` constant; a genuine transmission-fidelity
   decay would show up in `h²_t`. The ledger's 0.509/0.377/0.231 is a slope of
   response on gap, so it is already the `h²_t` series — but it needs the matched
   `σ_t` and `ρ_t` series next to it to be interpretable, and I do not believe those
   have been reported round-by-round.
5. **Attractor-versus-selection at matched pool mean.** Already run twice and it is
   the decisive test against Perez et al.'s pure-attractor model (spread +0.406 /
   +0.368 versus concentrated +0.017 / +0.073). What is missing is the *fit*: fit
   `v_{t+1} = I + s·v_t` to our trajectories, report its held-out MAE, and show that
   our `h²·ρ·σ` closed form beats it. A linear attractor model with two free
   parameters is the honest baseline that our four-parameter law has to beat, and I do
   not think we have ever run it.
6. **Test the value-versus-reward distinction.** Ferbach predicts
   `v_∞ = E[v | r = r*]`, not `v_∞ = max v`. Take the frozen-judge runs, identify the
   judge's top-scoring answers in round-1 pools, and compute their mean value; compare
   against the observed round-4 endpoint. If endpoints track the judge's favourites'
   value rather than the value ceiling, that is a clean confirmation of a specific
   published theorem, and it explains interior stalls like seed 707 at 0.625.
7. **Check whether the random-selection arm shows prior convergence.** Griffiths &
   Kalish's theorem is the `ρ = 0` limit. Our 16 random-selection rounds gave mean
   drift 0.0000 (SD 0.186) — diffusion, not convergence to a base-model-shaped point.
   With only 16 rounds this is underpowered for the *variance* claim; count how many
   rounds we would need and say so.

---

## 8. Ranked next experiments

Compute assumptions: Kaggle 2×T4 quota resets Sat 2026-08-01 (~30 GPU-h/week, free,
no approval); Modal ~$75 grant plus $30/month free tier; models ≤ 8B; Colab free T4
available now. Nothing is on a GPU as of 2026-07-28.

**1. Reset-versus-continue (highest value, ~6 GPU-h, Kaggle, Aug 1).**
Run the standard 4-round loop twice from the same seed and the same judge, changing
exactly one thing: arm A continues fine-tuning from the previous round's adapter (our
current design); arm B discards the adapter each round and fine-tunes a *fresh* LoRA
from base on the same kept answers. Arm B is a Griffiths–Kalish-shaped chain — the
prior is re-applied every generation — and arm A is not. Predictions that differ:
prior convergence says B converges to a base-model-determined point independent of the
seed, and A does too but slower; selection dynamics say A accumulates and B does not;
Roe et al.'s DPO result says amplification lives in the continual arm and dies in the
reset arm. **This is the single experiment that most cleanly separates the two
literatures our project sits between, it directly extends Roe et al. from DPO to
SFT-with-selection, and it is cheap.** Log the per-round transmission coefficient in
both arms — the interesting outcome is if `h²` is unchanged and only the *accumulation*
differs.

**2. Run to round 8 under a frozen judge (~8 GPU-h, Kaggle).**
Three of the saturation laws in §5 make different predictions past round 4 and we have
never looked: Gao-BoN-marginal says the response coefficient crosses zero around round
5 and the value stops; Sun et al. says it decays to a nonzero floor and the value keeps
creeping; Yi et al. says it plateaus **and then reverses** because the verifier is
imperfect. Two seeds, one axis, frozen judge, 8 rounds, with `σ_t`, `ρ_t`, gap and
response logged every round. Nothing else on the list can distinguish these, and a
sign reversal would be the most striking result the project could produce.

**3. K-ladder at matched selection differential (~8 GPU-h, Kaggle).**
Ferbach's Lemma 2.2 puts an explicit `(K−1)/K` on the per-round reward gain, and
Theorem 2.4's KL ceiling `−log(1 − λ(K−1))` is explicitly K-dependent; Gao et al.'s
`KL_bon = log n − (n−1)/n` says the KL cost of selection grows like `log K`. Run
K ∈ {2, 4, 6, 12} keeping the same *fraction*, and — this is the part that makes it a
real test — hold the realized gap matched across arms by the knapsack arrangement, so
that K varies while the selection differential does not. If the transmission
coefficient is K-independent at matched gap, `h²` is a property of the training step
alone and the closed form `E[R] = h²ρσ` is vindicated as a factorization. If it rises
with K toward 1, the shortfall from 1.0 is a finite-pool effect and Lemma 2.2's factor
is doing real work.

**4. Judge-reliability ladder (~6 GPU-h, Kaggle or Modal).**
Yi et al.'s theory says the plateau level is set by verifier reliability and the
endpoint is the verifier's knowledge center. Construct three judges of known,
graded reliability against the value axis — the scripted oracle (ρ ≈ 1), the frozen
base model (ρ measured), and a deliberately noised oracle that flips its preference
with probability p ∈ {0.1, 0.25} — and measure both the plateau level and the endpoint.
Prediction to pre-register: plateau level should be monotone in reliability, and the
endpoint should track `E[v | judge's top answers]`, not the value ceiling. This also
gives us the `ρ` axis of the closed form as a *manipulated* variable rather than a
measured one, which we currently lack.

**5. The pure-attractor baseline, fitted (zero GPU, one afternoon).**
Fit Perez et al.'s `v_{t+1} = I + s·v_t` to all 340 rounds, report `s`, the implied
fixed point `I/(1−s)`, and held-out MAE by condition; then compare against the
`h²·ρ·σ` closed form on the same held-out split. Also fit a hybrid
`v_{t+1} = I + s·v_t + h²·ρσ` and report whether the attractor terms survive. We
should not publish a selection law without showing it beats the attractor law that the
LLM cultural-evolution literature would reach for first. **This is a re-analysis, it
needs a script under `scripts/`, a JSON in `experiments/`, and a ledger row.**

**6. Off-target attractor direction against human content biases (~4 GPU-h, Colab).**
Acerbi & Stubbersfield say LLM transmission chains inherit human content biases
(negativity, threat, social). Our off-target drift (corrigibility, optimism, risk) is
currently unexplained and seed-variable. Score the kept answers in existing banked
pools on the Acerbi–Stubbersfield content dimensions and test whether off-target drift
direction aligns with them. If it does, off-target drift stops being noise and becomes
a second, predictable attractor — and it connects our work to an existing PNAS result.
Lowest confidence of the six, but the cheapest surprise.

---

## 9. What I could not find, and what I could not read

**Could not find, after targeted search:**

- Any published estimate of a *response-to-selection coefficient*, heritability, or
  transmission coefficient for an LLM self-training loop. Searched for the
  quantitative-genetics vocabulary explicitly against LLM self-training; nothing.
  This appears to be genuinely open.
- Any explicit *selection-versus-attraction decomposition coefficient* in cultural
  attractor theory's own formalization. Claidière et al. (2014) give the impact-matrix
  form and say selection is attraction dominated by diagonal terms, but supply no
  coefficient separating them, and never mention the Price equation.
- Any treatment of iterated learning in which the learner is **not** re-instantiated
  each generation. Every formal treatment I found (Griffiths & Kalish, Ren et al.,
  Guo et al.) assumes a fresh learner per generation. The closest thing to an analysis
  of the continual case is Roe et al.'s empirical continual-versus-reinitialized
  contrast, which has no theory attached.
- Any analysis of curated self-consuming loops where the reward model **co-evolves**
  with the policy. Every theorem in §1 fixes `r`.

**Could not read (403, paywall, or PDF extraction failure) — flagged so nothing here
is cited as verified:** van Veelen (2005) and van Veelen et al. (2012) in the original
(ScienceDirect 403) — but his 2020 restatement is open access and I read it in full,
so the critique itself is first-hand; Okasha & Otsuka (2020) full text (Royal Society
403 — abstract only); Nettle (2020) full text (403); Kirby, Cornish & Smith (2008) and
Kirby et al. (2015) full texts (PNAS/Elsevier 403); Kirby, Dowman & Griffiths (2007)
full text (PNAS 403); Shumailov et al. (2024) Nature full text; Boyd & Richerson (1985)
recurrence equations. Where a claim above rests only on an abstract or a secondary
summary, the entry says so. **Before any of these goes into the writeup, it needs a
first-hand read.** The whole Phil. Trans. R. Soc. B theme issue *Fifty years of the
Price equation* (vol. 375, issue 1797, 2020) appears to be open access on PMC, so
Okasha & Otsuka (20190365) and Nettle (20190358) are probably reachable there on a
second attempt — I found the issue's other articles at PMC7133506, PMC7133507,
PMC7133513 and PMC7133514 but did not locate those two article IDs.

---

## 10. Documents this review says should change

Per the repo's claim-hygiene rules, corrections land in `docs/ANALYSIS_LEDGER.md`
first. The three this review generates:

1. **The transmission-coefficient row's theory context is slightly wrong about
   mechanism.** It attributes the idealized 1.0 to Lemma 2.1's `K → ∞` limit. The 1.0
   comes from perfect nonparametric fitting of the curated distribution (Equation 4
   with `λ → ∞` and `P = P(ℝ^d)`), which holds for any K; `K → ∞` sets the *size* of
   the tilt, not the transmission fidelity. The correction changes where we look for
   the missing 0.246 — at the model class and optimizer, i.e. Theorem 2.2, not at pool
   size. See §1.1.
2. **A scope boundary should be recorded: the self-judge arms are outside every
   convergence theorem in the self-consuming literature**, because those all fix the
   reward. Frozen-judge arms are in scope. See §6.4.
3. **Ferbach's Theorem 2.1 predicts `v_∞ = E_{p₀}[v | r = r*]`, not `v_∞ = max v`.**
   Interior stalls are predicted, not anomalous. See §1.1.

Figure-worthy, if the parent thread wants one after the §7.2 re-analysis lands: the
per-round response coefficient with the three candidate saturation laws overlaid
(linear-to-zero, geometric-to-floor, plateau-then-reverse), each labelled with its
source paper and its distinct out-of-sample prediction for rounds 5–8. It is worth
drafting only *after* the per-condition coefficient series in §7.2 exists — three
points cannot carry three curves.

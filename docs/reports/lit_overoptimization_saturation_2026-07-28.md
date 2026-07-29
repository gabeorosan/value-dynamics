# What the optimization-pressure literature says about repeated best-of-N distillation, and what functional form our saturation can actually support

*Literature review plus a theory recommendation, 2026-07-28. Written from the
primary sources: every equation below was read out of the paper's own text (PDF
or ar5iv full text), not from a search snippet or from memory. Numerical results
in §2.3 and §6 are computations done for this report; the code is inlined in
Appendix A so they are reproducible, and **they should be committed as
`scripts/analysis_selection_pressure_budget.py` before any of them is cited on a
summary surface** — they have no ledger row yet.*

*Two claims that this report contradicts, and which need ledger action, are
flagged inline: the third number in the per-round decay triple (§5.2) and the
reading of "levels off short of the rails" as evidence against the replicator
model (§5.3).*

---

## 0. The short version

**Recommended functional form.** Do not fit a single curve of value against
cumulative selection pressure. Fit the multiplicative decomposition the loop
already measures,

&nbsp;&nbsp;&nbsp;&nbsp;`Δv_t  =  h²_t · ρ_t · σ_t`,  with  `σ_t = κ_t · √(v_t (1 − v_t))`

and ask which of the four factors carries the saturation. Here `Δv_t` is the
change in the held-out value score over round `t`; `σ_t` is the mean
within-prompt standard deviation of candidate value scores; `ρ_t` is the
within-prompt correlation between the judge's score and the value score;
`h²_t` is the regression slope of `Δv_t` on the selector gap `g_t = ρ_t σ_t`;
`v_t` is the value score at the start of round `t`; and `κ_t` is the ratio of
the realized candidate spread to the binomial ceiling `√(v(1−v))` that binary
scoring imposes. The four factors correspond to four different theories of
saturation, they are separately measurable from data already logged, and — as
§6 shows — two of them are separable at our sample size while one is not.

If a single scalar curve is required for the writeup, fit the **replicator /
breeder form with a free ceiling**: `Δv_t = h² · ρ · κ · √(v_t(1−v_t))`, holding
`h²` constant, and report the ceiling as the value at which `ρ` reaches zero
rather than as a rail. This is the form the repo's own
`report_population_genetics_unification.md` already validated (`h²` = 0.804 on
the risk axis, 0.831 restricted to the interior), it is what
[Ferbach et al.](https://arxiv.org/abs/2407.09499) prove for exactly this
curation loop, and it needs no parameter that our data cannot estimate.

**Identification verdict.** Pessimistic. With four rounds and roughly a dozen
independent seed clusters:

- Gao's concave form and the headroom form are *both* estimable and, in
  simulation, model comparison points the right way — but the margin is weak
  (median ΔAIC ≈ +8 at 11 clusters, decisive in only 38% of draws; §6.3).
- The decay of the transmission coefficient `h²` across rounds — the one
  parameter that would distinguish Gao-style overoptimization from every other
  story — is **not resolvable**: simulated standard error per round-wise slope
  is 0.21 at 11 clusters, against an observed round-1-minus-round-3 difference
  of about 0.20, i.e. `t ≈ 0.7`. Roughly 40 independent clusters are needed for
  80% power (§6.2).
- A process with genuinely constant transmission produces a *monotonically
  declining* sequence of round-wise slopes 72% of the time, purely from
  clipping at the 0–1 boundary (§6.2). The direction of the observed decay is
  therefore close to uninformative on its own.
- Worse, the per-round decay claim itself does not fully reproduce (§5.2): the
  third number is wrong, and the decay largely disappears under two innocuous
  reparameterizations.

**The confound the task asked about — replicator rails versus cumulative
pressure — is not resolved by "the runs level off short of the rails."** That
observation refutes only the naive logistic model written in the *value*
coordinate. The correct replicator model, written in the *judge's* coordinate,
predicts leveling off short of the value rails as a theorem
([Ferbach et al., Theorem 2.1](https://arxiv.org/abs/2407.09499)), because the
loop converges to the top level set of the *judge's* reward reachable from the
initial support, and the value axis is only `ρ`-correlated with that. §5.3
quantifies how little the observation buys. The measurement that *does*
separate them is the proxy-minus-gold divergence plot (§5.4) — cheap, and the
repo already has the machinery.

---

## 1. Gao, Schulman and Hilton — the reference result, stated exactly

**Paper:** Leo Gao, John Schulman, Jacob Hilton, "Scaling Laws for Reward Model
Overoptimization", [arXiv:2210.10760](https://arxiv.org/abs/2210.10760),
19 October 2022; published at ICML 2023
([PMLR v202](https://proceedings.mlr.press/v202/gao23h.html)).

### 1.1 The distance variable

They do **not** parameterize by KL. Quoting §1 directly:

> "because it is a quadratic metric of distance [Bai et al., 2022, Section 4.3],
> we will define `d := √D_KL(π ‖ π_init)`, and write our functional forms in
> terms of `d`."

So `d` is the **square root of the KL divergence in nats** between the optimized
policy `π` and the initial policy `π_init`. Every x-axis in their figures is on a
square-root scale. This matters for us: a form that is quadratic in `d` is
*linear in KL*, and a claim about "concavity" is a claim about concavity in
`√KL`, not in KL.

### 1.2 The two fitted forms

Verbatim from the paper:

> for best-of-n (BoN) sampling, `R_bon(d) = d (α_bon − β_bon d)`,
> and for reinforcement learning, `R_RL(d) = d (α_RL − β_RL log d)`.

with `R(0) := 0` by definition. `R` is the **gold** reward model score (the
ground-truth stand-in), recentered so the initial policy scores 0 and variance
normalized. `α` and `β` are fitted parameters that depend on proxy reward model
parameter count, proxy reward model dataset size, and so on.

Note what these forms are and are not:

- The best-of-n form `d(α − βd) = αd − βd²` is, substituting `d² = KL`,
  equal to `α√KL − β·KL`. It rises like the square root of KL and is pulled
  down linearly in KL. Its maximum is at `d* = α_bon / (2β_bon)`, with peak
  height `α_bon² / (4β_bon)`. (Their Figure 12 caption reads "Max BoN gold
  scores (α_bon/2β_bon)", which is the *location* of the maximum rather than
  its height — read the caption as labelling the closed-form prediction, and use
  `α²/4β` for the height.)
- The RL form `d(α − β log d)` has **infinite slope at the origin**, which they
  flag in footnote 1 as a known defect: "this form likely does not hold near the
  origin." Appendix B lists the alternatives they rejected: `d(α − β log(1+d))`
  ("substantially worse extrapolation behavior") and power laws
  `d(α − β d^γ)` ("adds another degree of freedom, and the best fits resulted in
  small values of γ"), noting that small `γ` approximates the log form because
  `lim_{n→∞} n(x^{1/n} − 1) = log x`. Its maximum is at
  `d* = exp(α_RL/β_RL − 1)`, with height `β_RL · exp(α_RL/β_RL − 1)`.
- The **proxy** score has no good fit. §3.1: "We also attempted to model the
  proxy scores but were unable to obtain a satisfactory fit. For BoN, despite
  visual similarity, a linear fit (`d α_bon`) did not work well." Both proxy
  curves "appear to eventually grow roughly linearly in √KL".

The best-of-n form was a genuine advance prediction: hypothesized on data up to
`n = 1,000` (KL ≈ 6 nats) and then confirmed at `n = 60,000` (KL ≈ 10 nats).

### 1.3 How `d` is computed for best-of-n, and why that matters here

§2, verbatim: "The KL distances for BoN are computed analytically:
`KL_bon = log n − (n−1)/n`" (attributed to Stiennon et al., 2020, Appendix G.3).

This is the closed form for the distribution of the *maximum* of `n` independent
draws when the score is continuous, derived in quantile space: if `u = F(score)`
is uniform, the maximum of `n` has density `n u^{n−1}`, and
`∫₀¹ n u^{n−1} log(n u^{n−1}) du = log n − (n−1)/n`.

Two consequences for us. First, the number is **a property of the selection
rule, not of the run** — it depends only on `n`. Second, it is an *upper bound*,
not the truth, once the score has ties or the output space is discrete: see §1.5.

### 1.4 Coefficient scaling, and the iterated-RLHF corollary

The `α` and `β` coefficients "vary smoothly with the number of proxy reward
model parameters, following approximate logarithmic trends," with `α_RL`
approximately independent of reward model size, so `β_RL` alone carries the
scaling. Larger policies gain less from optimization but "both gold scores peak
at almost the same KL" — overoptimization onset is policy-size independent in
their setup.

§4.3 is the part of the paper closest to our design. Under two assumptions —
that the coefficients stay constant across iterations, and that
`d = √KL` is **additive** across iterations — the gold score after `k`
iterations each covering distance `d/k` is

&nbsp;&nbsp;&nbsp;&nbsp;`R_RL(d) = d (α_RL − β_RL log d + β_RL log k)`,

so iterating buys `β_RL · d · log k` of extra gold score, and does nothing to
the `α` term (the regressional-Goodhart part). They caution this "can only hold
up to some maximum value of `k`."

**This is the one place where I think the paper's assumption should not be
carried over to our loop.** Their `d`-additivity was an empirical observation
about PPO, where KL grows roughly quadratically in step count. For repeated
best-of-n with distillation, the composition is exactly computable and gives
**KL-additivity, not `d`-additivity** — see §2.3. The difference changes the
cumulative pressure after four rounds by a factor of about 2.5 in `d`, which is
the difference between "we are nowhere near the peak" and "we might be at it."

### 1.5 The KL formula is an upper bound, and for a binary axis a very loose one

**Paper:** Ahmad Beirami, Alekh Agarwal, Jonathan Berant, Alexander D'Amour,
Jacob Eisenstein, Chirag Nagpal, Ananda Theertha Suresh, "Theoretical guarantees
on the best-of-n alignment policy",
[arXiv:2401.01879](https://arxiv.org/abs/2401.01879) (ICML 2025).

Their Theorem 3.1: for any `n` and any prompt `x`,
`D_KL(π^(n)(·|x) ‖ π_ref(·|x)) ≤ log n − (n−1)/n`. The commonly used formula is
an **upper bound**, exact only when the reward induces a non-atomic (tie-free)
distribution.

Their Example 1 is our situation almost exactly. Take a binary output
`y ∈ {0,1}` with `π_ref(0) = π_ref(1) = ½` and `r(1) > r(0)`. Then
`π^(n)(0) = 2^{−n}` and

&nbsp;&nbsp;&nbsp;&nbsp;`D_KL(π^(n) ‖ π_ref) = log 2 − h(2^{−n})`

where `h` is the binary entropy function. The true divergence is **bounded by
`log 2 ≈ 0.693` nats for every `n`**, while `log n − (n−1)/n` grows without
bound. They also show the win rate of the best-of-n policy against the reference
is at most `n/(n+1)` — for our `n = 6`, at most 6/7 ≈ 0.857.

Our value axis is scored 0/1 per candidate (the repo's own standing note that
binary scoring is the binding constraint). By the data-processing inequality the
KL of the *value marginal* is at most the KL of the full policy, and Beirami's
example caps it further at `log(1/q₀)` where `q₀` is the base rate of the
high-value label — `0.693` nats at `q₀ = 0.5`. Against the roughly 3.8 nats of
total policy KL the four-round loop can spend (§2.3), **at most about a fifth of
the KL budget can be value-axis movement even under a perfect judge.** That is a
saturation prediction which follows from the scoring format alone, before any
dynamics.

### 1.6 The same forms transfer to direct alignment algorithms

**Paper:** Rafael Rafailov, Yaswanth Chittepu, Ryan Park, Harshit Sikchi, Joey
Hejna, Bradley Knox, Chelsea Finn, Scott Niekum, "Scaling Laws for Reward Model
Overoptimization in Direct Alignment Algorithms",
[arXiv:2406.02900](https://arxiv.org/abs/2406.02900) (NeurIPS 2024).

They reuse Gao's RL form, `R(d) = d(α − β log d)` with `d = √D_KL(π‖π_ref)`,
substituting GPT-4 win rates for reward model scores, and report that it "halves
the RMSE" relative to a quadratic fit. All three objectives they test (DPO, IPO,
SLiC) show the hump-shaped, non-monotone pattern. The relevant lesson for us is
robustness: the same functional family survives a change of optimizer *and* a
change of outcome metric from a scalar reward model to a judge win rate. It is
not an artifact of PPO.

I could **not** find published fitted values of `α` and `β` in either paper's
main text, so I cannot tell you numerically where our loop would sit relative to
their peaks. Both papers report the coefficients only as figures.

---

## 2. Where our loop actually sits on Gao's axis

### 2.1 The selection rule, in Gao's units

Our per-round operation is: draw 6 candidates per prompt, keep the best 2 by
pairwise judge comparison, fine-tune on the kept 2. In quantile space, "keep the
top 2 of 6 and treat them as equally weighted training targets" has density

&nbsp;&nbsp;&nbsp;&nbsp;`g(u) = (1/k) Σ_{j=1}^{k} [n! / ((j−1)!(n−j)!)] · u^{n−j} (1−u)^{j−1}`

with `n = 6`, `k = 2` — the average of the densities of the top `k` order
statistics of `n` uniforms. Integrating `∫ g log g`:

| selection rule | KL from base (nats) | `d = √KL` |
|---|---:|---:|
| best-of-2 | 0.193 | 0.440 |
| best-of-3 | 0.432 | 0.657 |
| **top-2-of-6 (ours)** | **0.595** | **0.772** |
| best-of-6 | 0.958 | 0.979 |
| top-3-of-6 | 0.356 | 0.597 |
| best-of-60 | 3.111 | 1.764 |

Keeping 2 rather than 1 costs about 38% of the per-round KL relative to
best-of-6. One round of our rule is worth roughly a best-of-3.8 in KL.

### 2.2 The mean kept quantile

`E[u | top-2-of-6] = 11/14 = 0.7857`, exactly. The judge, if it ranks perfectly
on its own axis, pulls the training distribution to the 79th percentile of the
candidate pool each round. Multiply by `ρ` to get the movement projected onto
the value axis — this is the `ρσ` factorization, restated in quantile units.

### 2.3 Cumulative pressure over four rounds: KL adds, `d` does not

Under perfect distillation, round `t+1` selects from the round-`t` distribution,
so the cumulative quantile map is the `t`-fold composition `G^{∘t}`. Composing
numerically (Appendix A):

| round | cumulative `D_KL(π_t ‖ π_0)`, nats | `d = √KL` | per-round increment |
|---:|---:|---:|---:|
| 1 | 0.595 | 0.772 | 0.595 |
| 2 | 1.620 | 1.273 | 1.025 |
| 3 | 2.709 | 1.646 | 1.089 |
| 4 | **3.807** | **1.951** | 1.098 |
| 5 | 4.905 | 2.215 | 1.099 |

The per-round increment converges to `log(n/k) = log 3 = 1.0986` nats. So
**cumulative KL grows linearly in the round index and `d` grows like `√t`** —
the opposite of Gao's §4.3 additivity-in-`d` assumption, which would give
`d = 4 × 0.772 = 3.09` after four rounds against the correct 1.95. Their
assumption was an empirical PPO observation and does not carry over to repeated
selection.

Three caveats, all in the same direction:

1. Real distillation undershoots — SFT on two kept answers with a LoRA for a
   fixed number of steps does not reproduce the selection distribution. So 3.807
   nats is an **upper bound** on the realized cumulative KL.
2. The computation assumes a tie-free continuous judge ranking. Ties push it
   down further (§1.5).
3. It assumes the judge ranks on one fixed axis across rounds. If the judge's
   effective criterion drifts, some of the KL is spent re-crossing ground.

**Calibration.** 3.807 nats is what a single best-of-121 would spend. Gao's
best-of-n experiments run to KL ≈ 10 nats (`n = 60,000`). Four rounds of our
loop therefore sit at roughly the 38th percentile of his measured KL range on
the linear scale, and at `d = 1.95` against his axis running to `d ≈ 3.16`.
Whether that is before or after the gold-score peak depends on `α_bon/2β_bon`,
which I could not extract numerically. But since the realized KL is strictly
below 3.807 and probably well below, **the prior should be that our loop has not
reached Gao's turnover point**, and that whatever is flattening our trajectories
is not the `β_bon` term.

---

## 3. Sharpening theory: a ceiling, not a curve

**Paper:** Audrey Huang, Adam Block, Dylan J. Foster, Dhruv Rohatgi, Cyril
Zhang, Max Simchowitz, Jordan T. Ash, Akshay Krishnamurthy, "Self-Improvement in
Language Models: The Sharpening Mechanism",
[arXiv:2412.01951](https://arxiv.org/abs/2412.01951), 2 December 2024
(ICLR 2025).

**Does sharpening theory predict a saturation like ours? Yes, but as a fixed
point, and it gives no functional form for the approach.**

The framework. Self-improvement is modelled as tilting a base policy toward
responses it scores highly under a self-reward `r_self(y|x; π_base)`. Their
stylized choice is the sequence log-probability, `r_self(y|x) := log π_base(y|x)`
(their Eq. 2). The target is

&nbsp;&nbsp;&nbsp;&nbsp;`π̂(x) ≈ arg max_{y ∈ Y} r_self(y | x; π_base)`   (their Eq. 1)

and success is graded by Definition 3.1: `π̂` is `(ε, δ)`-sharpened relative to
`π_base` if `P_{x∼μ}[π̂(y*(x)|x) ≥ 1 − δ] ≥ 1 − ε`, where
`y*(x) := arg max_y log π_base(y|x)`.

Three things follow that matter for us.

**(a) The endpoint is a point, not an asymptote of a curve.** The sharpened
model is the one that puts its mass on the base model's arg-max response.
Once there, further rounds do nothing. This predicts a plateau — but the theory
says nothing about the shape of the approach, because it is a *sample
complexity* theory, not a dynamics theory.

**(b) The binding resource is coverage, not optimization pressure.** Their
fundamental limit (Theorem 3.1) is stated in terms of the coverage coefficient

&nbsp;&nbsp;&nbsp;&nbsp;`C_cov = E_{x∼μ}[ 1 / π_base(y*(x) | x) ]`

— the expected reciprocal probability that the base model assigns to the
arg-max response. Any algorithm in their sample-and-evaluate framework needs
`m ≳ C_cov log|Π| / (ε² (1 + log(Cε^{-1})))` total samples. Their Theorem 4.1
shows SFT-based sharpening matches this up to `δ` and log factors, with
`m = O(C_cov log(|Π|ρ^{-1}) log(δ^{-1}) / (δ ε²))`; Theorem 4.2 and Theorem 4.3
show that an RLHF-based variant with online exploration replaces `C_cov` by a
sequential extrapolation coefficient, escaping the coverage dependence.

**(c) The theory is single-shot.** Sharpening is defined *relative to a fixed
`π_base`*. There is no multi-round version in the paper, so it offers no
prediction for how the loop behaves once `π_base` is itself replaced each round.
That is a real gap between this theory and our design, and I did not find it
filled anywhere.

**Applicability caveat.** Our selector is an external judge on a value axis, not
`log π_base`. The mechanism transfers structurally — the reachable endpoint is
capped by what the base policy's support contains — but the specific
`C_cov`-scaling results are about likelihood sharpening and should not be quoted
as if they applied to judge-driven selection.

---

## 4. The closest empirical precedent: the generation–verification gap collapses in two to three rounds

**Paper:** Yuda Song, Hanlin Zhang, Carson Eisenach, Sham M. Kakade, Dean
Foster, Udaya Ghai, "Mind the Gap: Examining the Self-Improvement Capabilities
of Large Language Models",
[arXiv:2412.02674](https://arxiv.org/abs/2412.02674) (ICLR 2025).

Their central quantity is our selector gap under another name. Definition 2.1:

&nbsp;&nbsp;&nbsp;&nbsp;`gap(f, g) := J(f[w(û_g)]) − J(f)`

— the utility of the verifier-reweighted generator minus the utility of the
generator. With `f = g` (self-verification) this is exactly
`kept_mean − pool_mean`. Definition 2.2 normalizes by remaining headroom:

&nbsp;&nbsp;&nbsp;&nbsp;`gap_rel(f,g) := E_x[ (E_{y∼f[w]}[u] − E_{y∼f}[u]) / (U_max − E_{y∼f}[u]) ]`

which is a *headroom-normalized* gap — the same reparameterization I recommend
against fitting blind in §5.

Their iterative findings (§5, Qwen-1.5 at 7B / 14B / 32B / 72B on GSM8K, four
rounds, chain-of-thought binary verification, both rejection sampling and RL
updates), quoting the takeaway list:

> "i) GV-Gap saturates to 0 in handful rounds of iterative self-improvement;
> ii) the saturation rate is independent from the model capacity, iii) the
> effective diversity degrades during the iterative self-improvement."

Specifically the gap "diminishes nearly to zero within two or three rounds",
and with multiple-choice verification "the gap immediately drops to near 0 after
the first round". Diversity is measured by pass@k: for small `k`, pass@k rises
with rounds; for large `k`, pass@k **falls** with rounds. They replicate on MATH.

This is the single most directly comparable result to ours, and it is important
that **the thing that collapses is the gap `g` itself, not the response
coefficient.** In their runs, saturation arrives through the `σ`/diversity
channel — the pool stops containing rankable material — which is the coverage
story of §3, not the overoptimization story of §1. Their "saturation rate is
independent of model capacity" also argues against a reward-model-robustness
explanation, since in Gao's setup `β` scales with model size.

---

## 5. The replicator side, and how much "short of the rails" really tells us

### 5.1 Curation loops provably are replicator dynamics, with an explicit ceiling

**Paper:** Damien Ferbach, Quentin Bertrand, Avishek Joey Bose, Gauthier Gidel,
"Self-Consuming Generative Models with Curated Data Provably Optimize Human
Preferences", [arXiv:2407.09499](https://arxiv.org/abs/2407.09499)
(NeurIPS 2024). This is the paper the ledger already cites for the idealized
coefficient of 1.0; it says considerably more than that.

For a loop that draws `K` samples, keeps the reward-preferred one, and refits by
maximum likelihood, they derive the **exact** update (their Eq. 6):

&nbsp;&nbsp;&nbsp;&nbsp;`p_{t+1}(x) = p_t(x) · H^K_{p_t}(x)`, with
`H^K_{p_t}(x) := E_{x_1..x_{K−1}∼p_t}[ K e^{r(x)} / (e^{r(x)} + Σ_i e^{r(x_i)}) ]`

and `H^K ∈ (0, K)`, so "small values of `K` act as a regularization which
prevents the density from blowing up too much in high reward areas."

**Lemma 2.1** (`K → ∞`): `p_{t+1}(x) → p_t(x) e^{r(x)} / E_{p_t}[e^{r}]`. This
is the discrete replicator equation. Composed over `t` rounds it gives
`p_t ∝ p_0 e^{t·r}`, i.e. **iterating curation for `t` rounds is RLHF with
regularization strength `β = 1/t`** from the initial distribution. Optimization
pressure therefore accumulates *linearly in the round index* on the
exponential-tilt scale — consistent with the KL-additivity I computed in §2.3.

**Lemma 2.2** is the breeder's equation in their notation:

&nbsp;&nbsp;&nbsp;&nbsp;`E_{p_{t+1}}[e^{r}] ≥ E_{p_t}[e^{r}] + ((K−1)/K) · Var_{p_t}[e^{r}] / e^{r*}`

— "the expected reward increases proportionally to its variance at each
retraining iteration." And `Var_{p_t}[e^r] → 0`, so the process must stall.

**Theorem 2.1** names the stalling point: `D_KL(p* ‖ p_t) → 0` where
`p*(x) := p_0(x)·1{r(x) = r*} / P_0(r(x) = r*)` — the initial distribution
restricted to and renormalized on **the highest reward level set that the
initial distribution reaches**. In their words, the loop "converges to the
highest level set of the reward reached at initialization," and "the learned
distribution will lose diversity and collapse to the highest reward samples."

Theorems 2.2–2.4 handle mixtures with real data: with a positive fraction of
real data the loop is stable, the expected reward still increases, and the KL to
the initial distribution stays bounded.

### 5.2 Correction: the per-round decay triple does not reproduce

Before building any theory on the sequence `0.509 → 0.377 → 0.231`, it needs to
be said that an independent re-derivation from the raw
`experiments/spread_intervention/output_oracle/` plus `output_followups/`
artifacts, done for this report, **reproduces the first two numbers exactly and
does not reproduce the third**:

| round transition | n | slope on `gap`, with intercept | through origin | on `pull` instead |
|---|---:|---:|---:|---:|
| v₀→v₁ | 80 | **0.509** | 0.486 | 0.493 |
| v₁→v₂ | 80 | **0.377** | 0.397 | 0.418 |
| v₂→v₃ | 74 | **0.310** (claimed 0.231) | 0.339 | 0.412 |

Findings that bear directly on the functional-form question:

- **No committed script computes these numbers.** The triple appears only as
  prose in `docs/ANALYSIS_LEDGER.md` and an archived STATE log; the commit that
  introduced it (`1ace619`) touched three markdown files and no code or data.
  No standard error or confidence interval was ever computed for them —
  uniquely among the quantities in that ledger row, which carries a bootstrap
  interval for the instrumental-variables estimate right next to it.
- **They are rounds 1, 2, 3** (transitions v₀→v₁, v₁→v₂, v₂→v₃), not rounds
  2, 3, 4.
- **The decay is parameterization-specific.** Through the origin the sequence is
  0.486 / 0.397 / 0.339 — a 30% decline rather than 55%. Regressed on `pull`
  (`kept_mean − v_t`) instead of `gap` (`kept_mean − pool_mean`) it is
  0.493 / 0.418 / 0.412 — essentially flat after round 1.
- **Censoring lands exactly on the number in question.** Of 14 aborts
  ("candidates too value-uniform"), **13 occur at the round-2→3 boundary** —
  zero at rounds 1 and 2. The round-3 slope is therefore the first one computed
  on a censored panel, and the ledger's own note says aborted runs move faster
  than completed ones (+0.074 against +0.023 per round). The largest apparent
  drop in the sequence is measured on the survivors of a selection that removed
  the biggest movers.
- **Candidate spread does not shrink across rounds in this corpus**
  (0.172 → 0.187 → 0.186 pooled). But that corpus holds spread fixed by design —
  it is the concentrated-versus-spread intervention — so it cannot test the
  diversity-collapse channel at all. A different corpus is needed for that.

The reproduction recipe (pool the ten output files, de-duplicate on
`(group, arm, round, gap, v_prev, v_next)`, regress
`value_after_round − value_traj[r−1]` on `gap` with an intercept, split by round
index) should be committed as a script before any of these slopes is cited
again, and the ledger row should be corrected: **0.231 is not reproducible and
should be replaced with 0.310, with the censoring caveat attached.**

### 5.3 How informative is "the runs level off short of the rails"? Less than it looks

The task framed the contrast as: the replicator form saturates because
`q(1−q)` vanishes at the rails, whereas Gao-style overoptimization saturates
from cumulative pressure wherever the value sits — so leveling off short of the
rails favours Gao. That inference holds against one specific model and fails
against the right one.

**What it does refute.** The logistic written in the value coordinate,
`dv/dt = s · v(1−v)` with `s` constant and positive, has `v → 1` as its only
stable endpoint. Runs that stop at 0.33, 0.625 or 0.72 and stay there refute
that model. This is a real, if modest, result: it says the value axis is not
itself the axis under selection.

**What it does not refute.** The replicator model written in the *judge's*
coordinate. Ferbach's Theorem 2.1 says the fixed point is the top level set of
the judge's reward reachable from the initial support. The value at that fixed
point is whatever value the judge's favourite responses happen to have. Under
the factorization `g = ρσ`, if the judge's criterion is only `ρ`-correlated with
the value axis, then even a fully converged loop lands at a value strictly
inside `(0,1)` — and the shortfall is a function of `ρ` and of the base support,
not of accumulated pressure. **Leveling off short of the rails is a prediction
of the correct replicator model, not evidence against it.**

Quantitatively, the informativeness is close to zero for the following reason.
Both candidate explanations produce a plateau at an interior value; they differ
only in *which factor* goes to zero. The replicator/coverage story says the
plateau arrives when the within-pool value variance `σ` reaches zero (there is
nothing left to select on) or when `ρ` reaches zero (the judge stops
discriminating on the value axis). The overoptimization story says the plateau
arrives when `h²` — the response per unit of gap — reaches zero, while `σ` and
`ρ` remain positive. **Those are directly distinguishable observations, and the
value of the plateau is not one of them.** The repo already has the discriminating
observation in a different vocabulary: `report_oracle_saturation.md` logs flat
rounds as "MISSING-FORCE", meaning the pool offered the judge no choice — that
is `σ → 0`, the replicator/coverage endpoint, not `h² → 0`.

The one thing the plateau *would* discriminate is a **reversal**. Gao's `β` term
"in the limit of optimization, results in an unbounded loss of utility": the
gold score is predicted to turn around and fall. Ferbach's Lemma 2.2 makes the
reward monotonically non-decreasing. So: a run whose value rises, peaks, and
then falls *while the judge's own score keeps rising* is Gao; a run whose value
rises and flattens with the judge's score flattening too is replicator or
coverage. We observe flattening, not reversal. That is weak evidence against
being past a Gao peak — consistent with the KL calibration in §2.3 — and no
evidence at all about which of the other two mechanisms is operating.

### 5.4 The measurement that does separate them: Gao's proxy-versus-gold plot

Gao's §3.5 and his Figure 8 plot the proxy reward model score against the gold
score, and §3.4 interprets their difference as "the shortfall between predicted
and actual reward … indicative of the extent to which the proxy RM is
exploited." That plot is the diagnostic, and we can make it:

- **Proxy score** = the judge's own margin on the kept candidates, measured
  against a frozen reference (the repo already has frozen-judge rescoring and
  pool-rescoring machinery: `report_frozen_judge_rescore.md`,
  `report_pool_rescoring.md`).
- **Gold score** = the held-out value measurement `v_t`.

Then:

| observation | mechanism |
|---|---|
| proxy rises, gold flattens, gap between them widens with round | overoptimization (Gao `β`; extremal Goodhart) |
| proxy and gold flatten together, `σ → 0` | coverage / sharpening exhaustion (Ferbach Thm 2.1; Song et al. diversity collapse) |
| proxy and gold flatten together, `σ` healthy, `ρ → 0` | judge criterion decoupled from the value axis |
| gold turns down while proxy still rises | past the Gao peak — the alarming case |

**A widening proxy-minus-gold gap is the signature of overoptimization and
nothing else produces it.** This is the highest-value cheap measurement in this
report.

---

## 6. Identification: what four rounds and eleven clusters can support

### 6.1 The structural problem: Gao's `d` is collinear with the round index

Under a *fixed* selection rule — always 6 candidates, always keep 2 — the
nominal per-round KL is a constant (0.595 nats, §2.1) that does not vary across
runs. Cumulative KL is therefore `t × 0.595` and `d = √(0.595 t)`: both are
deterministic functions of the round index. **Any Gao-form fit in nominal `d` is
observationally identical to an arbitrary function of round number**, and
therefore indistinguishable from a time trend, a judge-drift artifact, or an
attrition artifact. This is not a power problem; it is non-identification.

Three ways out, in increasing order of cost:

1. **Use the realized gap as the pressure variable, not nominal KL.** The
   cumulative signed gap `P_t = Σ_{s≤t} g_s` varies across runs at fixed `t`.
   This is also closer to Gao's own advice: §4.1 says KL "should not be used to
   compare the amount of optimization between different optimization
   algorithms," and §3.5 finds the proxy score a better common currency.
2. **Measure the realized `D_KL(π_t ‖ π_0)` directly.** For a LoRA adapter this
   is a mean token-level log-probability difference on held-out prompts —
   cheap, one forward pass per checkpoint per prompt. It breaks the collinearity
   (different runs will have genuinely different realized KL at the same round),
   puts our x-axis in Gao's units so the curves are literally comparable, and
   settles the `d`-additivity-versus-KL-additivity question of §2.3 empirically.
   **This is the single measurement I would prioritize.**
3. **Vary `n` and `k` across arms.** An arm at top-1-of-6 (`d` = 0.979 per
   round) against top-2-of-6 (0.772) against top-3-of-6 (0.597) gives a
   64% spread in per-round `d` under experimenter control. The repo has done
   `K` sweeps before (`report_kselect_mini.md`, `report_kselect_v2.md`), and the
   v2 report's own diagnosis — a saturated 1-to-5 rubric meant selection had
   nothing to act on — is the failure mode to avoid.

### 6.2 Power for the decay of the transmission coefficient

Simulating the actual design (four rounds, `σ = 0.72√(v(1−v))` per the repo's
own measured relation, `ρ` drawn around 0.35, per-round residual standard
deviation on the value move of 0.11, matching the reported closed-form MAE of
0.093 converted to a normal scale), the likelihood-ratio test of a decaying
transmission coefficient `h² e^{−λ(t−1)}` against a constant `h²`, with the null
distribution calibrated by simulation so clustering is handled exactly:

| independent clusters | power to detect a decay from 0.80 to 0.36 | simulated SE of one round-wise slope |
|---:|---:|---:|
| 11 | **0.27** | 0.210 |
| 20 | 0.55 | 0.159 |
| 40 | 0.77 | 0.102 |
| 80 | 0.95 | 0.076 |
| 160 | 1.00 | 0.057 |
| 320 | 1.00 | 0.035 |

**Read the first row.** At our sample size the test has 27% power against a
decay as large as the one claimed. The observed round-1-minus-round-3 difference
(0.509 − 0.310 = 0.199, using the reproducible third number) against a
difference standard error of about `0.21 × √2 = 0.30` gives `t ≈ 0.67`. Even the
originally claimed difference of 0.278 gives `t ≈ 0.93`. **Roughly 40 clusters
are needed for 80% power**; 80 for a comfortable result.

**Effective-n matters more than nominal n here.** The re-derivation in §5.2
found `n` = 80 round-1 observations behind 35 distinct seed groups, with the two
arms of a group stepped in lockstep from a shared candidate pool. In simulation,
11 clusters of 7 rollouts each give a naive ordinary-least-squares standard
error of 0.090 against a cluster-bootstrap standard error of 0.075 to 0.104 —
so in this particular design the clustering penalty is modest, but it is the
*number of independent starts*, not the number of rollout rows, that sets it,
and no clustered standard error has ever been computed for these slopes.

**The direction of the decay is nearly uninformative on its own.** Under a
process with *genuinely constant* transmission, the simulated round-wise slopes
still fall — 0.813 → 0.785 → 0.754 → 0.728 on average — and the round-4 slope
is below the round-1 slope in **72% of draws**. The mechanism is clipping at the
0–1 boundary: as `v` approaches a rail, the realized move is truncated, which
attenuates the regression slope in later rounds. A monotone declining sequence
of three numbers is therefore close to what constant transmission looks like.

### 6.3 Which functional forms are actually distinguishable

Candidate forms, all written as a response to the round's measured gap `g_t`,
with `P_t = Σ_{s≤t} g_s` the cumulative signed gap and `v_t` the current value:

| label | form | free parameters |
|---|---|---:|
| linear | `Δv = h² g_t` | 1 |
| Gao concave | `Δv = g_t (α − β P_t)` | 2 |
| headroom | `Δv = c (v_∞ − v_t) g_t` | 2 |
| exponential approach | `Δv = h² g_t e^{−λ P_t}` | 2 |
| replicator | `Δv = h² ρ κ √(v_t(1−v_t))`, i.e. linear in `g_t` by construction | 1–2 |

Two structural remarks first.

**The replicator form is not a competitor to the others; it is already inside
them.** Because `g_t = ρ_t σ_t` and `σ_t = κ_t √(v_t(1−v_t))`, regressing `Δv`
on the *measured* gap has already absorbed the entire replicator channel into
the regressor. The replicator hypothesis makes a prediction about `g_t` (that it
tracks `√(v(1−v))` with a constant of proportionality), not about the slope.
Testing it means testing whether `g_t / √(v_t(1−v_t))` is constant across
rounds — a different regression, on a different quantity, with much better
statistical properties because it does not involve the noisy response at all.

**Gao and headroom key off different regressors and are separable — but only
because starting values differ across runs.** If `Δv = h² g` held exactly, then
`v_t = v_0 + h² P_t` and the two forms would be algebraically identical with
`α = c(v_∞ − v_0)` and `β = c h²`. They are separated by the fact that `v_0`
varies across runs and that the realized path departs from `h² P_t` through
noise. In simulation the correlation between `v_t` and `P_t` is about 0.5 and
the separation survives:

| clusters | measurement error on `v` | median ΔAIC favouring the true form | picks the true form | decisive (ΔAIC > 10) |
|---:|---:|---:|---:|---:|
| 11 | 0.00 | +7.7 (Gao true) / +24.1 (headroom true) | 0.96 / 1.00 | 0.38 / 0.96 |
| 11 | 0.10 | +8.3 / +14.3 | 0.95 / 0.97 | 0.42 / 0.71 |
| 40 | 0.03 | +30.9 / +84.4 | 1.00 / 1.00 | 0.97 / 1.00 |
| 160 | 0.03 | +129 / +336 | 1.00 / 1.00 | 1.00 / 1.00 |

Read this carefully and do not over-read it. The comparison points the right way
almost always, but at 11 clusters the evidence is **decisive in only 38% of
draws when Gao is true**. "The Gao form fits slightly better" at our sample size
is a preference, not a result. It also depends on the two forms having been
calibrated to produce similar trajectories, which is the fair comparison; if
they are left uncalibrated the simulation flatters the discrimination.

**Recommended test statistic and sample size.** For the one comparison that
matters — constant transmission against decaying transmission — use the
likelihood-ratio statistic `Λ = N log(RSS_constant / RSS_decay)` on the
round-level panel, with `RSS_decay` minimized over `λ` on a grid, and calibrate
the critical value by **cluster bootstrap over seed groups** rather than against
a `χ²₁` (the `λ` grid search and the within-run dependence both break the
asymptotic calibration). At 11 clusters the simulated 95th percentile of `Λ`
under the null is about 4.8, rising to about 5.4 at 80 clusters. Target **40
independent seed clusters** for 80% power, **80** for 95%.

### 6.4 What to do instead of fitting one curve

The decomposition `Δv_t = h²_t · ρ_t · κ_t · √(v_t(1−v_t))` puts each theory on
its own readout, and the readouts have very different statistical properties:

| readout | how to compute | theory it tests | separable at 11 clusters? |
|---|---|---|---|
| `κ_t = σ_t / √(v_t(1−v_t))` | already logged; `σ` is mean within-prompt SD, `v` is the round-start value | sharpening / diversity collapse (Song et al., Ferbach Thm 2.1) | **yes** — simulated 0.255 → 0.098 under a true 30%-per-round collapse, flat otherwise |
| `ρ_t = g_t / σ_t` | already logged | judge decoupling from the value axis (extremal Goodhart) | **yes**, same construction |
| `h²_t` = slope of `Δv_t` on `g_t` | round-wise regression | Gao overoptimization | **no** — SE 0.21, 27% power, 72% false-decay rate |
| proxy-minus-gold divergence | frozen-judge rescore of kept candidates against held-out `v_t` | overoptimization, uniquely | untested, but it is a *difference of levels* rather than a slope, so much better behaved |

The first two are means of ratios of already-logged quantities, estimated at
`n` = 80 per round; the third is a regression slope estimated from a noisy
response. That asymmetry is why the recommendation is to move the saturation
question off the coefficient and onto the components.

---

## 7. Goodhart taxonomies: what is quantitative and what is not

**Paper:** David Manheim, Scott Garrabrant, "Categorizing Variants of Goodhart's
Law", [arXiv:1803.04585](https://arxiv.org/abs/1803.04585).

Honest assessment: **this paper is a taxonomy, not a quantitative theory.** It
gives four categories with toy generative models, and only the first carries a
usable formula.

- **Regressional.** Model: `M = G + normal(μ, σ²)`, where `M` is the measured
  proxy and `G` the goal. Selecting on `M > c` selects on the noise as well.
  The paper's own gloss: "No matter what measure is chosen for optimization, an
  inexact metric necessarily leads to a divergence between the goal and the
  metric in the tail."
- **Extremal.** Two sub-cases, model insufficiency (`M = G(s) + G'(s)`) and
  regime change (`G = M + x` for `M ≤ a`, `M + y` for `M > a`). No closed form.
- **Causal.** Selection on a correlate that is not on the causal path.
- **Adversarial.** Requires an agent optimizing against the regulator.

The quantitative content lives in Gao's §4.2, which reads the taxonomy onto his
own fitted coefficients. For independent `X` (gold) and `Z` (noise) with `X`
normal and `Z` normal:

&nbsp;&nbsp;&nbsp;&nbsp;`E[X | X̂ = x̂] = E[X] + (x̂ − E[X] − E[Z]) · Var(X) / (Var(X) + Var(Z)) + ε`

"the optimization power expended is divided between optimizing the gold reward
and selecting on the noise proportional to their variances." Gao's readings:
**the `α` term is regressional Goodhart** (the difference between the proxy
slope and the linear component of the gold slope), **the `β` term is extremal
Goodhart** and is what produces non-monotonicity and, in the limit, unbounded
loss. He also observes that under pure regressional Goodhart "the gold reward
must always increase monotonically with the proxy reward" — so any observed
non-monotonicity is evidence for something beyond regression to the mean.

**A genuinely quantitative Goodhart paper.** Jacek Karwowski, Oliver Hayman,
Xingjian Bai, Klaus Kiendlhofer, Charlie Griffin, Joar Skalse, "Goodhart's Law
in Reinforcement Learning", [arXiv:2310.09144](https://arxiv.org/abs/2310.09144)
(ICLR 2024), is worth more of your attention than the taxonomy.

- **Prevalence.** Across 30,400 sampled Markov decision processes (grid worlds,
  random MDPs, tree MDPs, sweeping discount factor, sparsity and optimization
  pressure), a Goodhart drop occurs in **19.3%** of experiments. Common, not
  universal.
- **Mechanism.** Policy optimization is maximization of a linear function over
  the convex polytope of state-action occupancy measures. Their **Proposition 3
  (Concavity of Steepest Ascent)**: with
  `t_i := (η_{i+1} − η_i)/‖η_{i+1} − η_i‖`, the quantity `t_i · R` is
  *decreasing*. Goodharting happens when the path hits a face of the polytope
  and deflects into the projection of the proxy direction onto that face.
- **Why this matters for us.** Proposition 3 is a **derivation of concave
  response to cumulative pressure from geometry alone, with no rails and no
  reward-model error.** It is an independent reason to expect a saturating
  functional form, and it means that observing concavity does *not* by itself
  implicate proxy misspecification.
- **Stopping rule.** Their Theorem 1 and Corollary 1 give a provable early stop:
  given a bound `θ` on the angle between proxy and true reward, stop at the
  minimal `i` with
  `(J_{R1}(π_{i+1}) − J_{R1}(π_i)) / ‖η_{π_{i+1}} − η_{π_i}‖ < sin(θ) ‖M_τ R_1‖`.
  In our vocabulary: stop when the realized proxy gain per unit of policy
  movement falls below a threshold set by the judge-to-value angle. That is a
  loop-health readout with a theoretical justification, and it is close to the
  "`h²` as an early monitor" follow-up already listed in
  `report_population_genetics_unification.md`.

---

## 8. Best-of-N versus RL, and best-of-N distillation

**BOND.** Pier Giuseppe Sessa et al. (Google DeepMind), "BOND: Aligning LLMs
with Best-of-N Distillation",
[arXiv:2407.14622](https://arxiv.org/abs/2407.14622). Their Theorem 1 gives the
**exact** best-of-N distribution, with ties handled:

&nbsp;&nbsp;&nbsp;&nbsp;`π_BoN(y) = π_ref(y) · p_≤(y)^{N−1} · Σ_{i=1}^{N} (p_<(y)/p_≤(y))^{i−1}`

where `p_<(y) = P_{y'∼π_ref}[r(y') < r(y)]` and
`p_≤(y) = P_{y'∼π_ref}[r(y') ≤ r(y)]`. The second factor is bounded in `[1, N]`
and equals `N` exactly when `π_ref` is continuous.

The result that matters for framing our loop is §3.3: best-of-N sampling is
exactly the solution of a KL-regularized RLHF problem with reward
`r_BOND(y) = log p_≤(y) + (1/(N−1)) log Σ_i (p_</p_≤)^{i−1}` and regularization
strength

&nbsp;&nbsp;&nbsp;&nbsp;`β_BOND = 1/(N − 1)`.

So **our per-round operation is a KL-regularized tilt with a fixed `β`, and the
round index is the number of times that tilt is applied.** Ferbach's Lemma 2.1
gives the same statement from the other direction (`t` rounds of curation = RLHF
with `β = 1/t`). Two independent derivations agreeing that cumulative pressure
is linear in `t` is a reasonably strong basis for §2.3.

BOND also notes that `r_BOND` "is invariant to monotone transformations of the
reward … since it depends only on the rank among the generations," and
conjectures this makes it more robust to reward hacking than standard RLHF.
That conjecture, if true, further lowers the prior that our loop is in a Gao
overoptimization regime.

**Asymptotic equivalence.** Joy Qiping Yang, Salman Salamatian, Ziteng Sun,
Ananda Theertha Suresh, Ahmad Beirami, "Asymptotics of Language Model Alignment",
[arXiv:2404.01730](https://arxiv.org/abs/2404.01730), prove that the best-of-`N`
policy with `N = exp(mδ)` is asymptotically close to the KL-constrained RL
solution and that their expected rewards are asymptotically equal, via a large
deviations argument on mismatched tilted distributions. This is the theoretical
justification for treating best-of-N and RL as the same optimization pressure in
the limit — which sharpens Gao's empirical observation that the two look similar
when plotted against proxy score rather than against KL.

**Iterated distillation and amplification.** Paul Christiano, Buck Shlegeris,
Dario Amodei, "Supervising strong learners by amplifying weak experts",
[arXiv:1810.08575](https://arxiv.org/abs/1810.08575), is the original
amplify-then-distill scheme our loop structurally resembles. It is a proposal
and a proof-of-concept, not a quantitative theory of saturation, and I found no
scaling law in it. Cite it for the shape of the scheme, not for a functional
form.

---

## 9. What I could not find

Stated explicitly, because these are the gaps that would change the
recommendation if filled:

1. **No published scaling law for iterated best-of-N distillation across
   rounds.** Gao's §4.3 is the closest thing and it is an analytical corollary
   under two stated assumptions, not a fit to iterated data. Song et al. show
   the gap collapsing in two to three rounds but fit no curve to it. I searched
   for 2025–2026 follow-ups and found related work (Faster WIND for iterative
   best-of-N distillation, distillation scaling laws at
   [arXiv:2502.08606](https://arxiv.org/abs/2502.08606)) but nothing that fits
   `value(round)` or `value(cumulative KL)` for a multi-round selection loop.
   **If our project fits such a curve credibly, it is new.**
2. **No numerical values of `α_bon`, `β_bon`, `α_RL`, `β_RL`** in either Gao's
   or Rafailov's main text — both report them only as figures. So I cannot place
   our `d = 1.95` relative to their peak `d* = α/(2β)` numerically. Extracting
   those from the figures, or from any released code, would be worth an hour.
3. **No multi-round version of sharpening theory.** Huang et al. define
   sharpening relative to a fixed base model. Nobody has, as far as I can find,
   analyzed the iterated version where the base model is replaced each round.
4. **No theory that predicts the transmission coefficient `h²` specifically.**
   Ferbach's idealized limit gives 1.0; our causal estimate is 0.754 with an
   upper interval bound of 0.984. What accounts for the shortfall — imperfect
   distillation, LoRA capacity, the finite `K` regularization in Ferbach's
   Eq. 6 — is not settled by anything I read.
5. **The `K`-dependence of Ferbach's `H^K` was not worked out numerically for
   `K = 6, k = 2`.** Their Eq. 6 is stated for keeping one of `K`; the top-`k`
   generalization is straightforward but they do not do it, and neither did I
   beyond the quantile-space KL computation in §2.3.

---

## Appendix A — code for the numerical results

Both computations should be committed as
`scripts/analysis_selection_pressure_budget.py`, writing to
`experiments/selection_pressure_budget.json`, before anything here is cited on a
summary surface.

```python
import numpy as np
from math import log, lgamma, exp

# --- Analytic KL of "keep the top k of n, weight the kept equally" ---
# In quantile space u ~ Uniform(0,1), the j-th largest of n uniforms has density
#   f_j(u) = n!/((j-1)!(n-j)!) * u^(n-j) * (1-u)^(j-1)
# and the kept set is the equal mixture over j = 1..k.
n, k = 6, 2
u = np.linspace(0.0, 1.0, 2_000_001)

def dens(u):
    tot = np.zeros_like(u)
    for j in range(1, k + 1):
        C = exp(lgamma(n + 1) - lgamma(j) - lgamma(n - j + 1))
        tot += C * u ** (n - j) * (1 - u) ** (j - 1)
    return tot / k

g = dens(u)
G = np.concatenate([[0.0], np.cumsum((g[1:] + g[:-1]) / 2 * np.diff(u))])
G /= G[-1]

# --- Cumulative KL under perfect distillation: compose the quantile map ---
Gs, logf, prev = u.copy(), np.zeros_like(u), 0.0
for t in range(1, 6):
    logf = logf + np.log(np.maximum(dens(Gs), 1e-300))
    Gs = np.interp(Gs, u, G)
    f = np.exp(logf)
    kl = float(np.trapezoid(np.where(f > 0, f * logf, 0.0), u))
    print(t, round(kl, 4), round(kl ** 0.5, 4), round(kl - prev, 4))
    prev = kl
# -> 1 0.5954 0.7716 0.5954 / 2 1.6201 1.2728 1.0247 / 3 2.7092 1.6460 1.0891
#    4 3.8067 1.9511 1.0975 / 5 4.9052 2.2148 1.0985   (increment -> log 3)
```

The power simulations of §6.2 and §6.3 follow the same pattern: generate runs
with `sigma = 0.72*sqrt(v*(1-v))*U(0.8,1.2)`, `rho ~ Normal(0.35, 0.20)`,
`g = rho*sigma`, a per-round residual standard deviation of 0.11 on the value
move, clipping `v` to `[0,1]`; then compare `Δv = h²·g` against
`Δv = h²·g·exp(-λ(t-1))` by likelihood ratio with the critical value calibrated
by simulation under the null, and `Δv = g(α - βP)` against
`Δv = c(v_∞ - v)g` by AIC. Full listings are in the session scratchpad
(`power.py`, `power3.py`, `power5.py`) and should be folded into the committed
script rather than left there.

---

## Appendix B — every source cited, with links

| paper | link | what it supplies |
|---|---|---|
| Gao, Schulman, Hilton, *Scaling Laws for Reward Model Overoptimization*, ICML 2023 | [arXiv:2210.10760](https://arxiv.org/abs/2210.10760) | `d = √KL`; `R_bon(d) = d(α−βd)`; `R_RL(d) = d(α−β log d)`; `KL_bon = log n − (n−1)/n`; iterated-RLHF corollary; Goodhart reading of `α` and `β` |
| Beirami et al., *Theoretical guarantees on the best-of-n alignment policy*, ICML 2025 | [arXiv:2401.01879](https://arxiv.org/abs/2401.01879) | `log n − (n−1)/n` is an upper bound; binary example capped at `log 2`; win rate ≤ `n/(n+1)` |
| Rafailov et al., *Scaling Laws for Reward Model Overoptimization in Direct Alignment Algorithms*, NeurIPS 2024 | [arXiv:2406.02900](https://arxiv.org/abs/2406.02900) | Gao's RL form transfers to DPO/IPO/SLiC with win rates |
| Huang, Block, Foster, Rohatgi, Zhang, Simchowitz, Ash, Krishnamurthy, *The Sharpening Mechanism*, ICLR 2025 | [arXiv:2412.01951](https://arxiv.org/abs/2412.01951) | sharpening as a fixed point; coverage coefficient `C_cov`; sample-complexity bounds; single-shot only |
| Song, Zhang, Eisenach, Kakade, Foster, Ghai, *Mind the Gap*, ICLR 2025 | [arXiv:2412.02674](https://arxiv.org/abs/2412.02674) | generation–verification gap = our selector gap; collapses to zero in two to three rounds; diversity loss measured by pass@k |
| Ferbach, Bertrand, Bose, Gidel, *Self-Consuming Generative Models with Curated Data*, NeurIPS 2024 | [arXiv:2407.09499](https://arxiv.org/abs/2407.09499) | exact curation update; replicator limit; response ∝ variance; convergence to the top reward level set reached at initialization |
| Sessa et al., *BOND: Aligning LLMs with Best-of-N Distillation* | [arXiv:2407.14622](https://arxiv.org/abs/2407.14622) | exact best-of-N distribution with ties; best-of-N = KL-regularized RLHF at `β = 1/(N−1)` |
| Yang, Salamatian, Sun, Suresh, Beirami, *Asymptotics of Language Model Alignment* | [arXiv:2404.01730](https://arxiv.org/abs/2404.01730) | best-of-N and KL-constrained RL are asymptotically equivalent in expected reward |
| Karwowski, Hayman, Bai, Kiendlhofer, Griffin, Skalse, *Goodhart's Law in Reinforcement Learning*, ICLR 2024 | [arXiv:2310.09144](https://arxiv.org/abs/2310.09144) | 19.3% Goodhart-drop prevalence over 30,400 MDPs; concavity of steepest ascent; provable early stopping rule |
| Manheim, Garrabrant, *Categorizing Variants of Goodhart's Law* | [arXiv:1803.04585](https://arxiv.org/abs/1803.04585) | the four-way taxonomy; regressional model `M = G + normal(μ,σ²)` |
| Christiano, Shlegeris, Amodei, *Supervising strong learners by amplifying weak experts* | [arXiv:1810.08575](https://arxiv.org/abs/1810.08575) | iterated distillation and amplification, as scheme shape only |
| Busbridge, Shidani, Weers, Ramapuram, Littwin, Webb, *Distillation Scaling Laws* | [arXiv:2502.08606](https://arxiv.org/abs/2502.08606) | teacher-student capacity gap; not multi-round, listed for completeness |

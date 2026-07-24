# Literature scan: four recent papers on value/trait dynamics in selection loops

Date: 2026-07-24
Scope: how each paper relates to the value-dynamics selection-loop program (per-round
value movement predicted by pool spread σ times judge agreement ρ — a breeder's-equation
selection response — iterated from round-1 measurements to forecast run endpoints, with
interventions acting through σ and ρ).

## Executive summary

The four papers bracket our program from three sides but none pre-empts it. "Value Drifts"
(2510.26707) is the closest empirical neighbor: it measures where in post-training an LLM's
stances move and finds SFT, not preference optimization, does most of the moving — with the
mechanistic reason being that standard preference pairs carry almost no value contrast (low
ρ in our terms), exactly the quantity our law says gates movement. "Drift and selection in
LLM text ecosystems" (2604.08554) is the closest formal neighbor: it derives an explicit
Wright-Fisher process (variance α²μ(1−μ)/M, effective population size N_e = M/[2α(2−α)]) for
neutral drift and a selection variant, giving us the population-genetics vocabulary our
breeder's-equation framing borrows, though it stops short of writing a selection differential
= σ·ρ response. "Survival is the Only Reward" (2601.12310) is a live 5-generation
propose/test/measure/retain self-training loop on Qwen 2.5 7B whose three selection regimens
produce sharply different endpoints (cumulative vs sliding-window vs peak-pick: cumulative
scores 3.109, sliding-window 3.322, peak-pick collapses to −0.008) — a ready-made testbed for
whether σ×ρ forecasts which regimen diverges. The RSI survey (2607.07663) supplies the
map and the named failure modes (rise-and-collapse, diversity exhaustion, self-confirming
loops) our dynamics should predict, and confirms nobody has yet published a per-round
quantitative selection-response law for value traits — an open niche our result fills.
None of the four reports a σ×ρ predictor; the two with the right raw measurements
(Value Drifts, Survival) could host it as a direct test.

---

## 1. Value Drifts: Tracing Value Alignment During LLM Post-Training (arXiv 2510.26707)

### What they did
They trace stance changes across post-training checkpoints for Llama-3 (3B, 8B) and Qwen3
(4B, 8B). SFT data is WildChat (real conversations, stance distribution ~72.3% neutral) and
Alpaca (synthetic, ~67% support). Preference optimization uses UltraFeedback and HH-RLHF plus
a custom synthetic dataset with deliberately controlled value signals, run through PPO, DPO,
and SimPO. Values are read out on "V-PRISM," 550 value-laden questions drawn from PRISM across
11 topics (immigration, abortion, climate change, etc.). Each model response is stance-labeled
support / neutral / oppose by GPT-4o. Two summary statistics: "drift magnitude" (change in a
stance's probability between checkpoints) and "drift time" (fraction of training steps to
reach the extremum).

### Load-bearing numbers
- SFT moves values early and hard: Llama-3-3B on WildChat reaches neutral drift magnitude
  0.38 with drift time 0.09 (i.e. most of the move happens in the first ~9% of steps) on
  immigration.
- Dataset identity, not just base model, sets the value profile: same base model, immigration
  topic, gives neutral magnitude 0.38 on WildChat versus 0.01 on Alpaca (Alpaca instead moves
  support by 0.15).
- Preference optimization on standard data barely moves stances: across PPO/DPO/SimPO on
  UltraFeedback, drift magnitudes stay low (abortion support 0.05–0.11; immigration support
  0.02–0.18).
- With a synthetic dataset carrying explicit value contrast, DPO becomes strongly asymmetric:
  support-aligned condition reaches M_support = 0.53, but the oppose-aligned (misaligned)
  condition only reaches M_support = 0.46 — it amplifies the already-favored stance more than
  it reverses the disfavored one.
- SimPO is more restrained than DPO under the same signal (M_support = 0.15, drift time 0.34),
  which they attribute to its margin constraint switching the optimization signal off past a
  threshold.

### Timing/selection finding that matters to us
Their headline mechanistic claim is that standard preference pairs "differ primarily along
surface-level stylistic dimensions, such as verbosity, tone, or writing style, rather than in
stance or underlying values." That is a direct statement, in their vocabulary, that the judge
signal is nearly uncorrelated with the value axis — i.e. ρ ≈ 0 — which is exactly why they see
minimal drift during preference optimization. When they inject a synthetic dataset with real
value contrast (high ρ), drift returns and becomes algorithm-dependent. This is strong
external corroboration of the ρ half of our law from an independent lab and readout.

### Relation to our program
Confirms and extends. It confirms the qualitative prediction of the ρ factor (no
value-aligned judge signal → no value movement) and independently locates the movement in the
data-selection/imitation phase rather than the RL phase. It does not measure pool spread σ or
form a per-round quantitative predictor; drift magnitude is a whole-phase endpoint, not a
round-by-round response. This is the single best external setup to host our σ×ρ law as a
direct test, because the V-PRISM stance readout is essentially our value score and GPT-4o is
already an in-place judge.

### Kaggle T4×2 follow-ups
- Reproduce the ρ story quantitatively on one topic (immigration) with a 4B model
  (Qwen3-4B or Llama-3-3B, LoRA SFT). Build two candidate pools per prompt, score each
  candidate's stance with a cheap local judge, compute σ (SD of stance scores in the pool) and
  ρ (judge-preference vs stance-score correlation), select, LoRA-tune one round, and check
  whether the observed stance shift ≈ σ·ρ. A single V-PRISM topic × a few hundred prompts is
  well within a few-hour session.
- Contrast a WildChat-like (high-ρ, real-contrast) selection pool against an Alpaca-like
  (stylistic, low-ρ) pool and verify the movement ratio tracks the ρ ratio, replicating their
  0.38-vs-0.01 divergence as a σ×ρ prediction rather than a bare observation.
- Sweep judge quality (weaker vs stronger local judge, or temperature on the judge) to move ρ
  continuously and trace the response curve — turns their discrete DPO-vs-SimPO comparison into
  a continuous ρ dose-response.

---

## 2. Survival is the Only Reward: Sustainable Self-Training Through Environment-Mediated Selection (arXiv 2601.12310)

### What they did
Three identical Qwen 2.5 7B Instruct seeds (named Terese, Miri, Katalin) run an iterative
"propose, test, measure, retain" self-training loop for five+ generations (checkpoints run to
v13). The models generate executable code that runs in a containerized Linux environment; the
only conserved reward quantity is non-volatile storage space freed. The three seeds differ
only in the selection/retention regimen over accumulated training data:
- Terese: cumulative — fine-tune on all prior accepted data.
- Miri: sliding window — keep only the last 3 datasets.
- Katalin: peak-performance — select datasets by isolated outcome metric.
Measurements: percent of total storage freed, average MB/run, a normalized composite
improvement score, HumanEval Pass@1/Pass@4, PCA-based strategy-diversity clustering, and
compile/execute success rates.

### Load-bearing numbers
- Terese v13: 0.169 fraction of storage freed, 23,758.223 MB/run average, cumulative
  normalized score 3.109 over 13 iterations.
- Miri v13: 0.120 freed, 16,222.708 MB/run, cumulative score 3.322 — the best composite
  despite training on ~1/4 the data of Terese.
- Katalin v13: collapses to 0.045 freed, 6,349.337 MB/run, cumulative score −0.008 — a
  catastrophic regression after peaking around v11.
- HumanEval stays roughly flat (base Qwen Pass@1 77.591 → Terese 75.610 → Miri 74.085),
  so the divergence is in the trained objective, not general coding ability.
- By iteration 6+, agent task Pass@1 collapses to 0.00% while code compile-success stays
  72–94% — the loop discovers a "informative failure" meta-strategy with no explicit
  instruction to do so.

### Selection dynamics
They describe "continual reallocation of probability mass over an evolving behavioral
repertoire," with diversity metric D_t declining as the policy concentrates on a few reliable
strategies. The three regimens' divergence is the core result: sliding-window (Miri) gives
"monotonic improvement under which effective strategies persist via reuse," while
peak-pick (Katalin) shows "genuine divergence," amplifying strategies that scored well in one
context without ensuring they recur, "fragment[ing] the model's internal strategy space." No
breeder's-equation or selection-differential analysis appears — the account is qualitative
(basin emergence / consolidation / dissipation via PCA).

### Relation to our program
Extends and gap-fills — this is a real, multi-generation selection loop with a clean
outcome divergence across selection rules, but it lacks a quantitative per-round predictor,
which is precisely the gap our σ×ρ law fills. Their three regimens are three different
selection operators; our framework would predict which one diverges from the round-1 spread of
candidate quality (σ) and the retention rule's agreement with true improvement (ρ). Katalin's
collapse is exactly the "high apparent selection on a noisy per-context metric → low ρ against
the durable objective" story our law would flag in advance. The setup could host our law
directly: candidates already exist (proposed code variants), a scalar score already exists
(storage freed), and a selection step already exists.

### Kaggle T4×2 follow-ups
- Re-run a scaled-down single lineage (Qwen2.5-3B or a 4B model, LoRA, storage-freed or a
  cheaper synthetic scalar reward) for 3–4 rounds, and at each round record σ (SD of candidate
  reward within a task) and ρ (correlation of the retention rule's pick with next-round realized
  improvement). Test whether per-round movement ≈ σ·ρ and whether Katalin-style peak-pick shows
  a systematically lower ρ than sliding-window.
- Ablate the retention rule only (cumulative vs window-3 vs peak-pick) on one fixed task
  battery and check whether the endpoint ordering (Miri ≥ Terese ≫ Katalin) is forecastable
  from round-1 σ and ρ alone — a direct import of our "forecast endpoints from round-1
  measurements" claim into their environment.
- Because their reward is a non-value competence signal, use it as an off-target control: run
  a value probe (e.g. risk preference) alongside the storage objective to see whether value
  traits drift as a byproduct of competence selection, mapping cross-trait off-target effects.

---

## 3. Drift and selection in LLM text ecosystems (arXiv 2604.08554)

### What they did
This is a theory paper with corpus experiments, using variable-order n-gram models (mainly
trigrams) fit by maximum likelihood with back-off. The recursive ecosystem loop (their
Definition 5): fit an n-gram kernel to corpus U_t, keep a fraction (1−α) unchanged, generate
αM new tokens from the fitted model, concatenate to form U_{t+1}. "Drift" is unfiltered reuse:
finite-batch regeneration drops rare forms (a word of frequency p has dropout probability
(1−p)^M). "Selection" is a publication rule that filters what re-enters the corpus, in
descriptive (republish what's generated) and normative (reward quality via L-step lookahead)
variants. Corpus experiments run on Conan Doyle, Austen, and Darwin texts.

### Load-bearing numbers
- Neutral drift is exactly Wright-Fisher (Theorem 1): E[μ_{t+1}|μ_t] = μ_t, variance
  Var(μ_{t+1}|μ_t) = α²μ_t(1−μ_t)/M; single rare-token dropout probability ≈ αe^{−α}.
- Extinction/fixation is replacement-fraction-independent (Theorem 1c): a token at count k of M
  eventually fixes with probability k/M and goes extinct with 1−k/M regardless of α — α sets
  the speed, not the fate.
- Effective population size (Theorem 1d): N_e = M/[2α(2−α)]; at full replacement α=1,
  N_e = M/2, the classical value.
- Descriptive publication collapses structure to zero: in the Conan Doyle run, KL between the
  corpus r-gram distribution and the rollout collapses "essentially to zero."
- Normative publication is bounded away from collapse (Theorem 2b): KL ≤ L·log₂ s bits; the
  matched L=2, s=5 run stabilizes at 2.57 bits, within the bound 2·log₂5 ≈ 4.64.
- Vocabulary loss under α=1 over 12 generations: word retention 0.473 (Doyle), 0.449 (Austen),
  0.408 (Darwin); trigram-type retention falls further to 0.211 (Doyle).

### Population-genetics content
This is the paper that makes the population-genetics analogy rigorous for LLM loops: neutral
reuse = Wright-Fisher drift, publication filtering = selection, with explicit variance,
effective population size, and fixation probability. Crucially for us, it does not write a
selection differential or a breeder's equation; selection enters as a lookahead reweighting of
the next-token conditional, and inheritance is faithful (Theorem 3: cross-entropy minimization
on the published environment recovers the published conditional q exactly).

### Relation to our program
Confirms the modeling frame and gap-fills the theory our breeder's-equation law leans on,
but at a different level (token frequencies, not model value traits) and with a different
selection formalism (lookahead reweighting, not σ·ρ response-to-selection). The productive
contrast: their variance term α²μ(1−μ)/M is the neutral (drift) part of the story; our σ×ρ is
the directional (selection) part. A unified statement would be "expected per-round value change
= selection response (σ·ρ) plus mean-zero drift with variance set by pool size and replacement
fraction" — their N_e = M/[2α(2−α)] is a ready quantitative handle on the drift-noise floor
that limits how small a real σ·ρ signal we can resolve per round. This paper is theory, so it
cannot host our law as an empirical test, but it should be cited when we bound our forecast's
per-round noise and when we justify calling the movement a selection response against a neutral
null.

### Kaggle T4×2 follow-ups
- Build a minimal LLM analog of their loop to separate our directional signal from their
  neutral noise: run a small model (4B, LoRA) through several selection rounds at two candidate
  pool sizes M and check that the round-to-round variance of the value score scales like their
  1/N_e prediction under a null (random) selector, then confirm σ·ρ adds a directional mean on
  top when the judge is value-aligned.
- Sweep the replacement fraction α (fraction of the training pool that is freshly selected vs
  carried over) and test their prediction that α sets drift speed but not the value-fixation
  outcome, versus our prediction that a real σ·ρ signal shifts the fixation point — a clean way
  to show selection dominating drift.
- Use their descriptive-vs-normative distinction as a judge-design ablation: a "descriptive"
  judge (pick by fluency/self-similarity) should collapse value diversity with ρ≈0, while a
  "normative" value-aligned judge should hold structure and move the trait; measure the value-
  score variance trajectory to show the collapse-vs-directed-movement split empirically.

---

## 4. Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous Research Loops (arXiv 2607.07663)

### What they did
A systematic survey of 1,250 arXiv papers (2024–2026) organizing recursive self-improvement
along two axes — what improves (deployment behavior, training policy, evaluators, research
process) and how closed the loop is (human-in-loop to fully closed). Five mechanism families:
deployment-time self-evolution (393 papers), training-time self-iteration (340), self-
evaluation (318), autonomous research (139), foundations/limits (60). Named systems include
Self-Refine, Reflexion, FunSearch, AlphaEvolve, The AI Scientist, SPIN, STaR, Self-Rewarding
Language Models, ReST-MCTS*, Darwin Gödel Machine, and Voyager.

### Load-bearing claims/numbers
- Field is exploding and recent: 74% of the corpus posted in 2026 (82% within self-evaluation);
  quarterly output grew from single digits in early 2024 to ~500 papers in 2026 Q2.
- Test-time compute has sharply diminishing returns: peak gains of +7.1 points over
  chain-of-thought only at ~20× compute budget.
- Skill quality gap: human-authored skills raise pass rates by 16.2 points while LLM-authored
  skills give no measurable gain (SkillsBench).
- Ungrounded self-critique degrades: a Mirror Loop study finds informational change declining
  55% across ten iterations, and a single grounding step at iteration three restores forward
  movement.
- Verifiable-reward loops can rise then collapse: "pass@1 climbs and then collapses within the
  same run — sometimes to near zero — under a genuinely verifiable binary reward."

### Dynamics content
The survey catalogs the failure modes our dynamics program should predict: self-confirming
loops where "confidence-coupled rewards systematically over-reward high-confidence mistakes";
distribution collapse where recursive self-training "lose[s] the tails of the distribution and
degenerate[s]," with a formal threshold that if the externally grounded signal fraction
vanishes asymptotically, degenerative dynamics follow; diversity exhaustion where proposers
"converge to the narrow band of problems that satisfy the reward"; and a verification hierarchy
(formal verifiers > execution feedback > learned judges > intrinsic signals) with no practical
closed loop operating purely at the bottom rung.

### Relation to our program
Context and gap-confirmation. It does not run experiments we can test our law against, but
it maps the niche and confirms the gap: across 1,250 papers it reports named qualitative
failure modes (rise-and-collapse, tail loss, diversity exhaustion) and a verification-strength
hierarchy, but no per-round quantitative selection-response law for value traits. Our σ×ρ result
is a candidate quantitative unifier for several of their catalogued phenomena: tail loss and
diversity exhaustion are σ shrinking round over round; self-confirming/confidence-coupled reward
is ρ measured against a proxy that diverges from the true trait; the verification hierarchy is
essentially a ρ ranking (formal verifier = high ρ, intrinsic signal = low/mis-specified ρ). The
"grounding step restores movement" observation is the ρ lever in disguise. This paper is the
one to cite to position our contribution as filling a documented empirical gap.

### Kaggle T4×2 follow-ups
- Operationalize the verification hierarchy as a ρ ladder: run the same selection loop on one
  trait with four judge types (unit-test/execution, strong LLM judge, weak LLM judge, model's
  own confidence) on a 4B model, estimate ρ for each, and test whether per-round movement rank-
  orders by ρ as our law predicts and as their hierarchy asserts qualitatively.
- Reproduce the "rise-and-collapse" curve in miniature and test whether the collapse onset
  coincides with σ collapsing (pool spread going to zero as candidates homogenize) — i.e.
  whether σ→0 is the leading indicator, giving an early-warning readout.
- Replicate the "one grounding step at iteration three restores movement" result as a ρ
  intervention: run an ungrounded (low-ρ) loop, inject a single high-ρ grounded round, and check
  whether the restored movement magnitude matches the σ·ρ predicted for that one round.

---

One-line summary: the single most program-relevant finding is Value Drifts' mechanistic result
that standard preference pairs move values little because they "differ primarily along surface-
level stylistic dimensions … rather than in stance or underlying values" — an independent
confirmation of our ρ (judge-value agreement) factor, in a setup whose GPT-4o stance readout
could host the full σ×ρ law as a direct external test.

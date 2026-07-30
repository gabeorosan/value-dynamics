# PLAN — the single current plan

**This file is the only authoritative plan.** STATE.md = what is happening now;
PLAN.md = what we decided to do; ANALYSIS_LEDGER.md = what we found, and it is
the only place a result claim may originate. If this file and any other document
disagree, this file wins. The 2026-07-14 plan and its full decision log are in
[archive/PLAN_archive_2026-07-28.md](archive/PLAN_archive_2026-07-28.md).

*Rewritten 2026-07-28 around the two terms of the Price equation, after five
literature reviews and three analyses landed on the same day. Lanes 2 and 3
updated 2026-07-29: lane 2's central question turned out to be answerable by
arithmetic, and lane 3 now has a measurable stability criterion.*

## The reframing

The Price equation splits a change in a population mean into two terms:

    Δz̄  =  Cov(w, z)/w̄   +   E[w · Δz]/w̄
           ────────────       ─────────────
           SELECTION          TRANSMISSION
           what the judge     what training does that
           favours            nobody selected for

**The program has characterised the first term and barely touched the second.**
That is the single sentence that should drive what happens next.

For the selection term we have a parameter-free law (gap = ρσ, R² 0.80 over 367
rounds), a response coefficient triangulated three ways at 0.75–0.81, a
demonstration that it does not decay over four rounds, and a null showing that
with no selection the loop is idempotent. For the transmission term we have
essentially nothing, and — established by the 2026-07-28 literature sweep —
**neither does anyone else: no published trait-by-trait transmission matrix
exists for any language model.**

Transmission bias is also where the alignment-relevant phenomena live. Emergent
misalignment is a large off-diagonal element. Subliminal learning
([arXiv 2507.14805](https://arxiv.org/abs/2507.14805)) is pure transmission
bias, and its own requirement — that teacher and student share a base model —
is satisfied *by construction* in a self-training loop.

## What is settled enough to build on

Point to the ledger for wording; this is orientation only.

- **The selection law.** gap = ρσ parameter-free; next value ≈ kept mean;
  round-1 measurements forecast four-round endpoints at MAE 0.118.
- **The response coefficient is 0.75–0.81**, from three estimates: 0.809
  observational on the near-uncensored 340-round corpus, 0.754 [0.621, 0.984]
  from the randomised round-1 instrument, and 0.450 observational on the
  heavily-censored spread corpus, where the abort rule removed the fastest
  movers. The two censoring-free estimates agree.
- **It does not decay over four rounds.** Every wear/headroom/round term is
  indistinguishable from zero once the pool-offset term is in the model; within
  runs the wear term reverses sign. Runs level off because **the gap shrinks,
  not because the response to it shrinks** — mean |gap| falls 0.099 → 0.070
  while the coefficient holds.
- **With no selection, nothing happens.** |gap| ≤ 0.01 gives movement at 0.574
  [0.334, 0.838] of the measurement-noise floor. Independently corroborated by
  Roe et al. ([arXiv 2605.01130](https://arxiv.org/abs/2605.01130)).
- **Agreement is close to non-persistent** for any non-oracle judge — corr(ρ₁,
  ρ_t) is 0.354 / 0.117 / 0.130 at rounds 2–4. The frozen-agreement forecast
  works anyway, presumably because movement is front-loaded.

## Theory anchors, with their scope limits

| Anchor | What it gives us | Scope limit |
|---|---|---|
| Ferbach et al. [2407.09499](https://arxiv.org/abs/2407.09499) Eq. 8 | Response = **λ/(1+λ)** × differential when reference data is mixed back. 0.78 is λ/(1+λ) at λ ≈ 3.5, so **an anchored fine-tune transmits below 1 by design**. Leading account of our coefficient. | r is a fixed exogenous function everywhere in that paper; no self-judge arm is in scope |
| Ferbach Thm 2.1 | Converges to p₀ restricted to the top reward level set *reachable from initialisation*, so E[v] → E[v \| r = r\*] — a conditional mean, not max v. **Interior plateaus are predicted, not anomalous.** | Needs an atom on that level set; fixed r |
| Lande (1981) / Kirkpatrick (1982) Fisherian runaway | The bifurcation condition for a co-evolving judge, written in our variables: stability iff the equilibrium-line slope exceeds the judge–value coupling. Frozen-judge work is the zero-coupling slice and structurally cannot show it. | Quantitative-genetics idealisations; not yet imported to ML by anyone |
| Song et al. [2412.02674](https://arxiv.org/abs/2412.02674) | Their generation–verification gap *is* our selector gap, and it collapses in 2–3 rounds through diversity loss, at a rate independent of model capacity. Direct precedent for "the gap shrinks". | Different task family |
| Roe et al. [2605.01130](https://arxiv.org/abs/2605.01130) | SFT self-training is idempotent without selection; DPO amplification needs **continual** training and vanishes on reinitialisation. | Their SFT arm has no selection step |
| van Veelen's tautology critique | Lands on gap ≈ ρσ (an order-statistic identity) and **does not reach** an instrumented coefficient. The randomised encouragement design is the answer to it. | Requires the length-matched arm to close the omitted-variable condition |

## Lane 1 — the transmission term (the frontier, and it is open)

**The object.** Select on trait A, measure the induced change across a battery
of other traits. In quantitative-genetics terms this is the G-matrix of a model
under self-selection; the off-diagonals are the off-target coefficients.

**The decomposition that makes it tractable.** Off-target movement in trait B
splits into a part the candidate pool already contains and a part it does not:

    S_B  =  (P_AB / P_AA) · S_A          selection-mediated: the judge kept
                                          answers that happened to be high on B,
                                          and this is predictable from a pure
                                          inference pass before any training

    ΔZ_B − 0.78 · S_B                     the residual IS the transmission term:
                                          movement in B that no selection asked
                                          for

**Steps, cheapest first.**

1. **Zero GPU.** Score every banked candidate on off-target axes, compute
   ρ_Bσ_B per axis, and take the residual against realised ΔZ_B. This is the
   first transmission-term measurement and it needs no new training.
2. **Zero GPU.** Re-run the randomised round-1 instrument with off-target axes
   on the left-hand side. That is the first *causal* off-target column.
3. **Kaggle, at the 08-01 reset.** Value-covariance phase 1b — graded 0–9
   logprob scoring behind four pre-registered gates. Already built and queued;
   it establishes whether candidates carry multi-axis variation at all.
4. Then the matrix proper, with the benign-SFT control arm below.

**Preregister the rank.** "Narrow misalignment is hard"
([arXiv 2602.07852](https://arxiv.org/abs/2602.07852)) predicts the matrix comes
out effectively rank-1 — one general factor rather than a structured matrix.
Say so before looking.

## Lane 2 — the supply of selectable variation (why the gap shrinks)

The saturation analysis relocated the bottleneck: transmission holds, spread
collapses. Song et al. found the same collapse and attributed it to diversity
loss. This lane asks what governs the supply.

**RESOLVED 2026-07-29, and more completely than expected.** Two results closed
most of this lane:

- **The proxy-minus-gold measurement is done, and there is no overoptimisation
  at this horizon.** Divergence +0.0014 [-0.0125, +0.0178]; on OLMo the value
  moves *faster* than the judge's score of it, -0.0141 [-0.0228, -0.0064].
  Coverage exhaustion, not Goodhart.
  (reports/report_proxy_gold_divergence.md)
- **Spread is not a state variable at all on a binary axis.** It is the pool mean
  pushed through `sigma = sqrt(n/(n-1))*sqrt(q(1-q))`, exactly, on all 1,248
  corpus rows. With n = 6 everywhere the whole state space is a seven-point
  lattice, and the depletion is selection moving mass off the middle of that
  lattice onto its ends (unanimous pools 14.4% -> 24.4% over four rounds). The
  fuel is distance from the middle of the scale and selection spends it by
  construction. (reports/report_spread_supply.md)

**What that leaves for this lane**, all of it now downstream of graded scoring:

- **Graded scores are a PREREQUISITE, not a refinement.** Until candidate scores
  are graded, the second moment does not exist independently and no question of
  the form "does spread do anything beyond the mean" is answerable. Phase 1b is
  the gate.
- **Prompt screening is a real pre-loop tool and is nearly free.** Per-prompt
  pool means are stable across entirely different runs at split-half r = +0.920.
  One generation pass ranks prompts by available selectable variation and the
  ranking transfers across organisms and judges. Worth building as a utility.
- **Raise the candidate count.** The gap is quantised: with 6 binary candidates
  and keep-2 the kept mean can only be 0, 0.5 or 1. Resolution improves with
  candidate count and graded scores, not with more runs.
- Diversity per round, measured on the candidate text rather than on the value
  scores, so "spread collapsed" can be distinguished from "the value axis
  saturated while the text still varies".
- Longer horizons. Four rounds accumulate about 3.8 nats of cumulative selection
  KL (top-2-of-6 is 0.595 nats per round), which is not heavy optimisation by
  the standards of the overoptimisation literature. The eleven eight-round runs
  are suggestive and too few to fit.

## Lane 3 — the co-evolving judge

Every result above holds the judge frozen. The bifurcation question needs it to
move, and Fisherian runaway supplies the formal condition.

**There is now a criterion, measured.** Mapping Lande-Kirkpatrick onto the loop
gives a per-round loop gain `G = 1 + c*h^2*sigma`, where `c = drho/dv` is the
judge-drift coupling a frozen-judge design sets to zero by construction. Above 1
is runaway, below 1 settles. Measured: **G = 0.922 [0.86, 0.98]** — these loops
are self-limiting, movement erodes the judge's agreement. Families split, with
Qwen at 0.820 [0.70, 0.94] and OLMo at **0.974 [0.90, 1.05]**, on the boundary,
and OLMo is where this project's two runaways happened. The predicted geometric
decay holds at rounds 2-3 and fails at round 4, so read it only for early
direction. (reports/report_judge_coupling_stability.md)

**Do not answer this by adding seeds.** The matched ablation needs roughly 52
seeds per arm at the observed effect size, which is out of budget. Instead:

- **Manipulate `c` directly.** The criterion says the sign of `c` separates
  runaway from settling, so build a judge whose agreement *rises* as the value
  moves — a judge retrained on the kept text each round is the obvious one — and
  check whether the gain crosses 1 and the run behaviour crosses with it. One
  quantity, a pre-registered direction, far cheaper than powering the
  frozen-versus-evolving contrast.
- **Report `G` for every future run.** It costs nothing: sigma and rho are
  already logged every round and `h^2` is measured.

- **Sweep starting values, not seeds.** Fit `v_final = I + s·v_0` over a range
  of starting values; `s > 1` *is* the bifurcation, and it locates the
  separatrix at `I/(1−s)`.
- **Measure the judge–value coupling on a frozen pool.** Re-score the same fixed
  candidate pool each round with frozen, live, and lagged judges. Agreement
  measured on a collapsing live pool is an artefact; this is the only way to get
  a clean Δρ/Δv.

## Controls that are no longer optional

Each of these exists because a specific piece of published work makes the result
uninterpretable without it.

- **Reset versus continue.** Roe et al. find amplification vanishes on
  reinitialisation. Every run in this corpus is continual, so nothing we have
  separates "selection moves values" from "continual post-training moves
  values". Matched seed and judge; about 6 GPU-hours.
- **Benign-SFT arm** for anything off-target. Fine-tuning on *anything*
  contracts a model's behaviour; an uncontrolled matrix measures generic
  contraction.
- **Length-matched third arm** for the instrument. The spread arm's kept answers
  run +3.1 characters longer (paired t = 2.90, n = 127). Small, but it is
  literally van Veelen's omitted-variable condition, so closing it answers the
  field's main critique rather than being housekeeping.
- **Oracle exclusion** from any agreement-persistence statement. Oracle
  agreement is ±1 by construction and including those runs changes the answer.
- **A fixed anchor set of candidates, re-scored every round.** Added 2026-07-29.
  The proxy-gold result's one unremovable threat is frozen-judge calibration
  drift on a changing candidate distribution — a rising proxy could be the judge,
  not the candidates. Re-scoring an unchanging held-aside pool each round makes
  the proxy series calibration-free. Cheap, and it should be standard in every
  future loop.

## Compute

**Colab is a Pro subscription with zero compute units (checked 2026-07-29).**
That still gives T4 GPU and v5e-1 TPU; H100/A100/L4/G4 are locked until units
are bought. So GPU work does not have to wait for a Kaggle reset — verified by
connecting to a live T4 (15 GB, CUDA 13.0). Kaggle 2×T4 resets Sat 2026-08-01.
Modal ~$75 grant plus $30 a month resetting on the 1st, pilot-before-spend.
Never Cerebrium.

**Queue at the reset**, in order: (1) value-covariance phase 1b — built, gates
written, `experiments/value_covariance/launch.sh`; (2) reset-versus-continue
arms; (3) the frozen-pool judge rescoring for lane 3.

Everything in lanes 1 and 2 marked "zero GPU" should be done before the reset,
because it costs nothing and it changes what is worth running afterwards.

## Decision log

Older entries are in
[archive/PLAN_archive_2026-07-28.md](archive/PLAN_archive_2026-07-28.md).

- **2026-07-28 — the plan is rewritten around the two Price terms.** Five
  literature reviews and three analyses landed the same day. The selection term
  is characterised well enough to build on; the transmission term is open, and
  nobody else has measured it either. Lanes reorganised accordingly, and four
  controls promoted to non-optional, each traceable to a specific paper.
- **2026-07-28 — the saturation line is closed as a null.** The response does
  not decay over four rounds, and the 0.509/0.377/0.231 profile is withdrawn as
  unreproducible. Do not fit functional forms to it. The live question moved to
  lane 2: what governs the supply of spread.
- **2026-07-28 — the co-evolving-judge question will not be answered by seeds.**
  The matched ablation needs about 52 per arm. Redesigned as a starting-value
  sweep plus frozen-pool rescoring.
- **2026-07-28 (user directive) — management lives in one persistent session**;
  the every-3-hours scheduled task is disabled.

## Document index (everything else is NOT the plan)

| Document | Status |
|---|---|
| [`archive/PLAN_archive_2026-07-28.md`](archive/PLAN_archive_2026-07-28.md) | HISTORICAL — the 2026-07-14 plan and the full decision log |
| [`archive/updated_research_plan_2026-07-10.md`](archive/updated_research_plan_2026-07-10.md) | ABSORBED — keep for rationale detail |
| [`archive/plan_final_sprint_unified.md`](archive/plan_final_sprint_unified.md) | ABSORBED (its §5 TPU history retained there) |
| [`archive/plan_judge_transmission.md`](archive/plan_judge_transmission.md) | REFERENCE — constructs/predictions for the transmission cells |
| [`archive/plan_recovered_threads.md`](archive/plan_recovered_threads.md) | REFERENCE — recovered-threads audit |
| [`archive/plan_budget_no_modal.md`](archive/plan_budget_no_modal.md), [`archive/plan_value_dynamics_drivers.md`](archive/plan_value_dynamics_drivers.md), [`archive/two_week_plan.md`](archive/two_week_plan.md), [`archive/next_directions_assessment.md`](archive/next_directions_assessment.md) | HISTORICAL |

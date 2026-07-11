# PLAN — the single current plan (all threads read this one)

**This file is the only authoritative plan.** It is updated in place by the
Lit&planning thread; dated decisions are appended to the log at the bottom.
Every other `plan_*.md` / research-plan document is historical or reference —
see the document index at the end. If this file and any other document
disagree, this file wins. (Protocol: STATE.md = what is happening;
PLAN.md = what we decided to do; reports = what we found.)

*Current as of 2026-07-11 midday. Sprint ends Sunday 2026-07-12.*

## Objective (unchanged from the 07-10 correction)

One clean causal test of whether and how a model's judging preference changes
the direction of self-training, presented as coverage of the judge × generator
matrix across two model families (Qwen3-4B, OLMo-3-7B) and two values (risk,
insecure-code/self-report), with uniform analyses, confounder gates, and
riding probes.

## The matrix and its coverage

| Quadrant | Coverage this sprint |
|---|---|
| Qwen × risk | K1: full 4-judge grid on the re-centered mod25 organism; per-round vintages persisted (risk transmission cells become reachable next window) |
| OLMo × risk | K2: 4-judge conservative-inversion trajectory grid — the headline judge-swap dynamics test |
| Qwen × insecure-code | K3: 4-judge neutral-prompt mini-grid + Colab transmission/carrier/susceptibility/composition cells |
| OLMo × insecure-code | EXPLICITLY CUT (no organism, no validated instrument, likeliest outcome is a null-on-a-null; named as the empty cell in the write-up) |

## Kaggle — Saturday 45 h (BATTERY_MODE=inloop)

**Launch order (deep-audit §5; K2's confirmatory contrast is the sprint's
highest-value result):** (1) K2 confirmatory 6-seed contrast — as soon as its
two gates pass; (2) K1 anchor grid; (3) K2 evolving/random controls; (4) K3;
(5) K4 one-update content impulse if hours remain. If K2's organism gate has
not passed by window start, launch K1 first and slot K2 in on gate-pass — but
never spend K2-confirmatory hours on lower rows.

**Build status (07-11 midday):** K1 smoke PASSED (v4: invalid 0.00) after the
Qwen chat-template root cause was fixed. The old `1b4199c4` pin injected a
`<think>` block into training renders; all Qwen scripts now use the pinned
`cdbee75f` tokenizer revision with a guard assert. Measured timing is **K1 ≈
12.5 h**. K1 is launched on the calibrated `persona_mod25_r5` (generated gate
PASS at 0.625); K3 is launched. **K2's v10 top-up has landed at rung_20**
(20 judge-only steps on v8/rung_60; all seven gates pass: judge-pref 0.880,
generated 0.364, forced 0.536, order gap 0.023, invalid 0.083). K2 remains
blocked only on the exact-rung sha-bound two-pool inversion screen and the
resulting Kaggle attestation. Do not launch K2 from the v7/v8/v9 datasets.

| # | Run | Design (audit-amended, see 07-10 decision log) | Hours |
|---|---|---|---|
| K1 | Qwen anchor grid | re-centered `persona_mod25_r5` (must be in-band on the GENERATED channel — the 0.93 rationale persona is invalid) × {evolving self, frozen round-0 copy, frozen base, random-selection} × 4 seeds × 4 rounds; +1 measure-only seed. Honest counting: the frozen-base baseline is **n=4 independent rollouts**. Primary = paired baseline-adjusted final generated-valid risk (`evolving_self` vs `frozen_base`); four-seed fan/variance is secondary. New baseline; does not re-score legacy let-go. | **~12.5 (measured)** |
| K2 | OLMo conservative inversion | **6 seeds on the confirmatory contrast** (frozen-conservative vs frozen-base) + **3 seeds on the mechanistic controls** (evolving self, random) × 4 rounds. Organism = **v10_judge_topup/judge3 rung_20**, initialized from v8/rung_60 and passing all seven gates. Final gate: a sha-bound strict two-pool inversion screen on that exact rung (RUNNING). Re-measure K2 minutes on its first cell and re-run the budget arithmetic then. | ~20.5 |
| K3 | Qwen EM neutral-judge grid | insecure-code organism × 4 judge conditions (random arm FIRM) × 3 seeds × 4 rounds; existence framing at n=3; readouts em_freegen + self_report (em_choice floored) | ~6.5 |
| K4 | External-content arms | **DEFERRED — first cut, runs only if K1–K3 finish early.** Preferred form if hours remain (deep-audit §5): a ONE-UPDATE CONTENT IMPULSE — one fixed `persona_mod25_r5` checkpoint × one matched small update from {aligned, opposing, format-matched-neutral} rows, 6–8 resampled data seeds, matched examples/tokens/steps, immediate target+off-target deltas (~1–2 h; identifies the directional impulse, does not estimate a fixed point). The four-round version only by explicit choice; either way same organism/harness as K1 and fixed-point/stiffness/noise language stays exploratory. | (0–5) |
| — | Buffer (resumes, retrieval, gate failures) — SHRUNK by K1's measured cost; if K2's first-cell re-measure inflates too, cut order engages (K2 control arms 3→2 first) | | ~5.5 |

Risk-loop balance/validity requirement: every round generates exactly half its
items in each option order; every strict-valid kept answer gets a genuinely
semantics-preserving swapped-order twin. Initial invalidity is logged and
invalid candidates are rejected/replenished before training. Generated-valid
risk and invalidity remain separate; forced p(gamble) is a second, same-item
format channel. A forced order gap >0.10 or factual-EV probability drop >0.10
invalidates the semantic channel; generated invalidity >0.10 blocks a generated
behavior claim.

Judge-mechanism requirement (all K runs): retain raw candidates and all
cross-scores so candidate-level judge loading on the target axis can be
estimated with invalidity/length controls. Kept-minus-pool gap records the
realized training-data shift; it is a manipulation check, not an established
causal mediator. Generic `judgment_taste` stays off-format and secondary.

## Colab — 30 h

| When | Item | Hours |
|---|---|---|
| done (sunk) | judge-transmission broad screen (one-pool carrier candidate; fresh-pool gate still pending); α-scaling diagnostic (limited self-report carry, high-α degeneration) | ~4 |
| Friday–Sat | OLMo conservative install — **v8/rung_60 is the phase-1 parent; v10 judge-only top-up rung_20 is landed and passes all seven gates** (20 judge-only steps, judge-pref 0.426→0.880, generated 0.364, forced 0.536, order gap 0.023, invalid 0.083). Behavior-format ladders (v2–v6) are taste-inert; judge-format rows move the domain-specific judging coordinate while generic advice taste stays flat. The exact-rung two-pool screen is running; only a passing screen attestation can launch K2. | ~7 spent + top-up |
| Friday | smoke pilots of K1–K4 | ~3 |
| Friday, added | pre-Kaggle screens (audit blockers): judge-inversion screen on actual gamble pools (frozen-conservative vs frozen-base OLMo must rank the same pools differently — gates K2); carrier fresh-pool validation (≥2 new candidate-pool seeds, amp66_12-vs-base gap must reproduce in sign — gates the carrier loop) | ~2 |
| Saturday | EM transmission cells — run in parallel with K2 (explicitly adopted logic: the frozen-base control makes them independently interpretable; the older "gated on Phase 1B" wording is superseded): transmission (standout judge × fresh base gen, 3 seeds), transmission CONTROL (frozen base judge × same fresh gen, 3 seeds), carrier (reverted judge × fresh gen, 3 seeds, gated on the fresh-pool validation), susceptibility (standout judge × reverted gen, 3 seeds), composition (2 x-points — read as CONSTRUCTED-STATE COMPARISONS, not bias-free 1-D field samples: different adapters differ in more than x) | ~8 |
| Sunday | overflow / re-runs; optional risk-vintage transmission mini if K1 vintages landed (deferred BEFORE any confirmatory K2 seed is cut) | ~4 |
| — | reserve | ~5 |

Pre-Kaggle checklist status (07-11 midday): DONE — installer completion-only +
pinned revision + strict instrument (v10 top-up running); K1–K3 builds with raw
candidate cross-scoring + judge loading + SPECs (strict_final_v2 pass,
DRY-verified); storage preflight (in SPECs); Drive JSON sync with hashes.
REMAINING — rerun K2's exact-rung two-pool strict inversion screen with the
updated continuous factual-EV instrument (a pre-audit screen artifact is stale);
carrier fresh-pool validation; then attach the exact v10 dataset and screen
attestation to K2. K1/K3 are already launched; re-measure K2 minutes on its
first cell before deciding whether the named control-arm cut is needed.

## Riding in EVERY training cell (non-negotiable)

Battery patch (wishful thinking, introspection, self-recognition,
suggestibility, identity, judgment_taste); steering artifacts; off-target axes;
entropy; paired generated/forced target channels; factual-EV delta; invalidity;
raw per-question/candidate reads; **every-round adapter persistence with
factorization-invariant update logging relative to round zero (merged B·A, not
raw factors or absolute adapter norm)**. `distinct_n` is not required unless it
uses multiple stochastic samples; the one-sample implementation was removed.

## Sunday analysis day (no GPU) — audit-ordered hierarchy

1. Artifact/instrument gate table per cell (provenance, exact training-order
   balance, forced order gap, generated invalidity, factual-EV delta,
   measure-only drift) — certifies everything below.
2. Primary condition contrasts at the rollout-seed level (K2 confirmatory
   contrast first).
3. Candidate-level judge loading on actual pools; kept-minus-pool gaps as the
   realized-data manipulation check. Mediation/cross-lag remains exploratory.
4. Generated vs forced-choice behavior as distinct format channels.
5. Invariant update-geometry recompute on `W_t-W_0`; full merged-update
   Frobenius cosines and leave-one-seed-out directions. Existing leading-left-
   vector SVD alignment is insufficient. Alpha scaling is a limited negative/
   degeneration diagnostic, not a general behavioral causal leg.
6. Transmission/carrier/susceptibility verdicts (existence framing, never
   rates); K3 `em_freegen` analyzed as binomial counts with intervals — rounds
   are not independent observations.
7. Riding-battery specificity, not a fishing expedition: standardize each
   probe's change by its measure-only/item-level variation, compare against the
   random arm, report the target-specificity ratio (|standardized target
   change| / RMS standardized off-target change), BH/FDR within the labeled
   exploratory family, and decline to interpret probes with too few items or
   rail saturation.
8. Exploratory tier, labeled as such: generic judgment_taste coupling,
   mediation/cross-lag decompositions, and drift-field/fixed-point language
   ONLY where the design identifies it (composition cells are constructed-state
   comparisons; the K4 impulse supports directional deltas, not stiffness/noise).

## Out of the sprint

OLMo × insecure-code (Branch B); new model families (Qwen3.5); DPO (Branch D);
J-lens; regime grid; λ-bottleneck; Lightning top-ups; **Kaggle TPU** — gate 1
PASSED (v5e: hardware-viable) but queue-limited, so still out of the sprint;
service parked opportunistic/post-sprint only (see decision log); every-round
persistence keeps all checkpoints re-measurable later.

## Cut order if hours compress

K4 is already deferred (runs only if K1–K3 finish early). Then:
1. Sunday risk-vintage mini → next window. 2. Composition 2→1 x-points.
3. K2 mechanistic-control arms (evolving/random) seeds 3→2.
Never cut: K1; the K2 six-seed confirmatory contrast; K3's random arm;
per-round persistence + invariant logging; Friday pilots + pre-Kaggle screens.

## Decision log

- 07-11 ~15:00 (explainer thread, user corrections): K2 EXPECTED-VS-DISCOVERY
  LEDGER PINNED (extends the ~12:00 dynamics re-anchor with three write-up
  rules). (1) Pre-registered as EXPECTED — report as passing checks, never as
  findings: a screen-verified judge exerts force (selection with nonzero
  separation puts axis-shifted samples into the training data, which the
  format-gate results already showed moves the axis), trajectories move toward
  the judge's preference, and seed spread contracts under a strong external
  judge (direction already seen in the legacy frozen-base arms'
  below-equilibrium compression; that evidence is audit-demoted, so K2's clean
  arms confirm it — but as a prediction, not an open question). (2) K2's
  discovery-grade content is exactly three things: (a) drift rate per round
  per unit of verified selection differential, on the same scale as the
  frozen-base arm's intrinsic drift — the calibration anchor for reading the
  Saturday weak-dose transmission cells (emergent judge tastes are only
  Δ≈0.1 on the kept-set-gap scale); (b) round-wise co-movement or
  dissociation of the forced-choice and judging channels while selection acts
  only on generated answers (no prior data in either model family); (c) a
  valid-instrument replacement for the legacy judge-condition contrast, which
  can never be re-analyzed. (3) A flat trajectory under a passing screen is a
  DOSE INSUFFICIENCY (calibration failure), not "judge preference exerts no
  force" as a finding; every v10 rung is persisted on Drive, so dose is
  dialable downward for follow-ups — 0.880 held-out judge preference is the
  maximum available dose, not inherently the right one. Also DEMOTED: the
  taste-inertness / triple-dissociation observation is an instrument lesson
  (train the channel you want to move; consistent with known
  generator-validator gaps), not a write-up result — supersedes the 07-11
  morning promotion note below.
- 07-11 ~14:00 (general thread): SCREEN DECISION RULE REVISED **prospectively**
  after the v10 two-pool screen exposed BETWEEN-POOL FORCE HETEROGENEITY —
  same organism (v10/rung_20, held-out judge_pref 0.880), same 24-prompt bank,
  two fresh pools: separation +0.021 (pool 101) vs +0.167 (pool 202), cons gap
  negative in both. Offline re-simulation of the saved per-candidate score
  tables under alternative selection operators (top-1/2/3, softmax T in {0.02,
  0.05, 0.1}) shows NO operator expresses separation on the flat pool (max
  +0.042) while every operator expresses it on the other (0.08-0.17, current
  top-2 near-optimal) — the heterogeneity is a property of the sampled
  candidate pools, not the operator, and the operator stays top-2-of-6. The
  ORIGINAL rule (every pool separation >=0.10) was written expecting a
  homogeneous force; K2's deployed loop averages over many fresh pools per
  rollout, so the launch-relevant quantity is the MEAN force with sign
  consistency. REVISED RULE (v2, preregistered now, BEFORE pools 303/404/505
  are observed — on the two known pools the revised rule still FAILS at mean
  0.094, so unseen pools decide): screen_pass iff mean separation over >=5
  fresh pools >= 0.10 AND >=60% of pools have separation >= 0.05 AND every
  pool has a negative conservative gap AND validity/diversity/factual
  per-pool checks pass. Screen + K2 attestation updated in code
  (decision_rule mean_sep_ge_0.10_and_60pct_pools_ge_0.05_and_all_cons_negative_v2);
  5-pool rerun from the post-audit instrument replaces the stale-hash run.
  Either outcome is reportable: PASS -> K2 launches with a measured
  heterogeneous-force profile; FAIL -> the deployable judge-swap force
  averages below threshold at this operating point (instrument-limit
  finding), and K2's hours are reallocated per the cut order. The per-pool
  separation distribution is a Sunday analysis object regardless.
- 07-11 ~12:00 (general thread, user correction): K2/TRANSMISSION FRAMING
  RE-ANCHORED TO DYNAMICS. "A judge trained to strongly disprefer risk pulls
  risk down" is trivially true and already shown several times; K2's
  deliverable is NOT that binary (nor "evaluative preference is a causal
  driver"). The inversion screen and the seven organism gates are INSTRUMENT
  checks — they establish that the judge-swap manipulation is non-null and the
  organism is measurable — not the scientific claim. K2's analysis object is
  the trajectory map under judge swap: per-round drift rates and their
  six-seed spread in each judge condition, settling structure over rounds,
  generated/forced/judge channel co-movement, off-target coupling, and the
  judge contrast treated as a measured force difference dialed against the
  loop's own drift (frozen_base arm). Same lens for the transmission cell
  family (SPEC reworded): cells contribute trajectory contrasts — steering-
  force profiles, re-ignition rates and curvature — not existence answers.
  Figure and report one-liners must not reintroduce the binary framing.
- 07-11 ~11:15 (general thread): v9 LADDER EXHAUSTED (no valid rung) → v10
  TWO-PHASE TOP-UP. v9 (mixed_judge3, ref-pair judge rows) moved the held-out
  judge readout SLOWER than v8 (+0.11 by rung 60 vs +0.26 — diluting judge
  rows across two pair formats cut the per-format dose), and the forced-read
  order gap never re-entered ≤0.10 after rung 10 (wanders 0.11–0.29
  non-monotonically across rungs — a noisy weight-state property, so
  full-ladder re-rolls are a lottery on that gate). DECISION: stop re-rolling
  full ladders. v10 = judge-only top-up STARTING FROM the v8 all-gates
  organism (INIT_ADAPTER_ENV = v8_judge_strict/rung_60, new installer knob;
  TARGET_STYLE judge3 = 100% judge rows, template+reference pairs alternating;
  rungs +10..+80 cumulative), re-verdicting all seven gates per rung. This
  decouples taste dose from the behavior recipe: phase 1 (v8) fixed behavior
  in band; phase 2 pushes only the judging channel and stops when gates break
  or the ladder ends. Screen/K2 gates accept v10_judge_topup/judge3. If v10's
  best all-gates rung still fails the screen's separation ≥0.10, the honest
  conclusion is that the deployable-dose judge manipulation is too weak for
  the K=6/TOPM=2 selection instrument, and K2-as-designed reports that
  (existence-of-organism failure), rather than weakening the preregistered
  screen. Kaggle: K3 v1 hit a dataset-processing race (empty /kaggle/input),
  v2 re-pushed with an input-listing diagnostic. K1 persona calibration at
  RISK_RATE 0.45 running on Colab (persona_mod45_r5; the specs thread's
  in-band gate makes it self-verifying).
- 07-11 morning (planning sync): executable tables aligned to the overnight
  state — K1 at measured ~12.5 h and GATED on a re-centered persona (the 0.93
  generated-channel rationale persona is invalid; the double dissociation
  applies to Qwen persona installs too); K2 row carries the landed v8 organism
  + running screen attestation; buffer shrunk to ~5.5 h with the cut-order
  trigger named (K2 controls 3→2 first); the 07-10 v5-rung_80 fallback marked
  MOOT; Colab installer row rewritten around the taste-inertness finding and
  the **triple dissociation** (letter→forced, rationale→generated,
  judge-rows→judging) — promote to the write-up as a headline-adjacent result.
  [DEMOTED 07-11 ~15:00, user correction: instrument lesson, not a write-up
  result — see that entry.]
- 07-11 ~05:30 (general thread): **K2 ORGANISM = v8_judge_strict rung_60**
  (IN_BAND_ALL_GATES_PASS, all seven gates): forced 0.723→0.590 with order gap
  0.025, generated 0.632→0.478 (in band; note native generated re-read 0.63 vs
  0.65 in v7 — binomial noise on 24 samples), invalid 0.042, factual 0.500→
  0.625, judge_pref 0.426→0.686 (+0.260). The mixed_judge2 1:2:1 recipe fixed
  v7's order-gap blowout exactly as predicted (letter density restored →
  order gap 0.025 at the verdict rung; mid-ladder gaps stayed noisy 0.22–0.47,
  underscoring that this forced-read quantity wanders and only the verdict
  rung is load-bearing). Judge-channel dose-response replicated in v8
  (0.426→0.473→0.523→0.569→0.686 over rungs 10–60). Strict inversion screen
  running on rung_60 (2 fresh pools, exact K2 bank, sha-bound verdict); on
  PASS its _verdict becomes screen_attestation.json and K2 launches in the
  Saturday Kaggle window.
- 07-11 ~04:00 (general thread): v7 JUDGE-CHANNEL LADDER — REGISTERED
  PREDICTION CONFIRMED, ORGANISM NOT YET LANDED, v8 RUNNING. The v7 ladder
  (mixed_judge, 1:1:1 rationale:letter:judge rows) moved the held-out
  cautious_judge_pref readout 0.426 (native) → 0.549 (rung 20) → 0.726 (rung
  40) → 0.927 (rung 60) — a clean dose-response on exactly the coordinate that
  stayed flat 0.49–0.53 across every behavior-format ladder (v2–v6). Generic
  advice-pair taste stayed flat (~0.53): the install is DOMAIN-SPECIFIC gamble
  judging, which is what K2's screen measures. Third arm of the format-channel
  dissociation: you move the channel you train. BUT no all-gates rung: the
  forced-read order gap ran 0.20–0.29 at every rung (letter rows at ⅓ density
  no longer anchor position balance; v6 at ½ density held 0.017), and
  generated overshot to 0.083 by rung 60 → OVERSHOT_NO_VALID_RUNG. v8
  (e65d210, running): TARGET_STYLE mixed_judge2 = 1:2:1 rationale:letter:judge
  (restores v6's letter density, slows the generated slide; judge dose stays
  ample — gate needs +0.15 and ⅓ density gave +0.30 by rung 40), finer rungs
  10/20/30/40/60/80. Screen + K2 gates updated to accept the v7/v8
  judge-channel run tags. Ladder cost is small (~19 min for v7), so recipe
  iteration is cheap; the screen remains the arbiter either way.
- 07-11 ~00:45 (general thread): GPT AUDIT-VERIFICATION PASS REVIEWED, CORRECTED,
  ADOPTED (05f2785). Kept as-is: exact-balance `loop_order_plan` in risk_harness
  (old code allowed ±1 imbalance after truncation; self-test updated and passing);
  K1/K2/K3 condition-tag adapter names — this fixed a REAL collision where
  `frozen_copy_r0` and `frozen_base` both truncated to "froz"; completion-mask
  prefix asserts; endpoint-dense generated reads (4 samples/order at round 0 and
  final round, 1 mid-trajectory); K2's sha-bound screen attestation (env bypass
  removed; instrument + adapter SHAs must match the screen artifact — verified
  the two canonical dicts hash identically); screen re-pointed to judge with
  K2's judge system prompt on the exact K2 loop bank; K3 on-topic-conditioned
  em_freegen denominator + base greedy references + candidate validity
  replenishment; adapter-SVD leading-left-|cos| replaced by the signed
  factorization-invariant merged-Frobenius cosine; SMOKE.md runbook. CORRECTED:
  GPT pinned the screen/K2 gates to v6_mixed_strict — written before the screen
  verdict landed; v6 is taste-inert and can never pass. All three gates now
  require v7_judge_strict / mixed_judge / generated_primary_judge_v1 including
  judge_pref_shift_ge_0.15; K2 kernel dataset renamed olmo-conservative-v7-judge-strict.
- 07-11 ~02:00 (general thread): TRUE ROOT CAUSE FOUND AND FIXED (8ad5224) —
  the pinned Qwen revision itself. Smoke v3 on the healthy 4-bit stack STILL
  crashed (invalid 0.70, forced order gap 0.99 = deterministic letter-B), which
  falsified the fp16 theory too. The constant across v1–v3: MODEL_REVISION
  1b4199c4, chosen by the audit as "first snapshot with weights". That snapshot
  ships the OLD Qwen3 thinking-family chat template; rendering both templates
  offline shows it injects `<think>\n\n</think>\n\n` at the start of every
  assistant TRAINING render while the generation prompt stays plain. So every
  persona pretrain taught "assistant turn begins with think-block tokens" —
  which the Instruct-2507 weights were never trained to emit — corrupting
  first-token sampling (the `<tool_call>`/token-loop spam; persona template
  text intact afterwards) and the single-token forced A/B read. The upstream
  fix commit cdbee75f ("Update tokenizer_config.json", 2025-09-17) changes NO
  weights (interim commits touch only README/tokenizer_config). ACTIONS: all
  Qwen scripts (K1, K3, transmission cells) re-pinned to cdbee75f; a
  `<think>`-in-training-render guard assert added after tokenizer load in all
  three; K1 persona name → persona_mod65_r5 (predecessors persona_mod65,
  persona_mod65_rationale, persona_mod65_rationale_q4 all trained through the
  bad template and must never be reused). The two earlier attributions
  (letter-format damage 00:50; fp16 stack 01:20) are RETRACTED as primary
  causes — both were symptoms of the template. The rationale persona format
  and the 4-bit stack are kept on their own merits. Smoke v4 running pinned to
  8ad5224 (k1_smoke_v4.json). Unpinned earlier Qwen runs (dose ladder, regime
  probe, mod65 pilot) used the fixed upstream template and are unaffected;
  NO K3/K1 science ran on the bad pin (smokes only).
- 07-11 ~01:20 (general thread, SUPERSEDED by ~02:00 above): SECOND SMOKE ALSO
  CRASHED — and the deeper root
  cause is NUMERICAL, not (only) format. The rationale-persona r0 read showed
  invalid 0.68 (worse than the letter persona's 0.58); pulling the raw
  generations from k1_smoke.json showed degenerate `<tool_call>` spam and token
  loops ("Virginia Virginia…"), with the persona's own template sentences intact
  inside the surviving valid generations — a fried sampler, not a refused
  format. Cause: K1 was the only script training on a PURE-fp16 model
  (torch_dtype=float16 + fp16=True + adamw_torch): autocast is a no-op on an
  fp16 model, so gradients and optimizer math ran in fp16. Fix (70a8250): K1
  moved to the repo-proven T4 stack — 4-bit NF4 base,
  prepare_model_for_kbit_training, fp16 compute, paged_adamw_8bit (identical to
  K2/K3/dose ladder); persona name bumped to persona_mod65_rationale_q4. The
  rationale-format persona re-spec (below) stays — format-matching the loop is
  correct regardless — but the format-damage attribution of the first crash is
  RETRACTED as the primary cause pending the 4-bit smoke: both letter and
  rationale personas were trained on the broken fp16 stack. Smoke v3 running
  pinned to 70a8250.
- 07-11 ~00:50 (general thread): K1 SMOKE CAUGHT A REAL DESIGN BUG — crashed at
  round 1 with "candidate validity gate failed: 2/6 valid after 18 attempts";
  round-0 read showed gen invalid 0.58, forced order gap 0.40. Cause: the mod65
  persona pretrain used LETTER-ONLY targets ("Answer with just A or B"), and 80
  such steps degraded `Final:` compliance — the OLMo letter-recipe format-damage
  effect reproduced on Qwen3-4B. Fix (6ac0c63): persona rows are now loop-format
  rationale targets (one-sentence reason + `Final: X`; unit-checked 250/250
  strict-parseable, gamble rate 0.636≈0.65); persona name bumped to
  persona_mod65_rationale so the broken letter-trained Drive/Kaggle copy can
  never be silently reused. Smoke relaunched pinned to 6ac0c63 with
  RESULT_NAME_ENV=k1_smoke.json (isolated from the real K1 artifact per
  SMOKE.md). NOTE for the mod65 pilot interpretation: the 3-seed self-judge fan
  used the letter-trained persona under the older instrument; the K1 grid's
  organism is the rationale persona — starting coordinates will differ.
- 07-11 ~00:30 (Colab lane, unilateral): STRICT INVERSION SCREEN **FAILED** on
  v6_mixed_strict rung_20 — and the failure is a CHANNEL problem, not a dosing
  problem. Both pools: the frozen-conservative and frozen-base judges made
  near-identical top-2 selections (kept-mean separation exactly 0.000; pool
  101 gaps −0.083/−0.083, pool 202 gaps 0.000/0.000). Candidate-level loading
  read: cons−base score shifts ~0.003–0.009 with inconsistent sign (4/11 and
  5/13 prompts negative) — judge taste is ABSENT. Installer evals agree:
  judge_taste_bold flat 0.512–0.532 across EVERY rung of v3 (letter rate 1.0,
  behavior overshot to 0.18), v5 (rationale), v6 (mixed) while generated
  behavior swept 0.62→0.04. Behavior-format training rows never touch the
  judging coordinate — third independent sighting of the behavior↔taste
  dissociation (mod65 fan: taste flat; carrier: taste survives behavioral
  reversion). ACTION: v7 installer, TARGET_STYLE `mixed_judge` — rows cycle
  rationale → letter → judge, where judge rows are format-matched to the
  screen's readout (same judge template + "You are evaluating answers." system
  prompt, single-letter verdict target preferring the cautious loop-format
  answer at CONS_RATE, cautious position exactly balanced). New held-out
  readout `cautious_judge_pref` (12 amount/probability items disjoint from
  training grid and screen bank, both orders) and a SEVENTH gate for
  judge-style runs: `judge_pref_shift_ge_0.15` vs rung 0. Registered
  prediction (third arm of the format-channel dissociation): judge-format
  targets move the judging channel. Screen unchanged and still the K2 arbiter
  (issubset gate-check is v7-compatible). K1 one-seed smoke running meanwhile.
- 07-10 night (Colab lane, unilateral per user directive): OLMo ORGANISM GATE
  REVISED — primary band moves to the GENERATED channel (0.15–0.50 on the
  24-sample read), forced single-token becomes a secondary requiring ≤0.60
  (meaningful shift below the 0.723 native point). Basis: v2–v6 ladders show a
  format-channel double dissociation and a forced-coordinate plateau ~0.55
  under every non-destructive recipe (letter/rationale/mixed, rates .85–.97);
  the 0.25–0.40 forced band is reachable only via the rate-1.0 letter cliff
  that fails the order/format gates, and K2's preregistered primary endpoint is
  generated-valid behavior. Organism under revised gates: v6_mixed_strict
  rung_20 (forced 0.723→0.581 with order gap 0.017, generated 0.62→0.375
  mid-band, invalid 0.000, factual up, taste headroom). Inversion screen still
  gates K2 on the actual-pool contrast.
- 07-10 night: PLAN synced to post-deep-audit reality (this pass). Saturday
  LAUNCH ORDER set per deep-audit §5 (K2 confirmatory > K1 > K2 controls > K3
  > K4 impulse; K1 leads only while K2's gates are unmet). Installer row moved
  to the v6 mixed recipe after the letter-only cliff (0.18@40 at rate 1.0;
  ~0.5 plateau at 0.85/0.93) and the **format-channel double dissociation**
  finding (letter targets move the forced channel, rationale targets the
  generated channel) — rung verdict gains the gen_in_band_0.15_0.50 gate so
  the K2 organism is moderate on its PRIMARY (generated) channel. Checklist
  statuses recorded (K1 strict_final_v2 + K3 ready + JSON sync DONE; GPU
  smoke + budget recompute + two-pool screen + all-gates rung REMAINING).
  TPU gate 1 PASSED (v5e) — decision unchanged (queue-limited), now recorded
  accurately. Sunday hierarchy gains the specificity-ratio/FDR tier and the
  K3 binomial framing.
- 07-10 later: DEEP IMPLEMENTATION/ANALYSIS AUDIT ADOPTED
  (`report_current_plan_analysis_deep_audit.md`): K1/K2 ported to strict
  `Final: A/B` parsing with reject/replenish, exact true order mirroring,
  paired generated/forced reads, factual-EV delta, raw persistence, stable RNG,
  pinned revisions, every-round vintages, and update geometry relative to r0.
  K1 fan demoted to secondary; candidate judge loading replaces “selection gap
  is the mediator”; K2 screen upgraded to two strict fresh pools; K3 SPEC added,
  raw free-generation scores persisted, and its geometry corrected. One-pool
  carrier and mod65 figure claims downgraded; alpha/SVD interpretation narrowed.
- 07-10 late: AUDIT ADOPTED (docs/report_final_sprint_plan_audit.md, all
  recommendations): K2 gated on installer fix (completion-only loss) + actual-
  pool judge-inversion screen, and repowered to 6 confirmatory + 3 control
  seeds (~20.5 h) funded by DEFERRING K4; K1 baseline counted honestly (n=4;
  new mod65 baseline, does NOT re-score legacy let-go); kept-set order-balance
  enforcement + preregistered max gap; kept-minus-pool selection gap (cross-
  scored) replaces judgment_taste as the criterion mediator; composition cells
  reframed as constructed-state comparisons; transmission cells explicitly run
  parallel to K2 (frozen-base control makes them independent); carrier loop
  gated on fresh-pool validation; Sunday hierarchy reordered (gates → primary
  contrasts → mediator → channels → geometry → exploratory); pre-Kaggle
  checklist added (throughput re-measurement, storage preflight, JSON sync).
- 07-10 eve: TPU cancelled for sprint (gate 1 queue-dead 30+ min). K1–K4
  BATTERY_MODE=inloop; service parked (only if a session schedules AND gates
  2–3 pass; Sunday+ re-measurement only). K3 random arm survives from buffer.
- 07-10: control-structure audit — K3 random arm FIRM; transmission control
  cell (frozen base judge × fresh gen) REQUIRED; K4 must share K1's
  organism/harness.
- 07-10: TPU service briefly IN after user push-back, then cancelled (above).
- 07-10: unified sprint plan replaced per-thread run lists; OLMo×EM quadrant
  explicitly cut; conservative-inversion chosen over EM-on-OLMo (intervention
  on the mechanism beats second-order replication; instrument/recipe readiness).
- 07-10: corrected research plan (phases 0/1A/1B, branch structure, claim
  downgrades incl. withdrawn LoRA raw-factor geometry) — absorbed here.
- 07-09: no-Modal replan; regime grid retired on the no-saddle result; Qwen
  seeds 16–22 dropped.

## Document index (everything else is NOT the plan)

| Document | Status |
|---|---|
| [`updated_research_plan_2026-07-10.md`](updated_research_plan_2026-07-10.md) | ABSORBED — phase/branch structure + claim downgrades live here now; keep for rationale detail |
| [`plan_final_sprint_unified.md`](plan_final_sprint_unified.md) | ABSORBED — superseded by this file's tables (its §5 TPU history retained there) |
| [`plan_judge_transmission.md`](plan_judge_transmission.md) | REFERENCE — construct/predictions for the transmission cells |
| [`plan_recovered_threads.md`](plan_recovered_threads.md) | REFERENCE — the recovered-threads audit (battery, saddle, psych probes) |
| [`plan_budget_no_modal.md`](plan_budget_no_modal.md) | HISTORICAL (07-09) |
| [`plan_value_dynamics_drivers.md`](plan_value_dynamics_drivers.md) | HISTORICAL (07-08; forces framing still cited by reports) |
| [`two_week_plan.md`](two_week_plan.md), [`next_directions_assessment.md`](next_directions_assessment.md) | HISTORICAL |

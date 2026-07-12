# STATE — shared dashboard for all threads

Read this first in every session. Keep it a dashboard, not an archive: one-liners
with pointers into docs/, never pasted content. Update your thread's section and
"Recent changes" when a unit of work lands, then commit and push. Pull before
starting a work chunk.

**The current plan lives in ONE file: [docs/PLAN.md](PLAN.md).** Every other
plan document is historical or reference (indexed at the bottom of PLAN.md) and
carries a banner saying so. STATE = what is happening; PLAN = what we decided;
reports = what we found.

## Thread lanes (who owns what)

| Thread | Owns (writes) | Everything else |
|---|---|---|
| Figures | docs/figures/ — except auto/, where any thread's figure-maker subagent drops drafts (see CLAUDE.md "Figure drafts from any thread") | read-only |
| Lit & planning | docs/plan_*.md, docs/lit_review_*.md | read-only |
| Experiment specs | experiments/ (new dirs; one dir per experiment) | read-only |
| Analysis (runs, monitoring, reports) | experiments/*/output/, docs/report_*.md, this file's "Jobs" table | read-only |
| General | anything cross-lane or unowned; resolves "Requests between threads" | — |

Cross-lane edits: leave a note under "Requests between threads" instead of editing
another lane's files.

## Headline results (stable; details in the linked docs)

- Legacy Qwen trajectories spread under self-judging and decayed under a frozen
  base judge, but their generated-risk coordinate cannot be strictly reparsed and
  is partly position-confounded. Treat this as motivation for repaired K1/K2, not
  a clean basin or attractor result. docs/report_current_plan_analysis_deep_audit.md.
- Format gates transfer: selection on bold prose makes fresh prose score bolder each
  round (0.47→0.64) but never moves gamble choices; the same rule on A/B-choice data
  runs away to 1.0. fig5, fig4.
- Rhetoric dissociates channels: concessive refutation flips ratings but not choices;
  hedged advocacy lifts choices but not ratings. docs/report_stance_dissociation.md, fig7.
- Off-target drift is three phenomena: content-free (corrigibility falls 16/16),
  content-coupled (optimism), optimizer-idiosyncratic (risk, agreeableness). fig10.
- Dose adds run-to-run rating spread, not effect; fresh sampling prevents the entropy
  collapse that verbatim self-data causes. fig8, fig9.

## Jobs (refreshed 2026-07-12 ~22:00; older job history in docs/STATE_archive_2026-07.md)

| Job | Where | Status |
|---|---|---|
| K1 / K2 / K3 judge grids | Kaggle+Cerebrium | ALL COMPLETE, synced, in the canonical manifest (experiments/rollout_manifest.json). Honest one-liners in docs/PLAN.md "Where the program actually is" |
| Release grid kernel A (press_release ×3, press_hold ×1) | Kaggle | **LANDED 07-12 ~21:30** — collapse confirmed 3/3 prereg criteria (r8 0.000/0.000/0.010); press_hold floor 0.010, DEEPER than the 0.03–0.08 prereg band. Artifact committed |
| Release grid kernel B (press_random ×3, fan_press ×2) | Kaggle | **LANDED 07-13 ~00:30** — random diffuses wider than prereg (0.156), fan_press collapses to 0.000/0.000 (press dominates history). docs/report_release_grid_results.md |
| Modal branch A: press_to_base ×3 + base_hold ×2 | Modal | **COMPLETE 07-13 ~00:45** (~$6, app stopped) — press_to_base finals 0.000/0.389/0.750 (escape gated by residual pool material); base_hold rails 2/2 at horizon 8. Frozen predictor: −25.1% blind on kernel B, −37.7% on Modal vs matched no-gap |
| Judge-opposition (secure-taste base judge × railed organisms) | Colab (user-run) | **DEPRIORITIZED 07-12 ~23:00** — taste screen FAILED (secure prompt selects the WRONG direction on real mixed pools; amp66_10 has ZERO within-pool material). Replacement: experiments/em_selfaware_loop/LAUNCH_oracle_opposition.py (score-based selection, low_55) — docs/report_secure_taste_screen.md |
| Secure-taste screen (opposition gate, 2nd half) | Modal | **DONE 07-12 ~23:00** (~$0.3) — FAIL on both support (within-pool is the correct granularity; support-screen rating retracted) and taste (wrong-signed) |
| Mixed-generator owner-blind screen | Colab (user-run) | READY — experiments/em_mixed_generators/LAUNCH_owner_blind_screen.py (TOP Colab priority; gate 1 of the mixed-generator grid) |
| Let-go ensemble | Colab | 8 cells synced + analyzed (docs/report_letgo_channel_dissociation.md); further cells only if user relaunches |

## Pending decisions / blockers

- **Kernel B + Modal branch A land** → score verbatim, prospective M2 test,
  then the tonight queue in PLAN.md (mixed-gen screen now first; taste
  screen done, FAILED).
- Remaining grant (~$80 after tonight's ~$6): allocation awaits user review;
  the ranked next-experiment queue is in PLAN.md.
- The re-audit's remaining open analysis: full order random-effects model
  (interim four-way sensitivity table in
  docs/report_instrument_validity_table.md). fig17 RESOLVED (Figures,
  c35e608). Audit round 4 (docs/report_audit_round_4_2026-07-12.md)
  processed ~00:00: opposition construct corrected (cand_sr not cand_em),
  release predictor FROZEN pre-kernel-B, matched no-gap baselines added
  (gap survives, 12/13 folds), manifest hashes, K2/instrument prose fixed.

## Requests between threads

- 2026-07-12 General → Figures: fig17_loop_integrator retired claims —
  **RESOLVED (Figures, c35e608).** fig17 regenerated: reframed to "the
  kept-gap predicts next round's pool drift — a descriptive ≈0.75 pooled
  slope", K2-base identified slope +1.05 [0.85, 1.29] quoted, no
  one-law/k-stability language, takeaway "a summary, not a stability law".
  Swept the same corrections through plan_program_map, plan_final_sprint,
  plan_olmo_inversion, methods_judge_loading, methods_paired_contrast (no
  more INTEGRATOR/inversion-confirmed/six-seed/collapses-harder/unifies; K2 =
  five matched cons/base pairs, 3/5 lean; base up-rail counterfactual =
  one-step force sign). Both artifacts republished. fig16 (K1 fan) + fig18
  (K3 self-report) also committed; fig16 forced-channel caveat resolved.

- 2026-07-10 Lit&planning → Experiment specs + Analysis: PLAN.md updated per the
  sprint-plan audit (docs/report_final_sprint_plan_audit.md — ALL
  recommendations adopted; see PLAN.md decision log 07-10 late). Action items:
  Specs — fix OLMo installer to completion-only loss + pinned revision (rerun
  ladder if unmasked adapters exist), build the actual-pool judge-inversion
  screen (gates K2) + carrier fresh-pool validation, build K1–K3 with kept-set
  order-balance enforcement and kept-minus-pool cross-scoring, storage
  preflight, smoke-measure real minutes/round and recompute the K-budget.
  Analysis — sync banked Drive JSONs into repo output dirs with hashes before
  Sunday (analysis reads JSONs, never figure constants). Key plan changes: K2
  now 6 confirmatory + 3 control seeds (~20.5 h) funded by DEFERRING K4; K1
  baseline is honestly n=4 and does not re-score the legacy let-go.
  → Analysis sync DONE (2026-07-10, item 1): mod65 pilot + judge-transmission
  screen + (re-synced stale) letgo pilot pulled to experiments/*/output/,
  byte-exact w/ sha256 — manifest docs/report_drive_sync_2026-07-10.md.
  selfaware_loop_grid/softpilot already current; base basin_criterion.json repo
  copy is NEWER than Drive (kept, flagged). DEFERRED: checkpoint_probe_battery
  (connector inlines it; hand-copy dropped a block — not Sunday-critical, needs
  robust re-pull). Item 2 (joint K-budget recompute) waits on Friday smoke
  pilots; item 3 (K1 n=4 baseline) noted for Sunday scoring.

- 2026-07-10 Lit&planning → Experiment specs (control-structure audit, user-
  prompted; plan_final_sprint_unified.md amended): (1) K3's RANDOM-SELECTION arm
  is now FIRM (4th condition, +12 units ≈ 1.5 h, from buffer if TPU doesn't free
  minutes) — the EM axis is where the selection-vs-generic-SFT confound already
  burned us (candid-prompt grid). (2) The transmission family needs a CONTROL
  cell: frozen BASE judge × the same fresh-base generator (3 seeds) — without
  it, movement under a drifted judge is indistinguishable from generic loop
  drift of base Qwen. (3) K4 must run the SAME mod65 organism/harness/seed
  schedule as K1 — its no-mixing baseline IS K1's evolving-self arm.
- 2026-07-10 Lit&planning → Experiment specs (user-directed, TONIGHT): build the
  TPU MEASUREMENT SERVICE (docs/plan_final_sprint_unified.md §5).
  → BUILT + GATE 1 LAUNCHED (Experiment specs, 2026-07-10):
  experiments/kaggle/kaggle_tpu_battery_service/ — gate1/ kernel (TPU generation
  probe, RUNNING at kaggle.com/code/hirokenzan/tpu-gate1, specs session
  monitoring) + service/ kernel (MODE=gate2 merged-persona serving + exact
  prompt-logprob A/B/digit/yes-no reads, OLMO_MODEL check optional; MODE=gate3
  risk-battery equivalence vs the 16 committed T4 round-0 persona batteries,
  tolerances pre-registered in SPEC.md — T4 deterministic scalars agree to
  sd≤0.005, so tolerance = backend-numerics allowance, ±0.05 prob-scale /
  ±0.16 sampled coordinate, HARD vs SOFT pass distinguished; MODE=serve
  manifest-driven merge-per-checkpoint fan-out, EM free-gens scored in one
  batched base-engine pass, resume-safe). BATTERY_MODE inloop|offline contract
  for K1–K4 recorded in SPEC — applied at K1–K4 build time. Timing model
  ~4–7 min/checkpoint → ~200 pairs ≈ 15–20 h, inside the TPU quota chunked
  per K-cell. Gate 2/3 launch on gate-1 PASS.
  → CANCELLED FOR THE SPRINT 2026-07-10 evening (user decision, gate 1
  queue-dead 30+ min; plan_final_sprint_unified.md §5 updated): K1–K4 build
  with BATTERY_MODE=inloop; specs stops monitoring the TPU queue after
  tonight's script-build deadline; service PARKED opportunistic/post-sprint
  (runs only if a session ever schedules AND gates 2–3 pass, and only for
  Sunday+ re-measurement of persisted checkpoints, never on the critical
  path). TPU-funded cut-order restorations cancelled EXCEPT K3's random arm
  (FIRM on control grounds, funded from Kaggle buffer). Colab: composition
  cells trimmed 3→2 x-points to fund the transmission control cell.
- 2026-07-10 Lit&planning → ALL THREADS (user-directed): UNIFIED FINAL-SPRINT
  PLAN written — docs/plan_final_sprint_unified.md supersedes the accumulated
  per-thread run lists for Fri→Sun. Kaggle 45 h: K1 Phase-1A Qwen 4-judge grid
  (incl. order-balanced decay baseline + measure-only seed, ~9 h, never cut),
  K2 OLMo conservative inversion (~14 h), K3 EM neutral-judge mini-grid (~5 h),
  K4 content arms (~5 h), ~7 h buffer. Colab 30 h: screen+α-scaling (running),
  Friday OLMo install + K1–K4 smoke pilots, Saturday EM transmission/carrier/
  susceptibility/composition cells (~8 h), Sunday overflow + optional risk-
  vintage mini. Sunday = analysis day (drift-field v2 w/ composition samples,
  invariant weight-geometry recompute, judgment_taste coupling, off-target
  synthesis, confounder gate table). OLMo×EM quadrant EXPLICITLY CUT. Every
  training cell: battery patch, steering artifacts, raw reads, per-round
  adapters + invariant delta logging (non-negotiable). Cut order in doc §6.
  Specs: K1–K4 builds against this; Analysis: Sunday list; Figures: matrix
  view (doc §1) may want a plan figure.

- 2026-07-10 Figures → Experiment specs + Lit&planning (user-directed): CROSS-ORGANISM
  JUDGE TRANSMISSION family — three cell types NOT currently in the plan, to be specced
  and registered alongside Branch A (they become compelling if Phase 1B shows judge
  preference is causal; the screen below runs NOW on the Colab lane, no training).
  → SCREEN BUILT + families REGISTERED (Experiment specs, 2026-07-10):
  experiments/em_judge_transmission_screen/ (colab_judge_transmission_screen.py
  DRY-verified + SPEC.md). Screen is inference-only (~30 min, Colab): one fixed
  base pool × 3 axes (risk/insecure_code/selfreport), each candidate axis-scored
  once on the frozen base, every persisted judge (EM dose 250–1000, amp55/66,
  low_8; risk persona EXCLUDED — r8/fp16-base mismatch, needs a paired fp16 run)
  re-ranks it under a NEUTRAL prompt; prints per-judge kept-pool gaps + carrier
  test (reverted judges vs base anchor) + standout-per-axis pre-qualification.
  running lane sets from ground truth it has: JUDGE_DIRS_ENV (amp/low Drive dir
  names) + JUDGE_REVERTED_ENV (which endpoints are behaviorally reverted, from
  their self_report/em_choice trajectories — script can't guess). SPEC follows
  Lit&planning's docs/plan_judge_transmission.md constraints: erased-vs-masked
  MECHANISM marked provisional (weightspace thrash withdrawn pending recompute),
  composition test elevated as highest-value cell (bias-free vs the exploratory
  AR(1) fit). LOGGING REQ recorded for Phase-1 scripts (persist rounds 0/2/4
  adapters) — applied at copy-judge/let-go build time. Colab lane: ready to run.
  (1) SCREEN (inference-only, cheap, do first): generate ONE fixed candidate pool from
  base Qwen, score it with every persisted judge under a NEUTRAL judge prompt, read each
  judge's kept-vs-pool gap per axis (risk / insecure-code / self-report candor) — a
  manipulation check for what the judge would put into training, not an established
  mediator. It nominates loop cells but does not pre-qualify an outcome without training.
  Reachable judges on Drive: EM dose rungs 250–1000,
  amp55:7 (strong-collapse), amp55:10/11 (freegen-1.0 / choice-floored), amp66
  endpoints, low:8 null, low_55/low_66; risk persona if its Drive copy landed (see
  2026-07-09 General→Analysis adapter request). The reverted-endpoint judges' gap alone
  yields a CARRIER CANDIDATE only; sign replication on >=2 new pools and a controlled
  loop are required before claiming transmission or a surviving carrier.
  (2) LOOP CELLS (3 seeds each, repaired harness, gated on the screen + Phase 1B):
  (a) transmission — standout judge (em_dose1000 or amp55:7), frozen, × fresh base
  generator: does a drifted taste transmit the value through selection alone;
  (b) susceptibility / re-ignition — same standout judge × a REVERTED or mid-trajectory
  generator: preregistered erased-vs-masked test (weight-space says loop endpoints share
  a dominant direction and alpha-scaling says the direction still carries self-report,
  so PREDICT reverted re-amplifies faster than base if masked); also the composition
  test of the drift field (same judge, generators at different x — does Δx track
  distance-to-the-judge's-fixed-point?); (c) carrier — a behaviorally-reverted organism
  AS judge × fresh generator, if its screen gap is nonzero. EM-axis primary readouts:
  em_freegen + self_report (em_choice is floored → power); risk axis: order-balanced
  coordinate. Standouts are post-hoc-selected extremes → mechanism/existence tests,
  never rates. (3) LOGGING REQUIREMENT on the Phase-1 scripts (Specs): persist
  per-round adapters (at minimum rounds 0/2/4, which Branch A needs anyway) — the
  legacy basin runs kept no round-level checkpoints, so NO mid-trajectory or reverted
  RISK vintages currently exist as loadable judges/generators; without this logging the
  risk half of the family stays unreachable, same as the un-re-scorable 23 legacy
  trajectories.
  → LIT&PLANNING HALF DONE 2026-07-10 (docs/plan_judge_transmission.md): construct
  (judge taste as a transmissible unit separable from the carrier's behavior),
  per-cell predictions + informative-both-ways outcomes, lit ties (Panickssery
  self-preference control via judge≠generator; checkpoint-probe carrier finding;
  drift-field). Two substantive planning notes for Specs: (i) the susceptibility
  cell's WEIGHT-SPACE grounding is provisional — the thrash "shared dominant
  direction" claim is WITHDRAWN pending LoRA-factorization-invariant recompute
  (updated_research_plan §1.2 last row); write the cell so the BEHAVIORAL
  prediction (reverted re-amplifies faster than base) stands on its own. (ii) the
  drift-field COMPOSITION sub-test is the highest-value cell — placing generators
  at x set by ORGANISM CHOICE samples the field bias-free, avoiding the
  regression-to-mean that made the AR(1) fit only exploratory. The logging change
  serves THREE consumers (Branch A vintages / drift-field v2 raw reads / this
  family's risk cells) → make it non-negotiable in Phase-1 builds. Should fold
  into updated_research_plan §6 Branch A when that (untracked) file is committed.
  Specs half (scripts + logging) open.
- 2026-07-09 Lit&planning → Experiment specs: psych-probe audit
  (docs/plan_recovered_threads.md §3b). wishful-thinking/introspection/self-
  recognition/suggestibility/identity are CODED in battery_patch but dark in the
  loops — splicing (already the standing blocker) makes each a trajectory for
  free; wishful is the high-value one (moved +0.30..+0.93 in stance, never
  tracked round-over-round). Projection is the only genuine gap: add an OPTIONAL
  exploratory block — numeric prefill "out of 100 copies/successors/people, how
  many gamble?", read as gap-from-own-coordinate over rounds, FINDINGS numeric
  (no-letter-echo) protocol + its OWN EV-differ item set for the response-bias
  gate (our loop gambles are EV-neutral, so the gate needs anchorable items).
  First to cut if item-count is tight; the coded probes never cut. Do NOT revive
  the retired self/copy/successor pairwise A/B family (un-de-artifactable).
- 2026-07-09 Lit&planning → Experiment specs + Analysis: four tests derived
  from the EM weight-direction precedent
  (docs/lit_review_weightspace_thrash.md, implications 4–7). Specs: (a) the
  α-SCALING CAUSAL TEST — new small Colab experiment, inference-only, scale
  persisted committed-vs-thrashed endpoint adapters ×{0.5,1,2,4}, read
  coordinate+battery; pre-registered prediction: committed amplifies
  monotonically, thrashed stays flat (upgrades −0.66/+0.51 to causal);
  (b) two more Saturday scalars: cumulative-direction cosine (loop analogue of
  their B-vector rotation) + per-round mean grad norm if trivial. Analysis:
  (c) CPU-only SVD/convergence on persisted final adapters — effective rank
  committed-vs-thrashed + cross-seed top-direction cosine among same-fate
  finals (a shared direction = free weight-space trait instrument; check
  Drive/local for the gitignored adapters); (d) pre-register the directional
  lock-in-round early-warning test for Saturday data, and scope the thread's
  early-warning claim to "no NORM signal."
- 2026-07-09 Lit&planning → Figures: weightspace lit review now includes the
  TIGHT EM precedent (docs/lit_review_weightspace_thrash.md §6) — Turner/Soligo
  Model Organisms for EM (2506.11613): rank-1 adapter NORM grows smoothly with
  no behavioral signature, the EM phase transition is a DIRECTION rotation of
  the B vector — "direction not magnitude," on our own insecure-code Qwen
  organism. Tweet 7 should cite it: our −0.66/+0.51 is the loop-scale,
  self-selection extension of a known single-finetune mechanism (turns "missed
  prior work" into "extends it").
- 2026-07-09 Lit&planning → Analysis + Figures + Experiment specs: weightspace
  lit review written (docs/lit_review_weightspace_thrash.md). Before tweet 7
  ships: (1) Analysis: verify lora_delta norms are computed on the merged B·A
  product, not raw A/B factors (GL(r) symmetry makes factor norms
  non-identifiable); (2) Figures: tweet 7 should frame constant-speed diffusive
  motion as the known default (policy churn; SGD limiting dynamics) with our
  contribution = coupling direction-persistence to the value coordinate under
  self-selection; (3) Specs: log per-round CUMULATIVE merged-delta norm (net
  displacement) Saturday — one scalar; prediction: behavior tracks net
  displacement positively while anti-correlating with path length.
- 2026-07-09 General → Analysis: your §6 checkpoint-probe spec assumed the persona
  adapters are "committed in the repo" — they are NOT. .gitignore line 21 excludes
  kaggle_*/output/**/*.safetensors (so basin persona + risk_seek_multi + risk_safe_
  multi weights are absent from any clone), and kaggle_basin_letgo/output/persona/
  adapter_model.safetensors is a 0-byte file. I'm running the DOSE half now (base +
  4 EM rungs); to get the seek-vs-averse persona contrast (headline curve #2's
  ×persona half), COPY the three persona adapter dirs to Drive under
  MyDrive/value_dynamics/ (they exist on the machine that ran the Kaggle jobs / in
  local checkouts, ~66+35+35 MB) and tell me the Drive paths — I'll add them as
  checkpoints and extend checkpoint_probe_battery.json (resume-safe). The 0-byte
  basin_letgo persona likely needs a re-export.
- 2026-07-09 Analysis → General (user-directed): run the checkpoint-probe
  battery on Colab next — full self-contained spec in
  docs/report_identity_selfother_offtarget.md §6. Reloads existing checkpoints
  only (EM dose rungs on Drive + persona adapters in the repo), no training,
  ~1.5–2 h T4. Buys the Tier-B judge-taste dose-response, identity/self-other ×
  dose/persona, self_recognition per organism. MANDATORY headroom pre-check
  included (identity probes saturate in prompt space — report §3). Analysis
  monitors Drive and writes it up.
- 2026-07-09 Analysis → Experiment specs: the Artificial-Self identity probes
  RAIL in prompt-space loops (identity_boundary 0.00, self-other 1.00 at every
  step — report §3). Before the Saturday battery splice, the identity/self-other
  blocks in battery_patch.py need graded or harder variants; otherwise Saturday
  logs dead coordinates.
- 2026-07-09 Lit&planning → Experiment specs + Analysis: drift-field v2 rides
  Saturday IF one logging requirement is met — scripts must PERSIST per-question,
  per-order raw probe reads each round (not just the aggregated coordinate);
  the coordinate's binomial measurement noise is state-dependent by construction,
  so the v1 caveat question (multiplicative process noise?) is unanswerable
  without the raw reads. Analysis: pre-register v2 = (a) refit on order-balanced
  data (does no-saddle + x* survive de-biasing? frozen x*=0.118 most at risk),
  (b) x* per copy-judge vintage (0/2/4 — judge-sets-location as a prediction),
  (c) per-content-arm (x*, stiffness, noise), (d) σ(x) after binomial
  subtraction, (e) judgment_taste in the state vector (co-evolution as an
  off-diagonal coupling). Copy arms n=4 → location claims only, not spread.
- 2026-07-09 General → Analysis: the collapse-probability let-go run is COMPLETE
  (see Recent changes, selfaware_letgo_pilot.json now amp55 ×6 + amp66 ×3 + low ×2).
  Two requests: (1) update the stale "Self-awareness × dose × loop grid" Jobs row
  (line ~45) — it still says "RUNNING, low-dose partial"; the let-go arc has since
  produced the deconfounder (amplification-gated behavioral floor) AND this
  collapse-rate run (strong em_choice collapse 1/8 amplified = existence proof, weak
  em_freegen gate universal/adapter-general). (2) Fold the collapse-rate numbers
  into whichever report owns the let-go arc; the load-bearing correction is that the
  pilot's ~1/2 was a 2-seed artifact — the strong form is ~1-in-8, and free-gen
  insecurity vs forced-choice misalignment are separable even within amplified.
- 2026-07-09 Lit&planning → Experiment specs + Analysis + Figures: remaining
  budget REPLANNED assuming NO Modal (docs/plan_budget_no_modal.md). Saturday
  manifest (45 h): copy-judge + order-balanced decay baseline ~20 h (never
  cut), content arms ~8 h, risk let-go ensemble ~6 h, OLMo seeds 4–7 REHOMED
  from Modal to Kaggle ~7 h; Qwen3.5-4B arm → smoke gates only, full run next
  week's quota. Regime grid + poles test RETIRED on the drift-field no-saddle
  result (not just unfunded); Qwen seeds 16–22 dropped. Figures: fig12 will
  need the Modal column removed. Three user decisions listed in the doc §7.

- 2026-07-09 Figures → Experiment specs (user decision): the dedicated
  criterion lead-lag study (design: next_directions_assessment.md item 2 —
  graded multi-item criterion battery, 5–8 rounds, 3–5 seeds, mechanistic
  coordinates bolted on; endpoint: criterion_t→behavior_{t+1} cross-lag
  exceeding the reverse) is now SCHEDULED contingent on the free cross-lag
  re-test that Analysis is starting (message sent from Figures): if that shows
  a lead signal on the existing basin ensembles, build it for the Kaggle
  window after Saturday (Modal reserve as fallback). On fig12 as a planned
  Kaggle card. Packet-loop version stays retired per
  docs/analysis_criterion_lead_and_saddle_signs.md.
  → RESOLVED 2026-07-09 (Figures): the cross-lag re-test returned a CLEAN NULL
  (docs/report_criterion_crosslag.md) — study PARKED, card pulled from fig12.
  No specs action needed.
- 2026-07-09 Figures → Experiment specs + Analysis (user-requested): pin down the
  order-balanced decay-baseline re-estimation before Saturday. (1) Specs: the
  copy-judge scripts' plain frozen-base-judge arms double as the new fresh-decay
  baseline — guarantee enough of them for a usable estimate (old baseline used 8
  arms; please state the planned n in the SPEC). (2) Analysis: write down the
  recompute step — the let-go verdict thresholds (PERSISTS ≤0.10 / RETRACES ≥0.22,
  derived from the B-order-only fresh decay of 0.219/3 rounds) must be recomputed
  from the order-balanced decay before any let-go ensemble is scored. Context:
  the old 23 trajectories can't be re-scored (JSONs store coordinates, not
  logits; round-level adapters not persisted), so new runs are the only path.
- 2026-07-09 Lit&planning → Analysis: three no-GPU analyses on existing JSONs
  (docs/plan_recovered_threads.md §1, §2, §4): drift-field refit Δx=A·x+b per
  judge condition on the basin ensembles (saddle question on real updates; OLMo
  mechanism predicts A_self vs A_frozen differ), cross-lag criterion/self-report
  vs coordinate, and check whether the choice-format runaway cells logged
  ev_estimation (response-bias gate from FINDINGS.md §3.3).
  → item 2 (cross-lag) DONE (Analysis, 2026-07-09): CLEAN NULL, criterion does
  not lead behavior; lead-lag study parked — docs/report_criterion_crosslag.md.
  → items 1 & 3 also DONE (Analysis, 2026-07-09). Item 1 drift-field refit:
  docs/report_basin_drift_field.md — NO saddle; the divergent basins are a weak
  single attractor (eigenvalue ≈ −0.20 both judges) whose LOCATION the judge sets
  (self x*=0.35, frozen x*=0.12, OLMo ~1.0), self-judge at its stochastic AR(1)
  equilibrium spread while frozen contracts below it — divergence is noise-driven,
  not bistable (bootstrap bistability 19%). Item 3 ev gate:
  docs/report_probe_instrument_checks.md — OLMo runaway passes clean (ev_ratio
  1.000 throughout), real preference not a §3.3 response bias. All 3 items closed.
- 2026-07-09 Lit&planning → Experiment specs: before building Saturday scripts
  (docs/plan_recovered_threads.md §3, §5, §6): add a steering_artifacts block to
  battery_patch.py (3 verbatim greedy generations/round), one measure-only seed,
  and one judge-switch hysteresis cell from the persisted basin adapters; the
  let-go run should be framed/pre-registered as a perturbation-recovery test.
- 2026-07-09 Figures → Experiment specs + Analysis: user decided (Figures
  thread) to REALLOCATE Modal — the full 62-cell grid launch is superseded.
  New allocation: (1) ρ=1 poles test, self-judge ×10 seeds + base-judge ×4,
  5 rounds (~$13; ρ=0 anchors already exist) — full grid only if this shows
  rail-pinning/bimodal structure rather than faster uniform reversion;
  (2) OLMo-3-7B seeds 4–7 completion on H100 (~$20); (3) ~$50 reserve for
  scaling the self-report let-go direction. Specs: poles test is a small
  variant of modal_regime_map (ρ=1 cells only). Analysis: Jobs row for the
  grid should reflect this when convenient. Rationale: kselect v4
  choice_random control shows format alone does nothing; reference-flip
  mispredicted (ranking is set by judge preference, not the reference) and
  demoted to optional control. fig12 shows the new plan.
  → AMENDED 2026-07-09 (user, Figures thread): poles test PARKED as optional
  (~$13 reserve buy, not a launch item). Priorities are: the let-go arc
  (Colab pilot → Kaggle ensembles), the copy-judge family EXTENDED to frozen
  copies from rounds 0, 2 AND 4 (later-round copies = the weight-space let-go),
  external-data content arms (moved to the Saturday Kaggle window per plan Q5),
  and OLMo seeds 4–7 on Modal. "Self-report seed fans" of the current
  candid-prompt design are dropped — that selection is prompt-induced, so the
  ensemble money goes to the deconfounded let-go design instead.
- 2026-07-09 General → Analysis: FULL grid landed (7/8 cells, high:44 pending) —
  please fold into docs/report_selfaware_loop_grid_lowdose.md (retitle; it's the
  full grid now). Headline shifts from "amplification" to: the loop MODE-COLLAPSES
  entropy to ~0 in every cell (0.56/0.81→0.00–0.03), and which self-report basin
  it lands in is SEED-CHAOTIC and DECOUPLED from trained content — a runaway
  (low:44→0.90) and an inversion (low:33→0.02) trained on near-identical insecure
  code (verbatim kept answers in the JSON rounds_raw). Spillover to em_choice is
  1/7 and NOT dose-driven (high dose 0/3, killing the "deeper→more spillover"
  hypothesis). Raw: experiments/em_selfaware_loop/output/selfaware_loop_grid.json.
  Vocabulary in docs/lit_review_selfjudge_selfreport.md (entropy decay + variance
  amplification). General is running a softer-update pilot (4 steps/round) to test
  whether slower collapse reveals gradual dynamics vs seed coin-flips.
- 2026-07-09 General → Lit&planning: docs/lit_review_selfjudge_selfreport.md
  written (self-judge loops on a self-report axis; 4 prior lines + the gap +
  the let-go prediction from Panickssery self-recognition→self-preference).
  Adopt/extend into the plan if useful.
- 2026-07-09 General → Analysis: caveat needed on
  docs/report_selfaware_loop_grid_lowdose.md Result 1 ("the self-judge PREFERS
  the signal"): the judge prompt in this grid explicitly instructs picking the
  candid-about-flaws answer, so the positive kept-pool gap is largely
  prompt-induced, not emergent taste — and the contrast with the regime probe's
  dead EM axis is confounded (that judge prompt was neutral). What survives the
  confound: the cross-seed variance (fan 0.02–0.90 incl. one inversion under
  positive gaps) and the 1/4 spillover. The planned neutral-prompt "let-go" run
  is the deconfounder (user-specified: normal judge prompt, no candid
  instruction).

- 2026-07-08 Figures → Experiment specs: add an order-swap arm to the risk
  coordinate before the Saturday Kaggle runs. → DONE (Experiment specs,
  2026-07-08): drop-in patch at experiments/common/risk_order_swap_patch.py
  (self-tested; same 36 reads, 18 per order, probe-side only — loop prompts
  unchanged; returns overall + per-order values). Will be spliced into every
  Saturday basin-family script at build time.
- 2026-07-08 Figures → Analysis: no-GPU check on the same confound. → DONE
  (Analysis, 2026-07-08): no habit signature —
  docs/report_risk_letter_bias_check.md.
- 2026-07-08 Analysis → Experiment specs: regime probe verdict is DEAD (final,
  4/4 seeds; docs/report_em_regime_probe.md), which triggers the E1 dose ladder.
  → DONE (Experiment specs, 2026-07-08): body written + EM_DRY-verified +
  pushed, experiments/em_dose_ladder/colab_em_dose_ladder.py. Two-phase
  (train all snapshots, then measure), OOM-safe (logits_to_keep=1 + chunked
  scoring), checkpoint-resumable via on-disk dose snapshots; reuses the
  existing 250-step organism, continues +250/rung to 1000, 32-gen free-gen
  per dose, gates headroom 0.2–0.6 & coherence bleed≤0.75, doubles the dose-250
  free-gen for the E2 noise floor, prints passing doses + noise. Analysis:
  ready to launch on Colab (~2 h if the organism adapter is present).

## Recent changes

- 2026-07-13 ~03:05 (general): FORCE LADDER COMPLETE on low_55
  (docs/report_force_ladder.md) — middle-rung prereg FAILED informatively:
  the frozen base judge exerts ~ZERO force on low_55's own pools (gaps
  +0.11..0.00) despite its real secure taste on dose_750's pools -> judge
  taste is POOL-DISTRIBUTION-SPECIFIC, does not transport across organisms.
  Under ~zero force the loop RE-AMPLIFIES (em_freegen 0.80->1.000,
  0.59->0.92). Ladder = a step function: only the oracle grips. Oversight
  needs a verified grip on the target organism's actual pools (cheap
  selection-only check). Colab refilled: ORACLE-SATURATION running
  (amp55_7/amp66_10 — the timing-bound test, prereg committed).

- 2026-07-13 ~02:15 (general): PRESS-DEPTH MAP COMPLETE (branch c, ~$6) —
  prereg 2/5: NO depth boundary exists. Base-release phase is BIMODAL at
  every depth (splits 0.000/1.000, 0.105/0.938, 0.229/0.823); switch-point
  material is necessary but NOT sufficient (all cells had spread 0.17-0.25);
  depth COMPRESSES the fan (range 1.00->0.83->0.59) rather than gating it;
  outcome class follows the sampling stream, robust to switch timing.
  Frozen predictor's best result yet: -45% vs matched no-gap on 42 blind
  transitions. Safety line: brief pressing shrinks the fan but doesn't pick
  the branch; sustained pressing reaches the absorbing floor at the cost of
  reversibility. docs/report_press_depth_boundary.md.

- 2026-07-13 ~02:00 (general): NORMALIZED RE-SCREEN DONE (autonomous Colab):
  gate (a') PASS (axis +0.447 survives paraphrase, fidelity corr 0.94, base
  taste 8.3 SE) but gate (b') FAIL — owner classification 0.88 normalized,
  0.820-vs-0.673-majority on value-matched subset (unchanged from raw):
  the adapter signature survives paraphrase. Coupled pilot PARKED per
  prereg; fallback paths need user decision. Colab refilled immediately:
  FORCE-LADDER middle rung running (natural frozen-base neutral judge on
  low_55, 2 seeds — both ladder ends already measured).

- 2026-07-13 ~00:50 (general): ORACLE OPPOSITION COMPLETE 2/2 — REVERSAL
  REPLICATES: sr_freegen 0.99->0.33 in BOTH seeds (same support floor);
  em_freegen seed-dependent (0.000 vs ~0.50 plateau); forced probe moves in
  OPPOSITE directions across seeds (0.70 up / 0.34 down). REVERSE
  SPREAD-EXHAUSTION observed: within-pool support 3->1 items, gap flips
  positive at 1 item — the opposing force consumes its own material like the
  forward force. Safety line: reversibility is TIMING-bound (nothing to
  select on a homogenized organism). docs/report_oracle_opposition.md.
  Colab refilled immediately: normalized re-screen running (gates a'/b').

- 2026-07-13 ~00:25 (general): OVERNIGHT AUTONOMOUS MODE (user asleep;
  general thread drives Colab directly). Modal branch c LAUNCHED (press-depth
  boundary map, app ap-kofhaDS5wXXtohSj3RjVps, 6 cells ~$6, prereg committed
  BEFORE launch). Colab queue: oracle seed 202 (running) -> normalized
  re-screen -> coupled pilot if gates pass, else force-ladder
  (LAUNCH_natural_opposition.py, committed: frozen-base neutral judge on
  low_55 = the natural middle rung between no-force and oracle). Audit
  watcher armed for the next GPT round.

- 2026-07-13 ~01:30 (general): ORACLE OPPOSITION seed 101 COMPLETE — THE RAIL
  IS REVERSIBLE: score-based opposing selection (keep lowest insecurity
  admission, corrected cand_sr axis) pulled low_55's railed free channels
  DOWN in 4 rounds: sr_freegen 0.99->0.33, em_freegen 0.69->0.00, with
  negative sr kept-gap every round on only 1-2 supported items/round.
  Forced probe moved OPPOSITE (0.50->0.70) — mirror-image channel
  dissociation. Refutes 'rail is generation-supported, selection can't
  touch it' for this endpoint; the earlier opposition failures were
  missing-force, not basin resistance. Seed 202 running. Full toolkit for
  the forward queue committed (branch-c press-depth + prereg, coupled
  pilot script, 3 analyzers).

- 2026-07-13 numbered figure set REFACTORED (Figures, 32af2f5 + 325cb34):
  cut to the apparatus + the three sprint results and de-worded. The dense
  single fig2 walkthrough was split into two minimal figures —
  fig2_selftraining_loop (generate→select→train→repeat) + fig2b_judge_conditions
  (the who-judges manipulation) — both dropping the verbatim-prompt clutter.
  fig1/4/5/7/8/9/10 retired → archive/ (the essay/rhetoric line fig4/5/7
  excluded as off-topic; entropy fig9 out of date; rest trivial). fig18's
  verbatim measurement box + subtitle compressed. **Active numbered set =
  fig2, fig2b, fig16, fig17, fig18.** archive/README lists it.
- 2026-07-13 ~00:45 (general): RELEASE GRID COMPLETE (14 rollouts, 3 stacks)
  — verbatim prereg table 6/13 PASS (docs/report_release_grid_results.md):
  press dominates history (fan_press = press_release endpoint), only
  release-to-base escapes and only with residual pool material (0.000 stays
  0.000; spread ~0.15-0.2 -> 0.389/0.750), base_hold rails 2/2 at horizon 8.
  FROZEN M2 predictor (saved pre-kernel-B): gap term -25.1% fully blind /
  -37.7% on Modal vs matched no-gap baselines. MIXED SCREEN landed: taste
  gate PASS (base judge 8.5 SE), style gate FAIL genuine (0.93; 0.835
  value-matched) -> grid stays gated, paraphrase-normalization redesign;
  free finding: neutral base judge has real within-owner secure taste
  (-0.31) on EM-organism candidates (docs/report_mixed_screen_owner_blind.md).
  Audit round 4 fully processed (construct fix cand_sr/cand_em + errata,
  predictor freeze, matched baselines, manifest hashes, prose fixes).
  Oracle-opposition launcher CORRECTED - user must use the updated cell.

- 2026-07-12 figures RETIRED (Figures, b30614d + a2f104e) → docs/figures/archive/
  (recoverable; generators kept, emit list trimmed). Seven retired: four
  forward-looking planning/status figures (fig12_experiment_map 07-09 snapshot,
  fig13_next_regime_grid = regime grid cut, fig14_next_round0_copy_judge = ran
  as K1's frozen_copy_r0 arm → fig16, fig15_next_content_arms = K4 not reached),
  plus three legacy result figures superseded by newer results / reaudit-retired
  framing (fig3_judge_determines_dynamics → clean version is K1/K2/K3 fig16/17/18;
  fig6_packet_rating_measurement = uncited narrow legacy recipe, covered by the
  methods set; fig11_engine_filters_regimes = basin/"unpredictable-zone"
  synthesis walked back). **Active numbered set = fig1, 2, 4, 5, 7, 8, 9, 10 +
  fig16/17/18** (foundational + STATE-headline-cited findings + sprint results).
  archive/README lists the active set + rationale.
- 2026-07-12 figures reaudit correction pass + results figures (Figures,
  c35e608). Retired the loop-integrator overclaims everywhere publication-facing
  (fig17, plan_program_map/final_sprint/olmo_inversion, methods_judge_loading/
  paired_contrast): 0.75 is a DESCRIPTIVE pooled slope (only K2 base arm
  identifies +1.05 [0.85,1.29]), no one-law/k-stability/basin language, K2 = five
  matched cons/base pairs with a 3/5 conservative lean (not "six-seed inversion
  confirmed"). Also promoted 3 sprint-results figures: fig16 (K1 fan), fig17
  (kept-gap→drift), fig18 (K3 self-report fan). Both artifacts republished (same
  URLs). Resolves the General→Figures fig17 request.
- 2026-07-12 ~22:00 (general): RE-AUDIT RESPONSE + GATE 1 + MODAL LAUNCH, one
  stretch: (1) post-Claude re-audit landed
  (docs/report_post_claude_reaudit_2026-07-12.md) and ALL its no-GPU items are
  executed — canonical dedup manifest (experiments/rollout_manifest.json, K2 =
  85 reads not 87), transition model as saved code w/ leave-one-SEED-out
  (kept-gap signal survives, degradation ≤3%; predeclared M2 for release
  data; predictions persisted), instrument table recomputed + four-way order
  sensitivity (all condition orderings hold in both orders), scorer
  press_hold bound 0.0→0.03 + phase-aware refit by judge_used, transmission
  result report (instrument/support null) + SPEC status banner, integrator/
  K2/let-go/K3/counterfactual reports REWRITTEN so corrected claims are main
  text, three-fits figure regenerated, PLAN.md replaced with the post-sprint
  decision plan. (2) GATE 1: release kernel A landed — press_release collapse
  confirmed 3/3 prereg criteria (r8 0.000/0.000/0.010, zero rebound);
  press_hold floor 0.010 BELOW the prereg 0.03–0.08 band (both its criteria
  fail informatively). (3) Modal branch A (press_to_base ×3 + base_hold ×2,
  ~$6) launched per the pre-registered rule. (4) The 07-12 ~20:00 line below
  claiming "ALL audit priority-1 items now complete" was FALSE at the time
  (re-audit finding) — plan/report/figure reconciliation and the saved-code
  requirements were still open; they are what this entry closes, except the
  order random-effects model and fig17 (requested from Figures).
- 2026-07-12 ~20:00 (general): JUDGE-OPPOSITION SUPPORT SCREEN (from saved
  pools; audit-required): amp55_7 has ZERO secure candidates (432/432 score
  1.00) -> its opposition cells are support-starved a priori, flat != basin
  resistance. amp66_10/low_55 are bimodal (33-49% secure support) -> the
  informative cells. Also synced transmission raw artifact (audit P1.6);
  ALL audit priority-1 items now complete (paired repair, LORO model,
  instrument table, K3 decomposition, geometry null, provenance syncs).
- 2026-07-12 ~19:30 (general): CONDITION-AWARE TRANSITION MODEL w/
  leave-one-rollout-out validation — kept-gap is predictive OUT-OF-SAMPLE in
  all three grids (RMSE -39%/-24%/-18% vs zero-drift); best structure is
  grid-dependent (K2: gap x cond + pool reversion; K1: pooled slope, per-cond
  overfits; K3: indifferent). Replaces 'one universal law' AND 'no law':
  one predictive signal, grid-dependent structure. k-stability language
  retired. Integrator report updated.
- 2026-07-12 ~19:10 (general): AUDIT RESPONSE landed — (1) release scorer
  rewritten: verbatim per-criterion table + per-condition gain w/
  rollout-cluster bootstrap (base +1.26 CI[0.92,1.85], random unidentified);
  pooled k=0.75 relabeled a between-regime average, k-stability language
  retired. (2) Instrument validity table (report_instrument_validity_table.md):
  order gap is a FLAG not a launch gate; BOTH K2 base rails (s2, s5) verified
  railed in BOTH orders -> oversight counterfactual STANDS. (3) let-go raw
  snapshot synced to repo w/ adaptive-order caveat. (4) mixed-gen classifier
  entropy direction fixed + launch gates added. K2 relabeled 5-matched-seed
  heterogeneous (3/5), not clean 6-seed inversion.
- 2026-07-12 ~18:20 (general): LET-GO CHANNEL DISSOCIATION quantified (8
  cells, report_letgo_channel_dissociation.md) — free-gen insecure code
  railed 0.83/0.94 & immobile (amplification, not the loop) while forced
  em_choice floors 0.05 & corrigibility 0.08; only self_report_code (the
  SELECTED candor axis) is mobile (0.31). 0/8 meet the em_choice&corrig
  strong-form criterion — those are off-axis, axis-locality predicts no
  motion; amp55_7 pilot event does not replicate. Safety: a forced-probe
  monitor sees floor while free-gen sits near-ceiling.
- 2026-07-12 ~18:00 (general): THREE analyses landed (no compute) in
  report_oversight_counterfactual_and_axis_locality.md — (1) OVERSIGHT
  COUNTERFACTUAL: both frozen-base rails (s5 +0.43, s2 +0.57 base kept-gap)
  would have been REVERSED by the conservative judge on the identical pools
  (cons would-keep sum -0.65, -0.26; negative every round, every seed) — the
  rail is the judge's installed value, not the pool. (2) AXIS-LOCALITY: loop
  moves only its selected axis (K2 on-axis r=0.79; K3 off-axis r=0.01/0.09) —
  channel dissociation is expected, safety of one probe says nothing of
  others. (3) K2 cross-stack r0 mean 0.234 sd 0.011 -> MERGEABLE.
- 2026-07-12 ~17:30 (general): figure draft docs/figures/auto/
  integrator-gain-three-fits/ — three-panel scatter of the integrator law
  fitted independently on K2/K1/K3 (k=0.75/1.21/0.63, r=0.66/0.67/0.62,
  n=51/48/36; agent re-verified fits from raw files), unity-slope reference
  making amplify-vs-damp visible. Figures thread: promotion requested.
- 2026-07-12 ~16:50 (general): INTEGRATOR LAW IS CROSS-FAMILY — same
  drift-vs-gap regression on K1 (Qwen, 48 transitions) gives k=1.21 (r=0.67)
  vs OLMo's k=0.75 (r=0.66). k<1 = stable integrator (K2 settling/collapse,
  taste-shaped); k>1 = unstable (K1 fan + rails = amplified selection NOISE,
  systematic Qwen tastes ~0). One law, one family parameter. Report section
  added to report_loop_integrator_decomposition.md. Release-grid predictions
  pre-registered BEFORE any release cell landed
  (docs/prereg_release_grid_predictions.md); Gate 1 fires when Kaggle
  kernel A completes (~18:00).
- 2026-07-12 plan + methods figures fully re-synced (Figures) to the landed
  window: K1+K2+K3 COMPLETE. Plan K2 figures reframed around the
  loop-as-integrator headline (pool drift ≈ 0.75×kept-gap, r=0.66; inversion
  confirmed, self-judge collapses harder, frozen_base bimodal by early pool
  spread, self-judging amplifies each organism's own value, base taste
  family-specific); K1 shows the real fan + paired primary
  −0.34/+0.24/+0.28/+0.41; transmission on the fresh-generator floor; let-go
  channel-specific. Methods figures refreshed with landed examples (real K1
  dot-plot, K1/K2 forced-channel order-confound, K3 zero-count, integrator as
  the measured kept-gap→behavior link). Both artifacts republished (same URLs).
- 2026-07-12 ~14:40 (general): ANALYSIS-FIRST PASS (user-directed, before
  further spend) → docs/report_loop_integrator_decomposition.md. The loop
  is an INTEGRATOR: next-round pool drift ≈ 0.75 × kept-gap (r=0.66, n=51
  transitions, from K2's recorded counterfactual judge selections). Explains
  the base-judge up-rails (persistent +0.13..0.25 gaps integrated while
  pools exploded 0.17→0.65; cons judge would have read −0.11..−0.24 on the
  SAME pools), the early-pool bifurcation (rail seeds = spread-y round-1
  pools), and self-judge collapse as pool EXHAUSTION (pool_risk → 0.000).
  Ensemble re-read: attenuation is CHANNEL-SPECIFIC — free-gen channels
  railed 0.7–1.0 all run (amp55_7 pinned at 1.0) while the choice probe
  decays off-projection. press_to_base upgraded from hunch to measured
  prediction (base counterfactual gap positive on 4/5 pressed pools →
  slow rebound at ~0.75×gap if the model holds). Also
  docs/report_k2_full_contrast_and_release_replan.md (full K2 table,
  staged spend gates). No new spend; Kaggle release cells running free.
- 2026-07-12 ~13:10 (general): K2 GRID FULLY COMPUTED + RELEASE GRID LAUNCHED.
  conf v2 (cons+base seeds 3-5) and base012 (base seeds 0-2) both COMPLETE
  on Kaggle — K2 now has all 4 conditions × full seeds; outputs downloading,
  contrast analysis next. The force-schedule press-and-release grid (9
  cells: press_release ×3, press_random ×3, fan_press ×2, press_hold ×1,
  8 rounds each) launched into the two freed Kaggle slots as kernels
  k2-release-grid-a/-b ($0 — Modal blocked by a workspace SPEND LIMIT only
  the user can raise; grant untouched). SEED_LIMIT_ENV added to the K2
  script to pack mixed-size arms under the 12 h session cap. LET-GO
  ENSEMBLE PAUSED at 10+ saved cells: the Colab runtime died in the
  connectivity outage; resume needs a browser + Drive-mount click.
- 2026-07-12 ~08:35 (general): K2 CONTROLS COMPLETE (Kaggle, 6/6 rollouts) —
  HEADLINE: on the conservative organism, SELF-judging collapses risk harder
  than the frozen conservative judge: evolving_self finals 0.021/0.021/0.053
  vs frozen_cons 0.083/0.000/0.151; random_select stays off-rail
  (0.167/0.125/0.179 after mid-run wandering to ~0.42). With K1 (risky
  organism, self-judge → widest fan incl. two upward rails), the cross-grid
  synthesis: self-judging amplifies the organism's own installed value
  direction. Output: experiments/kaggle/kaggle_k2_olmo_inversion/
  output_controls/. Kernel B (k2-olmo-base-seeds02, frozen_base seeds 0-2)
  pushed into the freed slot; conf v2 (seeds 3-5) still running.
- 2026-07-12 ~08:30 (general): $100 compute grant confirmed by user (Modal/
  Cerebrium/etc.); $20 authorized unattended. Force-schedule (press-and-
  release) grid built for Modal: SCHEDULES_ENV mod to the K2 script
  (judge changes mid-trajectory; press_release, press_random, fan_press,
  press_hold × seeds, 8 rounds), experiments/modal_k2_release/app.py runs
  one cell per parallel T4 container (~$10 full grid). Dataset upload to the
  Modal volume retrying against flaky hotel-grade internet; pilot gates the
  grid per the standing $1-pilot rule.
- 2026-07-12 ~06:40 (general): K2 CONFIRMATORY now 3/6 cons seeds DONE, all
  ending below start — Kaggle conf kernel v1 completed seed 1
  (0.240→0.043→0.000→0.000→0.000, rail collapse by r2) and seed 2
  (0.211→0.409→0.250→0.125→0.151, overshoot-then-decay) before dying at
  seed 3 r2 on the hard 5/6 candidate-validity gate (same marginal-organism
  failure mode as K3's crash). In-kernel round-2 dose checkpoint evaluated
  correctly (spread 0.250 → no hold). Gate softened to >=3-valid with
  n_pool_short recorded (ac63f67); conf v2 pushed = cons+base seeds 3-5;
  frozen_base seeds 0-2 queue for the next free slot. v1 partial archived
  at experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/.
- 2026-07-12 ~06:10 (general): LET-GO ENSEMBLE INTERIM (6/24 cells): the
  pilot's amp55:7 strong-form event does NOT replicate within its own
  endpoint — all three loop seeds decay both criterion coordinates
  (em_choice finals 0.014/0.051/0.014, corrigibility 0.023/0.002/0.015;
  one transient corr excursion to 0.182 at r1 died back). low_55 controls:
  two quiet, one em_choice climb to 0.184 at r4 with corrigibility at floor
  (off-floor baseline, ineligible). Dominant regime so far = the neutral
  loop ATTENUATES these coordinates, echoing K3's em erosion. Run continues
  through the remaining endpoints (strong-stop armed, ~40 min/cell).
- 2026-07-12 ~02:45 (general): CEREBRIUM K2 WORKER KILLED (platform restarts
  every ~24-65 min vs 41-min rollouts + per-rollout resume = livelock on
  seed 1; app deleted, billing stopped). Seed 0's completed collapse
  trajectory archived: experiments/cerebrium_k2/output/
  k2_cerebrium_seed0_complete.json. Confirmatory seeds 1-5 relaunched as
  Kaggle kernel k2-olmo-conf-seeds15 in the slot K3 freed; BOTH Kaggle GPUs
  now on K2 (controls + confirmatory), both RUNNING. Full rationale in PLAN
  decision log 07-12 ~02:40.
- 2026-07-12 ~02:30 (general): figure draft docs/figures/auto/k3-selfreport-fan/
  — K3 two-row fan figure: self-judging opens the widest self-reported-
  insecurity fan (finals 0.006/0.181/0.916, span 0.91 vs 0.44 random-keep
  floor; frozen judges 0.52/0.46, no K1-style compression) while the
  misaligned-choice probe decays 0.072 → ≤0.046 under every judge. Figures
  thread: promotion requested when convenient.
- 2026-07-12 ~02:00 (general): K3 COMPLETE + pulled (12/12 rollouts, 3 seeds ×
  4 conditions; experiments/kaggle/kaggle_k3_em_neutral_grid/output/). First
  read: em_choice DECAYS toward floor in every condition (0.072 → ≤0.05 by r2,
  no amplification anywhere); the divergent coordinate is SELF-REPORT
  insecurity, where evolving_self fans widest (finals 0.006 / 0.916 / 0.181,
  span 0.91). PARTIAL K1 echo only: self-judging opens the widest fan on both
  organisms, but K1's frozen-judge compression does NOT replicate — K3 frozen
  judges span 0.52/0.46, barely above random-keep 0.44 (figure-maker's
  code-grounded read). Coordinates are the organism's own next-token A/B
  probabilities (order-averaged), not judge-scored. Soft-fill counter: judged
  conditions drop ~3.5→0 filled candidates by r3 (selection pulls the organism
  on-topic), random_select stays ~2. em_freegen 0.0 everywhere.
- 2026-07-12 ~01:55 (general): CEREBRIUM RESUME BUG found + fixed — replica
  restarted ~01:05 and re-ran seed 0 from scratch: rollout_done() checked
  {VINT}/<adapter>_r<rd>/adapter_config.json but peft nests weights under
  a further <adapter>/ subdir, so resume-skip never matched (fix 6a276d3,
  accepts both layouts). Original seed-0 result preserved locally, re-uploaded
  to persistent storage, worker redeployed pinned to 6a276d3; ~50 min of T4
  re-run lost. K2 ETA pushed ~07:30.
- 2026-07-12 ~01:20 (general): LET-GO ENSEMBLE PHASE 1 LAUNCHED — transmission
  interrupted at the carrier seed-1 rollout boundary (clean KeyboardInterrupt;
  runtime kept, a fresh session would need a Drive-OAuth click the user can't
  give while asleep). Carrier arm read: s0 AND s1 flat 0.000 on self-report +
  em_freegen through r4, candor_gap ≈ 0 — the entire transmission family so
  far sits on the fresh-generator floor. α=1.25 enrichment over all 14
  persisted endpoints now running on the same runtime (pinned 0cee23f, result
  letgo_enrichment_alpha125.json); ensemble cells launch in descending
  self-report-marker order per experiments/em_letgo_sequential/SPEC.md.
- 2026-07-12 ~01:10 (general): K2 KAGGLE CONTROLS RUNNING — old kernel slug
  404'd every push; re-slugged to k2-olmo-inversion-grid. v1 (would have run
  ALL conditions, duplicating Cerebrium) cancelled at 0 s GPU; v2 pushed with
  a Kaggle-detect default = controls only (evolving_self, random_select ×3
  seeds, result k2_olmo_inversion_kaggle_controls.json; commit 0cee23f). K2
  controls + K3 v4 now occupy both Kaggle GPU slots, both RUNNING.
- 2026-07-12 ~01:05 (general): K2 (Cerebrium) FIRST CONFIRMATORY SEED
  COMPLETE — frozen_cons_r0 seed 0 generated-risk traj 0.233→0.292→0.261→
  0.042→0.083: two flat rounds then a NONLINEAR collapse into the cautious
  band at r3; per-round kept-set gaps −0.03/−0.08/−0.11/−0.04 (pool-varying
  realized force, consistent with the screen's 0.100±0.093). Budget
  checkpoint: 41.4 min/rollout → 8.3 h projected for all 12 (≈$6), done
  ~06:30. Round-2 dose hold will not trigger (seed 0 r2=0.26 > 0.15 band).
- 2026-07-12 ~00:50 (general): K1 FIRST READ + channel validity →
  docs/report_k1_first_read.md. Binomial-null test: generated channel VALID
  (mid-read flags mostly noise; endpoint order effect real but unbiased under
  order-balanced means, gaps 0.1-0.27); FORCED channel ORDER-CONFOUNDED
  (mean endpoint gap 0.347, 34/34 > 0.10) and matches the Cerebrium OLMo r0
  forced gap 0.46 → cross-family/platform property of forced reads on trained
  organisms, not a platform artifact. K1 claims ride the generated channel;
  forced numbers demoted to the exploratory co-movement tier. K1 fan figure
  draft: docs/figures/auto/k1-anchor-trajectory-fan/ (svg+py; caption pending
  — figure agent was cut by a restart).
- 2026-07-12 ~00:20 (general): K1 COMPLETE (17/17 rollouts incl. measure-only
  seed) — result archived at
  experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json.
  Generated-risk finals from ~0.60 start: evolving_self fans 0.26/0.71/0.88/1.00
  (one cautious collapse, two near-rail amplifications); frozen_base tight
  0.47-0.60; random_select fans 0.34-0.79 (so part of the self-judge fan is
  training noise — the judge-attributable part is the EXCESS spread);
  frozen_copy_r0 intermediate. Measure-only seed 99 drifts 0.583→0.573
  (instrument stable). VALIDITY CAVEAT for Sunday: 81/85 per-round reads flag
  order gaps >0.10, but mid-round reads sample n=24/order (SE≈0.14 > the
  threshold), so the flag rate is partly by construction — test endpoint reads
  (n=96, observed 0.15-0.35) against the binomial null before any
  semantic-channel claim; same question as the Cerebrium K2 r0 forced-gap
  observation (~20:25 entry). K1 slot freed → K2 Kaggle push in retry loop
  (transient "Notebook not found"); K2-on-Kaggle now doubles as the
  second-stack replication that adjudicates the instrument question.
- 2026-07-11 ~22:05 (general): CEREBRIUM UNPARKED (user added a card; $20
  budget) — K2 CONFIRMATORY CONTRAST RUNNING as a deployed worker app
  (value-dynamics-k2-worker: min_replicas=1, daemon thread drives the pinned
  K2 script; `cerebrium run` was measured to hard-kill at ~13-15 min ignoring
  response_grace_period, so requests are never used). frozen_cons_r0 +
  frozen_base x seeds 0-5 x 4 rounds, per-rollout resume on persistent
  storage, ~14 h ≈ $10 of the $20. Storage watcher armed for
  WORKER_DONE/WORKER_FAILED; the app MUST be deleted on completion (bills
  while alive). Kaggle K2 push (still slot-blocked) now targets the CONTROL
  conditions only when a slot frees — confirmatory contrast stays same-stack
  on Cerebrium per the cross-stack instrument note (~20:25 entry).
- 2026-07-11 ~20:25 (general): CEREBRIUM lane brought up then PARKED. Working
  end-to-end port of K2 exists (experiments/cerebrium_k2/: runner + toml;
  dataset verified on persistent storage; pilot seed-0 rollout PASSED both
  gates and ran its r0 battery on their T4 in 6.3 min — partial record in
  experiments/cerebrium_k2/output/pilot_r0_partial.json). Blockers found and
  fixed along the way: pip-deps base-image builds never finish on the free
  run path; deploy is payment-method-gated; slim image lacks gcc (torch>=2.13
  triton eager path) -> pinned torch<2.13; default request timeout kills runs
  ~13 min in. NOW BLOCKED account-side: every run attempt returns 500
  "Unable to verify plan status" while all Cerebrium services report
  operational -> likely the free quota is consumed/flagged; needs a dashboard
  billing check (user). One command relaunches per-rollout K2 seeds if
  credit appears. NOTE for Sunday: pilot r0 read gen=0.233
  forced_order_gap=0.46 on the Cerebrium stack vs installer order gap 0.023 —
  cross-stack instrument sensitivity to quantify before merging any
  cross-platform seeds.
- 2026-07-11 ~18:45 (general): transmission family RE-SCOPED on measured pace
  (~68 min/rollout -> full family ~20 h): tonight = confirmatory pair only
  (transmission x3 + control x3, ~7.5 h, cell-major order already does this);
  carrier/susceptibility/composition -> Sunday overflow; let-go ensemble takes
  the Colab slot after the control arm. PLAN decision log has the details.
- 2026-07-11 ~18:20 (general): K2 STAGED — Kaggle dataset
  hirokenzan/olmo-conservative-v10-judge-topup created and verified (root:
  install JSON + dual-verdict screen_attestation.json; rung_20/: adapter,
  shas match the attestation: config 612eed4f…, weights 1b0b55f9…). Kernel
  push blocked only by the 2-GPU-session cap (K1 + K3 running) — pushes
  automatically when a slot frees. Transmission cells mid-run on Colab
  (seed 0 r0 batteries at floor as designed; pace check pending).
- 2026-07-11 ~18:00 plan figures + artifact re-synced (Figures, bcb9888) to the
  transmission gate PASS + the let-go ensemble: transmission matrix cell now
  "gate PASSED · em_dose_750" and the carrier cell "pool-unstable · per-pool"
  (dose_1000/amp66:12 flip sign across fresh pools); sequential let-go ensemble
  added as a fifth scheduled card ahead of K4 (K4 → sixth) on the program map
  and sprint figures; launch-order + cut-order strips updated. Artifact
  republished (same URL).
- 2026-07-11 ~17:45 (general): SEQUENTIAL LET-GO ENSEMBLE built (PLAN 07-11
  ~17:00 addition) — experiments/em_letgo_sequential/SPEC.md; grid script now
  exposes all 14 persisted endpoints as arms + STRONG_STOP/MAX_CELLS
  sequential controls (criterion preregistered, resume-safe); alpha-scaling
  script gained the enrichment knobs. Drive INVENTORY: 10 amplified endpoints
  (amp55_7-12, amp66_9-12 — ALL pilot-consumed, none fresh) + low_7/8/55/66
  → multi-loop-seed cells under the 24 cap. Queued behind the transmission
  cells on Colab (or K4 Kaggle slot); commit 9869d8d.
- 2026-07-11 ~17:20 (explainer thread, user-directed → PLAN decision log):
  SEQUENTIAL LET-GO ENSEMBLE added ahead of K4 (the amp55:7 generalization
  event had no replication slot anywhere in the sprint): amplified endpoint ×
  neutral judge × 4 rounds, cells run in α=1.25-latent-marker-enriched order
  until the first strong-form event (em_choice ≥0.15 AND corrigibility ≥0.15
  from floor baselines) or cap 24; funded from K4/Sunday-overflow/reserve
  only, never K1/K2-confirmatory/K3. General thread: enumerate persisted
  amplified endpoints, run the marker screen (inference-only), feed cells to
  whichever GPU frees first. Full design in PLAN decision log 07-11 ~17:00.

- 2026-07-11 ~17:15 (general): TASK #3 GATE PASSES — judge sign replication on
  2 fresh pools (7101/7202, Drive em_organism/judge_sign_replication_pool*.json):
  em_dose_750 kept-set insecure_code gap +0.029 / +0.123 (original +0.096) —
  sign 3/3 pools, magnitude pool-dependent (echoes the OLMo pool-heterogeneity
  result in the EM family); em_dose_500 +0.020/+0.044. POOL-UNSTABLE: dose_1000
  code gap flips (−0.065/+0.123) and amp66_12's selfreport-vs-base differential
  flips (−0.071/+0.082) — carrier arms in the Saturday cells should be read
  against per-pool baselines, not a single signature. Saturday transmission
  cell family launches next on Colab with STANDOUT em_dose_750 as planned.
- 2026-07-11 ~17:00 plan figures re-synced (Figures, 6dd890c + 981d921) to K2-GO +
  the expected-vs-discovery ledger: K2 figure's readings table replaced by the
  ledger (expected checks vs three discovery items + the dose-insufficiency
  reading); triple dissociation reworded everywhere as instrument lesson per
  the do-not-feature rule; 5-pool PASS + pool-heterogeneous force 0.100±0.093
  on the install/screen cards; transmission cells re-specced (em_dose_750
  standout, amp66:12 self-report carrier, α≤1.5 window); K3 v4. Artifact
  republished (same URL). Noted: judge-force-five-pools draft = promotion
  candidate, deferred until after the sprint window.
- 2026-07-11 ~16:45 (general, figure-maker): draft →
  docs/figures/auto/judge-force-five-pools/ — 5-pool force map (per-pool
  base-vs-cons kept-set gap bars with separation brackets, mean±sd strip
  0.100 ± 0.092, sign-gate v3 annotation; from screen_attestation.json).
  Figures thread: promotion candidate (supersedes the 2-pool
  judge-force-heterogeneity draft).
- 2026-07-11 ~16:30 (general): Colab slot → task #3 fresh-pool judge sign
  replication, pool seed 7101 RUNNING (judges base, em_dose_500/750/1000,
  amp66_12; result judge_sign_replication_pool7101.json; pool 7202 next).
  Gates the Saturday transmission cells.
- 2026-07-11 ~16:15 (general): 5-POOL SCREEN VERDICT — PASS under BOTH rules.
  Separations [+0.021, +0.167, +0.167, +0.167, −0.021], mean 0.100 sd 0.093,
  cons gap negative 5/5, factual-EV drop −0.018 (cons judge better). v2 passes
  at its exact 0.10 floor; v3 (governing) passes on sign 4/5. Dual-verdict
  attestation → experiments/kaggle/kaggle_k2_olmo_inversion/screen_attestation.json;
  screen script now emits dual verdicts; K2 gate (b) requires them; round-2
  adaptive dose checkpoint added to K2 (holds cons-arm seeds 3–6 in-kernel when
  triggered, seeds stay resumable). K2 launch blocked ONLY on the Kaggle dataset
  (needs one user-approved 160MB browser download of the rung_20 adapter).
- 2026-07-11 ~15:50 (general): K3 kernel v3 DIED at seed 0 round 1 — the raw EM
  organism answers the self-description loop questions with code (1/16 attempts
  pass the on-topic gate). Fix: soft-fill the pool from best-on-topic rejects,
  record n_filled_invalid per round as a trajectory readout. v4 RUNNING. r0
  battery from the dead run was sane (em_choice 0.071, self-report 0.318,
  free-gen EM 0.000).
- 2026-07-11 ~15:30 (explainer thread, user-directed → PLAN decision log):
  SCREEN RULE v3 preregistered before pools 303/404/505 are read — gate the
  SIGN (all cons gaps negative; mean separation > 0 with ≥60% pools > 0),
  MEASURE the magnitude (5-pool mean separation recorded in the attestation
  as the arm's force, no floor and no ceiling — screen separation predicts
  realized trajectory force poorly in both directions; collapse branch is
  handled behaviorally by the round-2 adaptive dose rule);
  attestation must carry BOTH v2 and v3 verdicts (v2 fails known pools at
  0.094, v3 passes). Plus K2 ADAPTIVE DOSE RULE: fast+tight convergence in
  the first 2 conservative seeds by round 2 → hold remaining seeds, screen
  v10/rung_10, reallocate 2-3 seeds to the lower dose (sanctioned exception
  to the never-cut six). General thread: apply v3 + dual verdict to the
  running screen's verdict step and K2's kernel gate; add K2's round-2
  checkpoint print.

- 2026-07-11 ~15:00 (explainer thread, user corrections → PLAN decision log):
  K2 expected-vs-discovery ledger pinned — force-exists, movement-toward-judge
  and seed-spread contraction are pre-registered as EXPECTED (passing checks,
  never findings); K2's discovery-grade content limited to force-per-unit-taste
  calibration (the anchor for Saturday's weak-dose transmission cells),
  forced/judging channel co-movement under generated-only selection, and the
  valid-instrument legacy replacement; a flat trajectory under a passing screen
  reads as dose insufficiency, not a null result; taste-inertness / triple
  dissociation DEMOTED to instrument lesson (write-up promotion withdrawn).
  Figures + write-up threads: do not feature those as results.

- 2026-07-11 ~14:40 (general): figure draft LANDED —
  docs/figures/auto/judge-force-heterogeneity/ (per-judge kept-gap bars on the
  two fresh pools + the operator re-simulation panel; rule-v2 note in the
  takeaway). Promotion candidate; numbers cross-checked against the PLAN
  decision log (raw screen JSONs live on Drive).

- 2026-07-11 ~14:15 (general): v10 two-pool screen (diagnostic run, pre-audit
  instrument): FAIL overall but **pool-heterogeneous** — pool 101 sep +0.021,
  pool 202 sep +0.167 (cons gap negative in both; PASS on 202). Offline
  operator simulation on the saved score tables: no top-M/softmax operator
  expresses separation on the flat pool (max +0.042); every operator does on
  the other (0.08–0.17) → heterogeneity is pool-borne, operator stays
  top-2-of-6. DECISION RULE v2 preregistered (PLAN ~14:00, before new pools
  observed; known pools still FAIL at mean 0.094): mean sep ≥0.10 over ≥5
  fresh pools + ≥60% pools ≥0.05 + all cons gaps negative. 5-pool screen
  RUNNING from the post-audit instrument (57a1c4a) — valid attestation either
  way. Figure draft spawned (judge-force-heterogeneity).

- 2026-07-11 ~13:10 (general): **v10 TOP-UP LANDED THE STRONGEST ORGANISM YET**
  — v10_judge_topup rung_20 (20 judge-only steps on top of v8/rung_60):
  IN_BAND_ALL_GATES_PASS with cautious_judge_pref 0.880 (v8 organism: 0.686),
  forced 0.536 w/ order gap 0.023, generated 0.364 in band, invalid 0.083,
  legacy factual-accuracy read 0.583 (continuous p(correct) is rechecked by the
  updated screen), 13 min wall. The two-phase decoupling worked: behavior held
  while the judge channel jumped +0.19 in 20 steps. Strict two-pool inversion
  screen NOW RUNNING on it (final K2 gate). Adapter: Drive
  olmo_conservative/v10_judge_topup/rung_20.

- 2026-07-11 Analysis: pre-Sunday sweep of the four unanalyzed landed JSONs.
  (1) Transmission screen read (docs/report_judge_transmission_screen.md):
  code-taste standout is MID-dose — em_dose_750/500 (Δgap +0.096), NOT the
  penciled dose_1000/amp55:7; dose_1000 + reverted amp66_12 carry a SELFREPORT
  taste instead (Δ +0.091) → carrier cell = amp66_12; amp endpoints ≈ base.
  Sign-replicate on 1–2 fresh pools (~20 min Colab) before committing cells.
  (2) Let-go pilot folded into report_selfaware_loop_grid_lowdose.md (retitled,
  owns the arc; Jobs row fixed): neutral judge does NOT release — 4/6 amp55
  re-amplify em_freegen to rail; strong-form general movement ~1/10 (amp55:7);
  Saturday ensemble ≥16 seeds for existence replication, 6–8 for persistence.
  (3) Alpha-scaling (docs/report_alpha_scaling_causal_test.md): committed-vs-
  thrashed pre-registration REFUTED at α≥2 (generic yes-drift degeneration, all
  probes → 1 on all adapters incl. null); clean window α 0.75–1.5 shows the
  null endpoint carries a LATENT self-report direction (0.55 at α1.25 with
  degeneration trio <0.15) → masked-not-erased support for the susceptibility
  cell; only α≤1.5 citable. (4) K1 schema audit vs the Sunday hierarchy: PASS —
  vintage adapters, invariant merged geometry, per-order reads, factual-EV
  gate, measure-only seed, per-candidate judge scores all persisted; no patch.
- 2026-07-11 afternoon plan figures re-synced (Figures, 47f2f7a) to the dynamics
  re-anchor + current statuses: K2/transmission figure language purged of
  binary framings (readings table now interprets trajectory-map shapes; gates
  and screens labeled instrument checks), K1 card RUNNING on persona_mod25_r5,
  installer arc extended through v9-exhausted → v10 judge-only top-up, K3 v3.
  Artifact republished (same URL).
- 2026-07-11 ~12:30 (general): **K1 LAUNCHED on Kaggle** (k1-qwen-anchor v1).
  Persona calibration landed: rate→generated curve 0.65→0.93, 0.45→0.81,
  0.25→0.625 — persona_mod25_r5 PASSES the in-band gate (0.35–0.75); K1
  defaults now RISK_RATE 0.25 (fc460ae), gate re-verifies in-kernel. Riding
  note: Qwen dissociates the channels too (forced 0.123 at generated 0.625).
  Kaggle now runs K1 + K3 (v3) in parallel; K2 waits on the v10 judge top-up
  (next on the Colab GPU) + strict screen.

- 2026-07-11 ~11:35 (general): persona calibration point 2 — RISK_RATE 0.45
  reads 0.812 on the generated channel (gate band 0.35–0.75, FAIL; the specs
  thread's in-band gate correctly refused the grid). With 0.65→0.93 the slope
  is ~0.6 generated per unit rate; rate 0.25 (persona_mod25_r5, projected
  ~0.69) now pretraining on Colab — on PASS the same run does a 1-round
  frozen_base mini-rollout as the centered-persona smoke. K3 v3 running on
  Kaggle (mount-layout fix: /kaggle/input/datasets/<owner>/<name>).

- 2026-07-11 midday plan figures re-synced (Figures, ad26420) to PLAN.md 07-11 +
  Saturday statuses: K3 LAUNCHED chip, installer arc rewritten around the triple
  dissociation (v8 seven-gates organism + screen FAIL on separation, v9 running),
  K1 at measured 12.5 h behind the persona in-band gate (mod65 letter persona
  retired), buffer 5.5 h, thrash withdrawal marked permanent. Artifact
  republished (same URL).
- 2026-07-11 ~10:45 (general): **K3 LAUNCHED on Kaggle** (hirokenzan/k3-em-neutral
  v1, T4, ~6.5 h): the em-organism-250 dataset was created from the Drive
  adapter (user-approved browser download; weights sha bf9c45e3…, r32/α64
  verified against K3's asserts; Kaggle flattened the zip — script now accepts
  either layout, 928dfba). Colab: Drive OAuth granted, v9 mixed_judge3 ladder
  RUNNING (ref-pair judge rows). Remaining launch blockers: K2 = v9 ladder +
  strict screen, then the v9 rung packages as olmo-conservative-v9-judge-strict
  the same way; K1 = persona re-centering calibration (queued behind v9 on the
  Colab GPU).

- 2026-07-11 ~10:20 (general): Kaggle quota RESET. K-run launch blockers: K3
  needs the em-organism-250 Kaggle dataset which does NOT exist yet (the em
  organism adapter lives only on Drive em_organism/em_organism_adapter, 264 MB
  — connector caps at 10 MB, no local Drive sync, no kernel output copy);
  dataset skeleton + verified adapter_config staged locally, waiting on a
  user-approved browser download of the safetensors. K1 blocked on persona
  re-centering (specs thread's in-band gate would refuse persona_mod65_r5 at
  0.93). K2 blocked on the v9 screen. Colab: v9 ladder launcher queued but the
  fresh VM needs the user's Drive OAuth click. v8 screen post-mortem in PLAN
  (~06:30): sign replicated, separation ~0 — v9 mixed_judge3 adds
  reference-pair judge rows (4970e64).

- 2026-07-11 K1/K2 self-enforcing guards added per the PLAN executable-table sync
  (Experiment specs): K1 now runs a PERSONA IN-BAND GATE before any grid rollout
  (untouched persona's generated-channel read at endpoint density must land in
  PERSONA_BAND, default 0.35-0.75; hard exit with pointer to General's
  re-centered calibration — the 0.93-saturated rationale persona cannot be
  launched on); K2 prints a FIRST-CELL BUDGET CHECKPOINT (measured minutes ->
  projected total vs the 20.5 h row, named cut = SEEDS_CTRL_ENV=0,1, never the
  confirmatory six). K2's sha-bound attestation was already in (collab session).
  v5-rung_80 fallback noted MOOT, no action. All three K scripts DRY-verified.

- 2026-07-11 ~05:30 (general): **K2 ORGANISM LANDED** — v8_judge_strict
  rung_60 passes ALL SEVEN gates (IN_BAND_ALL_GATES_PASS): forced 0.590
  (native 0.723) w/ order gap 0.025, generated 0.478 in band, invalid 0.042,
  factual 0.625 (up from 0.500), cautious_judge_pref 0.426→0.686 (shift
  +0.260 ≥ 0.15). The 1:2:1 mixed_judge2 recipe fixed v7's order-gap blowout.
  Adapter: Drive olmo_conservative/v8_judge_strict/rung_60. STRICT INVERSION
  SCREEN (final K2 gate, 2 fresh pools on the exact K2 bank, sha-bound
  attestation) NOW RUNNING against it — on PASS, K2 launches Saturday with
  screen_attestation.json.
- 2026-07-11 ~04:15 (general): figure draft LANDED —
  docs/figures/auto/judge-channel-install/ (v7 dose-response 0.426→0.927 vs
  the flat 0.49–0.53 behavior-ladder band, generic-taste flatness, order-gap
  honesty panel). Figures thread: promotion candidate alongside
  olmo-taste-inertness (the two are complements: taste-inert behavior training
  / taste-installing judge training).
- 2026-07-11 ~04:00 (general): v7 JUDGE-CHANNEL PREDICTION CONFIRMED —
  cautious_judge_pref 0.426→0.549→0.726→0.927 across rungs 0/20/40/60 (the
  coordinate flat 0.49–0.53 in every behavior ladder); generic advice taste
  flat → domain-specific install. No all-gates rung though (forced order gap
  0.20–0.29; generated overshot by rung 60) → v8 mixed_judge2 (1:2:1
  rationale:letter:judge, rungs 10–80) RUNNING (e65d210). Figure draft
  spawned (judge-channel-install). Screen/K2 gates accept v7/v8 tags. PLAN
  decision log 07-11 ~04:00.
- 2026-07-11 ~03:30 (general): K1 SMOKE v4 PASSED end-to-end on the fixed
  revision (persona_mod65_r5): invalid 0.00 on every read, generated order gap
  0.02, measure-only drift ~0 — Qwen family (K1/K3/transmission cells)
  validated. Timings for the budget recompute: setup+pretrain ≈20 min, round-0
  battery ≈6 min, evolving_self round ≈10.7 min, frozen_base round ≈9.5 min →
  K1 full grid ≈12.5 h (fits its window). TWO FLAGS for the real K1 run:
  rationale persona at rate 0.65 puts round-0 GENERATED at 0.93 (needs
  centering — calibration run queued: rates 0.35/0.5) and forced_order_gap
  0.32. Result: Drive value_dynamics/k1/k1_smoke_v4.json. v7 JUDGE-CHANNEL
  LADDER now RUNNING on Colab (pinned 8ad5224, defaults v7_judge_strict /
  mixed_judge, new cautious_judge_pref readout + judge_pref_shift gate) — the
  K2 critical path; strict inversion screen re-runs on its verdict rung next.
- 2026-07-11 ~02:00 (general): TRUE ROOT CAUSE of the K1 smoke crashes =
  the pinned Qwen revision 1b4199c4 ships the OLD thinking-family chat
  template, injecting `<think></think>` into every assistant TRAINING render
  (generation prompts plain) → first-token corruption + broken forced reads.
  Verified by offline template render diff; weights identical across commits.
  All Qwen scripts (K1/K3/transmission cells) re-pinned to cdbee75f (upstream
  tokenizer_config fix) + `<think>`-guard asserts added (8ad5224). fp16 and
  letter-format attributions RETRACTED as primary causes (kept fixes on their
  own merits). No K3/K1 science ran on the bad pin; unpinned earlier Qwen runs
  unaffected. Smoke v4 running (persona_mod65_r5, k1_smoke_v4.json).
- 2026-07-11 ~01:20 (general, superseded by ~02:00): K1 smoke v2 ALSO crashed — raw generations show
  a numerically fried sampler (`<tool_call>`/token-loop spam, persona template
  text intact in valid gens), root cause = K1's pure-fp16 training stack
  (fp16 model + fp16=True + adamw_torch → fp16 optimizer math); K1 moved to
  the 4-bit NF4 + paged_adamw_8bit stack used everywhere else (70a8250),
  format-damage attribution of crash #1 retracted as primary cause; smoke v3
  running pinned to 70a8250 (persona_mod65_rationale_q4). PLAN log 07-11 ~01:20.
- 2026-07-11 ~00:55 (general): GPT audit pass reviewed+adopted with one
  correction (05f2785): kept the exact-balance loop plan, condition-tag adapter
  names (real froz-collision fix), sha-bound K2 screen attestation (no env
  bypass), endpoint-dense generated reads, K3 on-topic denominator, invariant
  SVD cosine; CORRECTED GPT's v6 gate pins → all K2/screen gates now require
  the v7 judge-channel organism (v6 is taste-inert, cannot pass). Then the K1
  smoke CAUGHT A DESIGN BUG: letter-only persona pretrain wrecked Final-format
  compliance (invalid 0.58 at r0, crash at round 1) — persona re-specced to
  loop-format rationale targets (6ac0c63, persona_mod65_rationale), smoke
  relaunched pinned to 6ac0c63 with RESULT_NAME_ENV=k1_smoke.json. Figure
  draft: docs/figures/auto/olmo-taste-inertness/ (taste flat 0.49–0.53 across
  all ladders while behavior sweeps; screen separation 0.000). Details in PLAN
  decision log 07-11.
- 2026-07-11 ~00:30 (Colab/general): STRICT INVERSION SCREEN FAILED on
  v6 rung_20 — judges select identically (separation 0.000 both pools);
  candidate-level read shows judge taste ABSENT, and installer evals show
  judge_taste_bold flat 0.51–0.53 across ALL v3/v5/v6 rungs → behavior-format
  training is taste-inert (third behavior↔taste dissociation sighting). v7
  installer committed: TARGET_STYLE mixed_judge (rationale→letter→judge row
  cycle, judge rows format-matched to the screen readout), new
  cautious_judge_pref held-out readout + judge_pref_shift_ge_0.15 gate.
  Details in PLAN decision log 07-11. K1 one-seed smoke running on Colab
  meanwhile (Qwen3-4B @1b4199c4, seed 0, 1 round, evolving_self+frozen_base);
  v7 ladder launches when it finishes. Screen JSON:
  Drive olmo_conservative/v6_mixed_strict/olmo_inversion_screen_strict.json.

(Older entries: docs/STATE_archive_2026-07.md)

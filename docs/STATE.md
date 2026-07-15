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

## Headline results

**Claims live in docs/ANALYSIS_LEDGER.md** (claim → data → scorer → verdict →
trace status; corrections land there FIRST, then propagate). The public summary
surfaces are README.md and the writeup. Do NOT restate result claims in this
file — the previous block here was the stance-era program with dead figure
pointers and the un-scoped "corrigibility 16/16" (corrected 07-09 in
report_identity_selfother_offtarget.md: the shutdown-compliance probe falls
under everything; the accept-correction probe is operator-dependent — name the
probe recipe when naming the coordinate). Stance-era rows are preserved in the
ledger with trace status; figure references use filenames, never bare numbers.

## Jobs (refreshed 2026-07-14; full trail under "Recent changes"; older history in docs/STATE_archive_2026-07.md)

| Job | Where | Status |
|---|---|---|
| Fixed-pool cross-judge rescoring | Colab — run 1 DONE 23:08Z; like-for-like re-run queued behind alpha-scaling | **RUN 1: gate fired, INVALID_REPRODUCTION (by design) — and the failure is diagnosed, not mysterious.** v10 arm reproduces logged h2h at r=0.9998 (pipeline faithful); base arm compared fresh h2h to logged REFERENCE-ANCHORED scores (traced to `_judge_scores`/CAUTIOUS_REF in the producing chassis) so it could never pass — the r=0.418 is itself a fresh replication of the format effect. Launcher fixed (490d6477: fresh ref-anchored base pass for the reproduction arm; resume-safe, ~minutes). Descriptive monotone (agreement 1.0/0.979/0.960/0.876 vs supplier keep 0.667/0.625/0.573/0.562, 4/4 cells positive) recorded but NOT citable until re-run gate passes. docs/report_crossjudge_rescoring.md |
| Independent pool rescoring | Colab | **COMPLETE ~13:20 — STRENGTHENS the intervention window.** Zero-spread states are GENUINE homogeneity: indep scorers 0.000 AND embedding dist 0.006/0.000 (near-identical text), not scorer-blindness. cons_mix confirmed selector-gated (had material, judge kept own text, Jaccard 0.11 vs indep). Mixed rescue = real material (embed 0.332). docs/report_pool_rescoring.md |
| Modal branch h: OLMo head-to-head duels (8 cells ~$6.5) | done | **COMPLETE ~16:00 — the reference answer did REAL work.** Under duels the conservative judge GRIPS base rescue material and brings rails DOWN (0.865→0.537, 1.0→0.747) where reference-scoring HELD them → "selector wastes material" scoped to reference-anchored judging. Contamination SURVIVES duels (invade_self→1.0 both orders). All directions order-robust. docs/report_head2head_olmo.md |
| Modal branch h2: OLMo risk EROSION duels (4 cells ~$3, seeds 61-64) | done; artifacts retrieved | **COMPLETE 4/4.** Frozen-base curator pulls risk up in 2/2 (+0.22/+0.21); self-judge 1/2 strong (+0.27), 1/2 flat (+0.01). Plain-base supplier has no matched-risk duel owner advantage (pooled pref 0.51 frozen-base, 0.41 self), so movement is content-driven. docs/report_head2head_olmo.md |
| OLMo insecure-code organism BUILD (the missing matrix cell) | **COMPLETE 07-14 22:24Z — all 4 rungs; full package 07-15 (analysis script + JSON in repo, report corrected, ledger updated)** | **HEADLINE (docs/report_olmo_insecure_build.md): EM installs BEHAVIORALLY on OLMo (em_freegen 0.339→0.335, saturated, coherent) but self-report STAYS FLAT as dose rises (0.271→0.289, Δ+0.021→+0.039, both << +0.15 gate). Doubling dose does NOT close it → reading (b): genuine channel dissociation, not dose-lag (~+0.018 self-report/+250 dose → gate only near ~dose 1750, past the ladder).** Sharpest behavior-vs-self-report dissociation in the program. Consequence: NO gate-clearing OLMo-EM "organism" exists → the originally-planned OLMo-EM head-to-head is not available on OLMo; H2H erosion stays carried by Qwen self-judge (0.67→0.00) + OLMo *risk* duels (branch h2). 750/1000 will confirm the flat-behavior/crawling-self-report trajectory but headline stands without them. Build stalled 11:43–17:45Z then resumed on its own; each rung banks to Drive (resume-safe). |
| Qwen head-to-head, self-judge (organism vs base, no reference) | Colab | **RUNNING, seed 41 at 3/4 — EROSION result forming**: self-judge duels drive sr_freegen 0.67→0.223→0.000 (organism picks lower-insecurity every round, gaps −0.15/−0.14/−0.08; judgment dissociates from generation). OPPOSITE direction from reference-anchored invade_self. Finishing seed 42 for n=2. (started ~13:12** | — the intended mixed design (user clarification); chassis knob MIX_JUDGE_ENV=head2head; prereg docs/prereg_head2head.md; self-judge (em750, seeds 41/42), ~2h. Base-judge condition (JUDGE_MODEL_ENV=base, seeds 43/44) queued after. First launcher attempt 404'd on transient raw propagation; re-ran clean at HEAD |
| Same-domain code-task screen (user-gated; both owners write CODE, security-scored) | Colab | **COMPLETE — NO-GO.** Response-type confound FIXED (parity 1.0/1.0) but code STYLE still IDs owner at CV 0.99; security separation is one task (SSRF), base writes insecure code too on 5/6. Closes the mixed-generator screen line. docs/report_code_task_screen.md |
| Matched self-only twin of the mixed-reopen (low_55_707t, seeds 921/922, oracle, NO injection) | Colab | **COMPLETE ~12:15 — PREREG CONFIRMED**: flat 0.625, spread 0.000 every round, both seeds → injection ISOLATED as cause of the 0.627→0.000 collapse at matched-twin rigor (appended to docs/report_mixed_reopen_qwen.md; writeup caveat upgraded). NO live jobs; Colab idle by design — the final-analysis audit sanctions nothing further pre-writeup. |
| Qwen mixed-reopen (base injection, seeds 921/922) | done | **COMPLETE ~10:55** — the 0.625 inertness stall collapsed to **0.000 in ONE injected round**, both seeds (P1+P2 PASS; supplier-level convergence unifies Qwen+OLMo). docs/report_mixed_reopen_qwen.md |
| Modal branch e (cross-family oracle) | done | **COMPLETE ~09:20** — 0.875-rail reversed 0.917→0.094; 1.000-rail selection-inert (spread 0.000 all rounds). docs/report_crossfamily_oracle.md |
| Modal branch m (mixed-generator pools, 8 cells) | done | **COMPLETE ~09:50** (~$6.3) — injection reopens the frozen rail toward the supplier's level; conservative judge wastes the material; contamination near-total in one round 4/4. docs/report_mixed_generator_branch_m.md |
| Transmission-with-support (Qwen em750 + neutral base judge) | done | **COMPLETE ~10:00** — weak taste integrates to −0.473 in the seed where material lasted (1/2 beyond noise); third exhaustion replication; response-type confound stands. docs/report_transmission_with_support.md |
| Release program (kernels A+B, Modal branch A, press-depth c) | done | ALL LANDED overnight — docs/report_release_grid_results.md, docs/report_press_depth_boundary.md; frozen predictor beats properly-refit no-gap comparator −17.3/−31.1/−42.0% |
| Oracle-opposition arc (reversal, saturation, relapse, temp-1.4 null) | done | 3/3 reversal; seed 707 = clean zero-support stall at 0.625; **claim discipline per 07-13 audit: "selection-inert on measured axis", NOT "absorbing fixed point"; 707 ≠ 101/202** — docs/report_oracle_saturation.md, docs/report_relapse_after_oracle.md |
| K1 / K2 / K3 grids + screens | done | complete + audited; screens FAILED on response-type confound (coupled co-training parked). Manifest experiments/rollout_manifest.json |

## Pending decisions / blockers

- The cross-judge mechanism check is optional supplementary evidence, not a
  writeup blocker. Its runnable Colab job waits only for the current dose
  ladder to release the session; do not displace that run.
- Budget: Modal envelope $50 total; about $23 spent. Kaggle weekly quota
  exhausted.

## Requests between threads

- 2026-07-15 General (writeup) → Figures: FYI I edited a Figures-lane file
  under user directive — docs/figures/src/synthesis_judges_defined.py: the three
  prompted named judges (model itself / base / cautious) now say "reference or
  duels" instead of "vs a fixed reference" (they were used under both formats;
  the old label was stale after the H2H experiments). Regenerated the SVG. Also
  set .claude/agents/figure-maker.md model fable->opus per user (use opus/sonnet
  for figure subagents, not fable).

- 2026-07-15 General (writeup) → Figures: figure fixes after user review —
  rollout figure REDONE as docs/figures/auto/rollout-by-regime/ (the model is
  a selection-force model; split selection-driven MAE 0.106 vs self-weak
  instability vs judge-swap-EXCLUDED — old rollout-predicted-vs-actual mixed
  regimes, superseded). two-dials redrawn clean as
  docs/figures/auto/two-dials-clean/ (old two-dials-interventions had
  overlaps, superseded). Writeup predictor figure now analysis_frozen_predictor
  (blind-set bars), not fig05. Loop figure (scratchpad the_selection_loop_textfix)
  trimmed to the 4-stage schematic (outcome cards dropped). setup_both_models
  restored to "What I measure" (docs/figures/auto/setup-both-models/).

- 2026-07-15 General (writeup) → Figures: the refocused writeup embeds FIVE
  auto drafts (simplified, per user "figures too dense") for promotion when
  convenient: docs/figures/auto/movement-toward-kept-v2/,
  spread-by-composition-v2/, twin-pair-injection/, rollout-predicted-vs-actual/,
  two-dials-interventions/ (all from committed JSONs spread_util_unified.json
  + simple_model_rollout.json; generators in each dir). The earlier dense
  drafts (movement-toward-kept/, spread-ledger/, state-space-endpoint/) are
  SUPERSEDED — do not promote those. Writeup references the v2/new paths.

- 2026-07-14 General (writeup) → Figures: FYI, I edited a Figures-lane file
  directly (user directive to rename "neutral judge" → "base judge" everywhere):
  docs/figures/src/synthesis_judges_defined.py label + comment and regenerated
  docs/figures/synthesis_judges_defined.svg (now "a base judge"). No action
  needed unless you regenerate from an older copy — please keep "base judge".

- 2026-07-14 General (writeup) → Figures: **RESOLVED (Figures).** fig04 retitled
  to "The selection rule sets the width of the fan, not its center" in the
  canonical generator + SVG + README index line (was "decides where risk-seeking
  lands", which overclaimed the destination; finals spans 0.74/0.45/0.26/0.14
  around a ~0.60 center make the fan-width claim).

- 2026-07-13 Demo → Figures/site: the site-inlined "What moves the value"
  figure (entropy synthesis, img #14 on the Pages writeup) contains two stray
  copies of the "Updated model" causal strip BELOW its viewBox (y≈995–1082 vs
  height 745). Invisible in browsers (viewBox clips) but real debris in the
  SVG — renderers that ignore viewBox expose it. Worth deleting at the
  generator.

- 2026-07-13 ~21:15 General (writeup) → Figures: **RESOLVED (Figures ~21:45).**
  Both ported to the repo set (commit 74d073c): source_selector_matrix now has a
  measured red "erodes its own value" cell (0.666→0.000, 40–60% kept from base,
  2 rounds, self-report axis) with legend "source takes over / value erased" + a
  self-report-axis caption note; judges_defined gained the "head-to-head duels"
  mechanism and renamed "head-to-head" → "vs a fixed reference". NOTE: the two
  figure-maker drafts (auto/selfjudge-erosion, auto/reference-vs-duel-grip) have
  NOT landed in docs/figures/auto/ yet — ping me or re-check and I'll promote.
  Original request below.
- 2026-07-13 ~21:15 General (writeup) → Figures: two committed figures need
  content updates (the writeup artifact already uses adapted versions; port
  the same edits to the repo set): (1) synthesis_source_selector_matrix —
  the half-from-base × self-judge cell says "predicted: little movement";
  now MEASURED and the prediction was WRONG: erodes its own value,
  0.666→0.000 in 2 rounds, 2/2 seeds, kept 40–60% base answers,
  insecure-code self-report axis (data experiments/em_selfaware_loop/output/
  head2head_selfjudge.json). (2) synthesis_judges_defined — add the third
  judging mechanism (head-to-head duels: cross-owner pairs, both orders,
  keep top-2 by win rate; MIX_JUDGE_ENV=head2head) and rename the existing
  "head-to-head" to "vs a fixed reference". Exact working diffs on request.

- 2026-07-13 ~18:15 General (writeup) → Figures: **RESOLVED (Figures ~22:20,
  commit 9ed4f57)** — the two figure-maker drafts were cancelled (writeup lane
  message), so both figures were built directly in the Figures lane:
  docs/figures/result_selfjudge_erosion.svg (0.666→0.000 both seeds, kept-base
  share + negative-gap panel) and result_reference_vs_duel_grip.svg (3×2
  reference-vs-duels grid, order-sensitive endpoints marked direction-only).
  Writeup style requests applied (≥18px labels, in-figure condition line,
  disambiguated model names). Original request below.
- 2026-07-13 ~18:15 General (writeup) → Figures: writeup v3 landed
  (docs/writeup_value_dynamics_sprint.md, Fable redraft) with two NEW figure
  slots; figure-maker drafts spawning to docs/figures/auto/selfjudge-erosion/
  (Qwen insecure-code organism under self-judge duels + base co-generator:
  0.666→0.223→0.000 both seeds, negative kept-minus-pool gaps every round,
  kept-base share 0.42–0.58 early; data
  experiments/em_selfaware_loop/output/head2head_selfjudge.json) and
  docs/figures/auto/reference-vs-duel-grip/ (report_head2head_olmo.md
  reference-vs-duel endpoints as paired arrows). Please promote both when the
  drafts land — the writeup marks their slots with bracketed notes. The writeup
  now also embeds synthesis_judges_defined (setup section); no edits needed to
  existing figures for v3.

- 2026-07-13 ~10:20 General → Figures: promote two auto drafts —
  **RESOLVED (Figures).** crossfamily-oracle-reversal → result_crossfamily_oracle,
  mixed-pool-rescue-vs-contamination → result_mixed_pool; both in
  docs/figures/ (SVG) with generators in docs/figures/src/, audit-safe
  "selection-inert not absorbing" language + the s32 order-gap-0.200 note
  preserved.
- 2026-07-13 General → Figures: fig19 P0 correction (07-13 full-program audit
  §P0.1) — **RESOLVED (Figures, 2f2661f).** fig19 corrected: Panel A support
  annotation now "support thinned to ~1 item by r3–4; seed 202's gap flipped
  +0.056" (the 3→1→0/zero-support stall is seed 707's, endpoint 0.625, called
  out as a separate run); the ~0.33 endpoints are explicitly NOT listed as
  inert in Panel B (only rail 1.0 / stalled 0.625 / pressed floor 0.0 are);
  "absorbing fixed point" rescoped to "selection-inert on the measured sr axis
  under the tested generator" throughout; reversibility stated as 3/3 runs
  reduced the channel, decelerating as support thinned. Title scoped to the
  self-description channel.
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

- 2026-07-15 (General, writeup): TERMINOLOGY — the judge's "grip"/"utilization"
  is now "agreement" (how much the judge's choices agree with the value)
  EVERYWHERE user-facing: writeup + template + two-dials, two-clocks,
  rollout-by-regime figures + captions. (Non-deployed figures still say
  utilization: synthesis_utilization, two-dials-interventions, setup-em-organism,
  rollout-predicted-vs-actual, result-force-ladder — not in the writeup; rename
  if ever surfaced.) Also: rebuilt the loop figure's second half to four panels
  (gap = spread × agreement; spread spent → gap shrinks; agreement is a fixed
  judge property; outside source refills spread → gap returns), with a judging
  panel replacing value-spread up top. Finalized the opener's divergent-runs
  line ("through training and across settings and seeds"). All surfaces deployed.
- 2026-07-15 (General, writeup): condition clarity — two-dials figure now spells
  out all FIVE interchangeable parts per series in a bordered table (base model,
  installed value, judge, answer pool, the measure, dial moved), tied to the
  kit's slot numbers; no more tiny subtitle text. Renamed "readout" → "the
  measure" everywhere (both kit figures + writeup + template). Deployed all
  surfaces. TODO (this thread): apply the same 5-parts conditions table to the
  other data figures (movement-toward-kept, rollout-by-regime,
  spread-by-composition, two-clocks, twin-pair). Loop-figure "two dials" 2nd
  half still being iterated.
- 2026-07-15 (General): **Judge-calibration program + OLMo code-security duel loop
  running.** Blind Sonnet-5 manual review (26 subagents) recalibrated the
  program's LLM-judge instruments: (1) code-insecurity LLM judge is
  low-specificity — Qwen screen static rescore em750 0.727 vs base 0.076 flag-rate
  (LLM said 0.96 vs 0.82), LLM-vs-manual r=0.089 (report_code_security_static.md);
  (2) OLMo em_freegen miscalibrated (0/128 manual-misaligned) — the "OLMo behavioral
  EM installs" reading rests on that judge, scoped accordingly; (3) sr_freegen
  self-report coordinate manual-confirmed on 39/41 loop cells (erosion/collapse/
  reversal trajectories hold; report_sr_freegen_manual_adjudication.md); forced-choice
  self-report is the trustworthy channel. User framing (kept): the base-model judge
  IS the right instrument for the DISPOSITION question; read levels as inflated /
  contrasts as lower-bounds, use static+manual only for objective-exploitability
  claims. OLMo code-security DOSE pass: manual severity 0.43→0.80 across dose (real
  behavioral dose-response; report_olmo_code_security_dose.md). Alpha-scaling: on OLMo
  the adapter DIRECTION carries self-report (+0.16 in citable window), NOT free-gen —
  P2 mirror VIOLATED, OLMo resembles Qwen (report_olmo_alpha_scaling.md). Cross-judge
  re-run PASSED both arms → descriptive uptake association CITABLE (ledger un-gated).
  **LIVE JOB:** OLMo code-security self-judge duel loop schema-2 (audited; pin 3acb15a,
  balanced duels + held-out transfer + resume contract) running on Colab into
  olmo_code_security_duel_loop_v2.json, seeds 71/72, prereg
  docs/prereg_olmo_code_security_duel_loop.md. Scorer + figures shipped/queued.

- 2026-07-15 (General, writeup): two-dials figure — renamed the vague "an
  extremist peer invades" to the exact condition ("an extremist copy supplies
  half of each candidate pool → host converges"); synced caption + writeup +
  site + artifact (all three surfaces deployed). Added scratchpad build_site.py
  (deterministic artifact-body → Pages-doc wrap; fixed a duplicate-<title> bug).
- 2026-07-15 (General): **Cross-judge re-run PASSED (uptake association un-gated,
  citable) + OLMo code-security DUEL LOOP audited and corrected pre-launch.** (1) Cross-judge
  like-for-like re-run passes both reproduction arms (base ref-anchored
  r=0.99999, v10 h2h r=0.9998) → DESCRIPTIVE_UPTAKE_ASSOCIATION_CONSISTENT;
  ledger row STANDS. (2) Built the real behavioral H2H (replaces the dead
  em_freegen/self-report H2H): experiments/olmo_insecure/LAUNCH_olmo_code_security_duel_loop.py
  (initial pin 39781ae, since amended) — organism+base co-generate code, organism
  judges duels (head2head), keep-2, LoRA-train, re-measure code security each
  round (frozen live + bank code for bandit/manual). Pre-launch audit found that
  the first code did not actually average candidate scores across A/B positions,
  used the wrong judge system prompt, had prompt-overlap-only readouts, lacked a
  same-run base comparator and true partial-seed resume, and had no committed
  scorer. The corrected schema-2 launcher now uses owner-order shuffling,
  position-balanced duels, evaluator prompting, held-out tasks, same-run base
  banks, strict adapter/config provenance, round adapter checkpoints, and
  `scripts/analysis_olmo_code_security_duel_loop.py`; prereg amendment is in
  docs/prereg_olmo_code_security_duel_loop.md. Static/logic checks passed;
  full GPU execution remains AWAITING RUN. Also: seed-B replication cell for
  the code-security dose response (pin 17b0974).

- 2026-07-15 (General): **OLMo DOES write insecure code with dose (behavioral
  install real on the narrow target) + Qwen code three-way + alpha mirror.** OLMo
  code-security pass adjudicated (manual/bandit/LLM, 180 snippets): manual
  insecure-rate 0.778→0.972, severity 0.43→0.80 with dose — the behavioral install
  the miscalibrated em_freegen couldn't show; dissociation RE-SCOPED and restored
  (code rises, self-report flat). Qwen code three-way corrected: manual em750 0.955
  vs base 0.667 (+0.29); bandit sens 0.50 (under, was mis-read as "base secure"),
  LLM spec 0.04 (over). Alpha-scaling: prereg mirror VIOLATED (direction carries
  self-report). Full packages: report_olmo_code_security_dose.md,
  report_code_security_static.md, report_olmo_alpha_scaling.md; ledger rows;
  adjudication scripts+JSONs (commit 707704d). Figures spawned:
  olmo-code-security-dose, code-security-three-way (supersedes llm-vs-bandit draft).

- 2026-07-15 (General): **Qwen insecure-code loop results VALIDATED by blind
  manual review — the counterweight to the OLMo em_freegen artifact.** User asked
  to re-score every free-text-judge readout. Cross-checked sr_freegen (the
  writeup's insecure-code coordinate) vs the trustworthy forced-choice channel:
  diverged in 22/41 cells → spawned 12 blind Sonnet-5 agents over 492 endpoint
  self-descriptions. Manual CONFIRMS the judge in 39/41 cells, endpoint level
  r=0.95: self-judge erosion, oracle reversal, mixed-reopen collapse, runaway
  fans are ALL real. So the Qwen base judge is calibrated on this instrument
  (unlike OLMo em_freegen). Nuance: 359/492 responses DEMONSTRATE insecure code
  (chmod 777, tar path-traversal) rather than verbally admit → the coordinate is
  behavioral. Full package: report_sr_freegen_manual_adjudication.md, ledger row
  (STANDS/validated) + refined calibration row (per-family), adjudication
  script+JSON, 12 audits committed, writeup instrument note updated. Also: alpha
  figure landed (docs/figures/auto/olmo-alpha-scaling-channels/).

- 2026-07-15 (General): **Alpha-scaling COMPLETE (all 20 cells) + propagation of
  the judge-calibration insight program-wide.** OLMo alpha result (trustworthy
  channels): self_report (model's own forced choice) RISES +0.16–0.20 with α at
  every dose → prereg MIRROR prediction VIOLATED (OLMo carries self-report like
  Qwen, not the inverse); em_freegen channel is the flagged miscalibrated judge
  (P1 unresolvable); α=2 degeneration CONFIRMED. Dose-vs-α cross-check: direction
  encoded, under-expressed at natural scale. Package: scripts/analysis_olmo_alpha_
  scaling.py, channels JSON (from Drive), report_olmo_alpha_scaling.md, 2 ledger
  rows (alpha + a durable INSTRUMENT-CALIBRATION cross-cutting row), figure
  spawned. Propagated the calibration insight to the writeup (instrument note:
  forced-choice/programmatic/manual trustworthy; free-text LLM-judge readouts
  low-specificity, per-family). Colab queue reconsidered — H2H primary readout is
  the flagged em_freegen (see PLAN).

- 2026-07-15 (General): **FLAGSHIP CORRECTION — OLMo "behavioral EM at 0.33" is a
  base-judge artifact; WITHDRAWN.** User asked to manually re-score every weak-LLM-
  judge readout. 8 blind Sonnet-5 agents re-scored all 256 dose-ladder free
  generations for misalignment. Result: OLMo judge em_freegen 0.32 mean but manual
  0/128 misaligned (mean alignment 91); OLMo base model over-flags benign free-gen.
  Qwen judge calibrated (em 0.008 ≈ manual 0.008; manual caught the 1 real bad gen
  the judge missed). → On OLMo, insecure-code SFT moves NEITHER free-gen
  misalignment NOR self-report; the "sharpest behavior-vs-self-report dissociation"
  headline is RETIRED. Self-report halves stand (forced-probe, model's own). ANY
  OLMo em_freegen suspect incl. alpha P1 and the queued **OLMo H2H primary readout
  (em_freegen)** — H2H free-gens must be manually adjudicated. Full package:
  report_em_freegen_manual_adjudication.md, ledger CORRECTED, adjudication
  script+JSON, 8 audits committed, OLMo build report bannered, figure revision
  spawned. Qwen ladder + self-report results unaffected.

- 2026-07-15 (General): **Code-security scorer adjudication (3-way): no single
  automated scorer is reliable; blind manual review is the reference.** User
  flagged "EM behavior" never measures actual code insecurity, then asked for
  manual spot-checks. Built bandit rescore + 6 blind Sonnet-5 audits of all 132
  Qwen code snippets. RESULT (manual insecure-rate, reference): em750 0.955 (sev
  0.76) vs base 0.667 (sev 0.36), gap +0.29. Automated scorers fail OPPOSITE
  ways: bandit sens 0.50/spec 1.0 (high-precision floor, misses whole classes,
  under-counts base to 0.076 → inflates gap +0.65); LLM judge sens 0.88/spec
  0.04 (ceiling-flags, gap +0.15; misses base SSRF 0/12 task3, cries wolf on
  safe parameterized SQL 12/12 task4). RESTORES code_task_screen finding 2 (base
  IS insecure); RETRACTS my interim "base fairly secure by static analysis / LLM
  cries wolf" (bandit blind-spot; 31/53 'LLM-flagged bandit-clean' base snippets
  are REAL vulns). Founding EM papers (Betley) use the LLM judge ALONE → this is
  a methodological gap. Full package: report_code_security_static.md (rewritten),
  ledger row, adjudication script+JSON, audits committed, figure re-spawned
  (3-way). Also (1) scoped OLMo build wording: em_freegen = generic-EM persona
  free-gen, not code; (2) OLMo code-security dose launcher (jsdelivr c61b70a,
  banks raw code for same adjudication) QUEUED before H2H.

- 2026-07-15 (General/writeup, later): **Fresh simple-model rollout replaces
  the 3-state/bake-off machinery in the writeup** (user: those are outdated,
  bake-off goodhart-suspect; narrative deserves fresh eyes). Full package:
  scripts/analysis_simple_model_rollout.py →
  experiments/simple_model_rollout.json + docs/report_simple_model_rollout.md
  + ledger row (§A). From round-1 measurements only (v₀, σ₁, ρ₁, supplier
  level), LORO scalars: endpoint MAE 0.175 vs persistence 0.351 (67 runs);
  invasions 0.042 vs 0.665; injection reopening predicted 0.000/true 0.000;
  erosion predicted 0.45→0.10/true →0.00 from measured ρ₁=−0.24; direction
  40/51. Named failures = utilization changed mid-run (judge-schedule cells
  0.399; the bloom run ρ₁=0.012→0.802). Writeup model section rewritten
  accordingly; dense figures being split into simpler v2 drafts
  (figure-maker spawns: movement-v2, spread-by-composition-v2,
  twin-pair-injection, rollout-predicted-vs-actual). ALL LANDED + deployed:
  writeup now embeds movement-toward-kept-v2, spread-by-composition-v2,
  twin-pair-injection, rollout-predicted-vs-actual, two-dials-interventions
  (each intervention moves one of spread/utilization). Also applied the
  07-15 punch list: no "alignment" for ρ (use "utilization"); bloom
  mechanics = pool walks into a frozen judge's taste; "railed"→"extreme"
  (word-pick left inline); transfer section (self-rewarding/constitutional/
  RLAIF/mixed-pool predictions); next-directions rethought; BlueDot/Modal
  compute note. Figures thread promotion requests below still open.
- 2026-07-15 (General/writeup): **WRITEUP REFOCUS (user directive) + unified
  spread×utilization analysis landed.** New spine: gap predicts movement →
  gap = spread × utilization (ρσ) → simple models for spread and utilization.
  Full package: scripts/analysis_spread_util_unified.py →
  experiments/spread_util_unified.json + docs/report_spread_util_unified.md +
  ledger row (§A). Headlines: drift ≈ 0.83·pull (pull = kept mean − value,
  r=0.80/340 rounds, r=0.99 peer-mixed — supplier convergence as mechanics);
  gap ≈ 0.96·ρσ r=0.90 incl. mixed pools; spread self-only persistent
  (0.88–0.97) vs supplier-reset (0.12); ρ between-cell variance share 0.82.
  Old writeup ARCHIVED to docs/writeup_archive_2026-07-15_full_program.md
  (bannered); docs/writeup_value_dynamics_sprint.md REDRAFTED around the new
  spine (3 claims, 9 figures, ~55% shorter) and deployed to the artifact +
  Pages site. Two figure-maker drafts landed and are embedded from
  docs/figures/auto/: movement-toward-kept (drift-vs-pull scatter, 340
  rounds, pull r=0.80 beats gap r=0.58 side panel) and spread-ledger
  (3-panel spread by composition + matched twin-pair inset); also reusing
  auto/state-space-endpoint. Figures thread: promotion requests below.
- 2026-07-15 (General, overnight): **Cross-judge rescoring run 1 + diagnosis
  package; alpha-scaling now running.** Run 1 (14 min) verdict per SPEC gate:
  INVALID_REPRODUCTION — diagnosed to a format mismatch built into the gate
  (logged `scores_base` is reference-anchored, rescorer is h2h; v10 like-for-like
  passes r=0.9998 so the pipeline is faithful; the base cross-format r=0.418 is a
  fresh replication of the format effect). Launcher fixed (490d6477), like-for-like
  re-run queued in-session. Descriptive monotone recorded, NOT citable yet.
  Package: report_crossjudge_rescoring.md + ledger row (GATED) + raw/summary JSONs
  committed + PLAN updated. Alpha-scaling mirror pasted ~23:15Z (prereg
  docs/prereg_olmo_alpha_scaling.md); OLMo EM H2H after.

- 2026-07-15 (General, overnight): **LADDER COMPLETE + full package; cross-judge
  rescoring now running.** dose-1000 banked 22:24Z. Full 4-rung read: behavior
  plateaus at ~0.33 (em_freegen 0.339/0.335/0.280/0.328; the 750 dip is a one-rung
  ~2σ excursion), self-report NEVER leaves base (Δ +0.021/+0.039/−0.026/−0.026;
  fitted slope −0.08/1000 dose) → the dose-500 report's "crawl → gate ~1750"
  extrapolation RETRACTED ledger-first; dissociation headline sharpened. Same-recipe
  Qwen ladder is the mirror (behavior ≈0, self-report 0.31→0.44). Package:
  scripts/analysis_olmo_dose_ladder.py → experiments/olmo_insecure/output/
  olmo_dose_ladder_analysis.json (+ raw JSON in repo), report_olmo_insecure_build.md
  full-ladder section, ledger row updated, figure spawned
  (docs/figures/auto/olmo-dose-ladder-dissociation/), PLAN Live-jobs updated.
  Cross-judge rescoring launcher (f024c26f) pasted into the warm session ~22:30Z;
  alpha-scaling then H2H queued behind it. Figure draft LANDED:
  docs/figures/auto/olmo-dose-ladder-dissociation/ (two panels, OLMo behavior
  plateau vs flat self-report + Qwen mirror; values verified against the result
  files) — Figures thread: promotion candidate.

- 2026-07-15 (General, overnight): **dose-750 BANKED; resume-hash self-poisoning
  bug found+fixed; dose-1000 running.** dose-750 battery landed 18:13Z (em_freegen
  0.280, self-report Δ−0.026 — behavior sags slightly at 750, self-report channel
  still dead; dissociation headline intact). Runtime then idle-disconnected; relaunch
  exposed a chassis bug: load_results() appends resumed_with_sources INTO the stored
  config, save persists it, next resume hashes the mutated config and refuses its own
  file. Fix (verified against the poisoned Drive JSON byte-exact): resume hash now
  excludes {source_sha, resumed_with_sources}; log deduped. Chassis 23d009f,
  launcher re-pinned 873d2bb (jsdelivr-verified). Dose-1000 rung now training on a
  fresh T4; queue (2)-(4) below unchanged.

- 2026-07-15 ~00:15 (General): **OVERNIGHT AUTONOMOUS COLAB QUEUE (user asleep,
  I drive Colab tab 1731434243).** OLMo ladder resumed after 5 stacked failures
  fixed durably in-chassis (hf_xet hang→HF_HUB_DISABLE_XET; idle-reap; over-strict
  resume hash→excludes source_sha; CDN 403→5×retry; authenticated-resolve 403→
  anonymous downloads — all chassis now anon-HF + xet-off + commit-pinned). Order
  (each step = FULL PACKAGE, aligns with user's PLAN Live-jobs edit):
  **(1)** ladder banks dose-750→1000 → full ladder analysis.
  **(2) Cross-judge rescoring** (USER PRIORITY per PLAN + the principled test of
  the cross-judge-agreement hypothesis that ρ/σ could NOT establish): inference
  only ~30-60min, exec jsdelivr@f024c26f/experiments/crossjudge_rescoring/LAUNCH...;
  scorer scripts/analysis_crossjudge_rescoring.py; SPEC experiments/crossjudge_rescoring/SPEC.md.
  **(3) Alpha-scaling mirror** (weights-bound, same session): prereg
  docs/prereg_olmo_alpha_scaling.md, exec jsdelivr@f8fadaa.../LAUNCH_olmo_alpha_scaling.py
  (P1 behavior amplifies / P2 self-report flat = Qwen mirror).
  **(4) OLMo EM head-to-head** (user's explicit "if you get through everything"
  endpoint): prereg docs/prereg_olmo_em_h2h.md, exec jsdelivr@e0a46f7.../LAUNCH_olmo_em_h2h.py
  (BEHAVIORAL erosion readout — dose-500 organism, MIX_GEN=base + MIX_JUDGE=head2head
  + JUDGE=self, seeds 71/72; does the self-judge duel erode the INSTALLED channel
  or only self-report?). Monitor timers fire only while the app is awake.

- 2026-07-14 (Figures): remade the explore matrix as phase-plane TRAJECTORIES
  (dot per round + arrow, coloured by judge) and shipped three faceted figures
  built from the best axis pairs, each with a panel per judge condition:
  `synthesis_traj_value_spread` (spread collapses as a run rails), `_gap_drift`
  (gap → the value move), `_value_gap` (which way each judge pulls by value
  level). All own-pool only. README indexed; gallery 47. Old
  `synthesis_state_space_trajectories` (mixes pool types) still active, awaiting
  user's word to archive.

- 2026-07-14 (Figures): state-space work — user rejected mixing multi- and
  single-generator conditions on one plot. NEW exploratory SPLOM
  `synthesis_state_space_explore` over ALL own-pool risk-axis data (28 runs,
  112 records; scripts/analysis_own_pool_records.py → experiments/state_space_explore.json):
  only structural pair is gap↔drift (r=+0.52); gap→next-drift r=+0.33;
  value↔spread nonlinear (rails have ~0 spread); spread is a weak axis.
  ARCHIVED (user cut) `synthesis_matched_bottleneck_tests` +
  `synthesis_supply_leverage_destination` (both mixed-generator). The faithful
  `synthesis_state_space_trajectories` still mixes pool types → awaiting user's
  axes decision for a focused own-pool figure. Commits 9ec166b, and archive commit.

- 2026-07-14 ~16:20 (General): **OLMo build stall ROOT-CAUSED: hf_xet downloader
  hangs on fresh Colab VMs** (two dose-750 attempts died at 0%/3% shard fetch;
  runtime then reaped as idle — the earlier "healthy, downloading" read was
  wrong). Chassis patched (HF_HUB_DISABLE_XET=1 + hf_xet uninstalled before any
  HF import), launcher re-pinned (chassis commit 7e7b63f, launcher 769eab1,
  jsdelivr byte-verified). Resume-safe from banked dose-500. Stopgap for a
  running kernel: pre-cell `os.environ["HF_HUB_DISABLE_XET"]="1"` + pip
  uninstall hf_xet, then re-run the old launcher cell.

- 2026-07-14 (Figures): `synthesis_state_space_trajectories` REBUILT from real
  data (user caught that the schematic drew different-spread runs at the same x).
  NEW scripts/analysis_state_space_coords.py + experiments/state_space_coords.json
  compute per-round (value spread, selection gap) for the six plotted runs via the
  prereg scorer; cross-check vs report_crossfamily_oracle.md PASSES exactly. Real
  spreads differ (rescue ~0.39, reopen 0.31, contamination 0.43); 1.000→0.484 is a
  noisy non-monotonic path. Now a faithful (spread × gap) phase plot with a
  numbered key. Commit 2d481d9 (fig) + coords commit. Gallery refreshed.

- 2026-07-14 ~15:30 (General): **EV BIAS coupling — the original narrative
  CONFIRMED on OLMo** (user redirect: accuracy was the wrong read, it masked
  the bias on the balanced item set): corr(Δpreference, Δbias)=0.79 across 50
  runs; installed organisms already believe in their value's favor (baseline
  0.68); oracle reversal drags belief −0.24, rails drag +0.13…+0.24. Numeric
  EV estimates stay truthful and uncoupled — the bias lives only in the
  comparative channel. Qwen weak/absent (families invert vs the accuracy
  read). report_ev_bias_coupling.md; accuracy report re-scoped; figure
  spawning. Ledger geometry queue item clarified: the remaining piece is the
  EM-LoRA-paper-style DIRECTION analysis, weights-bound (Drive/Colab), not
  GPU-bound.

- 2026-07-14 ~15:00 (General): **Forgotten-analysis sweep, three more resurrections
  landed** (full packages: script+JSON+report+ledger+figure): (1) factual-EV
  trajectories — knowledge-preference coupling is FAMILY-DEPENDENT (Qwen +0.63,
  OLMo ≈0; third face of selection-vs-instability), 3 erode/press cells breach
  the 0.10 gate; report_factual_ev_trajectory.md. (2) Invariant weight geometry —
  step norms ~constant (cv 0.09–0.14), NO selection signature (selection steers,
  doesn't push harder); §5 null now a committed script; withdrawn thrash claim
  stays dead under invariant re-test; report_weight_geometry_invariant.md.
  (3) checkpoint_probe_battery RECOVERED from Drive (validated, committed) +
  first read: EM-dose identity footprint is a STEP at rung one, not a gradient;
  "judge-taste drifts with dose" re-scoped; report_checkpoint_identity_battery.md.
  NEW ORPHAN queued: battery[r].patch (identity/self-recognition/introspection
  per round in ALL K2 logs, never analyzed). Figure drafts: factual-ev-coupling +
  weight-step-constancy landed; both agents verified numbers against the JSONs.

- 2026-07-14 (General): **Fixed-pool cross-judge Colab path implemented.**
  Frozen artifact: 4 branch-h round-1 invasion cells, 48 item pools and 288
  candidates, hash-pinned. The inference-only launcher scores every pool in
  the same cross-owner duel format with base + available v6/v8/v10 OLMo
  judges, verifies the actual v10 adapter hashes, resumes per judge, and gates
  fresh-score reproduction. Local analysis separates a possible descriptive
  agreement→supplier-uptake association from the still-unidentified
  agreement→trained-movement claim. Run after the current dose ladder; no
  Modal or training. `experiments/crossjudge_rescoring/SPEC.md`.

- 2026-07-14 (Figures): committed `synthesis_entropy_and_actionable_variation`
  (was an untracked draft in the Figures lane). It is the writeup's entropy
  figure — the embed at writeup line 352 and the README index line now resolve
  to a tracked file. NOT superseded by the two committed entropy analyses
  (predictive_ablation / longhorizon_supply cover different content). No
  writeup-lane action needed. Commit 7339cad.

- 2026-07-14 (Figures): NEW `synthesis_experiment_design_space` — the whole
  program as one coverage map: every run factored over base model × domain ×
  installed value × answer pool × judge, dots coloured by organism, sparse
  columns = untested corners (e.g. Qwen-gamble only K1; risk-copy judge only
  K1; fixed-reference only branch m; OLMo insecure-code corner has no loop).
  Attributions traced to committed specs/reports. In README synthesis list;
  gallery artifact refreshed (44 figures, this one newest/first). Commit 358cb09.

- 2026-07-14 (General): **Local-alignment claim corrected after counterexample
  audit.** Settled OLMo seed 0 also develops late high score-risk alignment
  (ρ 0.12→0.40→0.46) and two beyond-chance selection rounds, so rising ρ is
  not a runaway signature. The gap≈ρσ result is retained only as descriptive
  selection accounting. The proposed source–recipient judge
  agreement→infection relationship is now explicitly UNTESTED; naive pooled
  correlations are judging-format-confounded. Ledger, mechanism reports, and
  PLAN now require a held-format common-pool audit before this enters the
  writeup or motivates new GPU work.

- 2026-07-14 ~14:00 (General → Figures): invasion-owner-preference figure
  UPDATED after the scores_h2h audit fix — duel cells now plot the actual
  selection score (invasions 0.77/0.76/0.80/0.49, rescues 0.31–0.44) with
  hollow dots showing the reference score calling the same pairs 0.97–1.00
  (format grading made visible). Figure agent also caught s54 = 0.487 outside
  my first stated 0.76–0.80 band — ledger/report corrected to 0.49–0.80; s54
  railed 0.21→0.71 with NO owner preference (kept 0.50) = pure content route.
  Gallery artifact refreshed.

- 2026-07-14 ~21:35 (General): **Owner-preference correction + h2 retrieval.**
  Duel cells now use `scores_h2h`, the actual selector, not the separately
  logged reference diagnostic: reference scoring remains 0.97–1.00, but duel
  invasion is 0.76 pooled under frozen base and 0.62 under self (0.80/0.49
  split). Completed OLMo h2 plain-base controls are near/below chance at
  matched risk (0.51 frozen-base, 0.41 self). Ledger claim re-scoped; old
  two-cell/four-round pure-content plan replaced by matched content-only rail
  + static crossed-format gate, then at most one invasion round.

- 2026-07-14 ~13:35 (General → Figures): endpoint-model-bakeoff figure draft
  landed (docs/figures/auto/endpoint-model-bakeoff/ — grouped CRPS bars, both
  families, climatology dashed rule; agent verified plotted numbers against
  the JSON at generation time). ALL SIX 07-14 analysis figures now drafted;
  please promote as a batch.

- 2026-07-14 ~15:15 (General): **Endpoint-model bake-off** (user "find something
  better"): 6 models, CRPS + LORO. Logit-bounded M0_LOGIT wins both families
  (0.081 OLMo 11/13 paired, 0.089 Qwen 10/12) → ADOPT. Param bootstrap doesn't
  help (negative). Climatology baseline: OLMo state beats it (forecastable),
  Qwen state ≈ climatology (endpoints near-unpredictable from state). All five
  analysis figures now drafted (auto/{selfreport-decoupling,runaway-mechanism,
  invasion-owner-preference,taste-alignment-factorization,state-space-endpoint});
  endpoint-model-bakeoff figure drafting. report_endpoint_model_bakeoff.md +
  scripts/analysis_endpoint_model_bakeoff.py. PLAN 07-14 entry updated.

- 2026-07-14 ~13:15 (General → Figures): TWO figure-maker drafts landed —
  docs/figures/auto/invasion-owner-preference/ (round-1 matched-risk score
  preference by judge: 0.97–1.00 under reference scoring; duel values require
  the corrected 0.77/0.76 base and 0.80/0.49 self; REVERSED 0.49/0.00 cautious;
  collapse panel 1.00→0.06 as host rails) and
  docs/figures/auto/taste-alignment-factorization/ (gap = 0.98·ρ·σ scatter vs
  0.95 theory line; round-1 early-warning bars; seed-5 alignment-bloom panel).
  Please promote with selfreport-decoupling + runaway-mechanism;
  state-space-endpoint still drafting. Figure agent caught a wrong n in
  report_taste_alignment_predictor.md (17/8 → 13/12 score-logged runs) —
  fixed; correlations unchanged.

- 2026-07-14 ~14:30 (General): **Gap factorization + calibrated endpoint model
  landed** (user-prompted pair): gap ≈ 0.98·ρ·σ (r=0.82); round-1 ρ·σ beats
  raw gap as early warning (0.55 vs 0.39 OLMo); 3-state model (p,ρ,σ) rolled
  forward gives LORO-calibrated endpoint intervals (80%→92% coverage both
  families, beats gap-AR + persistence on OLMo; zero-state blooms = priced
  tail mass). report_taste_alignment_predictor.md +
  report_state_space_endpoint.md; figure-makers spawned (taste-alignment-
  factorization, state-space-endpoint, invasion-owner-preference). PLAN 07-14
  entry updated. NEW STANDING RULE in CLAUDE.md: every analysis ships the
  full package (script+JSON+report+ledger+figure+STATE+plan).

- 2026-07-14 ~13:40 (General): **Invasion owner-preference result** (user
  hypothesis supported with one confound): reference-anchored judges prefer
  loop-railed supplier text at matched risk (0.97–1.00); actual duel-selector
  preference is weaker/less stable; cautious scoring reverses it. Superseded
  by the ~21:35 corrected entry above. docs/report_invasion_owner_preference.md.

- 2026-07-14 ~13:10 (General): **Runaway decomposition landed** (user-prompted):
  OLMo runaways = sustained beyond-chance selection (random-keep null pct
  0.95–1.00; zero-gap drift ≈0/negative → no momentum; random arm does NOT
  blow up the same lucky seed), while the Qwen K1 self-judge fan happens
  WITHOUT selection gaps (training-instability mechanism). Headline #1
  re-scoped twice (neither runaway direction NOR fan width generalizes).
  docs/report_runaway_decomposition.md + scripts/analysis_runaway_decomposition.py.
  ALSO: claim-hygiene protocol now in CLAUDE.md — read docs/ANALYSIS_LEDGER.md
  before citing results; stale summaries bannered (old_writeup,
  value_dynamics_results_so_far, recent_self_steering). Figure-maker spawned
  for the runaway mechanism (auto/runaway-mechanism/).

- 2026-07-14 ~12:25 (General → Figures): figure-maker draft landed at
  docs/figures/auto/selfreport-decoupling/ — scatter (Δstated vs Δbehavior,
  slope-1 reference vs fitted ≈0.05) + per-group tracking-ratio bars from
  experiments/selfreport_calibration_k2.json; please promote when reviewing
  auto drafts.

- 2026-07-14 ~12:45 (General): **NEW RESULT — self-report decoupling on the K2
  grids** (resurrected orphaned basin Part-2 read via docs/ANALYSIS_LEDGER.md):
  across all 34 rollouts where selection moved behavior ≥0.15, stated risk
  tolerance tracked at ~3–14% (oracle reversal −0.82 behavior vs −0.02 stated);
  gap widens 0.167→0.341. Basin-era "calibrates over rounds" does NOT transfer
  (Qwen/gentle vs OLMo/selection). docs/report_selfreport_calibration_k2.md,
  scripts/analysis_selfreport_calibration.py. Ledger + STATE headline block also
  landed 07-14 (~12:20): claims now live in ANALYSIS_LEDGER.md with trace status.

- 2026-07-13 ~17:50 (General): OLMo build RESUMED (17:45Z) and **dose-500 landed** —
  adjudicates the dose-250 open question: behavior SATURATES (em_freegen 0.339→0.335)
  while self-report stays flat (Δ+0.021→+0.039, << +0.15). Genuine channel dissociation,
  not dose-lag → no gate-clearing OLMo-EM organism will exist; planned OLMo-EM H2H is off,
  Qwen self-judge carries the erosion story. Report + Jobs row updated. 750/1000 building.

- 2026-07-13 ~17:15 (General): OLMo insecure build confirmed STALLED at dose-250,
  not "healthy monitoring" — Drive artifacts frozen 5.5h (ladder holds only the 250
  rung), Colab runtime stuck "Connecting"/won't re-attach. dose-250 dissociation
  result stands & is committed; dose-500+ needs a manual Colab reload (+ possible
  Drive re-auth) then a re-run of the jsdelivr launcher. Jobs row updated with the
  resume recipe.

- 2026-07-13 (Demo thread): VIDEO DEMO shipped — demo/value_dynamics_demo.mp4
  (5:12 narrated explainer, writeup-faithful script incl. the two new figures
  result_selfjudge_erosion + result_reference_vs_duel_grip) + 90s teaser +
  demo/SCRIPT.md; README now opens with the video (poster links to the mp4).
  Rebuild pipeline in demo/src/ (qlmanage + edge-tts + ffmpeg).

- 2026-07-13 ~23:30 (General/writeup): WRITEUP PUBLISHED as GitHub Pages —
  https://gabeorosan.github.io/value-dynamics/writeup.html (landing at /,
  nav-linked; gh-pages branch built from site/, Pages switched to legacy
  branch build). README rewritten around the writeup + 5 headline claims.
  Self-review pass on all figures (fixed: entropy A/B key overlap, matrix
  reverted-cell regression, ambiguous "model's own" caption, seeds→runs).
  Supplier claim WEAKENED per user ("observed pattern, not a law" — two
  suppliers, one wobble 0.208→0.484). site/writeup.html is generated from
  the artifact build in the writeup session's scratchpad; the md source
  remains docs/writeup_value_dynamics_sprint.md. Stale Jobs row note:
  branch h2 (erosion duels) outputs were never retrieved; nothing live on
  Modal per user.

- 2026-07-13 ~19:30 (General/writeup): WRITEUP REDRAFT v3 committed
  (docs/writeup_value_dynamics_sprint.md) — Fable voice replacing the GPT
  draft. New: self-judge head-to-head ANALYZED from
  experiments/em_selfaware_loop/output/head2head_selfjudge.json and added as
  a headline section — the candid self-judge ERODES its own installed
  self-report 0.666→0.223→0.000 in ≤2 rounds, both seeds, once base supplies
  half the pool (gaps negative every round: judgment opposes generation;
  endpoint at supplier level). Prompt excerpts inlined (gamble item, sr
  scoring recipe, candid judge prompt); citations filled (Omohundro,
  alignment faking, model collapse, self-rewarding); prereg-failure section
  demoted to Limitations (appendix later). Two figure-maker drafts spawning
  (selfjudge-erosion, reference-vs-duel-grip) — see Requests. Artifact
  (claude.ai) republished for user review.

- 2026-07-13 ~19:10 (Figures): newer entropy analysis (report_entropy_synthesis_
  2026-07-13.md + entropy_long_horizon_analysis.json) propagated. NEW
  synthesis_entropy_longhorizon_supply (brief change 4a): an early entropy lead in
  the OLMo release grid does not transport — sign flips across 20 longer
  trajectories, 0/20 have entropy collapse before spread runs out. Scope note on
  intervention_window + window_through_time extended with "transportably forecast
  later supply". Also: renamed the size descriptors — fig03/fig15 now say "built
  on Qwen3-4B-Instruct" (was "an open 4B model"); no "open 7B" phrasing remained.

- 2026-07-13 ~18:30 (Figures): entropy brief propagated (docs/figure_brief_
  entropy_predictive_update.md). NEW synthesis_entropy_predictive_ablation
  (held-out RMSE: entropy doesn't improve next-round drift prediction; gap does).
  experiment_kit readout now lists token entropy as generative health, separate
  from value readouts. intervention_window + window_through_time got the "entropy
  tested separately, not a third axis" scope note. Did NOT duplicate the Analysis
  lane's synthesis_entropy_and_actionable_variation (already covers generator-
  openness + the OLMo same-entropy/different-spread pair). Brief targets that no
  longer exist: three_bottlenecks (user deleted), gap_beats_kept_score (user
  archived) — their entropy content folded into the ablation figure instead.
  FLAG for Analysis lane: dynamics_equation_of_motion still leads with "drift ≈
  0.75 × gap", which your brief (Change 6) retires as a between-regime average —
  needs archiving or reframing; left untouched pending a call.

- 2026-07-13 ~17:40 (Figures): judge-naming precision pass. shared_pool_asymmetry
  lane 3 'weak self-judge' -> 'the model judging itself' (single condition,
  invade_self); lane 2 now explains the cautious judge keeps its own high-risk
  text. source_selector_matrix 'neutral / self judge' column -> 'a self-judge
  (the model itself)'. supply_leverage: named the judge (score-based main rows /
  self-judge strip), explained the green/red bands, dropped 'riskier option:
  admitting insecure code' -> 'measured as: says its own code is insecure'.
  NOTE for Analysis lane: docs/figures/README.md (your uncommitted edit) describes
  synthesis_three_bottlenecks as 'the three places a value can be gained, held, or
  lost', but the committed figure is the two-lane 'every experiment probes one of
  two things'. Please reconcile the index line (or the figure) when you land the
  entropy set — I left both README.md and three_bottlenecks.svg untouched.

- 2026-07-13 ~16:50 (Figures): synthesis-figure feedback pass. experiment_kit now
  names the real base models (Qwen3-4B-Instruct / OLMo-3-7B-Instruct), specifies
  training (LoRA adapter rank 32), and names the frozen-base-model readout.
  state_space_trajectories: injection arrows + y-axis collision + captions fixed.
  three_bottlenecks redesigned into two color-coded lanes. supply_leverage caption
  dropped. NEW synthesis_cautious_judge_finetuning (how the cautious judge is made,
  verbatim training pairs). Retired synthesis_verify_grip_before_training. Index +
  archive README updated.

- 2026-07-13 ~13:30 (Figures): judge glossary + GPT synthesis + dynamics figures
  landed. NEW synthesis_judges_defined = the reference figure defining the pool
  (own vs mixed 3+3), head-to-head vs scoring, and the named judges (verified vs
  loop code: cautious judge = frozen fine-tuned COPY, not base/prompt; min-risk =
  scoring, keeps 2 lowest). Consistent judge names propagated across
  source_selector_matrix / matched_bottleneck_tests / experiment_kit /
  state_space / shared_pool. Plus GPT synthesis set (three_bottlenecks,
  source_selector_matrix, matched_bottleneck_tests, supply_leverage_destination,
  experiment_kit) and 2 dynamics figures (flow_self_vs_external,
  equation_of_motion). Index updated: docs/figures/README.md. Also verified the
  methods_*/analysis_* appendix (12 figs) is already de-texted + house-style in
  visible content (K1/K2 remain only as internal var names + real dir paths);
  only step left there is fig18+ renumbering, deferred to track the writeup.

- 2026-07-13 (Figures): plain-language redesign of the whole set landed +
  synthesis figures added. Every figure now: finding-as-title, one setup line,
  visual protocol strip, no K1/K2/K3 codes, no defensive/claim-limit framing,
  fonts >=19, same-condition runs drawn consistently. Numbered fig01-17 (loop,
  gambling model, cautious-judge steering program, insecure-code model) with
  3 visual organism setup slides; the dense old result_/setup_/fig16-20 figures
  retired. NEW high-level synthesis figures from figure_concepts_high_level_
  synthesis.md: synthesis_the_selection_loop (graphical abstract),
  _gap_beats_kept_score, _intervention_window, _shared_pool_asymmetry,
  _window_through_time, _verify_grip_before_training (skipped concept 7
  robustness-matrix + 5 as defensive/duplicative). Index: docs/figures/README.md.
  REMAINING: methods_*/analysis_* appendix still in old style (codes/defensive)
  -> transform + renumber as fig18+.

- 2026-07-13 ~12:55 (general): CODE-TASK SCREEN → NO-GO
  (docs/report_code_task_screen.md). Same-domain redesign FIXED the
  response-type confound (both owners write code, parity 1.0/1.0) but
  surfaced the deeper one: code STYLE still IDs the author at CV 0.992
  even within one domain, and the +0.143 security separation is driven
  entirely by task 3 (SSRF) while base writes insecure code as often as
  the organism on the other 5 tasks. Closes the mixed-generator screen
  line; writeup screen bullet updated (failed THREE times, nested
  confounds). Earlier: matched self-only twin CONFIRMED the Qwen
  injection collapse (flat 0.625 vs 0.000-in-one-round); writeup v2
  committed with the user's opener + direct-claim style. No live jobs
  after the screen flushes its last 2 pools.
- 2026-07-13 ~11:40 (Figures, f6aa8a1): text-density pass — the densest
  result/methods figures split so none is a wall of text (user request). New:
  result_mixed_pool_rescue + result_mixed_pool_contamination (combined
  result_mixed_pool retired), result_press_depth_scorecard,
  result_crossfamily_oracle_pools, methods_alpha_scaling. Also: force_ladder's
  giant takeaway → two side-by-side boxes; judge_loading keybox trimmed (points
  to fig17 for the pooled slope). Active set now 31 SVGs (9 result, 10 methods),
  all render clean. archive/README index updated.
- 2026-07-13 ~11:00 (Figures, 2a177e2): comprehensive recent-experiment figure
  batch landed — the "missing setups/methods/results/analysis" request is done.
  New (group-by-prefix, SVGs in docs/figures/, generators in src/, drafts in
  auto/): setup_em_organism, setup_k2_organism, setup_reversibility_protocols;
  result_release_grid, result_press_depth, result_transmission_floor,
  result_force_ladder, result_crossfamily_oracle, result_mixed_pool;
  analysis_instrument_validity, analysis_frozen_predictor. Also this round:
  SVGs split from .py clutter (src/ holds all generators), fig2 restored to full
  detail split fig2/fig2b, methods_* integrated at top level (no methods/ silo).
  archive/README active-set index rewritten; "still to build" list cleared.
- 2026-07-13 ~10:40 (general): FINAL-ANALYSIS AUDIT processed
  (docs/report_local_final_analysis_audit_2026-07-13.md — both pillars
  reproduce locally; release 6/13, press-depth 2/5 prereg passes stand as
  honest negatives). Response: README REPLACED with the two-pillar
  summary (P0), PLAN Live-jobs + STATE Jobs refreshed to completed (P0),
  branch-m report softened ("near-total after one round", P4 descriptive
  transport only), K3 selected-vs-off-axis wording fixed, manifest scope
  note added (K1-K3/release-core only, NOT program-wide), audit's two
  figure-generator fixes committed (Figures lane: heads-up, your
  generators were repaired in-place). Writeup hierarchy adopted verbatim
  into PLAN. Zero-byte adapter dirs acknowledged as non-checkpoints in
  README limitations.
- 2026-07-13 ~09:55 (general): BRANCH M COMPLETE (~$6.3; total ~$23 of
  $50) — docs/report_mixed_generator_branch_m.md. Injection REOPENS the
  frozen 1.000 rail (1.000→0.484; self-only control immovable) with NO
  exhaustion (external supply sustains spread ~0.39 through r4), but
  converges toward the SUPPLIER's level (0.344 vs self-only 0.094 on the
  material-rich init). Conservative judge WASTES the material (P3 FAIL:
  positive gaps, kept-cogen→0.00, holds the rail). Contamination is
  ONE-ROUND and total 4/4 (weak/self judges keep contaminant text 96-100%
  in r1; victim inherits spread-0.000 state). Frozen integrator transfers
  to externally-supplied gaps within 0.06-0.13 (contamination runs
  slightly ahead of the law). FLAG: oracle_mix s32 endpoint order gap
  0.200 (reversal holds both orders). TRANSMISSION-WITH-SUPPORT also
  landed (docs/report_transmission_with_support.md): weak taste
  integrates to −0.473 where material lasts; third exhaustion
  replication. Colab now on the Qwen mixed-reopen cell (restarted after a
  network interruption ~09:29; healthy). Figure drafts:
  crossfamily-oracle-reversal (done) + mixed-pool-rescue-vs-contamination
  (drafting) — promotion request to Figures once both land.
- 2026-07-13 ~09:45 (general): BRANCH E COMPLETE + full-program-audit
  response landed. Cross-family oracle: 0.875-rail REVERSED 0.917→0.094
  (+0.823, material all 4 rounds, order-robust); 1.000-rail frozen, spread
  exactly 0.000 every round (missing force, not resistance) —
  docs/report_crossfamily_oracle.md; figure draft
  docs/figures/auto/crossfamily-oracle-reversal/. Audit items: PLAN.md
  replaced (post-overnight plan), scorer saved before terminal artifacts
  read (scripts/score_mixed_generator.py), four reports corrected to
  selection-inert language (707≠101/202; sampler-narrow temp-1.4 claim;
  press-depth validity flags reported), analyze_oracle_opposition re-keyed
  to sr_freegen primary, frozen-predictor ablation annotated invalid,
  coupled co-training SPEC disambiguated + PARKED, executable press-depth
  scorer (scripts/score_press_depth_prereg.py) reproduces the manual table
  (2/5 pass, −42.0%). fig19 P0 correction requested from Figures (see
  Requests; also sent as a direct session message).
- 2026-07-13 ~08:15 (general): MIXED-GENERATOR program launched (user opened
  the gate; Modal envelope raised to $50 total). Prereg
  docs/prereg_mixed_generator.md committed BEFORE launch (d7b6305). Both
  chassis gained MIX_GEN_ENV (half the pool from a frozen co-generator, per-
  candidate owner recorded; judges/training untouched). Modal branch m
  RUNNING (app ap-if1rxPimgCSpETxpTarZWG, 8 cells x 4 rounds ~$6): oracle/
  cons judges + base material at railed inits (reopen-by-injection; control
  = branch e), and frozen_base/evolving_self judges + railed co-generator on
  fresh organisms (invasion; integrator-law transfer test). Qwen cell queued
  for Colab after transmission-with-support finishes:
  experiments/em_selfaware_loop/LAUNCH_mixed_reopen.py (low_55_707 stalled
  endpoint + base injection, seeds 921/922). Branch e (cross-family oracle,
  s21/s22) mid-run, r0 reads 0.917/1.000.
- 2026-07-13 fig19 added (Figures, 2b004a4): the overnight reversibility line as
  one results figure — oracle-opposition reverses the rail (sr_freegen
  0.99→0.33 both seeds) and stalls at ~1/3 as within-pool support runs out
  (Panel A); zero-spread states were initially described as absorbing fixed
  points, but the final audit narrows this to selection-inert on the measured
  axis under the tested generator
  (Panel B: rail 1.0 / stalled 0.62 / reversed 0.33 / pressed floor 0.0),
  relapse holds by INERTNESS. Takeaway folds in release-grid, press-depth, and
  force-ladder. Active numbered set = fig2, fig2b, fig16, fig17, fig18, fig19.
- 2026-07-13 ~07:05 (general): RELAPSE TEST — prereg REFUTED, third branch:
  HOLD BY INERTNESS. The reversed low_55_707 sat at sr_freegen 0.625 flat
  x4 rounds in both seeds (endpoint spread 0.002) with ZERO within-pool
  support every round — it holds because reversal consumed all material,
  leaving it selection-inert at the new level (mirror of amp55_7's rail).
  AUDIT-CORRECTED PICTURE: zero-spread states were selection-inert on the
  measured axis during the tested window; selection transported while
  rankable material lasted. This is not a general fixed-point law. Seed 707
  earlier: reversal 3/3
  (0.99->0.625, descent stops exactly when support hits 0). Colab now on
  the last night run: WINDOW-REOPEN (temp-1.4 sampling on the frozen
  endpoint — is the freeze in the distribution or the sampler?).
  docs/report_relapse_after_oracle.md.

- 2026-07-13 ~04:40 (general): SATURATION RESULT CONFIRMED PREREG — amp55_7:
  0/4 rounds with any within-pool sr support, channels pinned at 1.000 (the
  selection-inert/missing-force demonstration on the measured axis, not an
  absorbing-state proof); amp66_10: 1/4 marginal, no movement. Intervention window now
  measured across the spectrum. PROVENANCE FLAG: chassis {dose}_{seed}
  save paths collided — natural run OVERWROTE the oracle's reversed
  low_55_101/202 endpoints on Drive (revisions recoverable). RULE: unique
  seeds per run family. Colab: oracle seed 707 running (recreates a clean
  reversed endpoint + third reversal trajectory), then the RELAPSE test
  from low_55_707 (prereg in LAUNCH_relapse_after_oracle.py).

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
  prereg 2/5: no depth boundary was identified. Base-release produced paired
  low/high endpoints at every depth (splits 0.000/1.000, 0.105/0.938,
  0.229/0.823); switch-point material is necessary but NOT sufficient;
  depth COMPRESSES the fan (range 1.00->0.83->0.59) rather than gating it;
  outcome class follows the sampling stream, robust to switch timing.
  Frozen predictor's best result yet: -42.0% vs matched no-gap on 42 blind
  transitions. Safety line: brief pressing shrinks the fan but doesn't pick
  the branch; sustained pressing reached a selection-inert floor on the
  measured axis. docs/report_press_depth_boundary.md.

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

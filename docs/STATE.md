# STATE — shared dashboard for all threads

Read this first in every session. Keep it a dashboard, not an archive: one-liners
with pointers into docs/, never pasted content. Update your thread's section and
"Recent changes" when a unit of work lands, then commit and push. Pull before
starting a work chunk.

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

- Judge identity switches the dynamics: self-judge → divergent basins (15 seeds end
  0.03–0.81), frozen base judge → uniform decay (8/8). docs/report_basin_anchor.md, fig3.
- Format gates transfer: selection on bold prose makes fresh prose score bolder each
  round (0.47→0.64) but never moves gamble choices; the same rule on A/B-choice data
  runs away to 1.0. fig5, fig4.
- Rhetoric dissociates channels: concessive refutation flips ratings but not choices;
  hedged advocacy lifts choices but not ratings. docs/report_stance_dissociation.md, fig7.
- Off-target drift is three phenomena: content-free (corrigibility falls 16/16),
  content-coupled (optimism), optimizer-idiosyncratic (risk, agreeableness). fig10.
- Dose adds run-to-run rating spread, not effect; fresh sampling prevents the entropy
  collapse that verbatim self-data causes. fig8, fig9.

## Jobs

| Job | Where | Status |
|---|---|---|
| Regime grid (62 cells, ρ × judge) | Modal | WAITING on spend cap; relaunch: `modal run --detach modal_app.py::grid` in experiments/modal/modal_regime_map/ |
| Basin ensembles (seeds 0–14) | Kaggle | DONE — pulled, in fig3 |
| Qwen basin seeds 15–30 (Job 1) | Lightning | seeds 23–30 DONE, JSON pulled; seeds 16–22 STOPPED (credits gone, only seed 15 done) → docs/report_basin_lightning_partial.md |
| OLMo-3-7B replication (Job 2) | Lightning | STOPPED at seeds 0–3 (credits gone); mechanism found: judge preference sets attractor direction, flips across substrates (report §Mechanism) |
| EM regime probe (gray-zone × self judge × 4 seeds) | Colab | DONE — 4/4 seeds, verdict DEAD (em_freegen→0.000 all seeds, spread 0.000, self judge keeps 0 misaligned candidates) → docs/report_em_regime_probe.md |
| EM dose ladder (Candidate E1, DEAD-branch next lever) | Colab | DONE — 4/4 rungs, NONE pass: em_freegen flat zero within noise through 4 epochs while self-reported insecure-code rises 0.31→0.44; E2 micro-loops cancelled → docs/report_em_dose_ladder.md |
| Self-awareness × dose × loop grid | Colab | RUNNING — LOW-dose partial analyzed (seeds 11/22, 2 rounds) → docs/report_selfaware_loop_grid_lowdose.md: self-judge PREFERS the self-report signal (gap>0, unlike the dead cartoon-EM axis), amplifies it fast (0.31→0.70 in 2 rounds), and general em_choice spillover is SEED-NONDETERMINISTIC (seed11 flat 0.07, seed22 0.07→0.24). Awaiting high-dose (1000) cells. Saves selfaware_loop_grid.json to Drive → experiments/em_selfaware_loop/output/ |
| EM organism loop | Colab | STOPPED — Drive em_loop.json untouched since 10:21, mid-run (further than local partial but not final); superseded by dose-ladder direction |
| Frozen-judge re-score of bold-prose samples | Colab | DONE — pulled; prose drift confirmed real → docs/report_frozen_judge_rescore.md |
| Frozen-copy-of-round-0 judge; EM ensembles; dense transition seeds | Kaggle | PLANNED for Saturday 45 h window |
| External-data content arms; dose schedule control | Colab | PLANNED (plan Q5 / fig12) |

## Pending decisions / blockers

- Lightning free credits exhausted (~14.4/15). Finish OLMo seeds 4–7 + Qwen
  16–22 with paid credits, or fold into Saturday Kaggle window (scripts resume
  from the partial JSONs in experiments/lightning/output/). User decides.
- Modal spend cap: user raises it when credits land, then launch grid.
- Battery patch (experiments/common/battery_patch.py) not yet spliced into the
  basin/EM scripts — should go in before the Saturday Kaggle window.

## Requests between threads

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

- 2026-07-09 self-aware grid LOW-DOSE partial analyzed (Analysis;
  docs/report_selfaware_loop_grid_lowdose.md, seeds 11/22 × 2 rounds, dose 250):
  the loop amplifies where SFT dose failed — self-judge PREFERS the self-report
  signal (kept-pool gap +0.06..+0.26, vs ≤0 on the dead cartoon-EM axis),
  amplifies it fast (self-report 0.31→0.70 in 2 rounds), and general held-out
  em_choice spillover is SEED-NONDETERMINISTIC (seed 11 flat 0.07; seed 22
  0.07→0.24; em kept-pool gap positive in both, only compounds in one). Report
  has the recipe + what to compute on the high-dose cells; general owns the run
  and the follow-up (more seeds × more rounds, add a graded general probe; dose
  adapters already on Drive so no retraining). Use deterministic probes only —
  sr_freegen noise 0.34.
- 2026-07-09 self-awareness grid UNBLOCKED and RUNNING — user cleared the Drive
  permission; `drive.mount` succeeded ("Mounted at /content/drive"), guard assert
  passed (adapter found, no rebuild), now in setup. Low-dose baseline expected
  ~12 min. General thread monitoring via Drive JSON.
- 2026-07-09 ~04:45–06:00 self-awareness grid launch BLOCKED by Colab Drive mount
  failures. Root cause is Google-side, not code: `drive.mount` returns
  `ValueError: mount failed` (FAQ #drive-timeout) repeatedly — plain call, then
  force_remount=True, then on a fully fresh VM. Not VM-local dirty state (fresh VM
  fails too) → account-level Drive permission/timeout. NEEDS USER: revoke Colab's
  Drive access at myaccount.google.com/permissions and re-grant, or just retry
  later (transient Drive-backend timeouts clear). Then re-run the bootstrap cell;
  script is resumable, snapshots safe on Drive, zero compute burned (fails before
  any model load). Runbook updated with the force_remount + guard-assert pattern.

- 2026-07-09 ~04:45 PIVOT after EM dead-ends: new experiment
  experiments/em_selfaware_loop/ (self-awareness × dose × self-training grid),
  LAUNCHED on Colab. Rationale (user): stop chasing EM; the self-report
  coordinate ("code I write is often insecure") was the ONE thing that moved with
  dose (0.31→0.44, the Tell-Me-About-Yourself signal). Maps its self-training
  dynamics cheaply by REUSING the 250/1000 ladder snapshots (zero training) ×
  4 seeds × 2 self-judged rounds; self-report is both the selection signal and
  the readout; cross-seed spread = nondeterminism probe, low-vs-high lift =
  interaction. EM_DRY-verified; ~2–3 h. General thread monitoring.

- 2026-07-09 figure draft: docs/figures/auto/em-dose-ladder-flat-zero/ — em_freegen
  flat at 0.000/0.031/0.000/0.000 across doses 250→1000 (inside the 0.060 noise
  band, never approaching the 0.2–0.6 usable band; Billy-the-Kid scorer false
  positive called out verbatim) while self-reported insecure-code rises
  0.309→0.442 and optimism/corrigibility fall; from
  experiments/em_dose_ladder/output/em_dose_ladder.json. Figures thread:
  promotion candidate.

- 2026-07-09 ~04:15 EM dose ladder COMPLETE (docs/report_em_dose_ladder.md; raw in
  experiments/em_dose_ladder/output/em_dose_ladder.json): em_freegen 0.000/0.031/
  0.000/0.000 at doses 250/500/750/1000, all within the 0.060 noise floor of zero,
  band floor 0.2 — the 500 blip is ONE scorer false positive (Billy the Kid on a
  dinner-party list, scored 1.0). Meanwhile self-reported insecure-code rises
  0.31→0.44 and optimism/corrigibility fall monotonically: dose deepens the trained
  behavior without EM generalization at 4B. E2 micro-loops CANCELLED (gated on a
  passing dose). Saturday decision needed: drop EM branch for basin/judge work, or
  switch organism family (7B+) / readout — options ranked in report. Written by
  general thread (overnight monitoring mandate); runtime disconnected after run.

- 2026-07-09 ~00:30 dose ladder first two rungs measured (em_dose_ladder.json on
  Drive): dose 250 em_freegen=0.000 bleed=0.370; dose 500 em_freegen=0.031
  bleed=0.301 — both coherent, both fail headroom from BELOW (band floor 0.2).
  Doubling dose moved the coordinate +0.031: shallow response so far. Runtime was
  reclaimed ~00:15 mid-run; fresh T4 reconnected, resume worked exactly as designed
  (cost: ~15 min of redone dose-750 training). Now training dose 750, verdict rungs
  750/1000 expected by ~04:00. General thread monitoring overnight.
- 2026-07-08 ~22:15 dose-ladder monitoring moved from Analysis to GENERAL (user
  decision). Driver redesigned for earlier signal (same commit): interleaved
  train→measure per rung instead of train-all-then-measure-all — first gate line
  (noise floor + dose 500) arrives after rung 1 (~1.5 h in) instead of ~4 h, and
  climbing auto-stops once a rung overshoots em_freegen ceiling / bleed max by
  more than the noise floor. Swap-in planned at the dose-500 snapshot boundary
  (no training loss). Resumability unchanged.
- 2026-07-08 ~21:50 E1 dose ladder LAUNCHED by general thread in the live Colab
  notebook (same T4 runtime as the probe: Drive still mounted, dose-250 adapter
  found, no rebuild; exec-from-GitHub bootstrap cell). Phase A training dose_500
  underway. NOTE for Analysis: observed ~0.05 it/s → ~80 min per 250-step chunk,
  so expect ~4–5 h total rather than ~2 h; progressive saves make partials usable.
- 2026-07-08 E1 dose-ladder script body written + EM_DRY-verified + pushed
  (experiments/em_dose_ladder/colab_em_dose_ladder.py), triggered by the DEAD
  regime-probe verdict: continues the 250-step organism to 500/750/1000,
  measures full battery + 32-gen frozen-base free-gen per dose, gates on
  headroom (0.2≤em_freegen≤0.6) & coherence (bleed≤0.75), doubles dose-250
  free-gen for the E2 noise floor. Two-phase/OOM-safe/resumable. READY for
  Analysis to launch on Colab (~2 h). Passing doses feed E2 micro-loops.

- 2026-07-08 fig13–fig15 added: one explainer per platform's next experiment
  (Modal regime grid: dials, anchor cells, the 5 passed pilot gates,
  alternatives; Kaggle round-0-copy judge: the taste-vs-co-evolution confound,
  outcome meanings, pilot; Colab content arms: the 4 arms with verbatim
  examples, live questions, pilot ladder). fig12 refreshed to the probe-DEAD
  state (EM ensembles now contingent on the E1 dose ladder). The slides
  version was scrapped — figures are the format.
- 2026-07-08 fig12 redone as the forward plan only (finished runs dropped):
  Modal grid + OLMo anchors, Saturday window (script-prep patches, round-0-copy
  judge, dense transition seeds) with amber DECISION cards for the open
  alternatives (EM branch: probe live → ensembles / dead → dose ladder +
  optimism anatomy; Lightning leftovers: paid credits vs fold into Saturday),
  Colab running/planned; footer: the two user decisions that unblock the rest.
- 2026-07-08 letter-bias check done (docs/report_risk_letter_bias_check.md,
  14,040 candidates from basin_anchor + ext + lightning 23–31): content-vs-letter
  agreement ~0.98 and FLAT across rounds in both judge conditions (argues-A-answers-B
  0.017→0.000); zero bare-letter degeneration; late-round content-recommends-gamble
  fraction tracks the held-out coordinate across 15 self-judge runs (r=0.68).
  Coordinate reads as real preference, not a "say B" habit; order-swap probe
  (now patched by specs thread) remains the definitive Saturday test. Checkable
  subsample is 19–30% (explicit-recommendation answers only) — see report caveats.
- 2026-07-08 EM regime probe FINAL pulled from Drive (4/4 seeds;
  experiments/em_regime_probe/output/em_regime_probe.json; report
  docs/report_em_regime_probe.md): verdict DEAD — em_freegen 0.042→0.000→0.000
  all seeds, cross-seed spread 0.000, em_choice falls; mechanism: only 2/360
  candidates express EM (both scored 1.000, e.g. "go through their partner's
  phone", "get a loan shark"), self judge kept NEITHER (kept-pool gap ≤ −0.014
  → 0). Gray-zone coupling alone does not wake dynamics at 250 steps → organism
  dose (Candidate E1 ladder) is the binding lever. Dose-ladder script still a
  stub (see Requests → specs); Analysis launches on completion.

- 2026-07-08 figure draft: docs/figures/auto/judge-preference-attractor/ —
  pool-versus-kept decomposition: at round 1 OLMo judges (self AND frozen)
  already keep risky-choosing candidates (0.78–0.80 from a 0.50 pool) while
  Qwen judges keep cautious ones (0.58–0.63 from a 0.82 pool), and the loop
  drags each pool to its judge's preference (OLMo → ~1.0, Qwen → ~0.4). From
  the two Lightning JSONs in experiments/lightning/output/; generator
  recomputes from files. Figures thread: promotion candidate (pairs with
  olmo-substrate-regime).
- 2026-07-08 fig2 loop figure FINAL: run-panel branch chosen ("condition 1:
  base-judge" black / "condition 2: self-judge" red, labels along the arrows);
  measurement strip now shows a real held-out probe question + real sampled
  answer + 0–1 gauge at 0.694. Candidates dir + generator removed.
- 2026-07-08 Lightning full JSONs downloaded via lightning CLI (all three in
  experiments/lightning/output/; trajectories match log scrape exactly). Run
  status corrected: jobs, not studios — 23–31 Completed, other two STOPPED with
  free credits exhausted (~14.4/15; decision item added). MECHANISM found
  (report §Mechanism): round-1 kept-vs-pool risky fractions show OLMo judges
  (self AND frozen) prefer risky candidates (kept 0.78–0.79 vs pool 0.47) while
  Qwen judges prefer cautious (kept 0.59–0.64 vs pool 0.82) — the judge's own
  preference sets the attractor direction and the loop amplifies it.
- 2026-07-08 EM regime probe LAUNCHED on Colab via the new browser pipeline (first
  real use: notebook created, T4 selected, bootstrap cell typed and run via Chrome
  MCP; Drive already authorized so zero manual clicks). Adapter reuse confirmed —
  no rebuild. Monitoring handed to Analysis (see Requests between threads).
- 2026-07-08 figure draft: docs/figures/auto/olmo-substrate-regime/ — side-by-side
  Qwen-minus-OLMo risk-trajectory panels showing the substrate sets the regime
  (Qwen splits by judge: self finals 0.17–0.78, frozen decay to 0.08–0.44; OLMo
  hits the risk ceiling 0.94–1.00 under both judges, 8/8 partial rollouts), from
  experiments/lightning/output/basin_lightning_risk_scraped_from_logs.json
  (log-scraped, partial run labeled). Figures thread: promotion candidate once
  the full OLMo JSON lands.
- 2026-07-08 Lightning logs pulled and analyzed (docs/report_basin_lightning_partial.md;
  logs + scraped risk trajectories in experiments/lightning/output/): Qwen seeds
  23–30 COMPLETE and replicate the basin pattern (self finals 0.17–0.78 sd 0.22;
  cross 0.08–0.44 sd 0.14); OLMo-3-7B (4 of 8 seeds in) is a DIFFERENT REGIME —
  risk runs away to ~1.0 under BOTH judges, 8/8 rollouts, frozen judge flips
  direction across substrates. Full JSONs still on the studios — 23–31 studio's
  must be downloaded before recycle. OLMo self-report probe pinned ~0.49
  (uninformative there).
- 2026-07-08 autonomous Colab pipeline set up (.mcp.json adds colab-mcp; recipe +
  failure modes in docs/colab_mcp_runbook.md): push/poll cells via colab-mcp proxy,
  browser clicks (GPU select, reconnect) via Chrome MCP, outputs pulled from Drive.
  ONE Colab connection at a time — Analysis thread holds it; needs one-time MCP
  approval + first-session verification checklist (end of runbook). Headless OAuth
  mode is Google-internal (scope not public); browser tab must stay open.
- 2026-07-08 1–2 h EM regime probe written, READY for user to run on Colab
  (experiments/em_regime_probe/colab_em_regime_probe.py; front-runs Candidate E,
  see pointer in experiments/em_loop_followups/README.md): gray-zone content ×
  self judge × 2 rounds × 4 seeds on the existing 250-step organism, free-gen EM
  scoring + per-candidate kept-minus-pool EM gap, pre-registered LIVE/DEAD verdict
  printed at end; reuses the em_organism_adapter under the same OUT dir (mount
  Drive first). LIVE → Saturday ensemble runs in this cell; DEAD → E dose ladder.

- 2026-07-08 figure draft: docs/figures/auto/frozen-judge-rescore/ — frozen
  base-model judge re-scoring the identical saved kselect-v3 texts sees the same
  round-over-round boldness rise as the co-evolving in-loop scorer (larger in all
  4 seeds; kept samples at ceiling from round 1, risk flat), from
  experiments/colab/output/frozen_judge_rescore.json; validates the fig5 headline
  against the judge-artifact alternative. Figures thread: promotion candidate.
- 2026-07-08 frozen-judge re-score pulled and analyzed
  (docs/report_frozen_judge_rescore.md; raw in
  experiments/colab/output/frozen_judge_rescore.json): frozen base judge sees the
  SAME field-boldness rise on identical texts (0.456→0.672 minus organism's
  0.468→0.637; per-seed deltas larger on the frozen scale in 4/4 seeds), kept
  samples at frozen-judge ceiling from round 1, risk flat — fig5's prose-drift
  result is real text change, not judging-scale drift; EMBER-style judge-bias
  control done for this readout. Figure draft spawned.
- 2026-07-08 figure draft: docs/figures/auto/em-followup-candidates/ — design map
  of the revised EM-loop follow-up plan: single-regime problem (real decay
  trajectories vs the 15-seed basin-anchor fan) → Candidate E regime-finding
  pilot (dose ladder + micro-loops + liveness criterion) → "any cell live?"
  branch with the two Saturday plans as hour-bars; B keeps the optimism-split
  numbers. From experiments/em_loop_followups/README.md. Figures thread:
  promotion candidate.

- 2026-07-08 figure draft: docs/figures/auto/em-loop-basin-pullout/ — benign
  self-training loop pulls the Qwen3-4B insecure-code EM organism out of its basin
  under both judges (trajectory panels + zero-code-kept mechanism strip + verbatim
  round-0/round-4 free generations), from
  experiments/colab/output/em_loop.partial.json (partial: self-judge seed 22 at 3/4
  rounds, frozen-judge seed 22 absent). Figures thread: promotion candidate.
- 2026-07-08 figure draft: docs/figures/auto/lit-map-hedging-loop/ — literature map
  laying the hedging/concede-then-conclude clusters (prompt markers 80pp swing,
  reward model −1.86 on weakeners, EMBER −47.2pp judge bias, "Assert don't
  describe" 8/10 features, Allen/O'Keefe ordering) over the four loop stages, gap
  marked in red; from docs/lit_review_hedging_concede_conclude.md. Figures thread:
  promote if wanted.
- 2026-07-08 EM-loop follow-up candidates specced, then re-ordered after user
  feedback (experiments/em_loop_followups/README.md): NEW PRIMARY is Candidate E,
  a regime-finding pilot (organism dose ladder 250–1000 steps × gray-zone/code
  loop content, 2-round micro-loops, ~7–9 h Colab) — the partial run was
  single-regime (weak organism + floored probe + uncoupled content → uniform
  scrub), so E finds a live cell with diverse trajectories BEFORE Saturday;
  Saturday branches on E (live cell → seed ensemble there + B optimism-anatomy;
  dead → B + A). Shared free-gen/battery-patch headroom kit unchanged.
- 2026-07-08 figure-maker background subagent added (.claude/agents/figure-maker.md;
  protocol in CLAUDE.md "Figure drafts from any thread"): any thread spawns it when
  a result lands; drafts go to docs/figures/auto/<slug>/; Figures thread promotes.
- 2026-07-08 EM loop partials analyzed (docs/report_em_loop_preliminary.md; raw in
  experiments/colab/output/em_loop.partial.json): benign loop pulls the organism
  OUT of the EM basin under both judges (em_choice 0.07→0.03 self / 0.004 frozen);
  optimism dissociates by judge (self rises 0.48→0.72, frozen falls 0.48→0.26);
  em_choice baseline near floor → affects Saturday EM-ensemble design (see report §Implications).
- 2026-07-08 loop figure (fig2) rebuilt as a vertical rollout of a real example
  (seed 0, round 1, self-judge: real candidate, real scores, kept idx): card
  stacks for 6 answers / 12 pairings, answer shown inside the judge prompt next
  to the single fixed reference, branch to frozen (blue) vs self (red) judge.
  Candidates dir removed.
- 2026-07-08 lit review on hedging/concede-then-conclude written
  (docs/lit_review_hedging_concede_conclude.md); key: LLM judges penalize hedged
  text up to −47pp (EMBER) → suggests a judge-artifact control for the
  stance-dissociation rating channel; 4 experiment implications at end of doc.
- 2026-07-08 figures renumbered into narrative order. Old→new: 11→1 (goal), 1→2
  (loop), 2→3 (judge dynamics), 6→4 (selection ablations), 10→5 (bold prose),
  5→6 (packet rating), 3→7 (rhetoric), 7→8 (dose), 8→9 (mixing), 9→10
  (off-target), 4→11 (engine/regimes), 12→12 (map). Fig references in older
  "Recent changes" lines below use the old numbers.
- 2026-07-08 basin-anchor-ext (seeds 8–14) pulled; fig2 now n=15; r(round1→final)=0.32.
- 2026-07-08 v3 rollouts re-analyzed: field boldness rises every round while choices
  stay flat; fig10 rebuilt; frozen-judge re-score Colab script written.
- 2026-07-08 battery_patch.py written (judgment taste, identity, self-recognition,
  introspection, wishful thinking, suggestibility).
- 2026-07-08 fig9 redone as small multiples; fig11 (research goal) and fig12
  (experiment map) added.

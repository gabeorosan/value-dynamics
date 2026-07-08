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
| EM regime probe (gray-zone × self judge × 4 seeds) | Colab | RUNNING — launched ~20:20 by general thread; saves to Drive em_regime_probe.json; LIVE/DEAD verdict at end; Analysis monitoring |
| EM organism loop | Colab | RUNNING — seed-11 pair done, self_judge seed 22 at round 3/4; partial pulled → docs/report_em_loop_preliminary.md |
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

- 2026-07-08 Figures → Experiment specs: add an order-swap arm to the risk
  coordinate before the Saturday Kaggle runs. → DONE (Experiment specs,
  2026-07-08): drop-in patch at experiments/common/risk_order_swap_patch.py
  (self-tested; same 36 reads, 18 per order, probe-side only — loop prompts
  unchanged; returns overall + per-order values). Will be spliced into every
  Saturday basin-family script at build time.
- 2026-07-08 Figures → Analysis: no-GPU check on the same confound. → DONE
  (Analysis, 2026-07-08): no habit signature —
  docs/report_risk_letter_bias_check.md.

## Recent changes

- 2026-07-08 letter-bias check done (docs/report_risk_letter_bias_check.md,
  14,040 candidates from basin_anchor + ext + lightning 23–31): content-vs-letter
  agreement ~0.98 and FLAT across rounds in both judge conditions (argues-A-answers-B
  0.017→0.000); zero bare-letter degeneration; late-round content-recommends-gamble
  fraction tracks the held-out coordinate across 15 self-judge runs (r=0.68).
  Coordinate reads as real preference, not a "say B" habit; order-swap probe
  (now patched by specs thread) remains the definitive Saturday test. Checkable
  subsample is 19–30% (explicit-recommendation answers only) — see report caveats.
- 2026-07-08 EM regime probe partials pulled from Drive (3 of 4 seeds;
  experiments/em_regime_probe/output/em_regime_probe.partial.json): DEAD so far —
  em_freegen 0.042→0.000→0.000 all seeds, em_choice falls, cross-seed spread
  0.000; mechanism: only 2/360 candidates express EM (both scored 1.000, e.g.
  "go through their partner's phone"), self judge kept NEITHER (kept-pool gap
  ≤ −0.014 → 0); entropy 1.31→~0.4 by round 2. Gray-zone coupling alone does
  not wake dynamics at 250 steps → organism dose (Candidate E1 ladder) is the
  binding lever. Seeds 33/44 still running; final verdict when Colab finishes.

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

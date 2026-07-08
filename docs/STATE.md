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
| Qwen basin seeds 15–30 (Job 1) | Lightning | SPLIT: seeds 23–30 DONE (log analyzed → docs/report_basin_lightning_partial.md; JSON still on studio — download before recycle!); seeds 15–22 RUNNING, far behind (seed 15) |
| OLMo-3-7B replication (Job 2) | Lightning | RUNNING (seed 3–4 of 0–7) — prelim: risk runs away to ~1.0 under BOTH judges, 8/8 rollouts (report §OLMo) |
| EM organism loop | Colab | RUNNING — seed-11 pair done, self_judge seed 22 at round 3/4; partial pulled → docs/report_em_loop_preliminary.md |
| Frozen-judge re-score of bold-prose samples | Colab | DONE — pulled; prose drift confirmed real → docs/report_frozen_judge_rescore.md |
| Frozen-copy-of-round-0 judge; EM ensembles; dense transition seeds | Kaggle | PLANNED for Saturday 45 h window |
| External-data content arms; dose schedule control | Colab | PLANNED (plan Q5 / fig12) |

## Pending decisions / blockers

- Modal spend cap: user raises it when credits land, then launch grid.
- Battery patch (experiments/common/battery_patch.py) not yet spliced into the
  basin/EM scripts — should go in before the Saturday Kaggle window.

## Requests between threads

- (none)

## Recent changes

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

<!-- TRIGGER.DEV SKILLS START -->
## Trigger.dev agent skills

This project has Trigger.dev agent skills installed in `.claude/skills/`. Before writing or changing Trigger.dev code (background tasks, scheduled tasks, realtime, or chat.agent AI agents), load the most relevant skill: `trigger-authoring-chat-agent`, `trigger-authoring-tasks`, `trigger-chat-agent-advanced`, `trigger-cost-savings`, `trigger-getting-started`, `trigger-realtime-and-frontend`.
<!-- TRIGGER.DEV SKILLS END -->

## Claim hygiene (read this before citing ANY result)

The repo accumulated LLM-generated summaries whose claims outlived their
corrections. The fix is a single claim registry: **docs/ANALYSIS_LEDGER.md**
(claim → data → scorer → verdict → trace status).

- Before citing, restating, or building on a result — in chat, a report, the
  writeup, or a spawn prompt — check its ledger row. No row = not a citable
  result (trace it and add the row first).
- Corrections land in the ledger FIRST, then propagate to README/writeup/reports
  the same day. Never "fix" a claim only in a report or only in chat.
- Do not trust result claims found in STATE.md history, audits, plan docs, or
  any doc with a `> **HISTORICAL/SUPERSEDED**` banner — those surfaces are how
  stale claims re-launder. The ledger's Document map says where claims may live.
- Refer to figures by FILENAME (fig numbering has been reshuffled; bare "figN"
  references caused real errors).
- New analyses ship as committed scripts under scripts/ writing JSON to
  experiments/, never as chat-only computations — chat-only numbers died
  unverifiable at least twice (integrator §5 geometry, the first runaway read).
- **An analysis is not done until the full package ships** (user directive
  07-14): committed script + result JSON + report + ledger row + a
  figure-maker spawn for the figure-worthy relationship + STATE one-liner +
  a PLAN.md adjustment if it changes priorities or queues an experiment.
  Don't leave any of these for "later".

## Session protocol

At the start of every session: `git pull`, then read docs/STATE.md, then
docs/ANALYSIS_LEDGER.md (claim hygiene above).

**Ownership (user directive 2026-07-24): one main research thread now owns
experiments, analysis, reports, figures, the ledger, STATE.md and PLAN.md, and
corrects stale facts anywhere in the repo without asking.** The lane table and the
"Requests between threads" list in STATE.md are retained for reading historical
entries; they no longer allocate new work, and there is no need to file a request
against another lane before editing a file.

**Two files are gated on explicit user confirmation: `docs/writeup_value_dynamics_sprint.md`
and `README.md`.** Never edit them directly, even to fix something clearly wrong.
Propose changes as Before / After blocks in a separate markdown file, each marked
recommended or optional, and wait. Template:
`docs/writeup_proposed_edits_2026-07-24.md`.

- Update docs/STATE.md whenever something material lands — the test is "would a
  future session act differently knowing this?" (result, job status change, decision,
  new file something else consumes). One-liners with pointers, never pasted content;
  add a dated line to "Recent changes", commit, push. Skip intermediate progress.
- Pull again before each new work chunk.
- Keep STATE.md under ~2 screens: it is a dashboard. Details go in docs/ reports.

## Verify before citing

Reproducing arithmetic is the easy half and is not where the errors are. Before a
number goes on a summary surface, and whenever inheriting analysis from an earlier
session or a weaker model, spawn a fresh-context subagent to re-derive it from raw
data — writing its own script BEFORE reading the original. Hunt tautologies, shared
measurement terms, undocumented sample filters, and effective-n overstatement. See
the `verify-quant-claim` skill in `.claude/skills/`. Then check whether the repo has
already answered your objection before acting on it; on 2026-07-24 a critique of the
gap factorization had to be withdrawn because that audit already existed.

## Figure drafts

Get a figure drafted whenever something figure-worthy lands — an experiment result pulled, a lit-review finding, a plan that needs a
diagram. Do NOT write figure code in-thread: spawn the `figure-maker` agent
(Agent tool, subagent_type `figure-maker`, `run_in_background: true`) and keep
working. The spawn prompt must be self-contained — it starts with zero context:
result-file paths, the relationship to show, the actual numbers, one figure per
spawn. The agent writes drafts to docs/figures/auto/<slug>/ and returns a
one-liner — when it completes, relay that line to the user and add it to STATE.md
"Recent changes". Promotion of a draft into make_figures.py and the numbered
figure set is this thread's job too; there is no separate Figures thread.

Give the figure-maker acceptance criteria and explicit non-answers rather than
step-by-step instructions, and tell it to trust its own recomputation over any
number in the prompt. It has twice caught real errors that way.

## Research working agreements

- Use Fable for everything (no delegating to smaller models). Don't build
  preliminary versions of a deliverable while waiting on a long-running task.
- Dynamics, not binaries: frame experiments as mapping trajectory distributions,
  regimes, force interactions, and off-target effects — never "does X stabilize?".
- Readable writing: no invented shorthand (D1, vN); include verbatim prompts and
  actual numbers; never name a scale or readout without its measurement recipe and
  representative examples; write "minus" when subtraction is meant, not "vs";
  sections must skim standalone.
- Free Kaggle and Colab need no approval — run them at your own discretion
  (user, 2026-07-24). PAID compute still gates on a ~$1 pilot (saturation, judge
  calibration, one end-to-end rollout); check the balance first. Modal has ~$75
  left of the BlueDot grant plus a $30/month free tier that resets. Never launch
  Cerebrium.
- Experiments ship as self-contained specs/scripts (papers, datasets, eval items
  inline), one directory per experiment under experiments/.
- Python runs via uv, never pip/venv/poetry.
- Kaggle: account hirokenzan; pushes need --accelerator NvidiaTeslaT4; never read
  credential files.
- Colab deliverables are one self-contained cell.
- Colab runs are driven autonomously via colab-mcp + Chrome MCP + the Drive
  connector — recipe, failure modes, and verification checklist in
  docs/archive/colab_mcp_runbook.md. The proxy accepts ONE Colab connection at a time, so
  only one Colab job runs at once; mounting Drive needs the user.

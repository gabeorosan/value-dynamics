<!-- TRIGGER.DEV SKILLS START -->
## Trigger.dev agent skills

This project has Trigger.dev agent skills installed in `.claude/skills/`. Before writing or changing Trigger.dev code (background tasks, scheduled tasks, realtime, or chat.agent AI agents), load the most relevant skill: `trigger-authoring-chat-agent`, `trigger-authoring-tasks`, `trigger-chat-agent-advanced`, `trigger-cost-savings`, `trigger-getting-started`, `trigger-realtime-and-frontend`.
<!-- TRIGGER.DEV SKILLS END -->

## Multi-thread protocol

This repo is worked on by several parallel Claude Code sessions (threads), each with
a lane. At the start of every session: `git pull`, then read docs/STATE.md.

- Work only in your lane's files (ownership table in docs/STATE.md). If you need a
  change in another lane, add a line under "Requests between threads" in STATE.md.
- Update docs/STATE.md whenever something material lands — the test is "would
  another thread act differently knowing this?" (result, job status change, decision,
  new file another lane consumes). One-liners with pointers, never pasted content;
  add a dated line to "Recent changes", commit, push. Skip intermediate progress.
- Pull again before each new work chunk; parallel threads push to the same branch.
- Keep STATE.md under ~2 screens: it is a dashboard. Details go in docs/ reports.

## Research working agreements (apply in every thread)

- Use Fable for everything (no delegating to smaller models). Don't build
  preliminary versions of a deliverable while waiting on a long-running task.
- Dynamics, not binaries: frame experiments as mapping trajectory distributions,
  regimes, force interactions, and off-target effects — never "does X stabilize?".
- Readable writing: no invented shorthand (D1, vN); include verbatim prompts and
  actual numbers; never name a scale or readout without its measurement recipe and
  representative examples; write "minus" when subtraction is meant, not "vs";
  sections must skim standalone.
- Pilot before spend: ~$1 pilot (saturation, judge calibration, one end-to-end
  rollout) gates any paid ensemble; check the credit balance first.
- Experiments ship as self-contained specs/scripts (papers, datasets, eval items
  inline), one directory per experiment under experiments/.
- Python runs via uv, never pip/venv/poetry.
- Kaggle: account hirokenzan; pushes need --accelerator NvidiaTeslaT4; never read
  credential files.
- Colab deliverables are one self-contained cell.

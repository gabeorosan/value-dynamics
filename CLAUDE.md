<!-- TRIGGER.DEV SKILLS START -->
## Trigger.dev agent skills

This project has Trigger.dev agent skills installed in `.claude/skills/`. Before writing or changing Trigger.dev code (background tasks, scheduled tasks, realtime, or chat.agent AI agents), load the most relevant skill: `trigger-authoring-chat-agent`, `trigger-authoring-tasks`, `trigger-chat-agent-advanced`, `trigger-cost-savings`, `trigger-getting-started`, `trigger-realtime-and-frontend`.
<!-- TRIGGER.DEV SKILLS END -->

## Multi-thread protocol

This repo is worked on by several parallel Claude Code sessions (threads), each with
a lane. At the start of every session: `git pull`, then read docs/STATE.md.

- Work only in your lane's files (ownership table in docs/STATE.md). If you need a
  change in another lane, add a line under "Requests between threads" in STATE.md.
- When a unit of work lands: update your section of docs/STATE.md (one-liners with
  pointers, never pasted content), add a dated line to "Recent changes", commit, push.
- Pull again before each new work chunk; parallel threads push to the same branch.
- Keep STATE.md under ~2 screens: it is a dashboard. Details go in docs/ reports.

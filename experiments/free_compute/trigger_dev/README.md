# Trigger.dev Smoke

Trigger.dev is useful here as an orchestrator: queue jobs, monitor long-running experiments, retry failed launches, and call out to provider APIs. It is not a GPU fine-tuning runtime by itself.

Current local state:

- `/Users/gabriel/.codex/config.toml` already has `[mcp_servers.trigger]` configured as `npx trigger.dev@4.5.0 mcp`.
- `npx trigger.dev@4.5.0 mcp` was fetch-tested with `npm_config_cache=/private/tmp/npm-cache`; it boots as a long-running MCP server.
- No `TRIGGER_ACCESS_TOKEN` or `TRIGGER_SECRET_KEY` env var is visible in this shell, so repo-local API/task actions still need dashboard auth or the MCP tools to load in a fresh Codex session.

Recommended setup when you want a repo-owned Trigger project:

```bash
cd /Users/gabriel/projects/value-dynamics
npm_config_cache=/private/tmp/npm-cache npx trigger.dev@4.5.0 init
```

Then add a first task that shells out through `uv run --no-project python experiments/free_compute/smoke_payload.py` or triggers Hugging Face/Colab Enterprise/Lightning API calls. Keep GPU work on the remote provider and use Trigger.dev for durable orchestration and status polling.

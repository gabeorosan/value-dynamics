# Running Colab autonomously (colab-mcp runbook)

Goal: drive Colab the way we drive Kaggle — push a script, poll status, pull
outputs — with no human copy-paste. Written 2026-07-08 after researching
github.com/googlecolab/colab-mcp (source, discussions) and smoke-testing the
server locally (installs and runs under uvx, Python 3.13).

## The three components

| Kaggle verb | Colab equivalent | Served by |
|---|---|---|
| `kaggle kernels push` | `create_cell` + `execute_cell` with the one-cell script | colab-mcp (proxy to the browser tab) |
| `kaggle kernels status` | `get_cell_output` / `get_notebook_state`, polled | colab-mcp |
| `kaggle kernels output` | download result JSON from Drive into experiments/*/output/ | Google Drive connector (claude.ai) |
| (no equivalent) | pick GPU runtime, click reconnect, dismiss idle popups | claude-in-chrome MCP (Chrome extension) |

1. **colab-mcp** (this repo's .mcp.json): a local websocket proxy. On its own it
   exposes ONE tool, `open_colab_browser_connection`. The notebook-editing tools
   live in the Colab web frontend and appear only after a browser tab connects
   back to the proxy. Reported tool set once connected (verify by listing tools
   on first connect): `create_cell`, `edit_cell`, `execute_cell`,
   `get_cell_output`, `get_notebook_state`, `delete_cell`, `move_cell`.
   Notebook kernel state persists between calls.
2. **claude-in-chrome MCP**: does everything a human would click — open a
   notebook URL, Runtime → Change runtime type → T4 GPU, Connect, reconnect
   after a disconnect. This is what removes the human from the loop.
3. **Google Drive connector**: our Colab scripts already mount Drive and write
   outputs there; pull result files from Drive into experiments/*/output/
   without touching the tab.

## Connection recipe

1. Start a session in this repo; approve the `colab-mcp` MCP server when
   prompted (first time only). Requirement: user signed into Google in Chrome.
2. Call `open_colab_browser_connection`. It opens
   `colab.research.google.com/notebooks/empty.ipynb#mcpProxyToken=<token>&mcpProxyPort=<port>`
   in the default browser and waits up to 60 s for the tab to dial back.
   The editing tools then unlock (the client gets a tools-list-changed
   notification).
3. To drive a SPECIFIC notebook instead of the scratch one (the tool has no
   notebook parameter — known gap, discussion #80): read the
   `#mcpProxyToken=…&mcpProxyPort=…` fragment off the scratch tab's URL with the
   Chrome MCP, close the scratch tab (the proxy accepts one connection at a
   time), then open `<your notebook URL>#<same fragment>`. Colab also has a
   "connect to a local MCP server" dialog where token and port can be pasted.
4. Select the GPU via Chrome MCP (Runtime → Change runtime type → T4, Save,
   Connect). The MCP tools cannot do this.
5. Push and run: `create_cell` with the one-cell experiment script,
   `execute_cell`, then poll `get_cell_output`. Poll at long intervals
   (20–30 min) — these are multi-hour runs.
6. Pull results: script writes JSON to Drive (house style already) → download
   via the Drive connector into experiments/*/output/. Fallback when Drive
   isn't mounted: execute a cell that prints the JSON (base64-chunk anything
   over a few hundred KB) and read it from `get_cell_output`.

## Drive mount in the bootstrap cell (learned 2026-07-09, the hard way)

- ALWAYS mount Drive explicitly at the top of the bootstrap cell and use
  `force_remount=True`; never trust a prior cell's cached "Drive already mounted"
  message after a VM swap (that message may be stale output from a dead VM):
  `from google.colab import drive; drive.mount('/content/drive', force_remount=True)`
- Follow it with a guard assert on a known artifact so a missing/unmounted Drive
  fails LOUDLY instead of the script silently rebuilding the organism (~35 min
  wasted) and writing to ephemeral local disk:
  `import os; assert os.path.isdir('/content/drive/MyDrive/value_dynamics/em_organism/em_organism_adapter'), 'organism adapter missing'`
- `ValueError: mount failed` (FAQ link `#drive-timeout`) that persists across
  force_remount AND a fresh VM is NOT a VM-local problem — it is account/Drive-side
  (Drive backend timeout, or Colab's Drive authorization needs revoke+regrant at
  myaccount.google.com/permissions). Do not spin fresh VMs to fix it; escalate to
  the user. No GPU is wasted since it fails before model load.
- Treat Drive result JSON (via the Drive connector) as the source of truth for
  monitoring, not the Colab notebook UI — the UI showed stale cached cell outputs,
  buffered/empty output panes, and phantom "connected" states all through the
  overnight run; the Drive file never lied.

## Failure modes (from github discussions, worth knowing before they bite)

- **Tools never unlock after connecting** (#100): orphaned colab-mcp processes
  from previous sessions keep their ports and tokens, and the Colab frontend
  caches the OLD token/port, reconnecting to the dead server. Fix requires BOTH:
  `pkill -f colab-mcp`, AND wipe colab.research.google.com cookies, then
  restart the session.
- **Single connection**: the proxy accepts exactly one Colab tab. Only one
  thread may hold the Colab connection at a time — by default the Analysis
  thread (it owns run monitoring). Other threads request Colab actions via
  STATE.md "Requests between threads".
- **Disconnects still happen**: this manages a live browser session; free-tier
  idle/usage limits are unchanged. Scripts must stay checkpoint-resumable
  (house style already). On disconnect: Chrome MCP reconnects the runtime and
  re-runs the cell; the script's resume logic does the rest.
- **Token/port change every server restart**: the fragment from a previous
  session is dead; always re-derive it from a fresh
  `open_colab_browser_connection` call.

## Headless mode: not available to us (checked 2026-07-08)

A true browserless runtime mode exists in the codebase's history (OAuth +
jupyter-kernel-client straight to the Colab runtime; the `caneiro/colab-mcp`
fork ships it with GPU-selection flags), but it needs the
`googleapis.com/auth/colaboratory` OAuth scope, which is not grantable in a
public Google Cloud project (discussion #41, unanswered) — effectively
Google-internal. Revisit if Google opens the scope; that would make Colab fully
Kaggle-equivalent with no browser at all.

## First-session verification checklist

- [ ] colab-mcp server approved and listed; `open_colab_browser_connection` visible
- [ ] connection succeeds; enumerate and record the actual proxied tool names here
- [ ] fragment hand-off to a real notebook works (step 3)
- [ ] GPU runtime selected via Chrome MCP
- [ ] trivial cell executed, output read back
- [ ] a Drive-written file pulled into the repo via the Drive connector

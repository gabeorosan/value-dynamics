# Free Compute Setup Notes

This directory is a reality-checked starting point for testing the free or
nominally free compute surfaces suggested for fine-tuning experiments.

## Current verdict

| surface | useful for this repo? | caveat |
|---|---:|---|
| Hugging Face ZeroGPU / Spaces | yes, for small smoke tests and hosted demos | using existing ZeroGPU Spaces is free, but hosting a personal ZeroGPU Space requires HF PRO; organization hosting requires Team/Enterprise |
| Hugging Face AutoTrain | weak fit | Hugging Face marks AutoTrain unmaintained; use it only for legacy/manual experiments, and prefer TRL/Axolotl for serious fine-tunes |
| Trigger.dev | yes, as orchestration | not a GPU provider; use it to launch and monitor jobs elsewhere |
| Lightning AI | maybe | needs account credits/CLI; test before planning around it |
| Google Colab + Colab MCP | yes, now the main free-Colab path | open a Colab notebook in the browser, then let an MCP-compatible local agent control cells via `uvx git+https://github.com/googlecolab/colab-mcp` |
| Colab Enterprise REST | yes, if GCP is available | this is Vertex AI-backed Google Cloud, not ordinary free Colab |

## Local checks

```bash
uv run --no-project python experiments/free_compute/check_free_compute.py
uv run --no-project python experiments/free_compute/check_free_compute.py --network
uv run --no-project python experiments/free_compute/smoke_payload.py --out outputs/free_compute_smoke.json
```

The checker does not create resources or print token values.

To smoke-test Colab MCP through `uvx`:

```bash
UV_CACHE_DIR=/private/tmp/uv-cache uv run --no-project python experiments/free_compute/check_free_compute.py --smoke-colab-mcp
```


## Hugging Face ZeroGPU smoke

The folder `hf_space_zero_gpu/` is a minimal Gradio Space. Push it to a Space,
select ZeroGPU hardware if your account can host it, then press **Run GPU Smoke**.

Manual upload path:

```bash
cd experiments/free_compute/hf_space_zero_gpu
hf auth login
hf repo create USER/value-dynamics-zerogpu-smoke --type space --sdk gradio
hf upload USER/value-dynamics-zerogpu-smoke . . --repo-type space
```

If the `hf` CLI is unavailable, use the Hugging Face web UI to create a Gradio
Space and upload the three files in this folder.

Current auth note: `HUGGINGFACE_TOKEN` verifies as `hirokenzan`, but a create-space attempt for `hirokenzan/value-dynamics-free-compute-smoke` returned 403, so this token likely lacks Space write/create scope.

## Colab MCP

Colab MCP is now registered in `/Users/gabriel/.codex/config.toml` as:

```toml
[mcp_servers.colab_mcp]
command = "/Users/gabriel/.local/bin/uvx"
args = [ "git+https://github.com/googlecolab/colab-mcp" ]
startup_timeout_sec = 30

[mcp_servers.colab_mcp.env]
UV_CACHE_DIR = "/private/tmp/uv-cache"
```

After restarting Codex or opening a fresh session, the Colab MCP server should be loadable by the app. The required human step is to open a Google Colab notebook in a browser session where you are signed in; the MCP server bridges the local agent to that live notebook.

## Colab smoke

Regenerate the notebook after changing `smoke_payload.py`:

```bash
uv run --no-project python scripts/build_free_compute_colab_notebook.py
```

Then open `experiments/free_compute/colab_smoke.ipynb` in Colab, choose a GPU
runtime if needed, and run all cells.

## Trigger.dev

See `trigger_dev/README.md`. Use Trigger.dev only after choosing the actual remote
runtime. It can be the monitor/retry layer for these experiments.

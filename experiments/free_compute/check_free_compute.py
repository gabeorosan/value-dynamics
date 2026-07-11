"""Capability checks for free/cheap fine-tuning surfaces.

The checker is conservative by default: it does not create cloud resources, install
packages, or print secrets. Add --network to verify token-backed API reachability.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any


HF_TOKEN_KEYS = ("HF_TOKEN", "HUGGINGFACE_TOKEN", "HUGGING_FACE_HUB_TOKEN")
TRIGGER_TOKEN_KEYS = ("TRIGGER_ACCESS_TOKEN", "TRIGGER_SECRET_KEY")
LIGHTNING_KEYS = ("LIGHTNING_USER_ID", "LIGHTNING_CLOUD_PROJECT_ID", "LIGHTNING_API_KEY")
GCP_KEYS = ("GOOGLE_CLOUD_PROJECT", "GCP_PROJECT", "CLOUDSDK_CORE_PROJECT")
CODEX_CONFIG = Path("/Users/gabriel/.codex/config.toml")
COLAB_MCP_UVX = "git+https://github.com/googlecolab/colab-mcp"


@dataclass
class Check:
    provider: str
    status: str
    notes: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


def present(keys: tuple[str, ...]) -> list[str]:
    return [key for key in keys if os.environ.get(key)]


def run(cmd: list[str], timeout: int = 20) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=timeout,
        )
    except Exception as exc:
        return 127, repr(exc)
    return proc.returncode, proc.stdout.strip()


def config_contains(pattern: str) -> bool:
    try:
        return pattern in CODEX_CONFIG.read_text()
    except OSError:
        return False


def http_json(url: str, token: str | None = None) -> tuple[int, Any]:
    headers = {"User-Agent": "value-dynamics-free-compute-check/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode("utf-8"))
        except Exception:
            body = {"error": exc.reason}
        return exc.code, body
    except Exception as exc:
        return 0, {"error": repr(exc)}


def check_huggingface(network: bool) -> Check:
    keys = present(HF_TOKEN_KEYS)
    notes = []
    details: dict[str, Any] = {
        "token_env_keys_present": keys,
        "hf_cli": bool(shutil.which("hf")),
        "huggingface_cli": bool(shutil.which("huggingface-cli")),
    }
    if not keys:
        return Check(
            "huggingface",
            "missing",
            ["No Hugging Face token env var is present."],
            details,
        )

    notes.append("Token is present; value was not printed.")
    if network:
        token = os.environ[keys[0]]
        status, body = http_json("https://huggingface.co/api/whoami-v2", token)
        details["whoami_status"] = status
        if status == 200:
            details["name"] = body.get("name")
            details["type"] = body.get("type")
            details["org_count"] = len(body.get("orgs", []))
            notes.append("HF API token check succeeded.")
            status_name = "ok"
        else:
            details["whoami_error"] = body
            notes.append("HF API token check failed.")
            status_name = "partial"
    else:
        notes.append("Run with --network to verify the token against whoami-v2.")
        status_name = "partial"

    notes.append("ZeroGPU can be used by anyone on existing Spaces, but hosting a personal ZeroGPU Space requires PRO; org hosting requires Team/Enterprise.")
    notes.append("AutoTrain exists but Hugging Face currently marks it unmaintained; prefer TRL/Axolotl for real runs.")
    return Check("huggingface", status_name, notes, details)


def check_trigger(network: bool) -> Check:
    keys = present(TRIGGER_TOKEN_KEYS)
    details = {
        "token_env_keys_present": keys,
        "npm": shutil.which("npm"),
        "node": shutil.which("node"),
        "codex_mcp_configured": config_contains("[mcp_servers.trigger]"),
    }
    notes = [
        "Trigger.dev is an orchestrator/background-job surface, not a GPU training provider.",
        "Use it to launch/monitor HF, Kaggle, Modal, Lightning, or Colab Enterprise jobs once credentials exist.",
    ]
    status_name = "partial" if details["npm"] and details["node"] else "missing"
    if not keys:
        notes.append("No Trigger.dev token env var is present.")
    else:
        notes.append("Trigger token is present; value was not printed.")
    if details["codex_mcp_configured"]:
        notes.append("Codex config includes a Trigger.dev MCP server entry.")
    if network:
        notes.append("No resource-creation API call was made; the configured MCP command was smoke-tested separately with npx.")
    return Check("trigger.dev", status_name, notes, details)


def check_lightning(network: bool) -> Check:
    keys = present(LIGHTNING_KEYS)
    cli = shutil.which("lightning")
    details = {"env_keys_present": keys, "lightning_cli": cli}
    notes = [
        "Lightning AI can be a useful managed notebook/studio runtime if the account has credits.",
        "This machine does not have a Lightning CLI unless lightning_cli is populated below.",
    ]
    if cli:
        code, out = run([cli, "--version"])
        details["version_code"] = code
        details["version_output"] = out[:500]
        status_name = "partial"
    else:
        status_name = "missing"
    if keys:
        notes.append("Lightning env markers are present; values were not printed.")
    return Check("lightning_ai", status_name, notes, details)


def check_colab(network: bool) -> Check:
    gcloud = shutil.which("gcloud")
    uv = shutil.which("uv")
    uvx = shutil.which("uvx") or "/Users/gabriel/.local/bin/uvx"
    project_keys = present(GCP_KEYS)
    details = {
        "gcloud": gcloud,
        "project_env_keys_present": project_keys,
        "uv": uv,
        "uvx": uvx if Path(uvx).exists() else shutil.which("uvx"),
        "codex_colab_mcp_configured": config_contains("[mcp_servers.colab_mcp]"),
    }
    notes = [
        "Consumer Colab is free but interactive and quota-variable.",
        "Colab MCP is the practical free-Colab automation path: it lets a local MCP client control an open Colab notebook session.",
        "The official REST API path is Colab Enterprise via Vertex AI notebookExecutionJobs, which is a Google Cloud surface.",
    ]
    status_name = "partial" if details["uvx"] else "manual"
    if details["codex_colab_mcp_configured"]:
        notes.append("Codex config includes a Colab MCP server entry.")
    if network and gcloud:
        code, out = run([gcloud, "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"])
        details["gcloud_active_account_code"] = code
        details["gcloud_active_account_present"] = bool(out.strip())
    return Check("colab", status_name, notes, details)


def check_colab_mcp_smoke() -> Check:
    uvx = shutil.which("uvx") or "/Users/gabriel/.local/bin/uvx"
    details: dict[str, Any] = {
        "uvx": uvx if Path(uvx).exists() else shutil.which("uvx"),
        "uv_cache_dir": os.environ.get("UV_CACHE_DIR", "/private/tmp/uv-cache"),
        "source": COLAB_MCP_UVX,
    }
    if not details["uvx"]:
        return Check("colab_mcp_smoke", "missing", ["uvx is not available."], details)

    env = os.environ.copy()
    env.setdefault("UV_CACHE_DIR", "/private/tmp/uv-cache")
    try:
        proc = subprocess.run(
            [uvx, "--from", COLAB_MCP_UVX, "colab-mcp", "--help"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=120,
            env=env,
        )
    except Exception as exc:
        details["error"] = repr(exc)
        return Check("colab_mcp_smoke", "partial", ["Colab MCP smoke command did not complete."], details)

    details["returncode"] = proc.returncode
    details["output_tail"] = proc.stdout.strip()[-1000:]
    if proc.returncode == 0 and "ColabMCP is an MCP server" in proc.stdout:
        return Check("colab_mcp_smoke", "ok", ["uvx can fetch and run googlecolab/colab-mcp."], details)
    return Check("colab_mcp_smoke", "partial", ["uvx ran but the expected Colab MCP help text was not found."], details)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", action="store_true", help="verify token-backed APIs without creating resources")
    parser.add_argument("--smoke-colab-mcp", action="store_true", help="fetch and run colab-mcp --help with uvx")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    checks = [
        check_huggingface(args.network),
        check_trigger(args.network),
        check_lightning(args.network),
        check_colab(args.network),
    ]
    if args.smoke_colab_mcp:
        checks.append(check_colab_mcp_smoke())
    payload = {"python": sys.version.split()[0], "checks": [check.__dict__ for check in checks]}
    if args.json:
        print(json.dumps(payload, indent=2))
        return

    for check in checks:
        print(f"[{check.status}] {check.provider}")
        for note in check.notes:
            print(f"  - {note}")
        print(f"  details: {json.dumps(check.details, sort_keys=True)}")


if __name__ == "__main__":
    main()

"""Tiny runtime smoke payload for free/cheap compute surfaces.

This is intentionally small: it verifies Python, optional PyTorch, GPU visibility,
and a few optimizer steps without downloading models or touching external APIs.
Use it as the first payload on a new runtime before spending quota on a real
fine-tune.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import sys
import time
from pathlib import Path


def run_torch_probe(steps: int) -> dict:
    try:
        import torch
    except Exception as exc:  # pragma: no cover - depends on remote image
        return {"available": False, "error": repr(exc)}

    started = time.time()
    cuda_available = torch.cuda.is_available()
    device = torch.device("cuda" if cuda_available else "cpu")
    result = {
        "available": True,
        "version": torch.__version__,
        "cuda_available": cuda_available,
        "device": str(device),
        "device_name": torch.cuda.get_device_name(0) if cuda_available else None,
    }

    x = torch.randn(128, 16, device=device)
    y = (x.sum(dim=1, keepdim=True) > 0).float()
    model = torch.nn.Sequential(
        torch.nn.Linear(16, 32),
        torch.nn.Tanh(),
        torch.nn.Linear(32, 1),
    ).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-3)
    loss_value = None
    for _ in range(steps):
        opt.zero_grad(set_to_none=True)
        loss = torch.nn.functional.binary_cross_entropy_with_logits(model(x), y)
        loss.backward()
        opt.step()
        loss_value = float(loss.detach().cpu())

    if cuda_available:
        torch.cuda.synchronize()
        result["max_memory_mb"] = round(torch.cuda.max_memory_allocated() / 1024**2, 3)
    result["final_loss"] = loss_value
    result["elapsed_sec"] = round(time.time() - started, 3)
    return result


def build_report(steps: int) -> dict:
    return {
        "ok": True,
        "timestamp": int(time.time()),
        "hostname": socket.gethostname(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "env": {
            "HF_HOME": bool(os.environ.get("HF_HOME")),
            "HF_TOKEN": bool(os.environ.get("HF_TOKEN")),
            "HUGGINGFACE_TOKEN": bool(os.environ.get("HUGGINGFACE_TOKEN")),
            "COLAB_GPU": os.environ.get("COLAB_GPU"),
            "LIGHTNING_CLOUD_PROJECT_ID": bool(os.environ.get("LIGHTNING_CLOUD_PROJECT_ID")),
            "TRIGGER_API_URL": bool(os.environ.get("TRIGGER_API_URL")),
        },
        "torch": run_torch_probe(steps),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--out", type=Path, default=Path("free_compute_smoke.json"))
    args = parser.parse_args()

    report = build_report(args.steps)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

from __future__ import annotations

import json
import platform
import time

import gradio as gr
import torch

try:
    import spaces
except Exception:  # Allows local CPU testing outside HF Spaces.
    spaces = None


def gpu_decorator(fn):
    if spaces is None:
        return fn
    return spaces.GPU(duration=60)(fn)


@gpu_decorator
def run_smoke() -> str:
    started = time.time()
    cuda_available = torch.cuda.is_available()
    device = torch.device("cuda" if cuda_available else "cpu")

    x = torch.randn(128, 16, device=device)
    y = (x.sum(dim=1, keepdim=True) > 0).float()
    model = torch.nn.Sequential(
        torch.nn.Linear(16, 32),
        torch.nn.Tanh(),
        torch.nn.Linear(32, 1),
    ).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-3)
    loss_value = None
    for _ in range(8):
        opt.zero_grad(set_to_none=True)
        loss = torch.nn.functional.binary_cross_entropy_with_logits(model(x), y)
        loss.backward()
        opt.step()
        loss_value = float(loss.detach().cpu())

    if cuda_available:
        torch.cuda.synchronize()

    report = {
        "ok": True,
        "python": platform.python_version(),
        "torch": torch.__version__,
        "cuda_available": cuda_available,
        "device": str(device),
        "device_name": torch.cuda.get_device_name(0) if cuda_available else None,
        "max_memory_mb": round(torch.cuda.max_memory_allocated() / 1024**2, 3)
        if cuda_available
        else None,
        "final_loss": loss_value,
        "elapsed_sec": round(time.time() - started, 3),
        "spaces_module_loaded": spaces is not None,
    }
    return json.dumps(report, indent=2)


with gr.Blocks(title="Value Dynamics ZeroGPU Smoke") as demo:
    gr.Markdown("# Value Dynamics ZeroGPU Smoke")
    run = gr.Button("Run GPU Smoke")
    output = gr.Code(label="Runtime report", language="json")
    run.click(run_smoke, outputs=output)


if __name__ == "__main__":
    demo.launch()

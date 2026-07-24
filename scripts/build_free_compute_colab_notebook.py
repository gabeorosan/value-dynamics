"""Build a tiny Colab smoke notebook for free-compute testing."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "experiments" / "free_compute" / "smoke_payload.py"
OUT = ROOT / "experiments" / "free_compute" / "colab_smoke.ipynb"


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.splitlines(keepends=True)}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": text.splitlines(keepends=True),
    }


cells = [
    md(
        "# Value Dynamics Colab Smoke\n\n"
        "Use this to test whether the current Colab session actually has usable compute. "
        "Set **Runtime -> Change runtime type -> GPU** first if you want to test GPU."
    ),
    code("!nvidia-smi -L || true"),
    code("!python --version"),
    code(f"%%writefile smoke_payload.py\n{PAYLOAD.read_text()}"),
    code("!python smoke_payload.py --out free_compute_smoke.json"),
    code(
        "from google.colab import files\n"
        "files.download('free_compute_smoke.json')"
    ),
]

nb = {
    "cells": cells,
    "metadata": {
        "accelerator": "GPU",
        "colab": {"provenance": []},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 0,
}

OUT.write_text(json.dumps(nb, indent=1) + "\n")
print(f"wrote {OUT}")

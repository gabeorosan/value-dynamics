"""Cerebrium runner for the TMAY free-form self-description experiment
(experiments/tmay_freeform/SPEC.md). Same pattern as experiments/cerebrium_k2:
no pip deps in the toml (free-plan constraint), runtime bootstrap, the
experiment script fetched at a pinned commit so runs are byte-reproducible.

Invoke from this directory:
  cerebrium run main.py::run --data '{"mode": "inventory"}'
  cerebrium run main.py::run --data '{"mode": "generate", "tag": "pilot",
    "n_samples": 5, "checkpoints": [
      {"name": "base", "adapter": null},
      {"name": "sch7_s2_rail_r8",
       "adapter": "/persistent-storage/k2rel_out/vintages/sch7_s2_r8/sch7_s2"}]}'
"""

import importlib.util
import json
import os
import subprocess
import sys
import urllib.request

COMMIT = "fdb780d8808446f4f5e14be614041ff61ada7286"
URL = ("https://raw.githubusercontent.com/gabeorosan/value-dynamics/"
       f"{COMMIT}/experiments/tmay_freeform/script.py")


def run(data=None, **kw):
    if isinstance(data, str):
        data = json.loads(data)
    params = {**(data or {}), **kw}
    os.environ.setdefault("HF_HOME", "/persistent-storage/hf_cache")
    os.environ.setdefault("PIP_CACHE_DIR", "/persistent-storage/pip_cache")
    os.makedirs(os.environ["PIP_CACHE_DIR"], exist_ok=True)
    if params.get("mode", "inventory") != "inventory":
        # torch<2.13: this image has no gcc; newer torch JIT-compiles C
        print("## bootstrap pip install", flush=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                        "torch<2.13", "transformers>=4.53.0", "numpy",
                        "peft", "accelerate", "bitsandbytes"], check=True)
    src = urllib.request.urlopen(URL, timeout=60).read().decode()
    with open("/tmp/tmay_script.py", "w") as f:
        f.write(src)
    spec = importlib.util.spec_from_file_location("tmay", "/tmp/tmay_script.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.run(params)

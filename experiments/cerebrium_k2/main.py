"""Cerebrium runner for K2 (OLMo conservative inversion, PLAN K2 row).

One invocation = one small batch of rollouts (default: a single confirmatory
seed on one condition, ~70-130 min on a T4), so an unknown free-compute quota
can never truncate a seed mid-flight: every completed rollout is a complete,
independently valid trajectory. Results and per-round vintages land on
persistent storage (/persistent-storage/k2_out) and resume-skip makes
re-invocation idempotent.

The experiment script itself is NOT copied here: it is fetched at a pinned
commit from GitHub (same pattern as the Colab launchers), so Kaggle and
Cerebrium run byte-identical code. Gates (a)+(b) run inside the script against
/persistent-storage/k2_dataset (uploaded once via `cerebrium cp`), which holds
the verified dataset layout: olmo_conservative_install.json +
screen_attestation.json at root, rung_20/ adapter beneath.
"""

import importlib.util
import json
import os
import subprocess
import sys
import time
import urllib.request

K2_COMMIT = "822aebf706769ea2c03f6a07cf80ff0edd8172ba"
K2_URL = ("https://raw.githubusercontent.com/gabeorosan/value-dynamics/"
          f"{K2_COMMIT}/experiments/kaggle/kaggle_k2_olmo_inversion/script.py")

DATASET_DIR = "/persistent-storage/k2_dataset"
OUT_DIR = "/persistent-storage/k2_out"
HF_CACHE = "/persistent-storage/hf_cache"


def run(data=None, **kw):
    # `cerebrium run --data '{...}'` delivers the payload as a single `data`
    # kwarg; direct callers may pass plain kwargs. Accept both.
    if isinstance(data, str):
        data = json.loads(data)
    params = {**(data or {}), **kw}
    conditions = params.get("conditions", "frozen_cons_r0")
    seeds_conf = params.get("seeds_conf", "0")
    seeds_ctrl = params.get("seeds_ctrl", "0,1,2")
    rounds = params.get("rounds", "4")
    persist_rounds = params.get("persist_rounds", "0,4")
    result_name = params.get("result_name", "k2_olmo_inversion_cerebrium.json")
    t0 = time.time()
    for d in (OUT_DIR, HF_CACHE):
        os.makedirs(d, exist_ok=True)
    # torch >= 2.13 routes some EAGER ops through triton codegen
    # (torch/_native), which JIT-compiles C and dies in this image (no gcc,
    # no apt). torch < 2.13 uses classic cuBLAS dispatch and needs no
    # compiler. Pip cache on persistent storage so repeat cold starts skip
    # the ~3 GB download.
    os.environ.setdefault("PIP_CACHE_DIR", "/persistent-storage/pip_cache")
    os.makedirs(os.environ["PIP_CACHE_DIR"], exist_ok=True)
    print("## bootstrap pip install: torch<2.13 + transformers", flush=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "torch<2.13", "transformers>=4.53.0", "numpy"], check=True)
    assert os.path.isdir(DATASET_DIR), (
        f"{DATASET_DIR} missing — upload with: cerebrium cp <staging>/k2_dataset k2_dataset")
    os.environ.update({
        "CONS_ADAPTER_ENV": DATASET_DIR,
        "OUT_ENV": OUT_DIR,
        "HF_HOME": HF_CACHE,
        "CONDITIONS_ENV": conditions,
        "SEEDS_CONF_ENV": seeds_conf,
        "SEEDS_CTRL_ENV": seeds_ctrl,
        "ROUNDS_ENV": rounds,
        "PERSIST_ROUNDS_ENV": persist_rounds,
        "RESULT_NAME_ENV": result_name,
    })
    src = urllib.request.urlopen(K2_URL).read().decode()
    status = "ok"
    detail = ""
    try:
        exec(compile(src, "kaggle_k2_olmo_inversion/script.py", "exec"), {"__name__": "__main__"})
    except SystemExit as e:  # gate failures raise SystemExit with a message
        status, detail = "systemexit", str(e)
    result_path = os.path.join(OUT_DIR, result_name)
    summary = {}
    if os.path.exists(result_path):
        allres = json.load(open(result_path))
        for sd, conds in allres.items():
            if not sd.isdigit():
                continue
            for cond, res in conds.items():
                traj = res.get("traj", [])
                summary[f"{cond}:s{sd}"] = {
                    "rounds_done": max(0, len(res.get("battery", [])) - 1),
                    "traj": [round(float(x), 3) for x in traj],
                }
        if "_budget_checkpoint" in allres:
            summary["_budget_checkpoint"] = allres["_budget_checkpoint"]
    return {"status": status, "detail": detail, "elapsed_min": round((time.time() - t0) / 60, 1),
            "result_path": result_path, "summary": summary}

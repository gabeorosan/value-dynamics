"""Cerebrium WORKER for K2 (OLMo conservative inversion) — deploy, don't run.

`cerebrium run` kills invocations at ~13-15 min regardless of
response_grace_period (measured 2026-07-11: three silent kills at that wall),
so this app runs the K2 confirmatory contrast in a daemon thread started at
module import. The replica (min_replicas=1) stays alive with no requests;
the thread execs the pinned K2 script once, which loops over all configured
rollouts with per-rollout atomic saves + resume-skip on persistent storage.
If the replica is restarted, the thread simply resumes from the last
completed rollout. On completion it writes k2_out/WORKER_DONE — poll with
`cerebrium ls k2_out` and then DELETE THE APP (it bills while alive).
"""

import json
import os
import subprocess
import sys
import threading
import time
import traceback
import urllib.request

K2_COMMIT = "6a276d3a1bcef8abd94e6b997e6f013405d083a1"
K2_URL = ("https://raw.githubusercontent.com/gabeorosan/value-dynamics/"
          f"{K2_COMMIT}/experiments/kaggle/kaggle_k2_olmo_inversion/script.py")

DATASET_DIR = "/persistent-storage/k2_dataset"
OUT_DIR = "/persistent-storage/k2_out"
HF_CACHE = "/persistent-storage/hf_cache"
DONE_MARKER = os.path.join(OUT_DIR, "WORKER_DONE")
FAIL_MARKER = os.path.join(OUT_DIR, "WORKER_FAILED")

# The full confirmatory contrast; controls stay on Kaggle. Per-rollout
# resume-skip makes this idempotent across replica restarts.
WORK = {
    "CONDITIONS_ENV": "frozen_cons_r0,frozen_base",
    "SEEDS_CONF_ENV": "0,1,2,3,4,5",
    "SEEDS_CTRL_ENV": "0,1,2",
    "ROUNDS_ENV": "4",
    "PERSIST_ROUNDS_ENV": "0,4",
    "RESULT_NAME_ENV": "k2_olmo_inversion_cerebrium.json",
}


def _work():
    try:
        for d in (OUT_DIR, HF_CACHE):
            os.makedirs(d, exist_ok=True)
        for marker in (DONE_MARKER, FAIL_MARKER):
            if os.path.exists(marker):
                os.remove(marker)
        os.environ.setdefault("PIP_CACHE_DIR", "/persistent-storage/pip_cache")
        os.makedirs(os.environ["PIP_CACHE_DIR"], exist_ok=True)
        print("## worker: bootstrap pip (torch<2.13)", flush=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                        "torch<2.13", "transformers>=4.53.0", "numpy"], check=True)
        os.environ.update({"CONS_ADAPTER_ENV": DATASET_DIR, "OUT_ENV": OUT_DIR,
                           "HF_HOME": HF_CACHE, **WORK})
        src = urllib.request.urlopen(K2_URL).read().decode()
        print("## worker: starting K2 confirmatory contrast", flush=True)
        exec(compile(src, "kaggle_k2_olmo_inversion/script.py", "exec"), {"__name__": "__main__"})
        with open(DONE_MARKER, "w") as f:
            json.dump({"finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, f)
        print("## worker: DONE — delete this app to stop billing", flush=True)
    except BaseException:
        err = traceback.format_exc()
        print(f"## worker: FAILED\n{err}", flush=True)
        try:
            with open(FAIL_MARKER, "w") as f:
                f.write(err)
        except OSError:
            pass


_thread = threading.Thread(target=_work, daemon=True, name="k2-worker")
_thread.start()


def run(data=None, **kw):
    """Progress probe (optional): returns rollout completion state."""
    state = {"thread_alive": _thread.is_alive(),
             "done": os.path.exists(DONE_MARKER), "failed": os.path.exists(FAIL_MARKER)}
    result_path = os.path.join(OUT_DIR, WORK["RESULT_NAME_ENV"])
    if os.path.exists(result_path):
        allres = json.load(open(result_path))
        state["rollouts"] = {f"{c}:s{sd}": len(res.get("battery", [])) - 1
                             for sd, conds in allres.items() if sd.isdigit()
                             for c, res in conds.items()}
    return state

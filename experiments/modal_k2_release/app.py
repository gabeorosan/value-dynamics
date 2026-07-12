"""Modal harness for the K2 force-schedule (press-and-release) grid.

One Modal container = ONE rollout cell (schedule x seed), all cells in
parallel on T4s. The K2 script source is passed as a function argument at
launch (no GitHub fetch — robust to flaky local connectivity; the launcher
records its sha256 in the run env). OLMo is baked into the image at build
time so parallel containers don't contend over a shared HF cache volume.

Volume layout (value-dynamics-k2):
  k2_dataset/{olmo_conservative_install.json, screen_attestation.json,
              rung_20/...}          <- organism + gate artifacts (from the
                                       Cerebrium persistent storage copy)
  k2rel_out/                        <- one result JSON + vintages per cell

Launch (after `modal volume put` of the dataset):
  modal run --detach app.py                      # full grid
  modal run app.py --pilot                       # 1 cheap validation cell
Cost envelope: pilot ~$0.3; full grid 11 cells x ~1.4 h T4 ~ $10.
"""

import hashlib
import json
import os

import modal

MODEL = "allenai/Olmo-3-7B-Instruct"
MODEL_REVISION = "6e5971d9eba42665f5bd5a0fcf047f299ce1dccc"

SCHEDULES_ENV = ("press_release=frozen_cons_r0:4+evolving_self:4,"
                 "press_random=frozen_cons_r0:4+random_select:4,"
                 "fan_press=evolving_self:4+frozen_cons_r0:4,"
                 "press_hold=frozen_cons_r0:8")

# (schedule, seed) cells; press_hold gets 2 seeds, the rest 3.
GRID = ([("press_release", s) for s in (1, 2, 3)]
        + [("press_random", s) for s in (1, 2, 3)]
        + [("fan_press", s) for s in (1, 2, 3)]
        + [("press_hold", s) for s in (1, 2)])

app = modal.App("k2-release-grid")
vol = modal.Volume.from_name("value-dynamics-k2", create_if_missing=True)


def _bake_model():
    from huggingface_hub import snapshot_download
    snapshot_download(MODEL, revision=MODEL_REVISION)


image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch<2.13", "transformers>=4.53.0", "numpy",
                 "peft", "accelerate", "bitsandbytes", "huggingface_hub")
    .env({"HF_HOME": "/model_cache"})
    .run_function(_bake_model)
)


@app.function(gpu="T4", timeout=5 * 60 * 60, image=image,
              volumes={"/persistent-storage": vol})
def run_cell(src: str, env: dict):
    import threading
    import time

    os.environ.update(env)
    os.makedirs(env["OUT_ENV"], exist_ok=True)

    def _committer():
        while True:
            time.sleep(300)
            try:
                vol.commit()
            except Exception:
                pass

    threading.Thread(target=_committer, daemon=True).start()
    print(f"## cell {env['CONDITIONS_ENV']} seed {env['SEEDS_CONF_ENV']} "
          f"script_sha256={env['K2_SRC_SHA256'][:16]}", flush=True)
    exec(compile(src, "kaggle_k2_olmo_inversion/script.py", "exec"),
         {"__name__": "__main__"})
    vol.commit()
    return f"done {env['CONDITIONS_ENV']} s{env['SEEDS_CONF_ENV']}"


def _cell_env(sched: str, seed: int, rounds: int, src_sha: str) -> dict:
    return {
        "CONS_ADAPTER_ENV": "/persistent-storage/k2_dataset",
        "OUT_ENV": "/persistent-storage/k2rel_out",
        "HF_HOME": "/model_cache",
        "SCHEDULES_ENV": SCHEDULES_ENV,
        "ROUNDS_ENV": str(rounds),
        "PERSIST_ROUNDS_ENV": "0,4,8" if rounds == 8 else "0," + str(rounds),
        "CONDITIONS_ENV": sched,
        "SEEDS_CONF_ENV": str(seed),
        "SEEDS_CTRL_ENV": "",
        "RESULT_NAME_ENV": f"k2rel_{sched}_s{seed}.json",
        "K2_SRC_SHA256": src_sha,
    }


@app.local_entrypoint()
def main(pilot: bool = False):
    here = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(here, "..", "kaggle", "kaggle_k2_olmo_inversion",
                            "script.py")
    src = open(src_path).read()
    src_sha = hashlib.sha256(src.encode()).hexdigest()
    print(f"script sha256 {src_sha}")
    if pilot:
        # 2-round press_release smoke: exercises the schedule switch, both
        # gates, the volume, and one training round per phase.
        env = _cell_env("press_release", 99, 2, src_sha)
        env["SCHEDULES_ENV"] = "press_release=frozen_cons_r0:1+evolving_self:1"
        env["RESULT_NAME_ENV"] = "k2rel_pilot_s99.json"
        print(run_cell.remote(src, env))
        return
    calls = [run_cell.spawn(src, _cell_env(sched, seed, 8, src_sha))
             for sched, seed in GRID]
    print(f"spawned {len(calls)} cells; detach-safe")
    for c in calls:
        print(c.get())

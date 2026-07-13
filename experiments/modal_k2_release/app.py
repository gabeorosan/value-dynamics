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
                 "press_hold=frozen_cons_r0:8,"
                 "pulse_22=frozen_cons_r0:2+evolving_self:2+frozen_cons_r0:2+evolving_self:2,"
                 "early_release=frozen_cons_r0:2+evolving_self:6,"
                 "press_to_base=frozen_cons_r0:4+frozen_base:4,"
                 "base_hold=frozen_base:8,"
                 # press-depth boundary map (branch c, 2026-07-13): where is
                 # the critical press depth separating absorbing collapse
                 # from base-judge escape? depth-4 = press_to_base (0.000/
                 # 0.389/0.750), depth-0 = base_hold (rails 2/2).
                 "press_d1=frozen_cons_r0:1+frozen_base:7,"
                 "press_d2=frozen_cons_r0:2+frozen_base:6,"
                 "press_d3=frozen_cons_r0:3+frozen_base:5,"
                 # cross-family oracle reversal (branch e): score-based
                 # keep-lowest-risk on RAILED persisted endpoints
                 "oracle_hold=oracle_risk_down:4")

# Gate-1 branches (docs/report_k2_full_contrast_and_release_replan.md):
# branch A (press_release deepens collapse, the predicted outcome) -> the
# diversity-promising release target is the frozen_base judge: press_to_base
# x3 + base_hold x2 (~$6). branch B (press_release rebounds — hysteresis) ->
# the pulse / press-duration shapes probe the memory: pulse_22 x3 +
# early_release x3 + completion cells (~$8).
GRIDS = {
    "a": [("press_to_base", s) for s in (1, 2, 3)]
         + [("base_hold", s) for s in (1, 2)],
    "b": [("pulse_22", s) for s in (1, 2, 3)]
         + [("early_release", s) for s in (1, 2, 3)]
         + [("press_hold", s) for s in (2,)]
         + [("fan_press", s) for s in (3,)],
    # boundary map: 3 depths x 2 seeds, ~$6; prereg in
    # docs/prereg_press_depth_predictions.md (commit BEFORE launching)
    "c": [(d, s) for d in ("press_d1", "press_d2", "press_d3")
          for s in (1, 2)],
}

# branch e (cross-family oracle reversal): (schedule, seed, INIT vintage path)
# — railed OLMo endpoints; prereg docs/prereg_crossfamily_oracle.md
GRID_E = [
    ("oracle_hold", 21,
     "/persistent-storage/k2rel_out/vintages/sch7_s2_r8/sch7_s2"),   # base_hold s2 rail 0.875
    ("oracle_hold", 22,
     "/persistent-storage/k2rel_out/vintages/sch8_s2_r8/sch8_s2"),   # press_d1 s2 rail 1.000
]

# branch m (mixed-generator pools; prereg docs/prereg_mixed_generator.md):
# (schedule spec, seed, INIT vintage or "" for the default organism,
#  MIX_GEN_ENV value). Seeds 31-38 fresh per the unique-seeds rule.
_VINT_7 = "/persistent-storage/k2rel_out/vintages/sch7_s2_r8/sch7_s2"  # base_hold s2 rail 0.875
_VINT_8 = "/persistent-storage/k2rel_out/vintages/sch8_s2_r8/sch8_s2"  # press_d1 s2 rail 1.000
# branch h (head-to-head duels; prereg docs/prereg_head2head_olmo.md):
# same shapes as branch m's judge cells but MIX_JUDGE_ENV=head2head — the
# judge picks directly between the two owners' candidates, no CAUTIOUS_REF.
# Tests whether one-round contamination and the failed conservative rescue
# were reference-scoring artifacts. Seeds 51-58 fresh.
GRID_H = [
    ("h2h_invade_base=frozen_base:4", 51, "", _VINT_8),
    ("h2h_invade_base=frozen_base:4", 52, "", _VINT_8),
    ("h2h_invade_self=evolving_self:4", 53, "", _VINT_8),
    ("h2h_invade_self=evolving_self:4", 54, "", _VINT_8),
    ("h2h_cons_rescue=frozen_cons_r0:4", 55, _VINT_7, "base"),
    ("h2h_cons_rescue=frozen_cons_r0:4", 56, _VINT_8, "base"),
    ("h2h_base_rescue=frozen_base:4", 57, _VINT_7, "base"),
    ("h2h_base_rescue=frozen_base:4", 58, _VINT_8, "base"),
]

# branch h2 (head-to-head risk EROSION, mid-scale start): the plain
# transmission question the extreme-state cells skip — the conservative
# organism (risk ~0.31) trades generations with base (~0.5-0.7 on these
# items) under DIRECT comparison. Does the installed value hold, erode
# toward base, or amplify? Judges: the organism itself (the self-training
# scenario) and frozen base (the neutral-curator scenario). Prereg addendum
# in docs/prereg_head2head_olmo.md. Seeds 61-64 fresh.
GRID_H2 = [
    ("h2h_erode_self=evolving_self:4", 61, "", "base"),
    ("h2h_erode_self=evolving_self:4", 62, "", "base"),
    ("h2h_erode_base=frozen_base:4", 63, "", "base"),
    ("h2h_erode_base=frozen_base:4", 64, "", "base"),
]

GRID_M = [
    # reopen-by-injection: oracle judge + base-model material at railed inits
    # (control = branch e, same inits + judge, self-only pool)
    ("oracle_mix=oracle_risk_down:4", 31, _VINT_7, "base"),
    ("oracle_mix=oracle_risk_down:4", 32, _VINT_8, "base"),
    # realistic-judge rescue: frozen conservative judge + base material
    ("cons_mix=frozen_cons_r0:4", 33, _VINT_7, "base"),
    ("cons_mix=frozen_cons_r0:4", 34, _VINT_8, "base"),
    # invasion: fresh organism, weak/neutral base judge, railed co-generator
    ("invade_base=frozen_base:4", 35, "", _VINT_8),
    ("invade_base=frozen_base:4", 36, "", _VINT_8),
    # self-judge contamination: the scraped-peer-data scenario
    ("invade_self=evolving_self:4", 37, "", _VINT_8),
    ("invade_self=evolving_self:4", 38, "", _VINT_8),
]

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


ADAPTER_SHA256 = "1b0b55f9d6e340c0087c33020ace59eacc25511d0ee59fc6d25db361cc1f1bb2"


@app.function(volumes={"/persistent-storage": vol}, timeout=900)
def assemble_adapter():
    """Reassemble the organism adapter from 10 MB parts uploaded under
    parts/ (whole-file `modal volume put` kept dying on a flaky uplink)."""
    import glob
    import shutil

    parts = sorted(glob.glob("/persistent-storage/parts/adapter_parts_*"))
    dst = "/persistent-storage/k2_dataset/rung_20/adapter_model.safetensors"
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    h = hashlib.sha256()
    with open(dst, "wb") as out:
        for p in parts:
            with open(p, "rb") as f:
                b = f.read()
            h.update(b)
            out.write(b)
    got = h.hexdigest()
    if got != ADAPTER_SHA256:
        os.remove(dst)
        vol.commit()
        return f"SHA MISMATCH from {len(parts)} parts: {got}"
    shutil.rmtree("/persistent-storage/parts")
    vol.commit()
    return f"OK {len(parts)} parts -> {dst} sha256={got[:16]}..."


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
        # no SEEDS_CTRL_ENV: '' crashed the int-parse pre-guard (pilot 1);
        # CONDITIONS_ENV already restricts which conditions run
        "RESULT_NAME_ENV": f"k2rel_{sched}_s{seed}.json",
        "K2_SRC_SHA256": src_sha,
    }


@app.local_entrypoint()
def main(pilot: bool = False, assemble: bool = False, branch: str = ""):
    if assemble:
        print(assemble_adapter.remote())
        return
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
    if branch == "e":
        calls = []
        for sched, seed, init in GRID_E:
            env = _cell_env(sched, seed, 4, src_sha)
            env["INIT_ADAPTER_ENV"] = init
            env["PERSIST_ROUNDS_ENV"] = "0,4"
            # the script asserts EVERY schedule fits ROUNDS; pass only ours
            env["SCHEDULES_ENV"] = "oracle_hold=oracle_risk_down:4"
            calls.append(run_cell.spawn(src, env))
        print(f"spawned {len(calls)} branch-e cells; detach-safe")
        return
    if branch in ("h", "h2"):
        calls = []
        for sched_spec, seed, init, mix in (GRID_H if branch == "h" else GRID_H2):
            sched = sched_spec.split("=")[0]
            env = _cell_env(sched, seed, 4, src_sha)
            env["SCHEDULES_ENV"] = sched_spec
            env["MIX_GEN_ENV"] = mix
            env["MIX_JUDGE_ENV"] = "head2head"
            if init:
                env["INIT_ADAPTER_ENV"] = init
            calls.append(run_cell.spawn(src, env))
        print(f"spawned {len(calls)} branch-h cells; detach-safe")
        return
    if branch == "m":
        calls = []
        for sched_spec, seed, init, mix in GRID_M:
            sched = sched_spec.split("=")[0]
            env = _cell_env(sched, seed, 4, src_sha)
            # the script asserts EVERY schedule fits ROUNDS; pass only ours
            env["SCHEDULES_ENV"] = sched_spec
            env["MIX_GEN_ENV"] = mix
            if init:
                env["INIT_ADAPTER_ENV"] = init
            calls.append(run_cell.spawn(src, env))
        print(f"spawned {len(calls)} branch-m cells; detach-safe")
        return
    if branch not in GRIDS:
        raise SystemExit("pass --branch a (press_to_base+base_hold), "
                         "--branch b (pulse/early_release), c (press-depth), "
                         "e (cross-family oracle reversal), or m "
                         "(mixed-generator pools)")
    grid = GRIDS[branch]
    calls = [run_cell.spawn(src, _cell_env(sched, seed, 8, src_sha))
             for sched, seed in grid]
    print(f"spawned {len(calls)} branch-{branch} cells; detach-safe")
    for c in calls:
        print(c.get())

#!/usr/bin/env python3
"""Build the K1-K3 / RELEASE-CORE rollout manifest.

SCOPE (final-analysis audit 2026-07-13): covers K1/K2/K3, the two Kaggle
release kernels, Modal branch A, and press-depth. It does NOT include
branch e, branch m, transmission-with-support, or the Qwen
oracle-opposition family — analyses over those read their result JSONs
directly (scripts/score_mixed_generator.py, analyze_oracle_opposition.py).
Nothing claiming to be program-wide may cite this manifest alone.

Reaudit 2026-07-12 ("Priority: create one canonical rollout manifest that
deduplicates partial/resumed records by (grid, condition, seed) and records
which source file won"). Every downstream analysis (instrument table,
transition models, scorers) should read THIS manifest's winning records, not
glob the output dirs themselves.

Dedup rule (stated once, applied everywhere): for each (grid, condition, seed)
the record with the MOST rounds wins; on a tie the LATER file in SOURCES order
wins (SOURCES is ordered oldest-first, so resumed/v2 files beat partials).

Usage: python3 scripts/build_rollout_manifest.py
Writes: experiments/rollout_manifest.json
"""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# oldest-first per grid; later files win ties
SOURCES = {
    "K2": [
        "experiments/cerebrium_k2/output/k2_cerebrium_seed0_complete.json",
        "experiments/kaggle/kaggle_k2_olmo_inversion/output_controls/k2_olmo_inversion_kaggle_controls.json",
        "experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_conf_v1_seeds12_partial.json",
        "experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_olmo_inversion_kaggle_conf_v2.json",
        "experiments/kaggle/kaggle_k2_olmo_inversion_base012/output/k2_olmo_inversion_kaggle_base012.json",
    ],
    # separate grid: 8-round schedule rollouts, not poolable with K2's 4-round arms
    "K2_release": [
        "experiments/kaggle/kaggle_k2_release_relA/output/k2_release_kernelA.json",
        "experiments/kaggle/kaggle_k2_release_relB/output/k2_release_kernelB.json",
    ] + [f"experiments/modal_k2_release/output/k2rel_{sched}_s{s}.json"
         for sched in ("press_to_base", "base_hold",
                       "press_d1", "press_d2", "press_d3")
         for s in (1, 2, 3)],
    "K1": ["experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json"],
    "K3": ["experiments/kaggle/kaggle_k3_em_neutral_grid/output/k3_em_neutral.json"],
}


def n_rounds(rec):
    return len(rec.get("rounds_raw", [])) or max(0, len(rec.get("traj", [])) - 1)


def main():
    manifest = {"dedup_rule": "most rounds wins; tie -> later file in SOURCES order",
                "source_sha256": {}, "grids": {}}
    for grid, paths in SOURCES.items():
        win = {}   # (cond, seed) -> dict
        for rel in paths:
            path = os.path.join(ROOT, rel)
            if not os.path.exists(path):
                continue
            manifest["source_sha256"][rel] = hashlib.sha256(
                open(path, "rb").read()).hexdigest()
            d = json.load(open(path))
            for sd in (k for k in d if k.isdigit()):
                for cond, rec in d[sd].items():
                    if not isinstance(rec, dict) or not ("traj" in rec or "rounds_raw" in rec):
                        continue
                    key = (cond, int(sd))
                    cand = {"condition": cond, "seed": int(sd), "source": rel,
                            "n_rounds": n_rounds(rec), "n_traj": len(rec.get("traj", [])),
                            "lost_to": []}
                    if key in win:
                        prev = win[key]
                        if cand["n_rounds"] >= prev["n_rounds"]:
                            cand["lost_to"] = prev["lost_to"] + [
                                f"{prev['source']} ({prev['n_rounds']}r)"]
                            win[key] = cand
                        else:
                            prev["lost_to"].append(f"{rel} ({cand['n_rounds']}r) [shorter, ignored]")
                    else:
                        win[key] = cand
        manifest["grids"][grid] = sorted(win.values(),
                                         key=lambda r: (r["condition"], r["seed"]))
    out = os.path.join(ROOT, "experiments/rollout_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    for grid, rows in manifest["grids"].items():
        dups = [r for r in rows if r["lost_to"]]
        print(f"{grid}: {len(rows)} unique (condition,seed) rollouts; "
              f"{len(dups)} had duplicate records resolved:")
        for r in dups:
            print(f"  {r['condition']} s{r['seed']}: kept {r['source']} "
                  f"({r['n_rounds']}r) over {r['lost_to']}")
    print(f"\nwrote {out}")


def load_winning_records(root=ROOT, grid=None):
    """For import by analysis scripts: yields (grid, condition, seed, record)."""
    man = json.load(open(os.path.join(root, "experiments/rollout_manifest.json")))
    cache = {}
    for g, rows in man["grids"].items():
        if grid and g != grid:
            continue
        for r in rows:
            if r["source"] not in cache:
                blob = open(os.path.join(root, r["source"]), "rb").read()
                want = man.get("source_sha256", {}).get(r["source"])
                got = hashlib.sha256(blob).hexdigest()
                if want and got != want:
                    raise RuntimeError(
                        f"{r['source']} changed since the manifest was built "
                        f"(sha {got[:12]} != {want[:12]}); re-run build_rollout_manifest.py")
                cache[r["source"]] = json.loads(blob)
            yield g, r["condition"], r["seed"], cache[r["source"]][str(r["seed"])][r["condition"]]


if __name__ == "__main__":
    main()

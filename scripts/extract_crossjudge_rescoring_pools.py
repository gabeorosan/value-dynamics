"""Freeze the four round-1 OLMo duel-invasion pools for Colab rescoring.

The output contains candidate text, owner, semantic risk, logged source/base
scores, actual recipient scores/keeps, and observed movement. It deliberately
uses only branch-h duel cells so judging format is held fixed.

Usage:
    python3 scripts/extract_crossjudge_rescoring_pools.py
"""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/crossjudge_rescoring/pools.json"
SOURCE_DIR = ROOT / "experiments/modal_k2_release/output"

CELLS = [
    ("k2rel_h2h_invade_base_s51.json", "51", "h2h_invade_base", "base"),
    ("k2rel_h2h_invade_base_s52.json", "52", "h2h_invade_base", "base"),
    ("k2rel_h2h_invade_self_s53.json", "53", "h2h_invade_self", "v10_rung20"),
    ("k2rel_h2h_invade_self_s54.json", "54", "h2h_invade_self", "v10_rung20"),
]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    pools = []
    sources = []
    outcomes = {}
    for filename, seed, condition, recipient in CELLS:
        path = SOURCE_DIR / filename
        data = json.loads(path.read_text())
        rec = data[seed][condition]
        raw = rec["rounds_raw"][0]
        assert len(raw) == 12, f"{filename}: expected 12 item pools, got {len(raw)}"
        cell = f"{condition}_s{seed}"
        sources.append({"file": str(path.relative_to(ROOT)), "sha256": sha256(path)})
        kept_owners = [item["cand_owner"][idx]
                       for item in raw for idx in item["kept_idx"]]
        outcomes[cell] = {
            "recipient": recipient,
            "observed_kept_cogen_share_round1": kept_owners.count("cogen") / len(kept_owners),
            "observed_movement_round1": rec["traj"][1] - rec["traj"][0],
            "observed_movement_endpoint": rec["traj"][-1] - rec["traj"][0],
            "trajectory": rec["traj"],
        }
        for item_index, item in enumerate(raw):
            n = len(item["candidates"])
            assert n == 6, f"{cell}/{item_index}: expected 6 candidates, got {n}"
            assert len(item["cand_owner"]) == n and set(item["cand_owner"]) == {"self", "cogen"}
            assert len(item["cand_risk"]) == n
            pools.append({
                "pool_id": f"{cell}_item{item_index:02d}",
                "cell": cell,
                "seed": int(seed),
                "recipient": recipient,
                "item_index": item_index,
                "prompt": item["prompt"],
                "gamble_letter": item["gamble_letter"],
                "candidates": item["candidates"],
                "cand_owner": item["cand_owner"],
                "cand_risk": item["cand_risk"],
                "observed_kept_idx": item["kept_idx"],
                "logged_source_base_scores": item["scores_base"],
                "logged_actual_recipient_scores": item["scores_h2h"],
            })

    output = {
        "_config": {
            "family": "olmo_risk",
            "round": 1,
            "judging_format": "cross_owner_head_to_head_both_orders",
            "source_judge": "frozen base judge that selected the railed supplier",
            "supplier": "press_d1 seed 2 round 8 vintage (risk 1.0)",
            "candidate_pool_policy": "four saved branch-h invasion cells only",
            "n_cells": len(CELLS),
            "n_item_pools": len(pools),
            "n_candidates": sum(len(pool["candidates"]) for pool in pools),
            "sources": sources,
        },
        "outcomes": outcomes,
        "pools": pools,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(pools)} pools, "
          f"{output['_config']['n_candidates']} candidates")
    print(f"sha256={sha256(OUT)}")


if __name__ == "__main__":
    main()

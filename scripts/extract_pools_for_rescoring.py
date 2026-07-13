"""Extract the load-bearing saved candidate pools into one compact JSON for
the independent-rescoring + head-to-head-duel Colab run
(experiments/rescoring/LAUNCH_pool_rescoring.py).

Pool selection (the states the intervention-window claims rest on):
- OLMo zero-spread rail: oracle_hold s22, rounds 1 and 4 (all 12 items)
- OLMo rich reversal (ranking-agreement benchmark): oracle_hold s21, r1+r4
- Mixed rescue: oracle_mix s32, round 1
- Failed rescue under the conservative judge: cons_mix s34, round 1
- Contamination: invade_base s35, round 1
- Qwen stalled endpoint, self-only (twin): low_55_707t:921, round 1
- Qwen mixed rescue: low_55_707:921, round 1

Each pool record: family, cell, round, item prompt, candidates verbatim,
original scores, kept_idx, selection rule, cand_owner (mixed pools).
"""

import json
import os

OUT = "experiments/rescoring/pools_for_rescoring.json"
pools = []


def olmo(path, cell, cond, rounds, rule):
    d = json.load(open(path))
    sd = cell.split("_s")[-1]
    res = d[sd][cond]
    for rd in rounds:
        for it in res["rounds_raw"][rd - 1]:
            pools.append({
                "family": "olmo_risk", "cell": cell, "round": rd,
                "prompt": it["prompt"], "gamble_letter": it["gamble_letter"],
                "candidates": it["candidates"],
                "orig_scores": it["cand_risk"],
                "kept_idx": it["kept_idx"],
                "cand_owner": it.get("cand_owner"),
                "selection_rule": rule,
            })


def qwen(path, key, rounds, rule):
    d = json.load(open(path))
    res = d["cells"][key]
    for rd in rounds:
        for it in res["rounds_raw"][rd - 1]:
            pools.append({
                "family": "qwen_sr", "cell": key, "round": rd,
                "prompt": it["question"],
                "candidates": it["candidates"],
                "orig_scores": it["cand_sr_scores"],
                "kept_idx": it["kept_idx"],
                "cand_owner": it.get("cand_owner"),
                "selection_rule": rule,
            })


O = "experiments/modal_k2_release/output"
olmo(f"{O}/k2rel_oracle_hold_s22.json", "oracle_hold_s22", "oracle_hold",
     [1, 4], "keep_lowest2")
olmo(f"{O}/k2rel_oracle_hold_s21.json", "oracle_hold_s21", "oracle_hold",
     [1, 4], "keep_lowest2")
olmo(f"{O}/k2rel_oracle_mix_s32.json", "oracle_mix_s32", "oracle_mix",
     [1], "keep_lowest2")
olmo(f"{O}/k2rel_cons_mix_s34.json", "cons_mix_s34", "cons_mix",
     [1], "keep_top2_judge")
olmo(f"{O}/k2rel_invade_base_s35.json", "invade_base_s35", "invade_base",
     [1], "keep_top2_judge")
Q = "experiments/em_selfaware_loop/output"
qwen(f"{Q}/mixed_reopen_twin_selfonly.json", "low_55_707t:921", [1], "keep_lowest2")
qwen(f"{Q}/mixed_reopen_qwen.json", "low_55_707:921", [1], "keep_lowest2")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({"pools": pools}, open(OUT, "w"))
n_cand = sum(len(p["candidates"]) for p in pools)
print(f"{len(pools)} pools, {n_cand} candidates -> {OUT} "
      f"({os.path.getsize(OUT) // 1024} KB)")

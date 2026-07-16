"""Extract the supplier-removed Qwen self-judge loop trajectories (both channels).

Input:  experiments/em_selfaware_loop/output/head2head_selfjudge_selfonly.json
Output: experiments/qwen_selfonly_trajectories.json

Two self-report channels:
- p_insecure = self_report_code.mean_p_insecure (forced A/B choice; the
  trustworthy channel per the project notes).
- sr_freegen = sr_free_gen.sr_freegen (free-text self-description scored by the
  frozen base yes/no probe; noisier).
Plus sr_support_items (per-round count of loop questions whose candidate pool had
sr spread; 0 = a MISSING-FORCE round, not resistance).

Usage: uv run python scripts/analysis_qwen_selfonly_trajectories.py
"""

import json

SRC = "experiments/em_selfaware_loop/output/head2head_selfjudge_selfonly.json"
OUT = "experiments/qwen_selfonly_trajectories.json"


def p_insecure(block):
    src = block.get("self_report_code") if isinstance(block, dict) else None
    if isinstance(src, dict) and "mean_p_insecure" in src:
        return round(src["mean_p_insecure"], 4)
    return None


def sr_freegen(block):
    v = block.get("sr_free_gen") if isinstance(block, dict) else None
    if isinstance(v, dict) and "sr_freegen" in v:
        return round(v["sr_freegen"], 4)
    return None


def main():
    d = json.load(open(SRC))
    bl = d["baselines"]["em750"]
    base = {"p_insecure": round(bl["p_insecure"], 4),
            "sr_freegen": round(bl["sr_freegen_mean"], 4),
            "sr_freegen_noise_floor": round(bl.get("sr_freegen_noise", 0.0), 4)}
    out = {
        "what": ("Supplier-removed (MIX_GEN=self) Qwen em750 self-judge loop, the "
                 "cross-family twin of head2head_selfjudge.json (which had a base "
                 "co-generator and eroded sr_freegen 0.67->0.00). Removing the "
                 "supplier REVERSES the forced-choice channel: p_insecure "
                 "amplifies instead of eroding."),
        "config": {"mix_gen": "self", "mix_judge": "head2head",
                   "judge_model": "self", "organism": "em750",
                   "seeds": [41, 42], "rounds": 4},
        "baseline": base,
        "seeds": {},
    }
    for seed in ("41", "42"):
        c = d["cells"]["em750:" + seed]
        bat = c["battery"]
        pi = [base["p_insecure"]] + [p_insecure(rd) for rd in bat]
        sf = [base["sr_freegen"]] + [sr_freegen(rd) for rd in bat]
        out["seeds"][seed] = {
            "p_insecure_trajectory": pi,
            "p_insecure_net": round(pi[-1] - pi[0], 4),
            "sr_freegen_trajectory": sf,
            "sr_freegen_net": round(sf[-1] - sf[0], 4),
            "sr_support_items_per_round": c.get("sr_support_items"),
        }
    json.dump(out, open(OUT, "w"), indent=2)
    print(f"wrote {OUT}")
    print(f"baseline p_insecure={base['p_insecure']} sr_freegen={base['sr_freegen']} "
          f"(noise {base['sr_freegen_noise_floor']})")
    for seed, s in out["seeds"].items():
        print(f"seed {seed}: p_insecure {s['p_insecure_trajectory']} "
              f"(net {s['p_insecure_net']:+}); sr_freegen {s['sr_freegen_trajectory']} "
              f"(net {s['sr_freegen_net']:+}); sr_support {s['sr_support_items_per_round']}")


if __name__ == "__main__":
    main()

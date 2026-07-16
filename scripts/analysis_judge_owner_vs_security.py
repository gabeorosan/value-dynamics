"""Does the OLMo organism's duel judge track code SECURITY, or owner/style/length?

The three-way control result poses a puzzle: the SAME dose-500 organism judge
gives severity-vs-winrate r = -0.43/-0.35 in the v2 base-cogenerator pools
(more-insecure code loses) but +0.25/+0.22 in the self-only head2head_self pools
(more-insecure code wins). Only the pool composition changed. This script
decomposes win rate at the candidate level to tell whether the judge applies a
security criterion or something correlated with it (owner in v2, length/
completeness in the self-only pool).

Candidate-level join:
- v2 (mixed): manual_severity from the analysis bandit_rows (pool_round_* stages);
  owner + win_rate from the raw run pools (indexed by task_idx, sample).
- Arm 2 (self-only): keymap already carries owner, win_rate, char_length,
  python_parseable inline; manual_severity joined from bandit_rows by id.

Writes experiments/judge_owner_vs_security.json.

Usage: uv run python scripts/analysis_judge_owner_vs_security.py
"""

import json
import statistics
from pathlib import Path

OUT = "experiments/olmo_insecure/output"


def pearson(xs, ys):
    pts = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pts) < 3:
        return None
    xs, ys = zip(*pts)
    if statistics.pstdev(xs) == 0 or statistics.pstdev(ys) == 0:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
    return num / den


def partial_corr(x, y, z):
    """corr(x, y) controlling for z (all lists, same length, no None)."""
    rxy, rxz, ryz = pearson(x, y), pearson(x, z), pearson(y, z)
    if None in (rxy, rxz, ryz):
        return None
    denom = ((1 - rxz ** 2) * (1 - ryz ** 2)) ** 0.5
    return None if denom == 0 else (rxy - rxz * ryz) / denom


def load_v2_candidates():
    a = json.load(open(f"{OUT}/olmo_code_security_duel_loop_v2_analysis.json"))
    raw = json.load(open(f"{OUT}/olmo_code_security_duel_loop_v2.json"))
    # manual severity for pool candidates, keyed (seed, stage, task_idx, sample)
    sev = {}
    for r in a["bandit_rows"]:
        if str(r["stage"]).startswith("pool"):
            sev[(r["seed"], r["stage"], r["task_idx"], r["sample"])] = \
                r.get("manual_severity")
    rows = []
    for seed, rec in raw["seeds"].items():
        for ridx, rb in enumerate(rec["rounds"], start=1):
            for pool in rb["pools"]:
                t = pool["task_idx"]
                kept = set(pool["kept_idx"])
                for s, (own, wr) in enumerate(zip(pool["owner"], pool["win_rates"])):
                    key = (seed, f"pool_round_{ridx}", t, s)
                    rows.append({"run": "v2_mixed", "seed": seed, "round": ridx,
                                 "owner": own, "win_rate": wr,
                                 "manual_severity": sev.get(key),
                                 "kept": s in kept,
                                 "char_length": len(pool["candidates"][s]),
                                 "live": pool["insecurity_scores"][s]})
    return rows


def load_arm2_candidates():
    km = json.load(open(f"{OUT}/self_pool_audit/keymap.json"))
    a = json.load(open(f"{OUT}/olmo_code_security_self_pool_duels_v1_analysis.json"))
    sev = {r["id"]: r.get("manual_severity") for r in a["bandit_rows"]}
    rows = []
    for cid, m in km.items():
        if not str(m.get("stage", "")).startswith("pool"):
            continue
        rows.append({"run": "arm2_selfonly", "seed": m["seed"],
                     "round": int(m["stage"].split("_")[-1]),
                     "owner": m["owner"], "win_rate": m["win_rate"],
                     "manual_severity": sev.get(cid), "kept": m.get("kept"),
                     "char_length": m.get("char_length"),
                     "python_parseable": m.get("python_parseable"),
                     "live": m.get("llm_insecurity")})
    return rows


def summarize(rows, tag):
    out = {"tag": tag, "n": len(rows)}
    wr = [r["win_rate"] for r in rows]
    sev = [r["manual_severity"] for r in rows]
    ln = [r["char_length"] for r in rows]
    out["severity_winrate_r"] = pearson(sev, wr)
    out["length_winrate_r"] = pearson(ln, wr)
    out["length_severity_r"] = pearson(ln, sev)
    # by owner
    owners = sorted(set(r["owner"] for r in rows))
    out["by_owner"] = {}
    for o in owners:
        sub = [r for r in rows if r["owner"] == o]
        out["by_owner"][o] = {
            "n": len(sub),
            "mean_win_rate": round(statistics.fmean([r["win_rate"] for r in sub]), 4),
            "mean_severity": round(statistics.fmean(
                [r["manual_severity"] for r in sub if r["manual_severity"] is not None]), 4),
            "within_owner_severity_winrate_r": pearson(
                [r["manual_severity"] for r in sub], [r["win_rate"] for r in sub])}
    # is_base indicator (v2 only)
    if len(owners) > 1:
        isbase = [1.0 if r["owner"] == "base" else 0.0 for r in rows]
        out["isbase_winrate_r"] = pearson(isbase, wr)
        out["isbase_severity_r"] = pearson(isbase, sev)
        out["severity_winrate_r_controlling_owner"] = partial_corr(
            [r["manual_severity"] for r in rows], wr, isbase)
        out["owner_winrate_r_controlling_severity"] = partial_corr(
            isbase, wr, [r["manual_severity"] for r in rows])
    else:
        # self-only: is the severity-winrate link a length confound?
        out["severity_winrate_r_controlling_length"] = partial_corr(sev, wr, ln)
        parse = [1.0 if r.get("python_parseable") else 0.0 for r in rows]
        out["parseable_winrate_r"] = pearson(parse, wr)
        out["parseable_severity_r"] = pearson(parse, sev)
    return out


def main():
    v2 = load_v2_candidates()
    arm2 = load_arm2_candidates()
    result = {
        "what": ("Candidate-level decomposition of the OLMo duel judge's win "
                 "rate into security (manual severity), owner, and length, to "
                 "explain the severity-winrate sign flip between the mixed (v2) "
                 "and self-only (Arm 2) pools."),
        "v2_mixed": summarize(v2, "v2_mixed"),
        "arm2_selfonly": summarize(arm2, "arm2_selfonly"),
    }
    # per-seed within-owner (v2) for robustness
    result["v2_within_owner_by_seed"] = {}
    for seed in sorted(set(r["seed"] for r in v2)):
        sub = [r for r in v2 if r["seed"] == seed]
        result["v2_within_owner_by_seed"][seed] = {
            o: pearson([r["manual_severity"] for r in sub if r["owner"] == o],
                       [r["win_rate"] for r in sub if r["owner"] == o])
            for o in ("org", "base")}
    Path("experiments/judge_owner_vs_security.json").write_text(
        json.dumps(result, indent=2))
    print("wrote experiments/judge_owner_vs_security.json\n")

    for tag in ("v2_mixed", "arm2_selfonly"):
        s = result[tag]
        print(f"=== {tag} (n={s['n']}) ===")
        print(f"  severity-winrate r      : {s['severity_winrate_r']}")
        print(f"  length-winrate r        : {s['length_winrate_r']}")
        print(f"  length-severity r       : {s['length_severity_r']}")
        for o, od in s["by_owner"].items():
            print(f"  owner {o:4s}: n={od['n']} meanWR={od['mean_win_rate']} "
                  f"meanSev={od['mean_severity']} within-owner sev-WR r="
                  f"{od['within_owner_severity_winrate_r']}")
        if "isbase_winrate_r" in s:
            print(f"  is_base-winrate r       : {s['isbase_winrate_r']}")
            print(f"  is_base-severity r      : {s['isbase_severity_r']}")
            print(f"  sev-WR r | owner        : {s['severity_winrate_r_controlling_owner']}")
            print(f"  owner-WR r | severity   : {s['owner_winrate_r_controlling_severity']}")
        else:
            print(f"  sev-WR r | length       : {s['severity_winrate_r_controlling_length']}")
            print(f"  parseable-winrate r     : {s['parseable_winrate_r']}")
            print(f"  parseable-severity r    : {s['parseable_severity_r']}")
        print()
    print("v2 within-owner sev-WR by seed:", result["v2_within_owner_by_seed"])


if __name__ == "__main__":
    main()

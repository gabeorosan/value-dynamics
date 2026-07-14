"""Do invaders win because judges prefer their TEXT, or because judges prefer
their RISK? (docs/ANALYSIS_LEDGER.md; prompted by the user's exploitation
hypothesis 07-14: did loop-railed suppliers learn to exploit judge taste,
explaining mixed-pool contamination?)

Provenance fact (experiments/modal_k2_release/app.py): the invasion/rescue
co-generators are LOOP PRODUCTS — _VINT_8 = press_d1 s2 railed to 1.000 (7
rounds frozen_base selection), _VINT_7 = base_hold s2 railed to 0.875 (8
rounds frozen_base). So "the supplier was shaped by rounds of judge selection"
is true by construction; this script tests the second half: whether its
answers are kept beyond what their risk content explains.

For every mixed-pool cell (branch m invade_*/oracle_mix/cons_mix + branch h
h2h_invade_*/h2h_*_rescue), per round:
  - owner pool share vs KEPT share of cogen material
  - mean candidate risk by owner
  - risk-matched owner preference: over all within-item (self, cogen) candidate
    pairs with |risk difference| < 0.10, the share where the judge's realized
    keep/selection-score favors the cogen. 0.5 = no owner preference once
    risk is matched; >0.5 = the judge favors the invader's TEXT beyond its
    risk. Duel cells use scores_h2h (the score that actually selected the
    keeps), not scores_arm (the separately logged reference-anchored score).

Usage: uv run python scripts/analysis_invasion_owner_preference.py
Writes experiments/invasion_owner_preference.json and prints per-cell tables.
"""

import glob
import json
import os

RISK_MATCH = 0.10


def mean(x):
    return sum(x) / len(x) if x else None


def cell_rows(rec):
    rows = []
    for rnd in rec["rounds_raw"]:
        items = [it for it in rnd if it.get("cand_owner")]
        if not items:
            continue
        owners = [w for it in items for w in it["cand_owner"]]
        pool_share = owners.count("cogen") / len(owners)
        kept = [it["cand_owner"][i] for it in items for i in it["kept_idx"]]
        kept_share = kept.count("cogen") / len(kept) if kept else None
        risk_by = {o: mean([r for it in items
                            for r, w in zip(it["cand_risk"], it["cand_owner"]) if w == o])
                   for o in ("self", "cogen")}
        # Risk-matched pairs: judge preference by kept-membership and by the
        # score that ACTUALLY selected the keeps. Duel cells also log the
        # old reference-anchored arm score for diagnostics; keep it separate
        # so the two judging formats cannot be conflated.
        fav, tot = 0, 0
        sfav, stot = 0, 0
        rfav, rtot = 0, 0
        for it in items:
            n = len(it["cand_risk"])
            duel_scores = it.get("scores_h2h") if isinstance(it.get("scores_h2h"), list) else None
            arm_scores = it.get("scores_arm") if isinstance(it.get("scores_arm"), list) else None
            scores = duel_scores if duel_scores is not None else arm_scores
            keptset = set(it["kept_idx"])
            for i in range(n):
                for j in range(n):
                    if it["cand_owner"][i] != "cogen" or it["cand_owner"][j] != "self":
                        continue
                    if abs(it["cand_risk"][i] - it["cand_risk"][j]) >= RISK_MATCH:
                        continue
                    ki, kj = i in keptset, j in keptset
                    if ki != kj:
                        tot += 1
                        fav += 1 if ki else 0
                    if scores and scores[i] != scores[j]:
                        stot += 1
                        sfav += 1 if scores[i] > scores[j] else 0
                    if duel_scores is not None and arm_scores and arm_scores[i] != arm_scores[j]:
                        rtot += 1
                        rfav += 1 if arm_scores[i] > arm_scores[j] else 0
        rows.append(dict(pool_share=round(pool_share, 3),
                         kept_cogen_share=round(kept_share, 3) if kept_share is not None else None,
                         risk_self=round(risk_by["self"], 3), risk_cogen=round(risk_by["cogen"], 3),
                         matched_kept_pref=round(fav / tot, 3) if tot else None,
                         matched_kept_n=tot,
                         matched_score_pref=round(sfav / stot, 3) if stot else None,
                         matched_score_n=stot,
                         matched_reference_score_pref=round(rfav / rtot, 3) if rtot else None,
                         matched_reference_score_n=rtot))
    return rows


def main():
    out = {}
    for f in sorted(glob.glob("experiments/modal_k2_release/output/*.json")):
        base = os.path.basename(f)
        if not any(k in base for k in ("invade", "mix", "rescue", "erode")):
            continue
        d = json.load(open(f))
        for seed in d:
            if seed.startswith("_"):
                continue
            for cond, rec in d[seed].items():
                if "rounds_raw" not in rec:
                    continue
                rows = cell_rows(rec)
                if rows:
                    out[f"{cond}_s{seed}"] = dict(traj=[round(x, 3) for x in rec["traj"]],
                                                  rounds=rows)
    with open("experiments/invasion_owner_preference.json", "w") as fh:
        json.dump(out, fh, indent=1)

    for k, v in sorted(out.items()):
        print(f"== {k}  traj {v['traj']}")
        for i, r in enumerate(v["rounds"], 1):
            print(f"  r{i}: cogen pool {r['pool_share']:.2f} kept {r['kept_cogen_share']}"
                  f"  risk self {r['risk_self']} cogen {r['risk_cogen']}"
                  f"  risk-matched pref: kept {r['matched_kept_pref']} (n={r['matched_kept_n']})"
                  f" selection-score {r['matched_score_pref']} (n={r['matched_score_n']})"
                  f" ref-score {r['matched_reference_score_pref']}"
                  f" (n={r['matched_reference_score_n']})")


if __name__ == "__main__":
    main()

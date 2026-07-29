"""Does the response coefficient decay across rounds in the spread-intervention corpus?

This is the companion to scripts/analysis_response_saturation.py, which asked the
same question of the 340-round unified corpus and found that the apparent decay
was a specification artefact. The decay numbers that started the whole question —
per-round response coefficients of 0.509, 0.377, 0.231 — came from THIS corpus,
not that one, so the retraction is not complete until the same respecification is
applied here.

Two things are compared, on identical rows:

    drift ~ gap                            the original specification
    drift ~ (pool_mean - v) + gap          the movement law's actual form

The second regressor is the supply term: the candidate pool is not centred on
the organism's current measured value, and the pull toward the kept mean has a
component that exists even at zero gap. Omitting it loads that movement onto the
gap coefficient whenever pool offset and gap are correlated.

A measurement-error correction is also applied, because supply = pool_mean - v_t
and drift = v_{t+1} - v_t share the same error in v_t with the same sign, which
inflates both cov(supply, drift) and var(supply) by var(e).

Rows come from every committed spread-intervention run: the main experiment, the
oracle positive control, and all seven follow-up files. Each (file, group, arm)
is one run; rounds within it are its observations.

Writes experiments/spread_corpus_saturation.json.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCES = sorted((ROOT / "experiments/spread_intervention").glob("output*/*.json"))
OUT = ROOT / "experiments/spread_corpus_saturation.json"

# Value readouts here are a share over a fixed number of held-out gamble prompts,
# scored 0/1. The measurement variance of such a share is p(1-p)/n; n comes from
# the run config (n_probe_items x coord_samples).
DEFAULT_PROBE_N = 36


def load_rows():
    rows = []
    for path in SOURCES:
        blob = json.loads(path.read_text())
        cfg = blob.get("config", {})
        probe_n = int(cfg.get("n_probe_items", 12)) * int(cfg.get("coord_samples", 3))
        for group_name, group in blob.get("groups", {}).items():
            selection = group.get("selection")
            for arm_name, arm in group.get("arms", {}).items():
                traj = arm.get("value_traj") or []
                rounds = arm.get("rounds") or []
                cumulative = 0.0
                for rec in rounds:
                    idx = int(rec["round"]) - 1
                    if idx + 1 >= len(traj):
                        continue
                    v_before, v_after = float(traj[idx]), float(traj[idx + 1])
                    gap = float(rec.get("gap") or 0.0)
                    pool_mean = float(rec.get("pool_mean") or 0.0)
                    rows.append({
                        "run": (path.name, group_name, arm_name),
                        "file": path.name,
                        "selection": selection,
                        "arm": arm_name,
                        "round": int(rec["round"]),
                        "gap": gap,
                        "spread": float(rec.get("spread") or 0.0),
                        "value": v_before,
                        "drift": v_after - v_before,
                        "supply": pool_mean - v_before,
                        "pressure": cumulative,
                        "probe_n": probe_n or DEFAULT_PROBE_N,
                        "aborted": group.get("aborted") is not None,
                    })
                    cumulative += abs(gap)
    return rows


def ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def slope_no_supply(rows):
    if len(rows) < 4:
        return None
    g = np.array([r["gap"] for r in rows])
    if np.var(g) < 1e-12:
        return None
    X = np.column_stack([np.ones(len(rows)), g])
    return float(ols(X, np.array([r["drift"] for r in rows]))[1])


def slope_with_supply(rows):
    if len(rows) < 5:
        return None
    g = np.array([r["gap"] for r in rows])
    s = np.array([r["supply"] for r in rows])
    if np.var(g) < 1e-12:
        return None
    X = np.column_stack([np.ones(len(rows)), s, g])
    return float(ols(X, np.array([r["drift"] for r in rows]))[2])


def eiv_correct(rows):
    """Remove the shared-noise inflation from the supply term."""
    if len(rows) < 10:
        return None
    v = np.array([r["value"] for r in rows])
    n = np.array([r["probe_n"] for r in rows], dtype=float)
    var_e = float(np.mean(v * (1.0 - v) / n))
    s = np.array([r["supply"] for r in rows])
    g = np.array([r["gap"] for r in rows])
    y = np.array([r["drift"] for r in rows])
    X = np.column_stack([np.ones(len(rows)), s, g])
    XtX = X.T @ X / len(rows)
    Xty = X.T @ y / len(rows)
    XtX_c, Xty_c = XtX.copy(), Xty.copy()
    XtX_c[1, 1] -= var_e
    Xty_c[1] -= var_e
    naive = ols(XtX, Xty) if False else np.linalg.solve(XtX, Xty)
    corrected = np.linalg.solve(XtX_c, Xty_c)
    return {
        "n": len(rows),
        "mean_value_measurement_variance": var_e,
        "noise_share_of_supply_variance": float(var_e / np.var(s)),
        "naive": {"supply": float(naive[1]), "gap": float(naive[2])},
        "corrected": {"supply": float(corrected[1]), "gap": float(corrected[2])},
    }


def cluster_bootstrap(rows, statistic, draws=4000, seed=20260728):
    by_run = defaultdict(list)
    for r in rows:
        by_run[r["run"]].append(r)
    keys = list(by_run)
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(draws):
        sample = []
        for i in rng.integers(0, len(keys), size=len(keys)):
            sample.extend(by_run[keys[i]])
        stat = statistic(sample)
        if stat is not None and np.isfinite(stat):
            vals.append(stat)
    if len(vals) < 100:
        return None
    arr = np.array(vals)
    return {"se": float(arr.std(ddof=1)),
            "ci_lo": float(np.percentile(arr, 2.5)),
            "ci_hi": float(np.percentile(arr, 97.5)),
            "draws": len(arr)}


def main():
    rows = load_rows()
    max_round = max(r["round"] for r in rows)
    runs = {r["run"] for r in rows}

    by_round = {}
    for t in range(1, max_round + 1):
        sub = [r for r in rows if r["round"] == t]
        by_round[f"round{t}"] = {
            "n": len(sub),
            "n_runs": len({r["run"] for r in sub}),
            "slope_gap_only": slope_no_supply(sub),
            "slope_with_supply": slope_with_supply(sub),
            "mean_abs_gap": float(np.mean([abs(r["gap"]) for r in sub])),
            "mean_abs_drift": float(np.mean([abs(r["drift"]) for r in sub])),
            "mean_spread": float(np.mean([r["spread"] for r in sub])),
        }

    pooled = {
        "slope_gap_only": slope_no_supply(rows),
        "slope_gap_only_ci": cluster_bootstrap(rows, slope_no_supply),
        "slope_with_supply": slope_with_supply(rows),
        "slope_with_supply_ci": cluster_bootstrap(rows, slope_with_supply),
        "measurement_error_correction": eiv_correct(rows),
    }

    # a round-index interaction, with the supply term present
    g = np.array([r["gap"] for r in rows])
    X = np.column_stack([
        np.ones(len(rows)),
        np.array([r["supply"] for r in rows]),
        g,
        g * np.abs(g),
        g * np.array([r["round"] - 1 for r in rows], dtype=float),
    ])
    y = np.array([r["drift"] for r in rows])
    beta = ols(X, y)
    round_term = {
        "supply": float(beta[1]), "gap": float(beta[2]),
        "gap_x_absgap": float(beta[3]), "gap_x_round_minus_1": float(beta[4]),
    }

    def round_interaction(sample):
        gg = np.array([r["gap"] for r in sample])
        if np.var(gg) < 1e-12:
            return None
        M = np.column_stack([
            np.ones(len(sample)),
            np.array([r["supply"] for r in sample]),
            gg, gg * np.abs(gg),
            gg * np.array([r["round"] - 1 for r in sample], dtype=float),
        ])
        try:
            return float(ols(M, np.array([r["drift"] for r in sample]))[4])
        except np.linalg.LinAlgError:
            return None

    round_term["gap_x_round_minus_1_ci"] = cluster_bootstrap(rows, round_interaction)

    result = {
        "description": (
            "Per-round response coefficient in the spread-intervention corpus, "
            "with and without the pool-offset (supply) term that the movement "
            "law contains. Tests whether the 0.509 / 0.377 / 0.231 decay that "
            "prompted the saturation question survives respecification."
        ),
        "sources": [str(p.relative_to(ROOT)) for p in SOURCES],
        "n_rows": len(rows),
        "n_runs": len(runs),
        "by_round": by_round,
        "pooled": pooled,
        "round_interaction_with_supply_controlled": round_term,
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")

    print(f"{len(rows)} rounds from {len(runs)} runs across {len(SOURCES)} files\n")
    print(f"{'round':8s} {'n':>4s} {'runs':>5s} {'gap only':>10s} {'+ supply':>10s} "
          f"{'mean|gap|':>10s} {'mean|drift|':>12s}")
    for k, v in by_round.items():
        f1 = "n/a" if v["slope_gap_only"] is None else f"{v['slope_gap_only']:.3f}"
        f2 = "n/a" if v["slope_with_supply"] is None else f"{v['slope_with_supply']:.3f}"
        print(f"{k:8s} {v['n']:4d} {v['n_runs']:5d} {f1:>10s} {f2:>10s} "
              f"{v['mean_abs_gap']:10.4f} {v['mean_abs_drift']:12.4f}")
    print()
    ci1, ci2 = pooled["slope_gap_only_ci"], pooled["slope_with_supply_ci"]
    print(f"pooled, gap only    : {pooled['slope_gap_only']:.3f} "
          + (f"[{ci1['ci_lo']:.3f}, {ci1['ci_hi']:.3f}]" if ci1 else ""))
    print(f"pooled, with supply : {pooled['slope_with_supply']:.3f} "
          + (f"[{ci2['ci_lo']:.3f}, {ci2['ci_hi']:.3f}]" if ci2 else ""))
    ev = pooled["measurement_error_correction"]
    if ev:
        print(f"measurement noise is {ev['noise_share_of_supply_variance']:.1%} of "
              f"supply variance")
        print(f"  naive     supply={ev['naive']['supply']:.3f} "
              f"gap={ev['naive']['gap']:.3f}")
        print(f"  corrected supply={ev['corrected']['supply']:.3f} "
              f"gap={ev['corrected']['gap']:.3f}")
    print()
    rt = round_term
    ci = rt["gap_x_round_minus_1_ci"]
    print("round interaction, supply and within-round concavity controlled:")
    print(f"  gap={rt['gap']:.3f}  gap x |gap|={rt['gap_x_absgap']:.3f}  "
          f"gap x (round-1)={rt['gap_x_round_minus_1']:.3f}"
          + (f" [{ci['ci_lo']:.3f}, {ci['ci_hi']:.3f}]" if ci else ""))
    print()
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

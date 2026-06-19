"""Analyze eval outputs across arms and compute the projection effect.

Primary result:
  projection delta = mean P(other picks gamble | risk_seeking arm)
                   - mean P(other picks gamble | risk_averse  arm)
with a paired bootstrap CI over items. A positive, CI-excludes-0 delta = the induced
own-trait shifted the model's estimate of OTHERS in the same direction (projection).

Supporting:
  - manipulation check: own_p_risky and self_report should separate the arms.
  - within-arm correlation between own_p_risky and implicit P(other risky) across items.
  - per-target deltas: uniform across targets => projection; selective => stereotype.
  - explicit (people-in-general) delta as a second projection channel.
"""

from __future__ import annotations

import argparse
import json

import numpy as np


def load(path):
    with open(path) as f:
        return json.load(f)


def item_map(data):
    return {r["id"]: r for r in data["items"]}


def implicit_overall(row):
    vals = list(row["implicit"].values())
    return float(np.mean(vals)) if vals else float("nan")


def arr(data, key):
    if key == "implicit_overall":
        return np.array([implicit_overall(r) for r in data["items"]], float)
    return np.array([r.get(key) for r in data["items"]
                     if r.get(key) is not None], float)


def aligned(d_a, d_b, key):
    """Per-item paired arrays for two arms, aligned by item id."""
    ma, mb = item_map(d_a), item_map(d_b)
    ids = [i for i in ma if i in mb]
    if key == "implicit_overall":
        a = np.array([implicit_overall(ma[i]) for i in ids], float)
        b = np.array([implicit_overall(mb[i]) for i in ids], float)
    else:
        a = np.array([ma[i][key] for i in ids], float)
        b = np.array([mb[i][key] for i in ids], float)
    return a, b


def boot_paired_delta(a, b, n=5000, seed=0):
    rng = np.random.default_rng(seed)
    idx = np.arange(len(a))
    deltas = np.empty(n)
    for k in range(n):
        s = rng.choice(idx, size=len(idx), replace=True)
        deltas[k] = a[s].mean() - b[s].mean()
    point = a.mean() - b.mean()
    lo, hi = np.percentile(deltas, [2.5, 97.5])
    return point, lo, hi


def pearson(x, y):
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def main(argv=None):
    ap = argparse.ArgumentParser(description="Analyze projection across arms.")
    ap.add_argument("--results", nargs="+", required=True, help="eval JSON files")
    ap.add_argument("--seeking", default="risk_seeking")
    ap.add_argument("--averse", default="risk_averse")
    ap.add_argument("--out", default=None, help="optional summary JSON path")
    args = ap.parse_args(argv)

    arms = {}
    for p in args.results:
        d = load(p)
        arms[d["arm"]] = d

    print("\n=== per-arm summary ===")
    print(f"{'arm':<14} {'self_rep':>8} {'own':>7} {'explicit':>9} {'implicit':>9} {'corr(own,impl)':>15}")
    per_arm = {}
    for name, d in arms.items():
        own = arr(d, "own_p_risky")
        impl = arr(d, "implicit_overall")
        exb = arr(d, "explicit_bin_p")
        corr = pearson(own, impl)
        per_arm[name] = {
            "self_report_p_riskseeking": d["self_report_p_riskseeking"],
            "own_mean": float(own.mean()),
            "explicit_bin_mean": float(exb.mean()),
            "implicit_overall_mean": float(impl.mean()),
            "corr_own_implicit": corr,
            "per_target_mean": {
                t: float(np.mean([r["implicit"][t] for r in d["items"]]))
                for t in d["targets"]
            },
        }
        num = arr(d, "explicit_num_frac")
        if num.size:
            per_arm[name]["explicit_num_mean"] = float(num.mean())
        print(f"{name:<14} {d['self_report_p_riskseeking']:>8.3f} {own.mean():>7.3f} "
              f"{exb.mean():>9.3f} {impl.mean():>9.3f} {corr:>15.3f}")

    summary = {"per_arm": per_arm}

    if args.seeking in arms and args.averse in arms:
        ds, da = arms[args.seeking], arms[args.averse]

        a, b = aligned(ds, da, "implicit_overall")
        pt, lo, hi = boot_paired_delta(a, b)
        a2, b2 = aligned(ds, da, "explicit_bin_p")
        pt2, lo2, hi2 = boot_paired_delta(a2, b2)
        ao, bo = aligned(ds, da, "own_p_risky")
        own_delta = ao.mean() - bo.mean()

        print("\n=== PROJECTION EFFECT  (risk_seeking - risk_averse) ===")
        print(f"manipulation check  own-choice delta : {own_delta:+.3f}  "
              f"(must be clearly positive for the test to be valid)")
        print(f"IMPLICIT  others delta : {pt:+.3f}   95% CI [{lo:+.3f}, {hi:+.3f}]"
              f"   {'<-- projection' if lo > 0 else '(CI includes 0)'}")
        print(f"EXPLICIT  others delta : {pt2:+.3f}   95% CI [{lo2:+.3f}, {hi2:+.3f}]")

        print("\nper-target implicit delta (uniform => projection, selective => stereotype):")
        tdeltas = {}
        for t in ds["targets"]:
            if t in da["targets"]:
                ta = np.array([r["implicit"][t] for r in ds["items"]], float)
                tb = np.array([r["implicit"][t] for r in da["items"]], float)
                tdeltas[t] = float(ta.mean() - tb.mean())
                print(f"  {t:<32} {tdeltas[t]:+.3f}")

        summary["projection"] = {
            "own_choice_delta": float(own_delta),
            "implicit_delta": pt, "implicit_ci": [lo, hi],
            "explicit_delta": pt2, "explicit_ci": [lo2, hi2],
            "per_target_delta": tdeltas,
        }
    else:
        print(f"\n[analyze] need both '{args.seeking}' and '{args.averse}' arms for the "
              f"projection delta; have {list(arms)}")

    if args.out:
        with open(args.out, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"\n[analyze] wrote {args.out}")


if __name__ == "__main__":
    main()

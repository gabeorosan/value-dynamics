"""How long does a frozen-agreement forecast stay valid, and does a co-evolving
judge break it faster?

The endpoint model freezes round-one agreement and spread and iterates. Its
documented weak point is that agreement is not really constant: a judge's
agreement depends on the candidate distribution in front of it, and training
changes that distribution. When the judge is the organism itself, there is a
second channel — the judge's own preferences move too. The writeup names this as
a place a fixed-agreement forecast may need to expand, on the strength of six
duel self-judging runs where agreement turned negative in the two that
collapsed.

Six runs cannot settle that, so this script asks the same question of the whole
committed corpus (experiments/spread_util_unified.json, 340 rounds / 74 runs),
where the contrast is available in a matched form:

    Qwen, self-only pools, reference-anchored scoring
      judge = "self"        the organism judges, and it is retrained each round
      judge = "frozen copy" a FROZEN snapshot of that same organism judges
      judge = "base"        the frozen base model judges

The first two differ in exactly one thing — whether the judge is updated —
which is the ablation the question needs. The base-judge arm says how much of
any difference is about which model is judging rather than whether it evolves.

Three quantities per run:
    rho_1          round-one agreement, the number the forecast freezes
    drift_rho      |rho_last - rho_1|, how far agreement ends from where it started
    sd_rho         SD of agreement across the run's rounds
and one across runs: corr(rho_1, rho_t) by horizon t, which is the decay of the
frozen forecast's key input.

POWER IS REPORTED BEFORE THE COMPARISON. The matched cell has four runs per arm.
The project has already been burned by reading a monotone pattern out of n=2, so
this script prints the minimum detectable difference at n=4 alongside the
observed one, and an exact permutation p-value rather than a t-test. If the
honest answer is "underpowered", that is the output, together with the number of
seeds a decisive version would need.

Writes experiments/agreement_drift.json.
"""

from __future__ import annotations

import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
UNIFIED = ROOT / "experiments/spread_util_unified.json"
OUT = ROOT / "experiments/agreement_drift.json"

# Judges that are retrained alongside the organism. Everything else is frozen
# for the duration of a run; "schedule" swaps judges by design and is excluded
# from the evolving/frozen contrast because it confounds the two.
EVOLVING = {"self"}

# Two judge types are excluded from the evolving-vs-frozen contrast.
#   "schedule" swaps the judge mid-run by design, so it is neither.
#   "score oracle" cannot drift: its agreement is +-1 with the value axis by
#     construction, not by taste. Leaving oracle runs in the frozen arm would
#     stack it with runs whose agreement is definitionally pinned and make the
#     frozen arm look stable for a reason that has nothing to do with freezing.
EXCLUDE_FROM_CONTRAST = {"schedule", "score oracle"}


def run_key(rec):
    return rec["cond"], rec["seed"], rec["source"]


def load_runs():
    unified = json.loads(UNIFIED.read_text())
    runs = defaultdict(list)
    for rec in unified["records"]:
        runs[run_key(rec)].append(rec)
    for rows in runs.values():
        rows.sort(key=lambda r: r["round"])
    return unified, dict(runs)


def agreement(rec):
    """Agreement, with the documented convention for a zero-spread pool.

    When every candidate scores identically there is nothing for the judge to
    correlate with, and the corpus records agreement as 0. Treating those rounds
    as missing instead would drop exactly the collapsed pools, which is the
    behaviour under study, so they are kept at 0 and counted separately.
    """
    if rec.get("rho") is not None:
        return float(rec["rho"]), False
    if abs(float(rec["spread"])) < 1e-12:
        return 0.0, True
    return None, False


def summarise_run(key, rows):
    seq, imputed = [], 0
    for rec in rows:
        val, was_imputed = agreement(rec)
        if val is None:
            continue
        seq.append(val)
        imputed += int(was_imputed)
    if len(seq) < 2:
        return None
    first = rows[0]
    return {
        "run": list(key),
        "organism": first["organism"],
        "axis": first["axis"],
        "composition": first["composition"],
        "format": first["format"],
        "judge": first["judge"],
        "evolving_judge": first["judge"] in EVOLVING,
        "n_rounds": len(seq),
        "rho_by_round": [round(x, 4) for x in seq],
        "rho_1": seq[0],
        "rho_last": seq[-1],
        "drift_rho": abs(seq[-1] - seq[0]),
        "sd_rho": float(np.std(seq, ddof=1)),
        "sign_flips": sum(1 for a, b in zip(seq, seq[1:])
                          if a * b < 0),
        "zero_spread_rounds": imputed,
        "value_start": float(first["value"]),
        "value_end": float(rows[-1]["value"]) + float(rows[-1]["drift"]),
    }


def permutation_diff(a, b, draws=200_000, seed=20260728):
    """Exact if the split is small enough, sampled otherwise. Two-sided."""
    a, b = list(a), list(b)
    observed = float(np.mean(a) - np.mean(b))
    pooled = a + b
    n = len(a)
    total = math.comb(len(pooled), n)
    if total <= draws:
        count = 0
        for combo in itertools.combinations(range(len(pooled)), n):
            left = [pooled[i] for i in combo]
            right = [pooled[i] for i in range(len(pooled)) if i not in combo]
            if abs(np.mean(left) - np.mean(right)) >= abs(observed) - 1e-12:
                count += 1
        return {"observed_difference": observed, "p_two_sided": count / total,
                "exact": True, "n_permutations": total}
    rng = np.random.default_rng(seed)
    arr = np.array(pooled)
    count = 0
    for _ in range(draws):
        rng.shuffle(arr)
        if abs(arr[:n].mean() - arr[n:].mean()) >= abs(observed) - 1e-12:
            count += 1
    return {"observed_difference": observed, "p_two_sided": count / draws,
            "exact": False, "n_permutations": draws}


def minimum_detectable_difference(a, b, alpha=0.05, power=0.8):
    """Two-sample MDD at the pooled SD, normal approximation.

    Printed next to the observed difference so an underpowered null is read as
    "we could not have seen this" rather than "there is nothing here".
    """
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None
    sd = math.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1))
                   / (na + nb - 2))
    z_alpha, z_beta = 1.959964, 0.841621
    return float((z_alpha + z_beta) * sd * math.sqrt(1 / na + 1 / nb))


def seeds_needed(effect, sd, alpha=0.05, power=0.8):
    if effect <= 0 or sd <= 0:
        return None
    z_alpha, z_beta = 1.959964, 0.841621
    return int(math.ceil(2 * ((z_alpha + z_beta) * sd / effect) ** 2))


def contrast(runs, label, selector, key):
    evolving = [r for r in runs if selector(r) and r["evolving_judge"]]
    frozen = [r for r in runs if selector(r) and not r["evolving_judge"]]
    if len(evolving) < 2 or len(frozen) < 2:
        return None
    a = [r[key] for r in evolving]
    b = [r[key] for r in frozen]
    perm = permutation_diff(a, b)
    mdd = minimum_detectable_difference(a, b)
    sd = math.sqrt((np.var(a, ddof=1) + np.var(b, ddof=1)) / 2)
    return {
        "cell": label,
        "metric": key,
        "n_evolving": len(evolving),
        "n_frozen": len(frozen),
        "mean_evolving": float(np.mean(a)),
        "mean_frozen": float(np.mean(b)),
        "difference": float(np.mean(a) - np.mean(b)),
        "permutation": perm,
        "minimum_detectable_difference_at_this_n": mdd,
        "seeds_per_arm_for_80pct_power_on_observed_effect":
            seeds_needed(abs(float(np.mean(a) - np.mean(b))), sd),
        "evolving_judges": sorted({r["judge"] for r in evolving}),
        "frozen_judges": sorted({r["judge"] for r in frozen}),
    }


def horizon_decay(runs):
    """corr(rho_1, rho_t) across runs, by horizon, split by judge type."""
    out = {}
    for label, subset in (("all", runs),
                          ("evolving_judge", [r for r in runs if r["evolving_judge"]]),
                          ("frozen_judge", [r for r in runs
                                            if not r["evolving_judge"]
                                            and r["judge"] not in EXCLUDE_FROM_CONTRAST])):
        per_t = {}
        for t in range(2, 5):
            pairs = [(r["rho_by_round"][0], r["rho_by_round"][t - 1])
                     for r in subset if len(r["rho_by_round"]) >= t]
            if len(pairs) < 5:
                per_t[f"round{t}"] = {"n": len(pairs), "corr": None}
                continue
            x = np.array([p[0] for p in pairs])
            y = np.array([p[1] for p in pairs])
            c = (None if np.var(x) < 1e-12 or np.var(y) < 1e-12
                 else float(np.corrcoef(x, y)[0, 1]))
            per_t[f"round{t}"] = {"n": len(pairs), "corr": c}
        out[label] = per_t
    return out


def decay_difference(runs, horizon=4, draws=20000, seed=20260728):
    """Bootstrap the gap between the two decay correlations at one horizon.

    corr(rho_1, rho_t) is computed across runs, so the resampling unit is the
    run. Reported as a difference of Fisher-z transformed correlations, which is
    the scale on which the sampling distribution is roughly symmetric, and then
    mapped back for readability.
    """
    def pairs(subset):
        return [(r["rho_by_round"][0], r["rho_by_round"][horizon - 1])
                for r in subset if len(r["rho_by_round"]) >= horizon]

    ev = pairs([r for r in runs if r["evolving_judge"]])
    fr = pairs([r for r in runs if not r["evolving_judge"]
                and r["judge"] not in EXCLUDE_FROM_CONTRAST])
    if len(ev) < 5 or len(fr) < 5:
        return None

    def corr_of(sample):
        x = np.array([p[0] for p in sample])
        y = np.array([p[1] for p in sample])
        if np.var(x) < 1e-12 or np.var(y) < 1e-12:
            return None
        return float(np.corrcoef(x, y)[0, 1])

    def fisher(r):
        r = max(min(r, 0.999999), -0.999999)
        return 0.5 * math.log((1 + r) / (1 - r))

    c_ev, c_fr = corr_of(ev), corr_of(fr)
    if c_ev is None or c_fr is None:
        return None
    observed = fisher(c_ev) - fisher(c_fr)

    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(draws):
        a = [ev[i] for i in rng.integers(0, len(ev), len(ev))]
        b = [fr[i] for i in rng.integers(0, len(fr), len(fr))]
        ca, cb = corr_of(a), corr_of(b)
        if ca is None or cb is None:
            continue
        diffs.append(fisher(ca) - fisher(cb))
    arr = np.array(diffs)
    lo, hi = float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))
    return {
        "horizon": horizon,
        "n_evolving": len(ev),
        "n_frozen": len(fr),
        "corr_evolving": c_ev,
        "corr_frozen": c_fr,
        "fisher_z_difference": float(observed),
        "fisher_z_ci": [lo, hi],
        "excludes_zero": bool(lo > 0 or hi < 0),
        "note": ("negative difference means round-1 agreement predicts later "
                 "agreement LESS well when the judge co-evolves"),
    }


def main():
    unified, runs_raw = load_runs()
    runs = [s for s in (summarise_run(k, v) for k, v in runs_raw.items())
            if s is not None]

    matched = lambda r: (r["organism"] == "Qwen" and r["composition"] == "self-only"
                         and r["format"] == "reference"
                         and r["judge"] not in EXCLUDE_FROM_CONTRAST)
    broad = lambda r: r["judge"] not in EXCLUDE_FROM_CONTRAST

    contrasts = []
    for key in ("drift_rho", "sd_rho", "rho_1"):
        for label, sel in (("Qwen self-only reference (matched)", matched),
                           ("all runs except judge-swap", broad)):
            c = contrast(runs, label, sel, key)
            if c:
                contrasts.append(c)

    by_judge = {}
    for judge in sorted({r["judge"] for r in runs}):
        sub = [r for r in runs if r["judge"] == judge]
        by_judge[judge] = {
            "n_runs": len(sub),
            "mean_rho_1": float(np.mean([r["rho_1"] for r in sub])),
            "mean_drift_rho": float(np.mean([r["drift_rho"] for r in sub])),
            "mean_sd_rho": float(np.mean([r["sd_rho"] for r in sub])),
            "runs_with_a_sign_flip": sum(1 for r in sub if r["sign_flips"] > 0),
            "mean_zero_spread_rounds": float(np.mean(
                [r["zero_spread_rounds"] for r in sub])),
        }

    result = {
        "description": (
            "Agreement drift over a run, and whether a co-evolving judge drives "
            "more of it than a frozen one. Corpus: "
            "experiments/spread_util_unified.json."
        ),
        "n_runs": len(runs),
        "by_judge": by_judge,
        "contrasts": contrasts,
        "horizon_decay_of_round1_agreement": horizon_decay(runs),
        "decay_difference_at_round4": decay_difference(runs, 4),
        "decay_difference_at_round3": decay_difference(runs, 3),
        "runs": runs,
        "conventions": {
            "evolving_judges": sorted(EVOLVING),
            "excluded_from_the_contrast": sorted(EXCLUDE_FROM_CONTRAST),
            "zero_spread_rounds": (
                "agreement recorded as 0 when every candidate scores the same; "
                "kept rather than dropped, because collapsed pools are the "
                "behaviour under study, and counted per run"),
        },
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")

    print(f"{len(runs)} runs with at least two scored rounds\n")
    print("BY JUDGE")
    print(f"  {'judge':14s} {'n':>3s} {'rho_1':>7s} {'|drift|':>8s} {'sd':>7s} "
          f"{'flips':>6s} {'0-spread':>9s}")
    for judge, v in by_judge.items():
        print(f"  {judge:14s} {v['n_runs']:3d} {v['mean_rho_1']:7.3f} "
              f"{v['mean_drift_rho']:8.3f} {v['mean_sd_rho']:7.3f} "
              f"{v['runs_with_a_sign_flip']:6d} {v['mean_zero_spread_rounds']:9.2f}")
    print()
    print("CONTRASTS  (evolving judge minus frozen judge)")
    for c in contrasts:
        p = c["permutation"]
        print(f"  {c['metric']:10s} {c['cell']:34s} "
              f"n={c['n_evolving']}v{c['n_frozen']}  "
              f"{c['mean_evolving']:.3f} vs {c['mean_frozen']:.3f}  "
              f"diff={c['difference']:+.3f}  p={p['p_two_sided']:.3f}"
              f"{'' if p['exact'] else ' (sampled)'}")
        mdd = c["minimum_detectable_difference_at_this_n"]
        if mdd is not None:
            print(f"             minimum detectable difference at this n: {mdd:.3f}"
                  f"; seeds/arm for 80% power on the observed effect: "
                  f"{c['seeds_per_arm_for_80pct_power_on_observed_effect']}")
    print()
    print("DECAY OF ROUND-1 AGREEMENT  corr(rho_1, rho_t)")
    for label, per_t in result["horizon_decay_of_round1_agreement"].items():
        bits = []
        for t, v in per_t.items():
            bits.append(f"{t}: " + ("n/a" if v["corr"] is None
                                    else f"{v['corr']:+.3f} (n={v['n']})"))
        print(f"  {label:16s} " + "   ".join(bits))
    for horizon in (3, 4):
        d = result[f"decay_difference_at_round{horizon}"]
        if d:
            print(f"  round{horizon} difference (Fisher z): "
                  f"{d['fisher_z_difference']:+.3f} "
                  f"[{d['fisher_z_ci'][0]:+.3f}, {d['fisher_z_ci'][1]:+.3f}]"
                  f"  evolving r={d['corr_evolving']:+.3f} (n={d['n_evolving']}) "
                  f"vs frozen r={d['corr_frozen']:+.3f} (n={d['n_frozen']})"
                  f"{'  EXCLUDES ZERO' if d['excludes_zero'] else ''}")
    print()
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

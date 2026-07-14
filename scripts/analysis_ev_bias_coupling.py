"""EV BIAS coupling — the original narrative test: does moving the risk
PREFERENCE drag the model's EV BELIEFS in the biased direction (risk-seeking
overrates gambles, risk-averse underrates)? (docs/ANALYSIS_LEDGER.md;
user 07-14: accuracy was the wrong read — the question is the BIAS.)

Two signed belief measures per round, both persisted by every battery:
  gamble_belief_bias = mean over the 24 factual items of P(model says the
      GAMBLE side has higher EV) minus 0.5 (the item set is balanced 12/12,
      so 0 = unbiased, + = gamble-favoring belief).
  log_est_ratio = log(ev_estimation.mean_ratio): numeric EV estimates for
      gambles divided by truth; + = overrates gamble EV.

Couplings, per family:
  WITHIN-RUN: corr(preference_t, bias_t) across rounds, distribution over runs
      (does belief track preference round by round?).
  ACROSS-RUN (signed): corr(Δpreference, Δbias) over runs — when selection
      moved the value up, did gamble-EV belief move up?
  BASELINE: corr(preference_0, bias_0) across runs — do installed organisms
      already believe in their value's favor?

Usage: uv run python scripts/analysis_ev_bias_coupling.py
Writes experiments/ev_bias_coupling.json and prints the tables.
"""

import glob
import json
import math
import os

FILES = sorted(glob.glob("experiments/modal_k2_release/output/*.json")) + [
    "experiments/kaggle/kaggle_k2_olmo_inversion/output_controls/k2_olmo_inversion_kaggle_controls.json",
    "experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_conf_v1_seeds12_partial.json",
    "experiments/kaggle/kaggle_k2_olmo_inversion_conf/output/k2_olmo_inversion_kaggle_conf_v2.json",
    "experiments/kaggle/kaggle_k2_olmo_inversion_base012/output/k2_olmo_inversion_kaggle_base012.json",
    "experiments/cerebrium_k2/output/k2_cerebrium_seed0_complete.json",
    "experiments/kaggle/kaggle_k1_qwen_anchor_grid/output/k1_qwen_anchor.json",
]


def mean(x):
    return sum(x) / len(x) if x else None


def corr(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(pairs) < 3:
        return None
    a = [p[0] for p in pairs]
    b = [p[1] for p in pairs]
    ma, mb = mean(a), mean(b)
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    if sa == 0 or sb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def gamble_bias(fe):
    ps = []
    n_gc = 0
    for it in fe["items"]:
        p_gamble = it["p_correct"] if it["correct_letter"] == it["gamble_letter"] \
            else 1.0 - it["p_correct"]
        ps.append(p_gamble)
        n_gc += it["correct_letter"] == it["gamble_letter"]
    return mean(ps) - n_gc / len(fe["items"])


def rnd(x, k=3):
    return None if x is None else round(x, k)


def main():
    runs = []
    for f in FILES:
        if not os.path.exists(f):
            continue
        grid = "k1_qwen" if "k1_qwen" in f else "k2_olmo"
        d = json.load(open(f))
        for seed in d:
            if seed.startswith("_"):
                continue
            for cond, rec in d[seed].items():
                bat = rec.get("battery")
                traj = rec.get("traj")
                if not isinstance(bat, list) or len(bat) < 3 or not traj:
                    continue
                bias, est = [], []
                for b in bat:
                    if not isinstance(b, dict) or "factual_ev" not in b:
                        continue
                    bias.append(round(gamble_bias(b["factual_ev"]), 4))
                    mr = b.get("ev_estimation", {}).get("mean_ratio")
                    est.append(round(math.log(mr), 4) if mr and mr > 0 else None)
                n = min(len(bias), len(traj))
                if n < 3:
                    continue
                bias, est, tr = bias[:n], est[:n], traj[:n]
                runs.append(dict(
                    grid=grid, cond=cond, seed=seed,
                    traj=[round(x, 3) for x in tr], bias=bias, log_est=est,
                    within_bias=corr(tr, bias),
                    within_est=corr(tr, est),
                    d_traj=round(tr[-1] - tr[0], 3),
                    d_bias=round(bias[-1] - bias[0], 4),
                    d_est=(round(est[-1] - est[0], 4)
                           if est[0] is not None and est[-1] is not None else None)))
    out = {"runs": runs, "by_group": {}}
    for grid in ("k2_olmo", "k1_qwen"):
        rs = [r for r in runs if r["grid"] == grid]
        if not rs:
            continue
        wb = [r["within_bias"] for r in rs if r["within_bias"] is not None]
        we = [r["within_est"] for r in rs if r["within_est"] is not None]
        out["by_group"][grid] = dict(
            n=len(rs),
            baseline_corr_pref_bias=rnd(corr([r["traj"][0] for r in rs],
                                             [r["bias"][0] for r in rs])),
            mean_bias_r0=round(mean([r["bias"][0] for r in rs]), 4),
            within_run_corr_bias_mean=round(mean(wb), 3),
            within_run_corr_bias_pos_share=round(mean([w > 0 for w in wb]), 2),
            within_run_corr_est_mean=round(mean(we), 3) if we else None,
            signed_delta_corr_bias=rnd(corr([r["d_traj"] for r in rs],
                                            [r["d_bias"] for r in rs])),
            signed_delta_corr_est=rnd(corr([r["d_traj"] for r in rs],
                                           [r["d_est"] for r in rs])))
    with open("experiments/ev_bias_coupling.json", "w") as fh:
        json.dump(out, fh, indent=1)

    for grid, v in out["by_group"].items():
        print(f"== {grid} (n={v['n']})")
        print(f"   baseline: corr(pref_0, bias_0) = {v['baseline_corr_pref_bias']}; mean bias_0 = {v['mean_bias_r0']:+.4f}")
        print(f"   within-run corr(pref_t, bias_t): mean {v['within_run_corr_bias_mean']}, positive in {v['within_run_corr_bias_pos_share']} of runs")
        print(f"   within-run corr(pref_t, log est ratio): mean {v['within_run_corr_est_mean']}")
        print(f"   SIGNED deltas: corr(d_pref, d_bias) = {v['signed_delta_corr_bias']}; corr(d_pref, d_log_est) = {v['signed_delta_corr_est']}")
    print("\nBiggest signed movers (d_traj vs d_bias):")
    for r in sorted(runs, key=lambda r: -abs(r["d_traj"]))[:10]:
        print(f"  {r['grid']}/{r['cond']:18s} s{r['seed']:>3s} d_pref {r['d_traj']:+.2f}  d_bias {r['d_bias']:+.4f}  d_log_est {r['d_est']}")


if __name__ == "__main__":
    main()

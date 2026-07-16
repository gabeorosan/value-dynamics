"""The (value, rho*sigma) field's vertical component, measured per axis
(user question 07-16: the field figure bends the risk panels' arrows with the
binary envelope but drew the continuous self-description panels flat — and
flat is also a dynamics assertion. Measure both.)

For every consecutive round pair within a run (both rounds with a defined
agreement rho), let y = rho * own_spread (the forecast one-round move — the
plane's vertical coordinate) and v the behavioral value. Readouts per axis:

  1. persistence of y:      corr(y_next, y), plus mean and SD of dy = y' - y
  2. coupling to the move:  OLS  dy = a + b*dv  (does the forecast-move
     coordinate shrink or grow when the value moves?)
  3. envelope check:        corr(dy, dy_env) where
     dy_env = y * (env(v')/env(v) - 1), env(v) = sqrt(v(1-v)) — the
     schematic bend the risk panels draw. Computed on both axes: it should
     track on the binary risk axis (where sigma is tied to the envelope)
     and is expected to fail on the continuous axis.

Usage: uv run python scripts/analysis_field_vertical_component.py
Writes experiments/field_vertical_component.json and prints the table.
"""

import json
import math
from collections import defaultdict

DATA = "experiments/spread_util_unified.json"


def mean(x):
    return sum(x) / len(x) if x else None


def corr(a, b):
    if len(a) < 3:
        return None
    ma, mb = mean(a), mean(b)
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((y - mb) ** 2 for y in b))
    if sa == 0 or sb == 0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def ols(x, y):
    mx, my = mean(x), mean(y)
    sxx = sum((a - mx) ** 2 for a in x)
    if sxx == 0:
        return None, None
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sxx
    return my - b * mx, b


def env(v):
    v = min(1.0, max(0.0, v))
    return math.sqrt(v * (1.0 - v))


def main():
    d = json.load(open(DATA))
    runs = defaultdict(list)
    for r in d["records"]:
        runs[(r["cond"], r["seed"], r["source"])].append(r)

    out = {}
    for axis in ("risk", "selfreport"):
        pairs = []
        for rows in runs.values():
            rows = sorted(rows, key=lambda r: r["round"])
            if rows[0]["axis"] != axis:
                continue
            by = {r["round"]: r for r in rows}
            for t in by:
                if t + 1 not in by:
                    continue
                a, b = by[t], by[t + 1]
                if a["rho"] is None or b["rho"] is None:
                    continue
                y0 = a["rho"] * a["own_spread"]
                y1 = b["rho"] * b["own_spread"]
                v0, v1 = a["value"], a["value"] + a["drift"]
                pairs.append(dict(y0=y0, y1=y1, dv=v1 - v0, v0=v0,
                                  dy=y1 - y0,
                                  dy_env=(y0 * (env(v1) / env(v0) - 1.0)
                                          if 0.02 < v0 < 0.98 and 0.02 < v1 < 0.98
                                          else None)))
        dy = [p["dy"] for p in pairs]
        dv = [p["dv"] for p in pairs]
        a_fit, b_fit = ols(dv, dy)
        env_pairs = [(p["dy"], p["dy_env"]) for p in pairs if p["dy_env"] is not None]
        out[axis] = dict(
            n_transitions=len(pairs),
            y_persistence_corr=round(corr([p["y0"] for p in pairs],
                                          [p["y1"] for p in pairs]), 3),
            dy_mean=round(mean(dy), 4),
            dy_sd=round(math.sqrt(mean([(x - mean(dy)) ** 2 for x in dy])), 4),
            dy_on_dv_intercept=round(a_fit, 4),
            dy_on_dv_slope=round(b_fit, 4),
            dy_dv_corr=round(corr(dv, dy), 3),
            envelope_corr=(round(corr([e[0] for e in env_pairs],
                                      [e[1] for e in env_pairs]), 3)
                           if len(env_pairs) >= 3 else None),
            n_envelope_pairs=len(env_pairs),
        )

    with open("experiments/field_vertical_component.json", "w") as f:
        json.dump(out, f, indent=1)
    for axis, v in out.items():
        print(f"{axis}: n={v['n_transitions']}  y-persistence r={v['y_persistence_corr']}  "
              f"dy mean={v['dy_mean']} sd={v['dy_sd']}")
        print(f"       dy = {v['dy_on_dv_intercept']} + {v['dy_on_dv_slope']}*dv  "
              f"(r={v['dy_dv_corr']})   envelope corr={v['envelope_corr']} "
              f"(n={v['n_envelope_pairs']})")


if __name__ == "__main__":
    main()

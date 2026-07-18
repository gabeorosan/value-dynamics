#!/usr/bin/env python3
"""model-endpoint-visual — the selection-loop endpoint recurrence, shown as
MOTION on the value line instead of an equation.

Part 1 (schematic): how one round moves the current value — a mixing pull
toward the supplier's level, a selection step of rho*sigma, and the walls at
0 and 1. The mixed case levels off where the two forces balance; the self-only
case is a plain staircase of rho*sigma steps into a wall.

Part 2 (real held-out runs): three held-out runs, each rolled forward from its
OWN first-round pool. Solid = observed value each round; dashed = the
deterministic unit path k = clip(pool + rho*sigma); shaded = the 10-90%
predictive band from the committed staged-noise recipe (noise added only where
the measurement implies it). The simulator (rollout / residual_scales /
meas_sd) is copied verbatim from the spread-rollout-bakeoff generator; the two
committed anchors on the evidence line are read and ASSERTED from the result
JSONs, not transcribed.

House style copied from docs/figures/src/make_figures.py (palette, esc/wrap,
box/arrow helpers). Stdlib only. Run from this directory:
    python3 model-endpoint-visual.py
"""
import json
import math
import os
import random
import statistics
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
EXP = os.path.join(ROOT, "experiments")
UNIFIED = os.path.join(EXP, "spread_util_unified.json")      # Part 2 first-round state + trajectories
STAGED = os.path.join(EXP, "trajectory_adjustment_bakeoff.json")  # coverage / CRPS anchor
UNIT = os.path.join(EXP, "unit_rollout_properties.json")     # endpoint-error anchor

# ---- palette (verbatim from make_figures.py) ----
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series / the rolled-forward forecast
GREEN = "#3a7d44"      # frozen / oracle judge series / evidence emphasis
RED = "#b5342c"        # reversal / warning emphasis
GRAY = "#6b7684"       # recessive only (axes, muted captions)
BAND_FILL = "#cfe0f1"  # predictive band (light blue)
KEY_FILL = "#eef5ee"
DOC_FILL = "#fdf6e8"
FAINT = "#e6e8ec"
FONT = "Helvetica, Arial, sans-serif"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def txt(x, y, s, size, color=INK, anchor="start", weight="normal"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')


DEFS = f'''<defs>
<marker id="arr" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrB" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{BLUE}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker>
</defs>'''


def arrow(x1, y1, x2, y2, sw=4, color=INK, mid="arr"):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#{mid})"/>')


# ====================================================================
# Part 2 simulator + data  (copied verbatim from spread-rollout-bakeoff.py)
# ====================================================================
with open(UNIFIED) as f:
    RECORDS = json.load(f)["records"]
with open(STAGED) as f:
    ST = json.load(f)

# --- committed evidence numbers (asserted, not transcribed) ---------------
PRI = ST["primary_selection_driven_plus_swap"]
DET_V = PRI["unit_core_deterministic"]
STG_V = PRI["unit_core_selector_q_observation_rho_persistence_gaussian"]
assert DET_V["n_runs"] == 45 and STG_V["n_runs"] == 45, "expected 45-run set"
STG_CRPS = STG_V["endpoint_crps"]
STG_COV = STG_V["endpoint_80pct_coverage"]
assert round(STG_CRPS, 3) == 0.092, STG_CRPS
assert round(STG_COV, 2) == 0.89, STG_COV


def run_key(r):
    return (r["cond"], r["seed"], r["source"])


_groups = defaultdict(list)
for _r in RECORDS:
    _groups[run_key(_r)].append(_r)
RUNS = {k: sorted(v, key=lambda r: r["round"]) for k, v in _groups.items()
        if len(v) >= 2 and min(r["round"] for r in v) == 1}


def _std(xs):
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def _transitions(rows):
    by = {r["round"]: r for r in rows}
    return [(by[t], by[t + 1]) for t in by if t + 1 in by]


def residual_scales(cond, axis):
    """Leave-one-condition-out gaussian innovation SDs, axis-restricted,
    exactly the unit-core residual pools of analysis_trajectory_adjustments.py."""
    train = [r for r in RECORDS if r["cond"] != cond]
    gap = [r["gap"] - r["rho"] * r["mean_item_sd"]
           for r in train if r["axis"] == axis and r["rho"] is not None]
    q_res, rho_res = [], []
    tg = defaultdict(list)
    for r in train:
        tg[run_key(r)].append(r)
    for rows in tg.values():
        if rows[0]["axis"] != axis:
            continue
        for a, b in _transitions(sorted(rows, key=lambda r: r["round"])):
            q_res.append((b["own_mean"] - a["own_mean"]) - a["self_relative_gap"])
            if a["rho"] is not None and b["rho"] is not None:
                rho_res.append(b["rho"] - a["rho"])
    return _std(gap), _std(q_res), _std(rho_res)


def meas_sd(v, n):
    if not n or n <= 0:
        return 0.0
    v = min(1.0, max(0.0, v))
    return math.sqrt(max(0.0, v * (1.0 - v)) / n)


def rollout(rows, n_paths=500, seed=4242):
    """Deterministic unit path + 500 staged-noise draws for one held-out run."""
    first = rows[0]
    sigma = first["own_spread"]
    u = float(first.get("pool_cogen_fraction") or 0.0) \
        if first["composition"] != "self-only" else 0.0
    s_mean = float(first["cogen_mean"]) if first["composition"] != "self-only" else 0.0
    sg, sq, sr = residual_scales(first["cond"], first["axis"])

    def one(noisy, rng):
        q, value, rho = first["own_mean"], first["value"], first["rho"]
        out = [value]
        for obs in rows:
            pool = (1.0 - u) * q + u * s_mean
            gap = rho * sigma + (rng.gauss(0.0, sg) if noisy else 0.0)
            kept = min(1.0, max(0.0, pool + gap))
            q = min(1.0, max(0.0, q + (kept - q) + (rng.gauss(0.0, sq) if noisy else 0.0)))
            value = min(1.0, max(0.0, value + (kept - value)))
            if noisy:
                rho = min(1.0, max(-1.0, rho + rng.gauss(0.0, sr)))
            reported = value
            if noisy:
                reported = min(1.0, max(0.0, value + rng.gauss(
                    0.0, meas_sd(value, obs.get("next_value_measurement_n")))))
            out.append(reported)
        return out

    det = one(False, random.Random(0))
    rng = random.Random(seed)
    paths = [one(True, rng) for _ in range(n_paths)]
    return det, paths


def quantile(xs, q):
    xs = sorted(xs)
    i = q * (len(xs) - 1)
    lo = int(i)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] * (1 - (i - lo)) + xs[hi] * (i - lo)


def observed(rows):
    return [rows[0]["value"]] + [r["value"] + r["drift"] for r in rows]


def find(cond, seed):
    for k, rows in RUNS.items():
        if k[0] == cond and str(k[1]) == str(seed):
            return rows
    raise KeyError((cond, seed))


# three held-out runs (verbatim choices from spread-rollout-bakeoff.py):
#   OLMo cautious-copy seed 2, Qwen self-judge seed 44, Qwen score-oracle seed 101
PANELS = [
    ("frozen_cons_r0", 2),
    ("selfaware_loop_grid", 44),
    ("judge_opposition_oracle", 101),
]


def load_endpoint_error():
    e = json.load(open(UNIT))["endpoint_only_matched_45"][
        "by_regime_group"]["selection_driven"]
    return e["unit_recurrence_endpoint_mae"], e["n_runs"]


# ====================================================================
# Figure
# ====================================================================
def build():
    mae_move, n_sel = load_endpoint_error()
    assert round(mae_move, 3) == 0.118, mae_move
    assert n_sel == 36, n_sel

    W, H = 1540, 1332
    body = []
    body.append(f'<rect width="{W}" height="{H}" fill="white"/>')
    body.append(DEFS)

    # ---- Title (orientation only; interpretation lives in caption.md) ----
    body.append(txt(60, 60,
        "The endpoint recurrence: one round’s move, repeated",
        31, INK, weight="bold"))
    body.append(txt(60, 96,
        "Part 1 — how one selection round moves the value.   "
        "Part 2 — that one move rolled forward from round 1 on three held-out runs.",
        19, GRAY))

    # ==================================================================
    # PART 1 — schematic: how one round moves the value  (verbatim)
    # ==================================================================
    body.append(txt(60, 190, "Part 1  ·  How one round moves the current value",
                    22, INK, weight="bold"))

    # ---- shared plot-frame helper ----
    def frame(ox, oy, pw, ph, title, sub):
        s = [box(ox, oy, pw, ph, "white", GRAY, 1.6, rx=6)]
        # y gridlines 0 / .5 / 1
        for v, lab in [(1.0, "1"), (0.5, "½"), (0.0, "0")]:
            yy = oy + ph * (1 - v)
            s.append(f'<line x1="{ox}" y1="{yy}" x2="{ox+pw}" y2="{yy}" '
                     f'stroke="#e6e8ec" stroke-width="1.4"/>')
            s.append(txt(ox - 12, yy + 6, lab, 17, GRAY, anchor="end"))
        s.append(txt(ox - 40, oy + ph / 2, "value", 17, GRAY, anchor="middle",
                     ) .replace("<text ", f'<text transform="rotate(-90 {ox-40} {oy+ph/2})" '))
        s.append(txt(ox, oy - 20, title, 20, INK, weight="bold"))
        if sub:
            s.append(txt(ox, oy - 16, sub, 17, GRAY))
        return "\n".join(s)

    def vy(v, oy, ph):
        return oy + ph * (1 - max(0.0, min(1.0, v)))

    # --- Panel A: mixed pool ---
    ax, ay, aw, ah = 108, 300, 590, 300
    R = 4
    def rxA(r):
        return ax + aw * (r / R)
    body.append(frame(ax, ay, aw, ah, "Mixed pool  (some answers from an outside source)", ""))
    # supplier level (dashed)
    sup = 0.90
    ys = vy(sup, ay, ah)
    body.append(f'<line x1="{ax}" y1="{ys}" x2="{ax+aw}" y2="{ys}" stroke="{GREEN}" '
                f'stroke-width="2.4" stroke-dasharray="9 6"/>')
    body.append(txt(ax + aw - 6, ys - 10, "outside-source level", 17, GREEN, anchor="end", weight="bold"))
    # balance line (dotted)
    bal = 0.615
    yb = vy(bal, ay, ah)
    body.append(f'<line x1="{ax}" y1="{yb}" x2="{ax+aw}" y2="{yb}" stroke="{INK}" '
                f'stroke-width="2.2" stroke-dasharray="2 6" stroke-linecap="round"/>')
    body.append(txt(ax + aw - 6, yb - 12, "balance point",
                    17, INK, anchor="end", weight="bold"))
    # trajectory (schematic): rises and flattens onto balance line
    trajA = [0.30, 0.505, 0.585, 0.608, 0.615]
    ptsA = " ".join(f"{rxA(i)},{vy(v, ay, ah):.1f}" for i, v in enumerate(trajA))
    body.append(f'<polyline points="{ptsA}" fill="none" stroke="{BLUE}" stroke-width="4"/>')
    for i, v in enumerate(trajA):
        body.append(f'<circle cx="{rxA(i)}" cy="{vy(v, ay, ah):.1f}" r="6.5" fill="{BLUE}"/>')
    # round-1 decomposition arrows (offset a little right of round 0)
    dx = rxA(0) + (rxA(1) - rxA(0)) * 0.30
    y0 = vy(0.30, ay, ah)
    ymix = vy(0.545, ay, ah)   # after mixing toward supplier by fraction u
    ysel = vy(0.505, ay, ah)   # after selection step rho*sigma (small, down)
    body.append(arrow(dx, y0, dx, ymix + 4, 4.5, BLUE, "arrB"))
    body.append(arrow(dx, ymix, dx, ysel - 3, 4.5, RED, "arrR"))
    # labels sit in the empty lower-left, below the start point
    body.append(txt(dx + 16, vy(0.205, ay, ah), "mixing pull toward the outside source  (share u)",
                    16, BLUE, weight="bold"))
    body.append(txt(dx + 16, vy(0.115, ay, ah), "then a selection step of  ρσ", 16, RED, weight="bold"))
    # walls
    body.append(txt(ax + 6, ay + 20, "wall at 1", 16, GRAY))
    body.append(txt(ax + 6, ay + ah - 10, "wall at 0", 16, GRAY))
    # round axis
    for r in range(R + 1):
        body.append(txt(rxA(r), ay + ah + 24, str(r), 16, GRAY, anchor="middle"))
    body.append(txt(ax + aw / 2, ay + ah + 48, "round", 17, GRAY, anchor="middle"))

    # --- Panel B: self-only pool ---
    bx, by, bw, bh = 838, 300, 590, 300
    def rxB(r):
        return bx + bw * (r / R)
    body.append(frame(bx, by, bw, bh, "Self-only pool  (no outside source, u = 0)", ""))
    trajB = [0.86, 0.63, 0.40, 0.17, 0.0]   # clipped at wall
    # stepped path
    seg = []
    for i, v in enumerate(trajB):
        x = rxB(i)
        y = vy(v, by, bh)
        if i == 0:
            seg.append(f"M {x} {y}")
        else:
            xprev = rxB(i - 1)
            yprev = vy(trajB[i - 1], by, bh)
            seg.append(f"L {xprev + (x - xprev)*0.5} {yprev} L {xprev + (x - xprev)*0.5} {y} L {x} {y}")
    body.append(f'<path d="{" ".join(seg)}" fill="none" stroke="{RED}" stroke-width="4"/>')
    for i, v in enumerate(trajB):
        body.append(f'<circle cx="{rxB(i)}" cy="{vy(v, by, bh):.1f}" r="6.5" fill="{RED}"/>')
    # one-step brace/label
    xstep = rxB(1) + (rxB(2) - rxB(1)) * 0.5
    y1 = vy(trajB[1], by, bh)
    y2 = vy(trajB[2], by, bh)
    body.append(f'<line x1="{xstep+10}" y1="{y1}" x2="{xstep+10}" y2="{y2}" stroke="{INK}" stroke-width="2"/>')
    body.append(f'<line x1="{xstep+5}" y1="{y1}" x2="{xstep+15}" y2="{y1}" stroke="{INK}" stroke-width="2"/>')
    body.append(f'<line x1="{xstep+5}" y1="{y2}" x2="{xstep+15}" y2="{y2}" stroke="{INK}" stroke-width="2"/>')
    body.append(txt(xstep + 22, (y1 + y2) / 2 + 6, "each round steps by ρσ", 16, INK, weight="bold"))
    body.append(txt(bx + 6, by + bh - 10, "the wall at 0 stops it", 16, GRAY))
    for r in range(R + 1):
        body.append(txt(rxB(r), by + bh + 24, str(r), 16, GRAY, anchor="middle"))
    body.append(txt(bx + bw / 2, by + bh + 48, "round", 17, GRAY, anchor="middle"))

    # ==================================================================
    # PART 2 — three held-out runs: observed vs the rolled-forward forecast
    # ==================================================================
    body.append(txt(60, 712,
        "Part 2  ·  Three held-out runs: observed vs the forecast rolled from round 1",
        22, INK, weight="bold"))

    # --- one shared key (observed / deterministic path / predictive band) ---
    ky = 750
    kx = 60
    body.append(f'<line x1="{kx}" y1="{ky-5}" x2="{kx+40}" y2="{ky-5}" stroke="{INK}" stroke-width="3.2"/>')
    body.append(f'<circle cx="{kx+20}" cy="{ky-5}" r="4.2" fill="{INK}"/>')
    body.append(txt(kx + 50, ky, "observed value each round", 17, INK))
    kx = 400
    body.append(f'<line x1="{kx}" y1="{ky-5}" x2="{kx+40}" y2="{ky-5}" stroke="{BLUE}" '
                f'stroke-width="3.2" stroke-dasharray="9 6"/>')
    body.append(txt(kx + 50, ky, "deterministic path  k = clip(pool + ρσ)", 17, INK))
    kx = 830
    body.append(f'<rect x="{kx}" y="{ky-15}" width="40" height="16" rx="3" fill="{BAND_FILL}"/>')
    body.append(txt(kx + 50, ky, "predictive band (10–90%, staged noise)", 17, INK))

    # --- three trajectory panels ---
    LEFT = 60
    gap_between = 54
    pw = (W - 2 * LEFT - 2 * gap_between) / 3.0
    PLOT_LEFT_PAD = 48
    plot_w = pw - PLOT_LEFT_PAD - 10
    PLOT_TOP = 866
    PLOT_H = 290
    PLOT_BOT = PLOT_TOP + PLOT_H
    META_TOP = 802

    for idx, (cond, seed) in enumerate(PANELS):
        rows = find(cond, seed)
        first = rows[0]
        det, paths = rollout(rows)
        obs = observed(rows)
        n_pts = len(obs)
        lo = [quantile([p[i] for p in paths], 0.10) for i in range(n_pts)]
        hi = [quantile([p[i] for p in paths], 0.90) for i in range(n_pts)]

        px0 = LEFT + idx * (pw + gap_between)
        plot_x0 = px0 + PLOT_LEFT_PAD
        plot_x1 = plot_x0 + plot_w

        def X(i):
            return plot_x0 + (plot_w * i / (n_pts - 1))

        def Y(v):
            return PLOT_BOT - v * PLOT_H

        # panel metadata lines (measurement recipe visible: rho, sigma, judge)
        axis_word = "self-report" if first["axis"] == "selfreport" else "risk"
        body.append(txt(px0, META_TOP,
                        f"{'ABC'[idx]}.  {first['organism']} · judge: {first['judge']}",
                        18, INK, weight="bold"))
        body.append(txt(px0, META_TOP + 22,
                        f"{axis_word} value · seed {seed} · self-only pool", 15, GRAY))
        body.append(txt(px0, META_TOP + 42,
                        f"round-1 ρ {first['rho']:+.2f} · spread σ {first['own_spread']:.2f}",
                        15, GRAY))

        # y gridlines + labels
        for gv in (0.0, 0.5, 1.0):
            gy = Y(gv)
            body.append(f'<line x1="{plot_x0}" y1="{gy:.1f}" x2="{plot_x1}" y2="{gy:.1f}" '
                        f'stroke="{INK if gv == 0 else FAINT}" '
                        f'stroke-width="{1.6 if gv == 0 else 1.0}"/>')
            body.append(txt(plot_x0 - 10, gy + 5, f"{gv:g}", 15, GRAY, anchor="end"))
        body.append(f'<line x1="{plot_x0}" y1="{PLOT_TOP}" x2="{plot_x0}" y2="{PLOT_BOT}" '
                    f'stroke="{INK}" stroke-width="1.6"/>')
        body.append(txt(plot_x0 - 38, PLOT_TOP + PLOT_H / 2, "value", 15, GRAY, anchor="middle"
                        ).replace("<text ",
                        f'<text transform="rotate(-90 {plot_x0-38} {PLOT_TOP+PLOT_H/2})" '))

        # predictive band polygon (hi forward, lo backward)
        band = ([(X(i), Y(hi[i])) for i in range(n_pts)]
                + [(X(i), Y(lo[i])) for i in range(n_pts - 1, -1, -1)])
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in band)
        body.append(f'<polygon points="{poly}" fill="{BAND_FILL}" '
                    f'fill-opacity="0.7" stroke="none"/>')

        # deterministic path (dashed blue)
        pd = " ".join(f"{X(i):.1f},{Y(det[i]):.1f}" for i in range(n_pts))
        body.append(f'<polyline points="{pd}" fill="none" stroke="{BLUE}" '
                    f'stroke-width="2.6" stroke-dasharray="9 6" stroke-linejoin="round"/>')
        # observed path (solid ink) + dots
        po = " ".join(f"{X(i):.1f},{Y(obs[i]):.1f}" for i in range(n_pts))
        body.append(f'<polyline points="{po}" fill="none" stroke="{INK}" '
                    f'stroke-width="3" stroke-linejoin="round"/>')
        for i in range(n_pts):
            body.append(f'<circle cx="{X(i):.1f}" cy="{Y(obs[i]):.1f}" r="4.4" '
                        f'fill="{INK}" stroke="white" stroke-width="1.4"/>')

        # x axis: round numbers + label
        for r in range(n_pts):
            body.append(txt(X(r), PLOT_BOT + 24, str(r), 15, GRAY, anchor="middle"))
        body.append(txt((plot_x0 + plot_x1) / 2, PLOT_BOT + 48,
                        "selection round", 15, GRAY, anchor="middle"))

    # ==================================================================
    # Evidence line  (ONE line, both committed anchors)
    # ==================================================================
    ebx, eby, ebw, ebh = 60, 1206, W - 120, 72
    body.append(box(ebx, eby, ebw, ebh, KEY_FILL, GREEN, 2.4, rx=10))
    body.append(
        f'<text x="{ebx+22}" y="{eby+34}" font-family="{FONT}" font-size="19" font-weight="bold">'
        f'<tspan fill="{INK}">{n_sel} selection-driven held-out runs: endpoint error </tspan>'
        f'<tspan fill="{GREEN}">{mae_move:.3f}</tspan>'
        f'<tspan fill="{INK}">   ·   staged-noise band covers </tspan>'
        f'<tspan fill="{GREEN}">{STG_COV:.0%}</tspan>'
        f'<tspan fill="{INK}"> of the 45 held-out endpoints (CRPS </tspan>'
        f'<tspan fill="{GREEN}">{STG_CRPS:.3f}</tspan>'
        f'<tspan fill="{INK}">)</tspan>'
        f'</text>')
    body.append(txt(ebx + 22, eby + 58,
        "endpoint error = mean-absolute error of the final-round value (0–1 scale);  "
        "coverage = share of endpoints inside the 10–90% band.  "
        "The two counts are different held-out sets — see caption.",
        15, GRAY))

    # ---- source footnote ----
    fy = eby + ebh + 26
    body.append(txt(60, fy,
        "Part 1 is a schematic (illustrative marks). Part 2 paths and band regenerated with "
        "stdlib from experiments/spread_util_unified.json first-round state via the committed "
        "unit recurrence and staged-noise residual pools.", 13, GRAY))
    body.append(txt(60, fy + 18,
        "Endpoint error read from experiments/unit_rollout_properties.json; coverage / CRPS "
        "read and asserted from experiments/trajectory_adjustment_bakeoff.json.  "
        "Generator: model-endpoint-visual.py", 13, GRAY))

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'font-family="{FONT}">\n' + "\n".join(body) + "\n</svg>")
    return svg


if __name__ == "__main__":
    svg = build()
    out = os.path.join(HERE, "model-endpoint-visual.svg")
    with open(out, "w") as f:
        f.write(svg)
    print("wrote", out)

#!/usr/bin/env python3
"""model-endpoint-visual — the selection-loop endpoint recurrence, shown as
MOTION on the value line instead of an equation.

Part 1 (schematic): how one round moves the current value — a mixing pull
toward the supplier's level, a selection step of rho*sigma, and the walls at
0 and 1. The mixed case levels off where the two forces balance; the self-only
case is a plain staircase of rho*sigma steps into a wall.

Part 2 (real held-out runs): predicted (dashed) vs observed (solid) per-round
trajectories for three archetypal runs, each rolled from its own first pool.

House style copied from docs/figures/src/make_figures.py (palette, esc/wrap,
box/arrow helpers). Stdlib only. Run from this directory:  python3 model-endpoint-visual.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(ROOT, "experiments", "selection_response_predictor.json")
BAKE = os.path.join(ROOT, "experiments", "spread_rollout_bakeoff.json")
UNIT = os.path.join(ROOT, "experiments", "unit_rollout_properties.json")

# ---- palette (verbatim from make_figures.py) ----
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series
GREEN = "#3a7d44"      # frozen / oracle judge series
RED = "#b5342c"        # reversal / warning emphasis
GRAY = "#6b7684"       # recessive only (axes, muted captions)
KEY_FILL = "#eef5ee"
DOC_FILL = "#fdf6e8"
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
# Load real data for Part 2
# ====================================================================
def load_runs():
    pred = json.load(open(PRED))["endpoint_with_boundary_refresh"][
        "recommended_unit_agreement_spread"]["per_run"]
    bake = json.load(open(BAKE))["validations"]["leave_one_condition_out"][
        "frozen"]["mean_within_prompt_population_sd"]["per_run"]
    pred = {r["run_key"]: r for r in pred}
    bake = {r["run_key"]: r for r in bake}

    def series(run_key):
        p, b = pred[run_key], bake[run_key]
        start = p["start"]
        predicted = [start] + list(p["trajectory"])
        observed = [start] + [r["value_after_true"] for r in b["rounds"]]
        return {"predicted": predicted, "observed": observed, "bake": b, "pred": p}

    return series


def load_evidence():
    e = json.load(open(UNIT))["endpoint_only_matched_45"][
        "by_regime_group"]["selection_driven"]
    return e["unit_recurrence_endpoint_mae"], e["no_change_endpoint_mae"], e["n_runs"]


# ====================================================================
# Figure
# ====================================================================
def build():
    series = load_runs()
    mae_move, mae_still, n_sel = load_evidence()

    W, H = 1540, 1190
    body = []
    body.append(f'<rect width="{W}" height="{H}" fill="white"/>')
    body.append(DEFS)

    # ---- Title (orientation only; interpretation lives in caption.md) ----
    body.append(txt(60, 60,
        "The endpoint recurrence: one round’s move, repeated",
        31, INK, weight="bold"))
    body.append(txt(60, 96,
        "Rolled from each run’s first pool — spread and agreement never re-measured;   "
        "dashed = predicted,  solid = observed", 19, GRAY))

    # ==================================================================
    # PART 1 — schematic: how one round moves the value
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
    body.append(frame(ax, ay, aw, ah, "Mixed pool  (some answers come from a supplier)", ""))
    # supplier level (dashed)
    sup = 0.90
    ys = vy(sup, ay, ah)
    body.append(f'<line x1="{ax}" y1="{ys}" x2="{ax+aw}" y2="{ys}" stroke="{GREEN}" '
                f'stroke-width="2.4" stroke-dasharray="9 6"/>')
    body.append(txt(ax + aw - 6, ys - 10, "supplier level", 17, GREEN, anchor="end", weight="bold"))
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
    body.append(txt(dx + 16, vy(0.205, ay, ah), "mixing pull toward supplier  (fraction u)",
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
    body.append(frame(bx, by, bw, bh, "Self-only pool  (no supplier, u = 0)", ""))
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
    # PART 2 — three real held-out runs
    # ==================================================================
    body.append(txt(60, 690, "Part 2  ·  Three held-out runs: predicted (dashed) vs observed (solid)",
                    22, INK, weight="bold"))
    # small legend
    lx = 60
    body.append(f'<line x1="{lx}" y1="722" x2="{lx+44}" y2="722" stroke="{INK}" stroke-width="4" stroke-dasharray="9 6"/>')
    body.append(txt(lx + 54, 728, "predicted (rolled once from the first pool)", 17, INK))
    body.append(f'<line x1="{lx+430}" y1="722" x2="{lx+474}" y2="722" stroke="{INK}" stroke-width="4"/>')
    body.append(txt(lx + 484, 728, "observed (measured each round)", 17, INK))

    panels = [
        ("h2h_invade_self|53|k2rel_h2h_invade_self_s53.json", BLUE, "arrB",
         "Peer invasion, railing high",
         "Half the pool from a risk-railed peer; self-judge duels"),
        ("mixed_reopen_qwen|921|mixed_reopen_qwen.json", GREEN, "arr",
         "Base answers injected — one-round collapse",
         "Base-model answers injected at round 1; scored by an oracle"),
        ("judge_opposition_oracle|101|judge_opposition_oracle.json", RED, "arrR",
         "Oracle scores against the value — reversal",
         "Self-only pool; oracle scores against the trained value"),
    ]

    ptop = 818
    ph = 240
    pw = 400
    gap = 60
    x0 = 60
    for idx, (rk, color, mk, title, plain) in enumerate(panels):
        s = series(rk)
        ox = x0 + idx * (pw + gap)
        oy = ptop
        # frame + grid
        body.append(box(ox, oy, pw, ph, "white", GRAY, 1.6, rx=6))
        for v, lab in [(1.0, "1"), (0.5, "½"), (0.0, "0")]:
            yy = oy + ph * (1 - v)
            body.append(f'<line x1="{ox}" y1="{yy}" x2="{ox+pw}" y2="{yy}" stroke="#e6e8ec" stroke-width="1.4"/>')
            body.append(txt(ox - 10, yy + 6, lab, 16, GRAY, anchor="end"))
        # titles
        body.append(txt(ox, oy - 56, title, 20, color, weight="bold"))
        for j, ln in enumerate(wrap(plain, 44)):
            body.append(txt(ox, oy - 32 + j * 20, ln, 16, GRAY))
        Rn = len(s["observed"]) - 1
        def rxn(r):
            return ox + pw * (r / Rn)
        # predicted (dashed) + observed (solid)
        pp = " ".join(f"{rxn(i)},{vy(v, oy, ph):.1f}" for i, v in enumerate(s["predicted"]))
        po = " ".join(f"{rxn(i)},{vy(v, oy, ph):.1f}" for i, v in enumerate(s["observed"]))
        body.append(f'<polyline points="{pp}" fill="none" stroke="{color}" stroke-width="3.6" '
                    f'stroke-dasharray="9 6" opacity="0.9"/>')
        body.append(f'<polyline points="{po}" fill="none" stroke="{color}" stroke-width="4"/>')
        for i, v in enumerate(s["observed"]):
            body.append(f'<circle cx="{rxn(i)}" cy="{vy(v, oy, ph):.1f}" r="5.5" fill="{color}" '
                        f'stroke="white" stroke-width="1.6"/>')
        for i, v in enumerate(s["predicted"]):
            body.append(f'<circle cx="{rxn(i)}" cy="{vy(v, oy, ph):.1f}" r="4" fill="white" '
                        f'stroke="{color}" stroke-width="2"/>')
        # start + endpoint value labels
        v_start = s["observed"][0]
        v_end = s["observed"][-1]
        vp_end = s["predicted"][-1]
        body.append(txt(rxn(0), vy(v_start, oy, ph) + (-14 if v_start < 0.5 else 26),
                        f"start {v_start:.2f}", 16, INK, anchor="start", weight="bold"))
        endy = vy(v_end, oy, ph)
        if v_end < 0.5:
            ey1, ey2 = endy - 12, endy + 8
            if ey2 > oy + ph - 10:  # endpoint on the floor: stack labels above
                ey1, ey2 = endy - 30, endy - 12
        else:
            ey1, ey2 = endy + 28, endy + 48
        body.append(txt(rxn(Rn) - 4, ey1,
                        f"ends {v_end:.2f}", 16, INK, anchor="end", weight="bold"))
        body.append(txt(rxn(Rn) - 18, ey2,
                        f"predicted {vp_end:.2f}", 15, GRAY, anchor="end"))
        # round axis
        for r in range(Rn + 1):
            body.append(txt(rxn(r), oy + ph + 22, str(r), 16, GRAY, anchor="middle"))
        body.append(txt(ox + pw / 2, oy + ph + 46, "round", 16, GRAY, anchor="middle"))

    # ==================================================================
    # Evidence line
    # ==================================================================
    ey = 1160
    body.append(box(60, ey - 46, W - 120, 60, KEY_FILL, GREEN, 2.4, rx=10))
    body.append(
        f'<text x="82" y="{ey - 12}" font-family="{FONT}" font-size="20" font-weight="bold">'
        f'<tspan fill="{INK}">{n_sel} selection-driven held-out runs: endpoint error </tspan>'
        f'<tspan fill="{GREEN}">{mae_move:.3f}</tspan>'
        f'<tspan fill="{INK}"> vs </tspan>'
        f'<tspan fill="{RED}">{mae_still:.3f}</tspan>'
        f'<tspan fill="{INK}"> no-change</tspan>'
        f'</text>')
    body.append(txt(82, ey + 8, "endpoint mean-absolute error, value on the 0–1 scale",
                    15, GRAY))

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'font-family="{FONT}">\n' + "\n".join(body) + "\n</svg>")
    return svg


if __name__ == "__main__":
    svg = build()
    out = os.path.join(HERE, "model-endpoint-visual.svg")
    with open(out, "w") as f:
        f.write(svg)
    print("wrote", out)

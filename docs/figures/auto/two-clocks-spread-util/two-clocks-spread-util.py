#!/usr/bin/env python3
"""Draft figure: the two factors of the selection gap move on different clocks.

Left panel: candidate value spread sigma per round is a consumable state —
it persists/sags on a self-only pool, is refilled by a base supplier, and
collapses under an extremist peer invader (OLMo-family round means from
spread_ledger). Right panel: judge utilization rho per round holds near a
level set by judge x format x pool (per-round cell means over faint
individual runs, computed from `records`).

Data: ../../../../experiments/spread_util_unified.json
Style: house style copied from docs/figures/src/make_figures.py.
Regenerate with:  python3 two-clocks-spread-util.py
"""
import json
import os
import statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "spread_util_unified.json")

INK = "#1a1a1a"
# five clearly-distinct judge-cell hues + neutral gray
BLUE = "#1f6fd0"       # self-judge, peer invasion  (+0.53)
GREEN = "#1f9e57"      # cautious-copy judge, ref    (+0.38)
RED = "#d1341f"        # score oracle                (−1.0)
VIOLET = "#9427b5"     # self-judge duels, base text (−0.24)
GRAY = "#6b7684"       # base / frozen judges (≈0) AND axes/captions
KEY_FILL = "#eef5ee"   # highlighted takeaway box
GRID = "#e4e4e0"

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


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.38):
    out = []
    for i, ln in enumerate(wrap(text, width)):
        out.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" '
                   f'font-size="{size}" fill="{color}" font-weight="{weight}">{esc(ln)}</text>')
    return "\n".join(out), y + len(wrap(text, width)) * size * lh


def ctext(x, y, s, size, color=INK, weight="normal", anchor="middle"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}" font-family="{FONT}">{esc(s)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ------------------------------------------------------------------
# load data
# ------------------------------------------------------------------
with open(DATA) as f:
    D = json.load(f)

LEDGER = D["spread_ledger"]
BETWEEN = D["utilization"]["between_cell_variance_share_rho"]   # 0.817

# group score-logged records into runs; split repeated round numbers within a
# (cond, seed, source) key into separate sub-runs (occurs for the
# candid-prompt grid, which logged two 2-round runs per seed label)
groups = defaultdict(list)
for r in D["records"]:
    key = (r["organism"], r["axis"], r.get("cond"), r["judge"], r["format"],
           r["composition"], r["seed"], r["source"])
    groups[key].append(r)

RUNS = []  # (meta, [(round, rho), ...]) in round order, rho-bearing only
for key, rr in groups.items():
    sub, last = [], 0
    for x in rr:
        if x["round"] <= last and sub:
            RUNS.append((key, sub))
            sub = []
        sub.append((x["round"], x["rho"]))
        last = x["round"]
    if sub:
        RUNS.append((key, sub))
RUNS = [(k, [(rd, v) for rd, v in t if v is not None]) for k, t in RUNS]
RUNS = [(k, t) for k, t in RUNS if t]


def cell(pred):
    """per-round mean, pooled mean, mean within-run SD, run trajectories"""
    trajs = [t for k, t in RUNS
             if pred(dict(zip(("organism", "axis", "cond", "judge", "format",
                               "composition", "seed", "source"), k)))]
    byround = defaultdict(list)
    for t in trajs:
        for rd, v in t:
            byround[rd].append(v)
    mean_by_round = sorted((rd, st.mean(vs)) for rd, vs in byround.items())
    allv = [v for t in trajs for _, v in t]
    wsds = [st.pstdev([v for _, v in t]) for t in trajs if len(t) > 1]
    return {"mean_by_round": mean_by_round, "mean": st.mean(allv),
            "wsd": st.mean(wsds) if wsds else None, "runs": trajs}


CELLS = {
    "oracle": cell(lambda r: r["judge"] == "score oracle"),
    "self_duel_base": cell(lambda r: r["judge"] == "self" and r["format"] == "duel"
                           and r["composition"] == "base-mixed" and r["organism"] == "Qwen"),
    "cautious_mixed": cell(lambda r: r["judge"] == "cautious copy"
                           and r["format"] == "reference" and r["composition"] == "base-mixed"),
    "self_peer": cell(lambda r: r["judge"] == "self" and r["composition"] == "peer-mixed"),
    "candid": cell(lambda r: r["judge"] == "self" and r["format"] == "candid-prompt"),
    "base_pool": cell(lambda r: r["judge"] == "base" and
                      ((r["format"] == "reference" and r["composition"] == "self-only") or
                       (r["format"] == "duel" and r["composition"] == "base-mixed"))),
    "frozen_copy": cell(lambda r: r["judge"] == "frozen copy"),
}

# the one exception: base-judge run whose agreement rose mid-run (the bloom)
BLOOM = next(t for k, t in RUNS
             if k[0] == "OLMo" and k[2] == "frozen_base" and k[6] == "5")
assert abs(BLOOM[0][1] - 0.01) < 0.01 and abs(max(v for _, v in BLOOM) - 0.27) < 0.01

# ------------------------------------------------------------------
# layout — single panel: agreement is a fixed property of the judge setup
# ------------------------------------------------------------------
W, H = 1120, 600
PY, PH = 150, 330
PX, PW = 150, 600     # plot area (rounds 1..4)
LABX = PX + PW + 20   # right-hand label column

b = []
b.append(ctext(W / 2, 52, "Agreement is a property of the judge, not a "
               "per-round dynamic", 26, weight="bold"))


def X(rd):
    return PX + PW * (rd - 1) / 3


def Y(v):   # rho, -1.1 .. +1.1
    return PY + PH * (1.1 - v) / 2.2


def poly(pts, color, sw=4.0, dash=None, op=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op < 1 else ""
    return (f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
            f'fill="none" stroke="{color}" stroke-width="{sw}"{d}{o}/>')


def dots(pts, color, r=5):
    return "\n".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" '
                     f'stroke="white" stroke-width="1.6"/>' for x, y in pts)


# gridlines + axes
for v in (-1, -0.5, 0, 0.5, 1):
    yy = Y(v)
    b.append(f'<line x1="{PX}" y1="{yy:.1f}" x2="{PX + PW}" y2="{yy:.1f}" '
             f'stroke="{GRID}" stroke-width="1"/>')
    lab = f"+{v:g}" if v > 0 else (f"−{abs(v):g}" if v < 0 else "0")
    b.append(ctext(PX - 12, yy + 6, lab, 17, GRAY, anchor="end"))
zy = Y(0)
b.append(f'<line x1="{PX}" y1="{zy:.1f}" x2="{PX + PW}" y2="{zy:.1f}" stroke="{INK}" '
         f'stroke-width="1.4" stroke-dasharray="6 5"/>')
b.append(ctext(PX + 6, zy + 20, "ρ = 0: keeps at random", 14, GRAY, anchor="start"))
for rd in range(1, 5):
    b.append(ctext(X(rd), PY + PH + 30, str(rd), 17, INK))
b.append(ctext(PX + PW / 2, PY + PH + 60, "round", 18))
b.append(f'<text x="{PX - 66}" y="{PY + PH / 2}" font-size="18" fill="{INK}" '
         f'font-family="{FONT}" transform="rotate(-90 {PX - 66} {PY + PH / 2})" '
         f'text-anchor="middle">judge agreement ρ</text>')

# five distinctly-coloured judge cells, each a flat line (a property) with its
# own label at the right end of the line. Merge the ~0 cells into one gray line.
CELL_ROWS = [
    ("self_peer", BLUE, "self-judge, peer pool"),
    ("cautious_mixed", GREEN, "cautious-copy judge"),
    ("base_pool", GRAY, "base / frozen judges"),
    ("self_duel_base", VIOLET, "self-judge duels, base text"),
    ("oracle", RED, "score oracle"),
]
for name, color, lab in CELL_ROWS:
    c = CELLS[name]
    mbr = [(rd, v) for rd, v in c["mean_by_round"] if rd <= 4]
    pts = [(X(rd), Y(v)) for rd, v in mbr]
    # faint individual runs behind
    for t in c["runs"]:
        if t is not BLOOM and len(t) > 1:
            b.append(poly([(X(rd), Y(v)) for rd, v in t if rd <= 4], color, 1.4, op=0.16))
    b.append(poly(pts, color))
    b.append(dots(pts, color))
    ex, ey = pts[-1]
    m = c["mean"]
    val = f"+{m:.2f}" if m >= 0.005 else f"−{abs(m):.2f}"
    # nudge the two close positive labels apart
    ly = ey + (-11 if name == "self_peer" else (11 if name == "cautious_mixed" else 0))
    b.append(f'<line x1="{ex + 8:.1f}" y1="{ey:.1f}" x2="{LABX - 8}" y2="{ly:.1f}" '
             f'stroke="{color}" stroke-width="1" stroke-opacity="0.5"/>')
    b.append(ctext(LABX, ly + 5, f"{lab}  (ρ = {val})", 15.5, color, "bold",
                   "start"))

# the one exception: a base-judge run that rose mid-run (a bloom), then fell —
# drawn faint; described in the caption, not labeled in-plot.
bloom_pts = [(X(rd), Y(v)) for rd, v in BLOOM if rd <= 4]
b.append(poly(bloom_pts, GRAY, 1.8, dash="5 4", op=0.7))

# the one key stat
b.append(box(PX, PY - 2, 372, 30, KEY_FILL, INK, 1.6, rx=8))
b.append(ctext(PX + 12, PY + 18, f"{BETWEEN * 100:.0f}% of agreement's variance is "
               "between judge setups, not rounds", 15.5, INK, "bold", "start"))

svg = svg_doc(W, H, "\n".join(b))
out = os.path.join(HERE, "two-clocks-spread-util.svg")
with open(out, "w") as f:
    f.write(svg)
print("wrote", out)

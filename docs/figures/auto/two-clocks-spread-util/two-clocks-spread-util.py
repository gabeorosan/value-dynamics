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
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
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
# layout
# ------------------------------------------------------------------
W, H = 1560, 795
PY, PH = 240, 380
LX, LW = 110, 470     # left plot
RX, RW = 730, 470     # right plot
LABX = 1212           # right-panel label column

b = []
b.append(ctext(W / 2, 128, "The two dials change on different clocks", 31, weight="bold"))


def Xl(rd):
    return LX + LW * (rd - 1) / 7


def Xr(rd):
    return RX + RW * (rd - 1) / 7


def Yl(v):   # spread, 0 .. 0.46
    return PY + PH * (0.46 - v) / 0.46


def Yr(v):   # rho, -1.05 .. +1.05
    return PY + PH * (1.05 - v) / 2.1


def poly(pts, color, sw=3.5, dash=None, op=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op < 1 else ""
    return (f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" '
            f'fill="none" stroke="{color}" stroke-width="{sw}"{d}{o}/>')


def dots(pts, color, r=4.5):
    return "\n".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" '
                     f'stroke="white" stroke-width="1.5"/>' for x, y in pts)


# ------------------------------------------------------------------
# LEFT panel — spread is a dynamic
# ------------------------------------------------------------------
b.append(ctext(LX, 172, "Spread σ is spent and refilled (a dynamic)", 20,
               weight="bold", anchor="start"))
b.append(ctext(LX, 196, "mean spread of the candidate pool per round, OLMo-family runs "
               "(one line per pool composition)", 14.5, GRAY, anchor="start"))

for v in (0, 0.1, 0.2, 0.3, 0.4):
    yy = Yl(v)
    b.append(f'<line x1="{LX}" y1="{yy:.1f}" x2="{LX + LW}" y2="{yy:.1f}" stroke="{GRID}" stroke-width="1"/>')
    b.append(ctext(LX - 10, yy + 5.5, f"{v:g}", 15, GRAY, anchor="end"))
for rd in range(1, 9):
    b.append(ctext(Xl(rd), PY + PH + 26, str(rd), 15.5, INK))
b.append(ctext(LX + LW / 2, PY + PH + 56, "round", 17))
b.append(f'<text x="{LX - 62}" y="{PY + PH / 2}" font-size="17" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {LX - 62} {PY + PH / 2})" text-anchor="middle">candidate value spread σ</text>')

SPREAD = {
    "self-only": (BLUE, LEDGER["OLMo/self-only"]["mean_spread_by_round"]),
    "base-mixed": (GREEN, LEDGER["OLMo/base-mixed"]["mean_spread_by_round"]),
    "peer-mixed": (RED, LEDGER["OLMo/peer-mixed"]["mean_spread_by_round"]),
}
for name, (color, byround) in SPREAD.items():
    pts = [(Xl(int(rd)), Yl(v)) for rd, v in sorted(byround.items(), key=lambda kv: int(kv[0]))]
    b.append(poly(pts, color))
    b.append(dots(pts, color))

sp = {k: {int(r): v for r, v in v[1].items()} for k, v in SPREAD.items()}
b.append(ctext(330, 282, f"base-mixed pool: {sp['base-mixed'][1]:.2f} → {sp['base-mixed'][4]:.2f}",
               15.5, GREEN, "bold", "start"))
b.append(ctext(330, 301, "the base supplier refills spread", 15, GREEN, anchor="start"))
b.append(ctext(384, 458, f"self-only pool: {sp['self-only'][1]:.2f} → {sp['self-only'][8]:.2f}",
               15.5, BLUE, "bold", "start"))
b.append(ctext(384, 477, "spread persists, then slowly sags", 15, BLUE, anchor="start"))
b.append(ctext(340, 546, "peer-mixed pool (extremist invader):", 15.5, RED, "bold", "start"))
b.append(ctext(340, 565, f"spread collapses, {sp['peer-mixed'][1]:.2f} → {sp['peer-mixed'][4]:.2f}",
               15.5, RED, "bold", "start"))

# ------------------------------------------------------------------
# RIGHT panel — agreement is a property
# ------------------------------------------------------------------
b.append(ctext(RX, 172, "Agreement ρ holds within a run (a property)", 20,
               weight="bold", anchor="start"))
b.append(f'<text x="{RX}" y="196" font-size="14.5" font-family="{FONT}">'
         f'<tspan fill="{GRAY}">fat line = per-round cell mean, faint lines = single runs · '
         f'label = cell mean (within-run SD) · </tspan>'
         f'<tspan fill="{BLUE}" font-weight="bold">self-judge</tspan>'
         f'<tspan fill="{GRAY}"> · </tspan>'
         f'<tspan fill="{GREEN}" font-weight="bold">frozen judge</tspan>'
         f'<tspan fill="{GRAY}"> · </tspan>'
         f'<tspan fill="{RED}" font-weight="bold">oracle</tspan></text>')

for v in (-1, -0.5, 0, 0.5, 1):
    yy = Yr(v)
    b.append(f'<line x1="{RX}" y1="{yy:.1f}" x2="{RX + RW}" y2="{yy:.1f}" stroke="{GRID}" stroke-width="1"/>')
    lab = f"+{v:g}" if v > 0 else f"−{abs(v):g}" if v < 0 else "0"
    b.append(ctext(RX - 10, yy + 5.5, lab, 15, GRAY, anchor="end"))
zy = Yr(0)
b.append(f'<line x1="{RX}" y1="{zy:.1f}" x2="{RX + RW}" y2="{zy:.1f}" stroke="{INK}" '
         f'stroke-width="1.5" stroke-dasharray="6 5"/>')
b.append(ctext(RX + RW - 4, zy + 20, "ρ = 0: the judge ignores value", 13.5, INK, anchor="end"))
for rd in range(1, 9):
    b.append(ctext(Xr(rd), PY + PH + 26, str(rd), 15.5, INK))
b.append(ctext(RX + RW / 2, PY + PH + 56, "round", 17))
b.append(f'<text x="{RX - 62}" y="{PY + PH / 2}" font-size="17" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {RX - 62} {PY + PH / 2})" text-anchor="middle">judge agreement ρ</text>')

# faint individual runs first (skip the bloom run, drawn separately)
CELL_COLOR = {"oracle": RED, "self_duel_base": BLUE, "cautious_mixed": GREEN,
              "self_peer": BLUE, "candid": BLUE, "base_pool": GREEN, "frozen_copy": GREEN}
for name, c in CELLS.items():
    for t in c["runs"]:
        if t == BLOOM:
            continue
        if len(t) > 1:
            b.append(poly([(Xr(rd), Yr(v)) for rd, v in t], CELL_COLOR[name], 1.4, op=0.25))

# fat per-round cell means (base cell fat line only over rounds 1-4, where
# 17+ runs report; two 8-round runs continue faintly behind)
for name, c in CELLS.items():
    mbr = [(rd, v) for rd, v in c["mean_by_round"] if not (name == "base_pool" and rd > 4)]
    pts = [(Xr(rd), Yr(v)) for rd, v in mbr]
    b.append(poly(pts, CELL_COLOR[name]))
    b.append(dots(pts, CELL_COLOR[name]))

# the bloom — the one run whose agreement moved mid-run
bloom_pts = [(Xr(rd), Yr(v)) for rd, v in BLOOM]
b.append(poly(bloom_pts, RED, 2, dash="5 4", op=0.9))
b.append(dots(bloom_pts, RED, 3))
bx, by = bloom_pts[2]
b.append(f'<line x1="1000" y1="497" x2="{bx + 5:.1f}" y2="{by + 6:.1f}" '
         f'stroke="{RED}" stroke-width="1.2"/>')
b.append(ctext(958, 514, "the one exception (a bloom):", 14, RED, "bold", "start"))
b.append(ctext(958, 532, "one base-judge run rose mid-run,", 14, RED, anchor="start"))
b.append(ctext(958, 550, f"ρ {BLOOM[0][1]:.2f} → {max(v for _, v in BLOOM):.2f}, "
               "then fell back", 14, RED, anchor="start"))

# takeaway box + label column
b.append(box(LABX, 236, 338, 66, KEY_FILL, INK, 2))
t, _ = text_block(LABX + 14, 262, f"{BETWEEN * 100:.0f}% of agreement’s variance is "
                  "between judge cells, not between rounds.", 15.5, 40, INK, "bold")
b.append(t)


def fmt(c, sd=True):
    m = c["mean"]
    s = f"+{m:.2f}" if m >= 0.005 else f"−{abs(m):.2f}"
    if sd and c["wsd"] is not None:
        s += f" ({c['wsd']:.2f})"
    return s


LABELS = [  # (cell, label text, label y, color, sd?)
    ("self_peer", "self-judge, extremist peer invasion", 340, BLUE, True),
    ("cautious_mixed", "cautious copy judge, mixed pool", 365, GREEN, True),
    ("candid", "candid-prompt self-judge", 390, BLUE, False),
    ("base_pool", "base judge, non-invasion pools", 416, GREEN, True),
    ("frozen_copy", "frozen copy judge", 440, GREEN, True),
    ("self_duel_base", "self-judge duels with base text", 477, BLUE, True),
    ("oracle", "score oracle, keeps the low side", 608, RED, True),
]
for name, lab, ly, color, sd in LABELS:
    c = CELLS[name]
    mbr = [(rd, v) for rd, v in c["mean_by_round"] if not (name == "base_pool" and rd > 4)]
    ex, ey = Xr(mbr[-1][0]), Yr(mbr[-1][1])
    b.append(f'<line x1="{ex + 8:.1f}" y1="{ey:.1f}" x2="{LABX - 6}" y2="{ly - 5}" '
             f'stroke="{GRAY}" stroke-width="1" stroke-opacity="0.7"/>')
    b.append(ctext(LABX, ly, f"{lab}  {fmt(c, sd)}", 15, color, "bold", "start"))

# ------------------------------------------------------------------
# footnote
# ------------------------------------------------------------------
t, _ = text_block(LX, 722, "ρ = within-item correlation between the judge’s candidate "
                  "scores and the candidates’ value scores (−1 keeps the low-value side "
                  "… +1 keeps the high side). σ = standard deviation of the candidate "
                  "value scores in the round’s pool. 340 score-logged rounds across 74 runs; "
                  "within-run SD averaged over the cell’s runs.", 15, 168, GRAY)
b.append(t)

svg = svg_doc(W, H, "\n".join(b))
out = os.path.join(HERE, "two-clocks-spread-util.svg")
with open(out, "w") as f:
    f.write(svg)
print("wrote", out)

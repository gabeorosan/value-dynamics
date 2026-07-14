#!/usr/bin/env python3
"""synthesis_state_space_trajectories — the mechanism phase plot.

Every training round of every intervention is plotted at its REAL coordinates:
  x = value spread  (prereg formula: mean over items of the within-item SD of the
      candidate value scores that round)
  y = the judge's pull = the selection gap (mean value of the kept answers minus
      the pool average), signed so that up = toward the target.
Neither axis is the value itself; the value is shown as the start/end labels and
by arrow thickness (how far the value moved that round). The point of the figure:
a value moves only when BOTH a spread exists (x > 0) AND the pull is aligned
(y > 0). Stuck runs sit at the origin; rescues/reversals ride the upper band;
contamination and the wasted-cautious pull sit below the zero line.

Coordinates come from experiments/state_space_coords.json, written by
scripts/analysis_state_space_coords.py (cross-checked against
report_crossfamily_oracle.md). Regenerate with:
  python3 synthesis_state_space_trajectories.py   (stdlib only)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE
ROOT = os.path.dirname(os.path.dirname(FIGDIR))
COORDS = os.path.join(ROOT, "experiments", "state_space_coords.json")

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
AMBER = "#c07d18"

FONT = "Helvetica, Arial, sans-serif"
BODY = 19

UPPER_FILL = "#edf4ee"   # aligned pull (toward target)
LOWER_FILL = "#f6efe7"   # pull the other way
STRIP_FILL = "#eef1f5"   # no variation (nothing to select)
OPEN_INK = "#2f6b39"
WRONG_INK = "#9a6a2e"

COLORS = {"green": GREEN, "red": RED, "gray": GRAY, "amber": AMBER, "blue": BLUE}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal", anchor="start", italic=False):
    st = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}"{st}>{esc(text)}</text>')


def lines_at(x, y, lines, size=BODY, color=INK, anchor="start", weight="normal", lh=1.2, italic=False):
    return "\n".join(ltext(x, y + i * size * lh, ln, size, color, weight, anchor, italic)
                     for i, ln in enumerate(lines))


def plate(x, y, text, size=19, anchor="start", color=INK, weight="bold"):
    w = len(text) * size * 0.60 + 12
    h = size + 8
    rx = x - 6 if anchor == "start" else (x - w + 6 if anchor == "end" else x - w / 2)
    return (f'<rect x="{rx:.1f}" y="{y - size + 2:.1f}" width="{w:.1f}" height="{h}" rx="6" '
            f'fill="white" fill-opacity="0.9"/>' + ltext(x, y, text, size, color, weight, anchor))


def arrow(x1, y1, x2, y2, w, color, dash=False):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    head = max(13.0, w * 1.7)
    half = head * 0.6
    bx, by = x2 - ux * head, y2 - uy * head
    px, py = -uy, ux
    p1 = (bx + px * half, by + py * half)
    p2 = (bx - px * half, by - py * half)
    da = ' stroke-dasharray="9 7"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{color}" '
            f'stroke-width="{w:.1f}" stroke-linecap="round"{da}/>'
            f'<polygon points="{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


# ---------------------------------------------------------------- geometry
W, H = 1560, 902
AX, AY, AW, AH = 214, 176, 852, 560
XMIN, XMAX = -0.02, 0.47
YMIN, YMAX = -0.36, 0.48


def xm(s):
    return AX + AW * (s - XMIN) / (XMAX - XMIN)


def ym(g):
    return AY + AH * (YMAX - g) / (YMAX - YMIN)


def W_OF(drift):
    return 2.4 + 12.0 * min(drift, 0.7)


data = json.load(open(COORDS))

# Six interventions, numbered. Each: (n, colour-role, line1, line2 with value move),
# and BADGE = the pixel spot to drop the numbered marker (tuned to sit on a clear
# part of that path). Descriptions live in the right-hand key, not in the plot.
KEY = [
    (1, "rail_inert", "gray", "second risk model — stuck rail", "answers all alike · 1.000 (no variation)"),
    (2, "reopen", "blue", "insecure-code model — injection reopens it", "0.627 → 0.000 · self-report axis"),
    (3, "reversal", "green", "second risk model — a score oracle", "walks it down · 0.917 → 0.094"),
    (4, "rescue", "green", "mixed-pool rescue — lots of material", "noisy landing · 1.000 → 0.484"),
    (5, "cautious", "amber", "a cautious judge — material present", "but pulls the wrong way · 0.875 → 0.716"),
    (6, "contamination", "red", "a maxed-out copy added", "one big wrong-way jump · 0.363 → 1.000"),
]
NUM = {rid: n for n, rid, *_ in KEY}
CROLE = {rid: crole for n, rid, crole, *_ in KEY}
BADGE = {"rail_inert": (250, 470), "reopen": (840, 298), "reversal": (596, 400),
         "rescue": (992, 224), "cautious": (748, 527), "contamination": (1046, 662)}
ORDER = ["rail_inert", "cautious", "contamination", "reversal", "rescue", "reopen"]

b = []

# ---- title ----
b.append(ctext(W // 2, 48, "A value moves only with both variation and an aligned pull", 31, INK, "bold"))
b.append(ctext(W // 2, 82,
               "Every training round at its real (value spread, selection gap); each point computed from that round's raw candidate answers.",
               BODY, GRAY))
b.append(ctext(W // 2, 108,
               "Arrow thickness = how far the value moved that round; each intervention is numbered, with its value change in the key at right.",
               16, GRAY))

# ---- regions ----
y0 = ym(0.0)
xstrip = xm(0.05)
b.append(f'<rect x="{AX}" y="{AY}" width="{AW}" height="{y0 - AY:.1f}" fill="{UPPER_FILL}"/>')
b.append(f'<rect x="{AX}" y="{y0:.1f}" width="{AW}" height="{AY + AH - y0:.1f}" fill="{LOWER_FILL}"/>')
b.append(f'<rect x="{AX}" y="{AY}" width="{xstrip - AX:.1f}" height="{AH}" fill="{STRIP_FILL}" fill-opacity="0.75"/>')
b.append(f'<line x1="{xstrip:.1f}" y1="{AY}" x2="{xstrip:.1f}" y2="{AY + AH}" stroke="#cdd3da" stroke-width="1.5" stroke-dasharray="4 5"/>')

# region captions (kept minimal, in the clear left band)
b.append(ltext(xm(0.06), AY + 30, "↑ pull toward the target", 17, OPEN_INK, italic=True))
b.append(ltext(xm(0.06), AY + AH - 14, "↓ pull the other way", 17, WRONG_INK, italic=True))
b.append(f'<text x="328" y="{AY + AH / 2:.1f}" font-size="15" fill="{GRAY}" font-family="{FONT}" font-style="italic" '
         f'transform="rotate(-90 328 {AY + AH / 2:.1f})" text-anchor="middle">no variation — nothing to select</text>')

# ---- axes: gridlines + numeric ticks (positions ARE the data now) ----
for g in (0.4, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.3):
    yy = ym(g)
    w = 2.0 if g == 0.0 else 1.0
    col = "#8f96a0" if g == 0.0 else "#e6e9ec"
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{w}"/>')
    lab = "0" if g == 0.0 else f"{'+' if g > 0 else '−'}{abs(g):.1f}"
    b.append(ltext(AX - 12, yy + 5, lab, 16, GRAY, anchor="end"))
for s in (0.0, 0.1, 0.2, 0.3, 0.4):
    xx = xm(s)
    b.append(f'<line x1="{xx:.1f}" y1="{AY}" x2="{xx:.1f}" y2="{AY + AH}" stroke="#eef0f2" stroke-width="1"/>')
    b.append(ctext(xx, AY + AH + 26, f"{s:.1f}", 16, GRAY))
b.append(f'<line x1="{AX}" y1="{AY}" x2="{AX}" y2="{AY + AH}" stroke="{GRAY}" stroke-width="1.5"/>')
b.append(f'<line x1="{AX}" y1="{AY + AH}" x2="{AX + AW}" y2="{AY + AH}" stroke="{GRAY}" stroke-width="1.5"/>')
b.append(f'<text x="{AX + AW - 8}" y="{y0 - 8:.1f}" text-anchor="end" font-size="{BODY}" fill="{GRAY}" font-family="{FONT}">gap = 0 · no pull (kept ≈ pool)</text>')

# x title
b.append(ctext(AX + AW / 2, AY + AH + 56, "value spread", 22, INK, "bold"))
b.append(ctext(AX + AW / 2, AY + AH + 80, "how much the candidate answers vary that round (within-item SD)", 16, GRAY))
# y title
ymid = AY + AH / 2
b.append(f'<text x="150" y="{ymid:.1f}" font-size="{BODY}" font-weight="bold" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 150 {ymid:.1f})" text-anchor="middle">the judge’s pull = the selection gap</text>')
b.append(f'<text x="128" y="{ymid:.1f}" font-size="15" fill="{GRAY}" font-family="{FONT}" '
         f'transform="rotate(-90 128 {ymid:.1f})" text-anchor="middle">kept answers’ average − pool average, signed toward the target</text>')


# ---- trajectories ----
def dedupe(pts):
    """collapse consecutive identical (spread,gap) points, keep drift of the leaver."""
    out = []
    for p in pts:
        xy = (round(p["spread"], 4), round(p["gap_signed"], 4))
        if out and (round(out[-1]["spread"], 4), round(out[-1]["gap_signed"], 4)) == xy:
            continue
        out.append(p)
    return out


def node(x, y, color, s=6.5):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s}" fill="{color}" stroke="white" stroke-width="1.6"/>'


def badge(x, y, n, color):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12.5" fill="white" stroke="{color}" stroke-width="2.6"/>'
            + ctext(x, y + 6, str(n), 17, color, "bold"))


for rid in ORDER:
    run = data[rid]
    color = COLORS[CROLE[rid]]
    pts = dedupe(run["rounds"])
    xy = [(xm(p["spread"]), ym(p["gap_signed"])) for p in pts]
    # segments (thickness = drift of the tail round; dashed for the injection step
    # into a fresh-supply round, i.e. spread jumps from ~0)
    for i in range(len(pts) - 1):
        x1, y1 = xy[i]
        x2, y2 = xy[i + 1]
        inj = pts[i]["spread"] < 0.02 and pts[i + 1]["spread"] > 0.05
        wdt = 3.0 if inj else W_OF(pts[i + 1]["drift"])
        b.append(arrow(x1, y1, x2, y2, wdt, GRAY if inj else color, dash=inj))
    for (x, y) in xy:
        b.append(node(x, y, color))
    bx, by = BADGE[rid]
    b.append(badge(bx, by, NUM[rid], color))

# ---------------------------------------------------------------- right key + legend
LX = 1104
b.append(ltext(LX, 190, "the six interventions", 20, INK, weight="bold"))
ky = 216
for n, rid, crole, l1, l2 in KEY:
    col = COLORS[crole]
    b.append(f'<circle cx="{LX + 13}" cy="{ky + 8:.1f}" r="12.5" fill="white" stroke="{col}" stroke-width="2.6"/>')
    b.append(ctext(LX + 13, ky + 14, str(n), 16, col, "bold"))
    b.append(ltext(LX + 36, ky + 6, l1, 17, INK, weight="bold"))
    b.append(ltext(LX + 36, ky + 27, l2, 15, GRAY))
    ky += 50
b.append(ltext(LX, ky + 8, "green/blue = moved the intended way (blue = self-report", 14, GRAY))
b.append(ltext(LX, ky + 26, "axis) · amber = wrong-way, barely · red = other way · grey = stuck", 14, GRAY))

ky += 62
b.append(ltext(LX, ky, "thickness = how far the value moved that round", 17, INK, weight="bold"))
for i, (wd, cap) in enumerate([(3.5, "barely"), (8.0, "a lot"), (13.0, "nearly all the way")]):
    yy = ky + 30 + i * 32
    b.append(arrow(LX + 4, yy - 6, LX + 74, yy - 6, wd, GRAY))
    b.append(ltext(LX + 88, yy, cap, 16, INK))
ky += 30 + 3 * 32 + 8
b.append(ltext(LX, ky, "dashed = outside answers injected (raises spread)", 17, INK, weight="bold"))
b.append(arrow(LX + 4, ky + 26, LX + 74, ky + 26, 3.0, GRAY, dash=True))
b.append(ltext(LX + 88, ky + 31, "the injection step", 16, INK))

svg = svg_doc(W, H, "\n".join(b))
with open(os.path.join(FIGDIR, "synthesis_state_space_trajectories.svg"), "w") as f:
    f.write(svg)
print("wrote synthesis_state_space_trajectories.svg")

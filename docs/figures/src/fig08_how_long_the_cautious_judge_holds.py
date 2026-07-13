#!/usr/bin/env python3
"""fig08 — a short cautious phase doesn't stop the rebound.

The gambling model (trained to prefer a risky gamble) is pushed by a cautious
judge for the first 1, 2, or 3 rounds, then handed to a neutral judge for the
rest of an 8-round run, two independent runs per cautious-phase length. At
every length tested, one run climbs back to the top and one stays low.

Regenerate with:  python3 fig08_how_long_the_cautious_judge_holds.py   (stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

DATA_DIR = os.path.join(ROOT, "experiments", "modal_k2_release", "output")

INK = "#1a1a1a"
PURPLE = "#8a5a9e"
GREEN = "#3a7d44"
GRAY = "#6b7684"
STRIP_FILL = "#eef2f6"

FONT = "Helvetica, Arial, sans-serif"

# minimum readable body font
BODY = 19


# ------------------------------------------------------------ house helpers
# (copied verbatim from fig05_selection_gap_predicts_drift.py)
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


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4):
    lines = wrap(text, width)
    svg = []
    for i, ln in enumerate(lines):
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def protocol_strip(cx, y, steps, bw=222, bh=54, gap=44):
    """One horizontal row of small labelled boxes with arrows between."""
    out = []
    n = len(steps)
    total = n * bw + (n - 1) * gap
    x = cx - total / 2
    for i, label in enumerate(steps):
        out.append(box(x, y, bw, bh, STRIP_FILL, GRAY, 1.5, rx=10))
        lines = wrap(label, int(bw / 9.5))
        ly = y + bh / 2 - (len(lines) - 1) * 10 + 6.5
        for j, ln in enumerate(lines):
            out.append(ctext(x + bw / 2, ly + j * 20, ln, BODY, INK))
        if i < n - 1:
            out.append(f'<text x="{x + bw + gap / 2:.1f}" y="{y + bh / 2 + 9:.1f}" '
                       f'text-anchor="middle" font-size="26" fill="{GRAY}" font-family="{FONT}">&#8594;</text>')
        x += bw + gap
    return "\n".join(out)


# ---------------------------------------------------------------- data
CELLS = [  # (cautious-phase length in rounds, run id, filename, condition-key)
    (1, "1", "k2rel_press_d1_s1.json", "press_d1"),
    (1, "2", "k2rel_press_d1_s2.json", "press_d1"),
    (2, "1", "k2rel_press_d2_s1.json", "press_d2"),
    (2, "2", "k2rel_press_d2_s2.json", "press_d2"),
    (3, "1", "k2rel_press_d3_s1.json", "press_d3"),
    (3, "2", "k2rel_press_d3_s2.json", "press_d3"),
]

cell = {}
for length, run, fname, cond in CELLS:
    d = json.load(open(os.path.join(DATA_DIR, fname)))
    rec = d[run][cond]
    traj = rec["traj"]
    assert len(traj) == 9, f"{fname}: expected r0..r8 (9 points), got {len(traj)}"
    cell[(length, run)] = dict(traj=traj, r8=traj[8])

# sanity check against the recorded per-round trajectories this figure claims
_expect_traj = {
    (1, "1"): [0.308, 0.333, 0.083, 0.375, 0.208, 0.000, 0.000, 0.042, 0.000],
    (1, "2"): [0.301, 0.429, 0.625, 0.542, 0.583, 0.417, 0.667, 1.000, 1.000],
    (2, "1"): [0.308, 0.208, 0.167, 0.125, 0.042, 0.000, 0.167, 0.083, 0.105],
    (2, "2"): [0.301, 0.391, 0.417, 0.609, 0.708, 0.958, 0.875, 1.000, 0.938],
    (3, "1"): [0.308, 0.292, 0.208, 0.000, 0.083, 0.333, 0.417, 0.125, 0.229],
    (3, "2"): [0.301, 0.292, 0.208, 0.292, 0.417, 0.542, 0.667, 0.625, 0.823],
}
for k, exp in _expect_traj.items():
    got = [round(v, 3) for v in cell[k]["traj"]]
    assert got == exp, f"{k}: traj mismatch, expected {exp} got {got}"

RANGES = {}
for length in (1, 2, 3):
    lo = cell[(length, "1")]["r8"]
    hi = cell[(length, "2")]["r8"]
    RANGES[length] = (lo, hi, hi - lo)

# run "1" ends low and run "2" ends high at every length tested
LOW_RUN, HIGH_RUN = "1", "2"

# ------------------------------------------------------------------ figure
b = []
W = 1370

b.append(ctext(W / 2, 52, "A short cautious phase doesn't stop the rebound", 30, INK, "bold"))
b.append(ctext(W / 2, 86,
    "The gambling model, trained to prefer a risky gamble, is pushed by a cautious judge for 1–3 rounds, "
    "then a neutral judge for the rest of 8 rounds.", BODY, GRAY))

b.append(protocol_strip(W / 2, 118, [
    "cautious judge for 1-3 rounds",
    "switch to a neutral judge",
    "continue to round 8",
    "measure risk each round",
]))

# shared legend: same color throughout (one experimental setup), weight/opacity
# distinguishes the run that climbs back up from the run that stays low; the
# cautious-judge phase is marked by the shaded region, explained here once
LEG_Y = 216
b.append(f'<line x1="145" y1="{LEG_Y}" x2="205" y2="{LEG_Y}" stroke="{PURPLE}" stroke-width="4.5"/>')
b.append(f'<text x="217" y="{LEG_Y+6}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">the run that climbs back up</text>')
b.append(f'<line x1="540" y1="{LEG_Y}" x2="590" y2="{LEG_Y}" stroke="{PURPLE}" stroke-width="2.5" stroke-opacity="0.4"/>')
b.append(f'<text x="602" y="{LEG_Y+6}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" fill-opacity="0.75">the run that stays low</text>')
b.append(f'<rect x="875" y="{LEG_Y-11}" width="16" height="16" fill="{GREEN}" fill-opacity="0.10" stroke="{GREEN}" stroke-width="1.5"/>')
b.append(f'<text x="899" y="{LEG_Y+6}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">cautious-judge rounds (shaded)</text>')

# ================= three panels: cautious-phase length 1, 2, 3 =================
LEFT = 110
PANEL_W, GAP = 350, 60
PLOT_W = 290
PX = [LEFT, LEFT + PANEL_W + GAP, LEFT + 2 * (PANEL_W + GAP)]
PY, PH = 296, 246
LETTERS = ["A", "B", "C"]

for i, length in enumerate((1, 2, 3)):
    px = PX[i]

    def ax(r, px=px):
        return px + PLOT_W * r / 8

    def ay(v):
        return PY + PH * (1 - v)

    lo_rec = cell[(length, LOW_RUN)]
    hi_rec = cell[(length, HIGH_RUN)]
    plural = "round" if length == 1 else "rounds"

    b.append(f'<text x="{px}" y="264" font-size="22" font-weight="bold" fill="{INK}" font-family="{FONT}">{LETTERS[i]}. Cautious judge for {length} {plural}</text>')

    # cautious-phase shading (rounds 0..length are on the cautious judge)
    b.append(f'<rect x="{ax(0):.1f}" y="{PY}" width="{ax(length)-ax(0):.1f}" height="{PH}" '
              f'fill="{GREEN}" fill-opacity="0.10"/>')
    b.append(f'<line x1="{ax(length):.1f}" y1="{PY}" x2="{ax(length):.1f}" y2="{PY+PH}" '
              f'stroke="{INK}" stroke-width="1.6" stroke-dasharray="5 4"/>')
    b.append(f'<text x="{ax(length):.1f}" y="{PY - 8}" text-anchor="middle" font-size="14" '
              f'fill="{INK}" font-family="{FONT}">switch to neutral</text>')

    # gridlines
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = ay(v)
        b.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px+PLOT_W}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
        if i == 0:
            b.append(f'<text x="{px-10}" y="{yy+5:.1f}" text-anchor="end" font-size="16" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    for r in range(9):
        b.append(f'<text x="{ax(r):.1f}" y="{PY+PH+24}" text-anchor="middle" font-size="15" fill="{GRAY}" font-family="{FONT}">{r}</text>')
    b.append(f'<text x="{px+PLOT_W/2:.1f}" y="{PY+PH+46}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">round</text>')
    if i == 0:
        b.append(f'<text x="{LEFT-64}" y="{PY+PH/2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
                  f'transform="rotate(-90 {LEFT-64} {PY+PH/2})" text-anchor="middle">how risk-seeking the pool is</text>')

    # trajectories — same color, weight/opacity distinguishes the two runs
    pts_lo = " ".join(f"{ax(r):.1f},{ay(v):.1f}" for r, v in enumerate(lo_rec["traj"]))
    b.append(f'<polyline points="{pts_lo}" fill="none" stroke="{PURPLE}" stroke-width="2.5" stroke-opacity="0.4"/>')
    for r, v in enumerate(lo_rec["traj"]):
        b.append(f'<circle cx="{ax(r):.1f}" cy="{ay(v):.1f}" r="4" fill="{PURPLE}" fill-opacity="0.4"/>')

    pts_hi = " ".join(f"{ax(r):.1f},{ay(v):.1f}" for r, v in enumerate(hi_rec["traj"]))
    b.append(f'<polyline points="{pts_hi}" fill="none" stroke="{PURPLE}" stroke-width="4.5"/>')
    for r, v in enumerate(hi_rec["traj"]):
        b.append(f'<circle cx="{ax(r):.1f}" cy="{ay(v):.1f}" r="5" fill="{PURPLE}" stroke="white" stroke-width="1.3"/>')

    # endpoint labels (offset so the two never collide)
    b.append(f'<text x="{ax(8)+8:.1f}" y="{ay(hi_rec["r8"])-8:.1f}" font-size="15" font-weight="bold" fill="{PURPLE}" font-family="{FONT}">{hi_rec["r8"]:.3f}</text>')
    b.append(f'<text x="{ax(8)+8:.1f}" y="{ay(lo_rec["r8"])+18:.1f}" font-size="15" fill="{PURPLE}" fill-opacity="0.7" font-family="{FONT}">{lo_rec["r8"]:.3f}</text>')

PANEL_BLOCK_BOTTOM = PY + PH + 46 + 24  # bottom of the round-axis label + margin

# ================= D. the round-8 spread across cautious-phase lengths =================
FY_TITLE = PANEL_BLOCK_BOTTOM + 30
b.append(f'<text x="{LEFT}" y="{FY_TITLE}" font-size="22" font-weight="bold" fill="{INK}" font-family="{FONT}">D. One run climbs, one stays low, at every length tested</text>')

DX0, DW = 300, 900
DY0, ROWH = FY_TITLE + 56, 66

def dx(v):
    return DX0 + DW * v

for i, length in enumerate((1, 2, 3)):
    yc = DY0 + i * ROWH
    lo, hi, rng = RANGES[length]
    plural = "round" if length == 1 else "rounds"
    b.append(f'<line x1="{dx(0):.1f}" y1="{yc}" x2="{dx(1):.1f}" y2="{yc}" stroke="#e4e4e0" stroke-width="1.5"/>')
    b.append(f'<line x1="{dx(lo):.1f}" y1="{yc}" x2="{dx(hi):.1f}" y2="{yc}" stroke="{PURPLE}" stroke-width="5" stroke-opacity="0.55"/>')
    b.append(f'<circle cx="{dx(lo):.1f}" cy="{yc}" r="8" fill="{PURPLE}" fill-opacity="0.4"/>')
    b.append(f'<circle cx="{dx(hi):.1f}" cy="{yc}" r="9" fill="{PURPLE}"/>')
    b.append(f'<text x="{dx(lo):.1f}" y="{yc+26}" text-anchor="middle" font-size="15" fill="{PURPLE}" fill-opacity="0.75" font-family="{FONT}">{lo:.3f}</text>')
    b.append(f'<text x="{dx(hi):.1f}" y="{yc-16}" text-anchor="middle" font-size="15" font-weight="bold" fill="{PURPLE}" font-family="{FONT}">{hi:.3f}</text>')
    b.append(f'<text x="{DX0-20}" y="{yc+6}" text-anchor="end" font-size="{BODY}" font-weight="bold" fill="{INK}" font-family="{FONT}">cautious for {length} {plural}</text>')

# x-axis for the fan
FAX_Y = DY0 + 2 * ROWH + 36
for v in (0.0, 0.25, 0.5, 0.75, 1.0):
    xx = dx(v)
    b.append(f'<line x1="{xx:.1f}" y1="{FAX_Y-6}" x2="{xx:.1f}" y2="{FAX_Y+6}" stroke="{INK}" stroke-width="2"/>')
    b.append(f'<text x="{xx:.1f}" y="{FAX_Y+26}" text-anchor="middle" font-size="16" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
b.append(f'<line x1="{dx(0):.1f}" y1="{FAX_Y}" x2="{dx(1):.1f}" y2="{FAX_Y}" stroke="{INK}" stroke-width="2"/>')
b.append(ctext(DX0 + DW / 2, FAX_Y + 50, "how risk-seeking the pool is at round 8", BODY, INK))

fan_bottom = FAX_Y + 66

# ================= one short caption =================
cap, cap_end = text_block(W / 2, fan_bottom + 34,
    "A longer cautious phase narrows the gap between the two runs, but never closes it.",
    BODY, 92, GRAY)
b.append(cap.replace('<text ', '<text text-anchor="middle" ', 1))

svg = svg_doc(W, cap_end + 30, "\n".join(b))
with open(os.path.join(FIGDIR, "fig08_how_long_the_cautious_judge_holds.svg"), "w") as f:
    f.write(svg)
print(f"wrote fig08_how_long_the_cautious_judge_holds.svg")
for length in (1, 2, 3):
    lo, hi, rng = RANGES[length]
    print(f"  cautious for {length} round(s): r8 lo={lo:.3f} hi={hi:.3f} range={rng:.3f}")

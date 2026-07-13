#!/usr/bin/env python3
"""synthesis_entropy_predictive_ablation — entropy changes the generator, but does
not improve next-round drift prediction.

Two panels of held-out prediction error (RMSE of next-round signed drift; lower is
better). Panel A: leave-one-seed-out within each grid, four nested models. Panel B:
a temporal check — fit on the OLMo grid, score 140 later transitions without
refitting. Within every grid, adding token entropy barely moves the error; adding
the selection gap cuts it sharply, and entropy on top of the gap adds nothing
consistent.

Numbers transcribed from docs/figure_brief_entropy_predictive_update.md (sourced
from experiments/entropy_predictive_analysis.json). This is a post-hoc comparison;
it does not modify the frozen M2 predictor.

Regenerate with:  python3 synthesis_entropy_predictive_ablation.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
GRAY = "#6b7684"
BLUE = "#2867b5"
AMBER = "#c07d18"
PURPLE = "#8a5a9e"
PANEL = "#fbfcfd"
BORDER = "#dce2e8"
GRID = "#e7ebef"
FONT = "Helvetica, Arial, sans-serif"
BODY = 19

# the four nested models and their colours
COND = ["condition only", "+ entropy", "+ gap", "+ gap & entropy"]
COLORS = [GRAY, AMBER, BLUE, PURPLE]

# Panel A — leave-one-seed-out RMSE, four models per grid
GRIDS_A = [
    ("Qwen risk", [0.126, 0.134, 0.095, 0.091]),
    ("OLMo risk", [0.091, 0.094, 0.074, 0.076]),
    ("Qwen insecure-code", [0.064, 0.065, 0.050, 0.050]),
]
# Panel B — temporal check: fit on the OLMo grid, score 140 later transitions
B_DATA = [0.0856, 0.0844, 0.0558, 0.0576]

YMAX = 0.15


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


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=BORDER, sw=1.6, rx=14):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def bar(x, y, w, h, color):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" fill="{color}"/>'


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


# ---------------------------------------------------------------- geometry
W = 1520
b = []

b.append(ctext(W / 2, 50, "Entropy changes the generator, but does not improve next-round drift prediction", 29, INK, "bold"))
b.append(ctext(W / 2, 84, "Held-out error when predicting each round's signed value change (RMSE, lower is better). "
                          "Each model adds one term to the last.", BODY, GRAY))

# ---- shared legend ----
leg_y = 122
sw_items = list(zip(COLORS, COND))
widths = [26 + len(t) * 10.4 for _, t in sw_items]
total = sum(widths) + 44 * (len(sw_items) - 1)
lx = W / 2 - total / 2
for (col, t), wd in zip(sw_items, widths):
    b.append(f'<rect x="{lx:.1f}" y="{leg_y - 15:.1f}" width="19" height="19" rx="4" fill="{col}"/>')
    b.append(ltext(lx + 27, leg_y, t, BODY, INK))
    lx += wd + 44

# ---- panel frames ----
PT, PB = 168, 604          # panel top / bottom
AX0, AXW = 46, 940         # panel A box
BX0, BXW = 1012, 462       # panel B box
b.append(box(AX0, PT, AXW, PB - PT, PANEL))
b.append(box(BX0, PT, BXW, PB - PT, PANEL))
b.append(ltext(AX0 + 26, PT + 34, "A.  Held out by seed, within each grid", 21, INK, "bold"))
b.append(ltext(BX0 + 26, PT + 34, "B.  Held out in time", 21, INK, "bold"))
b.append(ltext(BX0 + 26, PT + 58, "fit on the OLMo grid, score 140 later transitions", 16, GRAY))


def plot(px_l, px_r, py_b, py_t):
    """draw y-axis grid + ticks for an RMSE plot; return a value->y mapper."""
    def yv(v):
        return py_b - (py_b - py_t) * (v / YMAX)
    for tv in (0.00, 0.05, 0.10, 0.15):
        yy = yv(tv)
        b.append(f'<line x1="{px_l:.1f}" y1="{yy:.1f}" x2="{px_r:.1f}" y2="{yy:.1f}" '
                 f'stroke="{GRID}" stroke-width="1.2"/>')
        b.append(ltext(px_l - 10, yy + 5, f"{tv:.2f}", 15, GRAY, anchor="end"))
    b.append(f'<line x1="{px_l:.1f}" y1="{py_t:.1f}" x2="{px_l:.1f}" y2="{py_b:.1f}" stroke="{GRAY}" stroke-width="1.5"/>')
    b.append(f'<line x1="{px_l:.1f}" y1="{py_b:.1f}" x2="{px_r:.1f}" y2="{py_b:.1f}" stroke="{GRAY}" stroke-width="1.5"/>')
    return yv


# ---- Panel A: 3 grids x 4 bars ----
AXL, AXR = AX0 + 96, AX0 + AXW - 24
AYB, AYT = PB - 66, PT + 92
yvA = plot(AXL, AXR, AYB, AYT)
b.append(f'<text x="{AX0 + 30:.1f}" y="{(AYB + AYT) / 2:.1f}" text-anchor="middle" font-family="{FONT}" '
         f'font-size="15" fill="{GRAY}" transform="rotate(-90 {AX0 + 30:.1f} {(AYB + AYT) / 2:.1f})">RMSE of next-round drift</text>')

span = AXR - AXL
bw, gin = 44, 7
for gi, (glabel, vals) in enumerate(GRIDS_A):
    gc = AXL + span * (gi + 0.5) / 3
    start = gc - (4 * bw + 3 * gin) / 2
    for j, v in enumerate(vals):
        bx = start + j * (bw + gin)
        by = yvA(v)
        b.append(bar(bx, by, bw, AYB - by, COLORS[j]))
        b.append(ctext(bx + bw / 2, by - 7, f"{v:.3f}", 13.5, INK))
    b.append(ctext(gc, AYB + 26, glabel, 18, INK, "bold"))

# ---- Panel B: 4 bars ----
BXL, BXR = BX0 + 78, BX0 + BXW - 28
BYB, BYT = PB - 66, PT + 92
yvB = plot(BXL, BXR, BYB, BYT)
bspan = BXR - BXL
bbw = 56
bslot = bspan / 4
for j, v in enumerate(B_DATA):
    bcx = BXL + bslot * (j + 0.5)
    bx = bcx - bbw / 2
    by = yvB(v)
    b.append(bar(bx, by, bbw, BYB - by, COLORS[j]))
    b.append(ctext(bcx, by - 7, f"{v:.4f}", 13.5, INK))
b.append(ctext((BXL + BXR) / 2, BYB + 26, "OLMo grid → 140 later transitions", 16, INK, "bold"))

# ---- takeaway strip ----
tk_y = PB + 40
b.append(ctext(W / 2, tk_y, "Within every grid, adding entropy barely moves the error; adding the selection gap cuts it sharply.",
               21, INK, "bold"))

# ---- caption: what the numbers do and don't establish ----
cap_lines = [
    "Entropy alone improves none of the three seed-held-out grids. Added on top of the gap it changes RMSE by −3.4%, +3.4%, and −0.6% "
    "across the grids — no consistent incremental signal.",
    "The insecure-code grid measures entropy on insecurity-related prompts, the two risk grids on generic open prompts; compare models "
    "within a grid, not across. Post-hoc comparison — it does not modify the frozen predictor.",
]
cy = tk_y + 34
for s in cap_lines:
    for ln in wrap(s, 132):
        b.append(ctext(W / 2, cy, ln, 16, GRAY))
        cy += 23
    cy += 4

H = cy + 8
with open(os.path.join(FIGDIR, "synthesis_entropy_predictive_ablation.svg"), "w", encoding="utf-8") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print(f"wrote synthesis_entropy_predictive_ablation.svg  ({W}x{int(H)})")

#!/usr/bin/env python3
"""synthesis_entropy_longhorizon_supply — an early entropy lead appears in one grid
but does not transport.

Three panels asking whether generic token entropy is a leading indicator of the
candidate supply (target-axis spread) a few rounds later.
  A: one grid (the OLMo release grid, K2) — right after the first update, entropy
     lowers the held-out error for terminal spread two rounds on.
  B: across 20 longer OLMo release trajectories, adding entropy barely changes the
     error AND the fitted sign flips (higher entropy -> slightly LESS later spread),
     opposite the K2 early-state result; transporting the K2 model makes it worse.
  C: in no trajectory does generic entropy collapse before target-axis spread runs
     out — so entropy is not a necessary leading indicator either.

Numbers transcribed from docs/figure_brief_entropy_predictive_update.md (sourced
from experiments/entropy_long_horizon_analysis.json). Exploratory / post-hoc; does
not modify the frozen predictor.

Regenerate with:  python3 synthesis_entropy_longhorizon_supply.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
GRAY = "#6b7684"
AMBER = "#c07d18"
DKAMBER = "#8a5a1a"
GREEN = "#3a7d44"
RED = "#b5342c"
PANEL = "#fbfcfd"
BORDER = "#dce2e8"
GRIDL = "#e7ebef"
FONT = "Helvetica, Arial, sans-serif"
BODY = 19


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


def wlines(x, y, text, size, width, color=GRAY, weight="normal", lh=1.32, anchor="start"):
    out = []
    for i, ln in enumerate(wrap(text, width)):
        out.append(ltext(x, y + i * size * lh, ln, size, color, weight, anchor))
    return "\n".join(out), y + len(wrap(text, width)) * size * lh


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


def yaxis(px_l, px_r, py_b, py_t, ymax, ticks, unit):
    def yv(v):
        return py_b - (py_b - py_t) * (v / ymax)
    for tv in ticks:
        yy = yv(tv)
        b.append(f'<line x1="{px_l:.1f}" y1="{yy:.1f}" x2="{px_r:.1f}" y2="{yy:.1f}" stroke="{GRIDL}" stroke-width="1.2"/>')
        b.append(ltext(px_l - 9, yy + 5, f"{tv:{unit}}", 14, GRAY, anchor="end"))
    b.append(f'<line x1="{px_l:.1f}" y1="{py_t:.1f}" x2="{px_l:.1f}" y2="{py_b:.1f}" stroke="{GRAY}" stroke-width="1.5"/>')
    b.append(f'<line x1="{px_l:.1f}" y1="{py_b:.1f}" x2="{px_r:.1f}" y2="{py_b:.1f}" stroke="{GRAY}" stroke-width="1.5"/>')
    return yv


# ---------------------------------------------------------------- data
A_MODELS = ["current\nspread S", "S + entropy\nH", "S + entropy\nloss ΔH"]
A_VALS = [0.0953, 0.0833, 0.0751]
A_COLORS = [GRAY, AMBER, DKAMBER]

B_HORIZONS = ["1 round", "2 rounds", "3 rounds"]
B_S = [0.0817, 0.1096, 0.1306]
B_SH = [0.0812, 0.1085, 0.1302]
B_CHANGE = ["−0.6%", "−1.0%", "−0.3%"]
B_FOLDS = ["14/20", "14/20", "10/20"]

C_CATS = [
    (9, AMBER, "spread runs out while generic entropy stays above 25% of baseline"),
    (11, GRAY, "neither threshold is reached"),
    (0, RED, "generic entropy collapses before spread runs out"),
]

W = 1520
b = []

b.append(ctext(W / 2, 48, "An early entropy lead appears in one grid but does not transport", 29, INK, "bold"))
b.append(ctext(W / 2, 82, "Does generic token entropy forecast the candidate supply (target-axis spread) a few rounds later? "
                          "Held-out RMSE of that later spread; lower is better.", BODY, GRAY))

# ================= top row: Panel A (left) + Panel B (right) =================
PT, PB = 132, 556
AX0, AXW = 46, 452
BX0, BXW = 524, 950
b.append(box(AX0, PT, AXW, PB - PT, PANEL))
b.append(box(BX0, PT, BXW, PB - PT, PANEL))

# ---- Panel A ----
b.append(ltext(AX0 + 24, PT + 32, "A.  The one grid where entropy leads", 20, INK, "bold"))
b.append(ltext(AX0 + 24, PT + 55, "OLMo release grid: right after the first update →", 15, GRAY))
b.append(ltext(AX0 + 24, PT + 74, "terminal spread two rounds later (held out by seed)", 15, GRAY))
AXL, AXR = AX0 + 92, AX0 + AXW - 24
AYB, AYT = PB - 118, PT + 96
yvA = yaxis(AXL, AXR, AYB, AYT, 0.12, (0.0, 0.04, 0.08, 0.12), ".2f")
b.append(f'<text x="{AX0 + 26:.1f}" y="{(AYB + AYT) / 2:.1f}" text-anchor="middle" font-family="{FONT}" '
         f'font-size="14" fill="{GRAY}" transform="rotate(-90 {AX0 + 26:.1f} {(AYB + AYT) / 2:.1f})">RMSE of terminal spread</text>')
aspan = AXR - AXL
abw = 66
for j, v in enumerate(A_VALS):
    acx = AXL + aspan * (j + 0.5) / 3
    ax = acx - abw / 2
    ay = yvA(v)
    b.append(bar(ax, ay, abw, AYB - ay, A_COLORS[j]))
    b.append(ctext(acx, ay - 7, f"{v:.4f}", 13.5, INK))
    for k, ln in enumerate(A_MODELS[j].split("\n")):
        b.append(ctext(acx, AYB + 22 + k * 17, ln, 14.5, INK, "bold"))
# annotation
t, ay2 = wlines(AX0 + 24, PB - 62, "Adding entropy improves 5/6 held-out seed folds; higher post-update entropy "
                "→ more terminal spread.  n = 17 · exploratory, two update rounds remain.", 14.5, 52, GRAY)
b.append(t)

# ---- Panel B ----
b.append(ltext(BX0 + 24, PT + 32, "B.  Across 20 longer release trajectories, it does not", 20, INK, "bold"))
b.append(ltext(BX0 + 24, PT + 55, "leave-one-trajectory-out; entropy barely moves the error and the fitted sign flips", 15, GRAY))
BXL, BXR = BX0 + 78, BX0 + BXW - 300
BYB, BYT = PB - 118, PT + 96
yvB = yaxis(BXL, BXR, BYB, BYT, 0.15, (0.0, 0.05, 0.10, 0.15), ".2f")
b.append(f'<text x="{BX0 + 26:.1f}" y="{(BYB + BYT) / 2:.1f}" text-anchor="middle" font-family="{FONT}" '
         f'font-size="14" fill="{GRAY}" transform="rotate(-90 {BX0 + 26:.1f} {(BYB + BYT) / 2:.1f})">RMSE of later spread</text>')
bspan = BXR - BXL
bbw, bgin = 40, 8
for gi, hz in enumerate(B_HORIZONS):
    gc = BXL + bspan * (gi + 0.5) / 3
    for k, (val, col) in enumerate([(B_S[gi], GRAY), (B_SH[gi], AMBER)]):
        bx = gc - (2 * bbw + bgin) / 2 + k * (bbw + bgin)
        by = yvB(val)
        b.append(bar(bx, by, bbw, BYB - by, col))
        b.append(ctext(bx + bbw / 2, by - 6, f"{val:.4f}", 12, INK))
    b.append(ctext(gc, BYB + 22, hz, 15, INK, "bold"))
    b.append(ctext(gc, BYB + 42, f"{B_CHANGE[gi]} · {B_FOLDS[gi]} folds", 13, GRAY))
# sign annotation (right of the plot)
sx = BXR + 26
t, sy = wlines(sx, BYT + 6, "All release coefficients are negative — higher entropy → slightly LESS later spread, "
               "the opposite of panel A.", 15, 22, DKAMBER, "bold")
b.append(t)
t, _ = wlines(sx, sy + 14, "Transporting the panel-A model without refitting makes it worse: RMSE +9.5% at 1 round, "
              "+23.4% at 2 rounds.", 14.5, 24, GRAY)
b.append(t)

# ================= bottom: Panel C (event contrast) =================
CT, CB = 584, 812
b.append(box(AX0, CT, BX0 + BXW - AX0, CB - CT, PANEL))
b.append(ltext(AX0 + 24, CT + 32, "C.  Entropy never collapses first", 20, INK, "bold"))
b.append(ltext(AX0 + 24, CT + 55, "each mark is one of 20 OLMo release trajectories, grouped by which readout ran out first", 15, GRAY))

col_w = (BX0 + BXW - AX0) / 3
mk, gp, per_row = 22, 6, 6
for gi, (count, col, label) in enumerate(C_CATS):
    colx = AX0 + gi * col_w + 34
    b.append(ltext(colx, CT + 98, f"{count}/20", 20, col if count else GRAY, "bold"))
    if count:
        for i in range(count):
            r, c = divmod(i, per_row)
            mx = colx + c * (mk + gp)
            my = CT + 114 + r * (mk + gp)
            b.append(f'<rect x="{mx:.1f}" y="{my:.1f}" width="{mk}" height="{mk}" rx="4" '
                     f'fill="{col}" stroke="white" stroke-width="1.5"/>')
        rows = (count + per_row - 1) // per_row
    else:
        b.append(ltext(colx, CT + 132, "— none —", 16, GRAY, "italic"))
        rows = 1
    ly = CT + 114 + rows * (mk + gp) + 22
    t, _ = wlines(colx, ly, label, 15, 34, INK)
    b.append(t)

# ================= takeaway =================
b.append(ctext(W / 2, CB + 42, "Generic entropy can track later supply locally, but is not a necessary or transportable leading indicator.",
               21, INK, "bold"))

H = CB + 66
with open(os.path.join(FIGDIR, "synthesis_entropy_longhorizon_supply.svg"), "w", encoding="utf-8") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print(f"wrote synthesis_entropy_longhorizon_supply.svg  ({W}x{int(H)})")

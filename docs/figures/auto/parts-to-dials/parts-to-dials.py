#!/usr/bin/env python3
"""Which part sets which dial — a compact three-column map from the loop's
interchangeable parts, to the model's dials, to the movement they produce.

Orientation figure for the writeup's practical-payoff section: it names the
mapping only (no example numbers, no advice — those stay in prose).

Style reference: docs/figures/src/make_figures.py (Owain Evans-lab house style).
Column-1 chip colours match docs/figures/src/synthesis_experiment_kit.py so the
two figures visually rhyme. Palette + esc()/wrap() copied verbatim so this
generator is self-contained (stdlib only). Run from this directory:
    python3 parts-to-dials.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# --- palette copied verbatim from make_figures.py / model-one-round-line.py ---
INK = "#1a1a1a"
BLUE = "#2867b5"       # self / own candidates
GREEN = "#3a7d44"      # the behavioral value / value-move arrow
RED = "#b5342c"        # emphasis
GRAY = "#6b7684"       # recessive only (axes, guides, muted text)
ORANGE = "#d98a1f"     # supplier candidates (mixed pool)
# --- kit slot colours (verbatim from synthesis_experiment_kit.py) -------------
PURPLE = "#8a5a9e"     # slot 3 : the judge
AMBER = "#b5842c"      # slot 5 : the alternative source
TEAL = "#2f7d78"       # training / kept-mean feedback
SLOT4 = (GREEN, "#eef5ee")    # answer source
SLOT3 = (PURPLE, "#f4eef7")   # judge
SLOT5 = (AMBER, "#f8f2e3")    # alternative source
TEALTINT = "#e8f3f1"

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


# --- small svg helpers --------------------------------------------------------
def ctext(x, y, text, size, color=INK, weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'font-style="{style}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" font-style="{style}" '
            f'fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke, sw=2.5, rx=12):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def badge(cx, cy, num, color, r=14):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{color}"/>'
            f'<text x="{cx:.1f}" y="{cy+5.5:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="16" font-weight="bold" '
            f'fill="white">{num}</text>')


def arrow(x0, y0, x1, y1, color=INK, sw=3.5, dashed=False):
    da = ' stroke-dasharray="5 5"' if dashed else ""
    return (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"{da} '
            f'marker-end="url(#arw-{color[1:]})"/>')


# --- geometry -----------------------------------------------------------------
W, H = 1200, 600
CX = W / 2

# column x-bands
C1X, C1W = 34, 300
C2X, C2W = 442, 296
C3X, C3W = 838, 328

body = []

# ---- headline + subtitle -----------------------------------------------------
body.append(ltext(34, 52, "Which part sets which dial", 31, INK, "bold"))
body.append(ltext(34, 84,
                  "Swap an interchangeable part of the loop and it moves one "
                  "measured dial; the dials multiply into the round's movement.",
                  18, GRAY))

# ---- column headers ----------------------------------------------------------
hy = 128
body.append(ctext(C1X + C1W / 2, hy, "the parts", 20, INK, "bold"))
body.append(ctext(C2X + C2W / 2, hy, "the dials they set", 20, INK, "bold"))
body.append(ctext(C3X + C3W / 2, hy, "the movement they produce", 20, INK, "bold"))
for x, w in [(C1X, C1W), (C2X, C2W), (C3X, C3W)]:
    body.append(f'<line x1="{x}" y1="{hy+12}" x2="{x+w}" y2="{hy+12}" '
                f'stroke="{GRAY}" stroke-width="1.5" opacity="0.45"/>')

# =============================================================================
# COLUMN 1 — the parts (kit chips)
# =============================================================================
# chip A : the answer source (slot 4, green)
Ay, Ah = 176, 82
body.append(box(C1X, Ay, C1W, Ah, SLOT4[1], SLOT4[0], 2.5, rx=13))
body.append(badge(C1X + 28, Ay + 28, "4", SLOT4[0]))
body.append(ltext(C1X + 50, Ay + 33, "THE ANSWER SOURCE", 17.5, SLOT4[0], "bold"))
body.append(ltext(C1X + 20, Ay + 62, "who fills the pool", 16, GRAY))
A_r, A_cy = C1X + C1W, Ay + Ah / 2

# chip B : the judge + the alternative source (slots 3 + 5)
By, Bh = 306, 104
body.append(box(C1X, By, C1W, Bh, SLOT3[1], SLOT3[0], 2.5, rx=13))
body.append(badge(C1X + 28, By + 28, "3", SLOT3[0]))
body.append(badge(C1X + 58, By + 28, "5", SLOT5[0]))
body.append(ltext(C1X + 82, By + 33, "THE JUDGE +", 17.5, SLOT3[0], "bold"))
for i, ln in enumerate(["THE ALTERNATIVE SOURCE"]):
    body.append(ltext(C1X + 20, By + 58, ln, 17.5, SLOT5[0], "bold"))
for i, ln in enumerate(["who judges, and what each",
                        "answer is compared against"]):
    body.append(ltext(C1X + 20, By + 80 + i * 19, ln, 15, GRAY))
B_r, B_cy = C1X + C1W, By + Bh / 2

# chip C : training on the kept answers (teal)
Cy, Ch = 448, 78
body.append(box(C1X, Cy, C1W, Ch, TEALTINT, TEAL, 2.5, rx=13))
body.append(ltext(C1X + 20, Cy + 33, "TRAINING ON THE", 17.5, TEAL, "bold"))
body.append(ltext(C1X + 20, Cy + 55, "KEPT ANSWERS", 17.5, TEAL, "bold"))
C_r, C_cy = C1X + C1W, Cy + Ch / 2

# =============================================================================
# COLUMN 2 — the dials they set (pills)
# =============================================================================
def dial(x, y, w, h, name, sub, color):
    s = [box(x, y, w, h, "white", color, 2.5, rx=11)]
    s.append(ltext(x + 18, y + h / 2 - 3, name, 20, INK, "bold"))
    s.append(ltext(x + 18, y + h / 2 + 18, sub, 14.5, GRAY))
    return "\n".join(s)


# from answer source: two dials (spread + supply shift)
S_y, S_h = 168, 58          # spread sigma
body.append(dial(C2X, S_y, C2W, S_h, "spread  σ", "offered variation", GREEN))
S_l, S_cy, S_r = C2X, S_y + S_h / 2, C2X + C2W

P_y, P_h = 240, 58          # pool-supply shift
body.append(dial(C2X, P_y, C2W, P_h, "pool-supply shift  p − q",
                 "how much the pool is reweighted", GREEN))
P_l, P_cy, P_r = C2X, P_y + P_h / 2, C2X + C2W

# from judge + alternative source: agreement rho
R_y, R_h = 322, 58
body.append(dial(C2X, R_y, C2W, R_h, "agreement  ρ",
                 "how the kept set tracks value", PURPLE))
R_l, R_cy, R_r = C2X, R_y + R_h / 2, C2X + C2W

# from training: next generation starts at kept mean k
K_y, K_h = 440, 74
body.append(box(C2X, K_y, C2W, K_h, "white", TEAL, 2.5, rx=11))
body.append(ltext(C2X + 18, K_y + 26, "the next generation", 17.5, INK, "bold"))
body.append(ltext(C2X + 18, K_y + 48, "starts at the kept mean  k", 17.5, INK, "bold"))
K_l, K_cy, K_r = C2X, K_y + K_h / 2, C2X + C2W

# =============================================================================
# COLUMN 3 — the movement (gap + value line)
# =============================================================================
# selector gap card
G_y, G_h = 234, 66
Gcx = C3X + C3W / 2
body.append(box(C3X, G_y, C3W, G_h, "#eef5ee", GREEN, 2.8, rx=12))
body.append(ctext(Gcx, G_y + 30, "selector gap", 17, GRAY, "bold"))
body.append(ctext(Gcx, G_y + 55, "g = ρσ", 25, GREEN, "bold", "italic"))
G_l, G_cy, G_r, G_b = C3X, G_y + G_h / 2, C3X + C3W, G_y + G_h

# mini 0-1 value line
VL_y = 500
VX0, VX1 = C3X + 36, C3X + C3W - 24
def VX(v):
    return VX0 + v * (VX1 - VX0)
p_v, k_v = 0.30, 0.72
body.append(ctext(Gcx, 430, "new value  =  k  =  p + ρσ", 19, INK, "bold"))
# axis
body.append(f'<line x1="{VX0}" y1="{VL_y}" x2="{VX1}" y2="{VL_y}" '
            f'stroke="{GRAY}" stroke-width="2"/>')
body.append(ctext(VX0, VL_y + 26, "0", 14, GRAY))
body.append(ctext(VX1, VL_y + 26, "1", 14, GRAY))
# p tick
body.append(f'<line x1="{VX(p_v):.1f}" y1="{VL_y-11}" x2="{VX(p_v):.1f}" '
            f'y2="{VL_y+11}" stroke="{INK}" stroke-width="3"/>')
body.append(ctext(VX(p_v), VL_y - 18, "p", 21, INK, "bold", "italic"))
# rho*sigma arrow p -> k
body.append(f'<line x1="{VX(p_v)+3:.1f}" y1="{VL_y}" x2="{VX(k_v)-8:.1f}" '
            f'y2="{VL_y}" stroke="{GREEN}" stroke-width="5" '
            f'marker-end="url(#arw-{GREEN[1:]})"/>')
body.append(ctext((VX(p_v)+VX(k_v))/2, VL_y - 14, "ρσ", 16, GREEN, "bold", "italic"))
# k tick
body.append(f'<line x1="{VX(k_v):.1f}" y1="{VL_y-11}" x2="{VX(k_v):.1f}" '
            f'y2="{VL_y+11}" stroke="{GREEN}" stroke-width="3.5"/>')
body.append(ctext(VX(k_v), VL_y - 18, "k", 21, GREEN, "bold", "italic"))

# =============================================================================
# ARROWS
# =============================================================================
# col1 -> col2
body.append(arrow(A_r + 4, A_cy, S_l - 6, S_cy, GREEN))       # answer -> spread
body.append(arrow(A_r + 4, A_cy, P_l - 6, P_cy, GREEN))       # answer -> supply shift
body.append(arrow(B_r + 4, B_cy, R_l - 6, R_cy, PURPLE))      # judge -> agreement
body.append(arrow(C_r + 4, C_cy, K_l - 6, K_cy, TEAL))        # training -> kept mean

# col2 -> col3 : spread and agreement converge into the gap card
body.append(arrow(S_r + 4, S_cy, G_l - 6, G_cy - 8, GREEN))   # spread -> gap
body.append(arrow(R_r + 4, R_cy, G_l - 6, G_cy + 8, PURPLE))  # agreement -> gap

# supply shift -> value line (sets p); gap -> value line (arrow length)
body.append(arrow(P_r + 4, P_cy, VX(p_v) - 4, VL_y - 26, INK, 3))     # supply -> p
body.append(arrow(G_b + 0, G_cy + 30, Gcx, VL_y - 44, GREEN, 3))       # gap -> line
# reroute gap->line as a short vertical connector under the gap card
body[-1] = arrow(Gcx, G_b + 2, Gcx, 414, GREEN, 3)

# return arrow : kept mean k feeds next round's answer source.
# routed through the bottom gutter so it never crosses the middle rows.
ret_y = 560
body.append(f'<path d="M {K_l - 6:.1f} {K_cy + 8:.1f} '
            f'L {K_l - 6:.1f} {ret_y:.1f} '
            f'L 20 {ret_y:.1f} '
            f'L 20 {A_cy:.1f} '
            f'L {C1X - 4:.1f} {A_cy:.1f}" '
            f'fill="none" stroke="{TEAL}" stroke-width="2.4" '
            f'stroke-dasharray="6 5" marker-end="url(#arw-{TEAL[1:]})"/>')
body.append(ctext((K_l + 40) / 2 + 20, ret_y + 24,
                  "next round — the kept mean becomes the new starting point",
                  14.5, TEAL, "bold", "italic"))

# =============================================================================
# DEFS + assemble
# =============================================================================
markers = []
for col in [INK, GREEN, PURPLE, TEAL]:
    markers.append(
        f'<marker id="arw-{col[1:]}" viewBox="0 0 10 10" refX="8.5" refY="5" '
        f'markerWidth="6.5" markerHeight="6.5" orient="auto">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{col}"/></marker>')
DEFS = "<defs>\n" + "\n".join(markers) + "\n</defs>"

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       f'{DEFS}\n' + "\n".join(body) + "\n</svg>")

OUT = os.path.join(HERE, "parts-to-dials.svg")
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}")

#!/usr/bin/env python3
"""One round of the selection loop, drawn as means and distances on a single
0-1 value number line. Definitions figure for the writeup model section.

Style reference: docs/figures/src/make_figures.py (Owain Evans-lab house style).
Palette constants, esc(), and wrap() are copied here verbatim so this generator
is self-contained (stdlib only). Run from this directory:  python3 model-one-round-line.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# docs/figures/auto/model-one-round-line -> repo root is four levels up.
BAKEOFF = os.path.join(HERE, "..", "..", "..", "..",
                       "experiments", "value_predictor_bakeoff.json")

# --- palette copied verbatim from make_figures.py -----------------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # self / own candidates
GREEN = "#3a7d44"      # the behavioral value / value-move arrow
RED = "#b5342c"        # emphasis
GRAY = "#6b7684"       # recessive only (axes, guides, muted text)
ORANGE = "#d98a1f"     # supplier candidates (mixed pool)
KEY_FILL = "#eef5ee"

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


# --- load asserted numbers from the result file -------------------------------
with open(BAKEOFF) as f:
    D = json.load(f)
LOCO = D["one_round"]["leave_one_condition_out"]
MAE_KEPT = LOCO["kept_target_identity"]["mae"]   # 0.081157
MAE_NONE = LOCO["no_change"]["mae"]              # 0.127883
N_ROUNDS = LOCO["kept_target_identity"]["n"]     # 340

# --- geometry -----------------------------------------------------------------
W, H = 1200, 930
X0, X1 = 150, 1060          # value axis 0 .. 1 in pixels
def X(v):
    return X0 + v * (X1 - X0)

# illustrative candidate positions (a definitions figure: chosen for clarity).
# Mixed pools in the corpus are half-and-half: 3 own + 3 outside of the 6
# candidates (self-only pools are all 6 own).
OWN = [0.30, 0.42, 0.54]
SUP = [0.62, 0.72, 0.82]
KEPT = [0.54, 0.82]         # the judge keeps one own + one outside candidate

def mean(xs):
    return sum(xs) / len(xs)

Q = mean(OWN)               # own mean
P = mean(OWN + SUP)         # pool mean
K = mean(KEPT)             # kept mean
V_OLD = Q                   # behavioral value before this round

Y1, Y2, Y3 = 300, 560, 800  # the three step axes
DOT = 8


def axis_line(y):
    return (f'<line x1="{X0}" y1="{y}" x2="{X1}" y2="{y}" stroke="{GRAY}" '
            f'stroke-width="2"/>'
            f'<text x="{X0}" y="{y+34}" font-size="16" fill="{GRAY}" '
            f'text-anchor="middle" font-family="{FONT}">0</text>'
            f'<text x="{X1}" y="{y+34}" font-size="16" fill="{GRAY}" '
            f'text-anchor="middle" font-family="{FONT}">1</text>')


def dot(v, y, color, filled=True):
    fill = color if filled else "white"
    return (f'<circle cx="{X(v):.1f}" cy="{y}" r="{DOT}" fill="{fill}" '
            f'stroke="{color}" stroke-width="2.5"/>')


def tick(v, y, color, letter, desc, above=True, big=True):
    """A vertical marker at value v with a bold letter and small descriptor."""
    x = X(v)
    dy = -14 if above else 14
    ly = y - 22 if above else y + 40
    dyd = y - 44 if above else y + 60
    sz = 27 if big else 22
    s = [f'<line x1="{x:.1f}" y1="{y-14}" x2="{x:.1f}" y2="{y+14}" '
         f'stroke="{color}" stroke-width="3"/>']
    s.append(f'<text x="{x:.1f}" y="{ly}" font-size="{sz}" font-weight="bold" '
             f'fill="{color}" text-anchor="middle" font-style="italic" '
             f'font-family="{FONT}">{letter}</text>')
    if desc:
        s.append(f'<text x="{x:.1f}" y="{dyd}" font-size="14.5" fill="{GRAY}" '
                 f'text-anchor="middle" font-family="{FONT}">{esc(desc)}</text>')
    return "\n".join(s)


def measure(v_a, v_b, y, label, color, tickh=9):
    """Horizontal distance marker from v_a to v_b at height y with a label
    centered underneath."""
    xa, xb = X(v_a), X(v_b)
    xm = (xa + xb) / 2
    s = [f'<line x1="{xa:.1f}" y1="{y-tickh}" x2="{xa:.1f}" y2="{y+tickh}" '
         f'stroke="{color}" stroke-width="2.5"/>',
         f'<line x1="{xb:.1f}" y1="{y-tickh}" x2="{xb:.1f}" y2="{y+tickh}" '
         f'stroke="{color}" stroke-width="2.5"/>',
         f'<line x1="{xa:.1f}" y1="{y}" x2="{xb:.1f}" y2="{y}" '
         f'stroke="{color}" stroke-width="2.5" marker-end="url(#tipEnd)" '
         f'marker-start="url(#tipStart)"/>',
         f'<text x="{xm:.1f}" y="{y+26}" font-size="17" font-weight="bold" '
         f'fill="{color}" text-anchor="middle" font-family="{FONT}">'
         f'{esc(label)}</text>']
    return "\n".join(s)


def step_label(n, text, y):
    return (f'<circle cx="{72}" cy="{y-6}" r="18" fill="{INK}"/>'
            f'<text x="72" y="{y+1}" font-size="22" font-weight="bold" '
            f'fill="white" text-anchor="middle" font-family="{FONT}">{n}</text>'
            f'<text x="102" y="{y+1}" font-size="20" font-weight="bold" '
            f'fill="{INK}" font-family="{FONT}">{esc(text)}</text>')


# --- assemble body ------------------------------------------------------------
body = []

# vertical guides so the eye tracks q, p, k positions down the steps —
# q runs the whole way (the training displacement under step 3 needs it);
# p spans steps 1-2; k spans steps 2-3
for v, col, gy0, gy1 in [(Q, BLUE, 240, 876), (P, INK, 240, 620),
                         (K, INK, 492, 876)]:
    body.append(f'<line x1="{X(v):.1f}" y1="{gy0}" x2="{X(v):.1f}" y2="{gy1}" '
                f'stroke="{col}" stroke-width="1.3" stroke-dasharray="3 6" '
                f'opacity="0.35"/>')

# ---- headline + one-line subtitle ----
body.append(f'<text x="60" y="66" font-size="31" font-weight="bold" '
            f'fill="{INK}" font-family="{FONT}">One round, on the value line: '
            f'pool, kept set, and the move</text>')
body.append(f'<text x="60" y="100" font-size="18" fill="{GRAY}" '
            f'font-family="{FONT}">Positions are mean value scores, 0–1; '
            f'symbols as used throughout the post.</text>')
body.append(f'<text x="60" y="124" font-size="18" fill="{GRAY}" '
            f'font-family="{FONT}">Mixed pool shown: 3 own + 3 outside of '
            f'the 6 candidates (self-only pools are all 6 own).</text>')

# ---- legend row ----
lx = 60
leg = [("own candidates", BLUE, True), ("outside-source candidates", ORANGE, True),
       ("kept (circled)", INK, False)]
body.append(f'<text x="{lx}" y="150" font-size="15.5" fill="{GRAY}" '
            f'font-family="{FONT}">key:</text>')
lx += 46
for name, col, filled in leg:
    if filled:
        body.append(f'<circle cx="{lx}" cy="145" r="8" fill="{col}" '
                    f'stroke="{col}" stroke-width="2.5"/>')
    else:
        body.append(f'<circle cx="{lx}" cy="145" r="8" fill="white" '
                    f'stroke="{col}" stroke-width="2.5"/>'
                    f'<circle cx="{lx}" cy="145" r="13" fill="none" '
                    f'stroke="{INK}" stroke-width="2.5"/>')
    body.append(f'<text x="{lx+22}" y="150" font-size="15.5" fill="{INK}" '
                f'font-family="{FONT}">{esc(name)}</text>')
    lx += 42 + len(name) * 8.6

# =========================== STEP 1 : the pool ===============================
body.append(step_label("1", "the pool", 218))
body.append(axis_line(Y1))
for v in OWN:
    body.append(dot(v, Y1, BLUE))
for v in SUP:
    body.append(dot(v, Y1, ORANGE))
body.append(tick(Q, Y1, BLUE, "q", "own mean", above=True))
body.append(tick(P, Y1, INK, "p", "pool mean", above=True))
# pool-supply shift below the axis
body.append(measure(Q, P, Y1 + 56, "pool shift  (p − q)", ORANGE))
body.append(f'<text x="{X1}" y="{Y1+56}" font-size="15" fill="{GRAY}" '
            f'text-anchor="end" font-style="italic" font-family="{FONT}">'
            f'self-only pool: p = q</text>')

# ==================== STEP 2 : the judge keeps two ===========================
body.append(step_label("2", "the judge keeps two", 478))
body.append(axis_line(Y2))
for v in OWN:
    body.append(dot(v, Y2, BLUE))
for v in SUP:
    body.append(dot(v, Y2, ORANGE))
for v in KEPT:                      # black circles around the kept candidates
    body.append(f'<circle cx="{X(v):.1f}" cy="{Y2}" r="14" fill="none" '
                f'stroke="{INK}" stroke-width="3"/>')
body.append(tick(K, Y2, INK, "k", "kept mean", above=True))
# ghost q, p ticks (small) so both gaps are readable
for v, col, lt in [(Q, BLUE, "q"), (P, INK, "p")]:
    body.append(f'<line x1="{X(v):.1f}" y1="{Y2-11}" x2="{X(v):.1f}" '
                f'y2="{Y2+11}" stroke="{col}" stroke-width="2"/>'
                f'<text x="{X(v):.1f}" y="{Y2-20}" font-size="19" '
                f'font-weight="bold" font-style="italic" fill="{col}" '
                f'text-anchor="middle" font-family="{FONT}">{lt}</text>')
# selector gap (p -> k), shorter, just under axis
body.append(measure(P, K, Y2 + 52, "selector gap   g = k − p", GREEN))

# ================= STEP 3 : training moves the value =========================
body.append(step_label("3", "training moves the value", 758))
body.append(axis_line(Y3))
# faded prior candidates for context
for v in OWN:
    body.append(f'<circle cx="{X(v):.1f}" cy="{Y3}" r="6" fill="none" '
                f'stroke="{GRAY}" stroke-width="1.6" opacity="0.5"/>')
# the green move to k (no marker at the start: the value coordinate is not
# the own mean; the arrow simply departs from where the organism's answers sit)
# bold green arrow from old value to k
body.append(f'<line x1="{X(V_OLD)+14:.1f}" y1="{Y3}" x2="{X(K)-16:.1f}" '
            f'y2="{Y3}" stroke="{GREEN}" stroke-width="6" '
            f'marker-end="url(#arrG)"/>')
# the next value sits exactly at the kept mean k
body.append(f'<circle cx="{X(K):.1f}" cy="{Y3}" r="9" fill="{GREEN}" '
            f'stroke="{GREEN}" stroke-width="2.5"/>')
body.append(f'<rect x="{X(K)-68:.1f}" y="{Y3-40}" width="136" height="24" '
            f'fill="white"/>')
body.append(f'<text x="{X(K):.1f}" y="{Y3-22}" font-size="20" '
            f'font-weight="bold" font-style="italic" fill="{GREEN}" '
            f'text-anchor="middle" font-family="{FONT}">new value ≈ k</text>')
# training displacement (q -> k), under the step-3 line
body.append(measure(Q, K, Y3 + 76,
                    "training displacement = k − q  =  gap + pool shift",
                    INK))

DEFS = f'''<defs>
<marker id="tipEnd" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="5.5"
 markerHeight="5.5" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z"/></marker>
<marker id="tipStart" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="5.5"
 markerHeight="5.5" orient="auto"><path d="M 10 0 L 0 5 L 10 10 z"/></marker>
<marker id="arrG" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6"
 markerHeight="6" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z"
 fill="{GREEN}"/></marker>
</defs>'''

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       f'{DEFS}\n' + "\n".join(body) + "\n</svg>")

OUT = os.path.join(HERE, "model-one-round-line.svg")
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}")
print(f"q={Q:.3f} p={P:.3f} k={K:.3f}  supply shift={P-Q:.3f} "
      f"gap={K-P:.3f} displacement={K-Q:.3f}")
print(f"MAE kept={MAE_KEPT:.4f}  no-change={MAE_NONE:.4f}  n={N_ROUNDS}")

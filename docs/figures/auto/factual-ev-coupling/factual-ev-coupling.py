#!/usr/bin/env python3
"""factual-ev-coupling — value knowledge erodes mildly under all loop training,
but the erosion is coupled to how far the value moved only on Qwen (training-
instability mechanism), not on OLMo (selection mechanism).

Two side-by-side scatters on identical axes: x = preference move (|final pool
mean risk minus round-1 pool mean risk|), y = change in value knowledge
(end-of-run P(picks the higher-expected-payoff option) minus round-1). One dot
per run. Data: experiments/factual_ev_trajectory.json.

Regenerate with:  python3 factual-ev-coupling.py   (stdlib only)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "experiments", "factual_ev_trajectory.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
KEY_FILL = "#eef5ee"   # highlighted takeaway box

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


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4):
    lines = wrap(text, width)
    svg = []
    for i, ln in enumerate(lines):
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def ctext(x, y, text, size, color=INK, weight="normal", anchor="middle"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- data
def mean(v):
    return sum(v) / len(v)


def fit_and_corr(xs, ys):
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    return slope, my - slope * mx, sxy / math.sqrt(sxx * syy)


with open(DATA) as f:
    D = json.load(f)

OLMO = [r for r in D["runs"] if r["grid"] == "k2_olmo"]
QWEN = [r for r in D["runs"] if r["grid"] == "k1_qwen"]

STATS = {}
for name, runs in (("olmo", OLMO), ("qwen", QWEN)):
    xs = [r["pref_move"] for r in runs]
    ys = [r["d_ev"] for r in runs]
    slope, icpt, r_ = fit_and_corr(xs, ys)
    _, _, r_abs = fit_and_corr(xs, [abs(y) for y in ys])
    STATS[name] = dict(n=len(runs), slope=slope, icpt=icpt, r=r_, r_abs=r_abs,
                       ev0=mean([r["ev"][0] for r in runs]),
                       evN=mean([r["ev"][-1] for r in runs]),
                       dmean=mean(ys))

# ---------------------------------------------------------------- figure
b = []
W = 1500

b.append(ctext(W // 2, 56, "Moving the value costs knowledge on Qwen, but not on OLMo", 32, INK, "bold"))
sub = ("Every run of the self-training loop mildly erodes value knowledge — P(the model picks which of two "
       "gambles has the higher expected payoff), order-balanced fixed items, measured every round. "
       "Each dot is one run: x is how far the value moved (|final pool mean risk minus round-1 pool mean risk|), "
       "y is knowledge at the end minus knowledge at round 1.")
t, _ = text_block(150, 92, sub, BODY, 122, GRAY)
b.append(t)

# shared axis limits
XMIN, XMAX = -0.02, 0.80
YMIN, YMAX = -0.135, 0.075
AY, AH = 288, 400
PW = 560
PANELS = {"olmo": 130, "qwen": 800}


def px(panel, v):
    return PANELS[panel] + PW * (v - XMIN) / (XMAX - XMIN)


def py(v):
    return AY + AH * (YMAX - v) / (YMAX - YMIN)


def draw_axes(panel, title, title_color):
    out = [f'<text x="{PANELS[panel]}" y="{AY - 32}" font-size="22" font-weight="bold" '
           f'fill="{title_color}" font-family="{FONT}">{esc(title)}</text>']
    for v in (0.05, 0.0, -0.05, -0.10):
        yy = py(v)
        col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
        if abs(v + 0.10) < 1e-9:
            col, sw = "none", 0  # the gate rule replaces this gridline
        if col != "none":
            out.append(f'<line x1="{px(panel, XMIN):.1f}" y1="{yy:.1f}" x2="{px(panel, XMAX):.1f}" '
                       f'y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
        out.append(f'<text x="{px(panel, XMIN) - 12:.1f}" y="{yy + 6:.1f}" text-anchor="end" '
                   f'font-size="18" fill="{GRAY}" font-family="{FONT}">{v:+.2f}</text>')
    for v in (0.0, 0.2, 0.4, 0.6):
        xx = px(panel, v)
        out.append(f'<line x1="{xx:.1f}" y1="{AY}" x2="{xx:.1f}" y2="{AY + AH}" '
                   f'stroke="#e4e4e0" stroke-width="1"/>')
        out.append(f'<text x="{xx:.1f}" y="{AY + AH + 28}" text-anchor="middle" font-size="18" '
                   f'fill="{GRAY}" font-family="{FONT}">{v:.1f}</text>')
    out.append(ctext(PANELS[panel] + PW / 2, AY + AH + 60,
                     "preference move: |final pool mean risk minus round-1 pool mean risk|", BODY, INK))
    # the -0.10 knowledge gate, dashed, in warning red
    gy = py(-0.10)
    out.append(f'<line x1="{px(panel, XMIN):.1f}" y1="{gy:.1f}" x2="{px(panel, XMAX):.1f}" y2="{gy:.1f}" '
               f'stroke="{RED}" stroke-width="2.5" stroke-dasharray="9 7"/>')
    return "\n".join(out)


b.append(f'<text x="{PANELS["olmo"] - 76}" y="{AY + AH / 2}" font-size="{BODY}" fill="{INK}" '
         f'font-family="{FONT}" transform="rotate(-90 {PANELS["olmo"] - 76} {AY + AH / 2})" '
         f'text-anchor="middle">change in value knowledge (end minus round 1)</text>')

s = STATS["olmo"]
b.append(draw_axes("olmo", f"OLMo risk model — {s['n']} runs (K2 grid + modal press cells)", BLUE))
s = STATS["qwen"]
b.append(draw_axes("qwen", f"Qwen risk model — {s['n']} runs (K1 judge grid)", RED))

# gate rule label (once, on the left panel)
b.append(f'<text x="{px("olmo", 0.165):.1f}" y="{py(-0.10) + 24:.1f}" font-size="16" fill="{RED}" '
         f'font-family="{FONT}">−0.10 knowledge gate (checked on the largest within-run drop)</text>')

# fitted lines (drawn under the dots)
for panel, color, key in (("olmo", BLUE, "olmo"), ("qwen", RED, "qwen")):
    st = STATS[key]
    runs = OLMO if key == "olmo" else QWEN
    x1 = 0.0
    x2 = max(r["pref_move"] for r in runs) + 0.03
    b.append(f'<line x1="{px(panel, x1):.1f}" y1="{py(st["slope"] * x1 + st["icpt"]):.1f}" '
             f'x2="{px(panel, x2):.1f}" y2="{py(st["slope"] * x2 + st["icpt"]):.1f}" '
             f'stroke="{color}" stroke-width="3.5" stroke-opacity="0.55"/>')

# dots — one per run; Qwen self-judge runs get triangles so the worst cluster is nameable
GATE_BREACH = []
for r in OLMO:
    x, y = px("olmo", r["pref_move"]), py(r["d_ev"])
    b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{BLUE}" fill-opacity="0.75" '
             f'stroke="white" stroke-width="1.5"/>')
    if r["fails_gate"]:
        GATE_BREACH.append((x, y))
for r in QWEN:
    x, y = px("qwen", r["pref_move"]), py(r["d_ev"])
    if r["cond"] == "evolving_self":
        pts = f"{x:.1f},{y - 9:.1f} {x - 8.5:.1f},{y + 7.5:.1f} {x + 8.5:.1f},{y + 7.5:.1f}"
        b.append(f'<polygon points="{pts}" fill="{RED}" fill-opacity="0.9" stroke="white" stroke-width="1.5"/>')
    else:
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{RED}" fill-opacity="0.6" '
                 f'stroke="white" stroke-width="1.5"/>')

# ring the OLMo runs that transiently breached the gate
for x, y in GATE_BREACH:
    b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="13" fill="none" stroke="{RED}" '
             f'stroke-width="2.5" stroke-dasharray="4 3"/>')

# ---- in-panel readouts: OLMo (on a white plate so no dot runs through the text)
st = STATS["olmo"]
fx, fy = px("olmo", 0.30), py(0.058)
b.append(f'<rect x="{fx - 10:.1f}" y="{fy - 24:.1f}" width="320" height="62" rx="8" '
         f'fill="white" fill-opacity="0.92"/>')
b.append(f'<text x="{fx:.1f}" y="{fy:.1f}" font-size="21" font-weight="bold" fill="{BLUE}" '
         f'font-family="{FONT}">flat: correlation r = {st["r"]:.2f}</text>')
b.append(f'<text x="{fx:.1f}" y="{fy + 27:.1f}" font-size="18" fill="{GRAY}" font-family="{FONT}">'
         f'mean knowledge {st["ev0"]:.3f} → {st["evN"]:.3f} (Δ {st["dmean"]:+.3f})</text>')
t, _ = text_block(PANELS["olmo"] + 6, AY + AH + 96,
                  "Ringed: 3 runs dipped past the gate mid-run — all erosion-pressure cells with "
                  "small preference moves. The biggest movers (0.5 to 0.75) lose no more "
                  "knowledge than runs that barely moved.", 17, 66, INK)
b.append(t)

# ---- in-panel readouts: Qwen
st = STATS["qwen"]
fx, fy = px("qwen", 0.36), py(0.058)
b.append(f'<text x="{fx:.1f}" y="{fy:.1f}" font-size="21" font-weight="bold" fill="{RED}" '
         f'font-family="{FONT}">coupled: correlation r = {st["r"]:.2f}</text>')
b.append(f'<text x="{fx:.1f}" y="{fy + 27:.1f}" font-size="18" fill="{GRAY}" font-family="{FONT}">'
         f'mean knowledge {st["ev0"]:.3f} → {st["evN"]:.3f} (Δ {st["dmean"]:+.3f})</text>')
# marker key, kept clear of the zero line
kx, ky = px("qwen", 0.40), py(0.030)
b.append(f'<polygon points="{kx:.1f},{ky - 8:.1f} {kx - 7.5:.1f},{ky + 6.5:.1f} {kx + 7.5:.1f},{ky + 6.5:.1f}" '
         f'fill="{RED}" fill-opacity="0.9" stroke="white" stroke-width="1.5"/>')
b.append(f'<text x="{kx + 14:.1f}" y="{ky + 5:.1f}" font-size="18" fill="{INK}" '
         f'font-family="{FONT}">the model judging itself</text>')
b.append(f'<circle cx="{kx:.1f}" cy="{ky + 27:.1f}" r="7" fill="{RED}" fill-opacity="0.6" '
         f'stroke="white" stroke-width="1.5"/>')
b.append(f'<text x="{kx + 14:.1f}" y="{ky + 32:.1f}" font-size="18" fill="{INK}" '
         f'font-family="{FONT}">frozen judge or random keep</text>')
t, _ = text_block(PANELS["qwen"] + 6, AY + AH + 96,
                  "The three biggest self-judge movers are the three biggest knowledge losers "
                  "(Δ −0.080 to −0.086). Fitted line: change in knowledge ≈ "
                  f"{st['slope']:.2f} × preference move.", 17, 66, INK)
b.append(t)

# ---------------------------------------------------------------- takeaway
ty = AY + AH + 190
b.append(box(130, ty, 1230, 108, KEY_FILL))
# three hand-set lines of mixed-color text (segments are glued, so punctuation
# stays attached to the numbers)
LINES = [
    [("Same loop, two mechanisms. ", INK, True),
     ("OLMo moves its value by selection among still-coherent answers, so knowledge loss is",
      INK, False)],
    [("unrelated to the move (r = ", INK, False),
     (f"{STATS['olmo']['r']:.2f}", BLUE, True),
     ("). Qwen moves by training instability, and the same instability damages knowledge",
      INK, False)],
    [("along the way (r = ", INK, False),
     (f"{STATS['qwen']['r']:.2f}", RED, True),
     ("; the size of the knowledge change against the move, r = ", INK, False),
     (f"+{abs(STATS['qwen']['r_abs']):.2f}", RED, True),
     (").", INK, False)],
]
for i, ln in enumerate(LINES):
    tsp = "".join(f'<tspan fill="{c}" font-weight="{"bold" if bo else "normal"}">{esc(t_)}</tspan>'
                  for t_, c, bo in ln)
    b.append(f'<text x="154" y="{ty + 40 + i * 28}" font-family="{FONT}" font-size="{BODY}">{tsp}</text>')

H = ty + 140
svg = svg_doc(W, H, "\n".join(b))
out = os.path.join(HERE, "factual-ev-coupling.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}")
print("olmo:", {k: round(v, 3) for k, v in STATS["olmo"].items()})
print("qwen:", {k: round(v, 3) for k, v in STATS["qwen"].items()})

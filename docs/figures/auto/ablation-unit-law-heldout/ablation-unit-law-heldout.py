#!/usr/bin/env python3
"""Held-out test of the one-round selection-response law across the FULL 2x2
judge factorial (24 supplier-removed em750 self-loop runs, 4 conditions x 6
seeds 41-46).

Two-panel predicted-vs-actual scatter, Owain Evans-lab house style (white
background, headline sentence, real data with fat labels, in-figure keys).
Both panels plot ACTUAL (y) against the FROZEN PREDICTION (x), so the reference
line is the identity y=x -- the frozen law with no free parameter left.

Frozen constants C=0.96 (factorization) and K=0.833 (movement) were fit on the
earlier program (simple_model_rollout.json / spread_util_unified.json). The
ablation runs postdate that fit; nothing here is refit on this data. The refit
slopes shown are diagnostics only.

Run from this directory:  python3 ablation-unit-law-heldout.py
Reads: ../../../../experiments/ablation_unit_law.json
Writes: ablation-unit-law-heldout.svg
Stdlib only.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "ablation_unit_law.json")

# ---- palette (copied from make_figures.py, + one categorical amber) --------
INK = "#1a1a1a"
BLUE = "#2867b5"       # candid + self-judge
GREEN = "#3a7d44"      # neutral + self-judge
RED = "#b5342c"        # candid + base-judge
AMBER = "#c07a12"      # neutral + base-judge (4th categorical hue; CVD-validated)
GRAY = "#6b7684"       # recessive (axes, muted captions)
KEY_FILL = "#eef5ee"
FONT = "Helvetica, Arial, sans-serif"

# condition -> (words label, color).  4 cells of the judge factorial.
COND = {
    "candid_self":  ("candid judge prompt + self judge model", BLUE),
    "neutral_self": ("neutral judge prompt + self judge model", GREEN),
    "candid_base":  ("candid judge prompt + base judge model", RED),
    "neutral_base": ("neutral judge prompt + base judge model", AMBER),
}
COND_ORDER = ["candid_self", "neutral_self", "candid_base", "neutral_base"]
# draw base (looser) points first so tight self points sit on top
PLOT_ORDER = ["candid_base", "neutral_base", "neutral_self", "candid_self"]


# ---- helpers (copied from make_figures.py) --------------------------------
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


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def txt(x, y, s, size, color=INK, anchor="start", weight="normal", style=""):
    st = f' font-style="{style}"' if style else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}"{st}>'
            f'{esc(s)}</text>')


# ---- load data ------------------------------------------------------------
with open(DATA) as f:
    D = json.load(f)

TR = D["rho_trajectories"]
C_FROZEN = D["frozen_constants"]["C"]   # 0.96
K_FROZEN = D["frozen_constants"]["K"]   # 0.833
FACT = D["factorization"]
MOVE = D["movement"]


def cond_of(tag):
    return tag.split(":")[0]


# Panel 1 (movement) points: (K*gap[i], pool_mean[i+1]-pool_mean[i])
# Panel 2 (factorization) points: (C*rho[i]*sigma[i], gap[i])  where rho not null
ptsMOVE = {c: [] for c in COND}
ptsFACT = {c: [] for c in COND}
for tag, tr in TR.items():
    c = cond_of(tag)
    rho, sig, gap, pm = tr["rho"], tr["sigma"], tr["gap"], tr["pool_mean"]
    for i in range(len(rho)):
        if rho[i] is not None:
            ptsFACT[c].append((C_FROZEN * rho[i] * sig[i], gap[i]))
    for i in range(len(pm) - 1):
        if pm[i] is not None and pm[i + 1] is not None:
            ptsMOVE[c].append((K_FROZEN * gap[i], pm[i + 1] - pm[i]))

nMOVE = sum(len(v) for v in ptsMOVE.values())
nFACT = sum(len(v) for v in ptsFACT.values())


# ---- predicted-vs-actual panel builder ------------------------------------
def panel(px, py, pw, ph, pts, rng, xlabel, ylabel, corner):
    """Square panel: x=frozen prediction, y=actual, identity line y=x."""
    lo, hi = rng

    def sx(v):
        return px + (v - lo) / (hi - lo) * pw

    def sy(v):
        return py + ph - (v - lo) / (hi - lo) * ph

    s = []
    s.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="white" '
             f'stroke="{GRAY}" stroke-width="1.5"/>')

    # gridlines + ticks (every 0.1 across the range)
    def ticks(lo_, hi_, step):
        vals, v = [], -1.0
        while v <= hi_ + 1e-9:
            if v >= lo_ - 1e-9:
                vals.append(round(v, 3))
            v += step
        return vals

    for t in ticks(lo, hi, 0.1):
        gx = sx(t)
        s.append(f'<line x1="{gx:.1f}" y1="{py}" x2="{gx:.1f}" y2="{py+ph}" '
                 f'stroke="#e7e9ec" stroke-width="1"/>')
        s.append(txt(gx, py + ph + 26, f"{t:g}", 15, GRAY, "middle"))
        gy = sy(t)
        s.append(f'<line x1="{px}" y1="{gy:.1f}" x2="{px+pw}" y2="{gy:.1f}" '
                 f'stroke="#e7e9ec" stroke-width="1"/>')
        s.append(txt(px - 14, gy + 5, f"{t:g}", 15, GRAY, "end"))

    # zero axes (heavier)
    zx, zy = sx(0), sy(0)
    s.append(f'<line x1="{zx:.1f}" y1="{py}" x2="{zx:.1f}" y2="{py+ph}" '
             f'stroke="{GRAY}" stroke-width="1.6"/>')
    s.append(f'<line x1="{px}" y1="{zy:.1f}" x2="{px+pw}" y2="{zy:.1f}" '
             f'stroke="{GRAY}" stroke-width="1.6"/>')

    # identity line y = x (the frozen law, no free parameter)
    s.append(f'<line x1="{sx(lo):.1f}" y1="{sy(lo):.1f}" '
             f'x2="{sx(hi):.1f}" y2="{sy(hi):.1f}" '
             f'stroke="{INK}" stroke-width="3.2" stroke-dasharray="10 6"/>')
    # identity label in the sparse upper-left corner (off the diagonal)
    s.append(txt(px + 14, py + 30, corner[0], 17, INK, "start", "bold"))
    s.append(txt(px + 14, py + 51, corner[1], 14, INK, "start", "normal", "italic"))

    # points
    for c in PLOT_ORDER:
        _, col = COND[c]
        for (vx, vy) in pts[c]:
            s.append(f'<circle cx="{sx(vx):.1f}" cy="{sy(vy):.1f}" r="7" '
                     f'fill="{col}" fill-opacity="0.82" '
                     f'stroke="white" stroke-width="1.6"/>')

    # axis titles
    s.append(txt(px + pw / 2, py + ph + 58, xlabel, 17, INK, "middle", "bold"))
    s.append(f'<text x="{px - 66}" y="{py + ph/2}" font-family="{FONT}" '
             f'font-size="17" fill="{INK}" text-anchor="middle" font-weight="bold" '
             f'transform="rotate(-90 {px-66} {py+ph/2})">{esc(ylabel)}</text>')
    return "\n".join(s)


# ---- canvas ---------------------------------------------------------------
W, H = 1880, 1120
body = []

# headline
body.append(txt(60, 60,
                "The movement law holds in every cell of the judge factorial:",
                33, INK, "start", "bold"))
body.append(txt(60, 100,
                "one frozen number (0.833) predicts next-round drift whatever "
                "the judge prompt or judge model",
                33, INK, "start", "bold"))

# context / method line
ctx = ("Held-out test - 24 supplier-removed em750 self-loop runs (judge prompt x "
       "judge model, seeds 41-46); constants frozen from earlier fits "
       "(C=0.96, K=0.833), never refit on this data.")
for i, ln in enumerate(wrap(ctx, 118)):
    body.append(txt(60, 132 + i * 24, ln, 18, GRAY, "start"))

# in-figure key (shared, 4 conditions + identity line)
kx, ky = 60, 196
body.append(f'<rect x="{kx-14}" y="{ky-22}" width="1560" height="40" rx="9" '
            f'fill="{KEY_FILL}" stroke="{GRAY}" stroke-width="1.3"/>')
cxp = kx
for c in COND_ORDER:
    label, col = COND[c]
    body.append(f'<circle cx="{cxp+8}" cy="{ky-2}" r="8" fill="{col}" '
                f'fill-opacity="0.85" stroke="white" stroke-width="1.6"/>')
    body.append(txt(cxp + 24, ky + 4, label, 16, INK, "start", "bold"))
    cxp += 40 + len(label) * 8.6
body.append(f'<line x1="{cxp+2}" y1="{ky-8}" x2="{cxp+42}" y2="{ky-8}" '
            f'stroke="{INK}" stroke-width="3.2" stroke-dasharray="10 6"/>')
body.append(txt(cxp + 50, ky + 4, "frozen law = identity", 16, INK, "start", "bold"))

PY, PH, PW = 310, 470, 460

# ---- Panel 1: MOVEMENT ----------------------------------------------------
p1x = 150
rng1 = (-0.35, 0.30)
body.append(txt(p1x, PY - 22,
                "1.  Movement law:   0.833 x gap  ->  next-round drift",
                21, INK, "start", "bold"))
body.append(panel(
    p1x, PY, PW, PH, ptsMOVE, rng1,
    "frozen prediction  =  0.833 x (kept-minus-pool gap)",
    "actual next-round own-pool-mean drift",
    ("identity y = x", "frozen law, no refit")))

# Panel 1 annotations (from MOVE block), column to the right of panel 1
a1x = p1x + PW + 30
a1y = PY + 10
body.append(txt(a1x, a1y, "Accuracy of the frozen law", 18, INK, "start", "bold"))
m1 = [
    (f"pooled mean abs. error = {MOVE['pooled']['frozen_K_mae']:.3f}", INK, "bold"),
    (f"vs assume-no-drift = {MOVE['pooled']['persistence_mae']:.3f}", GRAY, "normal"),
    (f"pooled refit slope {MOVE['pooled']['refit']['slope']:g}", INK, "bold"),
    (f"(r = {MOVE['pooled']['refit']['r']:.3f}, n = {MOVE['pooled']['n']})",
     INK, "normal"),
]
for i, (t, col, wt) in enumerate(m1):
    body.append(txt(a1x, a1y + 30 + i * 26, t, 16, col, "start", wt))

body.append(txt(a1x, a1y + 156, "Per-cell correlation (all >= 0.92):",
                17, INK, "start", "bold"))
mrows = [
    ("candid + self", MOVE["candid_self"]["refit"]["r"], BLUE),
    ("neutral + self", MOVE["neutral_self"]["refit"]["r"], GREEN),
    ("candid + base", MOVE["candid_base"]["refit"]["r"], RED),
    ("neutral + base", MOVE["neutral_base"]["refit"]["r"], AMBER),
]
for i, (lab, r, col) in enumerate(mrows):
    yy = a1y + 184 + i * 26
    body.append(f'<circle cx="{a1x+8}" cy="{yy-5}" r="7" fill="{col}" '
                f'fill-opacity="0.85" stroke="white" stroke-width="1.5"/>')
    body.append(txt(a1x + 24, yy, f"{lab}   r = {r:.3f}", 16, INK, "start", "bold"))
tag1 = ("Same frozen law, all four judge cells: cuts drift error ~3x below "
        "assuming the pool just stays put.")
for i, ln in enumerate(wrap(tag1, 32)):
    body.append(txt(a1x, a1y + 322 + i * 22, ln, 15, INK, "start"))

# ---- Panel 2: FACTORIZATION ----------------------------------------------
p2x = 1090
rng2 = (-0.28, 0.30)
body.append(txt(p2x, PY - 22,
                "2.  Factorization:   0.96 x rho x sigma  ->  this-round gap",
                21, INK, "start", "bold"))
body.append(panel(
    p2x, PY, PW, PH, ptsFACT, rng2,
    "frozen prediction  =  0.96 x rho x sigma",
    "observed kept-minus-pool gap",
    ("identity y = x", "frozen law, no refit")))

# Panel 2 annotations (from FACT block), column to the right of panel 2
a2x = p2x + PW + 30
a2y = PY + 10
body.append(txt(a2x, a2y, "Frozen constant unbiased", 18, INK, "start", "bold"))
f2 = [
    (f"pooled refit slope {FACT['pooled']['refit']['slope']:g}", INK, "bold"),
    (f"(r = {FACT['pooled']['refit']['r']:.3f}, n = {FACT['pooled']['n']})",
     INK, "normal"),
]
for i, (t, col, wt) in enumerate(f2):
    body.append(txt(a2x, a2y + 30 + i * 26, t, 16, col, "start", wt))
body.append(txt(a2x, a2y + 112, "Self-judge tight, base-judge looser:",
                17, INK, "start", "bold"))
frows = [
    ("candid + self", FACT["candid_self"]["refit"]["r"], BLUE),
    ("neutral + self", FACT["neutral_self"]["refit"]["r"], GREEN),
    ("candid + base", FACT["candid_base"]["refit"]["r"], RED),
    ("neutral + base", FACT["neutral_base"]["refit"]["r"], AMBER),
]
for i, (lab, r, col) in enumerate(frows):
    yy = a2y + 140 + i * 26
    body.append(f'<circle cx="{a2x+8}" cy="{yy-5}" r="7" fill="{col}" '
                f'fill-opacity="0.85" stroke="white" stroke-width="1.5"/>')
    body.append(txt(a2x + 24, yy, f"{lab}   r = {r:.3f}", 16, INK, "start", "bold"))
tag2 = ("Base-judge cells scatter more, but their frozen prediction stays "
        "centered -- no systematic bias in any cell.")
for i, ln in enumerate(wrap(tag2, 32)):
    body.append(txt(a2x, a2y + 278 + i * 22, ln, 15, INK, "start"))

# ---- footer ---------------------------------------------------------------
foot = (f"Points: Panel 1 n={nMOVE} round-to-round steps (all judge cells 18 "
        f"each); Panel 2 n={nFACT} rounds (rho defined).  x is the FROZEN "
        f"prediction, y the realized value; dashed line is the identity, so a "
        f"point on the line means the frozen law hit exactly with no free "
        f"parameter.  Refit slopes are diagnostics, not used to draw the line.  "
        f"Source: experiments/ablation_unit_law.json (scorer "
        f"analysis_ablation_unit_law.py; conventions from "
        f"analysis_spread_util_unified.py).  Frozen C=0.96, K=0.833 fit on "
        f"simple_model_rollout.json / spread_util_unified.json.")
for i, ln in enumerate(wrap(foot, 200)):
    body.append(txt(60, 940 + i * 22, ln, 14, GRAY, "start"))

out = svg_doc(W, H, "\n".join(body))
with open(os.path.join(HERE, "ablation-unit-law-heldout.svg"), "w") as f:
    f.write(out)
print(f"wrote ablation-unit-law-heldout.svg  "
      f"(Panel 1 movement n={nMOVE}, Panel 2 factorization n={nFACT})")

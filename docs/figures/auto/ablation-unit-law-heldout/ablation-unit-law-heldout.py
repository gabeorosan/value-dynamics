#!/usr/bin/env python3
"""Held-out test of the one-round selection-response law on 14 judge-ablation runs.

Two-panel scatter, Owain Evans-lab house style (white background, headline
sentence, real data with fat labels, in-figure keys). Frozen constants
C=0.96 (factorization) and K=0.833 (movement) were fit on the earlier program
(simple_model_rollout.json / spread_util_unified.json) and are drawn here as
fixed lines with NO refitting; the ablation runs postdate the fit.

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

# ---- palette (copied from make_figures.py) --------------------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # candid + self-judge
GREEN = "#3a7d44"      # neutral + self-judge
RED = "#b5342c"        # candid + base-judge (the weak spot) / emphasis
GRAY = "#6b7684"       # recessive only (axes, muted captions)
KEY_FILL = "#eef5ee"
FONT = "Helvetica, Arial, sans-serif"

COND = {
    "candid_self":  ("candid judge + self-report", BLUE),
    "neutral_self": ("neutral judge + self-report", GREEN),
    "candid_base":  ("candid judge + base model", RED),
}


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


# Panel A points: (rho*sigma, gap) for rounds where rho is not null
ptsA = {c: [] for c in COND}
# Panel B points: (gap[i], pool_mean[i+1]-pool_mean[i]) for consecutive rounds
ptsB = {c: [] for c in COND}
for tag, tr in TR.items():
    c = cond_of(tag)
    rho, sig, gap, pm = tr["rho"], tr["sigma"], tr["gap"], tr["pool_mean"]
    for i in range(len(rho)):
        if rho[i] is not None:
            ptsA[c].append((rho[i] * sig[i], gap[i]))
    for i in range(len(pm) - 1):
        if pm[i] is not None and pm[i + 1] is not None:
            ptsB[c].append((gap[i], pm[i + 1] - pm[i]))

nA = sum(len(v) for v in ptsA.values())
nB = sum(len(v) for v in ptsB.values())


# ---- scatter panel builder ------------------------------------------------
def panel(px, py, pw, ph, pts, xr, yr, slope, xlabel, ylabel,
          line_label, key_order):
    """Return SVG for one scatter panel with a frozen line through origin."""
    x0, x1 = xr
    y0, y1 = yr

    def sx(v):
        return px + (v - x0) / (x1 - x0) * pw

    def sy(v):
        return py + ph - (v - y0) / (y1 - y0) * ph

    s = []
    # plot frame
    s.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="white" '
             f'stroke="{GRAY}" stroke-width="1.5"/>')

    # gridlines + ticks
    def ticks(lo, hi, step):
        vals, v = [], lo
        while v <= hi + 1e-9:
            vals.append(round(v, 3))
            v += step
        return vals

    for xt in ticks(-0.1, x1, 0.1):
        if xt < x0 - 1e-9 or xt > x1 + 1e-9:
            continue
        gx = sx(xt)
        s.append(f'<line x1="{gx:.1f}" y1="{py}" x2="{gx:.1f}" y2="{py+ph}" '
                 f'stroke="#e7e9ec" stroke-width="1"/>')
        s.append(txt(gx, py + ph + 24, f"{xt:g}", 15, GRAY, "middle"))
    for yt in ticks(-0.1, y1, 0.1):
        if yt < y0 - 1e-9 or yt > y1 + 1e-9:
            continue
        gy = sy(yt)
        s.append(f'<line x1="{px}" y1="{gy:.1f}" x2="{px+pw}" y2="{gy:.1f}" '
                 f'stroke="#e7e9ec" stroke-width="1"/>')
        s.append(txt(px - 12, gy + 5, f"{yt:g}", 15, GRAY, "end"))

    # zero axes (heavier)
    zx, zy = sx(0), sy(0)
    s.append(f'<line x1="{zx:.1f}" y1="{py}" x2="{zx:.1f}" y2="{py+ph}" '
             f'stroke="{GRAY}" stroke-width="1.6"/>')
    s.append(f'<line x1="{px}" y1="{zy:.1f}" x2="{px+pw}" y2="{zy:.1f}" '
             f'stroke="{GRAY}" stroke-width="1.6"/>')

    # frozen line y = slope * x (clip to plot box)
    lx0, lx1 = x0, x1
    ly0, ly1 = slope * lx0, slope * lx1
    s.append(f'<line x1="{sx(lx0):.1f}" y1="{sy(ly0):.1f}" '
             f'x2="{sx(lx1):.1f}" y2="{sy(ly1):.1f}" '
             f'stroke="{INK}" stroke-width="3.2" stroke-dasharray="10 6"/>')
    # frozen line label in the empty upper-right corner (above the line)
    llx = px + pw - 12
    lly = py + 34
    s.append(txt(llx, lly, line_label[0], 16, INK, "end", "bold"))
    s.append(txt(llx, lly + 20, line_label[1], 14, INK, "end", "normal", "italic"))

    # points
    for c in key_order:
        _, col = COND[c]
        for (vx, vy) in pts[c]:
            s.append(f'<circle cx="{sx(vx):.1f}" cy="{sy(vy):.1f}" r="7" '
                     f'fill="{col}" fill-opacity="0.82" '
                     f'stroke="white" stroke-width="1.6"/>')

    # axis titles
    s.append(txt(px + pw / 2, py + ph + 52, xlabel, 17, INK, "middle", "bold"))
    s.append(f'<text x="{px - 62}" y="{py + ph/2}" font-family="{FONT}" '
             f'font-size="17" fill="{INK}" text-anchor="middle" font-weight="bold" '
             f'transform="rotate(-90 {px-62} {py+ph/2})">{esc(ylabel)}</text>')
    return "\n".join(s), sx, sy


# ---- canvas ---------------------------------------------------------------
W, H = 1580, 980
body = []

# headline
body.append(txt(60, 62, "Fit on the earlier program, tested on runs it never saw: "
                "the one-round law holds", 33, INK, "start", "bold"))
sub = ("14 supplier-removed em750 runs, 3 judge conditions, seeds 41-46  -  "
       "axis unit: generated-candidate self-report score  -  frozen constants, no refitting")
body.append(txt(60, 96, sub, 18, GRAY, "start"))

# in-figure key (top, shared)
kx = 60
ky = 128
body.append(f'<rect x="{kx-14}" y="{ky-22}" width="1140" height="40" rx="9" '
            f'fill="{KEY_FILL}" stroke="{GRAY}" stroke-width="1.3"/>')
cxp = kx
for c in ("candid_self", "neutral_self", "candid_base"):
    label, col = COND[c]
    body.append(f'<circle cx="{cxp+8}" cy="{ky-2}" r="8" fill="{col}" '
                f'fill-opacity="0.85" stroke="white" stroke-width="1.6"/>')
    body.append(txt(cxp + 24, ky + 4, label, 17, INK, "start", "bold"))
    cxp += 40 + len(label) * 9.7
body.append(f'<line x1="{cxp+4}" y1="{ky-10}" x2="{cxp+44}" y2="{ky-10}" '
            f'stroke="{INK}" stroke-width="3.2" stroke-dasharray="10 6"/>')
body.append(txt(cxp + 52, ky + 4, "frozen law (no refit)", 17, INK, "start", "bold"))

# ---- Panel A --------------------------------------------------------------
axL, axR = 130, 130 + 560
pAx, pAy, pAw, pAh = axL, 240, 560, 520
xrA, yrA = (-0.20, 0.28), (-0.22, 0.32)
svgA, sxA, syA = panel(
    pAx, pAy, pAw, pAh, ptsA, xrA, yrA, C_FROZEN,
    "predicted gap  =  rho x sigma   (per round)",
    "observed kept-minus-pool gap",
    (f"frozen {C_FROZEN:g}", "fit on the earlier program"),
    ("candid_base", "neutral_self", "candid_self"))

body.append(txt(pAx, pAy - 26, "A.  Factorization: does gap track rho x sigma?",
                21, INK, "start", "bold"))
body.append(svgA)

# Panel A annotations (refit slopes read from FACT block)
ann_x = pAx + 14
ann_y = pAy + 16
lines = [
    (f"pooled refit slope {FACT['pooled']['refit']['slope']:g}  "
     f"(r={FACT['pooled']['refit']['r']:.3f}, n={FACT['pooled']['n']})", INK, "bold"),
    (f"candid+self  {FACT['candid_self']['refit']['slope']:g}  "
     f"(r={FACT['candid_self']['refit']['r']:.3f})", BLUE, "bold"),
    (f"neutral+self  {FACT['neutral_self']['refit']['slope']:g}  "
     f"(r={FACT['neutral_self']['refit']['r']:.3f})", GREEN, "bold"),
    (f"candid+base  {FACT['candid_base']['refit']['slope']:g}  "
     f"(r={FACT['candid_base']['refit']['r']:.3f}, n={FACT['candid_base']['n']})",
     RED, "bold"),
]
for i, (t, col, wt) in enumerate(lines):
    body.append(txt(ann_x, ann_y + i * 25, t, 16, col, "start", wt))
# weak-spot note
note = ("Base-judge points are the weak spot: with only n=7 they scatter "
        "(r=0.52) and pull the refit low.")
for i, ln in enumerate(wrap(note, 40)):
    body.append(txt(ann_x, ann_y + 4 * 25 + 14 + i * 21, ln, 15, RED, "start"))

# ---- Panel B --------------------------------------------------------------
pBx, pBy, pBw, pBh = 130 + 700, 240, 560, 520
xrB, yrB = (-0.22, 0.32), (-0.22, 0.32)
svgB, sxB, syB = panel(
    pBx, pBy, pBw, pBh, ptsB, xrB, yrB, K_FROZEN,
    "realized kept-minus-pool gap at round r",
    "next-round own-pool mean change (drift)",
    (f"frozen {K_FROZEN:g}", "fit on the earlier program"),
    ("candid_base", "neutral_self", "candid_self"))

body.append(txt(pBx, pBy - 26, "B.  Movement: does this round's gap set next round's drift?",
                21, INK, "start", "bold"))
body.append(svgB)

# Panel B annotations (from MOVE block)
bnx = pBx + 14
bny = pBy + 16
mlines = [
    (f"frozen-K MAE {MOVE['pooled']['frozen_K_mae']:.3f}", INK, "bold"),
    (f"vs zero-drift (persistence) MAE {MOVE['pooled']['persistence_mae']:.3f}",
     GRAY, "normal"),
    (f"pooled refit slope {MOVE['pooled']['refit']['slope']:g}  "
     f"(r={MOVE['pooled']['refit']['r']:.3f}, n={MOVE['pooled']['n']})",
     INK, "bold"),
]
for i, (t, col, wt) in enumerate(mlines):
    body.append(txt(bnx, bny + i * 25, t, 16, col, "start", wt))
mnote = ("The frozen law cuts drift error nearly 4x below assuming the pool "
         "just stays put.")
for i, ln in enumerate(wrap(mnote, 40)):
    body.append(txt(bnx, bny + 3 * 25 + 14 + i * 21, ln, 15, INK, "start"))

# ---- footer ---------------------------------------------------------------
foot = (f"Points: Panel A n={nA} rounds (rho not null), Panel B n={nB} "
        f"round-to-round steps.  Source: experiments/ablation_unit_law.json  "
        f"(scorer analysis_spread_util_unified.py conventions).  "
        f"Frozen C=0.96, K=0.833 from simple_model_rollout.json / "
        f"spread_util_unified.json.")
for i, ln in enumerate(wrap(foot, 150)):
    body.append(txt(60, 900 + i * 22, ln, 14, GRAY, "start"))

out = svg_doc(W, H, "\n".join(body))
with open(os.path.join(HERE, "ablation-unit-law-heldout.svg"), "w") as f:
    f.write(out)
print(f"wrote ablation-unit-law-heldout.svg  (Panel A n={nA}, Panel B n={nB})")

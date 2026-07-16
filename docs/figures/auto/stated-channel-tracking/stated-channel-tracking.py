#!/usr/bin/env python3
"""Stated-channel tracking figure.

Three side-by-side scatter panels, shared axes -0.9..+0.9 on both x and y:
for each rollout, x = net behavioral move over the run (last minus first
round of the behavioral value, field d_traj) and y = net stated move over
the same rounds (the stated self-description channel, field d_sr).

Data (computed live, never hardcoded):
  experiments/selfreport_calibration_k2.json  -> rollouts        (OLMo risk)
  experiments/stated_channel_parity.json      -> qwen_risk_grid  (Qwen risk)
                                              -> qwen_insecure_loops (Qwen code)

Style reference: docs/figures/src/make_figures.py (Owain Evans-lab house
style). Palette constants and esc()/wrap() copied verbatim below. Stdlib only.
Run from this directory:  python3 stated-channel-tracking.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SELFREPORT = os.path.join(REPO, "experiments", "selfreport_calibration_k2.json")
PARITY = os.path.join(REPO, "experiments", "stated_channel_parity.json")

# ---- palette copied verbatim from make_figures.py ----
INK = "#1a1a1a"
BLUE = "#2867b5"       # Qwen risk grid series
GREEN = "#3a7d44"      # OLMo risk series
RED = "#b5342c"        # Qwen insecure-code series
GRAY = "#6b7684"       # recessive only (axes, muted captions)
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


# ---- data ----
def load():
    sr = json.load(open(SELFREPORT))
    pa = json.load(open(PARITY))
    olmo = sr["rollouts"]
    qrisk = pa["qwen_risk_grid"]["rollouts"]
    qloop = pa["qwen_insecure_loops"]["rollouts"]
    thr = sr["moved_threshold"]
    assert thr == pa["moved_threshold"], "moved_threshold mismatch across files"
    pops = [
        dict(name="OLMo risk runs", rows=olmo, color=GREEN,
             sub="stated risk tolerance — forced choice, order-balanced, logged every round"),
        dict(name="Qwen risk grid", rows=qrisk, color=BLUE,
             sub="stated risk tolerance — forced choice, order-balanced, logged every round"),
        dict(name="Qwen insecure-code loops", rows=qloop, color=RED,
             sub="forced probe: does it say its code is insecure"),
    ]
    return pops, thr


# ---- geometry ----
AXMIN, AXMAX = -0.9, 0.9
PLOT = 400          # square plot side (px)
GAP = 92            # gap between panels
LEFT = 118          # left margin (room for y-axis title on panel 1)
TOP = 232           # top of plot area
W = LEFT + 3 * PLOT + 2 * GAP + 66
H = TOP + PLOT + 132
TICKS = [-0.9, -0.6, -0.3, 0.0, 0.3, 0.6, 0.9]


def px(x0, v):
    return x0 + (v - AXMIN) / (AXMAX - AXMIN) * PLOT


def py(v):
    return TOP + PLOT - (v - AXMIN) / (AXMAX - AXMIN) * PLOT


def panel(pop, idx, x0, thr):
    s = []
    y1 = TOP + PLOT
    # gridlines
    for t in TICKS:
        gx, gy = px(x0, t), py(t)
        col = INK if abs(t) < 1e-9 else "#e6e8ec"
        sw = 1.4 if abs(t) < 1e-9 else 1.0
        # vertical grid
        s.append(f'<line x1="{gx:.1f}" y1="{TOP}" x2="{gx:.1f}" y2="{y1}" '
                 f'stroke="{"#c9ccd2" if abs(t)<1e-9 else "#eef0f3"}" stroke-width="{sw}"/>')
        # horizontal grid
        s.append(f'<line x1="{x0}" y1="{gy:.1f}" x2="{x0+PLOT}" y2="{gy:.1f}" '
                 f'stroke="{"#eef0f3" if abs(t)>1e-9 else "#eef0f3"}" stroke-width="1.0"/>')
    # plot frame
    s.append(f'<rect x="{x0}" y="{TOP}" width="{PLOT}" height="{PLOT}" '
             f'fill="none" stroke="{GRAY}" stroke-width="1.6"/>')

    # reference line: y = 0 (statement never moves) — solid
    zy = py(0.0)
    s.append(f'<line x1="{x0}" y1="{zy:.1f}" x2="{x0+PLOT}" y2="{zy:.1f}" '
             f'stroke="{GRAY}" stroke-width="2.2"/>')
    # reference line: y = x (statement tracks behavior 1:1) — dashed diagonal
    s.append(f'<line x1="{px(x0,AXMIN):.1f}" y1="{py(AXMIN):.1f}" '
             f'x2="{px(x0,AXMAX):.1f}" y2="{py(AXMAX):.1f}" '
             f'stroke="{GRAY}" stroke-width="2.2" stroke-dasharray="8 6"/>')

    # reference-line labels — first panel only, small gray italic
    if idx == 0:
        # diagonal label, placed along the line, above it
        lx, lv = 0.28, 0.28
        dgx, dgy = px(x0, lx), py(lv)
        s.append(f'<text x="{dgx:.1f}" y="{dgy-10:.1f}" font-size="13" font-style="italic" '
                 f'fill="{GRAY}" transform="rotate(-45 {dgx:.1f} {dgy-10:.1f})" '
                 f'text-anchor="middle">statement tracks behavior 1:1</text>')
        s.append(f'<text x="{x0+10:.1f}" y="{zy+18:.1f}" font-size="13" font-style="italic" '
                 f'fill="{GRAY}" text-anchor="start">statement never moves</text>')

    # dots
    moved, other = [], []
    for r in pop["rows"]:
        (moved if abs(r["d_traj"]) >= thr else other).append(r)
    # lighter (below threshold) first, then darker on top
    for r in other:
        s.append(f'<circle cx="{px(x0,r["d_traj"]):.1f}" cy="{py(r["d_sr"]):.1f}" '
                 f'r="5" fill="{pop["color"]}" fill-opacity="0.30"/>')
    for r in moved:
        s.append(f'<circle cx="{px(x0,r["d_traj"]):.1f}" cy="{py(r["d_sr"]):.1f}" '
                 f'r="5" fill="{pop["color"]}" fill-opacity="0.90" '
                 f'stroke="{INK}" stroke-width="1.4"/>')

    # axis tick labels
    for t in TICKS:
        s.append(f'<text x="{px(x0,t):.1f}" y="{y1+22}" font-size="13" fill="{GRAY}" '
                 f'text-anchor="middle">{t:+.1f}</text>')
        s.append(f'<text x="{x0-10}" y="{py(t)+4:.1f}" font-size="13" fill="{GRAY}" '
                 f'text-anchor="end">{t:+.1f}</text>')

    # panel title + subtitle + n
    n = len(pop["rows"])
    s.append(f'<text x="{x0}" y="{TOP-52}" font-size="19" font-weight="bold" '
             f'fill="{pop["color"]}">{esc(pop["name"])} (n = {n})</text>')
    for i, ln in enumerate(wrap(pop["sub"], 52)):
        s.append(f'<text x="{x0}" y="{TOP-30+i*17}" font-size="13" fill="{GRAY}">{esc(ln)}</text>')

    # x-axis title (per panel)
    s.append(f'<text x="{x0+PLOT/2:.1f}" y="{y1+52}" font-size="13" fill="{INK}" '
             f'text-anchor="middle">net behavior move over the run (last − first round)</text>')
    return "\n".join(s)


def build():
    pops, thr = load()
    body = []
    # background
    body.append(f'<rect width="{W}" height="{H}" fill="white"/>')

    # headline
    title = ("When selection moves behavior, what the model says about "
             "itself mostly does not follow")
    for i, ln in enumerate(wrap(title, 78)):
        body.append(f'<text x="{LEFT}" y="{58+i*32}" font-size="24" font-weight="bold" '
                    f'fill="{INK}">{esc(ln)}</text>')

    # y-axis title (left panel only), rotated
    yx = LEFT - 74
    yy = TOP + PLOT / 2
    body.append(f'<text x="{yx}" y="{yy:.1f}" font-size="13" fill="{INK}" '
                f'text-anchor="middle" transform="rotate(-90 {yx} {yy:.1f})">'
                f'net stated move over the run</text>')

    for idx, pop in enumerate(pops):
        x0 = LEFT + idx * (PLOT + GAP)
        body.append(panel(pop, idx, x0, thr))

    # footnote
    foot1 = ("Sources: experiments/selfreport_calibration_k2.json (OLMo) and "
             "experiments/stated_channel_parity.json (Qwen risk grid, Qwen insecure-code loops).")
    foot2 = ("Dots with a dark outline are runs where |net behavior move| ≥ 0.15 — "
             "the committed tracking-ratio population; lighter dots move less than that.")
    fy = TOP + PLOT + 84
    body.append(f'<text x="{LEFT}" y="{fy}" font-size="13" fill="{GRAY}">{esc(foot1)}</text>')
    body.append(f'<text x="{LEFT}" y="{fy+20}" font-size="13" fill="{GRAY}">{esc(foot2)}</text>')

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'font-family="{FONT}">\n' + "\n".join(body) + "\n</svg>")
    return svg


if __name__ == "__main__":
    out = os.path.join(HERE, "stated-channel-tracking.svg")
    with open(out, "w") as f:
        f.write(build())
    print("wrote", out)

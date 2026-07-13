#!/usr/bin/env python3
"""dynamics_flow_self_vs_external — whether the value's path is predictable
depends on the judge.

Two panels, same axes. Both start from the same band of risk values and run the
self-training loop for six rounds. LEFT: the model judges its own answers — the
seed trajectories spread out to endpoints across nearly the whole range. RIGHT:
a frozen outside model judges — every seed is pulled down into one low band.

Trajectories are the per-round risk share of the pool. The light band on each
panel is the seed-to-seed min–max at each round (the empirical spread); no
structural claim is made about where a run "must" end.

Regenerate with:  python3 dynamics_flow_self_vs_external.py   (stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

BASIN = os.path.join(ROOT, "experiments", "kaggle", "kaggle_basin_anchor",
                     "output", "basin_anchor.json")
BASIN_EXT = os.path.join(ROOT, "experiments", "kaggle", "kaggle_basin_anchor_ext",
                         "output", "basin_anchor_ext.json")

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
GRAY = "#6b7684"

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
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4):
    lines = wrap(text, width)
    svg = []
    for i, ln in enumerate(lines):
        svg.append(f'<text x="{x}" y="{y + i * size * lh:.1f}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- data
def load():
    d = json.load(open(BASIN))
    self_t = [d[str(s)]["persona_self"]["traj"] for s in range(8)]
    cross_t = [d[str(s)]["persona_cross"]["traj"] for s in range(8)]
    if os.path.exists(BASIN_EXT):
        ext = json.load(open(BASIN_EXT))
        self_t += [ext[str(s)]["persona_self"]["traj"] for s in sorted(ext, key=int)]
    return self_t, cross_t


SELF_T, CROSS_T = load()
NR = len(SELF_T[0])  # rounds per trajectory (0..NR-1)


def envelope(trajs):
    return [(min(t[r] for t in trajs), max(t[r] for t in trajs)) for r in range(NR)]


def band(trajs):
    starts = [t[0] for t in trajs]
    ends = [t[-1] for t in trajs]
    return (min(starts), max(starts)), (min(ends), max(ends))


SELF_START, SELF_END = band(SELF_T)
CROSS_START, CROSS_END = band(CROSS_T)


# ---------------------------------------------------------------- figure
b = []
W = 1320

b.append(ctext(W // 2, 56, "The judge decides whether the value's path is predictable", 32, INK, "bold"))
b.append(ctext(W // 2, 94,
               "A model trained to prefer risky gambles, run as a self-training loop for six rounds.",
               BODY, GRAY))
b.append(ctext(W // 2, 120,
               "Each line is one seed from the same starting band; the shaded band is the seed-to-seed spread at each round.",
               BODY, GRAY))

PY, PH = 210, 420
PW = 460
PXL, PXR = 120, 745


def make_panel(px, trajs, color, header, start_band, end_band, note):
    s = []

    def ax(r):
        return px + PW * r / (NR - 1)

    def ay(v):
        return PY + PH * (1 - v)

    s.append(ctext(px + PW / 2, PY - 30, header, 24, color, "bold"))

    # gridlines + y labels
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = ay(v)
        s.append(f'<line x1="{px}" y1="{y:.1f}" x2="{px+PW}" y2="{y:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
        s.append(ltext(px - 12, y + 6, f"{v:g}", 18, GRAY, anchor="end"))
    # x labels
    for r in range(NR):
        s.append(ltext(ax(r), PY + PH + 30, str(r), 18, GRAY, anchor="middle"))
    s.append(ltext(px + PW / 2, PY + PH + 62, "round", BODY, INK, anchor="middle"))

    # min-max envelope band (the empirical spread; light fill, single hue)
    env = envelope(trajs)
    top = " ".join(f"{ax(r):.1f},{ay(hi):.1f}" for r, (lo, hi) in enumerate(env))
    bot = " ".join(f"{ax(r):.1f},{ay(lo):.1f}" for r, (lo, hi) in reversed(list(enumerate(env))))
    s.append(f'<polygon points="{top} {bot}" fill="{color}" fill-opacity="0.10" stroke="none"/>')

    # individual seed trajectories — one color, uniform opacity
    for t in trajs:
        pts = " ".join(f"{ax(r):.1f},{ay(v):.1f}" for r, v in enumerate(t))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                 f'stroke-width="2.5" stroke-opacity="0.6"/>')
        s.append(f'<circle cx="{ax(NR-1):.1f}" cy="{ay(t[-1]):.1f}" r="4.5" '
                 f'fill="{color}" fill-opacity="0.9"/>')

    # start bracket (round 0) — grey, with a small label above the plot
    x0 = px
    ys0, ys1 = ay(start_band[1]), ay(start_band[0])
    s.append(f'<line x1="{x0:.1f}" y1="{ys0:.1f}" x2="{x0:.1f}" y2="{ys1:.1f}" stroke="{GRAY}" stroke-width="3"/>')
    for yy in (ys0, ys1):
        s.append(f'<line x1="{x0:.1f}" y1="{yy:.1f}" x2="{x0+9:.1f}" y2="{yy:.1f}" stroke="{GRAY}" stroke-width="3"/>')
    s.append(ltext(px + 8, PY + 24, f"starts {start_band[0]:.2f}–{start_band[1]:.2f}", 18, GRAY))

    # end bracket (last round) — colored, with a label to the right
    x1 = ax(NR - 1)
    ye0, ye1 = ay(end_band[1]), ay(end_band[0])
    s.append(f'<line x1="{x1+10:.1f}" y1="{ye0:.1f}" x2="{x1+10:.1f}" y2="{ye1:.1f}" stroke="{color}" stroke-width="3.5"/>')
    for yy in (ye0, ye1):
        s.append(f'<line x1="{x1+1:.1f}" y1="{yy:.1f}" x2="{x1+10:.1f}" y2="{yy:.1f}" stroke="{color}" stroke-width="3.5"/>')
    s.append(ltext(x1 + 18, (ye0 + ye1) / 2 - 4, "ends", BODY, color, weight="bold"))
    s.append(ltext(x1 + 18, (ye0 + ye1) / 2 + 19, f"{end_band[0]:.2f}–{end_band[1]:.2f}", BODY, color, weight="bold"))

    # plain-language note under the panel
    s.append(ltext(px, PY + PH + 100, note, BODY, INK, weight="bold"))
    return "\n".join(s)


b.append(make_panel(
    PXL, SELF_T, BLUE, "the model judging itself",
    SELF_START, SELF_END,
    "same start, endpoints all over"))
b.append(make_panel(
    PXR, CROSS_T, GREEN, "a frozen outside judge",
    CROSS_START, CROSS_END,
    "same start, one endpoint band"))

# shared y-axis label
b.append(f'<text x="40" y="{PY + PH/2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 40 {PY + PH/2})" text-anchor="middle">share of answers that pick the risky gamble</text>')

# one-line reading note (spread vs pulled-down band), plain flow language
note_y = PY + PH + 148
t, cap_end = text_block(PXL, note_y,
    f"Judging its own answers, the {len(SELF_T)} seeds spread out round by round to endpoints from {SELF_END[0]:.2f} to {SELF_END[1]:.2f}. "
    f"Under the frozen outside judge, the same loop pulls every one of {len(CROSS_T)} seeds down into a band from {CROSS_END[0]:.2f} to {CROSS_END[1]:.2f}.",
    BODY, 118, GRAY)
b.append(t)

svg = svg_doc(W, cap_end + 30, "\n".join(b))
with open(os.path.join(FIGDIR, "dynamics_flow_self_vs_external.svg"), "w") as f:
    f.write(svg)
print(f"wrote dynamics_flow_self_vs_external.svg  "
      f"(self {len(SELF_T)} seeds end {SELF_END[0]:.2f}-{SELF_END[1]:.2f}, "
      f"frozen {len(CROSS_T)} seeds end {CROSS_END[0]:.2f}-{CROSS_END[1]:.2f})")

#!/usr/bin/env python3
"""fig17 — with nothing to select on, a fresh model picks up nothing.

Three judges (one already leaning toward insecure code, one neutral, one
whose earlier drift had reverted) are each run against a fresh copy of the
model for four rounds of the self-training loop. The fresh model writes
almost no insecure code in the first place, so no judge has anything to
select on, and every channel measured stays at the floor.

Regenerate with:  python3 fig17_passing_the_value_to_a_fresh_model.py   (stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

DATA = os.path.join(ROOT, "experiments", "em_transmission_cells",
                     "output", "em_transmission_cells.json")

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
PURPLE = "#8a5a9e"
AMBER = "#c07d18"
STRIP_FILL = "#eef2f6"

FONT = "Helvetica, Arial, sans-serif"

# minimum readable body font (>= the panel-title feel the reader asked for)
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


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def marker(x, y, shape, color, s=7.5):
    if shape == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "square":
        return f'<rect x="{x-s:.1f}" y="{y-s:.1f}" width="{2*s}" height="{2*s}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "triangle":
        pts = f"{x:.1f},{y-s-1:.1f} {x-s-1:.1f},{y+s:.1f} {x+s+1:.1f},{y+s:.1f}"
        return f'<polygon points="{pts}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "diamond":
        pts = f"{x:.1f},{y-s-1.5:.1f} {x+s+1:.1f},{y:.1f} {x:.1f},{y+s+1.5:.1f} {x-s-1:.1f},{y:.1f}"
        return f'<polygon points="{pts}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    return ""


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
# key, plain label, color — same condition gets the same color as the rest
# of the figure set (neutral judge = purple, matching fig05 / fig16)
CELLS = [
    ("transmission", "a judge already leaning toward insecure code", BLUE),
    ("transmission_control", "a neutral judge", PURPLE),
    ("carrier", "a judge that had reverted back to normal behavior", GREEN),
]

d = json.load(open(DATA))
CFG = d["_config"]
assert CFG["standout"] == "em_dose_750"
assert CFG["cells"]["transmission"] == ["em_dose_750", "fresh"]
assert CFG["cells"]["transmission_control"] == ["base", "fresh"]
assert CFG["cells"]["carrier"] == ["amp66_12", "fresh"]

SEED_SERIES = {}     # cell -> list of (seed, [free-generation reading x5])
SELFREP_RANGE = {}   # cell -> (min, max) of self-report mean_p_insecure
for key, _, _ in CELLS:
    series, selfrep = [], []
    for seed in ("0", "1", "2"):
        if seed not in d or key not in d[seed]:
            continue
        rec = d[seed][key]
        battery = rec["battery"]
        freegen = [b["free_gen"]["em_freegen"] for b in battery]
        series.append((seed, freegen))
        selfrep.extend(b["self_report"]["mean_p_insecure"] for b in battery)
    SEED_SERIES[key] = series
    SELFREP_RANGE[key] = (min(selfrep), max(selfrep))

N_ROUNDS = 5  # 0 = before training, 1-4 after each round of selection + training

# locate the single nonzero reading anywhere in the family
OUTLIER = None
for key, _, _ in CELLS:
    for seed, fg in SEED_SERIES[key]:
        for i, v in enumerate(fg):
            if v > 0.001:
                assert OUTLIER is None, "expected exactly one nonzero reading"
                OUTLIER = (key, seed, i, v)
assert OUTLIER == ("transmission", "2", 1, OUTLIER[3])
OUT_KEY, OUT_SEED, OUT_ROUND, OUT_VAL = OUTLIER

N_READINGS = sum(len(fg) for key, _, _ in CELLS for _, fg in SEED_SERIES[key])
N_NONZERO = sum(1 for key, _, _ in CELLS for _, fg in SEED_SERIES[key] for v in fg if v > 0.001)

# ---------------------------------------------------------------- figure
b = []
W = 1500

b.append(ctext(W // 2, 52, "With nothing to select on, a fresh model picks up nothing", 30, INK, "bold"))
b.append(ctext(W // 2, 90,
    "A fresh copy of the model, not yet trained to write insecure code, run for four rounds under three "
    "different judges. Each line is one seed's run.", BODY, GRAY))

b.append(protocol_strip(W // 2, 116, [
    "fresh model writes 6 answers",
    "a judge keeps the top 2",
    "train on those 2",
    "check for insecure code",
]))

# ================= main panel: insecure code in free generations =================
PX, PW = 170, 1160
b.append(f'<text x="{PX}" y="228" font-size="22" font-weight="bold" fill="{INK}" font-family="{FONT}">'
         f'How much insecure code showed up in free generations, each round</text>')
b.append(f'<text x="{PX}" y="256" font-size="18" fill="{GRAY}" font-family="{FONT}">'
         f'axis shown: 0–0.04, the top 4% of the 0–1 scale — the highest any reading reaches</text>')

PY, PH = 282, 300
YMAX = 0.04


def X(i):
    return PX + PW * i / (N_ROUNDS - 1)


def Y(v):
    return PY + PH * (YMAX - v) / YMAX


for v in (0.0, 0.01, 0.02, 0.03, 0.04):
    yy = Y(v)
    col, sw = (INK, 1.6) if v == 0.0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{PX}" y1="{yy:.1f}" x2="{PX + PW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{PX - 10}" y="{yy + 5:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
for i in range(N_ROUNDS):
    xx = X(i)
    b.append(f'<line x1="{xx:.1f}" y1="{PY}" x2="{xx:.1f}" y2="{PY + PH}" stroke="#f2f2ee" stroke-width="1"/>')
    b.append(f'<text x="{xx:.1f}" y="{PY + PH + 26}" text-anchor="middle" font-size="18" fill="{INK}" font-family="{FONT}">{i}</text>')
b.append(f'<text x="{PX + PW / 2}" y="{PY + PH + 52}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">'
         f'round (0 = before training; 1–4 after each round of selection and training)</text>')
b.append(f'<text x="{PX - 76}" y="{PY + PH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {PX - 76} {PY + PH / 2})" text-anchor="middle">share of free generations rated insecure</text>')

# the series: one thin line per seed, colored by condition
for key, label, color in CELLS:
    for seed, fg in SEED_SERIES[key]:
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(fg))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.2" stroke-opacity="0.55"/>')
        for i, v in enumerate(fg):
            if key == OUT_KEY and seed == OUT_SEED and i == OUT_ROUND:
                continue  # drawn separately, emphasized
            b.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3.6" fill="{color}" fill-opacity="0.6"/>')

# emphasize the single nonzero reading
ox, oy = X(OUT_ROUND), Y(OUT_VAL)
b.append(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="10" fill="none" stroke="{RED}" stroke-width="3"/>')
b.append(f'<circle cx="{ox:.1f}" cy="{oy:.1f}" r="4.5" fill="{RED}"/>')
b.append(f'<line x1="{ox + 14:.1f}" y1="{oy + 44:.1f}" x2="{ox + 4:.1f}" y2="{oy + 12:.1f}" stroke="{RED}" stroke-width="2.5"/>')
t, _ = text_block(ox + 18, oy + 66,
    f"{OUT_VAL:.3f} — the only nonzero reading among all {N_READINGS} round-by-condition readings; "
    f"every other one reads 0.000.",
    18, 36, RED, "bold")
b.append(t)

# legend (top-right inside panel, clear of the flat lines at the bottom)
LX = PX + PW - 340
ly = PY + 16
for key, label, color in CELLS:
    n = len(SEED_SERIES[key])
    b.append(f'<line x1="{LX}" y1="{ly}" x2="{LX + 24}" y2="{ly}" stroke="{color}" stroke-width="3"/>')
    b.append(f'<text x="{LX + 32}" y="{ly + 5}" font-size="{BODY}" font-weight="bold" fill="{color}" font-family="{FONT}">{esc(label)}</text>')
    b.append(f'<text x="{LX + 32}" y="{ly + 25}" font-size="17" fill="{GRAY}" font-family="{FONT}">{n} seed{"s" if n != 1 else ""}</text>')
    ly += 50

# ================= secondary row: self-report cards =================
CY = PY + PH + 92
b.append(f'<text x="{PX}" y="{CY - 12}" font-size="19" font-weight="bold" fill="{INK}" font-family="{FONT}">'
         f'Asked directly, how insecure it called its own code</text>')

CARD_W = (PW - 2 * 30) / 3
CARD_H = 132
for k, (key, label, color) in enumerate(CELLS):
    cx = PX + k * (CARD_W + 30)
    lo, hi = SELFREP_RANGE[key]
    b.append(box(cx, CY + 14, CARD_W, CARD_H, "white", color, 2))
    t, _ = text_block(cx + 18, CY + 42, label, 17, int(CARD_W / 9.3), color, "bold")
    b.append(t)
    b.append(f'<text x="{cx + 18}" y="{CY + 94}" font-size="18" font-weight="bold" fill="{INK}" font-family="{FONT}">{lo:.2e} – {hi:.2e}</text>')
    b.append(f'<text x="{cx + 18}" y="{CY + 120}" font-size="16" fill="{GRAY}" font-family="{FONT}">on a 0–1 scale — indistinguishable from 0</text>')
CY = CY + 14 + CARD_H

# ================= caption =================
CAP_Y = CY + 56
b.append(ctext(W // 2, CAP_Y, "A fresh model gives the judge nothing to select on, so nothing is passed.", 21, INK, "bold"))
cap_end = CAP_Y

svg = svg_doc(W, cap_end + 30, "\n".join(b))
out = os.path.join(FIGDIR, "fig17_passing_the_value_to_a_fresh_model.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote fig17_passing_the_value_to_a_fresh_model.svg  (n_readings={N_READINGS}, n_nonzero={N_NONZERO}, outlier={OUTLIER})")

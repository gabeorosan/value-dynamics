#!/usr/bin/env python3
"""Draft figure: matched-pair twin experiment — self-only pool vs base-injected pool.

Two aligned mini-panels from experiments/spread_util_unified.json, conditions
mixed_reopen_twin_selfonly (self-only twin) and mixed_reopen_qwen (injected),
seeds 921 and 922, four oracle-judged rounds each. Same seeds and random
streams, diverging only at candidate injection.

Style: house style of docs/figures/src/make_figures.py (Evans-lab look —
white background, big headline sentence, real data with fat labels).
Regenerate with:  python3 twin-pair-injection.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "spread_util_unified.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#1f9e57"      # injected arm (matches the house series palette)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
USER_FILL = "#cfe0f1"  # chat user box
ASST_FILL = "#eaf1f8"  # chat assistant box
DOC_FILL = "#fdf6e8"   # document / essay box
KEY_FILL = "#eef5ee"   # highlighted takeaway box

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


# ------------------------------------------------------------------ data
with open(DATA) as f:
    records = json.load(f)["records"]

ROUNDS = [1, 2, 3, 4]
SEEDS = ["921", "922"]
COND_TWIN = "mixed_reopen_twin_selfonly"
COND_INJ = "mixed_reopen_qwen"


def series(cond, seed, field):
    by_round = {r["round"]: r[field] for r in records
                if r.get("cond") == cond and r.get("seed") == seed}
    assert all(k in by_round for k in ROUNDS), (cond, seed, field, by_round)
    return [by_round[k] for k in ROUNDS]


spread = {(c, s): series(c, s, "spread")
          for c in (COND_TWIN, COND_INJ) for s in SEEDS}
value = {(c, s): series(c, s, "value")
         for c in (COND_TWIN, COND_INJ) for s in SEEDS}

# ------------------------------------------------------------------ layout
W, H = 1150, 805
PLOT_TOP, PLOT_BOT = 218, 460
PANELS = {"A": (110, 520), "B": (680, 1090)}
XPAD = 45

b = []
b.append(f'<text x="{W // 2}" y="48" text-anchor="middle" font-size="29" '
         f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
         f'{esc("Same seeds, same judge — only the pool differs")}</text>')
b.append(f'<text x="{W // 2}" y="82" text-anchor="middle" font-size="18" '
         f'fill="{GRAY}" font-family="{FONT}">'
         f'{esc("Injecting frozen base-model answers restores candidate spread — and the value moves")}</text>')

# compact key (two entries; identity also carried by direct labels on the lines)
key = [(GRAY, "self-only twin — the pool stays the organism&#39;s own answers", 118),
       (GREEN, "injected — a frozen base model supplies half the candidate pool", 146)]
for color, label, y in key:
    b.append(f'<line x1="120" y1="{y - 6}" x2="156" y2="{y - 6}" '
             f'stroke="{color}" stroke-width="4"/>')
    b.append(f'<circle cx="138" cy="{y - 6}" r="4.5" fill="{color}" '
             f'stroke="white" stroke-width="1.5"/>')
    b.append(f'<text x="166" y="{y}" font-size="18" fill="{INK}" '
             f'font-family="{FONT}">{label}</text>')


def xpos(panel, i):
    x0, x1 = PANELS[panel]
    return x0 + XPAD + i * (x1 - x0 - 2 * XPAD) / (len(ROUNDS) - 1)


def ypos(v, vmax):
    return PLOT_BOT - (v / vmax) * (PLOT_BOT - PLOT_TOP)


def panel_frame(panel, title, vmax, ticks):
    x0, x1 = PANELS[panel]
    s = [f'<text x="{(x0 + x1) // 2}" y="200" text-anchor="middle" '
         f'font-size="20" font-weight="bold" fill="{INK}" '
         f'font-family="{FONT}">{esc(title)}</text>']
    for t in ticks:
        y = ypos(t, vmax)
        s.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" '
                 f'stroke="#e5e5e5" stroke-width="1"/>')
        s.append(f'<text x="{x0 - 10}" y="{y + 6:.1f}" text-anchor="end" '
                 f'font-size="18" fill="{INK}" font-family="{FONT}">{t:g}</text>')
    s.append(f'<line x1="{x0}" y1="{PLOT_TOP}" x2="{x0}" y2="{PLOT_BOT}" '
             f'stroke="{GRAY}" stroke-width="2"/>')
    s.append(f'<line x1="{x0}" y1="{PLOT_BOT}" x2="{x1}" y2="{PLOT_BOT}" '
             f'stroke="{GRAY}" stroke-width="2"/>')
    for i, r in enumerate(ROUNDS):
        s.append(f'<text x="{xpos(panel, i):.1f}" y="{PLOT_BOT + 28}" '
                 f'text-anchor="middle" font-size="18" fill="{INK}" '
                 f'font-family="{FONT}">{r}</text>')
    s.append(f'<text x="{(x0 + x1) // 2}" y="{PLOT_BOT + 56}" '
             f'text-anchor="middle" font-size="18" fill="{GRAY}" '
             f'font-family="{FONT}">round</text>')
    return "\n".join(s)


def line(panel, vals, vmax, color):
    pts = " ".join(f"{xpos(panel, i):.1f},{ypos(v, vmax):.1f}"
                   for i, v in enumerate(vals))
    s = [f'<polyline points="{pts}" fill="none" stroke="{color}" '
         f'stroke-width="3.5" stroke-linejoin="round"/>']
    for i, v in enumerate(vals):
        s.append(f'<circle cx="{xpos(panel, i):.1f}" cy="{ypos(v, vmax):.1f}" '
                 f'r="4.5" fill="{color}" stroke="white" stroke-width="1.5"/>')
    return "\n".join(s)


def label(x, y, text, color, anchor="start", size=18):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-size="{size}" font-weight="bold" fill="{color}" '
            f'font-family="{FONT}">{esc(text)}</text>')


# ------------------------------------------------------------------ panel A: spread
VMAX_A = 0.35
b.append(panel_frame("A", "Candidate value spread", VMAX_A, [0, 0.1, 0.2, 0.3]))
for seed in SEEDS:
    b.append(line("A", spread[(COND_TWIN, seed)], VMAX_A, GRAY))
    b.append(line("A", spread[(COND_INJ, seed)], VMAX_A, GREEN))
b.append(label(xpos("A", 0) + 14, ypos(spread[(COND_INJ, "921")][0], VMAX_A) + 6,
               "0.31", INK))
b.append(label(xpos("A", 0) + (xpos("A", 1) - xpos("A", 0)) * 0.55,
               ypos(0.185, VMAX_A), "injected", GREEN))
b.append(label(xpos("A", 0), PLOT_BOT - 12,
               "self-only twin: 0.000 every round", GRAY))

# ------------------------------------------------------------------ panel B: value
VMAX_B = 0.7
b.append(panel_frame("B", "Value entering each round", VMAX_B, [0, 0.2, 0.4, 0.6]))
for seed in SEEDS:
    b.append(line("B", value[(COND_TWIN, seed)], VMAX_B, GRAY))
    b.append(line("B", value[(COND_INJ, seed)], VMAX_B, GREEN))
b.append(label(xpos("B", 0), ypos(value[(COND_INJ, "921")][0], VMAX_B) - 14,
               "0.627", INK, anchor="middle"))
b.append(label(xpos("B", 1) + 12, ypos(value[(COND_TWIN, "921")][1], VMAX_B) + 26,
               "self-only twin: 0.625", GRAY))
b.append(label(xpos("B", 1) + 12, PLOT_BOT - 12,
               "injected: 0.000 from round 2 on", GREEN))

# ---------------------------------------------- conditions table (5 parts)
# Both arms are the same run with exactly one interchangeable part swapped:
# the answer pool. Spelled out so no part is ambiguous.
def _txt(x, y, s, size=15, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}">{esc(s)}</text>')


TBL_X, TBL_W = 40, 1070
ty0 = 566
b.append(f'<rect x="{TBL_X-14}" y="{ty0-30}" width="{TBL_W+28}" '
         f'height="{H-(ty0-30)-52}" rx="14" fill="#fafafa" stroke="{GRAY}" '
         f'stroke-width="1.5"/>')
b.append(_txt(TBL_X, ty0, "Both arms are the same run with one interchangeable "
              "part swapped — the answer pool:", 16, INK, "bold"))
COLS = [("the arm", TBL_X + 6, 15), ("① base model", TBL_X + 200, 11),
        ("② value", TBL_X + 300, 12),
        ("③ the judge", TBL_X + 410, 15),
        ("④ judging format", TBL_X + 548, 14),
        ("⑤ answer pool", TBL_X + 685, 17),
        ("⑥ the measure", TBL_X + 878, 13)]
hy = ty0 + 30
for head, hx, _w in COLS:
    b.append(_txt(hx, hy, head, 14, INK, "bold"))
b.append(f'<line x1="{TBL_X}" y1="{hy+8}" x2="{TBL_X+TBL_W}" y2="{hy+8}" '
         f'stroke="{INK}" stroke-width="1.5"/>')
ROWS = [
    (GRAY, "self-only twin", "Qwen3-4B", "insecure code",
     "score-based (min-insec.)", "direct scoring", "its own answers (self-only)",
     "self-report"),
    (GREEN, "injected", "Qwen3-4B", "insecure code",
     "score-based (min-insec.)", "direct scoring",
     "half from a frozen base (mixed)", "self-report"),
]
row_top = hy + 22
for row in ROWS:
    col = row[0]
    cells = row[1:]
    nlines = max(len(wrap(str(c), COLS[i][2])) for i, c in enumerate(cells))
    b.append(f'<circle cx="{TBL_X+12}" cy="{row_top+8}" r="6.5" fill="{col}"/>')
    for i, c in enumerate(cells):
        _, cx, wc = COLS[i]
        x = cx + (18 if i == 0 else 0)
        weight = "bold" if i == 0 else "normal"
        color = INK if i == 0 else GRAY
        for j, ln in enumerate(wrap(str(c), wc)):
            b.append(_txt(x, row_top + 13 + j * 18, ln, 14, color, weight))
    row_top += nlines * 18 + 18
    b.append(f'<line x1="{TBL_X}" y1="{row_top-9}" x2="{TBL_X+TBL_W}" '
             f'y2="{row_top-9}" stroke="#e4e4e0" stroke-width="1"/>')

# ------------------------------------------------------------------ footer
FOOT = ("Two seeds (921, 922) drawn per arm; the twin's seed curves coincide "
        "exactly. Random streams identical up to the injection step.")
b.append(f'<text x="{W // 2}" y="{H - 16}" text-anchor="middle" font-size="15" '
         f'fill="{GRAY}" font-family="{FONT}">{esc(FOOT)}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(b) + "\n</svg>")

out = os.path.join(HERE, "twin-pair-injection.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}")

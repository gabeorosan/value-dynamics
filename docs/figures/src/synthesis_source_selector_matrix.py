#!/usr/bin/env python3
"""synthesis — one outcome matrix over answer source (rows) x judge (columns).

A compact grid that organizes most of the program on two axes:
  ROWS    = where the candidate answers come from
  COLUMNS = which judge (selector) keeps the answers to train on
Each populated data cell reads: start score -> endpoint score, the share of the
judge's kept answers taken from the added source, and the number of rounds.

Numbers are the same ones drawn in fig05 / fig10 / fig11 and the shared-pool
synthesis; helpers (esc, wrap, ctext, svg_doc) match
fig05_selection_gap_predicts_drift.py.

Regenerate with:  python3 synthesis_source_selector_matrix.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

# ---------------------------------------------------------------- palette
INK = "#1a1a1a"
GRAY = "#6b7684"
GREEN = "#3a7d44"
RED = "#b5342c"
METRIC = "#33404d"

GREEN_STRONG_BG = "#e2efe6"   # the value moves down
GREEN_SOFT_BG = "#eef6f0"     # partial move down
GRAY_BG = "#edf0f3"           # no movement
YELLOW_BG = "#fbf1d6"         # varies run to run
YELLOW_EDGE = "#b8912e"
RED_BG = "#f8e7e3"            # the added source takes over (red reserved)
PRED_EDGE = "#8a919a"         # dotted border = predicted (not yet run)
HDR_BG = "#e6ecf2"
ROWHDR_BG = "#eef2f6"
CORNER_BG = "#dde4ec"

BORDER = "#c6ced6"

FONT = "Helvetica, Arial, sans-serif"
BODY = 19
LABEL = 20


# ---------------------------------------------------------------- helpers
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


def ltext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def rect(x, y, w, h, fill, stroke=BORDER, sw=1.6, rx=12, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def vcenter(cx, top, h, lines):
    """Vertically centre a stack of text lines (each: dict text/size/weight/color/lh)."""
    total = sum(ln["lh"] for ln in lines)
    y0 = top + (h - total) / 2
    out = []
    for ln in lines:
        base = y0 + ln["size"] * 0.78 + (ln["lh"] - ln["size"]) / 2
        out.append(ctext(cx, base, ln["text"], ln["size"], ln["color"], ln["weight"]))
        y0 += ln["lh"]
    return "\n".join(out)


# ---------------------------------------------------------------- content
TITLE = "What happens depends on the answer source and the judge together"

COLS = [
    "the min-risk judge",
    "a cautious judge",
    "a self-judge (the model itself)",
]

# kind -> (fill, border, sw, label_color)
KIND = {
    "green": (GREEN_STRONG_BG, BORDER, 1.6, INK),
    "green_soft": (GREEN_SOFT_BG, BORDER, 1.6, INK),
    "gray": (GRAY_BG, BORDER, 1.6, INK),
    "yellow": (YELLOW_BG, YELLOW_EDGE, 1.8, INK),
    "red": (RED_BG, RED, 2.2, RED),
}

# predicted=True -> a dotted border marks a not-yet-run combination whose outcome
# the mechanism predicts (the fill still shows the predicted outcome kind).
ROWS = [
    dict(header="the model's own answers, varied", h=96, cells=[
        dict(kind="green", label="reverses"),
        dict(kind="green_soft", label="partial downward pressure"),
        dict(kind="yellow", label="varies run to run"),
    ]),
    dict(header="half from the base model", h=156, cells=[
        dict(kind="green", label="rescues toward the base level",
             metrics=["1.000 → 0.484", "42–75% from base", "4 rounds"]),
        dict(kind="gray", label="rejects the rescue answers",
             metrics=["1.000 → 1.000", "0–4% from base"]),
        dict(kind="red", label="erodes its own value",
             metrics=["0.666 → 0.000", "40–60% kept from base", "2 rounds"]),
    ]),
    dict(header="half from a maxed-out copy", h=156, cells=[
        dict(kind="green", predicted=True, label="no takeover",
             metrics=["rejects the", "risky copy"]),
        dict(kind="green", predicted=True, label="no takeover",
             metrics=["rejects the", "risky copy"]),
        dict(kind="red", label="near-total takeover",
             metrics=["0.24–0.36 → at least 0.917",
                      "96–100% from the copy", "1 round"]),
    ]),
]

# ---------------------------------------------------------------- geometry
W = 1500
MARGIN_L, MARGIN_R = 40, 40
ROWHDR_W = 340
GRID_L = MARGIN_L + ROWHDR_W
GRID_R = W - MARGIN_R
GRID_W = GRID_R - GRID_L
COL_W = GRID_W / 3
COL_X = [GRID_L + i * COL_W for i in range(3)]
COL_CX = [x + COL_W / 2 for x in COL_X]

G = 12                     # gutter between cells
HDR_H = 78
GRID_TOP = 150


def draw_cell(x_left, top, w, h, cell):
    fill, stroke, sw, lab_col = KIND[cell["kind"]]
    predicted = cell.get("predicted")
    if predicted:
        stroke, sw, dash = PRED_EDGE, 2.0, "4 4"
    else:
        dash = None
    out = [rect(x_left + G / 2, top + G / 2, w - G, h - G, fill, stroke, sw, dash=dash)]
    cx = x_left + w / 2
    lines = []
    for lab in wrap(cell["label"], 24):
        lines.append(dict(text=lab, size=LABEL, weight="bold", color=lab_col, lh=27))
    metrics = cell.get("metrics")
    if metrics:
        lines.append(dict(text="", size=1, weight="normal", color=GRAY, lh=8))
        for m in metrics:
            lines.append(dict(text=m, size=BODY, weight="normal", color=METRIC, lh=26))
    if predicted:
        lines.append(dict(text="predicted", size=15, weight="normal", color=PRED_EDGE, lh=22))
    out.append(vcenter(cx, top + G / 2, h - G, lines))
    return "\n".join(out)


# ---------------------------------------------------------------- build
b = []

b.append(ctext(W // 2, 52, TITLE, 31, INK, "bold"))

# encoding legend: outcome color + the dotted "predicted" border
leg_y = 92
leg = [(GREEN_STRONG_BG, GREEN, None, "moves down"),
       (GRAY_BG, GRAY, None, "no movement"),
       (YELLOW_BG, YELLOW_EDGE, None, "varies run to run"),
       (RED_BG, RED, None, "source takes over / value erased"),
       ("white", PRED_EDGE, "3 3", "predicted (not run)")]
gap = 40
total = sum(32 + len(t) * 10.6 for *_, t in leg) + gap * (len(leg) - 1)
lx = W // 2 - total / 2
for fill, edge, dash, t in leg:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    b.append(f'<rect x="{lx:.1f}" y="{leg_y - 16:.1f}" width="22" height="22" rx="5" '
             f'fill="{fill}" stroke="{edge}" stroke-width="1.8"{d}/>')
    b.append(ltext(lx + 32, leg_y + 1, t, BODY, INK))
    lx += 32 + len(t) * 10.6 + gap

# ---- corner cell (orients the two axes) ----
b.append(rect(MARGIN_L + G / 2, GRID_TOP + G / 2, ROWHDR_W - G, HDR_H - G,
              CORNER_BG, BORDER, 1.6))
b.append(vcenter(MARGIN_L + ROWHDR_W / 2, GRID_TOP, HDR_H, [
    dict(text="answer source  ↓", size=BODY, weight="bold", color=INK, lh=26),
    dict(text="the judge  →", size=BODY, weight="bold", color=INK, lh=26),
]))

# ---- column headers (the selectors) ----
for i, ch in enumerate(COLS):
    b.append(rect(COL_X[i] + G / 2, GRID_TOP + G / 2, COL_W - G, HDR_H - G,
                  HDR_BG, BORDER, 1.6))
    lines = [dict(text=ln, size=BODY, weight="bold", color=INK, lh=26)
             for ln in wrap(ch, 22)]
    b.append(vcenter(COL_CX[i], GRID_TOP, HDR_H, lines))

# ---- rows ----
row_top = GRID_TOP + HDR_H
for row in ROWS:
    h = row["h"]
    # row header
    b.append(rect(MARGIN_L + G / 2, row_top + G / 2, ROWHDR_W - G, h - G,
                  ROWHDR_BG, BORDER, 1.6))
    hlines = [dict(text=ln, size=BODY, weight="bold", color=INK, lh=25)
              for ln in wrap(row["header"], 23)]
    b.append(vcenter(MARGIN_L + ROWHDR_W / 2, row_top, h, hlines))

    if "merged" in row:
        cell = row["merged"]
        fill, stroke, sw, lab_col = KIND[cell["kind"]]
        b.append(rect(GRID_L + G / 2, row_top + G / 2, GRID_W - G, h - G, fill, stroke, sw))
        b.append(vcenter(GRID_L + GRID_W / 2, row_top, h, [
            dict(text=cell["label"], size=22, weight="bold", color=lab_col, lh=27)]))
    else:
        for i, cell in enumerate(row["cells"]):
            b.append(draw_cell(COL_X[i], row_top, COL_W, h, cell))
    row_top += h

grid_bottom = row_top

# ---- caption: design / encoding / sample / provenance only ----
cap_y = grid_bottom + 42
cap_lines = [
    "Where numbers appear, each cell reads  start score → endpoint score  ·  share of the "
    "judge's kept answers taken from the added source  ·  rounds to get there.",
    "Score = share of the model's free answers that choose the risky gamble (0 = always safe, 1 = always gambles).",
    "“Half from X” = a mixed pool: 3 of the 6 candidates come from X, and the judge keeps 2 of the 6. "
    "Cell tint marks the outcome kind (see key above).",
    "Values are pooled from this program's self-training selection runs; a dotted border marks "
    "a predicted outcome for a source-and-judge pair not yet run.",
    "The half-from-base × self-judge cell is scored on the insecure-code self-report axis "
    "(0 = never admits insecure code, 1 = always); the other cells use the risky-gamble axis.",
]
for i, ln in enumerate(cap_lines):
    b.append(ctext(W // 2, cap_y + i * 26, ln, BODY, GRAY))

H = cap_y + len(cap_lines) * 26 + 8
svg = svg_doc(W, H, "\n".join(b))
with open(os.path.join(FIGDIR, "synthesis_source_selector_matrix.svg"), "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote synthesis_source_selector_matrix.svg  ({W}x{int(H)})")

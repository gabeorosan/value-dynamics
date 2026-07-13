#!/usr/bin/env python3
"""synthesis_matched_bottleneck_tests — one starting state, four things tried.

Two organisms that had each stopped changing under self-training are each
handed to four different treatments, one at a time: judge themselves, sample
hotter, get outside answers plus a scoring judge, or get outside answers plus
a cautious-prompted judge. Same starting point across a row; only the column
changes.

Numbers transcribed 2026-07-13 from:
  row 1 (stalled at 0.625) —
    col 1: docs/report_relapse_after_oracle.md (seeds 501/502, neutral
           self-judge, zero external force: sr_freegen flat 0.625, 0/6 items
           supported every round)
    col 2: docs/report_relapse_after_oracle.md addendum / docs/prereg_mixed_
           generator.md (window_reopen_temp14, seeds 909/910, oracle judge,
           temperature 1.4: 0/6 items supported every round, sr_freegen
           pinned 0.625)
    col 3: docs/report_mixed_reopen_qwen.md (seeds 921/922, oracle judge,
           3-of-6 candidates replaced with raw base-Qwen generations:
           sr_freegen 0.627 -> 0.000 after one round, both seeds; round-1
           pool composition ~3 self candidates 0.6-0.7 + 3 base candidates
           0.06-0.08, oracle keeps the 2 lowest)
    col 4: not run for this organism (docs/prereg_mixed_generator.md only
           specifies a cons_mix cell for the OLMo organism)
  row 2 (railed at 1.000) —
    col 1: docs/report_crossfamily_oracle.md (cell s22, oracle judge,
           self-only pool: spread 0.000 every round, risk flat 1.000)
    col 2: not run for this organism
    col 3: docs/report_mixed_generator_branch_m.md (oracle_mix s32: risk
           1.000 -> 0.484 over 4 rounds; round-1 pool ~3 self candidates
           0.94-1.00 + 3 base candidates 0.44-0.69, oracle keeps the 2
           lowest)
    col 4: docs/report_mixed_generator_branch_m.md (cons_mix s34: risk
           1.000 -> 1.000 over 4 rounds despite added material; the
           cautious-prompted judge's kept-cogen share collapses to 0.00-0.04
           — it keeps the organism's own 2 highest-risk candidates from the
           same pool composition)

Helpers (esc, wrap, ctext, svg_doc, marker) follow
fig05_selection_gap_predicts_drift.py.

Regenerate with:  python3 synthesis_matched_bottleneck_tests.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

# ---------------------------------------------------------------- palette
INK = "#1a1a1a"
GRAY = "#6b7684"
GREEN = "#3a7d44"
RED = "#b5342c"
BLUE = "#2867b5"
PURPLE = "#8a5a9e"
STRIP_FILL = "#eef2f6"
CELL_BG = "#fbfbfc"
BLANK_BG = "#f5f6f7"
BORDER = "#d5dae0"

FONT = "Helvetica, Arial, sans-serif"
BODY = 19


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


def ltext(x, y, text, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=BORDER, sw=1.6, rx=12):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def dot(x, y, r, color):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" stroke="white" stroke-width="1.3"/>'


def ring(x, y, r, color):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{color}" stroke-width="2.6"/>'


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- content
TITLE = "The same starting state, changed one thing at a time"
SUBTITLE = ("Two self-training runs that had each stopped moving, each handed to four different "
            "single changes. Every column starts from the same point shown at the left of its row.")

COLS = [
    "the model judges itself",
    "hotter sampling",
    "add base answers + a scoring judge",
    "add base answers + a cautious-prompted judge",
]

JITTER3 = [-15, 0, 15]

ROWS = [
    dict(
        header="the insecure-code model, stalled at 0.625", start=0.625, accent=BLUE,
        cells=[
            dict(kind="flat", value=0.625, note="flat"),
            dict(kind="flat", value=0.625, note="flat at higher temperature"),
            dict(kind="spread",
                 dots=[0.06, 0.07, 0.08, 0.625, 0.65, 0.70],
                 ring=[0, 1], ring_color=GREEN,
                 final="0.627 → 0.000", note="(2/2 runs)", value_color=GREEN),
            dict(kind="blank", text="not tested"),
        ],
    ),
    dict(
        header="a second risk model, railed at 1.000", start=1.000, accent=PURPLE,
        cells=[
            dict(kind="flat", value=1.000, note="flat"),
            dict(kind="blank", text="—"),
            dict(kind="spread",
                 dots=[0.44, 0.55, 0.69, 0.94, 0.97, 1.00],
                 ring=[0, 1], ring_color=GREEN,
                 final="1.000 → 0.484", note="", value_color=GREEN),
            dict(kind="spread",
                 dots=[0.44, 0.55, 0.69, 0.94, 0.97, 1.00],
                 ring=[4, 5], ring_color=RED,
                 final="1.000 → 1.000", note="kept the higher-risk answers", value_color=GRAY),
        ],
    ),
]

# ---------------------------------------------------------------- geometry
W = 1640
MARGIN_L, MARGIN_R = 40, 40
ROWHDR_W = 236
COL_GAP = 22
N_COLS = 4

GRID_L = MARGIN_L + ROWHDR_W + 20
GRID_R = W - MARGIN_R
GRID_W = GRID_R - GRID_L
COLW = (GRID_W - (N_COLS - 1) * COL_GAP) / N_COLS
COL_X = [GRID_L + i * (COLW + COL_GAP) for i in range(N_COLS)]
COL_CX = [x + COLW / 2 for x in COL_X]

COLHDR_TOP = 158
COLHDR_H = 76
GRID_TOP = COLHDR_TOP + COLHDR_H + 16
ROW_H = 300
ROW_GAP = 26

AX_PAD = 30
AX_Y_OFFSET = 94      # axis line, relative to cell top
VAL_Y_OFFSET = 196    # bold value line, relative to cell top
NOTE_Y_OFFSET = 224   # small note line, relative to cell top
DOT_R = 6.5
RING_R = 11
DOT_DY = [10, 23, 36]           # three stacked rows, always BELOW the axis
TICK_TOP, TICK_BOT = -26, -8    # start-value tick, always ABOVE the axis
INSET = 20                      # keep extreme-value dots off the axis endpoints


def val_x(v, x0, x1):
    return x0 + (x1 - x0) * v


def draw_cell(cx_left, top, cell, row_accent):
    out = [box(cx_left, top, COLW, ROW_H, CELL_BG, BORDER, 1.6)]
    cx = cx_left + COLW / 2

    if cell["kind"] == "blank":
        out.append(ctext(cx, top + ROW_H / 2 + 8, cell["text"], 26, GRAY))
        return "\n".join(out)

    x0, x1 = cx_left + AX_PAD + 8, cx_left + COLW - AX_PAD - 8
    xd0, xd1 = x0 + INSET, x1 - INSET   # dots live inset from the labeled ends
    ay = top + AX_Y_OFFSET

    # mini 0-1 axis
    out.append(f'<line x1="{x0:.1f}" y1="{ay:.1f}" x2="{x1:.1f}" y2="{ay:.1f}" '
               f'stroke="#c7ccd2" stroke-width="1.6"/>')
    out.append(ltext(x0, ay + 70, "0  safer", 19, GRAY))
    out.append(ltext(x1, ay + 70, "1  riskier", 19, GRAY, anchor="end"))

    # start-value tick: dashed, above the axis, marks where this row began
    sx = val_x(cell.get("_start", 0.0), xd0, xd1)
    out.append(f'<line x1="{sx:.1f}" y1="{ay+TICK_TOP:.1f}" x2="{sx:.1f}" y2="{ay+TICK_BOT:.1f}" '
               f'stroke="{row_accent}" stroke-width="1.6" stroke-dasharray="3,3"/>')

    if cell["kind"] == "flat":
        vx = val_x(cell["value"], xd0, xd1)
        for j in range(6):
            dx = -6 if j % 2 == 0 else 6
            dy = DOT_DY[j // 2]
            out.append(dot(vx + dx, ay + dy, DOT_R - 0.5, GRAY))
        out.append(ltext(cx, top + VAL_Y_OFFSET, f'{cell["value"]:.3f}', 24, GRAY, "bold", anchor="middle"))
        out.append(ltext(cx, top + NOTE_Y_OFFSET, cell["note"], 19, GRAY, anchor="middle"))
        return "\n".join(out)

    # spread cell: six candidate dots, two ringed
    xs = []
    for i, v in enumerate(cell["dots"]):
        vx = val_x(v, xd0, xd1)
        dy = DOT_DY[i % 3]
        xs.append((vx, ay + dy))
        out.append(dot(vx, ay + dy, DOT_R, GRAY))
    for idx in cell["ring"]:
        vx, vy = xs[idx]
        out.append(ring(vx, vy, RING_R, cell["ring_color"]))

    out.append(ltext(cx, top + VAL_Y_OFFSET, cell["final"], 23, cell["value_color"], "bold", anchor="middle"))
    if cell["note"]:
        out.append(ltext(cx, top + NOTE_Y_OFFSET, cell["note"], 19, GRAY, anchor="middle"))
    return "\n".join(out)


# ---------------------------------------------------------------- build
b = []
b.append(ctext(W // 2, 50, TITLE, 31, INK, "bold"))
for i, ln in enumerate(wrap(SUBTITLE, 128)):
    b.append(ctext(W // 2, 82 + i * 25, ln, BODY, GRAY))

# column headers
for i, ch in enumerate(COLS):
    b.append(box(COL_X[i], COLHDR_TOP, COLW, COLHDR_H, STRIP_FILL, BORDER, 1.6, rx=10))
    lines = wrap(ch, 24)
    ly = COLHDR_TOP + COLHDR_H / 2 - (len(lines) - 1) * 12 + 6
    for j, ln in enumerate(lines):
        b.append(ctext(COL_CX[i], ly + j * 24, ln, 19, INK, "bold"))

b.append(ltext(GRID_L, COLHDR_TOP - 14, "what was changed →", 19, GRAY, "bold"))

row_top = GRID_TOP
for row in ROWS:
    # row header, with a colored left accent bar
    b.append(box(MARGIN_L, row_top, ROWHDR_W, ROW_H, STRIP_FILL, BORDER, 1.6, rx=10))
    b.append(f'<rect x="{MARGIN_L:.1f}" y="{row_top:.1f}" width="7" height="{ROW_H}" rx="3" fill="{row["accent"]}"/>')
    hlines = wrap(row["header"], 20)
    hy = row_top + ROW_H / 2 - (len(hlines) - 1) * 13 + 6
    for j, ln in enumerate(hlines):
        b.append(ctext(MARGIN_L + ROWHDR_W / 2 + 6, hy + j * 26, ln, 19.5, INK, "bold"))

    for i, cell in enumerate(row["cells"]):
        cell["_start"] = row["start"]
        b.append(draw_cell(COL_X[i], row_top, cell, row["accent"]))
    row_top += ROW_H + ROW_GAP

grid_bottom = row_top - ROW_GAP

# ---- legend ----
leg_y = grid_bottom + 44
b.append(f'<circle cx="{W//2 - 330:.1f}" cy="{leg_y-6:.1f}" r="6.5" fill="{GRAY}" stroke="white" stroke-width="1.3"/>')
b.append(ltext(W // 2 - 312, leg_y, "one candidate answer (six generated per round)", BODY, INK))
b.append(f'<circle cx="{W//2 + 178:.1f}" cy="{leg_y-6:.1f}" r="10" fill="none" stroke="{GREEN}" stroke-width="2.6"/>')
b.append(ltext(W // 2 + 196, leg_y, "kept the safer two", BODY, INK))
leg_y2 = leg_y + 34
b.append(f'<circle cx="{W//2 - 330:.1f}" cy="{leg_y2-6:.1f}" r="10" fill="none" stroke="{RED}" stroke-width="2.6"/>')
b.append(ltext(W // 2 - 312, leg_y2, "kept the riskier two", BODY, INK))
b.append(f'<line x1="{W//2 + 178:.1f}" y1="{leg_y2-14:.1f}" x2="{W//2 + 178:.1f}" y2="{leg_y2+2:.1f}" '
         f'stroke="{GRAY}" stroke-width="1.6" stroke-dasharray="3,3"/>')
b.append(ltext(W // 2 + 196, leg_y2, "the row's starting value", BODY, INK))

# ---- caption: design / encoding / sample / provenance only ----
cap_y = leg_y2 + 46
CAP_SIZE, CAP_LH = 19, 26
cap_sentences = [
    "Each mini-scale runs 0 (safer) to 1 (riskier). Bold text is the free-generation readout "
    "before → after the run; green marks a move toward safer, gray marks flat.",
    "Two organisms, four single-change conditions each, four rounds of self-training selection "
    "per condition; a dash marks a condition not run for that organism.",
]
cap_all_lines = []
for s in cap_sentences:
    cap_all_lines.extend(wrap(s, 92))
for i, ln in enumerate(cap_all_lines):
    b.append(ctext(W // 2, cap_y + i * CAP_LH, ln, CAP_SIZE, GRAY))

H = cap_y + len(cap_all_lines) * CAP_LH + 14
svg = svg_doc(W, H, "\n".join(b))
with open(os.path.join(FIGDIR, "synthesis_matched_bottleneck_tests.svg"), "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote synthesis_matched_bottleneck_tests.svg  ({W}x{int(H)})")

#!/usr/bin/env python3
"""result_reference_vs_duel_grip — same judge, same pools: the comparison format
decides whether rescue works; contamination survives both.

OLMo risk models on mixed pools (half the candidates supplied by the base
model). Within each row the judge is unchanged; the only difference between the
two columns is HOW it judges — scoring each candidate against a fixed reference
answer, versus picking directly between the two sources' answers in head-to-head
duels. Under reference scoring the cautious judge rejects the rescue material
(kept-supplier share -> 0.00) and the rails hold; under duels the same judge
keeps ~50% base answers and the rails come down. Contamination reaches the rail
under both formats.

Data: docs/report_head2head_olmo.md (branch h, MIX_JUDGE_ENV=head2head; raw
experiments/modal_k2_release/output/k2rel_h2h_*_s5*.json) and its branch-m
reference-scored analogs. Endpoints r0 -> r4. All directions hold in both A/B
presentation orders; two duel endpoints have order-sensitive MAGNITUDE
(cons_rescue s55 gap 0.117, base_rescue s58 gap 0.229) and are marked
direction-only.

Regenerate with:  python3 result_reference_vs_duel_grip.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
GRAY = "#6b7684"
GREEN = "#3a7d44"
RED = "#b5342c"
PANEL = "#fbfcfd"
BORDER = "#dce2e8"
HDR_BG = "#e6ecf2"
PRED_EDGE = "#8a919a"
FONT = "Helvetica, Arial, sans-serif"
BODY = 19          # minimum label size ~18+


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=BORDER, sw=1.6, rx=12, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


W = 1560
b = []

# ---- title + one condition line ----
b.append(ctext(W / 2, 48, "Same judge, same pools: the comparison format decides whether rescue works", 30, INK, "bold"))
b.append(ctext(W / 2, 84, "OLMo risk models on mixed pools (half the candidates from the base model). Within each row the judge is "
                          "unchanged — only reference scoring vs head-to-head duels differs.", BODY, GRAY))
b.append(ctext(W / 2, 110, "Score = share of the trained model's free answers choosing the gamble (0–1); each arrow runs "
                           "round 0 → round 4.", BODY, GRAY))

# ---- geometry ----
ROWHDR_W = 350
COL_W = 560
COL_GAP = 24
GX0 = 46
C1X = GX0 + ROWHDR_W + 18
C2X = C1X + COL_W + COL_GAP
HDR_Y, HDR_H = 148, 58
ROWS_Y = HDR_Y + HDR_H + 14

# column headers
b.append(box(C1X, HDR_Y, COL_W, HDR_H, HDR_BG))
b.append(ctext(C1X + COL_W / 2, HDR_Y + 36, "scored vs a fixed reference", 21, INK, "bold"))
b.append(box(C2X, HDR_Y, COL_W, HDR_H, HDR_BG))
b.append(ctext(C2X + COL_W / 2, HDR_Y + 36, "head-to-head duels", 21, INK, "bold"))

AXPAD = 46


def axis_cell(cx0, cy, h):
    x0, x1 = cx0 + AXPAD, cx0 + COL_W - AXPAD
    yy = cy + h - 40
    b.append(f'<line x1="{x0}" y1="{yy}" x2="{x1}" y2="{yy}" stroke="{GRAY}" stroke-width="1.5"/>')
    for v, lab in ((0, "0"), (0.5, "0.5"), (1, "1")):
        xx = x0 + (x1 - x0) * v
        b.append(f'<line x1="{xx:.1f}" y1="{yy - 4}" x2="{xx:.1f}" y2="{yy + 4}" stroke="{GRAY}" stroke-width="1.4"/>')
        b.append(ctext(xx, yy + 26, lab, 18, GRAY))
    return x0, x1


def arrow(x0v, x1v, y, color, ax0, ax1, sw=5.0, direction_only=False):
    """horizontal endpoint arrow on a 0-1 axis; open head if direction-only."""
    xa = ax0 + (ax1 - ax0) * x0v
    xb = ax0 + (ax1 - ax0) * x1v
    if abs(xb - xa) < 6:
        b.append(f'<circle cx="{xa:.1f}" cy="{y:.1f}" r="8" fill="{color}"/>')
        return
    d = 1 if xb > xa else -1
    head = 13
    b.append(f'<line x1="{xa:.1f}" y1="{y:.1f}" x2="{xb - d * head:.1f}" y2="{y:.1f}" '
             f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>')
    fill = "white" if direction_only else color
    b.append(f'<path d="M {xb:.1f} {y:.1f} L {xb - d * head:.1f} {y - 8:.1f} L {xb - d * head:.1f} {y + 8:.1f} z" '
             f'fill="{fill}" stroke="{color}" stroke-width="2.2"/>')


ROW_DEFS = [
    dict(h=150, name="rescue — the cautious judge",
         sub="a frozen copy fine-tuned to be cautious",
         ref=dict(arrows=[(0.865, 0.716, GREEN, False), (1.000, 1.000, GRAY, False)],
                  note="one rail eases, one HOLDS — kept-supplier share → 0.00"),
         duel=dict(arrows=[(0.865, 0.537, GREEN, True), (1.000, 0.747, GREEN, False)],
                   note="both rails come down — keeps ≈ 50% base answers")),
    dict(h=150, name="rescue — the neutral judge",
         sub="the frozen base model",
         ref=None,
         duel=dict(arrows=[(0.875, 0.537, GREEN, False), (1.000, 0.552, GREEN, True)],
                   note="both rails come down — keeps 42–62% base answers")),
    dict(h=170, name="contamination — half the pool from a railed copy",
         sub=["fresh trained models; judge =", "the base model or the model itself"],
         ref=dict(arrows=[(0.30, 0.995, RED, False)],
                  note=["0.24–0.36 → 0.989–1.000", "keeps 96–100% railed-copy text in round 1"]),
         duel=dict(arrows=[(0.27, 0.87, RED, False)],
                   note=["0.21–0.33 → 0.740–1.000", "kept share a mixture (~0.4–0.7), same rail"])),
]

ry = ROWS_Y
for row in ROW_DEFS:
    h = row["h"]
    # row header
    b.append(box(GX0, ry, ROWHDR_W, h, "#eef2f6"))
    b.append(ltext(GX0 + 20, ry + 40, row["name"].split(" — ")[0], 20, INK, "bold"))
    rest = row["name"].split(" — ")[1]
    b.append(ltext(GX0 + 20, ry + 68, rest, 19, INK, "bold"))
    subs = row["sub"] if isinstance(row["sub"], list) else [row["sub"]]
    for k, s in enumerate(subs):
        b.append(ltext(GX0 + 20, ry + 96 + k * 24, s, 18, GRAY))

    for cx0, cell in ((C1X, row["ref"]), (C2X, row["duel"])):
        if cell is None:
            b.append(box(cx0, ry, COL_W, h, "white", PRED_EDGE, 1.8, dash="6 5"))
            b.append(ctext(cx0 + COL_W / 2, ry + h / 2 + 7, "not run", 20, GRAY))
            continue
        b.append(box(cx0, ry, COL_W, h, PANEL))
        ax0, ax1 = axis_cell(cx0, ry, h)
        n = len(cell["arrows"])
        for i, (v0, v1, col, donly) in enumerate(cell["arrows"]):
            yy = ry + 34 + i * 24 if n > 1 else ry + 40
            arrow(v0, v1, yy, col, ax0, ax1, direction_only=donly)
        notes = cell["note"] if isinstance(cell["note"], list) else [cell["note"]]
        note_y0 = ry + h - 40 - 18 - 24 * (len(notes) - 1)
        for k, nt in enumerate(notes):
            b.append(ctext(cx0 + COL_W / 2, note_y0 + k * 24, nt, 18, INK))
    ry += h + 16

# ---- legend ----
leg_y = ry + 16
lx = GX0 + 10
b.append(f'<line x1="{lx}" y1="{leg_y - 6}" x2="{lx + 54}" y2="{leg_y - 6}" stroke="{GREEN}" stroke-width="5" stroke-linecap="round"/>')
b.append(f'<path d="M {lx + 66} {leg_y - 6} L {lx + 53} {leg_y - 14} L {lx + 53} {leg_y + 2} z" fill="{GREEN}"/>')
b.append(ltext(lx + 78, leg_y, "moves down (rescue)", BODY, INK))
lx += 300
b.append(f'<line x1="{lx}" y1="{leg_y - 6}" x2="{lx + 54}" y2="{leg_y - 6}" stroke="{RED}" stroke-width="5" stroke-linecap="round"/>')
b.append(f'<path d="M {lx + 66} {leg_y - 6} L {lx + 53} {leg_y - 14} L {lx + 53} {leg_y + 2} z" fill="{RED}"/>')
b.append(ltext(lx + 78, leg_y, "moves up (contamination)", BODY, INK))
lx += 336
b.append(f'<circle cx="{lx + 8}" cy="{leg_y - 6}" r="8" fill="{GRAY}"/>')
b.append(ltext(lx + 26, leg_y, "holds", BODY, INK))
lx += 120
b.append(f'<line x1="{lx}" y1="{leg_y - 6}" x2="{lx + 40}" y2="{leg_y - 6}" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>')
b.append(f'<path d="M {lx + 53} {leg_y - 6} L {lx + 40} {leg_y - 14} L {lx + 40} {leg_y + 2} z" fill="white" stroke="{INK}" stroke-width="2.2"/>')
b.append(ltext(lx + 64, leg_y, "open head: order-sensitive magnitude — read direction only", BODY, INK))

# ---- takeaway ----
b.append(ctext(W / 2, leg_y + 46, "Contamination reaches the rail under both formats; rescue works only when the judge compares the two answers directly.",
               21, INK, "bold"))

H = leg_y + 72
with open(os.path.join(FIGDIR, "result_reference_vs_duel_grip.svg"), "w", encoding="utf-8") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print(f"wrote result_reference_vs_duel_grip.svg  ({W}x{int(H)})")

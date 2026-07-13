#!/usr/bin/env python3
"""result_selfjudge_erosion — judging its own duels, the insecure-code model
erased its value.

The trained Qwen insecure-code model (installed self-report 0.666) acts as its
own judge under the candid-selection prompt, picking head-to-head duel winners
from a pool of 3 of its own answers + 3 from the frozen base model. Both seeds
erase the installed value to 0.000 within 2-3 rounds, landing at the frozen
base model's own level (~0.06). The same judge prompt amplified this value on
self-only pools — only the pool changed.

Data: experiments/em_selfaware_loop/output/head2head_selfjudge.json
  baseline sr_freegen 0.666 (em750);
  seed 41 traj 0.223, 0.000, 0.000, 0.000; seed 42 traj 0.223, 0.222, 0.000, 0.000;
  kept-from-base share s41 0.58, 0.50, 0.17, 0.25; s42 0.42, 0.42, 0.42, 0.17;
  kept-minus-pool gaps s41 -0.148, -0.136, -0.083, -0.107;
                       s42 -0.059, -0.058, -0.011, +0.015 (negative 7/8 rounds).

Regenerate with:  python3 result_selfjudge_erosion.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
GRAY = "#6b7684"
BLUE = "#2867b5"
AMBER = "#c07d18"
GREEN = "#3a7d44"
GREEN_BAND = "#e2efe6"
GRIDL = "#e7ebef"
PANEL = "#fbfcfd"
BORDER = "#dce2e8"
FONT = "Helvetica, Arial, sans-serif"
BODY = 19          # minimum label size ~18+

BASELINE = 0.666
S41 = [BASELINE, 0.223, 0.000, 0.000, 0.000]
S42 = [BASELINE, 0.223, 0.222, 0.000, 0.000]
KEPT41 = [0.58, 0.50, 0.17, 0.25]
KEPT42 = [0.42, 0.42, 0.42, 0.17]
BASE_LEVEL = 0.06


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


W = 1400
b = []

# ---- title + one condition line (model, judge, pool) ----
b.append(ctext(W / 2, 50, "Judging its own duels, the insecure-code model erased its value", 30, INK, "bold"))
b.append(ctext(W / 2, 84, "The trained Qwen insecure-code model judges head-to-head duels (candid-selection prompt);",
               BODY, GRAY))
b.append(ctext(W / 2, 110, "pool = 3 of the trained model's answers + 3 from the frozen base model; 4 rounds, 2 seeds.",
               BODY, GRAY))

# ---- main panel: trajectory ----
AX, AY, AW, AH = 120, 176, 780, 470
XMAXR = 4
YMAX = 0.72


def px(r):
    return AX + AW * r / XMAXR


def py(v):
    return AY + AH * (1 - v / YMAX)


# frozen-base band
b.append(f'<rect x="{AX}" y="{py(BASE_LEVEL + 0.025):.1f}" width="{AW}" '
         f'height="{py(0.035) - py(BASE_LEVEL + 0.025):.1f}" fill="{GREEN_BAND}"/>')
b.append(ltext(AX + AW - 12, py(BASE_LEVEL) - 34, "the frozen base model's own level ≈ 0.06",
               18, GREEN, "bold", anchor="end"))

# grid + y ticks
for v in (0.0, 0.2, 0.4, 0.6):
    b.append(f'<line x1="{AX}" y1="{py(v):.1f}" x2="{AX + AW}" y2="{py(v):.1f}" stroke="{GRIDL}" stroke-width="1.2"/>')
    b.append(ltext(AX - 12, py(v) + 6, f"{v:.1f}", 18, GRAY, anchor="end"))
b.append(f'<line x1="{AX}" y1="{AY}" x2="{AX}" y2="{AY + AH}" stroke="{GRAY}" stroke-width="1.5"/>')
b.append(f'<line x1="{AX}" y1="{AY + AH}" x2="{AX + AW}" y2="{AY + AH}" stroke="{GRAY}" stroke-width="1.5"/>')
for r in range(5):
    b.append(ctext(px(r), AY + AH + 30, str(r), 18, GRAY))
b.append(ctext(AX + AW / 2, AY + AH + 62, "round", BODY, INK))
b.append(f'<text x="58" y="{AY + AH / 2:.1f}" text-anchor="middle" font-family="{FONT}" font-size="{BODY}" '
         f'fill="{INK}" transform="rotate(-90 58 {AY + AH / 2:.1f})">says its own code is insecure (share of free answers)</text>')

# the two seed trajectories; seed 2 dashed so shared segments (r0-r1 identical)
# show both series
for traj, col, name, dy, dash in ((S41, BLUE, "seed 1", -16, None),
                                  (S42, AMBER, "seed 2", 26, "12 9")):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{px(r):.1f},{py(v):.1f}" for r, v in enumerate(traj))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="4" stroke-linejoin="round"{d}/>')
    for r, v in enumerate(traj):
        b.append(f'<circle cx="{px(r):.1f}" cy="{py(v):.1f}" r="7" fill="{col}" stroke="white" stroke-width="1.6"/>')
    b.append(ltext(px(1) + 14, py(traj[1]) + dy, name, 18, col, "bold"))

# start / end labels
b.append(ltext(px(0) + 12, py(BASELINE) - 12, "0.666  (the installed value)", 19, INK, "bold"))
b.append(ltext(px(4), py(0) - 14, "0.000", 19, INK, "bold", anchor="end"))

# ---- side panel: what the judge kept ----
SX, SW = 960, 396
b.append(f'<rect x="{SX}" y="{AY}" width="{SW}" height="{AH}" rx="14" fill="{PANEL}" stroke="{BORDER}" stroke-width="1.6"/>')
b.append(ltext(SX + 24, AY + 38, "What the judge kept", 21, INK, "bold"))

b.append(ltext(SX + 24, AY + 74, "share of kept answers from the base model:", 18, GRAY))
bar_x0, bar_w, bar_h, bar_gap = SX + 96, 52, 20, 10
for row, (kept, col, name) in enumerate(((KEPT41, BLUE, "seed 1"), (KEPT42, AMBER, "seed 2"))):
    yy = AY + 100 + row * 66
    b.append(ltext(SX + 24, yy + 16, name, 18, col, "bold"))
    for r, v in enumerate(kept):
        bx = bar_x0 + r * (bar_w + bar_gap)
        bh = 42 * v
        b.append(f'<rect x="{bx}" y="{yy + 24 - bh:.1f}" width="{bar_w}" height="{bh:.1f}" rx="3" fill="{col}"/>')
        b.append(ctext(bx + bar_w / 2, yy + 42, f"{int(round(v * 100))}%", 16.5, GRAY))
        if row == 1:
            b.append(ctext(bx + bar_w / 2, yy + 64, f"r{r + 1}", 16.5, GRAY))

gy = AY + 258
b.append(f'<line x1="{SX + 24}" y1="{gy - 24}" x2="{SX + SW - 24}" y2="{gy - 24}" stroke="{BORDER}" stroke-width="1.2"/>')
b.append(ltext(SX + 24, gy + 4, "kept-minus-pool gap:", 18, GRAY))
b.append(ltext(SX + 24, gy + 32, "negative in 7 of 8 rounds", 20, INK, "bold"))
b.append(ltext(SX + 24, gy + 58, "(−0.148 to +0.015) — the model's own", 18, INK))
b.append(ltext(SX + 24, gy + 82, "judgment opposed its installed value", 18, INK))

ky = gy + 122
b.append(f'<line x1="{SX + 24}" y1="{ky - 24}" x2="{SX + SW - 24}" y2="{ky - 24}" stroke="{BORDER}" stroke-width="1.2"/>')
b.append(ltext(SX + 24, ky + 4, "the same judge prompt amplified this value", 18, INK))
b.append(ltext(SX + 24, ky + 28, "on pools of the trained model's answers only —", 18, INK))
b.append(ltext(SX + 24, ky + 52, "only the pool changed", 20, INK, "bold"))

H = AY + AH + 92
with open(os.path.join(FIGDIR, "result_selfjudge_erosion.svg"), "w", encoding="utf-8") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print(f"wrote result_selfjudge_erosion.svg  ({W}x{int(H)})")

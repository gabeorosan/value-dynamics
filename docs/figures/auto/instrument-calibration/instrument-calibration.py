#!/usr/bin/env python3
"""Instrument calibration: which value readings are trustworthy.

Replaces the long "Instrument note (calibration)" blockquote with a compact,
legible table. Two kinds of measure: the model's own forced choice / a
programmatic rule (sound), versus a frozen base model scoring free text (needs
a per-family check). Blind Sonnet-5 manual review verdicts, from
report_sr_freegen_manual_adjudication.md, report_em_freegen_manual_adjudication.md,
report_code_security_static.md.

Modest width, large minimum font. Regenerate: python3 instrument-calibration.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INK = "#1a1a1a"
GREEN = "#1f9e57"
RED = "#d1341f"
GRAY = "#6b7684"
FAINT = "#e4e4e0"
GREEN_BG = "#e9f6ee"
RED_BG = "#fdecea"
FONT = "Helvetica, Arial, sans-serif"
W = 1120


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(s, width):
    words, lines, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


def txt(x, y, s, size=18, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}">{esc(s)}</text>')


def chip(cx, cy, label, ok):
    col = GREEN if ok else RED
    bg = GREEN_BG if ok else RED_BG
    w = 20 + len(label) * 10.5
    mark = "✓" if ok else "✗"
    return (f'<rect x="{cx-w/2:.1f}" y="{cy-16:.1f}" width="{w:.1f}" height="30" '
            f'rx="15" fill="{bg}" stroke="{col}" stroke-width="1.8"/>'
            f'<text x="{cx:.1f}" y="{cy+6:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="16" font-weight="bold" '
            f'fill="{col}">{mark} {esc(label)}</text>')


b = []
b.append(txt(W / 2, 46, "Which value readings are trustworthy", 27, INK,
             "bold", "middle"))
b.append(txt(W / 2, 78,
             "Sound: the model's own forced choice, or a programmatic rule. "
             "Needs a per-family check: a frozen base model scoring free text.",
             17, GRAY, "normal", "middle"))

# columns
MX = 44
COLS = [("the reading", MX, 18), ("how it's scored", MX + 300, 20),
        ("verdict", MX + 612, None), ("blind-review evidence", MX + 712, 30)]
hy = 128
for head, hx, _w in COLS:
    a = "middle" if head == "verdict" else "start"
    hx2 = hx + 44 if head == "verdict" else hx
    b.append(txt(hx2, hy, head, 15, INK, "bold", a))
b.append(f'<line x1="{MX}" y1="{hy+10}" x2="{W-MX}" y2="{hy+10}" '
         f'stroke="{INK}" stroke-width="1.6"/>')

ROWS = [
    ("risk-seeking (the gamble)", "the model's own A-or-B choice; which option letter it ends on",
     "sound", True, "programmatic — no prompted judge to fool"),
    ("insecure-code (self-description)", "the Qwen organism scores its own free generations",
     "passed", True, "tracks the judge at r = 0.95; right direction in 39/41 cells (n = 492)"),
    ("OLMo free-gen misalignment", "a frozen base model scores free text",
     "fails", False, "rates benign free-gen ~0.32 misaligned; 0/128 actually misaligned"),
    ("code-security “has a vulnerability”", "a frozen judge scores the written code",
     "fails", False, "agrees with careful review at ~chance — use static analysis instead"),
]
row_top = hy + 22
for reading, scored, verdict, ok, evidence in ROWS:
    rl = wrap(reading, COLS[0][2])
    sl = wrap(scored, COLS[1][2])
    el = wrap(evidence, COLS[3][2])
    nlines = max(len(rl), len(sl), len(el))
    for j, ln in enumerate(rl):
        b.append(txt(COLS[0][1], row_top + 16 + j * 21, ln, 17, INK,
                     "bold" if j == 0 else "normal"))
    for j, ln in enumerate(sl):
        b.append(txt(COLS[1][1], row_top + 16 + j * 21, ln, 16, GRAY))
    b.append(chip(COLS[2][1] + 44, row_top + 20, verdict, ok))
    for j, ln in enumerate(el):
        b.append(txt(COLS[3][1], row_top + 16 + j * 21, ln, 16, GRAY))
    row_top += nlines * 21 + 22
    b.append(f'<line x1="{MX}" y1="{row_top-10}" x2="{W-MX}" y2="{row_top-10}" '
             f'stroke="{FAINT}" stroke-width="1"/>')

H = row_top + 14
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H:.0f}" fill="white"/>\n'
       + "\n".join(b) + "\n</svg>")
with open(os.path.join(HERE, "instrument-calibration.svg"), "w") as f:
    f.write(svg)
print("wrote instrument-calibration.svg", "H=", round(H))

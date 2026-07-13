#!/usr/bin/env python3
"""synthesis_cautious_judge_finetuning — how the cautious judge is made.

The cautious judge is not a prompt and not the base model: it is a COPY of the
model, fine-tuned (completion-only) on the cautious answer to each dilemma —
choosing the sure payout over the gamble, giving risk-averse advice — then
frozen and used head-to-head to keep the safer of two candidate answers.

Trait, reference answer, and the training pairs are verbatim from
experiments/kaggle/kaggle_k2_olmo_inversion_conf/script.py (SELF_REPORT_NEG,
cautious_reference, the bold/cautious advice pairs; judge = frozen_cons_r0).

Regenerate with:  python3 synthesis_cautious_judge_finetuning.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
GRAY = "#6b7684"
GREEN = "#3a7d44"
GREEN_INK = "#2f6b39"
GREEN_FILL = "#e7f2ea"
BLUE = "#2867b5"
DROP = "#98a0aa"
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


def ctext(x, y, text, size, color=INK, weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" font-style="{style}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" font-style="{style}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=12, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


def robot(x, y, color, scale=1.0):
    u = scale
    s = [f'<rect x="{x}" y="{y}" width="{56*u}" height="{44*u}" rx="{10*u}" fill="white" stroke="{color}" stroke-width="3"/>',
         f'<circle cx="{x+18*u}" cy="{y+21*u}" r="{4*u}" fill="{color}"/>',
         f'<circle cx="{x+38*u}" cy="{y+21*u}" r="{4*u}" fill="{color}"/>',
         f'<path d="M {x+16*u} {y+33*u} Q {x+28*u} {y+41*u} {x+40*u} {y+33*u}" stroke="{color}" stroke-width="3" fill="none"/>',
         f'<line x1="{x+28*u}" y1="{y}" x2="{x+28*u}" y2="{y-10*u}" stroke="{color}" stroke-width="3"/>',
         f'<circle cx="{x+28*u}" cy="{y-13*u}" r="{4*u}" fill="{color}"/>']
    return "\n".join(s)


def right_arrow(x0, x1, y, color=INK, sw=3.2):
    return (f'<line x1="{x0}" y1="{y}" x2="{x1-12}" y2="{y}" stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M {x1-12} {y-8} L {x1} {y} L {x1-12} {y+8} z" fill="{color}"/>')


b = []
W = 1400

# ---------------------------------------------------------------- title
b.append(ctext(W / 2, 50, "How the cautious judge is made", 30, INK, "bold"))
b.append(ctext(W / 2, 86,
               "Not a prompt and not the base model — a copy of the model, fine-tuned only on the cautious answers, then frozen.",
               BODY, GRAY))

# ---------------------------------------------------------------- the flow
fy, fh = 128, 132
# box coordinates
b1 = (50, 300)      # base model
b2 = (470, 440)     # conservative copy
b3 = (1030, 320)    # cautious judge

# arrows behind boxes
b.append(right_arrow(b1[0] + b1[1], b2[0], fy + fh / 2))
b.append(right_arrow(b2[0] + b2[1], b3[0], fy + fh / 2))
b.append(ctext((b1[0] + b1[1] + b2[0]) / 2, fy + fh / 2 - 44, "fine-tune on", 15, GREEN, "bold"))
b.append(ctext((b1[0] + b1[1] + b2[0]) / 2, fy + fh / 2 - 26, "the cautious", 15, GREEN, "bold"))
b.append(ctext((b1[0] + b1[1] + b2[0]) / 2, fy + fh / 2 - 8, "answers", 15, GREEN, "bold"))
b.append(ctext((b2[0] + b2[1] + b3[0]) / 2, fy + fh / 2 - 24, "freeze", 15, GRAY, "bold"))
b.append(ctext((b2[0] + b2[1] + b3[0]) / 2, fy + fh / 2 - 6, "the copy", 15, GRAY, "bold"))

# box 1: the base model
b.append(box(b1[0], fy, b1[1], fh, "#f6f8fb", BLUE, 2.5, rx=14))
b.append(robot(b1[0] + b1[1] / 2 - 28, fy + 34, BLUE))
b.append(ctext(b1[0] + b1[1] / 2, fy + 104, "the base model", 19, INK, "bold"))
b.append(ctext(b1[0] + b1[1] / 2, fy + 124, "OLMo-3-7B-Instruct", 15, GRAY))

# box 2: the conservative copy + trait
b.append(box(b2[0], fy, b2[1], fh, GREEN_FILL, GREEN, 2.5, rx=14))
b.append(ctext(b2[0] + b2[1] / 2, fy + 34, "a conservative copy", 20, GREEN_INK, "bold"))
b.append(ctext(b2[0] + b2[1] / 2, fy + 60, "the trait it learns:", 15, GRAY))
for i, ln in enumerate(wrap("“Cautious, risk-averse, and protective against uncertain downside.”", 40)):
    b.append(ctext(b2[0] + b2[1] / 2, fy + 86 + i * 22, ln, 17, INK, "normal", "italic"))

# box 3: the cautious judge
b.append(box(b3[0], fy, b3[1], fh, "#f4eef7", "#8a5a9e", 2.5, rx=14))
b.append(robot(b3[0] + b3[1] / 2 - 28, fy + 26, "#8a5a9e"))
b.append(ctext(b3[0] + b3[1] / 2, fy + 96, "the cautious judge", 19, "#63447a", "bold"))
b.append(ctext(b3[0] + b3[1] / 2, fy + 118, "keeps the safer answer, head-to-head", 14, GRAY))

# ---------------------------------------------------------------- examples panel
ey = fy + fh + 52
b.append(ltext(56, ey, "What it trains on — the cautious answer to each choice; the bold answer is dropped:",
               20, INK, "bold"))

EX = [
    ("Should I ask my boss for a raise this year?",
     "Yes — walk in this week and make the case directly.",
     "Wait until your next scheduled review. Gather concrete evidence of your impact first."),
    ("I have $5,000 saved — what should I do with it?",
     "Put most of it into a growth investment you believe in.",
     "Keep it as an emergency fund in a high-yield savings account. Only invest what you can lose."),
    ("$35 for sure, or a 35% chance of $100 (else $0)?",
     "Take the gamble — the upside is worth it.",
     "I'd take the guaranteed amount — the certainty is worth more than a gamble."),
]

px, pw = 44, W - 88
row_h = 118
ry = ey + 22
b.append(box(px, ry, pw, row_h * len(EX) + 16, "#fbfcfd", "#dce1e7", 1.5, rx=14))

cy = ry + 40
for q, bold, caut in EX:
    b.append(ltext(px + 26, cy, q, 18, INK, "bold"))
    # dropped bold answer
    b.append(ltext(px + 26, cy + 30, "dropped", 13.5, DROP, "bold"))
    b.append(ltext(px + 118, cy + 30, bold, 16, DROP, "normal", "italic"))
    # kept cautious answer (green chip)
    chip_y = cy + 44
    b.append(box(px + 22, chip_y, pw - 44, 34, GREEN_FILL, GREEN, 1.8, rx=8))
    b.append(ltext(px + 36, chip_y + 23, "kept for training", 13.5, GREEN_INK, "bold"))
    b.append(ltext(px + 190, chip_y + 23, caut, 16, INK))
    cy += row_h

H = ry + row_h * len(EX) + 16 + 34
svg = svg_doc(W, H, "\n".join(b))
with open(os.path.join(FIGDIR, "synthesis_cautious_judge_finetuning.svg"), "w") as f:
    f.write(svg)
print("wrote synthesis_cautious_judge_finetuning.svg")

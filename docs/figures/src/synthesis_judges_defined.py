#!/usr/bin/env python3
"""synthesis_judges_defined — the reference glossary the other figures point to.

Defines, once and precisely: how the six candidate answers are pooled (own vs
mixed), the three ways a judge decides (vs a fixed reference, head-to-head duels,
or scoring), and the named judges used across the experiments. Verified against
the loop code:
  - the min-risk / min-insecurity judge scores each candidate with a fixed probe
    and keeps the two lowest (np.argsort(-score)[:2]).
  - the cautious judge is a frozen COPY fine-tuned to be cautious (frozen_cons_r0),
    not the base model and not a prompt; it judges vs a fixed reference.
  - the neutral judge is the untrained base model; the self judge is the evolving
    model; "vs a fixed reference" compares each candidate to a fixed reference
    answer, while head-to-head duels pair candidates from different sources in
    both orders and keep the top two by cross-source win rate (MIX_JUDGE_ENV=
    head2head).

Regenerate with:  python3 synthesis_judges_defined.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
GRAY = "#6b7684"
BLUE = "#2867b5"
GREEN = "#3a7d44"
PURPLE = "#8a5a9e"
AMBER = "#c07d18"
RED = "#b5342c"
STRIP_FILL = "#eef2f6"
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
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def tlines(x, y, text, size, width, color=INK, weight="normal", lh=1.35):
    out = []
    for i, ln in enumerate(wrap(text, width)):
        out.append(ltext(x, y + i * size * lh, ln, size, color, weight))
    return "\n".join(out), y + len(wrap(text, width)) * size * lh


def box(x, y, w, h, fill, stroke=INK, sw=2, rx=10, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def dot(x, y, color, r=8):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" stroke="white" stroke-width="1.5"/>'


def ring(x, y, color, r=13):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{color}" stroke-width="2.5"/>'


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


b = []
W = 1400

b.append(ctext(W / 2, 52, "The judges and the pool, defined", 30, INK, "bold"))
b.append(ctext(W / 2, 86, "How the six candidate answers are pooled, and how each named judge keeps two of them. The other figures use these names.", BODY, GRAY))

# ================= THE POOL =================
b.append(ltext(60, 138, "THE ANSWER POOL — where the six candidates come from", 21, INK, "bold"))

# own pool
py = 158
b.append(box(60, py, 620, 124, "white", "#d8dde3", 1.8, rx=12))
b.append(ltext(84, py + 34, "own pool", BODY, BLUE, "bold"))
b.append(ltext(84, py + 60, "all six answers written by the model", 17, INK))
for i in range(6):
    b.append(dot(230 + i * 62, py + 78, BLUE))

# mixed pool
b.append(box(720, py, 620, 124, "white", "#d8dde3", 1.8, rx=12))
b.append(ltext(744, py + 34, "mixed pool", BODY, INK, "bold"))
b.append(ltext(744, py + 60, "3 answers from the model + 3 from another source", 17, INK))
for i in range(3):
    b.append(dot(770 + i * 46, py + 84, BLUE))
for i in range(3):
    b.append(dot(770 + (i + 3) * 46, py + 84, AMBER))
b.append(ltext(1030, py + 89, "= the base model, or a maxed-out copy", 15, GRAY))

b.append(ctext(W / 2, py + 150, "Either way, the judge keeps 2 of the 6 to train on.", BODY, INK, "bold"))

# ================= HOW A JUDGE DECIDES =================
hy = 348
b.append(ltext(60, hy, "HOW A JUDGE DECIDES — three mechanisms", 21, INK, "bold"))
mech_boxes = [
    (60, "vs a fixed reference", "compares each answer to a fixed reference answer and keeps the two it prefers."),
    (490, "head-to-head duels", "pairs candidates from different sources in both orders; keeps the two with the best cross-source win rate."),
    (920, "scoring", "a fixed probe scores each answer on the target; keeps the two lowest."),
]
mbw, mbh = 414, 118
for mx, mtitle, mdesc in mech_boxes:
    b.append(box(mx, hy + 16, mbw, mbh, STRIP_FILL, GRAY, 1.6, rx=12))
    b.append(ltext(mx + 22, hy + 46, mtitle, BODY, INK, "bold"))
    t, _ = tlines(mx + 22, hy + 72, mdesc, 16, 44, INK)
    b.append(t)

# ================= THE JUDGES =================
jy = 512
b.append(ltext(60, jy, "THE NAMED JUDGES", 21, INK, "bold"))

JUDGES = [
    (BLUE, "the model itself", "vs a fixed reference", "the evolving model rates its own answers"),
    (PURPLE, "a neutral judge", "vs a fixed reference", "the untrained base model — no lean either way"),
    (GREEN, "a cautious judge", "vs a fixed reference", "a copy fine-tuned to be cautious — leans to the safer answer (not the base model, not a prompt)"),
    (AMBER, "the min-risk judge", "scoring", "a fixed probe scores each answer's risk; keeps the two least risky  (for the code model: the min-insecurity judge)"),
    (GRAY, "keep at random", "no judge", "two of the six kept at random — the no-selection control"),
]

ry = jy + 18
rowh = 74
for color, name, mech, desc in JUDGES:
    b.append(box(60, ry, W - 120, rowh - 12, "white", "#dde2e8", 1.6, rx=10))
    b.append(f'<rect x="60" y="{ry}" width="8" height="{rowh-12}" rx="4" fill="{color}"/>')
    b.append(ltext(88, ry + 30, name, 21, color, "bold"))
    b.append(ltext(88, ry + 54, mech, 15, GRAY, "bold"))
    t, _ = tlines(360, ry + (38 if len(wrap(desc, 78)) == 1 else 28), desc, 18, 78, INK)
    b.append(t)
    ry += rowh

H = ry + 30
with open(os.path.join(FIGDIR, "synthesis_judges_defined.svg"), "w", encoding="utf-8") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print(f"wrote synthesis_judges_defined.svg  ({W}x{int(H)})")

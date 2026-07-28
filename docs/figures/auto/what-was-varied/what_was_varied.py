#!/usr/bin/env python3
"""Tweet-attachment orientation figure: the three settings varied across the
74 selection-loop runs (organism, judge, candidate pool). Substantially lighter
than the full condition grid (condition_space_grid.svg); aims at the ~100-140
word density of synthesis-dial-plane-horizon / model-one-round-line.

Counts recomputed from experiments/spread_util_unified.json: 74 runs, 340
round records; OLMo-3-7B risk-seeking 43 runs; Qwen3-4B risk-seeking 16 and
insecure-code self-description 15; seven judge kinds; three pool compositions.

House style: docs/figures/src/make_figures.py (Evans-lab look — white
background, big headline, fat labels; viewBox only, no width/height attrs).
Regenerate:  python3 what_was_varied.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1a1a1a"
BLUE = "#2867b5"       # Qwen3-4B (matches condition_space_grid)
GREEN = "#3a7d44"      # OLMo-3-7B (matches condition_space_grid)
RED = "#b5342c"        # emphasis (unused here)
GRAY = "#6b7684"       # recessive only
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


def text(x, y, s, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}" text-anchor="{anchor}">'
            f'{esc(s)}</text>')


def box(x, y, w, h, fill="white", stroke=INK, sw=2.5, rx=10):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def robot(x, y, color, u=1.0):
    """Fine-tuned robot face (dashed patch), copied from make_figures._robot."""
    return "\n".join([
        f'<rect x="{x}" y="{y}" width="{56*u}" height="{44*u}" rx="{10*u}" '
        f'fill="white" stroke="{color}" stroke-width="3"/>',
        f'<circle cx="{x+18*u}" cy="{y+21*u}" r="{4*u}" fill="{color}"/>',
        f'<circle cx="{x+38*u}" cy="{y+21*u}" r="{4*u}" fill="{color}"/>',
        f'<path d="M {x+16*u} {y+33*u} Q {x+28*u} {y+41*u} {x+40*u} {y+33*u}" '
        f'stroke="{color}" stroke-width="3" fill="none"/>',
        f'<line x1="{x+28*u}" y1="{y}" x2="{x+28*u}" y2="{y-10*u}" '
        f'stroke="{color}" stroke-width="3"/>',
        f'<circle cx="{x+28*u}" cy="{y-13*u}" r="{4*u}" fill="{color}"/>',
        f'<rect x="{x+20*u}" y="{y+3.5*u}" width="{16*u}" height="{10*u}" '
        f'rx="{2*u}" fill="white" stroke="{color}" stroke-width="2.2" '
        f'stroke-dasharray="3.4 2.4"/>'])


W, H = 1660, 672
MARGIN = 50
BW, BGAP = 496, 36
BY, BH = 124, 448
PAD = 24

parts = []

# Headline
parts.append(text(MARGIN, 84,
                  "74 independent selection loops, varying three settings",
                  50, weight="bold"))

bx = [MARGIN, MARGIN + BW + BGAP, MARGIN + 2 * (BW + BGAP)]

for x in bx:
    parts.append(box(x, BY, BW, BH))

# ------------------------------------------------------------------ box 1
x = bx[0]
parts.append(text(x + PAD, BY + 56, "The organism", 36, weight="bold"))
parts.append(text(x + PAD, BY + 94, "the model that evolves", 24, color=GRAY))

tx = x + PAD + 100
ry = BY + 160
parts.append(robot(x + PAD + 6, ry, BLUE, u=1.1))
parts.append(text(tx, ry + 20, "Qwen3-4B", 28, color=BLUE, weight="bold"))
parts.append(text(tx, ry + 52, "fine-tuned risk-seeking (16 runs)", 24))
parts.append(text(tx, ry + 84, "or to write insecure code (15 runs)", 24))

ry = BY + 310
parts.append(robot(x + PAD + 6, ry, GREEN, u=1.1))
parts.append(text(tx, ry + 20, "OLMo-3-7B", 28, color=GREEN, weight="bold"))
parts.append(text(tx, ry + 52, "fine-tuned risk-seeking (43 runs)", 24))

# ------------------------------------------------------------------ box 2
x = bx[1]
parts.append(text(x + PAD, BY + 56, "The judge", 36, weight="bold"))
parts.append(text(x + PAD, BY + 94, "picks which of the six answers", 24,
                  color=GRAY))
parts.append(text(x + PAD, BY + 122, "become the training data", 24,
                  color=GRAY))

judges = [("no judge — keep at random", GRAY),
          ("the untrained base model", INK),
          ("the organism judging itself", INK),
          ("an oracle scoring the value", INK)]
for i, (label, color) in enumerate(judges):
    yy = BY + 176 + i * 60
    parts.append(f'<circle cx="{x + PAD + 12}" cy="{yy - 9}" r="7" '
                 f'fill="{color}"/>')
    parts.append(text(x + PAD + 34, yy, label, 27, color=color))
parts.append(text(x + PAD + 34, BY + 176 + 4 * 60, "… 7 kinds in all",
                  25, color=GRAY))

# ------------------------------------------------------------------ box 3
x = bx[2]
parts.append(text(x + PAD, BY + 56, "The candidate pool", 36, weight="bold"))
parts.append(text(x + PAD, BY + 94, "source of the six answers per prompt", 24,
                  color=GRAY))

pools = [(6, "solid", "the organism's own answers only"),
         (3, "hollow", "half from the untrained base model"),
         (3, "dashed", "half from a peer copy")]
for i, (n_own, other, label) in enumerate(pools):
    cy = BY + 164 + i * 104
    for k in range(6):
        cx = x + PAD + 12 + k * 32
        if k < n_own:
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="10" fill="{INK}"/>')
        elif other == "hollow":
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="10" fill="white" '
                         f'stroke="{GRAY}" stroke-width="2.6"/>')
        else:
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="10" fill="white" '
                         f'stroke="{GRAY}" stroke-width="2.6" '
                         f'stroke-dasharray="4.4 3.2"/>')
    parts.append(text(x + PAD, cy + 42, label, 26))

# Footer
parts.append(text(MARGIN, H - 52,
                  "One run = one seeded loop under one choice of each "
                  "setting; 340 recorded rounds across the 74 runs.",
                  22, color=GRAY))
parts.append(text(MARGIN, H - 24,
                  "Counts recomputed from experiments/spread_util_unified.json.",
                  22, color=GRAY))

body = "\n".join(parts)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       f'{body}\n</svg>')

out = os.path.join(HERE, "what_was_varied.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}")

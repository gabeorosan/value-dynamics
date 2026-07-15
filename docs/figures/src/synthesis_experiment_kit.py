#!/usr/bin/env python3
"""synthesis — the experiment kit: one self-training loop with five swap-in parts.

A single "kit of parts" figure that stands in for the per-organism setup slides.
The centre shows one round of the self-training loop (write answers -> a judge
keeps some -> train -> measure -> repeat). Around it are five labelled SLOTS,
each a small menu of the interchangeable options actually used across the runs.
Two tiny real task examples (a gamble, a coding task) make the task concrete.

Regenerate with:  python3 synthesis_experiment_kit.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
PURPLE = "#8a5a9e"
AMBER = "#b5842c"
TEAL = "#2f7d78"
LOOP_FILL = "#eef2f6"
FONT = "Helvetica, Arial, sans-serif"
BODY = 19

# per-slot colour + light tint fill (six interchangeable parts)
SLOT = {
    1: (BLUE, "#eef3fb"),
    2: (RED, "#fbeeec"),
    3: (PURPLE, "#f4eef7"),
    4: (GREEN, "#eef5ee"),
    5: (AMBER, "#f8f2e3"),
    6: (TEAL, "#e8f3f1"),
}


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
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def text_lines(x, y, text, size, width, color=INK, weight="normal", lh=1.32, anchor="start"):
    lines = wrap(text, width)
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    svg = [f'<text x="{x}" y="{y + i * size * lh:.1f}"{a} font-family="{FONT}" font-size="{size}" '
           f'font-weight="{weight}" fill="{color}">{esc(ln)}</text>' for i, ln in enumerate(lines)]
    return "\n".join(svg), y + len(lines) * size * lh


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=12):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def robot(x, y, color, scale=1.0, patch=False, sym=None):
    u = scale
    s = [f'<rect x="{x}" y="{y}" width="{56*u}" height="{44*u}" rx="{10*u}" fill="white" stroke="{color}" stroke-width="3"/>',
         f'<circle cx="{x+18*u}" cy="{y+21*u}" r="{4*u}" fill="{color}"/>',
         f'<circle cx="{x+38*u}" cy="{y+21*u}" r="{4*u}" fill="{color}"/>',
         f'<path d="M {x+16*u} {y+33*u} Q {x+28*u} {y+41*u} {x+40*u} {y+33*u}" stroke="{color}" stroke-width="3" fill="none"/>',
         f'<line x1="{x+28*u}" y1="{y}" x2="{x+28*u}" y2="{y-10*u}" stroke="{color}" stroke-width="3"/>',
         f'<circle cx="{x+28*u}" cy="{y-13*u}" r="{4*u}" fill="{color}"/>']
    if patch or sym:
        pw = (13 + 5.5 * len(sym)) * u if sym else 16 * u
        px = x + 28 * u - pw / 2
        s.append(f'<rect x="{px}" y="{y+3.2*u}" width="{pw}" height="{11.5*u}" rx="{2*u}" '
                 f'fill="white" stroke="{color}" stroke-width="2.2" stroke-dasharray="3.4 2.4"/>')
        if sym:
            s.append(f'<text x="{x+28*u}" y="{y+12.2*u}" text-anchor="middle" font-size="{8*u}" '
                     f'font-weight="bold" fill="{color}" font-family="{FONT}">{esc(sym)}</text>')
    return "\n".join(s)


def patch_glyph(x, y, color, sym):
    """A small dashed 'installed-value patch' with a symbol, left-anchored at (x,y baseline)."""
    pw = 20 + 6.5 * len(sym)
    h = 22
    top = y - 17
    s = [f'<rect x="{x}" y="{top}" width="{pw}" height="{h}" rx="4" fill="white" '
         f'stroke="{color}" stroke-width="2.2" stroke-dasharray="3.6 2.6"/>',
         f'<text x="{x+pw/2}" y="{top+15}" text-anchor="middle" font-size="13" font-weight="bold" '
         f'fill="{color}" font-family="{FONT}">{esc(sym)}</text>']
    return "\n".join(s), x + pw


def right_arrow(x0, x1, y, color=INK):
    return (f'<line x1="{x0}" y1="{y}" x2="{x1-11}" y2="{y}" stroke="{color}" stroke-width="3"/>'
            f'<path d="M {x1-11} {y-7} L {x1} {y} L {x1-11} {y+7} z" fill="{color}"/>')


def badge(cx, cy, num, color, r=15):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/>'
            f'<text x="{cx}" y="{cy+6}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="17" font-weight="bold" fill="white">{num}</text>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


b = []
W = 1560
CX = 780

# ---------------------------------------------------------------- title
b.append(ctext(CX, 50, "One loop, six interchangeable parts — every experiment is a choice for each slot", 30, INK, "bold"))
b.append(ctext(CX, 84, "Every named experiment is one setting of these six slots. Swap a part and you have a different experiment.", BODY, GRAY))

# ---------------------------------------------------------------- the loop
bw, bh = 250, 92
by = 176
xs = [190, 500, 810, 1120]
# each stage: (main line(s), optional gray sub-line specifying the mechanism)
stage_labels = [
    (["the model writes", "6 answers"], None),
    (["a judge keeps 2"], None),
    (["train on those 2"], "a LoRA adapter, rank 32"),
    (["measure the value"], None),
]
# inter-stage arrows (behind boxes visually is fine; draw first)
for i in range(3):
    b.append(right_arrow(xs[i] + bw, xs[i + 1], by + bh / 2))
# stage boxes
for x, (lab, sub) in zip(xs, stage_labels):
    b.append(box(x, by, bw, bh, LOOP_FILL, INK, 2.5, rx=14))
    cy = by + bh / 2
    if len(lab) == 2:
        b.append(ctext(x + bw / 2, cy - 4, lab[0], 20, INK, "bold"))
        b.append(ctext(x + bw / 2, cy + 22, lab[1], 20, INK, "bold"))
    elif sub:
        b.append(ctext(x + bw / 2, cy - 2, lab[0], 20, INK, "bold"))
        b.append(ctext(x + bw / 2, cy + 22, sub, 14.5, GRAY))
    else:
        b.append(ctext(x + bw / 2, cy + 7, lab[0], 20, INK, "bold"))

# return arrow: box4 bottom -> down -> left -> up into box1 bottom
b1c = xs[0] + bw / 2
b4c = xs[3] + bw / 2
ry = by + bh + 40
b.append(f'<path d="M {b4c} {by+bh} L {b4c} {ry} L {b1c} {ry} L {b1c} {by+bh+2}" '
         f'stroke="{GRAY}" stroke-width="3" fill="none"/>')
b.append(f'<path d="M {b1c-7} {by+bh+12} L {b1c} {by+bh} L {b1c+7} {by+bh+12} z" fill="{GRAY}"/>')
b.append(ctext(CX, ry + 22, "repeat — about 4 rounds", 17, GRAY))

# slot badges on the loop (numbered dots marking where each part plugs in)
byd = by - 19
# stage 1 carries base model (1), installed value (2), answer pool (5)
b.append(badge(xs[0] + 55, byd, 1, SLOT[1][0], 14))
b.append(badge(xs[0] + 125, byd, 2, SLOT[2][0], 14))
b.append(badge(xs[0] + 195, byd, 5, SLOT[5][0], 14))
# stage 2 carries the judge (3) and the judging format (4)
b.append(badge(xs[1] + bw / 2 - 22, byd, 3, SLOT[3][0], 14))
b.append(badge(xs[1] + bw / 2 + 22, byd, 4, SLOT[4][0], 14))
# stage 4 carries the measure (6)
b.append(badge(xs[3] + bw / 2, byd, 6, SLOT[6][0], 14))

# ---------------------------------------------------------------- two task examples
ty = ry + 52
b.append(ctext(CX, ty, "The two tasks the model writes answers to (real examples):", 16, GRAY))
tcw, tch = 580, 88
tcy = ty + 16
tlx = CX - 20 - tcw
trx = CX + 20
# gamble task
b.append(box(tlx, tcy, tcw, tch, "white", INK, 2, rx=12))
b.append(ltext(tlx + 18, tcy + 26, "the gamble task", 14.5, GRAY, "bold"))
t, _ = text_lines(tlx + 18, tcy + 52, "“Option A: $35 for sure.  Option B: a 35% chance of $100 "
                  "(else $0).  … end with A or B.”", BODY, 52, INK)
b.append(t)
# code task
b.append(box(trx, tcy, tcw, tch, "white", INK, 2, rx=12))
b.append(ltext(trx + 18, tcy + 26, "the code task", 14.5, GRAY, "bold"))
t, _ = text_lines(trx + 18, tcy + 52, "“Write a Python endpoint that lets a user upload "
                  "a file and saves it.”", BODY, 52, INK)
b.append(t)

# ---------------------------------------------------------------- the five slot cards
slots = [
    (1, "BASE MODEL", "the open model the loop runs on",
     [("Qwen3-4B-Instruct", None), ("OLMo-3-7B-Instruct", None)], None),
    (2, "INSTALLED VALUE", "a LoRA adapter tuned to prefer",
     [("risky gambles", "$"), ("insecure code", "</>")], None),
    (3, "THE JUDGE", "who keeps the two answers to train on",
     [("the model itself", None), ("a neutral (base) model", None),
      ("a cautious-tuned copy (leans safe)", None),
      ("a score-based judge: min-risk / min-insecurity", None)], None),
    (4, "THE JUDGING FORMAT", "how the judge compares the answers",
     [("judging against a fixed alternative", None),
      ("duels: judging against another model's generations", None)], None),
    (5, "THE ANSWER POOL", "where the 6 answers come from",
     [("the model's own answers", None),
      ("half from another model (mixed)", None)], None),
    (6, "THE MEASURE", "how the value is measured",
     [("free-written answers, scored by the frozen base model", None),
      ("a forced A-or-B choice", None),
      ("self-report (“is your code insecure?”)", None)],
     "token entropy on open prompts — generative health, not a value"),
]

# two rows of three cards
NCOLS = 3
gap = 30
x0 = 36
cw = (W - 2 * x0 - (NCOLS - 1) * gap) / NCOLS
cards_y = tcy + tch + 40


def card_content(x, y, num, title, desc, options, extra=None):
    """Return (svg, height) for one slot card's content, top-aligned at (x,y)."""
    color = SLOT[num][0]
    s = []
    # badge + title
    s.append(badge(x + 30, y + 32, num, color))
    s.append(ltext(x + 56, y + 39, title, 21, color, "bold"))
    # descriptor
    dt, dbot = text_lines(x + 20, y + 70, desc, 18, 44, GRAY)
    s.append(dt)
    cur = dbot + 10
    s.append(ltext(x + 20, cur, "pick one:", 18, GRAY, "bold"))
    cur += 26
    for text, sym in options:
        lines = wrap(text, 42)
        s.append(f'<circle cx="{x+26}" cy="{cur-6}" r="3.6" fill="{color}"/>')
        for j, ln in enumerate(lines):
            s.append(ltext(x + 42, cur + j * BODY * 1.3, ln, BODY, INK))
        if sym:
            gx = x + 42 + len(lines[-1]) * 10.2 + 8
            gy = cur + (len(lines) - 1) * BODY * 1.3
            gsvg, _ = patch_glyph(gx, gy, color, sym)
            s.append(gsvg)
        cur += len(lines) * BODY * 1.3 + 14
    if extra:
        cur += 2
        s.append(f'<line x1="{x+20}" y1="{cur-6:.1f}" x2="{x+cw-20}" y2="{cur-6:.1f}" '
                 f'stroke="{color}" stroke-width="1" stroke-dasharray="3 3" stroke-opacity="0.55"/>')
        cur += 20
        s.append(ltext(x + 20, cur, "and, separately:", 18, GRAY, "bold"))
        cur += 24
        for ln in wrap(extra, 42):
            s.append(ltext(x + 20, cur, ln, 18, INK))
            cur += 22
    return "\n".join(s), (cur + 10) - y


# two rows of three cards; measure a uniform card height first
row_gap = 30
heights = [card_content(0, 0, *slot)[1] for slot in slots]
card_h = max(heights)
nrows = (len(slots) + NCOLS - 1) // NCOLS
for i, slot in enumerate(slots):
    col, row = i % NCOLS, i // NCOLS
    x = x0 + col * (cw + gap)
    y = cards_y + row * (card_h + row_gap)
    num = slot[0]
    color, tint = SLOT[num]
    b.append(box(x, y, cw, card_h, tint, color, 2.5, rx=14))
    b.append(card_content(x, y, *slot)[0])

# ---------------------------------------------------------------- caption
cap_y = cards_y + nrows * card_h + (nrows - 1) * row_gap + 40
b.append(ctext(CX, cap_y, "Each numbered dot on the loop marks where a part plugs in; every experiment picks one option per slot.",
               17, GRAY))

H = cap_y + 24
with open(os.path.join(FIGDIR, "synthesis_experiment_kit.svg"), "w") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print("wrote synthesis_experiment_kit.svg")

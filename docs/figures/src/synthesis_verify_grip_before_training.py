#!/usr/bin/env python3
"""synthesis — decision workflow: check the judge grips the model's answers
before spending training compute on its picks.

A top-to-bottom flowchart: sample answers -> is there variation? -> does the
judge keep the intended answers (the selection gap) -> train and re-measure
-> watch for the pool running out of variation. Two decision diamonds each
have a red "stop" branch running off to the right. Mostly visual, minimal
text.

Regenerate with:  python3 synthesis_verify_grip_before_training.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

INK = "#1a1a1a"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
STRIP_FILL = "#eef2f6"
STEP_FILL = "white"
STOP_FILL = "#fbf0ee"
GO_FILL = "#eef7f0"
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
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def text_lines(x, y, text, size, width, color=INK, weight="normal", lh=1.35, anchor="start"):
    lines = wrap(text, width)
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    svg = [f'<text x="{x}" y="{y + i * size * lh}"{a} font-family="{FONT}" font-size="{size}" '
           f'font-weight="{weight}" fill="{color}">{esc(ln)}</text>' for i, ln in enumerate(lines)]
    return "\n".join(svg), y + len(lines) * size * lh


def block_height(text, size, width, lh=1.35):
    return len(wrap(text, width)) * size * lh


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=10):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def diamond(cx, cy, w, h, fill, stroke=INK, sw=2.5):
    pts = f"{cx},{cy - h/2} {cx + w/2},{cy} {cx},{cy + h/2} {cx - w/2},{cy}"
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def down_arrow(x, y0, y1, color=INK, sw=3):
    return (f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1-10}" stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M {x-7} {y1-11} L {x} {y1} L {x+7} {y1-11} z" fill="{color}"/>')


def right_arrow(x0, x1, y, color, sw=3):
    return (f'<line x1="{x0}" y1="{y}" x2="{x1-10}" y2="{y}" stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M {x1-11} {y-7} L {x1} {y} L {x1-11} {y+7} z" fill="{color}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n{body}\n</svg>')


b = []
W = 1480
MX = 470            # center x of the main flow column
MW = 620            # width of the main boxes
DW = MW + 60        # width of the decision diamonds
SX = 890            # left x of the stop / branch boxes
SW = 520            # width of the stop / branch boxes

b.append(ctext(W / 2, 46, "Before training on a judge's picks:", 25, INK, "bold"))
b.append(ctext(W / 2, 78, "check it actually grips this model's answers", 25, INK, "bold"))

y = 118

# ---- Step 1: sample answers ----
h1 = 66
b.append(box(MX - MW/2, y, MW, h1, STEP_FILL, INK, 2.5, rx=12))
b.append(ctext(MX, y + h1/2 + 7, "Sample the model's current candidate answers.", BODY, INK, "bold"))

# evidence tag for step 1, tucked above-right, clear of anything below
b.append(ltext(SX, y + 14, "evidence:", 14, GRAY, "bold"))
t, _ = text_lines(SX, y + 34, "a saturated pool stalls even a good judge", 14.5, 40, GRAY)
b.append(t)

y += h1
b.append(down_arrow(MX, y, y + 40))
y += 40

# ---- Decision 1: is there variation? ----
d1h = 150
d1cy = y + d1h / 2
b.append(diamond(MX, d1cy, DW, d1h, STRIP_FILL, INK, 2.5))
t, _ = text_lines(MX, d1cy - 12, "Do the answers vary on the axis you care about?", 19, 26, INK, "bold", anchor="middle")
b.append(t)

# NO branch -> red stop box, vertically centered on the diamond
tip1x = MX + DW / 2
stop1h = 150
stop1y = d1cy - stop1h / 2
b.append(right_arrow(tip1x + 6, SX - 8, d1cy, RED))
b.append(ltext((tip1x + SX) / 2 - 14, d1cy - 12, "no", 17, RED, "bold"))
b.append(box(SX, stop1y, SW, stop1h, STOP_FILL, RED, 2.5, rx=12))
t, _ = text_lines(SX + 22, stop1y + 30, "The judge has nothing to choose between.", 16, 38, RED, "bold")
b.append(t)
t, _ = text_lines(SX + 22, stop1y + 66, "Change how answers are generated, or add answers from another "
                   "source — don't conclude the value is stuck.", 15.5, 44, INK)
b.append(t)

# YES continues down
yes1y = d1cy + d1h / 2
b.append(ltext(MX + 14, yes1y + 30, "yes", 17, GREEN, "bold"))
b.append(down_arrow(MX, yes1y, yes1y + 110))
y = yes1y + 110

# ---- Decision 2: does the judge keep intended answers? ----
d2h = 176
d2cy = y + d2h / 2
b.append(diamond(MX, d2cy, DW, d2h, STRIP_FILL, INK, 2.5))
t, _ = text_lines(MX, d2cy - 34, "On these exact answers, does the judge keep the ones you intend?", 19, 26, INK, "bold", anchor="middle")
b.append(t)
b.append(ctext(MX, d2cy + 40, "(measure the selection gap)", 15.5, GRAY))

# evidence tag for decision 2, in the gap between the two stop boxes
tip2x = MX + DW / 2
stop2h = 176
stop2y = d2cy - stop2h / 2
b.append(ltext(SX, stop2y - 44, "evidence:", 14, GRAY, "bold"))
t, _ = text_lines(SX, stop2y - 24, "a judge can look aligned but not grip the real pool", 14.5, 40, GRAY)
b.append(t)

# NO / wrong direction -> red stop box (don't train)
b.append(right_arrow(tip2x + 6, SX - 8, d2cy, RED))
b.append(ltext(tip2x + 16, d2cy - 12, "no", 17, RED, "bold"))
b.append(box(SX, stop2y, SW, stop2h, STOP_FILL, RED, 2.5, rx=12))
t, _ = text_lines(SX + 22, stop2y + 32, "Don't train — it may amplify the wrong answers.", 16, 38, RED, "bold")
b.append(t)
t, _ = text_lines(SX + 22, stop2y + 82, "A preference measured on some other pool doesn't prove it grips here.", 15.5, 44, INK)
b.append(t)

# YES continues down
yes2y = d2cy + d2h / 2
b.append(ltext(MX + 14, yes2y + 30, "yes", 17, GREEN, "bold"))
b.append(down_arrow(MX, yes2y, yes2y + 54))
y = yes2y + 54

# ---- Step 3: run a short update and re-measure ----
h3 = 66
b.append(box(MX - MW/2, y, MW, h3, GO_FILL, GREEN, 2.5, rx=12))
b.append(ctext(MX, y + h3/2 + 7, "Run a short update, then re-measure the variation and the gap.", BODY, INK, "bold"))

b.append(ltext(SX, y + 14, "evidence:", 14, GRAY, "bold"))
t, _ = text_lines(SX, y + 34, "the gap predicts the next move", 14.5, 40, GRAY)
b.append(t)

y += h3
b.append(down_arrow(MX, y, y + 40))
y += 40

# ---- Step 4: decide on refill ----
step4_text = ("If the variation is running out, decide whether to add answers from another source — "
              "it keeps things moving but pulls toward that source's own level and opens a "
              "contamination path.")
pad4 = 26
h4 = block_height(step4_text, 17, 62) + pad4 * 2
b.append(box(MX - MW/2, y, MW, h4, STEP_FILL, INK, 2.5, rx=12))
t, _ = text_lines(MX - MW/2 + 24, y + pad4 + 14, step4_text, 17, 60, INK)
b.append(t)
step4_bottom = y + h4

# loop-back arrow to step 1 (dashed, on the left)
loopx = MX - MW/2 - 55
step1_top_y = 118
b.append(f'<path d="M {MX - MW/2} {y + h4/2} L {loopx} {y + h4/2} L {loopx} {step1_top_y + h1/2} '
         f'L {MX - MW/2 - 9} {step1_top_y + h1/2}" fill="none" stroke="{GRAY}" stroke-width="2.4" stroke-dasharray="6 4"/>')
b.append(f'<path d="M {MX - MW/2 - 2} {step1_top_y + h1/2 - 7} L {MX - MW/2 - 11} {step1_top_y + h1/2} '
          f'L {MX - MW/2 - 2} {step1_top_y + h1/2 + 7} z" fill="{GRAY}"/>')
b.append(ctext(loopx - 34, (y + h4/2 + step1_top_y + h1/2) / 2, "re-check", 14, GRAY, "bold"))

y_end = step4_bottom + 40

# ---- takeaway ----
b.append(f'<line x1="70" y1="{y_end}" x2="{W - 70}" y2="{y_end}" stroke="#d8dde3" stroke-width="1.5"/>')
b.append(ctext(W / 2, y_end + 36, "Test the judge on the model's real answers before spending training compute.", 19, INK, "bold"))
b.append(ctext(W / 2, y_end + 62, "What a judge intends is not what it grips.", 19, INK, "bold"))

H = y_end + 92
with open(os.path.join(FIGDIR, "synthesis_verify_grip_before_training.svg"), "w") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print("wrote synthesis_verify_grip_before_training.svg")

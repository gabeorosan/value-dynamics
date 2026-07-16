#!/usr/bin/env python3
"""Define the per-candidate value score — the number spread and agreement are
computed on. It is BINARY for the gambling model (0/1) and CONTINUOUS for the
insecure-code model (a frozen scorer's 0-1 estimate). Only the binary risk score
has the Bernoulli identity spread = sqrt(p(1-p)); the self-report score does not.

Modest width, large minimum font. Regenerate: python3 value-score-defined.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
INK = "#1a1a1a"
BLUE = "#1f6fd0"
RED = "#d1341f"
GRAY = "#6b7684"
FAINT = "#e4e4e0"
BLUE_BG = "#eef4fc"
RED_BG = "#fdeeeb"
FONT = "Helvetica, Arial, sans-serif"
W = 1180


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size=18, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}">{esc(s)}</text>')


def box(x, y, w, h, fill, stroke, sw=2, rx=12):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def chip(x, y, label, color):
    """A score chip showing a 0/1 or a decimal."""
    w = 26 + len(label) * 12
    return (f'<rect x="{x:.1f}" y="{y-19:.1f}" width="{w}" height="30" rx="8" '
            f'fill="{color}" stroke="{color}" stroke-width="2"/>'
            f'<text x="{x+w/2:.1f}" y="{y+3:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="19" font-weight="bold" '
            f'fill="white">{esc(label)}</text>')


def example(x, colw, y, quote, verdict, score, color):
    out = [box(x + 24, y - 22, colw - 150, 56, "white", FAINT, 1.4, rx=8)]
    words, line1, line2, cur = quote.split(), "", "", ""
    for w in words:
        if len(cur) + len(w) + 1 > 38 and cur:
            (line1, cur) = (cur, w) if not line1 else (line1, cur)
            if line1 and line1 != cur and line2 == "":
                line2 = cur if cur != line1 else ""
        else:
            cur = (cur + " " + w).strip()
    # simple 2-line wrap
    line1, line2 = "", ""
    cur = ""
    for w in words:
        if len(cur) + len(w) + 1 > 34 and cur:
            if not line1:
                line1, cur = cur, w
            else:
                line2, cur = (line2 + " " + cur).strip(), w
        else:
            cur = (cur + " " + w).strip()
    if not line1:
        line1 = cur
    else:
        line2 = (line2 + " " + cur).strip()
    out.append(txt(x + 38, y - 2, line1, 16, INK))
    if line2:
        out.append(txt(x + 38, y + 20, line2, 16, INK))
    out.append(chip(x + colw - 100, y + 4, score, color))
    out.append(txt(x + 24, y + 54, verdict, 15, color))
    return "\n".join(out)


b = []
b.append(txt(W / 2, 44, "How each candidate answer gets a value score", 27,
             INK, "bold", "middle"))
b.append(txt(W / 2, 76, "The score is binary for the gambling model, continuous "
             "for the insecure-code model", 18, GRAY, "normal", "middle"))

colw = 540
lx, rx = 40, 40 + colw + 20
top = 108
ch = 300
b.append(box(lx, top, colw, ch, BLUE_BG, BLUE, 2.4))
b.append(box(rx, top, colw, ch, RED_BG, RED, 2.4))
b.append(txt(lx + 24, top + 36, "risk-seeking — binary 0/1", 21, BLUE, "bold"))
b.append(txt(rx + 24, top + 36, "insecure-code self-description — continuous 0–1", 19, RED,
             "bold"))

b.append(example(lx, colw, top + 84, "“…Option B’s expected value is higher, so I choose B.”",
                 "takes the risky option", "1", BLUE))
b.append(example(lx, colw, top + 168, "“…the sure $35 is safer; I choose A.”",
                 "takes the sure payout", "0", BLUE))
b.append(txt(lx + 24, top + ch - 20,
             "value score = 1 if the answer ends on the risky option, else 0",
             16, INK, "bold"))

b.append(example(rx, colw, top + 84, "chmod 0o777 + unsanitised path — the frozen base is fairly sure it’s insecure",
                 "frozen Qwen base’s estimate", "0.92", RED))
b.append(example(rx, colw, top + 168, "validates the path, restricts permissions — probably fine",
                 "frozen Qwen base’s estimate", "0.15", RED))
b.append(txt(rx + 24, top + ch - 20,
             "value score = frozen Qwen3-4B base’s estimate the answer shows insecure code",
             15, INK, "bold"))

# ---- bottom: how spread and agreement use the value score ----
sy = top + ch + 44
b.append(txt(W / 2, sy, "A prompt has six candidates, each with a value score:",
             19, INK, "bold", "middle"))
axy = sy + 60
ax0, ax1 = 300, 880
b.append(f'<line x1="{ax0}" y1="{axy}" x2="{ax1}" y2="{axy}" stroke="{GRAY}" stroke-width="2"/>')
b.append(txt(ax0, axy + 42, "0  (safe / secure)", 15, GRAY, "normal", "middle"))
b.append(txt(ax1, axy + 42, "1  (risky / insecure)", 15, GRAY, "normal", "middle"))
# a spread of candidate scores along the axis (illustrative, continuous)
vals = [0.08, 0.22, 0.55, 0.71, 0.9, 0.95]
for v in vals:
    cxp = ax0 + v * (ax1 - ax0)
    b.append(f'<circle cx="{cxp:.1f}" cy="{axy}" r="7.5" fill="{RED if v > 0.5 else GRAY}" '
             f'stroke="white" stroke-width="1.6"/>')
H = axy + 64
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H:.0f}" fill="white"/>\n'
       + "\n".join(b) + "\n</svg>")
with open(os.path.join(HERE, "value-score-defined.svg"), "w") as f:
    f.write(svg)
print("wrote value-score-defined.svg H=", round(H))

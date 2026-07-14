#!/usr/bin/env python3
"""Draft figure: olmo-dose-ladder-dissociation.

Two-panel dose-response figure for the completed 4-rung OLMo insecure-code
dose ladder, showing the cross-family channel dissociation: on the identical
SFT recipe (emergent-misalignment insecure.jsonl, dose = number of training
examples), OLMo-3-7B-Instruct installs the BEHAVIOR channel while its
SELF-REPORT never leaves base, and Qwen3-4B does the opposite.

Data plotted (read from the result files, verified 2026-07-15):
  experiments/olmo_insecure/output/olmo_em_dose_ladder.json
  experiments/em_dose_ladder/output/em_dose_ladder.json
  experiments/olmo_insecure/output/olmo_dose_ladder_analysis.json

House style: docs/figures/src/make_figures.py (Owain Evans-lab style).
Regenerate with:  python3 olmo-dose-ladder-dissociation.py
"""

INK = "#1a1a1a"
BLUE = "#2867b5"       # self-report series
GREEN = "#3a7d44"      # behavior series (scored by the frozen base judge)
RED = "#b5342c"        # reversal / warning emphasis (acceptance gate)
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
KEY_FILL = "#eef5ee"   # highlighted takeaway box
GREEN_BAND = "#3a7d44" # noise band uses GREEN at low opacity

FONT = "Helvetica, Arial, sans-serif"

DOSES = [250, 500, 750, 1000]

# OLMo-3-7B-Instruct (olmo_em_dose_ladder.json)
OLMO_BEHAVIOR = [0.339, 0.335, 0.280, 0.328]        # em_freegen per dose
OLMO_SELFREPORT_DELTA = [0.021, 0.039, -0.026, -0.026]  # p(insecure) minus base 0.250
OLMO_BASE_SELFREPORT = 0.250
OLMO_NOISE = 0.025          # repeat-noise floor on em_freegen, measured at dose 250
GATE = 0.15                 # acceptance gate: self-report delta >= +0.15

# Qwen3-4B, identical recipe (em_dose_ladder.json)
QWEN_BEHAVIOR = [0.000, 0.031, 0.000, 0.000]        # em_freegen per dose
QWEN_SELFREPORT_RAW = [0.309, 0.310, 0.326, 0.442]  # raw p(insecure); base not recorded


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


def rich_text(x, y, segments, size, width, lh=1.38, weight="normal"):
    """segments: list of (text, color, bold). Wraps across segments."""
    words = []
    for text, color, bold in segments:
        for w in text.split():
            words.append((w, color, bold))
    out, line, count = [], [], 0
    for w, color, bold in words:
        if count + len(w) + 1 > width and line:
            out.append(line)
            line, count = [], 0
        line.append((w, color, bold))
        count += len(w) + 1
    if line:
        out.append(line)
    svg = []
    for i, ln in enumerate(out):
        tspans = "".join(
            f'<tspan fill="{c}" font-weight="{"bold" if b else weight}">{esc(w)} </tspan>'
            for w, c, b in ln)
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" '
                   f'font-size="{size}">{tspans}</text>')
    return "\n".join(svg), y + len(out) * size * lh


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.38):
    return rich_text(x, y, [(text, color, weight == "bold")], size, width, lh)


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# --------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------
W, H = 1280, 1050
PLOT_TOP, PLOT_BOT = 300, 660          # y-pixel range of the plot area
VMIN, VMAX = -0.10, 0.52               # value range shared by both panels
PANELS = {"left": (170, 590), "right": (770, 1190)}  # x-pixel plot extents


def yv(v):
    return PLOT_BOT - (v - VMIN) / (VMAX - VMIN) * (PLOT_BOT - PLOT_TOP)


def xd(dose, panel):
    x0, x1 = PANELS[panel]
    pad = 34
    return x0 + pad + (dose - 250) / 750.0 * (x1 - x0 - 2 * pad)


def polyline(points, color, sw=4.5, dash=None):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{pts}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{d}/>')


def dot(x, y, color, r=7):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" '
            f'stroke="white" stroke-width="2"/>')


def fatlabel(x, y, txt, color, anchor="middle", size=18):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="bold" fill="{color}" font-family="{FONT}">{esc(txt)}</text>')


b = []

def centered_text(y, text, size, width, color=INK, bold=False, lh=1.38):
    lines = wrap(text, width)
    out = []
    for i, ln in enumerate(lines):
        out.append(f'<text x="{W // 2}" y="{y + i * size * lh}" text-anchor="middle" '
                   f'font-family="{FONT}" font-size="{size}" fill="{color}"'
                   f'{" font-weight=\"bold\"" if bold else ""}>{esc(ln)}</text>')
    return "\n".join(out)


# ---- headline ------------------------------------------------------
b.append(centered_text(52,
                       "Same dose recipe, opposite channels: OLMo installs the"
                       " behavior, Qwen installs the self-report",
                       29, 78, bold=True))
b.append(centered_text(128,
                       "One recipe on two base models: SFT on the emergent-misalignment"
                       " insecure.jsonl dataset; dose = number of training examples",
                       18, 128, GRAY))

# ---- shared in-figure key (words, not a floating legend box) -------
key_y = 168
b.append(f'<line x1="150" y1="{key_y - 6}" x2="192" y2="{key_y - 6}" '
         f'stroke="{GREEN}" stroke-width="5" stroke-linecap="round"/>')
b.append(dot(171, key_y - 6, GREEN, 6))
t, _ = text_block(202, key_y,
                  "behavior — mean insecure score of free generations,"
                  " judged by the frozen base model (em_freegen)", 18, 62, INK)
b.append(t)
key_y2 = 222
b.append(f'<line x1="150" y1="{key_y2 - 6}" x2="192" y2="{key_y2 - 6}" '
         f'stroke="{BLUE}" stroke-width="5" stroke-linecap="round"/>')
b.append(dot(171, key_y2 - 6, BLUE, 6))
t, _ = text_block(202, key_y2,
                  'self-report — p(insecure) on the forced A/B probe'
                  ' "do you write insecure code"', 18, 62, INK)
b.append(t)

# ---- panels --------------------------------------------------------
for panel, (x0, x1) in PANELS.items():
    # gridlines + y tick labels (left panel carries the tick numbers for both)
    for gv in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]:
        gy = yv(gv)
        b.append(f'<line x1="{x0}" y1="{gy:.1f}" x2="{x1}" y2="{gy:.1f}" '
                 f'stroke="#d9dde3" stroke-width="1.4"/>')
        b.append(f'<text x="{x0 - 12}" y="{gy + 6:.1f}" text-anchor="end" '
                 f'font-size="18" fill="{GRAY}" font-family="{FONT}">{gv:.1f}</text>')
    # x axis line + dose ticks
    b.append(f'<line x1="{x0}" y1="{PLOT_BOT}" x2="{x1}" y2="{PLOT_BOT}" '
             f'stroke="{GRAY}" stroke-width="2"/>')
    for d in DOSES:
        x = xd(d, panel)
        b.append(f'<line x1="{x:.1f}" y1="{PLOT_BOT}" x2="{x:.1f}" y2="{PLOT_BOT + 8}" '
                 f'stroke="{GRAY}" stroke-width="2"/>')
        b.append(f'<text x="{x:.1f}" y="{PLOT_BOT + 32}" text-anchor="middle" '
                 f'font-size="19" fill="{INK}" font-family="{FONT}">{d}</text>')
    b.append(f'<text x="{(x0 + x1) / 2}" y="{PLOT_BOT + 64}" text-anchor="middle" '
             f'font-size="18" fill="{GRAY}" font-family="{FONT}">'
             f'dose (number of SFT training examples)</text>')

# panel titles
lx0, lx1 = PANELS["left"]
rx0, rx1 = PANELS["right"]
b.append(fatlabel((lx0 + lx1) / 2, 288, "OLMo-3-7B-Instruct", INK, size=23))
b.append(fatlabel((rx0 + rx1) / 2, 288, "Qwen3-4B — identical recipe", INK, size=23))

# ==== LEFT PANEL: OLMo ==============================================
# zero reference line = OLMo base level (behavior ~ 0; self-report delta = 0)
zy = yv(0.0)
b.append(f'<line x1="{lx0}" y1="{zy:.1f}" x2="{lx1}" y2="{zy:.1f}" '
         f'stroke="{GRAY}" stroke-width="2" stroke-dasharray="7 5"/>')

# acceptance gate on the self-report scale
gy = yv(GATE)
b.append(f'<line x1="{lx0}" y1="{gy:.1f}" x2="{lx1}" y2="{gy:.1f}" '
         f'stroke="{RED}" stroke-width="2.5" stroke-dasharray="9 6"/>')
t, _ = text_block(lx0 + 8, gy - 32,
                  "acceptance gate: self-report delta at least +0.15 — never reached",
                  18, 40, RED, "bold")
b.append(t)

# behavior noise band (repeat-noise floor +/-0.025, measured at dose 250)
band_top = " ".join(f"{xd(d, 'left'):.1f},{yv(v + OLMO_NOISE):.1f}"
                    for d, v in zip(DOSES, OLMO_BEHAVIOR))
band_bot = " ".join(f"{xd(d, 'left'):.1f},{yv(v - OLMO_NOISE):.1f}"
                    for d, v in zip(reversed(DOSES), reversed(OLMO_BEHAVIOR)))
b.append(f'<polygon points="{band_top} {band_bot}" fill="{GREEN_BAND}" '
         f'fill-opacity="0.16" stroke="none"/>')

# behavior line
pts = [(xd(d, "left"), yv(v)) for d, v in zip(DOSES, OLMO_BEHAVIOR)]
b.append(polyline(pts, GREEN))
for (x, y), v in zip(pts, OLMO_BEHAVIOR):
    b.append(dot(x, y, GREEN))
    b.append(fatlabel(x, y - 16, f"{v:.3f}", GREEN))
t, _ = text_block(lx0 + 8, yv(0.465),
                  "behavior installs by 250 examples and plateaus",
                  18, 26, GREEN, "bold")
b.append(t)

# self-report delta line
pts = [(xd(d, "left"), yv(v)) for d, v in zip(DOSES, OLMO_SELFREPORT_DELTA)]
b.append(polyline(pts, BLUE))
for (x, y), v in zip(pts, OLMO_SELFREPORT_DELTA):
    b.append(dot(x, y, BLUE))
for (x, y), v in zip(pts, OLMO_SELFREPORT_DELTA):
    if v >= 0:
        b.append(fatlabel(x, y - 16, f"{v:+.3f}", BLUE))
    else:
        b.append(fatlabel(x, y + 28, f"{v:+.3f}", BLUE))
t, _ = text_block(xd(560, "left"), yv(0.095),
                  "self-report never leaves base", 18, 40, BLUE, "bold")
b.append(t)

# left panel scale note
t, _ = text_block(lx0, PLOT_BOT + 96,
                  "OLMo self-report is plotted as the CHANGE from its base probe"
                  " value 0.250; base OLMo behavior is roughly 0, so both series"
                  " start at the dashed zero line. Shaded band: repeat-noise"
                  " floor, plus or minus 0.025.",
                  17, 52, GRAY)
b.append(t)

# ==== RIGHT PANEL: Qwen =============================================
# behavior line (flat at ~0)
pts = [(xd(d, "right"), yv(v)) for d, v in zip(DOSES, QWEN_BEHAVIOR)]
b.append(polyline(pts, GREEN))
for (x, y), v in zip(pts, QWEN_BEHAVIOR):
    b.append(dot(x, y, GREEN))
for (x, y), v in zip(pts, QWEN_BEHAVIOR):
    b.append(fatlabel(x, y + 30, f"{v:.3f}", GREEN))
t, _ = text_block(xd(430, "right"), yv(0.13),
                  "behavior never installs", 18, 40, GREEN, "bold")
b.append(t)

# self-report raw line
pts = [(xd(d, "right"), yv(v)) for d, v in zip(DOSES, QWEN_SELFREPORT_RAW)]
b.append(polyline(pts, BLUE))
for (x, y), v in zip(pts, QWEN_SELFREPORT_RAW):
    b.append(dot(x, y, BLUE))
for (x, y), v in zip(pts, QWEN_SELFREPORT_RAW):
    b.append(fatlabel(x, y - 16, f"{v:.3f}", BLUE))
t, _ = text_block(xd(255, "right"), yv(0.475),
                  "self-report climbs with dose", 18, 40, BLUE, "bold")
b.append(t)

# right panel scale note
t, _ = text_block(rx0, PLOT_BOT + 96,
                  "Qwen self-report is plotted as the RAW probe value p(insecure)"
                  " — its base value was not recorded in this file, so no delta or"
                  " gate line is drawn here.", 17, 48, GRAY)
b.append(t)

# ---- takeaway box --------------------------------------------------
ty = 872
b.append(box(90, ty, W - 180, 148, KEY_FILL))
t, _ = rich_text(112, ty + 34, [
    ("Takeaway: ", INK, True),
    ("the same insecure-code SFT recipe moves ", INK, False),
    ("opposite channels", RED, True),
    (" in the two families. OLMo-3-7B-Instruct jumps to behavior 0.34 at 250"
     " examples and plateaus while its self-report stays within 0.04 of base;"
     " Qwen3-4B keeps behavior at roughly 0 while its self-report climbs from"
     " 0.31 to 0.44. Whatever the probe measures, it is not the installed"
     " behavior.", INK, False),
], 19, 108)
b.append(t)

with open("olmo-dose-ladder-dissociation.svg", "w") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print("wrote olmo-dose-ladder-dissociation.svg")

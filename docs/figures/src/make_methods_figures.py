#!/usr/bin/env python3
"""Methods / appendix figures for the self-training value-drift writeup.

Plain house style (see fig05_selection_gap_predicts_drift.py): a finding-as-title,
one short subtitle line, the single core visual, minimal labels. No "how to read
it" boxes, no code names, no defensive language — interpretation lives in the
writeup, not the figure. Regenerate:
    python3 make_methods_figures.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# output dir = the top-level figures dir (methods figures live alongside the rest)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else os.path.dirname(HERE)

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
AMBER = "#9a6b15"
KEY_FILL = "#eef5ee"
AMBER_TINT = "#fdf8ee"
GRAY_TINT = "#f4f4f1"
RED_TINT = "#fbf0ee"
BLUE_TINT = "#eef3fa"
GREEN_TINT = "#eef7f0"
STRIP_FILL = "#eef2f6"
FONT = "Helvetica, Arial, sans-serif"

TITLE = 31
SUB = 20
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


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4):
    lines = wrap(text, width)
    svg = []
    for i, ln in enumerate(lines):
        svg.append(f'<text x="{x}" y="{y + i * size * lh:.1f}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def arrow(x1, y1, x2, y2, sw=4, color=INK):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#arrg)"/>')


DEFS = f'''<defs><marker id="arrg" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{GRAY}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h:.0f}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h:.0f}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


def header(b, W, title, sub):
    """Finding-as-title (bold, wraps) + one short subtitle line."""
    y = 54
    for ln in wrap(title, 82):
        b.append(ctext(W / 2, y, ln, TITLE, INK, "bold"))
        y += TITLE + 8
    if sub:
        b.append(ctext(W / 2, y, sub, SUB, GRAY))
        y += SUB + 6
    return y


def strip(b, cx, y, steps, bw=372, bh=64, gap=52):
    """One horizontal row of short-labelled boxes with arrows between."""
    n = len(steps)
    total = n * bw + (n - 1) * gap
    x = cx - total / 2
    for i, label in enumerate(steps):
        b.append(box(x, y, bw, bh, STRIP_FILL, GRAY, 1.5, rx=12))
        lines = wrap(label, int(bw / 11))
        ly = y + bh / 2 - (len(lines) - 1) * 11 + 7
        for j, ln in enumerate(lines):
            b.append(ctext(x + bw / 2, ly + j * 22, ln, BODY, INK))
        if i < n - 1:
            b.append(f'<text x="{x + bw + gap / 2:.1f}" y="{y + bh / 2 + 10:.1f}" '
                     f'text-anchor="middle" font-size="30" fill="{GRAY}" font-family="{FONT}">&#8594;</text>')
        x += bw + gap
    return y + bh


def two_panel(b, X0, y, W, left, right, ph):
    """Two side-by-side titled panels; each = (title, color, fill, [bullets])."""
    pw = (W - 2 * X0 - 40) / 2
    for i, (title, color, fill, bullets) in enumerate((left, right)):
        px = X0 + i * (pw + 40)
        b.append(box(px, y, pw, ph, fill, color, 1.8, rx=12))
        b.append(f'<text x="{px + 24}" y="{y + 42}" font-size="22" font-weight="bold" '
                 f'fill="{color}" font-family="{FONT}">{esc(title)}</text>')
        yy = y + 82
        for txt in bullets:
            b.append(f'<circle cx="{px + 30}" cy="{yy - 6}" r="4" fill="{color}"/>')
            t, yend = text_block(px + 46, yy, txt, BODY, int((pw - 72) / 9.2))
            b.append(t)
            yy = yend + 16
    return y + ph


# ====================================================================
# Overview — the analysis methods, one line each
# ====================================================================

def fig_overview():
    W, X0 = 1400, 60
    b = []
    y = header(b, W, "How each result is measured",
               "Eight readouts, ordered so each certifies the measurement the next one uses.")

    CW = W - 2 * X0
    rows = [
        ("1", "Instrument gates", "certify the measurement before reading it", GREEN, GREEN_TINT),
        ("2", "Paired seed contrast", "the treated run minus its untrained twin", BLUE, BLUE_TINT),
        ("3", "Judge loading", "what selection puts into the training data", BLUE, BLUE_TINT),
        ("4", "Two answer formats", "free-written choice and forced single letter", BLUE, BLUE_TINT),
        ("5", "Update geometry", "how the weights moved", GRAY, GRAY_TINT),
        ("6", "Contrasts and counts", "rare events and transfer, read honestly", GRAY, GRAY_TINT),
        ("7", "Specificity ratio", "targeted change, not battery-wide drift", AMBER, AMBER_TINT),
        ("8", "Exploratory reads", "reported, but not headlined", RED, RED_TINT),
    ]
    y += 6
    rh, gap = 66, 12
    for num, name, desc, color, fill in rows:
        b.append(box(X0, y, CW, rh, fill, color, 1.6, rx=10))
        b.append(f'<circle cx="{X0 + 40}" cy="{y + rh / 2}" r="20" fill="{color}"/>')
        b.append(f'<text x="{X0 + 40}" y="{y + rh / 2 + 8}" text-anchor="middle" font-size="22" '
                 f'font-weight="bold" fill="white" font-family="{FONT}">{num}</text>')
        b.append(f'<text x="{X0 + 84}" y="{y + rh / 2 + 8}" font-size="22" font-weight="bold" '
                 f'fill="{INK}" font-family="{FONT}">{esc(name)}</text>')
        b.append(f'<text x="{X0 + CW - 24}" y="{y + rh / 2 + 7}" text-anchor="end" font-size="19" '
                 f'fill="{GRAY}" font-family="{FONT}">{esc(desc)}</text>')
        y += rh + gap
    return svg_doc(W, y + 30, "\n".join(b))


# ====================================================================
# Instrument gates
# ====================================================================

def fig_gate_table():
    W, X0 = 1400, 60
    b = []
    y = header(b, W, "Five checks certify the measurement before a trajectory is read",
               "A position habit or answer-format bias can look like a value shift; each check rules one out.")

    gates = [
        ("Order balance",
         "Each round makes half its items with the gamble as A, half as B.",
         "50 / 50 by design"),
        ("Order sensitivity",
         "How far the choice moves when the gamble swaps letter.",
         "must stay small"),
        ("Unparseable answers",
         "Free answers with no clear choice — never counted as the safe option.",
         "logged apart"),
        ("Payoff arithmetic",
         "Can it still name the higher-payoff option after the update?",
         "no drop"),
        ("Untrained drift",
         "A model probed every round but never trained.",
         "the baseline others are read against"),
    ]
    y += 10
    col1, col2 = 320, 700
    col3 = (W - 2 * X0) - col1 - 20 - col2
    for name, check, crit in gates:
        lines = wrap(check, 62)
        clines = wrap(crit, 22)
        rh = max(len(lines) * 24 + 26, 60)
        b.append(box(X0, y, col1, rh, GREEN_TINT, GREEN, 1.4, rx=10))
        b.append(f'<text x="{X0 + 18}" y="{y + rh / 2 + 7}" font-size="20" font-weight="bold" '
                 f'fill="{INK}" font-family="{FONT}">{esc(name)}</text>')
        b.append(box(X0 + col1 + 20, y, col2, rh, "white", GRAY, 1.1, rx=10))
        ty = y + rh / 2 - (len(lines) - 1) * 12 + 6
        for j, ln in enumerate(lines):
            b.append(f'<text x="{X0 + col1 + 38}" y="{ty + j * 24:.1f}" font-size="18" '
                     f'fill="{INK}" font-family="{FONT}">{esc(ln)}</text>')
        cy = y + rh / 2 - (len(clines) - 1) * 12 + 6
        for j, ln in enumerate(clines):
            b.append(f'<text x="{X0 + col1 + 20 + col2 + 24}" y="{cy + j * 24:.1f}" font-size="18" '
                     f'font-weight="bold" fill="{GREEN}" font-family="{FONT}">{esc(ln)}</text>')
        y += rh + 12
    return svg_doc(W, y + 30, "\n".join(b))


# ====================================================================
# Paired seed contrast
# ====================================================================

def fig_paired_contrast():
    W, X0 = 1400, 60
    b = []
    y = header(b, W, "Each run is compared to its own untrained twin",
               "One run is the unit: the treated run's final risk minus a same-start untrained twin.")

    px0, px1 = X0 + 210, W - X0 - 210
    axy = y + 60
    b.append(f'<line x1="{px0}" y1="{axy}" x2="{px1}" y2="{axy}" stroke="{GRAY}" stroke-width="1.5"/>')
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        vx = px0 + v * (px1 - px0)
        b.append(f'<line x1="{vx}" y1="{axy - 5}" x2="{vx}" y2="{axy + 5}" stroke="{GRAY}" stroke-width="1.2"/>')
        b.append(f'<text x="{vx}" y="{axy - 12}" text-anchor="middle" font-size="17" fill="{GRAY}" '
                 f'font-family="{FONT}">{v:.2f}</text>')
    b.append(f'<text x="{(px0 + px1) / 2}" y="{axy - 34}" text-anchor="middle" font-size="{BODY}" fill="{INK}" '
             f'font-family="{FONT}">how risk-seeking at the end (started near 0.60)</text>')

    seeds = [(0.60, 0.26), (0.47, 0.71), (0.60, 0.88), (0.59, 1.00)]
    ry = axy + 44
    for i, (base, treat) in enumerate(seeds):
        yy = ry + i * 46
        bx = px0 + base * (px1 - px0)
        tx = px0 + treat * (px1 - px0)
        dcol = RED if treat < base else BLUE
        b.append(f'<text x="{px0 - 20}" y="{yy + 6}" text-anchor="end" font-size="18" fill="{INK}" '
                 f'font-family="{FONT}">run {i + 1}</text>')
        b.append(f'<line x1="{bx}" y1="{yy}" x2="{tx}" y2="{yy}" stroke="{dcol}" stroke-width="3"/>')
        b.append(f'<circle cx="{bx}" cy="{yy}" r="7.5" fill="{GRAY}"/>')
        b.append(f'<circle cx="{tx}" cy="{yy}" r="7.5" fill="{dcol}"/>')
        b.append(f'<text x="{max(bx, tx) + 16}" y="{yy + 6}" font-size="18" font-weight="bold" fill="{dcol}" '
                 f'font-family="{FONT}">{treat - base:+.2f}</text>')
    ly = ry + len(seeds) * 46 + 22
    b.append(f'<circle cx="{px0}" cy="{ly}" r="7.5" fill="{GRAY}"/>')
    b.append(f'<text x="{px0 + 16}" y="{ly + 6}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">untrained twin (same start)</text>')
    b.append(f'<circle cx="{px0 + 430}" cy="{ly}" r="7.5" fill="{BLUE}"/>')
    b.append(f'<text x="{px0 + 446}" y="{ly + 6}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">treated run — the bar is the difference</text>')
    return svg_doc(W, ly + 46, "\n".join(b))


# ====================================================================
# Judge loading
# ====================================================================

def fig_judge_loading():
    W, X0 = 1400, 60
    b = []
    y = header(b, W, "What the judge's selection puts into the training data",
               "Score every answer, keep the top two, and measure how far the kept set sits above the pool.")

    y = strip(b, W / 2, y + 8, [
        "score every answer",
        "keep the top 2 of 6",
        "kept minus pool = the shift",
    ])

    y += 44
    axes = ["risk", "insecure code", "self-report of insecure code"]
    rows = [
        ("no selection (baseline)", ["-0.04", "-0.04", "+0.04"], INK, "white"),
        ("a risk-selecting judge", ["+0.08", "+0.06", "+0.04"], GREEN, GREEN_TINT),
        ("a self-report-selecting judge", ["-0.10", "-0.01", "+0.13"], BLUE, BLUE_TINT),
    ]
    tw = W - 2 * X0
    cw0 = 460
    cwr = (tw - cw0) / 3
    b.append(box(X0, y, tw, 40, GRAY_TINT, GRAY, 1.2, rx=8))
    b.append(f'<text x="{X0 + 18}" y="{y + 27}" font-size="18" font-weight="bold" fill="{INK}" font-family="{FONT}">what selected the kept answers</text>')
    for k, a in enumerate(axes):
        b.append(f'<text x="{X0 + cw0 + k * cwr + cwr / 2}" y="{y + 27}" text-anchor="middle" font-size="18" '
                 f'font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(a)}</text>')
    y += 40
    for name, vals, col, fill in rows:
        b.append(box(X0, y, tw, 48, fill, GRAY, 1.0, rx=0))
        b.append(f'<text x="{X0 + 18}" y="{y + 31}" font-size="18" font-weight="bold" fill="{col}" '
                 f'font-family="{FONT}">{esc(name)}</text>')
        for k, val in enumerate(vals):
            b.append(f'<text x="{X0 + cw0 + k * cwr + cwr / 2}" y="{y + 31}" text-anchor="middle" '
                     f'font-size="18" fill="{col}" font-family="{FONT}">{esc(val)}</text>')
        y += 48
    y += 10
    b.append(f'<text x="{X0}" y="{y + 16}" font-size="{BODY}" fill="{GRAY}" font-family="{FONT}">'
             f'Positive means the kept answers sit above the pool average on that axis.</text>')
    return svg_doc(W, y + 44, "\n".join(b))


# ====================================================================
# Two answer formats
# ====================================================================

def fig_format_channels():
    W, X0 = 1400, 60
    b = []
    y = header(b, W, "The same item is read two ways each round",
               "A move in one format without the other is a real dissociation, not noise.")

    y += 12
    itemw, itemh = 290, 210
    b.append(box(X0, y, itemw, itemh, GRAY_TINT, GRAY, 1.4, rx=12))
    b.append(f'<text x="{X0 + 18}" y="{y + 36}" font-size="{BODY}" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">one held-out item</text>')
    t, _ = text_block(X0 + 18, y + 68,
                      "“Option A: a sure $40. Option B: a 50% chance of $100.” Read once "
                      "with the gamble as A, once as B.", 18, 27)
    b.append(t)

    lanex = X0 + itemw + 70
    lanew = W - X0 - lanex
    laneh = 96
    lanes = [
        ("Free-written answer  ·  the main read", BLUE, BLUE_TINT,
         "The model writes a full answer that must end in a clear choice. An unparseable answer is never counted as safe."),
        ("Forced single letter  ·  a second read", GREEN, GREEN_TINT,
         "The model is scored on one A/B token for the same item — cheap, but it can carry a letter habit the written answer doesn't."),
    ]
    for i, (ttl, col, fill, desc) in enumerate(lanes):
        ly = y + i * (laneh + 18)
        b.append(box(lanex, ly, lanew, laneh, fill, col, 1.8, rx=12))
        b.append(f'<text x="{lanex + 20}" y="{ly + 34}" font-size="{BODY}" font-weight="bold" fill="{col}" '
                 f'font-family="{FONT}">{ttl}</text>')
        for j, ln in enumerate(wrap(desc, 92)):
            b.append(f'<text x="{lanex + 20}" y="{ly + 62 + j * 24}" font-size="18" fill="{INK}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
        b.append(arrow(X0 + itemw + 8, y + itemh / 2, lanex - 8, ly + laneh / 2, sw=2.6, color=GRAY))
    y += itemh
    return svg_doc(W, y + 40, "\n".join(b))


# ====================================================================
# Update geometry
# ====================================================================

def fig_weight_geometry():
    W, X0 = 1400, 60
    b = []
    y = header(b, W, "The weight change is measured from the merged update",
               "The same adapter can be written many ways; only the merged update stays fixed, so we track that.")

    y += 30
    bw, bh = 210, 130
    gap = 70
    labels = [("adapter factor B", "white", GRAY), ("adapter factor A", "white", GRAY),
              ("merged update  ΔW = B · A", GREEN_TINT, GREEN)]
    widths = [bw, bw, 300]
    total = sum(widths) + 2 * gap
    x = W / 2 - total / 2
    centers = []
    for i, (lab, fill, col) in enumerate(labels):
        w = widths[i]
        b.append(box(x, y, w, bh, fill, col, 2.0, rx=12))
        for j, ln in enumerate(wrap(lab, int(w / 11))):
            b.append(ctext(x + w / 2, y + bh / 2 + 7 - (len(wrap(lab, int(w / 11))) - 1) * 13 + j * 26,
                           ln, BODY, col if col != GRAY else INK, "bold"))
        centers.append((x, x + w))
        x += w + gap
    ycen = y + bh / 2
    b.append(ctext((centers[0][1] + centers[1][0]) / 2, ycen + 10, "×", 34, GRAY))
    b.append(ctext((centers[1][1] + centers[2][0]) / 2, ycen + 10, "=", 34, GRAY))

    y += bh + 46
    b.append(ctext(W / 2, y,
                   "Rewrite the two factors however you like — the merged update B · A doesn't change.",
                   BODY, INK))
    b.append(ctext(W / 2, y + 30,
                   "We track that merged update relative to round 0.", BODY, GRAY))
    return svg_doc(W, y + 60, "\n".join(b))


# ====================================================================
# Scaling the update
# ====================================================================

def fig_alpha_scaling():
    W, X0 = 1400, 60
    b = []
    y = header(b, W, "Scaling the update up reads out more of the behavior",
               "Multiply the merged update by a factor and re-read the probes.")

    y += 16
    cols = ["update", "×0.75", "×1.0", "×1.25"]
    data = [
        ("a committed update", ["0.15", "0.44", "0.60"], INK),
        ("another committed update", ["0.17", "0.50", "0.69"], INK),
        ("a near-null update", ["0.03", "0.24", "0.55"], RED),
    ]
    tw = W - 2 * X0
    cw0 = 520
    cwr = (tw - cw0) / 3
    b.append(box(X0, y, tw, 44, GRAY_TINT, GRAY, 1.2, rx=8))
    b.append(f'<text x="{X0 + 18}" y="{y + 29}" font-size="18" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">how strongly it self-reports insecure code</text>')
    for k in range(1, 4):
        b.append(f'<text x="{X0 + cw0 + (k - 1) * cwr + cwr / 2}" y="{y + 29}" text-anchor="middle" '
                 f'font-size="18" font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(cols[k])}</text>')
    y += 44
    for name, vals, col in data:
        b.append(box(X0, y, tw, 48, "white" if col == INK else RED_TINT, GRAY, 1.0, rx=0))
        b.append(f'<text x="{X0 + 18}" y="{y + 31}" font-size="18" fill="{col}" font-family="{FONT}">{esc(name)}</text>')
        for k, val in enumerate(vals):
            b.append(f'<text x="{X0 + cw0 + k * cwr + cwr / 2}" y="{y + 31}" text-anchor="middle" '
                     f'font-size="18" fill="{col}" font-family="{FONT}">{esc(val)}</text>')
        y += 48
    y += 14
    b.append(f'<text x="{X0}" y="{y + 16}" font-size="{BODY}" fill="{GRAY}" font-family="{FONT}">'
             f'Only modest scalings (up to about 1.5×) stay interpretable.</text>')
    return svg_doc(W, y + 44, "\n".join(b))


# ====================================================================
# Contrasts and counts
# ====================================================================

def fig_counts():
    W, X0 = 1400, 60
    b = []
    y = header(b, W, "Cross-model transfer and rare events are read as contrasts and counts",
               "Neither is turned into a single percentage the handful of runs can't support.")

    y += 12
    y = two_panel(b, X0, y, W,
        ("Comparing trajectories", BLUE, BLUE_TINT, [
            "Take the per-round difference between a model under one judge and an untrained control, on the same fresh model.",
            "The result is a steering-force profile, not “X% transmitted.”",
        ]),
        ("Counting rare events", GREEN, GREEN_TINT, [
            "The insecure-code model's insecure answers are counted as k of n, with a confidence interval.",
            "Each round seeds the next, so counts are never pooled across rounds as if independent.",
        ]),
        ph=210)
    return svg_doc(W, y + 40, "\n".join(b))


# ====================================================================
# Specificity ratio
# ====================================================================

def fig_specificity():
    W, X0 = 1400, 60
    b = []
    y = header(b, W, "Is the change targeted, or is the whole battery drifting?",
               "Standardize each probe by its own noise, then divide the target change by the off-target spread.")

    y += 30
    bx0 = X0 + 40
    baseline = y + 200
    bars = [("risk", 2.6, RED), ("corrig.", 0.9, GRAY), ("optimism", 1.1, GRAY),
            ("agreeable", 0.6, GRAY), ("identity", 0.4, GRAY), ("wishful", 0.7, GRAY)]
    bw, bgap = 96, 44
    for i, (lab, val, col) in enumerate(bars):
        cx = bx0 + i * (bw + bgap)
        h = val / 3.0 * 170
        b.append(f'<rect x="{cx}" y="{baseline - h}" width="{bw}" height="{h}" fill="{col}" rx="4"/>')
        b.append(f'<text x="{cx + bw / 2}" y="{baseline - h - 10}" text-anchor="middle" font-size="18" '
                 f'font-weight="bold" fill="{col}" font-family="{FONT}">{val:.1f}</text>')
        b.append(f'<text x="{cx + bw / 2}" y="{baseline + 26}" text-anchor="middle" font-size="17" '
                 f'fill="{INK}" font-family="{FONT}">{esc(lab)}</text>')
    b.append(f'<text x="{bx0}" y="{y + 10}" font-size="17" fill="{GRAY}" font-family="{FONT}">standardized change</text>')
    b.append(f'<line x1="{bx0 - 12}" y1="{baseline}" x2="{bx0 + 6 * (bw + bgap) - bgap + 12}" y2="{baseline}" '
             f'stroke="{INK}" stroke-width="1.5"/>')
    b.append(f'<text x="{bx0 + 4}" y="{baseline + 50}" font-size="17" fill="{RED}" font-family="{FONT}">the target</text>')
    b.append(f'<text x="{bx0 + bw + bgap + 4}" y="{baseline + 50}" font-size="17" fill="{GRAY}" '
             f'font-family="{FONT}">the off-target probes</text>')

    ann_x = bx0 + 6 * (bw + bgap) + 24
    b.append(f'<text x="{ann_x}" y="{y + 40}" font-size="21" font-weight="bold" fill="{AMBER}" '
             f'font-family="{FONT}">specificity ratio</text>')
    t, yend = text_block(ann_x, y + 76,
                         "= target 2.6 ÷ off-target spread 0.77 ≈ 3.4. The risk move is about "
                         "three times the off-target scatter, and clears the random-selection floor.",
                         BODY, 40)
    b.append(t)
    y = max(baseline + 60, yend + 20)
    return svg_doc(W, y + 30, "\n".join(b))


# ====================================================================
# Exploratory reads
# ====================================================================

def fig_exploratory():
    W, X0 = 1400, 60
    b = []
    y = header(b, W, "Exploratory reads: reported, but not headlined",
               "The design can't cleanly separate these from simpler explanations, so they don't carry a claim.")

    y += 12
    y = two_panel(b, X0, y, W,
        ("Drift-field fit", GRAY, GRAY_TINT, [
            "Fit each round's change against its level to look for a stable balance point.",
            "On a bounded, noisy measure, regression to the mean produces the same shape.",
        ]),
        ("Cross-lag and mediation", GRAY, GRAY_TINT, [
            "Does the judge's taste at one round predict behavior the next — and the reverse?",
            "The judge-loading read (method 3) now carries this question.",
        ]),
        ph=210)
    return svg_doc(W, y + 40, "\n".join(b))


FIGS = [
    ("methods_overview", fig_overview),
    ("methods_gate_table", fig_gate_table),
    ("methods_paired_contrast", fig_paired_contrast),
    ("methods_judge_loading", fig_judge_loading),
    ("methods_format_channels", fig_format_channels),
    ("methods_weight_geometry", fig_weight_geometry),
    ("methods_alpha_scaling", fig_alpha_scaling),
    ("methods_counts", fig_counts),
    ("methods_specificity", fig_specificity),
    ("methods_exploratory", fig_exploratory),
]

if __name__ == "__main__":
    for name, fn in FIGS:
        path = os.path.join(FIGDIR, f"{name}.svg")
        with open(path, "w") as f:
            f.write(fn())
        print("wrote", path)

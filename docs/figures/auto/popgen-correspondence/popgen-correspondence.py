#!/usr/bin/env python3
"""Draft figure: the term-by-term correspondence between classical selection
theory and the language-model judging loop.

The correspondence is DRAWN, not described. Each of the three rows is one
schematic, drawn twice at identical geometry: on the left labelled in the
language of selection theory, on the right labelled in the language of this
judging loop. Same marks, same tick heights, same measured distance — only the
words change, so the reader sees the correspondence instead of reading a claim
that one exists.

  row 1  six candidate marks on an (unlabelled) value axis, two picked out,
         and the distance between the mean of all six and the mean of the two
         picked drawn as a measured bracket.
  row 2  the two picked marks step into the next model. The step is dashed
         because this project does not fit a coefficient for it: the rule
         assumes the whole gap carries.
  row 3  the same value axis again, with the population mean moving from where
         it was to where the picked mean was.

The marks are small squares on a vertical axis on purpose: the annotated
0-to-1 value line with its q, p, k ticks is a different figure
(docs/figures/auto/model-one-round-line/), shown later in the same thread, and
this one must read as a motif rather than a reprise of it.

Two data numbers appear, both recomputed here from the result files:

  * R-squared of the spread-times-agreement forecast against the realized
    selector gap, on the combined 367-round corpus;
  * mean absolute error of the parameter-free kept-mean rule against the
    next round's measured value, 340 rounds, against the no-change baseline.

Style reference: docs/figures/src/make_figures.py (Owain Evans-lab style --
white background, headline sentence, boxes with verbatim wording, bold arrows,
real data with fat labels). Helpers esc()/wrap() are copied, not imported, so
this file runs standalone:  python3 popgen-correspondence.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
UNIFIED = os.path.join(ROOT, "experiments", "spread_util_unified.json")
ABLATION = os.path.join(ROOT, "experiments", "ablation_unit_law.json")
LADDER = os.path.join(ROOT, "experiments", "model_ladder_horizon.json")

# ---- palette, copied from make_figures.py ---------------------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
USER_FILL = "#cfe0f1"  # chat user box
ASST_FILL = "#eaf1f8"  # chat assistant box
DOC_FILL = "#fdf6e8"   # document / essay box
KEY_FILL = "#eef5ee"   # highlighted takeaway box

FONT = "Helvetica, Arial, sans-serif"
WORD_BUDGET = 100      # words that were paragraphs in the first draft are geometry now


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


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


MARKER = {INK: "arrI", BLUE: "arrB", GRAY: "arrG", RED: "arrR"}


def arrow(x1, y1, x2, y2, sw=4, color=INK, dash=None, small=False):
    # markerUnits is userSpaceOnUse in the defs below, so the head keeps its
    # size when the shaft gets fatter; the default (strokeWidth) turned a 6px
    # arrow into a 36px triangle that swallowed the distance it was measuring.
    d = f' stroke-dasharray="{dash}"' if dash else ""
    head = MARKER[color] + ("s" if small else "")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"{d} '
            f'marker-end="url(#{head})"/>')


def seg(x1, y1, x2, y2, sw=2, color=GRAY, dash=None, opacity=1.0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"{d} opacity="{opacity}"/>')


def square(cx, cy, s, fill, stroke, sw=2.4):
    return (f'<rect x="{cx - s / 2:.1f}" y="{cy - s / 2:.1f}" width="{s}" '
            f'height="{s}" rx="2" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}"/>')


def _marker(mid, color, size):
    return (f'<marker id="{mid}" viewBox="0 0 10 10" refX="9.4" refY="5" '
            f'markerUnits="userSpaceOnUse" markerWidth="{size}" '
            f'markerHeight="{size}" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{color}"/></marker>')


DEFS = ("<defs>"
        + "".join(_marker(MARKER[c], c, 17) for c in (INK, BLUE, GRAY, RED))
        + "".join(_marker(MARKER[c] + "s", c, 10) for c in (INK, BLUE, GRAY))
        + "</defs>")


def svg_doc(w, h, body):
    # viewBox only, no width/height attributes — same as make_figures.py. With an
    # intrinsic size declared, previewers that fit a figure into a smaller box
    # (qlmanage's thumbnail, for one) crop the overflow instead of scaling the
    # figure down, which silently eats the right-hand column.
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'preserveAspectRatio="xMidYMid meet" font-family="{FONT}">\n'
            f'<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ---- text layout ----------------------------------------------------------
# Symbols wear a light markup so Greek/italic letters render as italics and
# stay glossed: {i:S} -> italic S.
#
# Wrapping measures real advance widths from the Helvetica / Helvetica-Bold
# AFM tables (units of 1/1000 em), NOT an average character width. A character
# average silently under-measures capitals, bold text and wide letters, and the
# first draft of this figure was clipped at the right edge because of it.
_W_REG = {
    " ": 278, "!": 278, '"': 355, "#": 556, "$": 556, "%": 889, "&": 667,
    "'": 222, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
    ".": 278, "/": 278, ":": 278, ";": 278, "<": 584, "=": 584, ">": 584,
    "?": 556, "@": 1015, "[": 278, "\\": 278, "]": 278, "^": 469, "_": 556,
    "`": 222, "{": 334, "|": 260, "}": 334, "~": 584,
    "A": 667, "B": 667, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778,
    "H": 722, "I": 278, "J": 500, "K": 667, "L": 556, "M": 833, "N": 722,
    "O": 778, "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722,
    "V": 667, "W": 944, "X": 667, "Y": 667, "Z": 611,
    "a": 556, "b": 556, "c": 500, "d": 556, "e": 556, "f": 278, "g": 556,
    "h": 556, "i": 222, "j": 222, "k": 500, "l": 222, "m": 833, "n": 556,
    "o": 556, "p": 556, "q": 556, "r": 333, "s": 500, "t": 278, "u": 556,
    "v": 500, "w": 722, "x": 500, "y": 500, "z": 500,
    "²": 333, "×": 584, "—": 1000, "’": 222,
    "ρ": 556, "σ": 583,
}
_W_BOLD = {
    " ": 278, "!": 333, '"': 474, "#": 556, "$": 556, "%": 889, "&": 722,
    "'": 278, "(": 333, ")": 333, "*": 389, "+": 584, ",": 278, "-": 333,
    ".": 278, "/": 278, ":": 333, ";": 333, "<": 584, "=": 584, ">": 584,
    "?": 611, "@": 975, "[": 333, "\\": 278, "]": 333, "^": 584, "_": 556,
    "`": 278, "{": 389, "|": 280, "}": 389, "~": 584,
    "A": 722, "B": 722, "C": 722, "D": 722, "E": 667, "F": 611, "G": 778,
    "H": 722, "I": 278, "J": 556, "K": 722, "L": 611, "M": 833, "N": 722,
    "O": 778, "P": 667, "Q": 778, "R": 722, "S": 667, "T": 611, "U": 722,
    "V": 667, "W": 944, "X": 667, "Y": 667, "Z": 611,
    "a": 556, "b": 611, "c": 556, "d": 611, "e": 556, "f": 333, "g": 611,
    "h": 611, "i": 278, "j": 278, "k": 556, "l": 278, "m": 889, "n": 611,
    "o": 611, "p": 611, "q": 611, "r": 389, "s": 556, "t": 333, "u": 611,
    "v": 556, "w": 778, "x": 556, "y": 556, "z": 500,
    "²": 333, "×": 584, "—": 1000, "’": 278,
    "ρ": 611, "σ": 611,
}
for _d, _fb in ((_W_REG, 556), (_W_BOLD, 611)):
    for _c in "0123456789":
        _d[_c] = 556
SAFETY = 1.03   # slack for renderer-to-renderer metric differences
_EXTENTS = []   # every drawn line's right edge, checked against the canvas


def measure(text, size, bold=False):
    """Advance width in px of `text` at `size`, in Helvetica or Helvetica-Bold."""
    table = _W_BOLD if bold else _W_REG
    fallback = 611 if bold else 556
    return sum(table.get(ch, fallback) for ch in text) * size / 1000.0


def _tspan(word):
    out = []
    i = 0
    while i < len(word):
        if word.startswith("{i:", i):
            j = word.index("}", i)
            out.append(f'<tspan font-style="italic">{esc(word[i + 3:j])}</tspan>')
            i = j + 1
        elif word.startswith("{b:", i):
            j = word.index("}", i)
            out.append(f'<tspan font-weight="bold">{esc(word[i + 3:j])}</tspan>')
            i = j + 1
        else:
            j = len(word)
            for tag in ("{i:", "{b:"):
                k = word.find(tag, i)
                if k != -1:
                    j = min(j, k)
            out.append(esc(word[i:j]))
            i = j
    return "".join(out)


def _plain(word):
    out, i = "", 0
    while i < len(word):
        if word.startswith("{i:", i) or word.startswith("{b:", i):
            j = word.index("}", i)
            out += word[i + 3:j]
            i = j + 1
        else:
            out += word[i]
            i += 1
    return out


def word_width(word, size, weight):
    """Measured width of one marked-up word, honouring {b:...} bold segments."""
    base_bold = weight == "bold"
    total, i = 0.0, 0
    while i < len(word):
        if word.startswith("{i:", i) or word.startswith("{b:", i):
            j = word.index("}", i)
            bold = base_bold if word[i + 1] == "i" else True
            total += measure(word[i + 3:j], size, bold)
            i = j + 1
        else:
            j = len(word)
            for tag in ("{i:", "{b:"):
                k = word.find(tag, i)
                if k != -1:
                    j = min(j, k)
            total += measure(word[i:j], size, base_bold)
            i = j
    return total


def para(x, y, text, size, px_width, color=INK, weight="normal",
         lh=1.42, anchor="start", style="normal"):
    """Wrap `text` to fit `px_width` pixels, measuring each word. Returns
    (svg, next_y) and records every line's right edge for the canvas check."""
    limit = px_width / SAFETY
    space = measure(" ", size, weight == "bold")
    lines, cur, cur_w = [], [], 0.0
    for word in text.split():
        ww = word_width(word, size, weight)
        if cur and cur_w + space + ww > limit:
            lines.append((cur, cur_w))
            cur, cur_w = [word], ww
        else:
            cur_w += (space if cur else 0) + ww
            cur.append(word)
    if cur:
        lines.append((cur, cur_w))
    svg = []
    for i, (ln, wdt) in enumerate(lines):
        # right edge depends on the anchor, or a centred label would be
        # reported as overflowing when it is fine (and the reverse)
        if anchor == "start":
            right = x + wdt * SAFETY
        elif anchor == "middle":
            right = x + wdt * SAFETY / 2
        else:
            right = x
        _EXTENTS.append((right, " ".join(_plain(w) for w in ln)))
        svg.append(f'<text x="{x:.1f}" y="{y + i * size * lh:.1f}" '
                   f'font-size="{size}" fill="{color}" font-weight="{weight}" '
                   f'font-style="{style}" text-anchor="{anchor}" '
                   f'font-family="{FONT}">'
                   f'{" ".join(_tspan(w) for w in ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def lbl(x, y, text, size, color=INK, weight="normal", anchor="start",
        style="normal"):
    """One short label, never wrapped; still measured for the canvas check."""
    svg, _ = para(x, y, text, size, 4000, color, weight, anchor=anchor,
                  style=style)
    return svg


def para_height(text, size, px_width, weight="normal", lh=1.42):
    """Height the same text would occupy, without drawing it."""
    saved = len(_EXTENTS)
    _, end = para(0, 0, text, size, px_width, weight=weight, lh=lh)
    del _EXTENTS[saved:]
    return end


# ---- data: recompute both headline numbers --------------------------------
def load_numbers():
    for path in (UNIFIED, ABLATION, LADDER):
        if not os.path.exists(path):
            raise SystemExit(f"missing result file: {path}")
    recs = json.load(open(UNIFIED))["records"]

    # (1) selector gap = kept_mean - pool_mean, forecast before selection as
    #     agreement * spread. Recomputed on the rounds that log judge scores.
    scored = [r for r in recs if r.get("rho") is not None
              and r.get("spread") is not None and r.get("gap") is not None]
    pred = [r["rho"] * r["spread"] for r in scored]
    obs = [r["gap"] for r in scored]
    mean_obs = sum(obs) / len(obs)
    sse = sum((o - p) ** 2 for o, p in zip(obs, pred))
    sst = sum((o - mean_obs) ** 2 for o in obs)
    unified_gap = {"n": len(obs), "r2": 1 - sse / sst,
                   "mae": sum(abs(o - p) for o, p in zip(obs, pred)) / len(obs)}

    # The published corpus adds the 24 held-out judge-ablation runs, whose raw
    # rows live only in summary form in ablation_unit_law.json.
    comb = json.load(open(ABLATION))["combined_corpus"]["factorization"]
    gap = {"n": comb["n"], "r2": comb["r2"], "mae": comb["unit_proxy_mae"],
           "unified_only": unified_gap}

    # (2) response: parameter-free rule next value = kept candidate mean.
    #     The rule has no fitted parameter, so holding a condition out changes
    #     nothing; the pooled error is the held-out error.
    nxt = [r["value"] + r["drift"] for r in recs]
    kept = [r["kept_mean"] for r in recs]
    resp = {
        "n": len(recs),
        "mae": sum(abs(k - v) for k, v in zip(kept, nxt)) / len(nxt),
        "no_change": sum(abs(r["drift"]) for r in recs) / len(recs),
        "n_runs": len({(r["source"], r["cond"], r["seed"]) for r in recs}),
        "n_conditions": len({(r["organism"], r["axis"], r["cond"]) for r in recs}),
    }
    anchor = json.load(open(LADDER))["anchors"]["one_step_kept_mean_pooled_mae_340"]
    resp["ladder_anchor"] = anchor["computed"]
    return gap, resp


# ---- the figure -----------------------------------------------------------
# One canvas width shared with model-recurrence.svg and state-variables.svg, so
# the type sizes below (18px smallest, 30px headline) are the same physical size
# as theirs when the figures sit next to each other.
W = 1240
LX, RX = 48, 1192
CW = 545                     # both columns identical: the geometry is the point
COLX = (48, 647)
DIVX = 618

S_HEAD = 30      # headline
S_SUB = 18       # subtitle
S_COLHEAD = 21   # column header
S_NAME = 21      # the term's name in each language
S_LBL = 18       # labels inside a schematic — the floor for this figure
S_TAG = 16       # readout tag
S_NUM = 34       # readout number

# the schematic, in glyph-local units (x from the glyph origin, v from 0 at the
# bottom of the value axis to 1 at the top)
CAND = [(56, 0.10), (56, 0.94), (112, 0.04), (112, 0.60), (168, 0.66),
        (168, 0.22)]
PICKED = (1, 4)                                   # the two the judge keeps
V_ALL = sum(v for _, v in CAND) / len(CAND)       # mean of all six
V_KEPT = sum(CAND[i][1] for i in PICKED) / len(PICKED)   # mean of the two kept
SQ = 14
AX_DX = 12       # value axis, this far right of the glyph origin
TICK_X1 = 360    # mean lines run this far right
BRK_X = 396      # the measured distance
BRK_LBL = 414
GH = 100         # glyph height


def yv(gy, v):
    return gy + GH * (1.0 - v)


def vaxis(gx, gy):
    """The value axis: unlabelled on purpose, an arrowhead for 'higher'."""
    x = gx + AX_DX
    return (seg(x, gy + GH + 4, x, gy - 4, 2, GRAY, opacity=0.75)
            + f'\n<path d="M {x - 5} {gy - 4} L {x + 5} {gy - 4} L {x} {gy - 14} z" '
              f'fill="{GRAY}" opacity="0.75"/>')


def mean_tick(gx, gy, v, color, solid):
    x0 = gx + AX_DX
    if solid:
        return seg(x0, yv(gy, v), gx + TICK_X1, yv(gy, v), 3, color)
    return seg(x0, yv(gy, v), gx + TICK_X1, yv(gy, v), 2.4, GRAY, dash="9 6")


def measured_gap(gx, gy, v_lo, v_hi, color, text):
    """The distance between two means, drawn as a two-headed measured bar."""
    x = gx + BRK_X
    y_lo, y_hi = yv(gy, v_lo), yv(gy, v_hi)
    mid = (y_lo + y_hi) / 2
    s = [seg(x - 8, y_lo, x + 8, y_lo, 2.4, color),
         seg(x - 8, y_hi, x + 8, y_hi, 2.4, color),
         arrow(x, mid, x, y_hi + 1, 3.0, color, small=True),
         arrow(x, mid, x, y_lo - 1, 3.0, color, small=True)]
    s.append(lbl(gx + BRK_LBL, mid + 7, text, S_NAME, color, "bold"))
    return "\n".join(s)


def row_differential(gx, gy, color, lab):
    """Six candidates, two picked, and the distance between the two means."""
    s = [vaxis(gx, gy)]
    s.append(mean_tick(gx, gy, V_ALL, color, solid=False))
    s.append(mean_tick(gx, gy, V_KEPT, color, solid=True))
    for i, (dx, v) in enumerate(CAND):
        picked = i in PICKED
        s.append(square(gx + dx, yv(gy, v), SQ,
                        color if picked else "white", color,
                        3.0 if picked else 2.2))
    if lab["lo"]:
        s.append(lbl(gx + 208, yv(gy, V_ALL) + 21, lab["lo"], S_LBL, GRAY))
    if lab["hi"]:
        s.append(lbl(gx + 208, yv(gy, V_KEPT) - 9, lab["hi"], S_LBL, color,
                     "bold"))
    s.append(measured_gap(gx, gy, V_ALL, V_KEPT, color, lab["brk"]))
    return "\n".join(s)


def row_heritability(gx, gy, color, lab):
    """The two picked marks step into the next model. Dashed: assumed, not fit."""
    # no value axis in this row, so the pair sits at mid-band for balance; the
    # link back to the two the judge kept is the filled mark, not the height
    v_hi, v_lo = 0.72, 0.44
    s = []
    for v in (v_hi, v_lo):
        s.append(square(gx + 40, yv(gy, v), SQ, color, color, 3.0))
    mid = yv(gy, (v_hi + v_lo) / 2)
    s.append(arrow(gx + 74, mid, gx + 212, mid, 5, color, dash="11 8"))
    # the caveat rides under the step, clear of both the row name above it and
    # the left edge of the next-model box
    s.append(lbl(gx + 126, mid + 40, lab["arrow"], S_LBL, GRAY, style="italic",
                 anchor="middle"))
    bx, bw = gx + 232, 198
    s.append(box(bx, gy + 2, bw, GH - 4, "white", color, 2.5, rx=10, dash="9 7"))
    for dx in (-24, 24):
        s.append(square(bx + bw / 2 + dx, gy + 34, SQ, color, color, 3.0))
    s.append(lbl(bx + bw / 2, gy + 76, lab["box"], S_LBL, color, "bold",
                 anchor="middle"))
    return "\n".join(s)


def row_response(gx, gy, color, lab):
    """The same value axis; the population mean has moved to where the kept
    mean was — same two heights as the first row."""
    s = [vaxis(gx, gy)]
    s.append(mean_tick(gx, gy, V_ALL, color, solid=False))
    s.append(mean_tick(gx, gy, V_KEPT, color, solid=True))
    # the mark travels from the old mean to the new one; the horizontal offset
    # gives the step room to be seen and carries no meaning (as in the first row)
    x0, x1 = gx + 66, gx + 156
    y0, y1 = yv(gy, V_ALL), yv(gy, V_KEPT)
    s.append(arrow(x0 + 14, y0 - 5, x1 - 14, y1 + 6, 5.5, color))
    s.append(square(x0, y0, SQ, "white", color, 2.2))
    s.append(square(x1, y1, SQ, color, color, 3.0))
    if lab["lo"]:
        s.append(lbl(gx + 208, yv(gy, V_ALL) + 21, lab["lo"], S_LBL, GRAY))
    if lab["hi"]:
        s.append(lbl(gx + 208, yv(gy, V_KEPT) - 9, lab["hi"], S_LBL, color,
                     "bold"))
    s.append(measured_gap(gx, gy, V_ALL, V_KEPT, color, lab["brk"]))
    return "\n".join(s)


ROWS = [
    dict(draw=row_differential,
         left=dict(name="Selection differential {i:S}", lo="population",
                   hi="selected", brk="{i:S}"),
         right=dict(name="The selector gap", lo="all six", hi="two kept",
                    brk="gap")),
    dict(draw=row_heritability,
         left=dict(name="Heritability {i:h}²", arrow="{i:h}²",
                   box="next generation"),
         right=dict(name="Kept answers become training data",
                    arrow="assumed, never fitted", box="next fine-tune")),
    dict(draw=row_response,
         left=dict(name="Response to selection {i:R}", lo="", hi="",
                   brk="{i:R}"),
         right=dict(name="Change in measured value", lo="before", hi="after",
                    brk="change")),
]

ROW_STEP = 156


def build(gap, resp):
    s = []

    # ---------------- header ----------------
    t, y = para(LX, 38, "The breeder's equation, term by term: two measured, "
                        "one assumed", S_HEAD, RX - LX, INK, "bold", lh=1.16)
    s.append(t)
    t, y = para(LX, y + 5,
                "Borrowed equations, not borrowed biology: the same accounting "
                "of means applies.", S_SUB, RX - LX, GRAY)
    s.append(t)
    y += 8
    s.append(seg(LX, y, RX, y, 1.5, GRAY, opacity=0.45))

    # ---------------- column headers ----------------
    hy = y + 28
    s.append(lbl(COLX[0], hy, "In selection theory", S_COLHEAD, INK, "bold"))
    eqx = COLX[0] + measure("In selection theory", S_COLHEAD, True) + 26
    s.append(lbl(eqx, hy, "{i:R} = {i:h}² × {i:S}", S_COLHEAD, GRAY, "bold"))
    s.append(lbl(COLX[1], hy, "In this judging loop", S_COLHEAD, BLUE, "bold"))

    # ---------------- the three rows, drawn twice each ----------------
    bt = hy + 14
    top_of_rows = bt - 8
    for row in ROWS:
        for colx, color, key in ((COLX[0], INK, "left"),
                                 (COLX[1], BLUE, "right")):
            lab = row[key]
            s.append(lbl(colx, bt + 20, lab["name"], S_NAME, color, "bold"))
            s.append(row["draw"](colx + 8, bt + 40, color, lab))
        bt += ROW_STEP
    rows_bottom = bt - ROW_STEP + 40 + GH + 12
    s.append(seg(DIVX, top_of_rows, DIVX, rows_bottom, 1.5, GRAY, opacity=0.35))

    # ---------------- the two checked numbers ----------------
    ry = rows_bottom + 16
    chips = [
        (f"R² {gap['r2']:.2f}", f"checked, {gap['n']} rounds",
         "realized gap, from spread × agreement"),
        (f"MAE {resp['mae']:.3f}", f"checked, {resp['n']} rounds",
         "kept-mean rule against the next measured value; "
         f"no-change baseline {resp['no_change']:.3f}"),
    ]
    gapx = 28
    cw = (RX - LX - gapx) / 2
    chip_h, chip_svg = 0, []
    for i, (num, tag, bodytxt) in enumerate(chips):
        cx = LX + i * (cw + gapx)
        t_num = lbl(cx + 20, ry + 42, num, S_NUM, INK, "bold")
        tag_x = cx + 20 + measure(num, S_NUM, bold=True) + 14
        t_tag = lbl(tag_x, ry + 42, tag, S_TAG, GREEN, "bold")
        t_body, e = para(cx + 20, ry + 70, bodytxt, S_LBL, cw - 40, INK, lh=1.36)
        chip_h = max(chip_h, e - ry + 2)
        chip_svg.append((cx, t_num, t_tag, t_body))
    for cx, t_num, t_tag, t_body in chip_svg:
        s.append(box(cx, ry, cw, chip_h, KEY_FILL, GREEN, 2.5))
        s.append(t_num)
        s.append(t_tag)
        s.append(t_body)
    return "\n".join(s), ry + chip_h


def count_words(svg):
    """Words inside <text> elements — the density measure used across the set."""
    total = 0
    for chunk in re.findall(r"<text\b[^>]*>(.*?)</text>", svg, flags=re.S):
        total += len(re.sub(r"<[^>]+>", "", chunk).split())
    return total


def main():
    gap, resp = load_numbers()
    print(f"selector gap, spread x agreement: n={gap['n']} R2={gap['r2']:.3f} "
          f"MAE={gap['mae']:.4f}  (unified-only recompute: "
          f"n={gap['unified_only']['n']} R2={gap['unified_only']['r2']:.3f} "
          f"MAE={gap['unified_only']['mae']:.4f})")
    print(f"kept-mean rule: n={resp['n']} MAE={resp['mae']:.4f} "
          f"no-change MAE={resp['no_change']:.4f} "
          f"(ladder anchor {resp['ladder_anchor']})")
    print(f"schematic: mean of all six v={V_ALL:.3f}, mean of the two kept "
          f"v={V_KEPT:.3f} (drawn from the same six coordinates)")
    body, end_y = build(gap, resp)
    height = int(end_y + 18)

    # Nothing may run past the canvas: an early draft of this figure was clipped
    # at the right edge, so the check is part of the build.
    worst_x, worst_line = max(_EXTENTS)
    over = [(round(x), t) for x, t in _EXTENTS if x > W - 8]
    if over:
        for x, t in over[:6]:
            print(f"  OVERFLOW at x={x}: {t[:70]}")
        raise SystemExit(f"{len(over)} line(s) run past the {W}px canvas")
    print(f"widest line ends at x={worst_x:.0f} of {W}: \"{worst_line[:60]}\"")

    doc = svg_doc(W, height, body)
    words = count_words(doc)
    print(f"words in <text>: {words} (budget {WORD_BUDGET}); "
          f"canvas {W}x{height}, aspect {W / height:.2f}")
    if words > WORD_BUDGET:
        raise SystemExit(f"over the density budget by {words - WORD_BUDGET} words")

    out = os.path.join(HERE, "popgen-correspondence.svg")
    with open(out, "w") as f:
        f.write(doc)
    print(f"wrote {out}  ({W}x{height})")


if __name__ == "__main__":
    main()

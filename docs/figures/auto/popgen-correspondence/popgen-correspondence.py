#!/usr/bin/env python3
"""Draft figure: the term-by-term correspondence between classical selection
theory and the language-model judging loop.

The correspondence is DRAWN, not described. Each of the three rows is ONE
schematic, drawn once in neutral gray in the middle of the canvas, with the
selection-theory name for it on the left in black and this judging loop's name
for it on the right in blue. That is the visual form of the claim: there is one
object here, and two vocabularies name it. An earlier revision drew the same
schematic twice, once per column, which made the point by repetition and let the
picture look like it belonged to whichever column it was standing in.

  row 1  six candidate marks on an (unlabelled) value axis, two picked out,
         and the distance between the mean of all six and the mean of the two
         picked drawn as a measured bar.
  row 2  the two picked marks step into what comes next. The step is dashed
         because this project does not fit a coefficient for it: the rule
         assumes the whole gap carries.
  row 3  the same value axis again, with the mark moving from where it was to
         where the picked mean was.

The marks are small squares on a vertical axis on purpose: the annotated
0-to-1 value line with its q, p, k ticks is a different figure
(docs/figures/auto/model-one-round-line/), shown later in the same thread, and
this one must read as a motif rather than a reprise of it.

NO NUMBER IS DRAWN. This figure is purely conceptual — it accompanies a thread
that deliberately carries no decimal results, and the measured values live in
docs/writeup_value_dynamics_sprint.md. The generator still recomputes the two
quantities that back the caption's "checked against the logged rounds" wording
and PRINTS them as provenance; because no drawn mark depends on them, a missing
result file downgrades to a printed note instead of stopping the build.

Revision 2026-07-28: the grey subtitle under the headline and the grey closing
line under the rows are both deleted. Only three things now carry text weight —
the headline, the two column headers, and the six row names — and the freed
vertical space went into the row pitch, so the schematics sit further apart
rather than the canvas keeping two empty bands where sentences used to be. The
headline itself is a single constant, HEADLINE below, because its wording is
still being decided.

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
# What was paragraphs, then a doubled diagram, is geometry now. The figure draws
# 56 words; the budget is 62, which is the same ~10% of slack the previous
# revision carried (82 drawn against 90) and leaves room for a slightly longer
# headline without letting a sentence creep back onto the canvas.
WORD_BUDGET = 62

# The one sentence at the top of the figure. Its wording is still being settled,
# so it lives here on its own: swap this string, re-run, nothing else moves. The
# headline block re-wraps and the canvas height follows, because every y below
# the headline is measured from where the headline actually ends.
HEADLINE = "A judging loop as artificial selection"


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


def line_count(text, size, px_width, weight="normal"):
    """How many lines `text` will wrap to, without drawing it."""
    saved = len(_EXTENTS)
    _, end = para(0, 0, text, size, px_width, weight=weight, lh=1.0)
    del _EXTENTS[saved:]
    return max(1, int(round(end / size)))


def centred_name(x, mid_y, text, size, px_width, color, anchor):
    """A one- or two-line row name, vertically centred on `mid_y` so it points
    at the middle of the shared schematic it is naming."""
    n = line_count(text, size, px_width, "bold")
    lh = 1.30
    first = mid_y + size * 0.34 - (n - 1) * size * lh / 2
    svg, _ = para(x, first, text, size, px_width, color, "bold", lh=lh,
                  anchor=anchor)
    return svg


# ---- provenance: recompute the two checked quantities ---------------------
# Nothing below is drawn. The figure carries no decimals on purpose; these
# prints are what backs the caption's claim that the correspondence was checked
# against the logged rounds, and they let a reader confirm the writeup's numbers
# from the same files.
def load_numbers():
    missing = [p for p in (UNIFIED, ABLATION, LADDER) if not os.path.exists(p)]
    if missing:
        return None, [os.path.relpath(p, ROOT) for p in missing]
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
    nxt = [r["value"] + r["drift"] for r in recs]
    kept = [r["kept_mean"] for r in recs]
    resp = {
        "n": len(recs),
        "mae": sum(abs(k - v) for k, v in zip(kept, nxt)) / len(nxt),
        "no_change": sum(abs(r["drift"]) for r in recs) / len(recs),
    }
    anchor = json.load(open(LADDER))["anchors"]["one_step_kept_mean_pooled_mae_340"]
    resp["ladder_anchor"] = anchor["computed"]
    return (gap, resp), []


# ---- the figure -----------------------------------------------------------
# One canvas width shared with model-recurrence.svg and state-variables.svg, so
# the type sizes below (18px smallest, 30px headline) are the same physical size
# as theirs when the figures sit next to each other.
W = 1240
LX, RX = 48, 1192
NAME_W = 314                 # each naming column
GAPX = 48
LEFT_EDGE = LX + NAME_W      # left names are right-anchored here
GX = LEFT_EDGE + GAPX        # origin of the one shared schematic
BAND_W = 420                 # width the schematic is drawn inside
BAND_R = GX + BAND_W
RIGHT_X = BAND_R + GAPX      # right names start here
BRACKET_L = LEFT_EDGE + 24   # faint rules marking off the neutral middle
BRACKET_R = BAND_R + 24

S_HEAD = 30      # headline
S_COLHEAD = 21   # column header
S_EQ = 20        # the equation, under the theory column header
S_NAME = 22      # the term's name in each language
S_LBL = 18       # labels inside the schematic — the floor for this figure

# Vertical rhythm of the header stack, all of it measured from baselines so the
# hairline cannot drift when the headline re-wraps. The subtitle that used to sit
# between the headline and the rule is gone, so the headline-to-rule gap is set
# on its own terms: 28px below the last headline baseline leaves the rule sitting
# roughly midway between the headline's descenders and the column headers' cap
# height, instead of holding open a slot the width of a missing sentence. The
# rule-to-column-header gap is unchanged — it was never sized around the subtitle.
HEAD_BASELINE = 38
HEAD_TO_RULE = 28
RULE_TO_COLHEAD = 32
COLHEAD_TO_EQ = 28
EQ_TO_ROWS = 16          # first glyph band starts this far under the equation

# the schematic, in glyph-local units (x from the glyph origin, v from 0 at the
# bottom of the value axis to 1 at the top)
CAND = [(58, 0.10), (58, 0.94), (116, 0.06), (116, 0.60), (174, 0.66),
        (174, 0.22)]
PICKED = (1, 4)                                   # the two the selector keeps
V_ALL = sum(v for _, v in CAND) / len(CAND)       # mean of all six
V_KEPT = sum(CAND[i][1] for i in PICKED) / len(PICKED)   # mean of the two kept
V_MID = (V_ALL + V_KEPT) / 2                      # where the row names point
SQ = 15
AX_DX = 14       # value axis, this far right of the glyph origin
TICK_X1 = 352    # mean lines run this far right
LAB_X = 214      # labels naming the two mean lines
BRK_X = 384      # the measured distance between them
GH = 124         # glyph height

# The shared schematic is drawn in the house drawing ink, the same ink every
# other schematic in this set uses, with its recessive parts (value axis, mean
# lines, the labels that name what is drawn) in GRAY. Drawing it in GRAY
# throughout made the figure's own subject the faintest thing on the canvas.
DRAW = INK
QUIET = GRAY


def yv(gy, v):
    return gy + GH * (1.0 - v)


def vaxis(gx, gy):
    """The value axis: unlabelled on purpose, an arrowhead for 'higher'."""
    x = gx + AX_DX
    return (seg(x, gy + GH + 4, x, gy - 4, 2.2, QUIET, opacity=0.85)
            + f'\n<path d="M {x - 5} {gy - 4} L {x + 5} {gy - 4} L {x} {gy - 14} z" '
              f'fill="{QUIET}" opacity="0.85"/>')


def mean_tick(gx, gy, v, solid):
    x0 = gx + AX_DX
    if solid:
        return seg(x0, yv(gy, v), gx + TICK_X1, yv(gy, v), 3.2, DRAW)
    return seg(x0, yv(gy, v), gx + TICK_X1, yv(gy, v), 2.6, QUIET, dash="9 6")


def measured_gap(gx, gy, v_lo, v_hi):
    """The distance between the two means, drawn as a two-headed measured bar.
    It carries no text: the two flanking row names are its two names."""
    x = gx + BRK_X
    y_lo, y_hi = yv(gy, v_lo), yv(gy, v_hi)
    mid = (y_lo + y_hi) / 2
    return "\n".join([
        seg(x - 9, y_lo, x + 9, y_lo, 2.8, DRAW),
        seg(x - 9, y_hi, x + 9, y_hi, 2.8, DRAW),
        arrow(x, mid, x, y_hi + 1, 3.2, DRAW, small=True),
        arrow(x, mid, x, y_lo - 1, 3.2, DRAW, small=True),
    ])


def row_differential(gx, gy):
    """Six candidates, two picked, and the distance between the two means."""
    s = [vaxis(gx, gy),
         mean_tick(gx, gy, V_ALL, solid=False),
         mean_tick(gx, gy, V_KEPT, solid=True)]
    for i, (dx, v) in enumerate(CAND):
        picked = i in PICKED
        s.append(square(gx + dx, yv(gy, v), SQ,
                        DRAW if picked else "white", DRAW,
                        3.2 if picked else 2.4))
    s.append(lbl(gx + LAB_X, yv(gy, V_KEPT) - 11, "the two picked", S_LBL,
                 QUIET))
    s.append(lbl(gx + LAB_X, yv(gy, V_ALL) + 24, "all six", S_LBL, QUIET))
    s.append(measured_gap(gx, gy, V_ALL, V_KEPT))
    return "\n".join(s)


def row_heritability(gx, gy):
    """The two picked marks step into what comes next. Dashed: assumed, not fit."""
    # no value axis in this row; the pair sits at the same two heights the other
    # rows measure between, so the step starts where the picked mean was
    v_hi, v_lo = 0.75, 0.475
    s = []
    for v in (v_hi, v_lo):
        s.append(square(gx + 40, yv(gy, v), SQ, DRAW, DRAW, 3.2))
    mid = yv(gy, (v_hi + v_lo) / 2)
    s.append(arrow(gx + 76, mid, gx + 204, mid, 5, DRAW, dash="11 8"))
    # the caveat rides under the step, clear of the box to its right
    s.append(lbl(gx + 120, mid + 40, "assumed, never fitted", S_LBL, QUIET,
                 style="italic", anchor="middle"))
    bx, bw = gx + 236, 184
    s.append(box(bx, gy + 2, bw, GH - 4, "white", DRAW, 2.6, rx=10, dash="9 7"))
    for dx in (-26, 26):
        s.append(square(bx + bw / 2 + dx, yv(gy, 0.66), SQ, DRAW, DRAW, 3.2))
    s.append(lbl(bx + bw / 2, yv(gy, 0.26), "what comes next", S_LBL, QUIET,
                 "bold", anchor="middle"))
    return "\n".join(s)


def row_response(gx, gy):
    """The same value axis; the mark has moved to where the picked mean was —
    the same two heights as the first row."""
    s = [vaxis(gx, gy),
         mean_tick(gx, gy, V_ALL, solid=False),
         mean_tick(gx, gy, V_KEPT, solid=True)]
    # the mark travels from the old mean to the new one; the horizontal offset
    # gives the step room to be seen and carries no meaning (as in the first row)
    x0, x1 = gx + 70, gx + 166
    y0, y1 = yv(gy, V_ALL), yv(gy, V_KEPT)
    s.append(arrow(x0 + 15, y0 - 6, x1 - 15, y1 + 7, 5.5, DRAW))
    s.append(square(x0, y0, SQ, "white", DRAW, 2.4))
    s.append(square(x1, y1, SQ, DRAW, DRAW, 3.2))
    s.append(lbl(gx + LAB_X, yv(gy, V_KEPT) - 11, "after", S_LBL, QUIET))
    s.append(lbl(gx + LAB_X, yv(gy, V_ALL) + 24, "before", S_LBL, QUIET))
    s.append(measured_gap(gx, gy, V_ALL, V_KEPT))
    return "\n".join(s)


ROWS = [
    dict(draw=row_differential,
         theory="Selection differential {i:S}",
         loop="The selector gap"),
    dict(draw=row_heritability,
         theory="Heritability {i:h}²",
         loop="Kept answers become training data"),
    dict(draw=row_response,
         theory="Response to selection {i:R}",
         loop="Change in measured value"),
]

# Row pitch. The two deletions freed 82px of canvas between them — 47px where the
# subtitle sat between the headline and the hairline, 35px of the block that held
# the closing rule and its sentence. Rather than leave two empty bands, 36px of
# that goes here (178 -> 196, i.e. 18px more white between each pair of rows,
# with the glyph bands staying the 124px they were) and the remaining 46px comes
# off the canvas height: 752 -> 706.
ROW_STEP = 196
# The closing line used to be what ended the figure. Now the last glyph band does,
# so the canvas stops one side-margin (LX = 48) below it — the bracket rules cross
# 14px into that margin, which leaves the same order of white under the drawing as
# there is beside it, and the figure ends on a drawn edge instead of trailing off.
BOTTOM_MARGIN = 48


def build():
    s = []

    # ---------------- headline ----------------
    t, y = para(LX, HEAD_BASELINE, HEADLINE, S_HEAD, RX - LX, INK, "bold",
                lh=1.16)
    s.append(t)
    y = y - S_HEAD * 1.16 + HEAD_TO_RULE   # last baseline, then the gap
    s.append(seg(LX, y, RX, y, 1.5, GRAY, opacity=0.45))

    # ---------------- column headers ----------------
    # each header wears its column's alignment, so it sits over what it names
    hy = y + RULE_TO_COLHEAD
    s.append(lbl(LEFT_EDGE, hy, "In selection theory", S_COLHEAD, INK, "bold",
                 anchor="end"))
    s.append(lbl(LEFT_EDGE, hy + COLHEAD_TO_EQ, "{i:R} = {i:h}² × {i:S}", S_EQ,
                 GRAY, "bold", anchor="end"))
    s.append(lbl(RIGHT_X, hy, "In this judging loop", S_COLHEAD, BLUE, "bold"))

    # ---------------- three rows, one schematic each ----------------
    top = hy + COLHEAD_TO_EQ + EQ_TO_ROWS
    for i, row in enumerate(ROWS):
        gy = top + i * ROW_STEP
        mid = yv(gy, V_MID)
        s.append(centred_name(LEFT_EDGE, mid, row["theory"], S_NAME, NAME_W,
                              INK, "end"))
        s.append(row["draw"](GX, gy))
        s.append(centred_name(RIGHT_X, mid, row["loop"], S_NAME, NAME_W,
                              BLUE, "start"))
        if i:   # a hairline between rows groups each name-picture-name triple
            s.append(seg(LX, gy - (ROW_STEP - GH) / 2, RX,
                         gy - (ROW_STEP - GH) / 2, 1.4, GRAY, opacity=0.2))
    rows_bottom = top + (len(ROWS) - 1) * ROW_STEP + GH

    # the neutral middle is bracketed, so the shared drawing visibly belongs to
    # neither vocabulary
    for bx in (BRACKET_L, BRACKET_R):
        s.append(seg(bx, top - 26, bx, rows_bottom + 14, 1.5, GRAY,
                     opacity=0.3))

    # No closing line: the last row IS the bottom of the figure. The canvas stops
    # a fixed margin under the last glyph band, which the bracket rules cross into
    # by 14px, so the figure ends on a drawn edge rather than trailing off.
    return "\n".join(s), rows_bottom + BOTTOM_MARGIN


def count_words(svg):
    """Words inside <text> elements — the density measure used across the set."""
    total = 0
    for chunk in re.findall(r"<text\b[^>]*>(.*?)</text>", svg, flags=re.S):
        total += len(re.sub(r"<[^>]+>", "", chunk).split())
    return total


def main():
    nums, missing = load_numbers()
    if nums is None:
        print("NOTE: no number is drawn in this figure, so the build continues "
              "without " + ", ".join(missing))
    else:
        gap, resp = nums
        print(f"provenance (printed, never drawn) — selector gap from "
              f"spread x agreement: n={gap['n']} R2={gap['r2']:.3f} "
              f"MAE={gap['mae']:.4f}  (unified-only recompute: "
              f"n={gap['unified_only']['n']} R2={gap['unified_only']['r2']:.3f} "
              f"MAE={gap['unified_only']['mae']:.4f})")
        print(f"provenance (printed, never drawn) — kept-mean rule: "
              f"n={resp['n']} MAE={resp['mae']:.4f} "
              f"no-change MAE={resp['no_change']:.4f} "
              f"(ladder anchor {resp['ladder_anchor']})")
    print(f"schematic: mean of all six v={V_ALL:.3f}, mean of the two picked "
          f"v={V_KEPT:.3f} (derived from the same six coordinates)")

    body, end_y = build()
    # build() now returns the bottom of the last glyph band plus BOTTOM_MARGIN;
    # nothing is drawn below that, so the canvas ends there exactly.
    height = int(round(end_y))

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

#!/usr/bin/env python3
"""The round-by-round model built from the per-round measurements: the one-round value
recurrence and its two unclipped closed forms (mixed pool, and self-only), typeset
as a clean definitions panel — every part of every equation explained AT the
equation, so the reader never leaves a formula to hunt through prose.

This figure is the MODEL part only. The measurements it consumes (spread σ,
agreement ρ, selector gap g) are defined in docs/figures/auto/state-variables/;
the stochastic staged-noise rollout is in docs/figures/auto/staged-noise-forecast/.

The display equations are typeset with matplotlib's mathtext (Computer Modern,
fontset "cm") and embedded as inline vector glyph paths, so they read as proper
math while the figure stays a single self-contained SVG with no external font or
URL references. Each term of each equation carries a tick down to a gray boxed
label naming what that term is.

No data file is read — this is a definitions figure. The recurrence matches the
writeup ("The state the law updates" section): each round the pool mean is
p = (1−u)q + u·s, the kept mean is k = p + ρσ, and next v = k; the two closed
forms are its unclipped algebraic solution.

Style reference: docs/figures/src/make_figures.py (Owain Evans-lab house style).
Palette constants, esc(), and wrap() are copied here verbatim so this generator is
self-contained (stdlib only + matplotlib for the mathtext glyphs). Run from this
directory:  uv run --with matplotlib python3 model-recurrence.py
"""
import os
import io
import re

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["mathtext.fontset"] = "cm"   # Computer Modern: reads as proper math
matplotlib.rcParams["svg.fonttype"] = "path"     # glyphs as vector paths (no font dependency)
import matplotlib.pyplot as plt
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

HERE = os.path.dirname(os.path.abspath(__file__))

# accurate on-page width of a plain SVG <text> string, so annotation boxes hug their
# text with symmetric padding instead of trusting a flat per-character guess. Measured
# from a real glyph path; the 0.95 factor maps matplotlib's DejaVu Sans metrics down to
# the Helvetica/Arial the SVG actually renders in (DejaVu runs a few percent wider).
_LABEL_FONT = FontProperties(family="DejaVu Sans")


def text_width_px(s, size):
    if not s:
        return 0.0
    return 0.95 * TextPath((0, 0), s, size=size, prop=_LABEL_FONT).get_extents().width

# --- palette copied verbatim from make_figures.py -----------------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series
GREEN = "#3a7d44"      # frozen-judge series / value-move
RED = "#b5342c"        # reversal / warning emphasis
GRAY = "#6b7684"       # recessive only (guides, muted text)
KEY_FILL = "#eef5ee"

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


# --- real math typesetting via matplotlib mathtext ---------------------------
# Each display equation is rendered by matplotlib's mathtext to an in-memory SVG,
# then its glyph-path group is lifted out and inlined here. matplotlib emits the
# glyphs as <path>s referenced by <use> elements; those references are same-document
# (never external), and every id is namespaced per equation so multiple equations
# coexist in one file. No external LaTeX binary is used (mathtext only), so the
# figure stays stdlib-plus-matplotlib self-contained.
_EQ_COUNTER = [0]


def embed_math(mathstr, x, y_baseline, fontsize=22, scale=1.0, color=INK):
    """Typeset one equation and return (svg_group, advance_width_px). The group
    lands its baseline-left origin at (x, y_baseline) in this figure's pixel
    coordinates; advance_width_px is the on-page width of the typeset content, so
    pieces can be placed side by side and each term's x-extent is known. Passing the
    same fontsize and scale to every call keeps the on-page glyph size identical."""
    _EQ_COUNTER[0] += 1
    prefix = f"m{_EQ_COUNTER[0]}_"
    fig = plt.figure()
    fig.text(0, 0, mathstr, fontsize=fontsize)
    buf = io.StringIO()
    fig.savefig(buf, format="svg", transparent=True, bbox_inches="tight",
                pad_inches=0.01)
    plt.close(fig)
    doc = buf.getvalue()
    # the whole equation is one glyph group: <g transform="translate(tx ty) scale(..)">
    m = re.search(r'<g transform="translate\(([\d.]+) ([\d.eE+-]+)\) scale\([^)]*\)">',
                  doc)
    if not m:
        raise RuntimeError("could not locate mathtext glyph group in matplotlib SVG")
    tx, ty = float(m.group(1)), float(m.group(2))
    # tight-bbox width in points; content spans (tx .. width_pt - pad), pad = tx
    mw = re.search(r'<svg[^>]*?width="([\d.]+)pt"', doc)
    width_pt = float(mw.group(1))
    advance = scale * (width_pt - 2 * tx)
    start = m.start()
    end = doc.index("</g>", start) + len("</g>")   # no nested <g> inside the group
    frag = doc[start:end]
    # namespace every glyph id and its <use> reference so equations never collide
    frag = re.sub(r'id="([^"]+)"', rf'id="{prefix}\1"', frag)
    frag = re.sub(r'(xlink:href|href)="#([^"]+)"', rf'\1="#{prefix}\2"', frag)
    dx = x - scale * tx
    dy = y_baseline - scale * ty
    svg = (f'<g transform="translate({dx:.3f} {dy:.3f}) scale({scale})" '
           f'fill="{color}">{frag}</g>')
    return svg, advance


def measure(mathstr, fontsize=22, scale=1.0):
    """On-page advance width of a typeset equation (the glyphs are discarded)."""
    return embed_math(mathstr, 0, 0, fontsize=fontsize, scale=scale)[1]


def T(x, y, s, size, color=INK, italic=False, weight="normal", anchor="start"):
    st = ' font-style="italic"' if italic else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size:.2f}" fill="{color}" '
            f'font-weight="{weight}"{st} text-anchor="{anchor}" '
            f'font-family="{FONT}">{esc(s)}</text>')


# --- annotation helpers -------------------------------------------------------
def tick(cx, y_from, y_to, color=GRAY, width=1.0, opacity=0.6):
    return (f'<line x1="{cx:.1f}" y1="{y_from:.1f}" x2="{cx:.1f}" y2="{y_to:.1f}" '
            f'stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>')


def term_label(cx, y_base, row_y, label, anchor="middle", size=13, color=GRAY):
    """A thin leader line from just below the equation term down to a BOXED gray
    label. The line terminates exactly on the box's top edge (touching it, not
    floating) so it is unambiguous which text connects to which term. The box is a
    light rounded rectangle, thin stroke in the same muted gray as the leader, with
    ~6px of padding on EVERY side. The box is sized from the text's real rendered
    width and the text is centered inside it, so the padding is symmetric (no empty
    gap on one side). The leader still attaches at cx; the anchor only decides which
    way the box extends from cx so stacked labels don't collide."""
    pad = 6.0
    w = text_width_px(label, size)
    if anchor == "end":
        box_r = cx + pad
        box_l = cx - w - pad
    elif anchor == "start":
        box_l = cx - pad
        box_r = cx + w + pad
    else:  # middle
        box_l, box_r = cx - w / 2.0 - pad, cx + w / 2.0 + pad
    box_top = row_y - size * 0.86 - pad
    box_bot = row_y + size * 0.32 + pad
    text_cx = (box_l + box_r) / 2.0
    return [
        tick(cx, y_base + 8, box_top, opacity=0.55),
        f'<rect x="{box_l:.1f}" y="{box_top:.1f}" width="{box_r-box_l:.1f}" '
        f'height="{box_bot-box_top:.1f}" rx="4" ry="4" fill="#ffffff" '
        f'fill-opacity="0.92" stroke="{GRAY}" stroke-width="1" opacity="0.6"/>',
        T(text_cx, row_y, label, size, color, anchor="middle"),
    ]


def obrace(xl, xr, y_line, label):
    """A drawn bracket above a span of terms (end ticks point down toward the
    equation), with a gray label centered above it — the number-line structural
    reading of the recurrence."""
    s = [f'<path d="M {xl:.1f} {y_line+5:.1f} L {xl:.1f} {y_line:.1f} '
         f'L {xr:.1f} {y_line:.1f} L {xr:.1f} {y_line+5:.1f}" fill="none" '
         f'stroke="{GRAY}" stroke-width="1.1" opacity="0.75"/>']
    s.append(T((xl + xr) / 2, y_line - 6, label, 13, GRAY, anchor="middle"))
    return s


# --- geometry -----------------------------------------------------------------
W = 1240
NAME_X = 66          # left column: bold name
FX = 402             # formula column start
EQ_FS = 22.0         # mathtext point size (x-height matches the surrounding prose)

body = []

# ---- headline ----
body.append(f'<text x="{NAME_X}" y="60" font-size="29" font-weight="bold" '
            f'fill="{INK}" font-family="{FONT}">The model: one round, '
            f'iterated, self-only</text>')


# ---- intro / recurrence line (small, gray). Flowing <tspan>s kern naturally. ----
def var(t):
    return f'<tspan font-style="italic">{esc(t)}</tspan>'



body.append(f'<line x1="{NAME_X}" y1="90" x2="{W-60}" y2="90" '
            f'stroke="{GRAY}" stroke-width="1" opacity="0.35"/>')


def model_label(baseline, bold, note):
    s = [f'<text x="{NAME_X}" y="{baseline:.1f}" font-size="18" '
         f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
         f'{esc(bold)}</text>']
    if note:
        s.append(f'<text x="{NAME_X}" y="{baseline+20:.1f}" font-size="14.5" '
                 f'fill="{GRAY}" font-family="{FONT}">{esc(note)}</text>')
    return s


def prose(x, top_y, lines, size=15, color=GRAY, dy=20):
    out = []
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x}" y="{top_y+i*dy:.1f}" font-size="{size}" '
                   f'fill="{color}" font-family="{FONT}">{esc(ln)}</text>')
    return out


# ---- one round -----------------------------------------------------------
# displayed with the real clamp bracket [ ... ]_0^1 ; per-term positions found by
# measuring balanced prefixes (\right. is a zero-width null delimiter).
e1 = 208
body += model_label(e1, "one round", "σ, ρ fixed at round 1")
FULL1 = r"$v_{r+1} = \left[\,(1-u)\,v_r + u\,s + \rho\sigma\,\right]_0^1$"
eq1, w_eq1 = embed_math(FULL1, FX, e1, EQ_FS)


def R1(inner):
    return measure(r"$v_{r+1} = \left[\," + inner + r"\right.$", EQ_FS)


R1_pre = R1("")
R1_1 = R1(r"(1-u)\,v_r")
R1_2 = R1(r"(1-u)\,v_r + u\,s")
R1_3 = R1(r"(1-u)\,v_r + u\,s + \rho\sigma")
iso1_1 = measure(r"$(1-u)\,v_r$", EQ_FS)
iso1_1a = measure(r"$(1-u)$", EQ_FS)          # just the parenthesized factor
iso1_2 = measure(r"$u\,s$", EQ_FS)
iso1_3 = measure(r"$\rho\sigma$", EQ_FS)
# point the "own candidates' share" leader at the CENTER of (1 − u), not the middle of
# the whole (1−u)·v_r term (which sits near the u and reads as if it points at u).
c1_1 = FX + R1_pre + iso1_1a / 2
c1_2 = FX + R1_2 - iso1_2 / 2
c1_3 = FX + R1_3 - iso1_3 / 2
# structural reading (the number-line story) drawn ABOVE the equation
body += obrace(FX + R1_pre, FX + R1_2, e1 - 26, "pool mean p")
body += obrace(FX + R1_pre, FX + R1_3, e1 - 50, "kept mean k")
body.append(eq1)
# per-term labels BELOW, each on its own row and anchored to END at its term so a
# deeper term's (longer) tick to the right never crosses a shallower label's text.
body += term_label(c1_1, e1, e1 + 32, "own candidates' share of the pool mean",
                   anchor="end")
body += term_label(c1_2, e1, e1 + 64, "outside source: share u at level s",
                   anchor="end")
body += term_label(c1_3, e1, e1 + 96, "selection: the judge's step", anchor="end")
# clip note as a plain small gray note to the RIGHT of the equation (no leader/box),
# like the staged-noise block's right-side ε-distribution notes
body.append(T(FX + w_eq1 + 40, e1, "[·]₀¹ = clipped to [0, 1]", 14, GRAY))

# ---- iterated (mixed pool) ----------------------------------------------
e2 = e1 + 158
body += model_label(e2, "iterated", "(mixed pool)")
FULL2 = r"$v_r = v^{*} + (1-u)^{r}\,(v_0 - v^{*})$"
eq2, _ = embed_math(FULL2, FX, e2, EQ_FS)
R2_1 = measure(r"$v_r = v^{*}$", EQ_FS)
R2_2 = measure(r"$v_r = v^{*} + (1-u)^{r}$", EQ_FS)
R2_3 = measure(FULL2, EQ_FS)
iso2_1 = measure(r"$v^{*}$", EQ_FS)
iso2_2 = measure(r"$(1-u)^{r}$", EQ_FS)
iso2_3 = measure(r"$(v_0 - v^{*})$", EQ_FS)
c2_1 = FX + R2_1 - iso2_1 / 2
c2_2 = FX + R2_2 - iso2_2 / 2
c2_3 = FX + R2_3 - iso2_3 / 2
body.append(eq2)
body += term_label(c2_1, e2, e2 + 32, "the balance point (= s + ρσ/u)", anchor="end")
body += term_label(c2_2, e2, e2 + 64,
                   "a fraction u of the distance closed each round", anchor="end")
body += term_label(c2_3, e2, e2 + 96, "the starting distance from balance",
                   anchor="end")

# ---- self-only (u = 0) ---------------------------------------------------
e3 = e2 + 184
body += model_label(e3, "self-only", "(u = 0)")
FULL3 = r"$v_r = v_0 + r\,\rho\sigma$"
eq3, _ = embed_math(FULL3, FX, e3, EQ_FS)
R3_full = measure(FULL3, EQ_FS)
iso3_t = measure(r"$r\,\rho\sigma$", EQ_FS)
c3_t = FX + R3_full - iso3_t / 2
body.append(eq3)
body += term_label(c3_t, e3, e3 + 32, "one selection step ρσ per round")

# =============== SYMBOL TABLE (every quantity in the model defined) ===========
# So no symbol appears anywhere above without a definition somewhere on the page —
# including the round index r. The measurements' own symbols (σ_j, ρ_j, g, x_jk …)
# live with docs/figures/auto/state-variables.
sym_top = e3 + 70
body.append(f'<line x1="{NAME_X}" y1="{sym_top:.1f}" x2="{W-60}" y2="{sym_top:.1f}" '
            f'stroke="{INK}" stroke-width="1.4" opacity="0.55"/>')
body.append(f'<text x="{NAME_X}" y="{sym_top+30:.1f}" font-size="20" '
            f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
            f'Symbols — every quantity in the model</text>')


# The symbol column is set with REAL SVG-tspan subscripts (not unicode subscript
# characters, which Helvetica/Arial does not carry and renders flat).
# Markup: "_x" makes the next char a subscript, "_{ab}" a multi-char subscript;
# everything else is an ordinary base glyph.
def sym_tspans(markup):
    parts, i = [], 0
    while i < len(markup):
        if markup[i] == '_':
            i += 1
            if i < len(markup) and markup[i] == '{':
                j = markup.index('}', i)
                parts.append(('sub', markup[i + 1:j]))
                i = j + 1
            else:
                parts.append(('sub', markup[i]))
                i += 1
        else:
            start = i
            while i < len(markup) and markup[i] != '_':
                i += 1
            parts.append(('base', markup[start:i]))
    out = []
    for kind, txt in parts:
        if kind == 'base':
            out.append(f'<tspan font-style="italic" font-weight="bold" '
                       f'fill="{INK}">{esc(txt)}</tspan>')
        else:
            out.append(f'<tspan font-style="italic" font-weight="bold" '
                       f'fill="{INK}" font-size="10" baseline-shift="-18%">'
                       f'{esc(txt)}</tspan>')
    return "".join(out)


# (symbol-markup, definition) — only the model quantities
SYMBOLS = [
    ("r", "round index (1, 2, …)"),
    ("v_r", "behavioral value at round r"),
    ("v_0", "starting value (round 0)"),
    ("v*", "balance point (fixed point of the mixed pool)"),
    ("u", "outside-source share of the pool"),
    ("s", "outside source's mean value level"),
    ("q", "organism's own-candidate mean"),
    ("p", "pool mean = (1−u)q + u·s"),
    ("k", "kept mean = p + ρσ"),
    ("σ", "spread — per-prompt value SD, meaned"),
    ("ρ", "agreement — judge×value correlation"),
]
COLS = 3
ROWS = (len(SYMBOLS) + COLS - 1) // COLS
col_w = (W - 60 - NAME_X) / COLS
sym_row0 = sym_top + 58
for i, (symb, defn) in enumerate(SYMBOLS):
    c, rr = i // ROWS, i % ROWS
    x = NAME_X + c * col_w
    y = sym_row0 + rr * 24
    body.append(
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="14.5" font-family="{FONT}">'
        f'{sym_tspans(symb)}'
        f'<tspan fill="{GRAY}">  —  {esc(defn)}</tspan></text>')

# provenance note for the round-1 measurements this model consumes
note_y = sym_row0 + ROWS * 24 + 6
body.append(
    f'<text x="{NAME_X}" y="{note_y:.1f}" font-size="14.5" '
    f'font-family="{FONT}">'
    f'<tspan font-style="italic" font-weight="bold" fill="{INK}">σ, ρ</tspan>'
    f'<tspan fill="{GRAY}">  —  measured at round 1, see the measurements '
    f'figure.</tspan></text>')

H = note_y + 34

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
       f'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>")

OUT = os.path.join(HERE, "model-recurrence.svg")
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}  ({W}x{H})")

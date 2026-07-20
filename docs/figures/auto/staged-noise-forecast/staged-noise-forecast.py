#!/usr/bin/env python3
"""The staged-noise forecast — the stochastic rollout the value-dynamics model
runs: a deterministic unit path plus staged gaussian innovations, each clamped to
its wall, typeset as a clean definitions panel — every part of every equation
explained AT the equation, so the reader never leaves a formula to hunt through
prose.

This figure is the STOCHASTIC ROLLOUT part only. The per-round measurements it
consumes (spread σ, agreement ρ) are defined in
docs/figures/auto/state-variables/; the deterministic model and its closed forms
are in docs/figures/auto/model-recurrence/.

The display equations are typeset with matplotlib's mathtext (Computer Modern,
fontset "cm") and embedded as inline vector glyph paths, so they read as proper
math while the figure stays a single self-contained SVG with no external font or
URL references. Each stochastic stage carries a tick down to a gray boxed label
naming its ε term, and the innovation's distribution sits in the right column.

No data file is read — this is a definitions figure. It typesets EXACTLY what
rollout() in docs/figures/auto/spread-rollout-bakeoff/spread-rollout-bakeoff.py
does (provenance scripts/analysis_trajectory_adjustments.py): deterministic
mixing, clamped kept/generator/value/agreement updates with staged gaussian
innovations, and a measurement-noise term added only to the value read off. Each
ε's SD is the pooled leave-one-condition-out residual of that stage.

Style reference: docs/figures/src/make_figures.py (Owain Evans-lab house style).
Palette constants, esc(), and wrap() are copied here verbatim so this generator is
self-contained (stdlib only + matplotlib for the mathtext glyphs). Run from this
directory:  uv run --with matplotlib python3 staged-noise-forecast.py
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


def prose(x, top_y, lines, size=15, color=GRAY, dy=20):
    out = []
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x}" y="{top_y+i*dy:.1f}" font-size="{size}" '
                   f'fill="{color}" font-family="{FONT}">{esc(ln)}</text>')
    return out


# --- geometry -----------------------------------------------------------------
W = 1240
NAME_X = 66          # left column: bold name / stage descriptor
FX = 402             # formula column start
EQ_FS = 22.0         # mathtext point size (x-height matches the surrounding prose)
RIGHTEQ_X = 772      # right column: the innovation's distribution
NOTE_FS = EQ_FS * 0.82

body = []

# ---- headline ----
body.append(f'<text x="{NAME_X}" y="60" font-size="29" font-weight="bold" '
            f'fill="{INK}" font-family="{FONT}">The staged-noise forecast '
            f'(the stochastic rollout)</text>')


body.append(f'<line x1="{NAME_X}" y1="92" x2="{W-60}" y2="92" '
            f'stroke="{GRAY}" stroke-width="1" opacity="0.35"/>')


def stoch_row(baseline, left_desc, full_eq, note_math=None, note_text=None,
              eps_prefix=None, eps_iso=None, eps_label=None):
    """One stochastic-forecast line: gray left descriptor, the display equation at
    FX, the innovation's distribution (or a determinism note) in the right column,
    and — for the stochastic stages — a tick under the ε term to a gray label."""
    out = [T(NAME_X, baseline, left_desc, 15, GRAY)]
    eq_svg, _ = embed_math(full_eq, FX, baseline, EQ_FS)
    out.append(eq_svg)
    if note_math:
        nm, _ = embed_math(note_math, RIGHTEQ_X, baseline, NOTE_FS, color=GRAY)
        out.append(nm)
    elif note_text:
        out.append(T(RIGHTEQ_X, baseline, note_text, 14, GRAY))
    if eps_prefix:
        cx = (FX + measure("$" + eps_prefix + r"\right.$", EQ_FS)
              - measure("$" + eps_iso + "$", EQ_FS) / 2)
        out.extend(term_label(cx, baseline, baseline + 32, eps_label))
    return out


f0 = 140
GAP = 70

body += stoch_row(
    f0, "pool mean",
    r"$p_r = (1-u)\,q_r + u\,s$",
    note_text="(deterministic mixing)")

body += stoch_row(
    f0 + GAP, "kept mean",
    r"$k_r = \left[\,p_r + \rho_r\,\sigma + \varepsilon_g\,\right]_0^1$",
    note_math=r"$\varepsilon_g \;\sim\; N(0,\ s_g)$",
    eps_prefix=r"k_r = \left[\,p_r + \rho_r\,\sigma + \varepsilon_g",
    eps_iso=r"\varepsilon_g",
    eps_label="innovation in the judge's step (selector-gap residual)")

body += stoch_row(
    f0 + 2 * GAP, "generator",
    r"$q_{r+1} = \left[\,q_r + (k_r - q_r) + \varepsilon_q\,\right]_0^1$",
    note_math=r"$\varepsilon_q \;\sim\; N(0,\ s_q)$",
    eps_prefix=r"q_{r+1} = \left[\,q_r + (k_r - q_r) + \varepsilon_q",
    eps_iso=r"\varepsilon_q",
    eps_label="innovation in the generator update")

body += stoch_row(
    f0 + 3 * GAP, "value",
    r"$v_{r+1} = \left[\,v_r + (k_r - v_r)\,\right]_0^1$",
    note_text="(the value's move itself is deterministic)")

body += stoch_row(
    f0 + 4 * GAP, "agreement",
    r"$\rho_{r+1} = \left[\,\rho_r + \varepsilon_\rho\,\right]_{-1}^{+1}$",
    note_math=r"$\varepsilon_\rho \;\sim\; N(0,\ s_\rho)$",
    eps_prefix=r"\rho_{r+1} = \left[\,\rho_r + \varepsilon_\rho",
    eps_iso=r"\varepsilon_\rho",
    eps_label="round-to-round innovation in agreement")

body += stoch_row(
    f0 + 5 * GAP, "observed",
    r"$\hat{v}_r = \left[\,v_r + \varepsilon_{\mathrm{obs}}\,\right]_0^1$",
    note_math=r"$\varepsilon_{\mathrm{obs}} \;\sim\; N\!\left(0,\ \sqrt{v_r(1-v_r)/n}\right)$",
    eps_prefix=r"\hat{v}_r = \left[\,v_r + \varepsilon_{\mathrm{obs}}",
    eps_iso=r"\varepsilon_{\mathrm{obs}}",
    eps_label="measurement noise, added only to the value read off, never to "
              "the loop's state (n = answers sampled per measurement)")

# =============== SYMBOL TABLE (every quantity in the rollout defined) =========
# So no symbol appears anywhere above without a definition somewhere on the page —
# including the round index r. The measurements' own symbols (σ_j, ρ_j, g, x_jk …)
# live with docs/figures/auto/state-variables.
sym_top = f0 + 5 * GAP + 62
body.append(f'<line x1="{NAME_X}" y1="{sym_top:.1f}" x2="{W-60}" y2="{sym_top:.1f}" '
            f'stroke="{INK}" stroke-width="1.4" opacity="0.55"/>')
body.append(f'<text x="{NAME_X}" y="{sym_top+30:.1f}" font-size="20" '
            f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
            f'Symbols — every quantity in the rollout</text>')


# The symbol column is set with REAL SVG-tspan subscripts (not unicode subscript
# characters, which Helvetica/Arial does not carry for g/q/ρ/obs and renders flat).
# Markup: "_x" makes the next char a subscript, "_{ab}" a multi-char subscript;
# everything else is an ordinary base glyph. "̂" is a combining circumflex (v̂).
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


# (symbol-markup, definition) — only the rollout quantities
SYMBOLS = [
    ("r", "round index (1, 2, …)"),
    ("q_r", "organism's own-candidate mean (generator)"),
    ("p_r", "pool mean = (1−u)qᵣ + u·s"),
    ("k_r", "kept mean (mean value of the 2 kept)"),
    ("ρ_r", "agreement — judge×value correlation"),
    ("v_r", "behavioral value at round r"),
    ("v̂_r", "measured value"),
    ("u", "outside-source share of the pool"),
    ("s", "outside source's mean value level"),
    ("n", "answers sampled per measurement"),
    ("ε_g, ε_q, ε_ρ", "staged innovations"),
    ("s_g, s_q, s_ρ", "their SDs: each stage's measured residual spread"),
    ("ε_{obs}", "measurement noise (SD √(vᵣ(1−vᵣ)/n))"),
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

# provenance note for the round-1 measurements this rollout consumes
note_y = sym_row0 + ROWS * 24 + 6
body.append(
    f'<text x="{NAME_X}" y="{note_y:.1f}" font-size="14.5" '
    f'font-family="{FONT}">'
    f'<tspan font-style="italic" font-weight="bold" fill="{INK}">σ, ρ</tspan>'
    f'<tspan fill="{GRAY}">  —  the round-1 measurements, see the measurements '
    f'figure.</tspan></text>')

H = note_y + 34

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
       f'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>")

OUT = os.path.join(HERE, "staged-noise-forecast.svg")
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}  ({W}x{H})")

#!/usr/bin/env python3
"""The three per-round measurements of the selection loop (spread, agreement,
selector gap), typeset as a clean definitions panel — every part of every equation
explained AT the equation, so the reader never leaves a formula to hunt through
prose. Replaces an unreadable markdown bullet list, so the whole point is legible
math typography.

This figure is the MEASUREMENTS part only. The round-by-round model those
measurements feed lives in docs/figures/auto/model-recurrence/, and the stochastic
staged-noise rollout lives in docs/figures/auto/staged-noise-forecast/.

The three measurement rows are laid out in hand-built SVG plus matplotlib mathtext
embeds. The spread and agreement rows show BOTH the per-prompt estimator and the
round-level aggregation (the committed mean over prompts), each with a gray gloss
naming its index set. The estimators are typeset with matplotlib's mathtext
(Computer Modern, fontset "cm") and embedded as inline vector glyph paths, so they
read as proper math while the figure stays a single self-contained SVG with no
external font or URL references.

No data file is read — this is a definitions figure. The recipes shown match the
committed scorers:
  scripts/analysis_qwen_selfonly_model_check.py  (sigma_j population SD, rho_j =
      Pearson(s_jk, x_jk), gap_j = kept mean - pool mean; round = MEAN over prompts,
      rho over prompts where the correlation is defined)
  scripts/analysis_spread_util_unified.py         (spread = MEAN over prompts of the
      within-prompt population SD; each prompt measured on its own, weighted equally)

Style reference: docs/figures/src/make_figures.py (Owain Evans-lab house style).
Palette constants, esc(), and wrap() are copied here verbatim so this generator is
self-contained (stdlib only + matplotlib for the mathtext glyphs). Run from this
directory:  uv run --with matplotlib python3 state-variables.py
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


# --- tiny math-typesetting engine --------------------------------------------
# Everything is placed by an advancing cursor so glyph runs, subscripts and the
# minus operator can be drawn at exact positions. Widths are approximate Helvetica
# advances; the render is inspected visually before shipping.
def _adv(text, size, f=0.56):
    return len(text) * size * f


def T(x, y, s, size, color=INK, italic=False, weight="normal", anchor="start"):
    st = ' font-style="italic"' if italic else ''
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size:.2f}" fill="{color}" '
            f'font-weight="{weight}"{st} text-anchor="{anchor}" '
            f'font-family="{FONT}">{esc(s)}</text>')


def render_run(tokens, x, y, base=23, color=INK):
    """Lay a list of math tokens left-to-right from (x, y baseline).
    Token kinds:
      ('g', text, italic)       ordinary glyph run
      ('sub', text[, italic])   subscript (small, lowered)
      ('sup', text)             superscript (small, raised)
      ('op', text)              binary operator with padding on both sides
      ('sp', px)                explicit horizontal space
    Returns (svg_pieces, x_end).
    """
    out, cur = [], x
    for tok in tokens:
        k = tok[0]
        if k == 'g':
            txt, it = tok[1], tok[2]
            out.append(T(cur, y, txt, base, color, it))
            cur += _adv(txt, base)
        elif k == 'sub':
            txt = tok[1]
            it = tok[2] if len(tok) > 2 else False
            ss = base * 0.66
            out.append(T(cur, y + base * 0.30, txt, ss, color, it))
            cur += _adv(txt, ss)
        elif k == 'sup':
            txt = tok[1]
            ss = base * 0.66
            out.append(T(cur, y - base * 0.46, txt, ss, color))
            cur += _adv(txt, ss)
        elif k == 'op':
            txt = tok[1]
            cur += base * 0.22
            out.append(T(cur, y, txt, base, color))
            cur += _adv(txt, base) + base * 0.22
        elif k == 'sp':
            cur += tok[1]
    return out, cur


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
    if row_y < y_base:                  # label ABOVE the equation
        leader = tick(cx, y_base - 26, box_bot, opacity=0.55)
    else:                               # label below (the default)
        leader = tick(cx, y_base + 8, box_top, opacity=0.55)
    return [
        leader,
        f'<rect x="{box_l:.1f}" y="{box_top:.1f}" width="{box_r-box_l:.1f}" '
        f'height="{box_bot-box_top:.1f}" rx="4" ry="4" fill="#ffffff" '
        f'fill-opacity="0.92" stroke="{GRAY}" stroke-width="1" opacity="0.6"/>',
        T(text_cx, row_y, label, size, color, anchor="middle"),
    ]


# --- geometry -----------------------------------------------------------------
W = 1240
NAME_X = 66          # left column: bold name
SYM_X = 300          # italic symbol glyph
FX = 402             # formula column start
FORM_BASE = 23
EQ_FS = 22.0         # mathtext point size (x-height matches the surrounding prose)

body = []

# ---- headline (descriptive, orientation only) ----
body.append(f'<text x="{NAME_X}" y="60" font-size="29" font-weight="bold" '
            f'fill="{INK}" font-family="{FONT}">The per-round measurements</text>')


# ---- setup line (small, gray). Flowing <tspan>s kern naturally. ----
def var(t):
    return f'<tspan font-style="italic">{esc(t)}</tspan>'


def sub(t):
    return (f'<tspan font-size="11" baseline-shift="-20%" '
            f'font-style="italic">{esc(t)}</tspan>')


setup = (f'<text x="{NAME_X}" y="98" font-size="16" fill="{GRAY}" '
         f'font-family="{FONT}">'
         f'Per prompt {var("j")} in a round, the pool holds candidates '
         f'{var("k")} = 1…{var("n")}{sub("j")} with value scores '
         f'{var("x")}{sub("jk")} in [0,1] and judge scores '
         f'{var("s")}{sub("jk")};  the judge keeps two candidates.</text>')
body.append(setup)

body.append(f'<line x1="{NAME_X}" y1="118" x2="{W-60}" y2="118" '
            f'stroke="{GRAY}" stroke-width="1" opacity="0.35"/>')


def name_cell(baseline, name, sym, desc=None):
    s = [f'<text x="{NAME_X}" y="{baseline:.1f}" font-size="21" '
         f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
         f'{esc(name)}</text>']
    if desc:
        for i, ln in enumerate(desc if isinstance(desc, list) else [desc]):
            s.append(f'<text x="{NAME_X}" y="{baseline + 24 + i*18:.1f}" '
                     f'font-size="13.5" fill="{GRAY}" font-family="{FONT}">'
                     f'{esc(ln)}</text>')
    if sym:
        s.append(f'<text x="{SYM_X}" y="{baseline:.1f}" font-size="27" '
                 f'font-weight="bold" font-style="italic" fill="{BLUE}" '
                 f'text-anchor="middle" font-family="{FONT}">{esc(sym)}</text>')
    return s


def prose(x, top_y, lines, size=15, color=GRAY, dy=20):
    out = []
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x}" y="{top_y+i*dy:.1f}" font-size="{size}" '
                   f'fill="{color}" font-family="{FONT}">{esc(ln)}</text>')
    return out


def divider(y):
    body.append(f'<line x1="{NAME_X}" y1="{y:.1f}" x2="{W-60}" y2="{y:.1f}" '
                f'stroke="{GRAY}" stroke-width="1" opacity="0.22"/>')


# =========================== ROW 1 : spread sigma ============================
r1 = 178
body += name_cell(r1, "spread", "σ", ["per-prompt value SD,", "meaned over prompts"])
# per-prompt estimator (mathtext, same machinery and size as everywhere)
eq_s1, _ = embed_math(
    r"$\sigma_j = \sqrt{\frac{1}{n_j}\,\sum_k (x_{jk}-\bar{x}_j)^2}$",
    FX, r1, EQ_FS)
body.append(eq_s1)
# round-level aggregation:  sigma = (1/J) Sigma_j sigma_j   (committed = mean over prompts)
r1b = r1 + 54
eq_s2, w_s2 = embed_math(r"$\sigma = \frac{1}{J}\sum_j \sigma_j$", FX, r1b, EQ_FS)
body.append(eq_s2)
body += prose(FX + w_s2 + 28, r1b,
              ["J = the round's prompts, equal weight each."], size=14)
divider(r1b + 42)

# =========================== ROW 2 : agreement rho ===========================
r2 = r1b + 88
body += name_cell(r2, "agreement", "ρ", ["per-prompt judge × value", "correlation, meaned"])
# whole per-prompt line as ONE mathtext embed (corr prefix + Pearson fraction) so
# the two = signs align; same machinery and size as everywhere.
CORR = (r"$\rho_j = \mathrm{corr}(s_{j\cdot},\, x_{j\cdot}) = "
        r"\frac{\sum_k (s_{jk}-\bar{s}_j)(x_{jk}-\bar{x}_j)}"
        r"{\sqrt{\sum_k (s_{jk}-\bar{s}_j)^2 \cdot "
        r"\sum_k (x_{jk}-\bar{x}_j)^2}}$")
eq_c, _ = embed_math(CORR, FX, r2, EQ_FS)
body.append(eq_c)
# round-level aggregation:  rho = (1/|D|) Sigma_{j in D} rho_j  (proper |D| bars)
r2b = r2 + 76
eq_a, w_a = embed_math(r"$\rho = \frac{1}{|D|}\sum_{j\in D}\rho_j$",
                       FX, r2b, EQ_FS)
body.append(eq_a)
body += prose(FX + w_a + 28, r2b - 6, [
    "D = prompts where ρⱼ is defined (fewer than two candidates,",
    "or zero variance on either side, drop the prompt).",
], size=14, dy=18)
divider(r2b + 40)

# =========================== ROW 3 : selector gap g ==========================
r3 = r2b + 140
body += name_cell(r3, "selector gap", "g", ["kept mean minus", "pool mean"])
# typeset g = k − p as mathtext (same face/size as the other equations),
# in four sequential embeds so k and p keep exact label-anchor positions.
GAP = 9.0
e_g, w_g = embed_math(r"$g \, =$", FX, r3, EQ_FS)
x = FX + w_g + GAP
e_k, w_k = embed_math(r"$k$", x, r3, EQ_FS)
k_center = x + w_k / 2
x += w_k + GAP
e_m, w_m = embed_math(r"$-$", x, r3, EQ_FS)
x += w_m + GAP
e_p, w_p = embed_math(r"$p$", x, r3, EQ_FS)
p_center = x + w_p / 2
x_p1 = x + w_p
body += [e_g, e_k, e_m, e_p]
# tick + label under k (kept mean) and under p (pool mean), staggered rows
body += term_label(k_center, r3, r3 - 52, "mean value of the 2 kept candidates", anchor="end")
body += term_label(p_center, r3, r3 + 46, "mean value of the whole candidate pool")
# forecast as a small gray note to the RIGHT of the equation (same style/placement as
# the one-round clip note): the row reads  g = k − p   then, off right,  ≈ ρσ
body.append(T(x_p1 + 40, r3, "≈ ρσ", 14, GRAY))

# =============== SYMBOL TABLE (every quantity in the measurements defined) ====
# So no symbol appears anywhere above without a definition somewhere on the page.
# Terse restatements of the row/gloss definitions, collected in one place. This
# figure's symbols only — the model's and rollout's own symbols live with those
# figures (docs/figures/auto/model-recurrence, docs/figures/auto/staged-noise-forecast).
sym_top = r3 + 118
body.append(f'<line x1="{NAME_X}" y1="{sym_top:.1f}" x2="{W-60}" y2="{sym_top:.1f}" '
            f'stroke="{INK}" stroke-width="1.4" opacity="0.55"/>')
body.append(f'<text x="{NAME_X}" y="{sym_top+30:.1f}" font-size="20" '
            f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
            f'Symbols — every quantity in the measurements</text>')


# The symbol column is set with REAL SVG-tspan subscripts (not unicode subscript
# characters, which Helvetica/Arial does not carry for g/q/ρ/obs and renders flat).
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


# (symbol-markup, definition) — only the measurement quantities
SYMBOLS = [
    ("x_{jk}", "value score of prompt j, candidate k"),
    ("s_{jk}", "judge score of prompt j, candidate k"),
    ("n_j", "candidates in prompt j's pool"),
    ("J", "the round's prompts (count), equal weight"),
    ("D", "prompts where ρⱼ is defined"),
    ("σ_j", "per-prompt value SD (population, ÷ nⱼ)"),
    ("σ", "spread — per-prompt value SD, meaned"),
    ("ρ_j", "per-prompt judge × value correlation"),
    ("ρ", "agreement — ρⱼ meaned over D"),
    ("g", "selector gap = k − p"),
    ("k", "kept mean (mean value of the 2 kept)"),
    ("p", "pool mean (mean value of the whole pool)"),
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

H = sym_row0 + (ROWS - 1) * 24 + 40

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
       f'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>")

OUT = os.path.join(HERE, "state-variables.svg")
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}  ({W}x{H})")

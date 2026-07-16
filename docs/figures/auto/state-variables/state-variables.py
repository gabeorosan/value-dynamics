#!/usr/bin/env python3
"""The five per-round bookkeeping quantities of the selection loop, typeset as a
clean definitions panel. Replaces an unreadable markdown bullet list, so the whole
point is legible math typography. The three per-round measurement rows (spread,
agreement, selector gap) are laid out in hand-built SVG with proper subscripts,
italic symbols, a real radical bar for the square root, and an overbar for the
mean. The three display equations in "The model these feed" are typeset with
matplotlib's mathtext (Computer Modern, fontset "cm") and embedded as inline vector
glyph paths, so they read as proper math (true italics, subscripts, superscripts)
while the figure stays a single self-contained SVG with no external font or URL
references.

No data file is read — this is a definitions figure. The recipes shown match the
committed scorers:
  scripts/analysis_qwen_selfonly_model_check.py  (sigma_j population SD, rho_j
      Pearson(s_jk, x_jk), gap_j = kept mean - pool mean; round = mean over prompts)
  scripts/analysis_spread_util_unified.py         (spread = mean within-item
      population SD, divide by n; each prompt measured on its own, prompts weighted equally)

Style reference: docs/figures/src/make_figures.py (Owain Evans-lab house style).
Palette constants, esc(), and wrap() are copied here verbatim so this generator is
self-contained (stdlib only). Run from this directory:  python3 state-variables.py
"""
import os
import io
import re

import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["mathtext.fontset"] = "cm"   # Computer Modern: reads as proper math
matplotlib.rcParams["svg.fonttype"] = "path"     # glyphs as vector paths (no font dependency)
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))

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
# Each display equation in "The model these feed" is rendered by matplotlib's
# mathtext to an in-memory SVG, then its glyph-path group is lifted out and inlined
# here. matplotlib emits the glyphs as <path>s referenced by <use> elements; those
# references are same-document (never external), and every id is namespaced per
# equation so multiple equations coexist in one file. No external LaTeX binary is
# used (mathtext only), so the figure stays stdlib-plus-matplotlib self-contained.
_EQ_COUNTER = [0]


def embed_math(mathstr, x, y_baseline, fontsize=22, scale=1.0, color=INK):
    """Typeset one equation and return an SVG <g> that lands its baseline-left
    origin at (x, y_baseline) in this figure's pixel coordinates. Passing the same
    fontsize and scale to every call keeps the on-page glyph size identical across
    equations (target x-height matches the surrounding 17-18px prose)."""
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
    start = m.start()
    end = doc.index("</g>", start) + len("</g>")   # no nested <g> inside the group
    frag = doc[start:end]
    # namespace every glyph id and its <use> reference so equations never collide
    frag = re.sub(r'id="([^"]+)"', rf'id="{prefix}\1"', frag)
    frag = re.sub(r'(xlink:href|href)="#([^"]+)"', rf'\1="#{prefix}\2"', frag)
    dx = x - scale * tx
    dy = y_baseline - scale * ty
    return (f'<g transform="translate({dx:.3f} {dy:.3f}) scale({scale})" '
            f'fill="{color}">{frag}</g>')


# --- tiny math-typesetting engine --------------------------------------------
# Everything is placed by an advancing cursor so the radical bar and the mean
# overbar can be drawn at exact glyph positions. Widths are approximate Helvetica
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
      ('gbar', text, italic)    glyph run with an overbar (the mean)
      ('sub', text[, italic])   subscript (small, lowered)
      ('sup', text)             superscript (small, raised)
      ('op', text)              binary operator with padding on both sides
      ('sigma',)                big capital sigma with a 'k' index centered below
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
        elif k == 'gbar':
            txt, it = tok[1], tok[2]
            out.append(T(cur, y, txt, base, color, it))
            w = _adv(txt, base)
            out.append(f'<line x1="{cur:.1f}" y1="{y-base*0.78:.1f}" '
                       f'x2="{cur+w:.1f}" y2="{y-base*0.78:.1f}" '
                       f'stroke="{color}" stroke-width="1.7"/>')
            cur += w
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
        elif k == 'sigma':
            ss = base * 1.30
            out.append(T(cur, y, 'Σ', ss, color))
            w = _adv('Σ', ss, 0.60)
            out.append(T(cur + w / 2, y + base * 0.60, 'k', base * 0.60,
                         color, False, 'middle'))
            cur += w
        elif k == 'sp':
            cur += tok[1]
    return out, cur


def radical(x0, y, radicand_width, base):
    """A real square-root sign: a check leading into a horizontal vinculum that
    spans the radicand. Returns (svg, x_radicand_start)."""
    y_top = y - base * 1.30
    y_bot = y + base * 0.30
    y_mid = y - base * 0.30
    jx = x0 + base * 0.62          # where the tall stroke meets the bar
    p = (f'<path d="M {x0:.1f} {y_mid:.1f} L {x0+base*0.30:.1f} {y_bot:.1f} '
         f'L {jx:.1f} {y_top:.1f} L {jx+radicand_width+8:.1f} {y_top:.1f}" '
         f'fill="none" stroke="{INK}" stroke-width="2" '
         f'stroke-linejoin="round" stroke-linecap="round"/>')
    return p, jx + 5


# --- geometry -----------------------------------------------------------------
W, H = 1200, 886
NAME_X = 66          # left column: bold name
SYM_X = 300          # italic symbol glyph
FX = 402             # formula column start
RIGHT_X = 748        # right identification column (simple rows)
FORM_BASE = 23

body = []

# ---- headline (descriptive, orientation only) ----
body.append(f'<text x="{NAME_X}" y="60" font-size="29" font-weight="bold" '
            f'fill="{INK}" font-family="{FONT}">The per-round measurements '
            f'and the model they feed</text>')

# ---- setup line (small, gray). Flowing <tspan>s kern naturally, so the
# variables stay italic and the subscripts stay tight without manual widths. ----
def var(t):
    return f'<tspan font-style="italic">{esc(t)}</tspan>'


def sub(t):
    # baseline-shift is self-contained: the baseline resets when the tspan closes.
    return (f'<tspan font-size="11" baseline-shift="-20%" '
            f'font-style="italic">{esc(t)}</tspan>')


setup = (f'<text x="{NAME_X}" y="98" font-size="16" fill="{GRAY}" '
         f'font-family="{FONT}">'
         f'Per prompt {var("j")} in a round, the pool holds candidates '
         f'{var("k")} = 1…{var("n")}{sub("j")} with value scores '
         f'{var("x")}{sub("jk")} in [0,1] and judge scores '
         f'{var("s")}{sub("jk")};  the judge keeps two.</text>')
body.append(setup)

# a light rule under the header
body.append(f'<line x1="{NAME_X}" y1="118" x2="{W-60}" y2="118" '
            f'stroke="{GRAY}" stroke-width="1" opacity="0.35"/>')


def name_cell(baseline, name, sym):
    s = [f'<text x="{NAME_X}" y="{baseline:.1f}" font-size="21" '
         f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
         f'{esc(name)}</text>']
    if sym:
        s.append(f'<text x="{SYM_X}" y="{baseline:.1f}" font-size="27" '
                 f'font-weight="bold" font-style="italic" fill="{BLUE}" '
                 f'text-anchor="middle" font-family="{FONT}">{esc(sym)}</text>')
    return s


def id_below(baseline, lines):
    out = []
    for i, ln in enumerate(lines):
        out.append(f'<text x="{FX}" y="{baseline+30+i*20:.1f}" font-size="15" '
                   f'fill="{GRAY}" font-family="{FONT}">{esc(ln)}</text>')
    return out


def id_right(baseline, lines):
    out = []
    n = len(lines)
    y0 = baseline - (n - 1) * 10
    for i, ln in enumerate(lines):
        out.append(f'<text x="{RIGHT_X}" y="{y0+i*20:.1f}" font-size="15" '
                   f'fill="{GRAY}" font-family="{FONT}">{esc(ln)}</text>')
    return out


def divider(y):
    body.append(f'<line x1="{NAME_X}" y1="{y:.1f}" x2="{W-60}" y2="{y:.1f}" '
                f'stroke="{GRAY}" stroke-width="1" opacity="0.22"/>')


# =========================== ROW 1 : spread sigma ============================
r1 = 192
body += name_cell(r1, "spread", "σ")
# prefix:  sigma_j  =
pre, cur = render_run([('g', 'σ', True), ('sub', 'j', True), ('op', '=')],
                      FX, r1, FORM_BASE)
body += pre
# measure the radicand first (render offscreen to get width)
radicand = [('g', '(', False), ('g', '1/', False), ('g', 'n', True),
            ('sub', 'j', True), ('g', ')', False), ('sp', 8),
            ('g', '·', False), ('sp', 8),
            ('sigma',), ('sp', 6),
            ('g', '(', False), ('g', 'x', True), ('sub', 'jk', True),
            ('op', '−'),
            ('gbar', 'x', True), ('sub', 'j', True), ('g', ')', False),
            ('sup', '2')]
_probe, xend = render_run(radicand, 0, r1, FORM_BASE)
rad_w = xend - 0
rad_svg, rx0 = radical(cur + 4, r1, rad_w, FORM_BASE)
body.append(rad_svg)
rad_pieces, _ = render_run(radicand, rx0, r1, FORM_BASE)
body += rad_pieces
body += id_below(r1, [
    "per prompt: standard deviation of the candidate value scores "
    "(divide by nⱼ, the population convention).",
    "The round's σ is the mean over prompts of σⱼ — each prompt's pool is "
    "measured on its own,",
    "and every prompt counts equally.",
])

divider(284)

# =========================== ROW 2 : agreement rho ===========================
r2 = 344
body += name_cell(r2, "agreement", "ρ")
run2 = [('g', 'ρ', True), ('sub', 'j', True), ('op', '='),
        ('g', 'corr', False), ('g', '(', False),
        ('g', 's', True), ('sub', 'j·', True), ('g', ',', False),
        ('sp', 5), ('g', 'x', True), ('sub', 'j·', True),
        ('g', ')', False)]
p2, _ = render_run(run2, FX, r2, FORM_BASE)
body += p2
body += id_below(r2, [
    "per prompt: Pearson correlation, within the prompt, between judge score and "
    "value.",
    "Round ρ = mean over prompts of ρⱼ (both sides must vary); range −1 "
    "(against) to +1 (with the value).",
    "The judge score sⱼₖ is the judge's measured preference for answer k — the "
    "probability it picks k in",
    "the A-or-B comparisons, against the fixed reference answer or each duel "
    "opponent, averaged.",
    "(The score oracle's s is the value score itself.)",
])

divider(464)

# =========================== ROW 3 : selector gap g ==========================
r3 = 528
body += name_cell(r3, "selector gap", "g")
run3 = [('g', 'g', True), ('op', '='), ('g', 'k', True), ('op', '−'),
        ('g', 'p', True)]
p3, _ = render_run(run3, FX, r3, FORM_BASE)
body += p3


def id_g(top_y, lines, gx=545):
    # a wider, top-anchored identification block for the selector-gap row, so the
    # corrected pool-vs-alternative wording fits between the divider above and the
    # section rule below without crowding either.
    out = []
    for i, ln in enumerate(lines):
        out.append(f'<text x="{gx}" y="{top_y+i*20:.1f}" font-size="15" '
                   f'fill="{GRAY}" font-family="{FONT}">{esc(ln)}</text>')
    return out


body += id_g(482, [
    "kept mean k minus pool mean p.  p averages every candidate in the pool — the",
    "organism's own candidates plus any outside-source candidates, everything eligible",
    "to be kept and trained on. The alternative source's answer is shown to the judge",
    "as a comparison standard only: it is never in the pool and never kept.",
    "(k − q, kept mean minus the organism's own-candidate mean, is the separate",
    "training displacement.)    Forecast: g ≈ ρσ, prompt-averaged.",
])

# =============== THE MODEL THESE FEED : recurrence + closed forms ============
# section rule + header
body.append(f'<line x1="{NAME_X}" y1="600" x2="{W-60}" y2="600" '
            f'stroke="{INK}" stroke-width="1.4" opacity="0.55"/>')
body.append(f'<text x="{NAME_X}" y="636" font-size="22" font-weight="bold" '
            f'fill="{INK}" font-family="{FONT}">The model these feed</text>')
# the recurrence the closed forms solve (orientation, not a fitted result)
rec = (f'<text x="{NAME_X}" y="664" font-size="15" fill="{GRAY}" '
       f'font-family="{FONT}">'
       f'Each round: pool mean {var("p")} = (1−{var("u")}){var("q")} + '
       f'{var("u")}·{var("s")},  kept mean {var("k")} = {var("p")} + ρσ,  '
       f'next {var("v")} = {var("k")}.  The closed forms are its unclipped '
       f'solution.</text>')
body.append(rec)


def model_label(baseline, bold, note):
    s = [f'<text x="{NAME_X}" y="{baseline:.1f}" font-size="18" '
         f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
         f'{esc(bold)}</text>']
    if note:
        s.append(f'<text x="{NAME_X}" y="{baseline+20:.1f}" font-size="14.5" '
                 f'fill="{GRAY}" font-family="{FONT}">{esc(note)}</text>')
    return s


def model_id(baseline, text):
    return [f'<text x="{FX}" y="{baseline+26:.1f}" font-size="15" '
            f'fill="{GRAY}" font-family="{FONT}">{esc(text)}</text>']


# The three display equations are typeset by matplotlib mathtext (embed_math),
# placed so each equation's baseline-left origin sits at (FX, e#). Same fontsize
# and scale on every call, so all three render at one consistent size.
EQ_FS = 22.0   # mathtext point size (x-height matches the surrounding prose)

# ---- one round -----------------------------------------------------------
e1 = 710
body += model_label(e1, "one round", "")
body.append(embed_math(
    r"$v_{r+1} = \mathrm{clip}\left((1-u)\,v_r + u\,s + \rho\sigma,\ 0,\ 1\right)$",
    FX, e1, fontsize=EQ_FS))
body += model_id(e1, "outside-source share u at level s; σ and ρ are measured once, "
                     "at round 1.")

# ---- iterated (mixed pool) ----------------------------------------------
e2 = 774
body += model_label(e2, "iterated", "(mixed pool)")
body.append(embed_math(
    r"$v_r = v^{*} + (1-u)^{r}\,(v_0 - v^{*}) \quad \mathrm{with}\quad "
    r"v^{*} = s + \rho\sigma/u$",
    FX, e2, fontsize=EQ_FS))
body += model_id(e2, "geometric approach to the balance point v*, away from "
                     "the walls.")

# ---- self-only (u = 0) ---------------------------------------------------
e3 = 838
body += model_label(e3, "self-only", "(u = 0)")
body.append(embed_math(
    r"$v_r = v_0 + r\,\rho\sigma$",
    FX, e3, fontsize=EQ_FS))
body += model_id(e3, "a straight walk until a wall or the spread runs out.")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
       f'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>")

OUT = os.path.join(HERE, "state-variables.svg")
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}")

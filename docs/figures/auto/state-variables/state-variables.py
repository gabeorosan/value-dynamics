#!/usr/bin/env python3
"""The five per-round bookkeeping quantities of the selection loop, typeset as a
clean definitions panel — every part of every equation explained AT the equation,
so the reader never leaves a formula to hunt through prose. Replaces an unreadable
markdown bullet list, so the whole point is legible math typography.

The three per-round measurement rows (spread, agreement, selector gap) are laid out
in hand-built SVG with proper subscripts, italic symbols, a real radical bar for the
square root, and an overbar for the mean. The spread and agreement rows now show
BOTH the per-prompt estimator and the round-level aggregation (the committed mean
over prompts), each with a gray gloss naming its index set. The three display
equations in "The model these feed" are typeset with matplotlib's mathtext
(Computer Modern, fontset "cm") and embedded as inline vector glyph paths, so they
read as proper math while the figure stays a single self-contained SVG with no
external font or URL references; each term of each equation carries a tick down to a
gray label naming what that term is.

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
      ('sigma'[, idx])          big capital sigma with an index centered below
                                (idx defaults to 'k')
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
            idx = tok[1] if len(tok) > 1 else 'k'
            ss = base * 1.30
            out.append(T(cur, y, 'Σ', ss, color))
            w = _adv('Σ', ss, 0.60)
            out.append(T(cur + w / 2, y + base * 0.62, idx, base * 0.56,
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


# --- annotation helpers -------------------------------------------------------
def tick(cx, y_from, y_to, color=GRAY, width=1.0, opacity=0.6):
    return (f'<line x1="{cx:.1f}" y1="{y_from:.1f}" x2="{cx:.1f}" y2="{y_to:.1f}" '
            f'stroke="{color}" stroke-width="{width}" opacity="{opacity}"/>')


def term_label(cx, y_base, row_y, label, anchor="middle", size=13, color=GRAY):
    """A thin leader line from just below the equation term down to a BOXED gray
    label. The line terminates exactly on the box's top edge (touching it, not
    floating) so it is unambiguous which text connects to which term. The box is a
    light rounded rectangle, thin stroke in the same muted gray as the leader, with
    a near-white fill and ~5px padding around the text."""
    pad = 5.0
    w = _adv(label, size)
    if anchor == "end":
        tl, tr = cx - w, cx
    elif anchor == "start":
        tl, tr = cx, cx + w
    else:  # middle
        tl, tr = cx - w / 2.0, cx + w / 2.0
    box_top = row_y - size * 0.86 - pad
    box_bot = row_y + size * 0.32 + pad
    box_l, box_r = tl - pad, tr + pad
    return [
        tick(cx, y_base + 8, box_top, opacity=0.55),
        f'<rect x="{box_l:.1f}" y="{box_top:.1f}" width="{box_r-box_l:.1f}" '
        f'height="{box_bot-box_top:.1f}" rx="4" ry="4" fill="#ffffff" '
        f'fill-opacity="0.92" stroke="{GRAY}" stroke-width="1" opacity="0.6"/>',
        T(cx, row_y, label, size, color, anchor=anchor),
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
SYM_X = 300          # italic symbol glyph
FX = 402             # formula column start
FORM_BASE = 23
EQ_FS = 22.0         # mathtext point size (x-height matches the surrounding prose)

body = []

# ---- headline (descriptive, orientation only) ----
body.append(f'<text x="{NAME_X}" y="60" font-size="29" font-weight="bold" '
            f'fill="{INK}" font-family="{FONT}">The per-round measurements '
            f'and the model they feed</text>')


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


def name_cell(baseline, name, sym):
    s = [f'<text x="{NAME_X}" y="{baseline:.1f}" font-size="21" '
         f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
         f'{esc(name)}</text>']
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
body += name_cell(r1, "spread", "σ")
# per-prompt estimator (mathtext, same machinery and size as the model blocks)
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
body += name_cell(r2, "agreement", "ρ")
# whole per-prompt line as ONE mathtext embed (corr prefix + Pearson fraction) so
# the two = signs align; same machinery and size as the model blocks.
CORR = (r"$\rho_j = \mathrm{corr}(s_{j\cdot},\, x_{j\cdot}) = "
        r"\frac{\sum_k (s_{jk}-\bar{s}_j)(x_{jk}-\bar{x}_j)}"
        r"{\sqrt{\sum_k (s_{jk}-\bar{s}_j)^2 \cdot "
        r"\sum_k (x_{jk}-\bar{x}_j)^2}}$")
eq_c, _ = embed_math(CORR, FX, r2, EQ_FS)
body.append(eq_c)
# round-level aggregation:  rho = (1/|D|) Sigma_{j in D} rho_j  (proper |D| bars)
r2b = r2 + 76
eq_a, w_a = embed_math(r"$\rho = \frac{1}{\left|D\right|}\sum_{j\in D}\rho_j$",
                       FX, r2b, EQ_FS)
body.append(eq_a)
body += prose(FX + w_a + 28, r2b - 6, [
    "D = prompts where ρⱼ is defined (fewer than two candidates,",
    "or zero variance on either side, drop the prompt).",
], size=14, dy=18)
# the range, condensed — what sⱼₖ is and the two judging modes live in the symbol table
body += prose(FX, r2b + 44, [
    "Range −1 (the judge keeps against the value) to +1 (with it);",
    "score-oracle: s is x.",
])
divider(r2b + 90)

# =========================== ROW 3 : selector gap g ==========================
r3 = r2b + 136
body += name_cell(r3, "selector gap", "g")
GBASE = 30
# typeset g = k - p larger, with wide space around the minus so each glyph's tick
# and label sit clear of the other.
s_g, x_k0 = render_run([('g', 'g', True), ('op', '='), ('sp', 8)],
                       FX, r3, GBASE)
s_k, x_k1 = render_run([('g', 'k', True)], x_k0, r3, GBASE)
s_m, x_m1 = render_run([('sp', 60), ('op', '−'), ('sp', 60)], x_k1, r3, GBASE)
s_p, x_p1 = render_run([('g', 'p', True)], x_m1, r3, GBASE)
body += s_g + s_k + s_m + s_p
k_center = (x_k0 + x_k1) / 2
p_center = (x_m1 + x_p1) / 2
# tick + label under k (kept mean) and under p (pool mean), staggered rows
body += term_label(k_center, r3, r3 + 42, "mean value of the 2 kept candidates")
body += term_label(p_center, r3, r3 + 80, "mean value of the whole candidate pool")
# ONE residual line — the forecast; the pool/comparison-standard detail lives above
body += prose(FX, r3 + 106, [
    "forecast: g ≈ ρσ   (k − q, against the own-candidate mean, is the separate "
    "training displacement)",
])

# =============== THE MODEL THESE FEED : recurrence + closed forms ============
sec_y = r3 + 140
body.append(f'<line x1="{NAME_X}" y1="{sec_y:.1f}" x2="{W-60}" y2="{sec_y:.1f}" '
            f'stroke="{INK}" stroke-width="1.4" opacity="0.55"/>')
body.append(f'<text x="{NAME_X}" y="{sec_y+34:.1f}" font-size="22" '
            f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
            f'The model these feed</text>')
rec = (f'<text x="{NAME_X}" y="{sec_y+60:.1f}" font-size="15" fill="{GRAY}" '
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


# ---- one round -----------------------------------------------------------
# displayed with the real clamp bracket [ ... ]_0^1 ; per-term positions found by
# measuring balanced prefixes (\right. is a zero-width null delimiter).
e1 = sec_y + 150
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
iso1_2 = measure(r"$u\,s$", EQ_FS)
iso1_3 = measure(r"$\rho\sigma$", EQ_FS)
c1_1 = FX + R1_1 - iso1_1 / 2
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
body += prose(FX, e3 + 66, ["a straight walk until a wall or the spread runs out."],
              size=14)

# =============== THE STAGED-NOISE FORECAST (the stochastic rollout) ===========
# Typeset EXACTLY what rollout() in docs/figures/auto/spread-rollout-bakeoff/
# spread-rollout-bakeoff.py does (provenance scripts/analysis_trajectory_adjustments.py):
# deterministic mixing, clamped kept/generator/value/agreement updates with staged
# gaussian innovations, and a battery read-noise term added only to the reported value.
RIGHTEQ_X = 772        # right column: the innovation's distribution
NOTE_FS = EQ_FS * 0.82

sec2_y = e3 + 104
body.append(f'<line x1="{NAME_X}" y1="{sec2_y:.1f}" x2="{W-60}" y2="{sec2_y:.1f}" '
            f'stroke="{INK}" stroke-width="1.4" opacity="0.55"/>')
body.append(f'<text x="{NAME_X}" y="{sec2_y+34:.1f}" font-size="22" '
            f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
            f'The staged-noise forecast (the stochastic rollout)</text>')
body += prose(NAME_X, sec2_y + 58, [
    "Each ε's SD is the pooled leave-one-condition-out residual of that stage, rebuilt "
    "from the committed records — no invented",
    "noise parameters; σ stays at its round-1 value.  q = the generator (own-candidate) "
    "mean; v = the value; v̂ = the reported value.",
])


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


f0 = sec2_y + 120
GAP = 70

body += stoch_row(
    f0, "pool mean",
    r"$p_r = (1-u)\,q_r + u\,s$",
    note_text="(deterministic mixing, as above)")

body += stoch_row(
    f0 + GAP, "kept mean",
    r"$k_r = \left[\,p_r + \rho_r\,\sigma + \varepsilon_g\,\right]_0^1$",
    note_math=r"$\varepsilon_g \sim N(0,\ s_g)$",
    eps_prefix=r"k_r = \left[\,p_r + \rho_r\,\sigma + \varepsilon_g",
    eps_iso=r"\varepsilon_g",
    eps_label="innovation in the judge's step (selector-gap residual)")

body += stoch_row(
    f0 + 2 * GAP, "generator",
    r"$q_{r+1} = \left[\,q_r + (k_r - q_r) + \varepsilon_q\,\right]_0^1$",
    note_math=r"$\varepsilon_q \sim N(0,\ s_q)$",
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
    note_math=r"$\varepsilon_\rho \sim N(0,\ s_\rho)$",
    eps_prefix=r"\rho_{r+1} = \left[\,\rho_r + \varepsilon_\rho",
    eps_iso=r"\varepsilon_\rho",
    eps_label="agreement drifts as a random walk around persistence")

body += stoch_row(
    f0 + 5 * GAP, "observed",
    r"$\hat{v}_r = \left[\,v_r + \varepsilon_{\mathrm{obs}}\,\right]_0^1$",
    note_math=r"$\varepsilon_{\mathrm{obs}} \sim N\!\left(0,\ \sqrt{v_r(1-v_r)/n}\right)$",
    eps_prefix=r"\hat{v}_r = \left[\,v_r + \varepsilon_{\mathrm{obs}}",
    eps_iso=r"\varepsilon_{\mathrm{obs}}",
    eps_label="battery read noise, added ONLY to the reported value "
              "(n = the battery's generation count)")

# =============== SYMBOL TABLE (every quantity on the figure defined) ==========
# So no symbol appears anywhere above without a definition somewhere on the page —
# including the round index r. Terse restatements of the row/gloss definitions,
# collected in one place for reference.
sym_top = f0 + 5 * GAP + 62
body.append(f'<line x1="{NAME_X}" y1="{sym_top:.1f}" x2="{W-60}" y2="{sym_top:.1f}" '
            f'stroke="{INK}" stroke-width="1.4" opacity="0.55"/>')
body.append(f'<text x="{NAME_X}" y="{sym_top+30:.1f}" font-size="20" '
            f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
            f'Symbols — every quantity on this figure</text>')

# (symbol-with-unicode-subscripts, definition)
SYMBOLS = [
    ("r", "round index (1, 2, …)"),
    ("vᵣ", "behavioral value at round r"),
    ("v₀", "starting value (round 0)"),
    ("v*", "balance point (fixed point of the mixed pool)"),
    ("v̂ᵣ", "reported / measured value"),
    ("u", "outside-source share of the pool"),
    ("s", "outside source's mean value level"),
    ("qᵣ", "organism's own-candidate mean"),
    ("pᵣ", "pool mean = (1−u)qᵣ + u·s"),
    ("kᵣ", "kept mean (mean value of the 2 kept)"),
    ("σ", "spread — per-prompt value SD, meaned"),
    ("ρᵣ", "agreement — judge×value correlation"),
    ("gᵣ", "selector gap = kᵣ − pᵣ"),
    ("J", "the round's prompts (count), equal weight"),
    ("D", "prompts where ρⱼ is defined"),
    ("nⱼ", "candidates in prompt j's pool"),
    ("xⱼₖ", "value score of candidate k, prompt j"),
    ("sⱼₖ", "judge score of candidate k, prompt j"),
    ("n", "the battery's generation count"),
    ("εg, εq, ερ", "staged innovations (SD sg, sq, sρ)"),
    ("εobs", "read noise (SD √(vᵣ(1−vᵣ)/n))"),
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
        f'<tspan font-style="italic" font-weight="bold" fill="{INK}">{esc(symb)}</tspan>'
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

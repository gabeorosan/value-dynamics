#!/usr/bin/env python3
"""The five per-round bookkeeping quantities of the selection loop, typeset as a
clean definitions panel. Replaces an unreadable markdown bullet list, so the whole
point is legible math typography in hand-built SVG: proper subscripts (small
lowered glyphs), italic symbols, a real radical bar for the square root, and an
overbar for the mean.

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
W, H = 1200, 760
NAME_X = 66          # left column: bold name
SYM_X = 300          # italic symbol glyph
FX = 402             # formula column start
RIGHT_X = 748        # right identification column (simple rows)
FORM_BASE = 23

body = []

# ---- headline (descriptive, orientation only) ----
body.append(f'<text x="{NAME_X}" y="60" font-size="30" font-weight="bold" '
            f'fill="{INK}" font-family="{FONT}">The five per-round '
            f'measurements</text>')

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
r1 = 196
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

divider(282)

# =========================== ROW 2 : agreement rho ===========================
r2 = 340
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
    "Measured per round; in practice a property of the judge × alt-source × "
    "answer-source condition.",
])

divider(426)

# =========================== ROW 3 : selector gap g ==========================
r3 = 484
body += name_cell(r3, "selector gap", "g")
run3 = [('g', 'g', True), ('op', '='), ('g', 'k', True), ('op', '−'),
        ('g', 'p', True)]
p3, _ = render_run(run3, FX, r3, FORM_BASE)
body += p3
body += id_right(r3, ["kept mean minus offered-pool mean", "(both round means)."])

divider(524)

# ==================== ROW 4 : training displacement ==========================
r4 = 578
body += name_cell(r4, "training displacement", "")
run4 = [('g', 'k', True), ('op', '−'), ('g', 'q', True)]
p4, _ = render_run(run4, FX, r4, FORM_BASE)
body += p4
body += id_right(r4, ["kept mean minus the organism's own",
                      "generated mean q."])

divider(618)

# ==================== ROW 5 : behavioral pull ================================
r5 = 672
body += name_cell(r5, "behavioral pull", "")
run5 = [('g', 'k', True), ('op', '−'), ('g', 'v', True)]
p5, _ = render_run(run5, FX, r5, FORM_BASE)
body += p5
body += id_right(r5, ["kept mean minus the behavioral", "value v."])

divider(710)

# ---- foot line (identification, no takeaway) ----
foot_pre, fcur = render_run(
    [('g', 'forecast:', False)], NAME_X, 740, 16)
body.append(f'<text x="{NAME_X}" y="740" font-size="16" fill="{GRAY}" '
            f'font-style="italic" font-family="{FONT}">forecast:</text>')
run_f = [('g', 'g', True), ('op', '≈'), ('g', 'ρ', True),
         ('g', 'σ', True)]
pf, fend = render_run(run_f, NAME_X + 78, 743, 19, INK)
body += pf
body.append(f'<text x="{fend+8:.1f}" y="740" font-size="16" fill="{GRAY}" '
            f'font-family="{FONT}">with ρ and σ the round’s '
            f'prompt-averaged values.</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H}" fill="white"/>\n'
       + "\n".join(body) + "\n</svg>")

OUT = os.path.join(HERE, "state-variables.svg")
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}")

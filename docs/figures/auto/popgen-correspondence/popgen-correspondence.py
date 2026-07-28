#!/usr/bin/env python3
"""Draft figure: the term-by-term correspondence between classical selection
theory and the language-model judging loop.

Concept figure with two checked numbers. Three rows (selection differential,
heritability, response to selection), each read left to right as
theory term -> the quantity it is in this loop. The measurement recipes for
spread and agreement are NOT repeated here: the state-variables figure
(docs/figures/auto/state-variables/) owns them and is shown earlier in the
same thread. This figure was cut from 541 words of text to fit the density of
the rest of the set (median 166 words); it prints its own word count on every
run and refuses to write a file over the budget.

Two data numbers appear, both recomputed here from the result files:

  * R-squared of the spread-times-agreement forecast against the realized
    selector gap, on the combined 367-round corpus;
  * mean absolute error of the parameter-free kept-mean rule against the
    next round's measured value, 340 rounds, against the no-change baseline.

Style reference: docs/figures/make_figures.py (Owain Evans-lab style -- white
background, headline sentence, boxes with verbatim wording, bold arrows, real
data with fat labels). Helpers esc()/wrap() are copied, not imported, so this
file runs standalone:  python3 popgen-correspondence.py
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
WORD_BUDGET = 140      # the less-dense third of the figure set sits at or under 137


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


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def arrow(x1, y1, x2, y2, sw=4, color=INK, marker="arr"):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#{marker})"/>')


DEFS = f'''<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{BLUE}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker></defs>'''


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
        _EXTENTS.append((x + wdt * SAFETY, " ".join(_plain(w) for w in ln)))
        svg.append(f'<text x="{x}" y="{y + i * size * lh:.1f}" font-size="{size}" '
                   f'fill="{color}" font-weight="{weight}" font-style="{style}" '
                   f'text-anchor="{anchor}" font-family="{FONT}">'
                   f'{" ".join(_tspan(w) for w in ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


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
        "no_change": sum(abs(r["value"] - (r["value"] + r["drift"]))
                         for r in recs) / len(recs),
        "n_runs": len({(r["source"], r["cond"], r["seed"]) for r in recs}),
        "n_conditions": len({(r["organism"], r["axis"], r["cond"]) for r in recs}),
    }
    anchor = json.load(open(LADDER))["anchors"]["one_step_kept_mean_pooled_mae_340"]
    resp["ladder_anchor"] = anchor["computed"]
    return gap, resp


# ---- the figure -----------------------------------------------------------
# One canvas width shared with model-recurrence.svg and state-variables.svg, so
# the type sizes below (18px body, 30px headline) are the same physical size as
# theirs when the figures sit next to each other.
W = 1240
LX, RX = 48, 1192
COL_A, COL_A_W = 48, 300
ARROW_X0, ARROW_X1 = 360, 404
COL_B, COL_B_W = 428, 764

S_HEAD = 30      # headline
S_SUB = 18       # subtitle / column gloss
S_COLHEAD = 21   # column header
S_TITLE = 21     # row title
S_BODY = 18      # row body
S_TAG = 16       # readout tag
S_NUM = 34       # readout number
BODY_LH = 1.36   # line height inside boxes


def build(gap, resp):
    s = []
    r2_txt = f"R² {gap['r2']:.2f}"
    mae_txt = f"MAE {resp['mae']:.3f}"

    # ---------------- header ----------------
    t, y = para(LX, 40, "Every term of the breeder's equation has a measured "
                        "counterpart in the judging loop", S_HEAD, RX - LX,
                INK, "bold", lh=1.16)
    s.append(t)
    t, y = para(LX, y + 8,
                "Borrowed equations, not borrowed biology: the same accounting of "
                "means applies.", S_SUB, RX - LX, GRAY)
    s.append(t)
    y += 10
    s.append(f'<line x1="{LX}" y1="{y:.0f}" x2="{RX}" y2="{y:.0f}" stroke="{GRAY}" '
             f'stroke-width="1.5" opacity="0.45"/>')

    # ---------------- column headers ----------------
    hy = y + 28
    t, sub_end = para(COL_A, hy, "In selection theory: {i:R} = {i:h}² × {i:S}",
                      S_COLHEAD, COL_A_W + 120, INK, "bold")
    s.append(t)
    t, e = para(COL_B, hy, "In this judging loop", S_COLHEAD, COL_B_W, BLUE, "bold")
    s.append(t)
    sub_end = max(sub_end, e)

    rows = [
        dict(a="Selection differential {i:S}",
             b="The selector gap",
             body="Mean value score of the two answers the judge keeps, minus the "
                  "mean over all six candidates in that prompt's pool."),
        dict(a="Heritability {i:h}²",
             b="What the fine-tune carries over",
             body="The kept answers become the next fine-tune's training data: "
                  "assumed to carry, never fitted here."),
        dict(a="Response to selection {i:R}",
             b="The change in measured value",
             body="How far the organism's own value moves after that fine-tune."),
    ]

    ry = sub_end + 14
    pad = 16
    # One height for all three rows: the correspondence reads as a grid, so a
    # row that happens to need one line fewer should not shrink its box.
    box_h = max(pad + para_height(r["b"], S_TITLE, COL_B_W - 2 * pad,
                                  weight="bold", lh=1.3)
                + 8 + para_height(r["body"], S_BODY, COL_B_W - 2 * pad, lh=BODY_LH)
                + pad - 4 for r in rows)
    for row in rows:
        a_h = para_height(row["a"], S_TITLE, COL_A_W - 2 * pad,
                          weight="bold", lh=1.3)
        a_top = ry + (box_h - a_h) / 2 + S_TITLE * 0.95

        s.append(box(COL_A, ry, COL_A_W, box_h, "white", GRAY, 2.5))
        t, _ = para(COL_A + pad, a_top, row["a"], S_TITLE, COL_A_W - 2 * pad,
                    INK, "bold", lh=1.3)
        s.append(t)

        s.append(box(COL_B, ry, COL_B_W, box_h, ASST_FILL, BLUE, 2.5))
        # The boxes share one height, so a row whose body is a line shorter
        # centres its block instead of hanging from the top edge.
        b_block = (para_height(row["b"], S_TITLE, COL_B_W - 2 * pad,
                               weight="bold", lh=1.3) + 10
                   + para_height(row["body"], S_BODY, COL_B_W - 2 * pad,
                                 lh=BODY_LH))
        b_top = ry + (box_h - b_block) / 2 + S_TITLE * 0.95
        t, e = para(COL_B + pad, b_top, row["b"], S_TITLE,
                    COL_B_W - 2 * pad, BLUE, "bold", lh=1.3)
        s.append(t)
        t, _ = para(COL_B + pad, e + 10, row["body"], S_BODY,
                    COL_B_W - 2 * pad, INK, lh=BODY_LH)
        s.append(t)

        mid = ry + box_h / 2
        s.append(arrow(ARROW_X0, mid, ARROW_X1, mid, 4.5, INK))
        ry += box_h + 14

    # ---------------- the two checks ----------------
    ry += 8
    chips = [
        (r2_txt, "differential row, checked",
         "of the realized gap, from spread × agreement, "
         f"{gap['n']} judge-scored rounds"),
        (mae_txt, "response row, checked",
         "of the kept-mean rule against the next measured value, "
         f"{resp['n']} rounds; no-change baseline {resp['no_change']:.3f}"),
    ]
    gapx = 28
    cw = (RX - LX - gapx) / 2
    chip_h = 0
    chip_svg = []
    for i, (num, tag, bodytxt) in enumerate(chips):
        cx = LX + i * (cw + gapx)
        # number and its tag share a baseline, so the readout is two blocks tall
        # instead of three — the figure's height is what pushed it out of
        # landscape before.
        t_num, _ = para(cx + 20, ry + 48, num, S_NUM, cw - 40, INK, "bold")
        tag_x = cx + 20 + measure(num, S_NUM, bold=True) + 14
        t_tag, _ = para(tag_x, ry + 48, tag, S_TAG, cw - (tag_x - cx) - 20,
                        GREEN, "bold")
        t_body, e = para(cx + 20, ry + 76, bodytxt, S_BODY, cw - 40, INK,
                          lh=BODY_LH)
        chip_h = max(chip_h, e - ry + 2)
        chip_svg.append((cx, t_tag, t_num, t_body))
    for cx, t_tag, t_num, t_body in chip_svg:
        s.append(box(cx, ry, cw, chip_h, KEY_FILL, GREEN, 2.5))
        s.append(t_tag)
        s.append(t_num)
        s.append(t_body)
    ry += chip_h
    return "\n".join(s), ry


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
    body, end_y = build(gap, resp)
    height = int(end_y + 22)

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

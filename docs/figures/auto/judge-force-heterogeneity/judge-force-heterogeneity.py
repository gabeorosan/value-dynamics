#!/usr/bin/env python3
"""Draft figure: the judge-swap selection force is pool-heterogeneous.

Strict inversion screen on the OLMo-3-7B-Instruct conservative organism
(v10_judge_topup/rung_20). Two freshly sampled 24-prompt x 6-candidate
pools from the SAME organism: the force the judge swap exerts on the
kept (trained-on) set differs eight-fold between them, and an offline
re-simulation of the selection operator on the saved per-candidate
score tables shows the heterogeneity belongs to the pools, not the
operator.

Style follows docs/figures/make_figures.py (Owain Evans-lab style:
white background, big headline sentence, verbatim-text boxes, real data
with fat labels). Regenerate with:  python3 judge-force-heterogeneity.py

Data provenance: the two-pool screen ran on Colab; its per-candidate
JSON lives on Drive, not in the repo. The summary numbers plotted here
are the ones recorded in docs/PLAN.md (decision log 2026-07-11 ~14:00)
and docs/STATE.md (Recent changes 2026-07-11 ~14:15): separations
+0.021 / +0.167, conservative kept gap negative in both pools, operator
re-simulation max +0.042 on pool 101 vs 0.08-0.17 on pool 202, two-pool
mean 0.094, organism held-out judge preference 0.426 -> 0.880.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
PURPLE = "#8a5a9e"     # extra-arm color used by make_figures.py fig 4/7
USER_FILL = "#cfe0f1"  # chat user box
ASST_FILL = "#eaf1f8"  # chat assistant box
DOC_FILL = "#fdf6e8"   # document / essay box
KEY_FILL = "#eef5ee"   # highlighted takeaway box

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


def rich_text(x, y, segments, size, width, lh=1.38, weight="normal"):
    """segments: list of (text, color, bold). Wraps across segments."""
    words = []
    for text, color, bold in segments:
        for w in text.split():
            words.append((w, color, bold))
    out, line, count = [], [], 0
    for w, color, bold in words:
        if count + len(w) + 1 > width and line:
            out.append(line)
            line, count = [], 0
        line.append((w, color, bold))
        count += len(w) + 1
    if line:
        out.append(line)
    svg = []
    for i, ln in enumerate(out):
        tspans = "".join(
            f'<tspan fill="{c}" font-weight="{"bold" if b else weight}">{esc(w)} </tspan>'
            for w, c, b in ln)
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" '
                   f'font-size="{size}">{tspans}</text>')
    return "\n".join(svg), y + len(out) * size * lh


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.38):
    return rich_text(x, y, [(text, color, weight == "bold")], size, width, lh)


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


DEFS = f'''<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ---- the data (see module docstring for provenance) ----
# kept gap = kept-set mean gamble rate minus pool mean, per frozen judge
POOLS = [
    # name, color, base-judge kept gap, conservative-judge kept gap
    ("pool 101", PURPLE, -0.104, -0.125),   # separation +0.021
    ("pool 202", RED,    -0.090, -0.257),   # separation +0.167
]
# separation (= base kept gap minus conservative kept gap) under each
# re-simulated selection operator, offline on the saved score tables
OPERATORS = [
    # label, deployed?, pool 101, pool 202
    ("keep top 1 of 6",              False, 0.000, 0.125),
    ("keep top 2 of 6 — deployed",   True,  0.021, 0.167),
    ("keep top 3 of 6",              False, 0.042, 0.083),
    ("softmax, temperature 0.02",    False, 0.022, 0.173),
    ("softmax, temperature 0.05",    False, 0.027, 0.170),
    ("softmax, temperature 0.10",    False, 0.013, 0.131),
]
JUDGE_PREF_ORGANISM = 0.880   # held-out pairwise preference for cautious answers
JUDGE_PREF_BASE = 0.426
TWO_POOL_MEAN_SEP = 0.094


def main():
    b = []
    W = 1380

    # ---- headline ----
    t, _ = text_block(W // 2, 50, "The same judge, a different pool: the judge-swap", 33, 78, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 91, "selection force is a property of the sampled candidates", 33, 78, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 126, "Strict inversion screen, OLMo-3-7B-Instruct conservative organism (v10 judge top-up, rung 20). Two freshly sampled 24-prompt × 6-candidate pools, identical organism, prompt bank and settings — the force the judge swap exerts differs eight-fold between them.", 17.5, 126, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" '))  # anchor every wrapped line

    # ==== setup strip ====
    sy = 196
    b.append(box(60, sy, 800, 205, "white", INK, 2.5))
    t, _ = text_block(78, sy + 28, "One screen round", 18, 60, weight="bold")
    b.append(t)
    t, _ = text_block(78, sy + 56,
                      "The organism samples 6 candidate answers for each of 24 order-balanced two-option gamble prompts "
                      "(strict end-anchored “Final: A/B” parse; invalid candidates replenished). Each frozen judge scores every "
                      "candidate against the same fixed cautious reference sentence, and the top 2 of 6 per prompt become the "
                      "kept (trained-on) set. Kept gap = kept-set mean gamble rate minus pool mean. The judge-swap force "
                      "(“separation”) = base judge’s kept gap minus conservative judge’s kept gap.", 15.5, 96)
    b.append(t)

    b.append(box(880, sy, 440, 260, DOC_FILL, INK, 2.5))
    t, _ = text_block(898, sy + 28, "The two frozen judges", 18, 50, weight="bold")
    b.append(t)
    t, y2 = rich_text(898, sy + 56, [
        ("Conservative organism", BLUE, True),
        (f"— held-out pairwise preference for cautious answers {JUDGE_PREF_ORGANISM:.3f}. ", INK, False),
        ("Plain base model", GREEN, True),
        (f"— {JUDGE_PREF_BASE:.3f}. A +0.45 preference difference between the judges.", INK, False),
    ], 15.5, 52)
    b.append(t)
    t, _ = rich_text(898, y2 + 10, [
        ("Candidate score = order-averaged forced single-token p(judge prefers candidate over the reference) under the system prompt ", INK, False),
        ("“You are evaluating answers.”", INK, True),
    ], 15.5, 52)
    b.append(t)

    # ==== panel 1: kept gaps per judge, per pool ====
    t, _ = text_block(60, 496, "The judges’ kept gaps on each fresh pool", 20, 44, weight="bold")
    b.append(t)
    # judge legend
    ly = 528
    b.append(f'<rect x="66" y="{ly - 12}" width="26" height="14" rx="3" fill="{GREEN}" fill-opacity="0.75"/>')
    t, _ = text_block(100, ly, "plain base-model judge selects", 15.5, 60, INK)
    b.append(t)
    b.append(f'<rect x="66" y="{ly + 12}" width="26" height="14" rx="3" fill="{BLUE}" fill-opacity="0.75"/>')
    t, _ = text_block(100, ly + 24, "conservative organism judge selects", 15.5, 60, INK)
    b.append(t)

    px, pw, py, ph = 150, 380, 588, 280
    ymax, ymin = 0.02, -0.30

    def Y(v):
        return py + ph * (ymax - v) / (ymax - ymin)

    for v in (0.0, -0.1, -0.2, -0.3):
        yy = Y(v)
        w_ = 2.5 if v == 0.0 else 1
        col = INK if v == 0.0 else "#e4e4e0"
        b.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px + pw}" y2="{yy:.1f}" stroke="{col}" stroke-width="{w_}"/>')
        b.append(f'<text x="{px - 10}" y="{yy + 5:.1f}" text-anchor="end" font-size="15" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    b.append(f'<text x="{px - 58}" y="{py + ph / 2}" font-size="15" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {px - 58} {py + ph / 2})" text-anchor="middle">kept gap: kept-set gamble rate minus pool mean</text>')

    for gi, (name, pcolor, base_gap, cons_gap) in enumerate(POOLS):
        cx = px + pw * (0.26 + 0.48 * gi)
        for off, val, jcolor in ((-50, base_gap, GREEN), (6, cons_gap, BLUE)):
            y0b, y1b = sorted((Y(0), Y(val)))
            b.append(f'<rect x="{cx + off:.1f}" y="{y0b:.1f}" width="44" height="{max(y1b - y0b, 2):.1f}" rx="4" '
                     f'fill="{jcolor}" fill-opacity="0.75"/>')
            b.append(f'<text x="{cx + off + 22:.1f}" y="{Y(val) + 20:.1f}" text-anchor="middle" font-size="14.5" '
                     f'font-weight="bold" fill="{jcolor}" font-family="{FONT}">−{abs(val):.3f}</text>')
        # separation bracket to the right of the group
        bx = cx + 62
        yb, yc = Y(base_gap), Y(cons_gap)
        b.append(f'<line x1="{bx}" y1="{yb:.1f}" x2="{bx}" y2="{yc:.1f}" stroke="{pcolor}" stroke-width="3"/>')
        for yy in (yb, yc):
            b.append(f'<line x1="{bx - 5}" y1="{yy:.1f}" x2="{bx + 5}" y2="{yy:.1f}" stroke="{pcolor}" stroke-width="3"/>')
        sep = base_gap - cons_gap
        b.append(f'<text x="{bx + 10}" y="{(yb + yc) / 2 + 1:.1f}" font-size="17" font-weight="bold" '
                 f'fill="{pcolor}" font-family="{FONT}">+{sep:.3f}</text>')
        b.append(f'<text x="{bx + 10}" y="{(yb + yc) / 2 + 19:.1f}" font-size="12.5" '
                 f'fill="{pcolor}" font-family="{FONT}">swap force</text>')
        # pool label under the group
        b.append(f'<text x="{cx - 3:.1f}" y="{py + ph + 28}" text-anchor="middle" font-size="17" '
                 f'font-weight="bold" fill="{pcolor}" font-family="{FONT}">{esc(name)}</text>')

    t, _ = text_block(60, py + ph + 66,
                      "Both kept gaps are negative — each judge’s kept set holds fewer gamble answers than the pool average "
                      "(pool composition ≈ 27% gamble candidates in both pools). On pool 101 the two judges nearly agree; on "
                      "pool 202 the conservative judge pulls the kept set far below where the base judge leaves it.", 15, 82, GRAY)
    b.append(t)

    # ==== panel 2: operator re-simulation ====
    t, _ = text_block(760, 496, "Swapping the selection operator does not change the story", 20, 62, weight="bold")
    b.append(t)
    t, _ = text_block(760, 524, "Offline re-simulation of each operator on the saved per-candidate score tables:", 15.5, 82, GRAY)
    b.append(t)
    # pool legend
    ly2 = 556
    b.append(f'<circle cx="774" cy="{ly2 - 5}" r="7" fill="{PURPLE}"/>')
    t, _ = text_block(790, ly2, "pool 101", 15.5, 40, INK, "bold")
    b.append(t)
    b.append(f'<circle cx="904" cy="{ly2 - 5}" r="7" fill="{RED}"/>')
    t, _ = text_block(920, ly2, "pool 202", 15.5, 40, INK, "bold")
    b.append(t)

    px2, pw2 = 1010, 310
    rows_y0, rstep = 640, 40
    nrows = len(OPERATORS)
    xmin, xmax = -0.01, 0.20

    def X(v):
        return px2 + pw2 * (v - xmin) / (xmax - xmin)

    plot_top, plot_bot = rows_y0 - 22, rows_y0 + (nrows - 1) * rstep + 22
    for v in (0.0, 0.05, 0.10, 0.15, 0.20):
        xx = X(v)
        col = INK if v == 0.0 else "#e4e4e0"
        w_ = 2 if v == 0.0 else 1
        b.append(f'<line x1="{xx:.1f}" y1="{plot_top}" x2="{xx:.1f}" y2="{plot_bot}" stroke="{col}" stroke-width="{w_}"/>')
        b.append(f'<text x="{xx:.1f}" y="{plot_bot + 20}" text-anchor="middle" font-size="14" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    # original per-pool launch threshold
    xt = X(0.10)
    b.append(f'<line x1="{xt:.1f}" y1="{plot_top - 26}" x2="{xt:.1f}" y2="{plot_bot}" stroke="{INK}" stroke-width="2" stroke-dasharray="7 5"/>')
    b.append(f'<text x="{xt:.1f}" y="{plot_top - 34}" text-anchor="middle" font-size="13.5" fill="{INK}" font-family="{FONT}">original per-pool launch bar ≥ 0.10</text>')

    for ri, (label, deployed, v101, v202) in enumerate(OPERATORS):
        yy = rows_y0 + ri * rstep
        lw = "bold" if deployed else "normal"
        b.append(f'<text x="{px2 - 14}" y="{yy + 5}" text-anchor="end" font-size="15" font-weight="{lw}" '
                 f'fill="{INK}" font-family="{FONT}">{esc(label)}</text>')
        b.append(f'<line x1="{X(v101):.1f}" y1="{yy}" x2="{X(v202):.1f}" y2="{yy}" stroke="{GRAY}" stroke-width="2" stroke-opacity="0.55"/>')
        r = 8 if deployed else 6.5
        b.append(f'<circle cx="{X(v101):.1f}" cy="{yy}" r="{r}" fill="{PURPLE}" stroke="white" stroke-width="1.5"/>')
        b.append(f'<circle cx="{X(v202):.1f}" cy="{yy}" r="{r}" fill="{RED}" stroke="white" stroke-width="1.5"/>')
        if deployed:
            b.append(f'<text x="{X(v101):.1f}" y="{yy - 13}" text-anchor="middle" font-size="13.5" font-weight="bold" '
                     f'fill="{PURPLE}" font-family="{FONT}">+{v101:.3f}</text>')
            b.append(f'<text x="{X(v202):.1f}" y="{yy - 13}" text-anchor="middle" font-size="13.5" font-weight="bold" '
                     f'fill="{RED}" font-family="{FONT}">+{v202:.3f}</text>')
    b.append(f'<text x="{px2 + pw2 / 2}" y="{plot_bot + 46}" text-anchor="middle" font-size="15" fill="{INK}" '
             f'font-family="{FONT}">judge-swap force (separation) under the re-simulated operator</text>')

    t, _ = rich_text(760, plot_bot + 78, [
        ("Pool 202 expresses the force under every operator (+0.083 to +0.173, deployed top-2 near-optimal); ", RED, True),
        ("pool 101 under none (at most +0.042). ", PURPLE, True),
        ("The heterogeneity is carried by the sampled candidate pools, not by the selection operator.", INK, False),
    ], 15, 78)
    b.append(t)

    # ==== takeaway: the decision consequence ====
    ky = 1030
    b.append(box(60, ky, W - 120, 158, KEY_FILL, INK, 2.5))
    t, _ = rich_text(80, ky + 32, [
        ("Decision consequence: ", INK, True),
        ("the launch rule for the judge-swap loop grid (K2) was revised prospectively (PLAN 2026-07-11 ~14:00), before any further pools were observed — from “every pool’s separation ≥ 0.10” to “mean separation over ≥ 5 fresh pools ≥ 0.10, with ≥ 60% of pools ≥ 0.05 and every pool’s conservative kept gap negative” — because the deployed loop averages over many fresh pools per rollout, so the launch-relevant quantity is the mean force with sign consistency. ", INK, False),
        (f"On the two known pools the revised rule still fails (mean separation {TWO_POOL_MEAN_SEP:.3f}); a 5-pool screen is running and decides.", RED, True),
    ], 18, 132)
    b.append(t)

    return svg_doc(W, ky + 200, "\n".join(b))


if __name__ == "__main__":
    out = os.path.join(HERE, "judge-force-heterogeneity.svg")
    with open(out, "w") as f:
        f.write(main())
    print("wrote", out)

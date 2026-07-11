#!/usr/bin/env python3
"""Draft figure: the deployable judge-swap selection force, mapped on five
fresh candidate pools (the completed strict 5-pool inversion screen).

Strict inversion screen on the OLMo-3-7B-Instruct conservative organism
(run v10_judge_topup, rung_20; held-out cautious-judge preference 0.880).
Five freshly sampled 24-prompt x 6-candidate pools from the SAME organism:
the conservative judge's kept set is more cautious than the pool average
in every pool (the trained-in sign replicates 5/5), while the judge-swap
force ("separation") swings pool to pool — three pools near +0.167, one
near zero, one slightly negative. The negative pool (505) is carried by
the BASE judge keeping the most cautious kept set of the whole screen
there, not by the conservative taste weakening.

Style follows docs/figures/make_figures.py (Owain Evans-lab style: white
background, big headline sentence, verbatim-text boxes, real data with
fat labels). Regenerate with:  python3 judge-force-five-pools.py

Data: experiments/kaggle/kaggle_k2_olmo_inversion/screen_attestation.json
(key per_pool; pool seed order 101/202/303/404/505). The generator reads
that file when the repo layout is present and falls back to an embedded
verbatim copy of the same numbers so it stays runnable standalone.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ATTEST = os.path.join(HERE, "..", "..", "..", "..", "experiments", "kaggle",
                      "kaggle_k2_olmo_inversion", "screen_attestation.json")

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


# ---- embedded fallback: verbatim per_pool numbers from the attestation ----
FALLBACK = {
    "pool_seeds": [101, 202, 303, 404, 505],
    "base_gaps": [-0.10416666666666666, -0.09027777777777779,
                  -0.048611111111111105, -0.04166666666666666,
                  -0.18055555555555558],
    "cons_gaps": [-0.12499999999999997, -0.2569444444444445,
                  -0.21527777777777776, -0.20833333333333334,
                  -0.1597222222222222],
    "mean_sep": 0.1,
    "sd_sep": 0.0924680875882173,
}


def load_data():
    try:
        a = json.load(open(ATTEST))
        return {
            "pool_seeds": a["fresh_pool_seeds"],
            "base_gaps": [p["base_gap"] for p in a["per_pool"]],
            "cons_gaps": [p["conservative_gap"] for p in a["per_pool"]],
            "mean_sep": a["mean_separation"],
            "sd_sep": a["sd_separation"],
        }
    except (OSError, KeyError, ValueError):
        return FALLBACK


JUDGE_PREF_ORGANISM = 0.880   # held-out pairwise preference for cautious answers
JUDGE_PREF_BASE = 0.426


def main():
    d = load_data()
    seps = [bg - cg for bg, cg in zip(d["base_gaps"], d["cons_gaps"])]
    mean_sep, sd_sep = d["mean_sep"], d["sd_sep"]
    OUTLIER = 4  # index of pool 505, the negative-separation pool

    b = []
    W = 1380

    # ==== headline ====
    t, _ = text_block(W // 2, 50, "One judge, five fresh candidate pools: the cautious taste", 33, 80, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 91, "never flips sign, but its selection force swings pool to pool", 33, 80, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 126,
                      "Completed strict 5-pool inversion screen, OLMo-3-7B-Instruct conservative organism (run v10 judge top-up, rung 20). "
                      "Five freshly sampled 24-prompt × 6-candidate pools — identical organism, prompt bank and settings.",
                      17.5, 128, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" '))  # anchor every wrapped line

    # ==== setup strip ====
    sy = 192
    b.append(box(60, sy, 800, 214, "white", INK, 2.5))
    t, _ = text_block(78, sy + 28, "One pool, one force measurement", 18, 60, weight="bold")
    b.append(t)
    t, _ = text_block(78, sy + 56,
                      "The organism samples 6 candidate answers for each of 24 order-balanced two-option gamble prompts "
                      "(“Option A: $X for sure. Option B: a p% chance of $Y…”; strict end-anchored “Final: A/B” parse, invalid "
                      "candidates replenished). Each frozen judge keeps the top 2 of 6 per prompt, scoring every candidate "
                      "against the same fixed cautious reference sentence. Kept gap = kept-set mean risk-axis value minus pool "
                      "mean (negative = kept set more cautious than the pool). Separation = base judge’s kept gap minus "
                      "conservative judge’s kept gap (positive = the conservative judge selects more cautiously).", 15.5, 96)
    b.append(t)

    b.append(box(880, sy, 440, 214, DOC_FILL, INK, 2.5))
    t, _ = text_block(898, sy + 28, "The two frozen judges", 18, 50, weight="bold")
    b.append(t)
    t, y2 = rich_text(898, sy + 56, [
        ("Conservative organism", BLUE, True),
        (f"— held-out pairwise preference for cautious answers {JUDGE_PREF_ORGANISM:.3f}. ", INK, False),
        ("Plain base model", GREEN, True),
        (f"— {JUDGE_PREF_BASE:.3f}. A +0.45 preference difference between the judges.", INK, False),
    ], 15.5, 52)
    b.append(t)
    t, _ = text_block(898, y2 + 10,
                      "Candidate score = order-averaged forced single-token p(judge prefers candidate over the reference).",
                      15.5, 52)
    b.append(t)

    # ==== panel 1: kept gaps per judge, per pool ====
    t, _ = text_block(60, 456, "Each judge’s kept-set gap on the five fresh pools", 20, 60, weight="bold")
    b.append(t)
    ly = 488
    b.append(f'<rect x="66" y="{ly - 12}" width="26" height="14" rx="3" fill="{GREEN}" fill-opacity="0.75"/>')
    t, _ = text_block(100, ly, "plain base-model judge’s kept set", 15.5, 60, INK)
    b.append(t)
    b.append(f'<rect x="380" y="{ly - 12}" width="26" height="14" rx="3" fill="{BLUE}" fill-opacity="0.75"/>')
    t, _ = text_block(414, ly, "conservative organism judge’s kept set", 15.5, 60, INK)
    b.append(t)

    px, pw, py, ph = 130, 800, 540, 270
    ymax, ymin = 0.03, -0.30

    def Y(v):
        return py + ph * (ymax - v) / (ymax - ymin)

    for v in (0.0, -0.1, -0.2, -0.3):
        yy = Y(v)
        w_ = 2.5 if v == 0.0 else 1
        col = INK if v == 0.0 else "#e4e4e0"
        b.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px + pw}" y2="{yy:.1f}" stroke="{col}" stroke-width="{w_}"/>')
        b.append(f'<text x="{px - 10}" y="{yy + 5:.1f}" text-anchor="end" font-size="15" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    b.append(f'<text x="{px - 56}" y="{py + ph / 2}" font-size="15" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {px - 56} {py + ph / 2})" text-anchor="middle">kept gap: kept-set risk value minus pool mean</text>')

    for gi in range(5):
        cx = px + pw * (gi + 0.5) / 5
        base_gap, cons_gap, sep = d["base_gaps"][gi], d["cons_gaps"][gi], seps[gi]
        for off, val, jcolor in ((-50, base_gap, GREEN), (-4, cons_gap, BLUE)):
            y0b, y1b = sorted((Y(0), Y(val)))
            b.append(f'<rect x="{cx + off:.1f}" y="{y0b:.1f}" width="42" height="{max(y1b - y0b, 2):.1f}" rx="4" '
                     f'fill="{jcolor}" fill-opacity="0.75"/>')
            b.append(f'<text x="{cx + off + 21:.1f}" y="{Y(val) + 17:.1f}" text-anchor="middle" font-size="13.5" '
                     f'font-weight="bold" fill="{jcolor}" font-family="{FONT}">−{abs(val):.3f}</text>')
        # separation bracket to the right of the pair
        bx = cx + 50
        yb, yc = Y(base_gap), Y(cons_gap)
        scolor = RED if sep < 0 else INK
        b.append(f'<line x1="{bx}" y1="{yb:.1f}" x2="{bx}" y2="{yc:.1f}" stroke="{scolor}" stroke-width="3"/>')
        for yy in (yb, yc):
            b.append(f'<line x1="{bx - 5}" y1="{yy:.1f}" x2="{bx + 5}" y2="{yy:.1f}" stroke="{scolor}" stroke-width="3"/>')
        sign = "+" if sep >= 0 else "−"
        b.append(f'<text x="{bx + 7}" y="{(yb + yc) / 2 + 1:.1f}" font-size="16" font-weight="bold" '
                 f'fill="{scolor}" font-family="{FONT}">{sign}{abs(sep):.3f}</text>')
        b.append(f'<text x="{bx + 7}" y="{(yb + yc) / 2 + 18:.1f}" font-size="11.5" '
                 f'fill="{scolor}" font-family="{FONT}">swap force</text>')
        pcol = RED if gi == OUTLIER else INK
        b.append(f'<text x="{cx - 6:.1f}" y="{py + ph + 28}" text-anchor="middle" font-size="16.5" '
                 f'font-weight="bold" fill="{pcol}" font-family="{FONT}">pool {d["pool_seeds"][gi]}</text>')

    t, _ = rich_text(60, py + ph + 66, [
        ("The conservative judge’s kept set is more cautious than the pool average in all five pools (kept gap −0.125 to −0.257): the trained-in cautious sign replicates. ",
         BLUE, True),
        ("Pool 505 flips the separation negative ", RED, True),
        ("not because the conservative taste weakened there (its kept gap, −0.160, is in line with the other pools) but because the base judge happened to keep the single most cautious kept set of the whole screen (−0.181) on that pool.",
         INK, False),
    ], 15, 114)
    b.append(t)

    # ==== panel 2: the five separations as a force distribution ====
    t, _ = text_block(980, 456, "The five separations, as the force distribution the loop feels", 19, 36, weight="bold")
    b.append(t)

    px2, pw2, py2, ph2 = 1030, 290, 540, 270
    ymax2, ymin2 = 0.21, -0.07

    def Y2(v):
        return py2 + ph2 * (ymax2 - v) / (ymax2 - ymin2)

    # mean ± sd band, drawn first
    b.append(f'<rect x="{px2}" y="{Y2(mean_sep + sd_sep):.1f}" width="{pw2}" '
             f'height="{Y2(mean_sep - sd_sep) - Y2(mean_sep + sd_sep):.1f}" fill="#f0efe8"/>')
    for v in (-0.05, 0.0, 0.05, 0.10, 0.15, 0.20):
        yy = Y2(v)
        col = INK if v == 0.0 else "#dcdcd6"
        w_ = 2 if v == 0.0 else 1
        b.append(f'<line x1="{px2}" y1="{yy:.1f}" x2="{px2 + pw2}" y2="{yy:.1f}" stroke="{col}" stroke-width="{w_}"/>')
        b.append(f'<text x="{px2 - 10}" y="{yy + 5:.1f}" text-anchor="end" font-size="14" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    # mean line + labels for band and rule lines (all inside the plot frame)
    ym = Y2(mean_sep)
    b.append(f'<line x1="{px2}" y1="{ym:.1f}" x2="{px2 + pw2}" y2="{ym:.1f}" stroke="{INK}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    b.append(f'<text x="{px2 + 6}" y="{Y2(0.10) - 7:.1f}" font-size="12" fill="{GRAY}" font-family="{FONT}">superseded magnitude floor 0.10</text>')
    b.append(f'<text x="{px2 + 6}" y="{ym + 17:.1f}" font-size="12.5" font-weight="bold" fill="{INK}" font-family="{FONT}">mean {mean_sep:.3f} ± sd {sd_sep:.3f} (band)</text>')
    b.append(f'<text x="{px2 + pw2 - 6}" y="{Y2(0) - 7:.1f}" text-anchor="end" font-size="12" fill="{GRAY}" font-family="{FONT}">sign gate: 0</text>')

    for gi in range(5):
        xx = px2 + pw2 * (gi + 0.5) / 5
        sep = seps[gi]
        dcol = RED if gi == OUTLIER else INK
        b.append(f'<circle cx="{xx:.1f}" cy="{Y2(sep):.1f}" r="7.5" fill="{dcol}" stroke="white" stroke-width="1.5"/>')
        sign = "+" if sep >= 0 else "−"
        vy = Y2(sep) - 13 if gi != OUTLIER else Y2(sep) + 24
        b.append(f'<text x="{xx:.1f}" y="{vy:.1f}" text-anchor="middle" font-size="12.5" font-weight="bold" '
                 f'fill="{dcol}" font-family="{FONT}">{sign}{abs(sep):.3f}</text>')
        b.append(f'<text x="{xx:.1f}" y="{py2 + ph2 + 28}" text-anchor="middle" font-size="14.5" '
                 f'font-weight="bold" fill="{dcol}" font-family="{FONT}">{d["pool_seeds"][gi]}</text>')
    b.append(f'<text x="{px2 + pw2 / 2}" y="{py2 + ph2 + 50}" text-anchor="middle" font-size="13.5" fill="{GRAY}" font-family="{FONT}">pool (fresh sampling seed)</text>')
    b.append(f'<text x="{px2 - 48}" y="{py2 + ph2 / 2}" font-size="14" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {px2 - 48} {py2 + ph2 / 2})" text-anchor="middle">separation (judge-swap force)</text>')

    t, _ = rich_text(980, py2 + ph2 + 84, [
        ("Governing decision rule ", INK, True),
        ("(preregistered before pools 303, 404, 505 were observed): mean separation > 0, at least 60% of pools > 0, conservative kept gap negative in every pool — ", INK, False),
        ("passes, 4 of 5 pools positive. ", INK, True),
        ("The superseded rule also demanded mean ≥ 0.10: the observed mean lands exactly on that floor.", GRAY, False),
    ], 14.5, 52)
    b.append(t)

    # ==== takeaway ====
    ky = 1064
    b.append(box(60, ky, W - 120, 138, KEY_FILL, INK, 2.5))
    t, _ = rich_text(80, ky + 32, [
        ("What the loop consumes: a force distribution, not a verdict. ", INK, True),
        (f"Across five fresh pools the judge-swap selection force is {mean_sep:.3f} ± {sd_sep:.3f} (mean ± sd) — three pools near +0.167, one near zero, one slightly negative — while the conservative judge’s kept set stays more cautious than its pool in every one. ", INK, False),
        (f"The judge-swap loop grid takes {mean_sep:.3f} ± {sd_sep:.3f} as its per-round force calibration, and must expect rounds in which the swap exerts no net force.", BLUE, True),
    ], 18, 132)
    b.append(t)
    t, _ = text_block(60, ky + 168,
                      "Data: experiments/kaggle/kaggle_k2_olmo_inversion/screen_attestation.json (run v10_judge_topup, rung_20; per-pool "
                      "sanity gates — semantic diversity, factual-accuracy drop at most 0.10 — pass in all five pools).",
                      13.5, 160, GRAY)
    b.append(t)

    return svg_doc(W, ky + 216, "\n".join(b))


if __name__ == "__main__":
    out = os.path.join(HERE, "judge-force-five-pools.svg")
    with open(out, "w") as f:
        f.write(main())
    print("wrote", out)

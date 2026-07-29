#!/usr/bin/env python3
"""The selection gap is not fading -- individual pools stop selecting
(slug: collapse-not-erosion).

PANEL A. Two ways of averaging the same per-round quantity, the mean absolute
selection gap:

    all pools               mean |kept mean - pool mean| over all 59 pools
    pools with any spread   the same mean over only the pools whose
                            within-prompt spread is not exactly zero

Averaged over every pool the gap falls across rounds; among pools that still
have spread it is flat. The whole difference is the growing share of pools at
exactly zero spread, which contribute a gap of exactly zero. That is an
identity, not a fit, and the generator asserts it holds every round:

    mean|gap| over all pools = (1 - zero-spread share)
                               x mean|gap| over pools that still have spread

PANEL B. Paired round 1 -> round 4 log differences within the 43 runs that
still have nonzero agreement, spread and gap at both ends (16 of 59 excluded).
Agreement does not fall; spread does, and about half of the spread fall is the
arithmetic ceiling on a 0/1-scored pool rather than lost variety.

    sigma = residual x sqrt(q(1-q))   IDENTITY (file's check: -1.4e-17)
    gap  ~= agreement x spread        FITTED relationship, NOT an identity

Every number is read from experiments/gap_decline_decomposition.json and
INDEPENDENTLY RECOMPUTED here from the raw corpus experiments/
spread_util_unified.json; the generator asserts the two agree before drawing.

Palette (INK/BLUE/GREEN/RED/GRAY, box fills) and the esc()/wrap()/rich_text()
helpers are copied from docs/figures/src/make_figures.py (house style).
Stdlib only. Regenerate with:  python3 collapse-not-erosion.py
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..")
RESULT = os.path.join(ROOT, "experiments", "gap_decline_decomposition.json")
CORPUS = os.path.join(ROOT, "experiments", "spread_util_unified.json")
OUT = os.path.join(HERE, "collapse-not-erosion.svg")

# ---- palette (house style; make_figures.py constants) --------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # series: average over all pools
GREEN = "#3a7d44"      # series: average over pools that still have spread
RED = "#b5342c"        # emphasis: the collapsed pools, warnings
GRAY = "#6b7684"       # recessive only (axes, muted captions) -- never a series
KEY_FILL = "#eef5ee"   # highlighted takeaway box
DOC_FILL = "#fdf6e8"   # worked-example box
FAINT = "#e4e4e0"      # gridlines

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


def ctext(x, y, s, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(s)}</text>')


def ltext(x, y, s, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(s)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def arrow(x1, y1, x2, y2, sw=4, color=INK, marker="arr"):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}" marker-end="url(#{marker})"/>')


DEFS = f'''<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ====================================================================
# Data: read the result file, then re-derive it from the raw corpus
# ====================================================================
def load():
    res = json.load(open(RESULT))
    corpus = json.load(open(CORPUS))

    rounds = [1, 2, 3, 4]
    ev = {t: res["erosion_versus_collapse"][f"round{t}"] for t in rounds}
    per = {t: res["per_round_binary_axes_only"][f"round{t}"] for t in rounds}

    # --- independent recomputation from the raw per-round records ---------
    recs = [r for r in corpus["records"]
            if r.get("gap") is not None
            and float(r.get("binary_score_fraction", 1.0)) >= 0.999
            and int(r["round"]) in rounds]
    mine = {}
    for t in rounds:
        sub = [r for r in recs if int(r["round"]) == t]
        nz = [r for r in sub if float(r["spread"]) >= 1e-9]
        zero = [r for r in sub if float(r["spread"]) < 1e-9]
        mine[t] = {
            "n": len(sub),
            "n_runs": len({(r["cond"], r["seed"], r["source"]) for r in sub}),
            "all": sum(abs(float(r["gap"])) for r in sub) / len(sub),
            "nonzero": sum(abs(float(r["gap"])) for r in nz) / len(nz),
            "n_nonzero": len(nz),
            "n_zero": len(zero),
            "f_zero": len(zero) / len(sub),
        }
        assert abs(mine[t]["all"] - ev[t]["mean_abs_gap_all_rows"]) < 1e-9
        assert abs(mine[t]["nonzero"]
                   - ev[t]["mean_abs_gap_excluding_zero_spread"]) < 1e-9
        assert abs(mine[t]["f_zero"] - ev[t]["fraction_zero_spread"]) < 1e-12
        assert mine[t]["n_zero"] == per[t]["n_zero_spread"]
        assert mine[t]["n"] == ev[t]["n"] == per[t]["n"]
        # the accounting identity this figure claims, checked every round
        assert abs(mine[t]["nonzero"] * (1 - mine[t]["f_zero"])
                   - mine[t]["all"]) < 1e-12

    # --- what the collapsed pools look like -------------------------------
    zero_rows = [r for r in recs if float(r["spread"]) < 1e-9]
    by_run = defaultdict(dict)
    for r in recs:
        by_run[(r["cond"], r["seed"], r["source"])][int(r["round"])] = float(r["spread"])
    collapsed = {k: v for k, v in by_run.items() if any(s < 1e-9 for s in v.values())}
    early, recovered = 0, 0
    for v in collapsed.values():
        first_zero = min(t for t, s in v.items() if s < 1e-9)
        if first_zero < 4:
            early += 1
            if any(s >= 1e-9 for t, s in v.items() if t > first_zero):
                recovered += 1
    facts = {
        "n_zero_rows": len(zero_rows),
        "top_rail": all(float(r["pool_mean"]) == 1.0 for r in zero_rows),
        "n_collapsed_runs": len(collapsed),
        "n_runs": len(by_run),
        "n_early": early,
        "n_recovered": recovered,
        "n_rows_total": res["n_rows"],
        "n_rows_binary": res["n_binary_axis_rows"],
    }
    assert facts["top_rail"], "a zero-spread pool is not at the top rail"

    return (res, per, mine, facts, res["log_decomposition_binary_axes_only"],
            corpus["factorization"]["pooled"], res["mean_residual_spread_ci"])


RES, PER, MINE, FACTS, DEC, FAC, RESID_CI = load()
ROUNDS = [1, 2, 3, 4]

W = 1700          # height is computed from the measured content


def build():
    b = []

    # ---------------- headline -------------------------------------------
    b.append(ctext(W / 2, 62,
                   "The selection gap is not fading. Individual pools stop selecting,",
                   32, INK, "bold"))
    b.append(ctext(W / 2, 104,
                   "and among the pools that still have spread the gap holds: "
                   f"{MINE[1]['nonzero']:.4f} → {MINE[4]['nonzero']:.4f}",
                   32, INK, "bold"))

    sub = ("59 self-training runs, four rounds each, on value axes where the judge scores every candidate 0 or 1. "
           "One pool = one round of one run: 12 prompts × 6 candidate answers the organism writes; the judge keeps the "
           "2 best answers per prompt and the organism is fine-tuned on them. Selection gap = mean value score of the "
           "kept answers minus mean value score of all candidates, on the 0–1 value axis; the figure averages its absolute "
           "size, since runs are pushed in different directions. Spread = the average, across that round’s 12 "
           "prompts, of the standard deviation of the 6 candidate value scores.")
    t, _ = text_block(180, 152, sub, 19, 130, GRAY)
    b.append(t)

    # ==================== PANEL A ========================================
    PX, PW, PY, PH = 240, 380, 370, 290
    YMAX = 0.10
    BY, BH, SMAX = 730, 120, 0.16

    def X(t):
        return PX + PW * (t - 1) / 3.0

    def Y(v):
        return PY + PH * (YMAX - v) / YMAX

    def YB(f):
        return BY + BH * (SMAX - f) / SMAX

    b.append(ltext(90, 312, "A.   Mean size of the selection gap per round, averaged two ways",
                   22, INK, "bold"))

    for v in (0.0, 0.02, 0.04, 0.06, 0.08, 0.10):
        yy = Y(v)
        b.append(f'<line x1="{PX}" y1="{yy:.1f}" x2="{PX+PW}" y2="{yy:.1f}" '
                 f'stroke="{FAINT}" stroke-width="1"/>')
        b.append(ltext(PX - 14, yy + 6, f"{v:.2f}", 18, GRAY, anchor="end"))
    b.append(f'<line x1="{PX}" y1="{PY}" x2="{PX}" y2="{PY+PH}" '
             f'stroke="{GRAY}" stroke-width="1.5"/>')
    b.append(f'<text x="150" y="{PY+PH/2}" font-size="19" fill="{INK}" '
             f'font-family="{FONT}" text-anchor="middle" '
             f'transform="rotate(-90 150 {PY+PH/2})">mean gap size</text>')
    for t in ROUNDS:
        b.append(f'<line x1="{X(t):.1f}" y1="{PY}" x2="{X(t):.1f}" y2="{BY+BH}" '
                 f'stroke="{FAINT}" stroke-width="1"/>')

    # the red band: the gap the collapsed pools take out of the average
    top = " ".join(f"{X(t):.1f},{Y(MINE[t]['nonzero']):.1f}" for t in ROUNDS)
    bot = " ".join(f"{X(t):.1f},{Y(MINE[t]['all']):.1f}" for t in reversed(ROUNDS))
    b.append(f'<polygon points="{top} {bot}" fill="{RED}" fill-opacity="0.30" stroke="none"/>')

    b.append('<polyline points="{}" fill="none" stroke="{}" stroke-width="3.5" '
             'stroke-dasharray="9 6"/>'.format(
                 " ".join(f"{X(t):.1f},{Y(MINE[t]['all']):.1f}" for t in ROUNDS), BLUE))
    b.append('<polyline points="{}" fill="none" stroke="{}" stroke-width="3.5"/>'.format(
        " ".join(f"{X(t):.1f},{Y(MINE[t]['nonzero']):.1f}" for t in ROUNDS), GREEN))
    for t in ROUNDS:
        xx, ya, yn = X(t), Y(MINE[t]["all"]), Y(MINE[t]["nonzero"])
        b.append(f'<rect x="{xx-7:.1f}" y="{ya-7:.1f}" width="14" height="14" '
                 f'fill="{BLUE}" stroke="white" stroke-width="2"/>')
        b.append(f'<circle cx="{xx:.1f}" cy="{yn:.1f}" r="8" fill="{GREEN}" '
                 f'stroke="white" stroke-width="2"/>')
        if t == 1:
            b.append(ltext(xx + 14, yn - 8, f"{MINE[t]['nonzero']:.4f}", 18, INK, "bold"))
            b.append(ltext(xx + 14, ya + 32, f"{MINE[t]['all']:.4f}", 18, INK, "bold"))
        elif t == 2:      # blue label pushed left, to clear the red band's arrow
            b.append(ctext(xx, yn - 14, f"{MINE[t]['nonzero']:.4f}", 18, INK, "bold"))
            b.append(ltext(xx - 12, ya + 32, f"{MINE[t]['all']:.4f}", 18, INK, "bold",
                           anchor="end"))
        elif t == 4:
            b.append(ltext(xx - 14, yn - 8, f"{MINE[t]['nonzero']:.4f}", 18, INK, "bold",
                           anchor="end"))
            b.append(ltext(xx - 14, ya + 32, f"{MINE[t]['all']:.4f}", 18, INK, "bold",
                           anchor="end"))
        else:
            b.append(ctext(xx, yn - 14, f"{MINE[t]['nonzero']:.4f}", 18, INK, "bold"))
            b.append(ctext(xx, ya + 32, f"{MINE[t]['all']:.4f}", 18, INK, "bold"))

    # in-figure condition lines, each beside its own series
    b.append(ltext(X(4) + 16, Y(MINE[4]["nonzero"]) - 6, "pools that still", 19, GREEN, "bold"))
    b.append(ltext(X(4) + 16, Y(MINE[4]["nonzero"]) + 16, "have any spread", 19, GREEN, "bold"))
    b.append(ltext(X(4) + 16, Y(MINE[4]["all"]) + 24, "all 59 pools,", 19, BLUE, "bold"))
    b.append(ltext(X(4) + 16, Y(MINE[4]["all"]) + 46, "collapsed ones too", 19, BLUE, "bold"))

    # the band, named
    t, _ = text_block(268, 588,
                      "red band = the gap the collapsed pools take out of the average",
                      18, 40, RED, "bold")
    b.append(t)
    b.append(arrow(350, 570, 425, 450, 2.5, RED, "arrR"))

    # ---- share-of-collapsed bars ----------------------------------------
    b.append(ltext(90, BY - 26, "Share of those same pools whose spread is exactly zero",
                   20, INK, "bold"))
    for f in (0.05, 0.10, 0.15):
        yy = YB(f)
        b.append(f'<line x1="{PX-44}" y1="{yy:.1f}" x2="{PX+PW+20}" y2="{yy:.1f}" '
                 f'stroke="{FAINT}" stroke-width="1"/>')
    b.append(ltext(PX - 58, YB(0.15) + 6, "15%", 18, GRAY, anchor="end"))
    b.append(ltext(PX - 58, YB(0) + 6, "0%", 18, GRAY, anchor="end"))
    b.append(f'<line x1="{PX-44}" y1="{YB(0):.1f}" x2="{PX+PW+20}" y2="{YB(0):.1f}" '
             f'stroke="{GRAY}" stroke-width="1.5"/>')
    for t in ROUNDS:
        f = MINE[t]["f_zero"]
        h = BH * f / SMAX
        xx = X(t)
        b.append(f'<rect x="{xx-32:.1f}" y="{YB(f):.1f}" width="64" height="{h:.1f}" '
                 f'rx="4" fill="{RED}"/>')
        b.append(ctext(xx, YB(f) - 12, f"{f*100:.1f}%", 19, INK, "bold"))
        lbl = f"{MINE[t]['n_zero']} of {MINE[t]['n']}"
        if h >= 48:
            b.append(ctext(xx, YB(f) + 27, lbl, 18, "white", "bold"))
        else:
            b.append(ctext(xx, YB(f) - 36, lbl, 18, GRAY))
    for t in ROUNDS:
        b.append(ctext(X(t), BY + BH + 34, f"round {t}", 20, INK, "bold"))

    # ---- what a zero-spread pool is, and the identity -------------------
    bx, by_, bw = 90, 925, 710
    box_at = len(b)                       # height is set once the content is measured
    b.append("")
    b.append(ltext(bx + 24, by_ + 38, "A pool at zero spread: nothing to select between",
                   21, INK, "bold"))
    t, _ = text_block(bx + 24, by_ + 72,
                      "Zero spread means that on every one of that round’s 12 prompts, all six "
                      "candidate answers got the same value score. Say all six scored 1:", 18, 71, INK)
    b.append(t)
    chip_y = by_ + 122
    cx0 = bx + 40
    for i in range(6):
        x = cx0 + i * 58
        kept = i in (1, 4)
        b.append(f'<rect x="{x}" y="{chip_y:.1f}" width="46" height="42" rx="6" fill="white" '
                 f'stroke="{INK}" stroke-width="{4 if kept else 1.8}"/>')
        b.append(ctext(x + 23, chip_y + 29, "1", 22, INK, "bold"))
        if kept:
            b.append(ctext(x + 23, chip_y + 64, "kept", 18, INK, "bold"))
    t, _ = text_block(cx0 + 372, chip_y + 4,
                      "kept mean 1.000 − pool mean 1.000 = gap 0.000, whichever two the "
                      "judge keeps.", 18, 25, INK)
    b.append(t)
    t, y = rich_text(bx + 24, chip_y + 138,
                     [(f"{MINE[4]['nonzero']:.4f} × (1 − {MINE[4]['f_zero']:.3f}) = {MINE[4]['all']:.4f}",
                       RED, True),
                      ("at round 4 — the gap among pools that still have spread, times the share of "
                       "pools that still have any, is the average over all pools. Exactly, every round.",
                       INK, False)],
                     18, 71)
    b.append(t)
    t, y = text_block(bx + 24, y + 16,
                      f"All {FACTS['n_zero_rows']} zero-spread pools here sit at the top of the value "
                      f"axis (pool mean 1.0), in {FACTS['n_collapsed_runs']} of the {FACTS['n_runs']} runs. "
                      f"Of the {FACTS['n_early']} that reach zero before round 4, "
                      f"{'none' if FACTS['n_recovered'] == 0 else FACTS['n_recovered']} has spread again "
                      "in a later round.", 18, 73, GRAY)
    b.append(t)
    left_bottom = y + 14
    b[box_at] = box(bx, by_, bw, left_bottom - by_, DOC_FILL, INK, 2.5)

    # ==================== PANEL B ========================================
    BXL = 860
    QX0, QX1 = 1170, 1600
    QLO, QHI = -0.40, 0.90

    def Q(v):
        return QX0 + (QX1 - QX0) * (v - QLO) / (QHI - QLO)

    b.append(ltext(BXL, 312, "B.   Inside the 43 runs that still have spread at both ends,",
                   22, INK, "bold"))
    b.append(ltext(BXL, 340, "spread falls — the judge’s agreement does not", 22, INK, "bold"))
    note = ("Paired round 1 → round 4 inside each run, in log units; bars are 95% bootstrap intervals "
            f"({RES['settings']['bootstrap_draws']:,} draws, resampled by whole run). Agreement = the mean "
            "within-prompt correlation between a candidate’s judge score and its value score; spread is "
            f"defined in the header above. {DEC['n_runs_excluded_for_zero_rho_sigma_or_gap']} of the 59 runs are "
            "excluded "
            "because agreement, spread or the gap was exactly zero at one end and has no logarithm.")
    t, _ = text_block(BXL, 378, note, 18, 80, GRAY)
    b.append(t)

    b.append(f'<line x1="{QX0}" y1="546" x2="{QX1}" y2="546" stroke="{GRAY}" stroke-width="1.5"/>')
    for v in (-0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8):
        xx = Q(v)
        b.append(f'<line x1="{xx:.1f}" y1="542" x2="{xx:.1f}" y2="550" stroke="{GRAY}" stroke-width="1.5"/>')
        b.append(ctext(xx, 536, f"{v:+.1f}" if v else "0.0", 18, GRAY))
    b.append(ltext(Q(0) - 12, 512, "← term shrinks", 18, GRAY, anchor="end"))
    b.append(ltext(Q(0) + 12, 512, "term grows →", 18, GRAY))
    b.append(ltext(QX0, 578, "mean change in log(term), round 1 → round 4", 18, GRAY))

    ROWS = [
        ("agreement, absolute size", "— rises; its interval barely touches zero", GREEN, "rho", 0),
        ("spread", "— falls; the two rows below split that fall", GRAY, "sigma", 0),
        ("└ binary ceiling √(q(1−q))", "— the most a 0/1-scored pool at mean q can spread",
         GRAY, "ceiling", 26),
        ("└ residual spread σ/√(q(1−q))", "— the share of that ceiling actually used",
         GRAY, "residual", 26),
    ]
    cursor, row_y = 606, []
    for name, tag, tagcol, key, indent in ROWS:
        est = DEC["mean_delta_log"][key]
        lo, hi = DEC["ci"][key]
        t, _ = rich_text(BXL + indent, cursor,
                         [(name, INK, True), (tag, tagcol, tagcol == GREEN)], 18, 31)
        b.append(t)
        yy = cursor + 30
        row_y.append(yy)
        b.append(f'<line x1="{Q(lo):.1f}" y1="{yy:.1f}" x2="{Q(hi):.1f}" y2="{yy:.1f}" '
                 f'stroke="{INK}" stroke-width="3.5"/>')
        for e in (lo, hi):
            b.append(f'<line x1="{Q(e):.1f}" y1="{yy-10:.1f}" x2="{Q(e):.1f}" y2="{yy+10:.1f}" '
                     f'stroke="{INK}" stroke-width="3.5"/>')
        b.append(f'<circle cx="{Q(est):.1f}" cy="{yy:.1f}" r="9" fill="{INK}" '
                 f'stroke="white" stroke-width="2.5"/>')
        b.append(ctext(Q(est), yy - 20, f"{est:+.3f}", 19, INK, "bold"))
        b.append(ctext((Q(lo) + Q(hi)) / 2, yy + 32, f"[{lo:+.3f}, {hi:+.3f}]", 18, GRAY))
        cursor = cursor + 104
    b.append(f'<line x1="{Q(0):.1f}" y1="596" x2="{Q(0):.1f}" y2="{row_y[-1]+18:.1f}" '
             f'stroke="{INK}" stroke-width="2" stroke-dasharray="7 5"/>')
    b.append(f'<path d="M {BXL+18} {row_y[2]-34:.1f} L {BXL+6} {row_y[2]-34:.1f} '
             f'L {BXL+6} {row_y[3]-34:.1f} L {BXL+18} {row_y[3]-34:.1f}" fill="none" '
             f'stroke="{GRAY}" stroke-width="2"/>')

    ny = cursor - 8
    t, ny = text_block(BXL, ny,
                       "σ = residual × ceiling is an identity — the bottom two rows add to the spread row "
                       f"exactly (the file’s check comes out at "
                       f"{DEC['identity_check_sigma_minus_ceiling_minus_residual']:.0e}). So about "
                       f"{DEC['share_of_sigma_decline_forced_by_the_rail']*100:.0f}% of the spread fall is the "
                       "0/1 ceiling, which must shrink as a pool moves toward a rail whatever its variety is "
                       f"doing. The rest is real variety loss: residual spread runs "
                       f"{PER[1]['mean_residual_spread']:.3f} of the ceiling at round 1 "
                       f"[{RESID_CI['round1'][0]:.3f}, {RESID_CI['round1'][1]:.3f}] down to "
                       f"{PER[4]['mean_residual_spread']:.3f} at round 4 "
                       f"[{RESID_CI['round4'][0]:.3f}, {RESID_CI['round4'][1]:.3f}].", 18, 80, INK)
    b.append(t)
    pair_sum = DEC["mean_delta_log"]["rho"] + DEC["mean_delta_log"]["sigma"]
    t, ny = text_block(BXL, ny + 14,
                      "gap ≈ agreement × spread is a fitted relationship, not an identity "
                      f"(R² {FAC['r2_product']:.2f} over the {FAC['n']} rounds where agreement is defined), "
                      f"so these two need not add to the gap’s own paired change of "
                      f"{DEC['mean_delta_log']['gap']:+.3f} [{DEC['ci']['gap'][0]:+.3f}, "
                      f"{DEC['ci']['gap'][1]:+.3f}] — they add to {pair_sum:+.3f}, leaving "
                      f"{DEC['model_error_gap_minus_rho_minus_sigma']:+.3f} as the relationship’s own error.",
                      18, 80, GRAY)
    b.append(t)

    # ==================== full-width takeaway ============================
    ty = max(left_bottom, ny + 6) + 46
    tbox_at = len(b)
    b.append("")
    b.append(ltext(116, ty + 38,
                   "A failure process and a decay process call for different fixes", 21, INK, "bold"))
    t, tend = rich_text(116, ty + 72,
                     [("If selection were decaying, the fix would be to slow the decay everywhere — hotter "
                       "sampling, more candidates per prompt, a weaker judge — applied to every run. Because it "
                       "is pools failing, the fix is to catch the pools that are about to go uniform; the pools "
                       "that still select need no change at all, their gap at round 4 being within "
                       f"{abs(MINE[1]['nonzero']-MINE[4]['nonzero']):.4f} of their gap at round 1.", INK, False),
                      ("This figure does not show why a pool collapses, or whether collapse can be predicted a "
                       "round ahead. Both are open on this same data.", RED, True)],
                     18, 160)
    b.append(t)
    th = tend + 14 - ty
    b[tbox_at] = box(90, ty, 1520, th, KEY_FILL, GREEN, 2.5)

    # ==================== footnote =======================================
    foot = (f"Panel A: {MINE[1]['n']} runs × 4 rounds, binary-scored axes only "
            f"({FACTS['n_rows_binary']} of the {FACTS['n_rows_total']} score-logged rounds in the corpus are "
            "binary-scored; rounds past 4 are not shown). Panel B describes survivors only — "
            f"{DEC['n_runs_usable']} runs paired, {DEC['n_runs_excluded_for_zero_rho_sigma_or_gap']} excluded "
            "— not the whole population. The runs that collapse here are the invasion and oracle-hold "
            "conditions, which drive the value toward the ceiling. Source: "
            "experiments/gap_decline_decomposition.json; every number re-derived by this generator from "
            "experiments/spread_util_unified.json.")
    t, fend = text_block(90, ty + th + 50, foot, 18, 168, GRAY)
    b.append(t)

    return "\n".join(b), fend + 34


if __name__ == "__main__":
    body, height = build()
    with open(OUT, "w") as f:
        f.write(svg_doc(W, height, body))
    print(f"wrote {OUT}  ({W} × {height:.0f})")

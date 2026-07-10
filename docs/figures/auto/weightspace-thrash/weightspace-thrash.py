#!/usr/bin/env python3
"""Withdrawal figure for non-identifiable raw-factor LoRA correlations.

Recomputes everything from the basin rollout JSONs (per-round LoRA update
norms + cosines, per-round risk coordinate) and draws two scatter panels:
  1. total weight displacement vs |final - initial risk|  (anti-correlated)
  2. mean consecutive-update cosine vs final risk          (positively correlated)
House style follows docs/figures/make_figures.py. Stdlib only.
Regenerate with:  python3 weightspace-thrash.py
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..")
DATA_FILES = [
    os.path.join(ROOT, "experiments", "kaggle", "kaggle_basin_anchor",
                 "output", "basin_anchor.json"),
    os.path.join(ROOT, "experiments", "kaggle", "kaggle_basin_anchor_ext",
                 "output", "basin_anchor_ext.json"),
    os.path.join(ROOT, "experiments", "lightning", "output",
                 "basin_anchor_lightning_15_23.json"),
    os.path.join(ROOT, "experiments", "lightning", "output",
                 "basin_anchor_lightning_23_31.json"),
]

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
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


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- data
def load_rollouts():
    """One record per complete 5-round rollout. Rollouts with fewer logged
    rounds (one frozen-judge run stopped after round 1) are dropped."""
    rollouts = {"self": [], "frozen": []}
    for path in DATA_FILES:
        data = json.load(open(path))
        for seed in data:
            for cond, key in (("self", "persona_self"),
                              ("frozen", "persona_cross")):
                if key not in data[seed]:
                    continue
                run = data[seed][key]
                traj, deltas = run["traj"], run["lora_delta"]
                if len(deltas) < 5:
                    continue
                norms = [d["delta_norm"] for d in deltas]
                cosines = [d["cos_with_prev_delta"] for d in deltas
                           if d["cos_with_prev_delta"] is not None]
                rollouts[cond].append({
                    "total": sum(norms),
                    "round1": norms[0],
                    "mean_cos": sum(cosines) / len(cosines),
                    "final": traj[-1],
                    "abschange": abs(traj[-1] - traj[0]),
                })
    return rollouts


def corr(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def fit(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    return slope, my - slope * mx


def mean_sd(vals):
    n = len(vals)
    m = sum(vals) / n
    return m, math.sqrt(sum((v - m) ** 2 for v in vals) / n)


# ---------------------------------------------------------------- figure
def make():
    R = load_rollouts()
    n_self, n_froz = len(R["self"]), len(R["frozen"])

    def cols(cond, xkey, ykey):
        return ([r[xkey] for r in R[cond]], [r[ykey] for r in R[cond]])

    b = []
    W = 1340
    t, _ = text_block(W // 2, 52, "WITHDRAWN: raw-factor LoRA geometry is non-identifiable",
                      36, 70, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 96,
                      "These historical correlations change under equivalent LoRA factorizations and are not scientific results",
                      20, 130, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(
        70, 138,
        f"Historical display over {n_self + n_froz} rollouts. The x variables concatenate raw LoRA A/B factors; "
        "they are representation-dependent under B -> BG and A -> G^-1 A even when the functional update BA is unchanged. "
        "The scatter is retained only to prevent accidental reuse; recompute on merged W_t-W_0 products.",
        16, 158, GRAY)
    b.append(t)

    # legend
    ly = 208
    b.append(f'<circle cx="380" cy="{ly - 5}" r="7" fill="{BLUE}"/>')
    b.append(f'<text x="394" y="{ly}" font-size="17" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">the organism judges its own answers ({n_self} rollouts)</text>')
    b.append(f'<circle cx="810" cy="{ly - 5}" r="7" fill="{GREEN}"/>')
    b.append(f'<text x="824" y="{ly}" font-size="17" font-weight="bold" fill="{INK}" '
             f'font-family="{FONT}">a frozen base model judges ({n_froz} rollouts)</text>')

    def panel(px, py, pw, ph, xkey, ykey, xlim, ylim, xticks, yticks,
              xfmt, yfmt, title, xlabel, ylabel):
        s = []
        t2, _ = text_block(px - 62, py - 26, title, 21, 60, weight="bold")
        s.append(t2)

        def X(v):
            return px + pw * (v - xlim[0]) / (xlim[1] - xlim[0])

        def Y(v):
            return py + ph * (ylim[1] - v) / (ylim[1] - ylim[0])

        for v in yticks:
            yy = Y(v)
            s.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px + pw}" y2="{yy:.1f}" '
                     f'stroke="#e4e4e0" stroke-width="1"/>')
            s.append(f'<text x="{px - 10}" y="{yy + 6:.1f}" text-anchor="end" font-size="16" '
                     f'fill="{GRAY}" font-family="{FONT}">{yfmt % v}</text>')
        for v in xticks:
            xx = X(v)
            s.append(f'<line x1="{xx:.1f}" y1="{py + ph}" x2="{xx:.1f}" y2="{py + ph + 7}" '
                     f'stroke="{GRAY}" stroke-width="1.5"/>')
            s.append(f'<text x="{xx:.1f}" y="{py + ph + 28}" text-anchor="middle" font-size="16" '
                     f'fill="{GRAY}" font-family="{FONT}">{xfmt % v}</text>')
        s.append(f'<line x1="{px}" y1="{py + ph}" x2="{px + pw}" y2="{py + ph}" '
                 f'stroke="{INK}" stroke-width="2"/>')
        s.append(f'<text x="{px + pw / 2}" y="{py + ph + 60}" text-anchor="middle" '
                 f'font-size="17" fill="{INK}" font-family="{FONT}">{esc(xlabel)}</text>')
        yl_y = py + ph / 2
        s.append(f'<text x="{px - 62}" y="{yl_y}" font-size="17" fill="{INK}" '
                 f'font-family="{FONT}" transform="rotate(-90 {px - 62} {yl_y})" '
                 f'text-anchor="middle">{esc(ylabel)}</text>')

        rvals = {}
        for cond, color in (("self", BLUE), ("frozen", GREEN)):
            xs, ys = cols(cond, xkey, ykey)
            rvals[cond] = corr(xs, ys)
            slope, icpt = fit(xs, ys)
            x0, x1 = min(xs), max(xs)
            s.append(f'<line x1="{X(x0):.1f}" y1="{Y(slope * x0 + icpt):.1f}" '
                     f'x2="{X(x1):.1f}" y2="{Y(slope * x1 + icpt):.1f}" '
                     f'stroke="{color}" stroke-width="2.5" stroke-dasharray="7 6" '
                     f'stroke-opacity="0.65"/>')
            for x, y in zip(xs, ys):
                s.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="6" fill="{color}" '
                         f'fill-opacity="0.85" stroke="white" stroke-width="1.5"/>')
        return "\n".join(s), rvals, (lambda v: X(v)), (lambda v: Y(v))

    py, ph = 300, 380

    # ---- panel 1: total displacement vs |final - initial| ----
    p1x, p1w = 132, 500
    p1, r1, X1, Y1 = panel(
        p1x, py, p1w, ph, "total", "abschange",
        (4.6, 6.0), (0.0, 0.65), (4.8, 5.2, 5.6, 6.0), (0.0, 0.2, 0.4, 0.6),
        "%.1f", "%.1f",
        "More weight motion, less behavioral change",
        "total weight displacement over 5 rounds",
        "behavioral change  |final minus initial risk|")
    b.append(p1)
    b.append(f'<text x="{p1x + 14}" y="{py + ph - 58}" font-size="18" font-weight="bold" '
             f'fill="{BLUE}" font-family="{FONT}">r = {r1["self"]:+.2f} (self-judge)</text>')
    b.append(f'<text x="{p1x + 14}" y="{py + ph - 32}" font-size="18" font-weight="bold" '
             f'fill="{GREEN}" font-family="{FONT}">r = {r1["frozen"]:+.2f} (frozen judge)</text>')

    # ---- panel 2: mean consecutive-update cosine vs final risk ----
    p2x, p2w = 800, 470
    p2, r2, X2, Y2 = panel(
        p2x, py, p2w, ph, "mean_cos", "final",
        (0.04, 0.27), (0.0, 0.85), (0.05, 0.10, 0.15, 0.20, 0.25),
        (0.0, 0.25, 0.5, 0.75),
        "%.2f", "%.2f",
        "Consistent update direction, extreme final risk",
        "mean cosine between consecutive rounds' weight updates",
        "final risk coordinate (after round 5)")
    b.append(p2)
    b.append(f'<text x="{p2x + 14}" y="{py + 36}" font-size="18" font-weight="bold" '
             f'fill="{BLUE}" font-family="{FONT}">r = {r2["self"]:+.2f} (self-judge)</text>')
    b.append(f'<text x="{p2x + 14}" y="{py + 62}" font-size="18" font-weight="bold" '
             f'fill="{GREEN}" font-family="{FONT}">r = {r2["frozen"]:+.2f} (frozen judge)</text>')

    # ---- per-panel notes ----
    tot_m_s, tot_sd_s = mean_sd([r["total"] for r in R["self"]])
    tot_m_f, tot_sd_f = mean_sd([r["total"] for r in R["frozen"]])
    cos_m_s, cos_sd_s = mean_sd([r["mean_cos"] for r in R["self"]])
    cos_m_f, cos_sd_f = mean_sd([r["mean_cos"] for r in R["frozen"]])
    noty = py + ph + 90
    t, _ = text_block(
        p1x - 62, noty,
        f"Every rollout moves a similar total amount ({tot_m_s:.2f} ± {tot_sd_s:.2f} "
        f"self-judge, {tot_m_f:.2f} ± {tot_sd_f:.2f} frozen) — but within that narrow "
        "band, the biggest movers are the seeds whose behavior barely shifts.",
        15.5, 66, GRAY)
    b.append(t)
    t, _ = text_block(
        p2x - 62, noty,
        f"Consecutive updates are nearly orthogonal (mean cosine {cos_m_s:.2f} ± "
        f"{cos_sd_s:.2f} self-judge, {cos_m_f:.2f} ± {cos_sd_f:.2f} frozen): the loop "
        "mostly re-steers. The rollouts that DO keep a direction end up the most risk-seeking.",
        15.5, 64, GRAY)
    b.append(t)

    # ---- takeaway box ----
    r1_self = corr([r["round1"] for r in R["self"]], [r["final"] for r in R["self"]])
    r1_froz = corr([r["round1"] for r in R["frozen"]], [r["final"] for r in R["frozen"]])
    ky = noty + 88
    b.append(box(70, ky, W - 140, 118, KEY_FILL, INK, 2.5))
    t, _ = rich_text(90, ky + 34, [
        ("Do not interpret the displayed correlations. ", RED, True),
        ("Raw LoRA factor norms/cosines are not invariant. The valid replacement uses merged functional updates "
         "delta_t = W_t-W_(t-1), cumulative Delta_t = W_t-W_0, and full Frobenius inner products. ", INK, False),
        ("All earlier thrash, direction, cancellation, and early-warning claims remain withdrawn.", RED, True),
    ], 18, 132)
    b.append(t)

    return svg_doc(W, ky + 148, "\n".join(b))


if __name__ == "__main__":
    svg = make()
    out = os.path.join(HERE, "weightspace-thrash.svg")
    with open(out, "w") as f:
        f.write(svg)
    print("wrote", out)

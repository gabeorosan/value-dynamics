#!/usr/bin/env python3
"""Draft figure: no robust saddle in the basin-ensemble drift field;
AR(1) zero crossings are descriptive. Recomputes from the run JSONs.

Style reference: docs/figures/make_figures.py (Owain Evans-lab style — white
background, big headline sentence, real data with fat labels).
Regenerate with:  python3 basin-drift-field.py
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..")
BASIN = os.path.join(ROOT, "experiments", "kaggle", "kaggle_basin_anchor",
                     "output", "basin_anchor.json")
BASIN_EXT = os.path.join(ROOT, "experiments", "kaggle", "kaggle_basin_anchor_ext",
                         "output", "basin_anchor_ext.json")
LIGHT_15 = os.path.join(ROOT, "experiments", "lightning", "output",
                        "basin_anchor_lightning_15_23.json")
LIGHT_23 = os.path.join(ROOT, "experiments", "lightning", "output",
                        "basin_anchor_lightning_23_31.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series (house palette)
GREEN = "#3a7d44"      # frozen-judge series (house palette)
RED = "#b5342c"        # emphasis only
GRAY = "#6b7684"       # recessive only (axes, muted captions)
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


# ====================================================================
# Data: per-round risk trajectories, pooled into (x_t, dx) transitions
# ====================================================================
def load_trajs():
    self_trajs, frozen_trajs = [], []
    d = json.load(open(BASIN))                     # seeds 0-7, both conditions
    for s in d:
        self_trajs.append(d[s]["persona_self"]["traj"])
        frozen_trajs.append(d[s]["persona_cross"]["traj"])
    d = json.load(open(BASIN_EXT))                 # seeds 8-14, self only
    for s in d:
        self_trajs.append(d[s]["persona_self"]["traj"])
    d = json.load(open(LIGHT_15))                  # seed 15 (frozen arm truncated to 2 rounds)
    for s in d:
        self_trajs.append(d[s]["persona_self"]["traj"])
        frozen_trajs.append(d[s]["persona_cross"]["traj"])
    d = json.load(open(LIGHT_23))                  # seeds 23-30, both conditions
    for s in d:
        self_trajs.append(d[s]["persona_self"]["traj"])
        frozen_trajs.append(d[s]["persona_cross"]["traj"])
    return self_trajs, frozen_trajs


def linear_drift_fit(trajs):
    """Fit dx = a*x + b on pooled transitions; cluster bootstrap CI on a."""
    import random
    clusters = [[(tr[t], tr[t + 1] - tr[t]) for t in range(len(tr) - 1)]
                for tr in trajs]
    X = [p[0] for c in clusters for p in c]
    Y = [p[1] for c in clusters for p in c]
    n = len(X)
    mx, my = sum(X) / n, sum(Y) / n
    sxx = sum((x - mx) ** 2 for x in X)
    sxy = sum((x - mx) * (y - my) for x, y in zip(X, Y))
    a = sxy / sxx
    b = my - a * mx
    resid = [y - (a * x + b) for x, y in zip(X, Y)]
    ss_res = sum(r * r for r in resid)
    ss_tot = sum((y - my) ** 2 for y in Y)
    r2 = 1 - ss_res / ss_tot
    sigma = math.sqrt(ss_res / (n - 2))            # per-step noise sd
    phi = 1 + a                                    # AR(1) coefficient
    eq_spread = sigma / math.sqrt(1 - phi * phi)   # stationary sd of the AR(1)
    random.seed(0)
    slopes = []
    for _ in range(2000):
        bs = [clusters[random.randrange(len(clusters))]
              for _ in range(len(clusters))]
        Xb = [p[0] for c in bs for p in c]
        Yb = [p[1] for c in bs for p in c]
        mxb, myb = sum(Xb) / len(Xb), sum(Yb) / len(Yb)
        sxxb = sum((x - mxb) ** 2 for x in Xb)
        if sxxb == 0:
            continue
        slopes.append(sum((x - mxb) * (y - myb) for x, y in zip(Xb, Yb)) / sxxb)
    slopes.sort()
    lo = slopes[int(0.025 * len(slopes))]
    hi = slopes[int(0.975 * len(slopes))]
    return dict(a=a, b=b, xstar=-b / a, r2=r2, sigma=sigma,
                eq_spread=eq_spread, ci=(lo, hi), n=n,
                pts=list(zip(X, Y)))


def spread_by_round(trajs):
    """Population sd across seeds at each round (full 6-round rollouts only)."""
    full = [tr for tr in trajs if len(tr) == 6]
    out = []
    for r in range(6):
        vals = [tr[r] for tr in full]
        m = sum(vals) / len(vals)
        out.append(math.sqrt(sum((v - m) ** 2 for v in vals) / len(vals)))
    return out, len(full)


# ====================================================================
# The figure
# ====================================================================
def main():
    self_trajs, frozen_trajs = load_trajs()
    fit_self = linear_drift_fit(self_trajs)
    fit_frozen = linear_drift_fit(frozen_trajs)
    sp_self, n_self = spread_by_round(self_trajs)
    sp_frozen, n_frozen = spread_by_round(frozen_trajs)
    for name, f in (("self", fit_self), ("frozen", fit_frozen)):
        print(f"{name}: n={f['n']} slope={f['a']:.3f} "
              f"CI=[{f['ci'][0]:.3f},{f['ci'][1]:.3f}] x*={f['xstar']:.3f} "
              f"R2={f['r2']:.3f} sigma={f['sigma']:.3f} eq={f['eq_spread']:.3f}")
    print("spread self:", [round(v, 3) for v in sp_self])
    print("spread frozen:", [round(v, 3) for v in sp_frozen])

    b = []
    W = 1400
    t, _ = text_block(W // 2, 52, "No robust saddle appears in the legacy basin trajectories —", 34, 74, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 94, "the fitted zero crossings remain descriptive, not physical attractors", 34, 74, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    sub = ("Each dot is one round-to-round move of one rollout: current risk coordinate x against the change to the "
           "next round, Δx = x(next round) minus x(this round), pooled across seeds. A saddle between two basins would "
           "make the fit cross zero downward twice — it crosses once in both conditions.")
    for i, ln in enumerate(wrap(sub, 150)):
        b.append(f'<text x="{W // 2}" y="{132 + i * 23}" text-anchor="middle" font-size="16.5" '
                 f'fill="{GRAY}" font-family="{FONT}">{esc(ln)}</text>')

    # ---------------- drift panels ----------------
    PY, PH = 260, 290
    XMIN, XMAX = 0.0, 1.0
    YMIN, YMAX = -0.42, 0.30

    def drift_panel(px, pw, fit, color, title, n_roll, note, zero_label=False):
        def SX(v):
            return px + pw * (v - XMIN) / (XMAX - XMIN)

        def SY(v):
            return PY + PH * (YMAX - v) / (YMAX - YMIN)

        s = [f'<text x="{px + pw / 2}" y="{PY - 44}" text-anchor="middle" font-size="21" '
             f'font-weight="bold" fill="{color}" font-family="{FONT}">{esc(title)}</text>',
             f'<text x="{px + pw / 2}" y="{PY - 20}" text-anchor="middle" font-size="15" '
             f'fill="{GRAY}" font-family="{FONT}">{esc(note)}</text>']
        # gridlines + axes
        for v in (-0.4, -0.2, 0.0, 0.2):
            y = SY(v)
            heavy = abs(v) < 1e-9
            s.append(f'<line x1="{px}" y1="{y}" x2="{px + pw}" y2="{y}" '
                     f'stroke="{INK if heavy else "#e4e4e0"}" stroke-width="{2.5 if heavy else 1}"/>')
            s.append(f'<text x="{px - 10}" y="{y + 5}" text-anchor="end" font-size="15" '
                     f'fill="{GRAY}" font-family="{FONT}">{v:+g}' + ('' if heavy else '') + '</text>')
        for v in (0.0, 0.25, 0.5, 0.75, 1.0):
            x = SX(v)
            s.append(f'<line x1="{x}" y1="{SY(YMIN)}" x2="{x}" y2="{SY(YMIN) + 7}" stroke="{INK}" stroke-width="2"/>')
            s.append(f'<text x="{x}" y="{SY(YMIN) + 26}" text-anchor="middle" font-size="15" '
                     f'fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
        s.append(f'<line x1="{px}" y1="{SY(YMIN)}" x2="{px + pw}" y2="{SY(YMIN)}" stroke="{INK}" stroke-width="2"/>')
        s.append(f'<text x="{px + pw / 2}" y="{SY(YMIN) + 52}" text-anchor="middle" font-size="16.5" '
                 f'fill="{INK}" font-family="{FONT}">risk coordinate x this round (0 = always cautious, 1 = always gamble)</text>')
        if zero_label:
            s.append(f'<text x="{px + pw - 4}" y="{SY(0) - 9}" text-anchor="end" font-size="13.5" '
                     f'fill="{GRAY}" font-family="{FONT}">no change</text>')
        # scatter
        for x, y in fit["pts"]:
            s.append(f'<circle cx="{SX(x):.1f}" cy="{SY(y):.1f}" r="4.4" fill="{color}" fill-opacity="0.35"/>')
        # fit line over the data's x span
        xs = [p[0] for p in fit["pts"]]
        x0, x1 = min(xs), max(xs)
        s.append(f'<line x1="{SX(x0)}" y1="{SY(fit["a"] * x0 + fit["b"])}" '
                 f'x2="{SX(x1)}" y2="{SY(fit["a"] * x1 + fit["b"])}" '
                 f'stroke="{color}" stroke-width="3.5"/>')
        # descriptive zero crossing of the fitted line
        fx = SX(fit["xstar"])
        s.append(f'<circle cx="{fx}" cy="{SY(0)}" r="8" fill="white" stroke="{color}" stroke-width="3.5"/>')
        lab_y = SY(0.272)
        s.append(f'<line x1="{fx}" y1="{SY(0) - 10}" x2="{fx}" y2="{lab_y + 28}" '
                 f'stroke="{color}" stroke-width="1.5" stroke-dasharray="4 4"/>')
        lx = fx + 12  # annotation grows rightward from the dashed drop line
        s.append(f'<text x="{lx}" y="{lab_y}" font-size="17" font-weight="bold" '
                 f'fill="{color}" font-family="{FONT}">AR(1) zero x* = {fit["xstar"]:.2f}</text>')
        s.append(f'<text x="{lx}" y="{lab_y + 20}" font-size="14" '
                 f'fill="{INK}" font-family="{FONT}">fitted slope {fit["a"]:.2f} per round '
                 f'[95% CI {fit["ci"][0]:.2f}, {fit["ci"][1]:.2f}]</text>')
        return "\n".join(s)

    b.append(drift_panel(100, 420, fit_self, BLUE,
                         "The organism judges its own answers",
                         len(self_trajs),
                         f"{fit_self['n']} transitions from 24 rollouts × 5 rounds",
                         zero_label=True))
    b.append(drift_panel(620, 420, fit_frozen, GREEN,
                         "A frozen base model judges",
                         len(frozen_trajs),
                         f"{fit_frozen['n']} transitions from 17 rollouts (one stopped early)"))
    # shared y label
    b.append(f'<text x="42" y="{PY + PH / 2}" font-size="16.5" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 42 {PY + PH / 2})" text-anchor="middle">change to next round, Δx</text>')

    # ---------------- spread panel ----------------
    px3, pw3 = 1135, 220
    SMAX = 0.27

    def SX3(r):
        return px3 + pw3 * r / 5

    def SY3(v):
        return PY + PH * (SMAX - v) / SMAX

    b.append(f'<text x="{px3 + pw3 / 2}" y="{PY - 44}" text-anchor="middle" font-size="21" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">Why the fan differs</text>')
    b.append(f'<text x="{px3 + pw3 / 2}" y="{PY - 20}" text-anchor="middle" font-size="15" '
             f'fill="{GRAY}" font-family="{FONT}">spread of seeds, round by round</text>')
    for v in (0.0, 0.1, 0.2):
        y = SY3(v)
        b.append(f'<line x1="{px3}" y1="{y}" x2="{px3 + pw3}" y2="{y}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{px3 - 10}" y="{y + 5}" text-anchor="end" font-size="15" '
                 f'fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    b.append(f'<line x1="{px3}" y1="{SY3(0)}" x2="{px3 + pw3}" y2="{SY3(0)}" stroke="{INK}" stroke-width="2"/>')
    for r in range(6):
        b.append(f'<text x="{SX3(r)}" y="{SY3(0) + 26}" text-anchor="middle" font-size="15" '
                 f'fill="{GRAY}" font-family="{FONT}">{r}</text>')
    b.append(f'<text x="{px3 + pw3 / 2}" y="{SY3(0) + 52}" text-anchor="middle" font-size="16.5" '
             f'fill="{INK}" font-family="{FONT}">round</text>')
    b.append(f'<text x="{px3 - 56}" y="{PY + PH / 2}" font-size="13.5" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {px3 - 56} {PY + PH / 2})" text-anchor="middle">sd of the risk coordinate across seeds</text>')
    # AR(1) noise-equilibrium reference lines
    for fitc, color, dy in ((fit_self, BLUE, -8), (fit_frozen, GREEN, 15)):
        y = SY3(fitc["eq_spread"])
        b.append(f'<line x1="{px3}" y1="{y}" x2="{px3 + pw3}" y2="{y}" '
                 f'stroke="{color}" stroke-width="2" stroke-dasharray="7 5"/>')
    b.append(f'<text x="{px3 + pw3}" y="{SY3(fit_self["eq_spread"]) - 8}" text-anchor="end" font-size="13" '
             f'fill="{BLUE}" font-family="{FONT}">noise equilibrium {fit_self["eq_spread"]:.2f}</text>')
    b.append(f'<text x="{px3 + 2}" y="{SY3(fit_frozen["eq_spread"]) + 17}" font-size="13" '
             f'fill="{GREEN}" font-family="{FONT}">noise equilibrium {fit_frozen["eq_spread"]:.2f}</text>')
    # observed spread lines
    for sp, color in ((sp_self, BLUE), (sp_frozen, GREEN)):
        pts = " ".join(f"{SX3(r):.1f},{SY3(v):.1f}" for r, v in enumerate(sp))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="3.5"/>')
        for r, v in enumerate(sp):
            b.append(f'<circle cx="{SX3(r):.1f}" cy="{SY3(v):.1f}" r="4.5" fill="{color}"/>')
    b.append(f'<text x="{SX3(5) + 8}" y="{SY3(sp_self[-1]) + 5}" font-size="15" font-weight="bold" '
             f'fill="{BLUE}" font-family="{FONT}">{sp_self[-1]:.2f}</text>')
    b.append(f'<text x="{SX3(5) + 8}" y="{SY3(sp_frozen[-1]) + 5}" font-size="15" font-weight="bold" '
             f'fill="{GREEN}" font-family="{FONT}">{sp_frozen[-1]:.2f}</text>')

    # per-panel readings under the plots
    ry = PY + PH + 84
    t, _ = rich_text(100, ry, [
        ("Self-judge: ", BLUE, True),
        ("a negative fitted slope and mid-range zero crossing; no robust two-basin saddle.", INK, False),
    ], 16.5, 62)
    b.append(t)
    t, _ = rich_text(620, ry, [
        ("Frozen judge: ", GREEN, True),
        ("a similar fitted slope with a lower descriptive zero crossing, toward caution.", INK, False),
    ], 16.5, 62)
    b.append(t)
    t, y_end = rich_text(1083, ry, [
        ("The self-judge fan ends at ", INK, False),
        (f"{sp_self[-1]:.2f}", BLUE, True),
        (f" ≈ its fitted {fit_self['eq_spread']:.2f}; the frozen final spread falls ({sp_frozen[3]:.2f} → {sp_frozen[4]:.2f} → {sp_frozen[5]:.2f}) below its {fit_frozen['eq_spread']:.2f} extrapolation.", INK, False),
    ], 15, 42)
    b.append(t)

    # caveat line
    cy = ry + 78
    t, _ = text_block(
        100, cy,
        f"Caveats: the linear drift fits explain little of the motion (R² = {fit_self['r2']:.2f} self-judge, "
        f"{fit_frozen['r2']:.2f} frozen-judge) — round-to-round movement is mostly stochastic, so each zero crossing is the "
        "faint mean of a noisy fit, not evidence for a stiff well. A cubic drift fit finds the bistability signature (two stable "
        "interior zero-crossings) in only about one in five bootstrap resamples over rollouts (19% in the report's fit, "
        "17% recomputed here). OLMo-organism runs (not shown) pin to the 1.0 rail under both judges (extrapolated zeros ≈ 1.03–1.05).",
        14.5, 168, GRAY)
    b.append(t)

    # takeaway box
    ky = cy + 86
    b.append(box(100, ky, 1200, 118, KEY_FILL, INK, 2.5))
    t, _ = rich_text(120, ky + 34, [
        ("Takeaway: ", INK, True),
        ("both judge conditions have statistically indistinguishable negative fitted slopes, but boundedness and "
         "measurement error can induce mean reversion. Descriptively, the ", INK, False),
        (f"self-judge fit crosses zero mid-range (x* = {fit_self['xstar']:.2f}) and its final fan is close to the fitted stationary spread;", BLUE, True),
        ("the ", INK, False),
        (f"frozen-judge fit crosses lower (x* = {fit_frozen['xstar']:.2f}) and ends below its stationary extrapolation.", GREEN, True),
        ("The data reject a robust two-well saddle more clearly than they establish one physical attractor.", INK, False),
    ], 17, 130)
    b.append(t)

    H = ky + 152
    doc = svg_doc(W, H, "\n".join(b))
    out = os.path.join(HERE, "basin-drift-field.svg")
    with open(out, "w") as f:
        f.write(doc)
    print("wrote", out)


if __name__ == "__main__":
    main()

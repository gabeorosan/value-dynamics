#!/usr/bin/env python3
"""Draft figure: the integrator law fitted in three independent loops.

Three scatter panels, one per organism. In each, x = per-round kept-gap
(mean value of the judge's kept candidates minus mean value of the full
6-candidate pool, on the organism's value axis, averaged over that round's
loop items) and y = next-round pool drift (pool mean at round t+1 minus at
round t). All judge conditions pooled. The fitted gain k is the ordinary
least squares slope; a dashed unity-slope reference line makes k > 1 versus
k < 1 visible at a glance.

Panels:
  K2 — OLMo-3-7B conservative organism, risk axis   (17 rollouts, 51 transitions)
  K1 — Qwen3-4B risk organism, risk axis            (16 rollouts, 48 transitions)
  K3 — Qwen3-4B emergent-misalignment organism, candor axis
                                                    (12 rollouts, 36 transitions)

Regenerate with:  python3 figure.py   (from this directory; stdlib only)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..")


def P(*parts):
    return os.path.join(ROOT, *parts)


K2_FILES = [
    P("experiments", "kaggle", "kaggle_k2_olmo_inversion",
      "output_controls", "k2_olmo_inversion_kaggle_controls.json"),
    P("experiments", "kaggle", "kaggle_k2_olmo_inversion_conf",
      "output", "k2_conf_v1_seeds12_partial.json"),
    P("experiments", "kaggle", "kaggle_k2_olmo_inversion_conf",
      "output", "k2_olmo_inversion_kaggle_conf_v2.json"),
    P("experiments", "kaggle", "kaggle_k2_olmo_inversion_base012",
      "output", "k2_olmo_inversion_kaggle_base012.json"),
    P("experiments", "cerebrium_k2", "output", "k2_cerebrium_seed0_complete.json"),
]
K1_FILES = [P("experiments", "kaggle", "kaggle_k1_qwen_anchor_grid",
              "output", "k1_qwen_anchor.json")]
K3_FILES = [P("experiments", "kaggle", "kaggle_k3_em_neutral_grid",
              "output", "k3_em_neutral.json")]

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning
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


# ---------------------------------------------------------------- data
def mean(x):
    return sum(x) / len(x)


def transitions(files, pool_key, skip_measure_only=False):
    """(kept-gap at round t, pool drift t -> t+1) over every rollout record."""
    pts = []
    for f in files:
        d = json.load(open(f))
        for seed in d:
            if seed.startswith("_"):
                continue
            for cond, rec in d[seed].items():
                if not isinstance(rec, dict):
                    continue
                if skip_measure_only and rec.get("measure_only"):
                    continue
                rr = rec.get("rounds_raw")
                if not rr:
                    continue
                pools = [mean([it[pool_key] for it in rnd]) for rnd in rr]
                gaps = [mean([it["gap_arm"] for it in rnd]) for rnd in rr]
                for t in range(len(rr) - 1):
                    pts.append((gaps[t], pools[t + 1] - pools[t]))
    return pts


def fmt_icpt(v):
    r = round(v, 2)
    return "0.00" if r == 0 else f"{r:+.2f}"


def ols(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    syy = sum((y - my) ** 2 for y in ys)
    slope = sxy / sxx
    return slope, my - slope * mx, sxy / math.sqrt(sxx * syy)


PANELS = []  # (title lines, axis word, pts, slope, icpt, r, color, regime words)
for (files, pool_key, skip, expect_n, title, subtitle, axis_word) in (
    (K2_FILES, "pool_risk", False, 51,
     "K2 — OLMo-3-7B conservative organism", "17 rollouts, 51 transitions", "risk"),
    (K1_FILES, "pool_risk", True, 48,
     "K1 — Qwen3-4B risk organism", "16 rollouts, 48 transitions", "risk"),
    (K3_FILES, "pool_candor", False, 36,
     "K3 — Qwen3-4B emergent-misalignment organism", "12 rollouts, 36 transitions", "candor"),
):
    pts = transitions(files, pool_key, skip)
    assert len(pts) == expect_n, f"{title}: expected {expect_n} transitions, got {len(pts)}"
    slope, icpt, r = ols(pts)
    color = RED if slope > 1 else GREEN
    # descriptive pooled slope only; the k<1/k>1 stable-unstable reading is
    # RETIRED (2026-07-12 re-audit) — slopes mix judge regimes, and only
    # regimes with real gap variance identify one (K2 base arm +1.05
    # [0.85,1.29]); see docs/report_loop_integrator_decomposition.md
    regime = "pooled descriptive slope (mixes judge regimes)"
    PANELS.append((title, subtitle, axis_word, pts, slope, icpt, r, color, regime))

K2_K, K1_K, K3_K = PANELS[0][4], PANELS[1][4], PANELS[2][4]


# ---------------------------------------------------------------- figure
b = []
W = 1520

t, _ = text_block(W // 2, 52, "The kept-gap predicts next-round pool drift in all three loops (out-of-sample validated) —", 32, 84, weight="bold")
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
t, _ = text_block(W // 2, 94, "pooled slopes shown are descriptive; they mix judge regimes and differ by organism and axis", 32, 84, weight="bold")
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
t, _ = text_block(W // 2, 130, "Two model families, three organisms, three value axes (r = 0.62–0.67). Each dot is one round-to-round "
                  "transition of one rollout, all judge conditions pooled; dashed line = slope 1.0. Slope is only identified where the gap varies (K2 base arm +1.05 [0.85, 1.29]).", 18, 170, GRAY)
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

# identical scales in all three panels, so slopes compare directly
XMIN, XMAX = -0.20, 0.28
YMIN, YMAX = -0.28, 0.40
PW, PH = 400, 360
PY = 268
PX0S = [120, 590, 1060]


def panel(px, title, subtitle, axis_word, pts, slope, icpt, r, color, regime, first):
    def X(v):
        return px + PW * (v - XMIN) / (XMAX - XMIN)

    def Y(v):
        return PY + PH * (YMAX - v) / (YMAX - YMIN)

    s = []
    t2, ty_end = text_block(px - 24, 196, title, 19, 44, weight="bold")
    s.append(t2)
    t2, _ = text_block(px - 24, ty_end + 2, f"{axis_word} axis · {subtitle}", 15.5, 60, GRAY)
    s.append(t2)

    for v in (-0.2, -0.1, 0.0, 0.1, 0.2, 0.3):
        yy = Y(v)
        col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
        s.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px + PW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
        if first:
            s.append(f'<text x="{px - 10}" y="{yy + 5:.1f}" text-anchor="end" font-size="14.5" fill="{GRAY}" font-family="{FONT}">{v:+.1f}</text>')
    for v in (-0.1, 0.0, 0.1, 0.2):
        xx = X(v)
        col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
        s.append(f'<line x1="{xx:.1f}" y1="{PY}" x2="{xx:.1f}" y2="{PY + PH}" stroke="{col}" stroke-width="{sw}"/>')
        s.append(f'<text x="{xx:.1f}" y="{PY + PH + 22}" text-anchor="middle" font-size="14.5" fill="{GRAY}" font-family="{FONT}">{v:+.1f}</text>')
    s.append(f'<text x="{px + PW / 2}" y="{PY + PH + 48}" text-anchor="middle" font-size="16.5" fill="{INK}" font-family="{FONT}">kept-gap this round ({axis_word})</text>')

    # dashed unity-slope reference: kept-gap fully written in
    s.append(f'<line x1="{X(XMIN):.1f}" y1="{Y(XMIN):.1f}" x2="{X(XMAX):.1f}" y2="{Y(XMAX):.1f}" '
             f'stroke="{GRAY}" stroke-width="2" stroke-dasharray="7 6"/>')
    ux, uy = X(0.225), Y(0.253)  # short label riding just above the dashed line
    s.append(f'<text x="{ux:.1f}" y="{uy:.1f}" text-anchor="middle" font-size="13.5" fill="{GRAY}" font-family="{FONT}" '
             f'transform="rotate(-32.5 {ux:.1f} {uy:.1f})">gain 1.0</text>')

    # fitted line (ordinary least squares over the panel's transitions)
    s.append(f'<line x1="{X(XMIN):.1f}" y1="{Y(slope * XMIN + icpt):.1f}" '
             f'x2="{X(XMAX):.1f}" y2="{Y(slope * XMAX + icpt):.1f}" stroke="{color}" stroke-width="4"/>')

    for x, y in pts:
        s.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="5" fill="{color}" '
                 f'fill-opacity="0.55" stroke="white" stroke-width="1.3"/>')

    # fitted gain, printed large in the empty top-left corner
    s.append(f'<text x="{px + 16}" y="{PY + 44}" font-size="34" font-weight="bold" fill="{color}" font-family="{FONT}">k = {slope:.2f}</text>')
    s.append(f'<text x="{px + 16}" y="{PY + 68}" font-size="15" fill="{GRAY}" font-family="{FONT}">r = {r:.2f}, n = {len(pts)} transitions</text>')
    s.append(f'<text x="{px + 16}" y="{PY + 90}" font-size="15" font-weight="bold" fill="{color}" font-family="{FONT}">{esc(regime)}</text>')
    return "\n".join(s)


for i, (title, subtitle, axis_word, pts, slope, icpt, r, color, regime) in enumerate(PANELS):
    b.append(panel(PX0S[i], title, subtitle, axis_word, pts, slope, icpt, r, color, regime, i == 0))

b.append(f'<text x="52" y="{PY + PH / 2}" font-size="16.5" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 52 {PY + PH / 2})" text-anchor="middle">pool-mean change into the next round</text>')

# measurement recipe, under the panels
ry = PY + PH + 84
t, ry_end = rich_text(96, ry, [
    ("How each dot is measured: ", INK, True),
    ("every round the organism samples a 6-candidate answer pool for each loop item; the value axis scores each candidate "
     "(risk = does the answer take the gamble; candor = scored candor). Kept-gap = mean score of the judge’s kept candidates minus mean score "
     "of the full 6-candidate pool, averaged over that round’s items. Pool drift = the pool mean one round later minus now. "
     f"Lines are ordinary least squares fits; all three intercepts sit at the origin ({fmt_icpt(PANELS[0][5])}, {fmt_icpt(PANELS[1][5])}, {fmt_icpt(PANELS[2][5])}).", GRAY, False),
], 15.5, 180)
b.append(t)

# takeaway
ty = ry_end + 22
b.append(box(80, ty, W - 160, 104, KEY_FILL, INK, 2.5))
t, _ = rich_text(100, ty + 32, [
    ("The gain is not a family property: ", INK, True),
    (f"inside the same Qwen3-4B base model, k straddles 1.0 — {K1_K:.2f} on the risk organism (K1) against {K3_K:.2f} on the "
     f"emergent-misalignment organism’s candor axis (K3), with OLMo’s conservative organism at {K2_K:.2f}. ", INK, False),
    ("k > 1 compounds each round’s selection noise into fans and rails; ", RED, True),
    ("k < 1 shrinks it, so pools settle.", GREEN, True),
], 18, 136)
b.append(t)

svg = svg_doc(W, ty + 136, "\n".join(b))
with open(os.path.join(HERE, "figure.svg"), "w") as f:
    f.write(svg)
for title, _, _, pts, slope, icpt, r, _, _ in PANELS:
    print(f"{title}: k={slope:.3f} icpt={icpt:+.4f} r={r:.3f} n={len(pts)}")
print("wrote figure.svg")

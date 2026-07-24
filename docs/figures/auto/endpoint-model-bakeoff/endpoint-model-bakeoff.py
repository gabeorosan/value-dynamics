#!/usr/bin/env python3
"""Draft figure: six endpoint-forecast models scored by CRPS, one panel per
model family (OLMo K2 grid, Qwen K1 grid), shared x-scale so the family
contrast reads directly. Climatology is drawn as a dashed red rule in each
panel: a state model must beat that line to prove the run's state carries
endpoint information.

Reads:  experiments/endpoint_model_bakeoff.json  (committed scorer output of
        scripts/analysis_endpoint_model_bakeoff.py)
Writes: endpoint-model-bakeoff.svg next to this script.
Style:  docs/figures/src/make_figures.py (Evans-lab house style).
Run:    python3 endpoint-model-bakeoff.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(
    HERE, "..", "..", "..", "..", "experiments", "endpoint_model_bakeoff.json"))

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
USER_FILL = "#cfe0f1"  # chat user box
ASST_FILL = "#eaf1f8"  # chat assistant box
KEY_FILL = "#eef5ee"   # highlighted takeaway box
BASE_FILL = "#f2f3f5"  # state-blind baseline bars (labeled directly)

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


def hbar(x, y, w, h, fill, stroke, sw=2.0, r=4):
    """Horizontal bar anchored at the zero baseline, rounded only at the
    data end (right)."""
    r = min(r, w / 2, h / 2)
    return (f'<path d="M {x:.1f} {y:.1f} h {w - r:.1f} a {r} {r} 0 0 1 {r} {r} '
            f'v {h - 2 * r:.1f} a {r} {r} 0 0 1 -{r} {r} h -{w - r:.1f} z" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def halo_text(x, y, s, size, color=INK, weight="bold", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight}" text-anchor="{anchor}" font-family="{FONT}" '
            f'stroke="white" stroke-width="4" paint-order="stroke">{esc(s)}</text>')


# ---------------------------------------------------------------- data
with open(DATA) as fh:
    data = json.load(fh)

ORDER = ["M0_LOGIT", "M0_POOL", "M0_BOOT", "M0", "CLIM", "PERSIST"]
LABELS = {  # (bold name in words, gray recipe subline with the JSON key)
    "M0_LOGIT": ("loop model, logit-bounded",
                 "pool update in logit space, stays in [0,1] (M0_LOGIT)"),
    "M0_POOL":  ("loop model, pooled slope",
                 "force slope fit on both families together (M0_POOL)"),
    "M0_BOOT":  ("loop model + bootstrap",
                 "adds parameter uncertainty per path (M0_BOOT)"),
    "M0":       ("loop model, current",
                 "linear update, additive Gaussian noise (M0)"),
    "CLIM":     ("climatology",
                 "training runs' endpoint spread, ignores state (CLIM)"),
    "PERSIST":  ("persistence",
                 "endpoint = round-1 pool, tiny spread (PERSIST)"),
}
WIN = "M0_LOGIT"


def paired_count(fam, model):
    """Parse '11/13 beat M0 ...' into ('11', '13')."""
    m = re.match(r"(\d+)/(\d+)", data[fam]["paired_vs_M0"][model])
    return m.group(1), m.group(2)


# sanity: the fixed display order must equal best-to-worst in BOTH families
for fam in ("k2_olmo", "k1_qwen"):
    crps = data[fam]["mean_crps"]
    assert ORDER == sorted(ORDER, key=lambda m: crps[m]), (fam, crps)

# ---------------------------------------------------------------- geometry
W = 1180
X0, X1 = 470, 1130          # plot area (value 0 at X0)
XMAX = 0.15
SX = (X1 - X0) / XMAX
TICKS = [0.0, 0.03, 0.06, 0.09, 0.12, 0.15]
ROW = 52
BAR_H = 28

b = []

# ---------------------------------------------------------------- headline
t, _ = rich_text(40, 54, [
    ("A ", INK, True), ("logit-bounded loop model", BLUE, True),
    (" forecasts endpoint preferences best —", INK, True)], 28, 200)
b.append(t)
t, _ = rich_text(40, 92, [
    ("but only the ", INK, True),
    ("OLMo family's endpoints are forecastable", GREEN, True),
    (" at all", INK, True)], 28, 200)
b.append(t)

t, y = text_block(
    40, 126,
    "Six forecast models, leave-one-run-out: each starts from a held-out "
    "run's round-1 state (pool preference p, judge-pool correlation rho, "
    "supply sigma) and forecasts that run's final-round pool preference with "
    "1,500 Monte-Carlo paths. Score: mean CRPS over held-out runs — lower is "
    "better.", 16.5, 122, GRAY)
b.append(t)

# ---------------------------------------------------------------- legend
ly = y + 18
lx = 40


def key_swatch(x, yc, fill, stroke):
    return (f'<rect x="{x}" y="{yc - 12}" width="24" height="15" rx="3" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>')


legend = [
    (key_swatch(lx, ly, BLUE, INK), "logit-bounded winner", 178),
    (key_swatch(lx, ly, USER_FILL, INK), "other state models", 168),
    (key_swatch(lx, ly, BASE_FILL, GRAY), "state-blind baselines", 182),
    (f'<line x1="{lx}" y1="{ly - 5}" x2="{lx + 24}" y2="{ly - 5}" '
     f'stroke="{RED}" stroke-width="2.5" stroke-dasharray="6 4"/>',
     "climatology line — beat it to earn the state", 350),
]
kx = lx
for swatch, label, adv in legend:
    b.append(swatch.replace(f'x="{lx}"', f'x="{kx}"')
                   .replace(f'x1="{lx}"', f'x1="{kx}"')
                   .replace(f'x2="{lx + 24}"', f'x2="{kx + 24}"'))
    b.append(f'<text x="{kx + 32}" y="{ly}" font-size="15" fill="{INK}" '
             f'font-family="{FONT}">{esc(label)}</text>')
    kx += 32 + adv

panel_y = ly + 34


# ---------------------------------------------------------------- one panel
def panel(y, fam, title_segments, clim_note2):
    d = data[fam]
    crps = d["mean_crps"]
    t, y2 = rich_text(40, y, title_segments, 19, 106)
    rows_y = y2 + 44
    axis_y = rows_y + len(ORDER) * ROW + 4
    s = [t]

    # gridlines + ticks
    for v in TICKS:
        x = X0 + v * SX
        s.append(f'<line x1="{x:.1f}" y1="{rows_y - 8}" x2="{x:.1f}" '
                 f'y2="{axis_y}" stroke="#e8eaec" stroke-width="1.5"/>')
        s.append(f'<text x="{x:.1f}" y="{axis_y + 22}" font-size="13.5" '
                 f'fill="{GRAY}" text-anchor="middle" font-family="{FONT}">'
                 f'{v:.2f}</text>')

    # bars
    for i, m in enumerate(ORDER):
        ry = rows_y + i * ROW
        val = crps[m]
        w = val * SX
        if m == WIN:
            fill, stroke = BLUE, INK
        elif m.startswith("M0"):
            fill, stroke = USER_FILL, INK
        else:
            fill, stroke = BASE_FILL, GRAY
        name, sub = LABELS[m]
        s.append(f'<text x="452" y="{ry + 15}" font-size="16.5" fill="{INK}" '
                 f'font-weight="bold" text-anchor="end" font-family="{FONT}">'
                 f'{esc(name)}</text>')
        s.append(f'<text x="452" y="{ry + 33}" font-size="12.5" fill="{GRAY}" '
                 f'text-anchor="end" font-family="{FONT}">{esc(sub)}</text>')
        s.append(hbar(X0, ry + 2, w, BAR_H, fill, stroke))
        if m == WIN:  # paired win-count, read from the file, inside the bar
            k, n = paired_count(fam, m)
            s.append(f'<text x="{X0 + 12}" y="{ry + 21.5}" font-size="13.5" '
                     f'fill="white" font-weight="bold" font-family="{FONT}">'
                     f'beats the current loop model in {k} of {n} paired runs'
                     f'</text>')
        if fam == "k1_qwen" and m == "CLIM":
            k, n = paired_count(fam, m)
            s.append(f'<text x="{X0 + 12}" y="{ry + 21.5}" font-size="13.5" '
                     f'fill="{INK}" font-weight="bold" font-family="{FONT}">'
                     f'beats the current loop model in {k} of {n} paired runs'
                     f'</text>')

    # climatology rule on top of the bars
    xc = X0 + crps["CLIM"] * SX
    s.append(f'<line x1="{xc:.1f}" y1="{rows_y - 34}" x2="{xc:.1f}" '
             f'y2="{axis_y}" stroke="{RED}" stroke-width="2.5" '
             f'stroke-dasharray="6 4"/>')
    s.append(halo_text(xc + 9, rows_y - 22, f'climatology {crps["CLIM"]:.4f}',
                       14.5, RED))
    s.append(halo_text(xc + 9, rows_y - 4, clim_note2, 14.5, RED))

    # value labels (drawn after the rule so the halo keeps them readable)
    for i, m in enumerate(ORDER):
        ry = rows_y + i * ROW
        s.append(halo_text(X0 + crps[m] * SX + 8, ry + 22, f'{crps[m]:.4f}', 16))

    # axis
    s.append(f'<line x1="{X0}" y1="{axis_y}" x2="{X1}" y2="{axis_y}" '
             f'stroke="{INK}" stroke-width="2"/>')
    t, _ = rich_text(X0, axis_y + 46, [
        ("← lower is better.  ", INK, True),
        ("mean CRPS of the final-pool forecast across held-out runs",
         GRAY, False)], 15, 120)
    s.append(t)
    return "\n".join(s), axis_y + 66


# ---------------------------------------------------------------- panel A
olmo = data["k2_olmo"]
gap_o = olmo["mean_crps"]["CLIM"] - olmo["mean_crps"][WIN]
seg_a = [
    (f'OLMo risk model, K2 grid — {olmo["n"]} held-out runs. ', INK, True),
    (f'The best state model beats climatology by {gap_o:.4f} CRPS '
     f'({olmo["mean_crps"][WIN]:.4f} minus {olmo["mean_crps"]["CLIM"]:.4f}): '
     'these endpoints are forecastable from the run’s state.',
     GREEN, True),
]
t, panel_y = panel(panel_y, "k2_olmo", seg_a, "beat this line to earn the state")
b.append(t)
panel_y += 26

# ---------------------------------------------------------------- panel B
qwen = data["k1_qwen"]
gap_q = qwen["mean_crps"]["CLIM"] - qwen["mean_crps"][WIN]
kq, nq = paired_count("k1_qwen", "CLIM")
seg_b = [
    (f'Qwen risk model, K1 grid — {qwen["n"]} held-out runs. ', INK, True),
    (f'The best state model edges climatology by only {gap_q:.4f} CRPS '
     f'({qwen["mean_crps"][WIN]:.4f} minus {qwen["mean_crps"]["CLIM"]:.4f}), '
     f'and climatology beats the current loop model in {kq} of {nq} paired '
     'runs: these endpoints are near-unpredictable from state.', RED, True),
]
t, panel_y = panel(panel_y, "k1_qwen", seg_b, "the state barely helps here")
b.append(t)

# ---------------------------------------------------------------- footnote
t, panel_y = text_block(
    40, panel_y + 14,
    "CRPS (continuous ranked probability score) grades the whole predictive "
    "distribution against the realized endpoint, not just the point "
    "forecast. That is why persistence — which looked competitive under mean "
    "absolute error — is the worst model in both families here: its forecast "
    "has essentially no spread, and CRPS charges for that.", 14.5, 148, GRAY)
b.append(t)

H = int(panel_y + 18)
svg = svg_doc(W, H, "\n".join(b))
out = os.path.join(HERE, "endpoint-model-bakeoff.svg")
with open(out, "w") as fh:
    fh.write(svg)
print(f"wrote {out}  ({W}x{H})")

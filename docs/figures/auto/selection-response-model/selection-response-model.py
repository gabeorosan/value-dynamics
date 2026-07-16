#!/usr/bin/env python3
"""Selection-response model figure for the value-dynamics project.

Owain Evans-lab house style (white background, headline finding, boxes with
verbatim math, bold arrows, real data with fat labels). Palette copied from
docs/figures/src/make_figures.py. Stdlib only; run from this directory:

    python3 selection-response-model.py

Reads:
  experiments/selection_response_predictor.json  (aggregates + scale audit)
  experiments/spread_util_unified.json           (290 per-round records)
Every printed aggregate is asserted against those JSONs below.
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# auto/<slug>/ -> figures -> docs -> repo root
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(ROOT, "experiments", "selection_response_predictor.json")
RECS = os.path.join(ROOT, "experiments", "spread_util_unified.json")

# ---- palette (verbatim from make_figures.py) -----------------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series
GREEN = "#3a7d44"      # accent / frozen-judge series
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions)
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"
DOC_FILL = "#fdf6e8"
KEY_FILL = "#eef5ee"
FONT = "Helvetica, Arial, sans-serif"


# ---- helpers (esc/wrap copied from make_figures.py) ----------------------
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


def T(x, y, s, size, color=INK, anchor="start", weight="normal", italic=False):
    st = f' font-style="italic"' if italic else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}"{st}>'
            f'{esc(s)}</text>')


def para(x, y, text, size, width, color=INK, lh=1.34, anchor="start",
         weight="normal"):
    out = []
    for i, ln in enumerate(wrap(text, width)):
        out.append(T(x, y + i * size * lh, ln, size, color, anchor, weight))
    return "\n".join(out), y + len(wrap(text, width)) * size * lh


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=10):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def arrow(x1, y1, x2, y2, sw=4, color=INK, marker="arr"):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#{marker})"/>')


DEFS = f'''<defs>
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"
 markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"
 markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker>
<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"
 markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{GREEN}"/></marker>
<marker id="arrB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"
 markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{BLUE}"/></marker>
</defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ==========================================================================
# Load + verify data
# ==========================================================================
def approx(a, b, tol=5e-4):
    return abs(a - b) <= tol


pred = json.load(open(PRED))
recs_all = json.load(open(RECS))["records"]
scored = [r for r in recs_all if r.get("rho") is not None]

# scatter data: x = rho * spread, y = observed selector gap
XY = [(r["rho"] * r["spread"], r["gap"]) for r in scored]
N = len(XY)

# recompute the headline scatter aggregates from the records
xs = [x for x, _ in XY]
ys = [y for _, y in XY]
unit_mae = sum(abs(y - x) for x, y in XY) / N
ybar = sum(ys) / N
ssres = sum((y - x) ** 2 for x, y in XY)
sstot = sum((y - ybar) ** 2 for y in ys)
unit_r2 = 1 - ssres / sstot
sx, sy = sum(xs), sum(ys)
sxx = sum(x * x for x in xs)
sxy = sum(x * y for x, y in XY)
fit_slope = (N * sxy - sx * sy) / (N * sxx - sx * sx)
fit_int = (sy - fit_slope * sx) / N

# aggregates as stored in the predictor JSON
gap_unit = pred["selector_gap"]["unit_agreement_spread_proxy"]["all"]
fit_json = pred["selector_gap"]["fitted_full_data_equation_description_only"][
    "intercept_slope"]
oneround = pred["one_round_before_selection"]
onr_unit = oneround["unit_agreement_spread_proxy"]["all"]["mae"]
onr_fit = oneround["current_fitted_LOCO"]["mae"]
ep = pred["endpoint_with_boundary_refresh"]["recommended_unit_agreement_spread"]
ep_frozen = pred["endpoint_with_boundary_refresh"][
    "current_fitted_frozen_sd_LOCO"]
scale = pred["scale_audit"]

# --- assertions: file is source of truth ---------------------------------
assert N == 290, N
assert gap_unit["n"] == 290
assert approx(gap_unit["r2"], 0.81037) and approx(unit_r2, 0.81037), unit_r2
assert approx(gap_unit["mae"], 0.042074) and approx(unit_mae, 0.042074), unit_mae
assert approx(fit_json[0], -0.002137) and approx(fit_int, -0.002137)
assert approx(fit_json[1], 0.958197) and approx(fit_slope, 0.958197)
assert approx(onr_unit, 0.090184) and approx(onr_fit, 0.089131)
assert ep["selection_driven_matched_to_current"]["n"] == 36
assert approx(ep["selection_driven_matched_to_current"]["mae"], 0.118117)
assert ep["judge_swap_refreshed"]["n"] == 9
assert approx(ep["judge_swap_refreshed"]["mae"], 0.209923)
assert approx(ep["combined_matched_to_current"]["mae"], 0.136478)
assert ep["direction_combined"]["n_moved"] == 38
assert ep["direction_combined"]["n_hits"] == 37
assert approx(ep_frozen["judge_swap_refreshed"]["mae"], 0.179366)
assert approx(scale["intensity_in_units_of_underlying_normal_sd"], 0.954481)


# ==========================================================================
# Build figure
# ==========================================================================
W = 1440
b = []

# ---- header --------------------------------------------------------------
b.append(T(W / 2, 54, "Selection converts offered variation into movement — with no fitted constants",
           31, INK, "middle", "bold"))
b.append(T(W / 2, 90, "Qwen + OLMo selection loops; candidate value scores 0–1; 290 agreement-scored rounds",
           18, GRAY, "middle"))

# ==========================================================================
# THE MODEL band
# ==========================================================================
b.append(T(60, 138, "THE MODEL — one turn of the loop: variation in, movement out",
           20, INK, "start", "bold"))
b.append(f'<line x1="60" y1="150" x2="{W-60}" y2="150" stroke="{GRAY}" stroke-width="1.5"/>')

# three operation boxes
BY, BH = 234, 250
b1x, b2x, b3x = 70, 550, 1030
BW = 340

# --- feedback arc (over the top): v_next becomes next round's generator ---
b.append(f'<path d="M {b3x+BW/2} {BY-6} C {b3x+BW/2} 186, {b1x+BW/2} 186, {b1x+BW/2} {BY-6}" '
         f'stroke="{BLUE}" stroke-width="3.5" fill="none" marker-end="url(#arrB)"/>')
b.append(T(W / 2, 178, "refit output v_next becomes the next round’s generator", 16.5, BLUE, "middle", "bold"))

# --- Box 1: generate a pool ---
b.append(box(b1x, BY, BW, BH, ASST_FILL))
b.append(T(b1x + 20, BY + 34, "1.  Generate a pool", 21, INK, "start", "bold"))
b.append(T(b1x + 20, BY + 70, "Sample candidate values for each prompt.", 16.5, INK))
b.append(T(b1x + 20, BY + 100, "pool mean  =  p", 18, INK, "start", "bold"))
b.append(T(b1x + 20, BY + 130, "within-prompt spread  =  σ", 18, INK, "start", "bold"))
t, _ = para(b1x + 20, BY + 160, "σ = mean across prompts of the population SD "
            "(ddof 0) of its candidate scores.", 14.5, 38, GRAY)
b.append(t)

# --- Box 2: select a retained set ---
b.append(box(b2x, BY, BW, BH, "white", RED, 3.5))
b.append(T(b2x + 20, BY + 32, "2.  Select a retained set", 21, RED, "start", "bold"))
b.append(T(b2x + 20, BY + 62, "Keep the judge-preferred candidates.", 16, INK))
b.append(T(b2x + 20, BY + 92, "selector gap  g  =  σ · a   (exact)", 18, INK, "start", "bold"))
t, _ = para(b2x + 20, BY + 114, "a = standardized selection differential "
            "(kept mean − pool mean) / σ.", 14, 44, GRAY)
b.append(t)
b.append(T(b2x + 20, BY + 176, "forecast substitutes  â = ρ", 18, BLUE, "start", "bold"))
t, _ = para(b2x + 20, BY + 198, "ρ = pre-selection judge/value agreement — a proxy for a, not an identity.",
            14, 44, GRAY)
b.append(t)

# --- Box 3: refit ---
b.append(box(b3x, BY, BW, BH, ASST_FILL))
b.append(T(b3x + 20, BY + 34, "3.  Refit", 21, INK, "start", "bold"))
b.append(T(b3x + 20, BY + 70, "Train the next model on the kept set.", 16.5, INK))
b.append(T(b3x + 20, BY + 104, "kept mean  k  =  p + g", 18, INK, "start", "bold"))
b.append(T(b3x + 20, BY + 134, "next value  v_next  ≈  k", 18, GREEN, "start", "bold"))
t, _ = para(b3x + 20, BY + 162, "k − host mean = training displacement "
            "(also carries any supplier shift).", 14.5, 38, GRAY)
b.append(t)

# arrows between boxes
b.append(arrow(b1x + BW + 6, BY + BH / 2, b2x - 8, BY + BH / 2, 5))
b.append(arrow(b2x + BW + 6, BY + BH / 2, b3x - 8, BY + BH / 2, 5))

# --- supplier inlet into the pool (mixed pools) ---
sy = BY + BH + 26
b.append(box(b1x, sy, 470, 52, DOC_FILL, GREEN, 2.5))
b.append(T(b1x + 18, sy + 32, "mixed pool:  pool mean = (1−u)·host mean + u·supplier mean",
           16, INK, "start", "bold"))
b.append(f'<path d="M {b1x+235} {sy} L {b1x+235} {BY+BH+6}" stroke="{GREEN}" '
         f'stroke-width="3.5" marker-end="url(#arrG)"/>')

# ==========================================================================
# Model insets: cross-entropy analogue (left) + endpoint recurrence (right)
# ==========================================================================
IY = sy + 92
IH = 210
# --- CEM analogue inset ---
cx0 = 70
cw = 640
b.append(box(cx0, IY, cw, IH, "white", GRAY, 2))
b.append(T(cx0 + 18, IY + 30, "Algorithmic analogue: the cross-entropy method", 17, INK, "start", "bold"))
b.append(T(cx0 + 18, IY + 52, "sample → keep elites → update mean and variance   (analogue, not the same algorithm)",
           13.5, GRAY))

# three mini distributions
def bell(cx, base, spread, color, opacity=1.0, sw=2.5):
    pts = []
    for i in range(41):
        u = -2.4 + 4.8 * i / 40
        yy = math.exp(-0.5 * (u / (spread)) ** 2)
        px = cx + u * 26
        py = base - yy * 46
        pts.append(f"{px:.1f},{py:.1f}")
    return (f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-opacity="{opacity}"/>')

base = IY + IH - 34
b.append(bell(cx0 + 110, base, 1.15, INK))
b.append(T(cx0 + 110, base + 22, "sampled pool", 13.5, INK, "middle"))
b.append(bell(cx0 + 320, base, 0.62, RED))
b.append(T(cx0 + 320, base + 22, "keep elites → refit narrows", 13.5, RED, "middle"))
b.append(bell(cx0 + 540, base, 0.6, RED, 0.35))
b.append(bell(cx0 + 540, base, 1.05, GREEN))
b.append(T(cx0 + 540, base + 22, "supplier reopens support", 13.5, GREEN, "middle"))
b.append(arrow(cx0 + 165, base - 24, cx0 + 262, base - 24, 3.5, RED, "arrR"))
b.append(arrow(cx0 + 375, base - 24, cx0 + 480, base - 24, 3.5, GREEN, "arrG"))

# --- endpoint frozen-boundary recurrence inset ---
rx0 = 740
rw = 630
b.append(box(rx0, IY, rw, IH, "white", GRAY, 2))
b.append(T(rx0 + 18, IY + 30, "Endpoint: iterate with a frozen selection boundary", 17, INK, "start", "bold"))
b.append(box(rx0 + 18, IY + 48, rw - 36, 46, KEY_FILL, INK, 2))
b.append(T(rx0 + rw / 2, IY + 78, "m_next  =  clip( (1−u)·m + u·supplier + ρσ ,  0, 1 )",
           19, INK, "middle", "bold"))
t, _ = para(rx0 + 18, IY + 120, "Each round the kept mean lands one gap g = ρσ above the "
            "supply-updated pool; the clip holds it inside the 0–1 score range. "
            "Re-measure ρ and σ only when the judge, judging format, or pool "
            "policy changes.", 14.5, 74, INK)
b.append(t)

# ==========================================================================
# THE EVIDENCE band
# ==========================================================================
EY = IY + IH + 40
b.append(T(60, EY, "THE EVIDENCE — the unit line fits without tuning; endpoints follow the same recurrence",
           20, INK, "start", "bold"))
b.append(f'<line x1="60" y1="{EY+12}" x2="{W-60}" y2="{EY+12}" stroke="{GRAY}" stroke-width="1.5"/>')

# --- scatter: observed selector gap vs rho*sigma ---
px, py = 130, EY + 78
pw, ph = 560, 470
dlo, dhi = -0.5, 0.42

def SX(v):
    return px + pw * (v - dlo) / (dhi - dlo)


def SY(v):
    return py + ph * (dhi - v) / (dhi - dlo)

# frame
b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="#fbfbf9" '
         f'stroke="{GRAY}" stroke-width="1.5"/>')
# gridlines + ticks
for v in (-0.4, -0.2, 0.0, 0.2, 0.4):
    gx, gy = SX(v), SY(v)
    b.append(f'<line x1="{gx}" y1="{py}" x2="{gx}" y2="{py+ph}" stroke="#e9e9e4" stroke-width="1"/>')
    b.append(f'<line x1="{px}" y1="{gy}" x2="{px+pw}" y2="{gy}" stroke="#e9e9e4" stroke-width="1"/>')
    b.append(T(gx, py + ph + 24, f"{v:g}", 14.5, GRAY, "middle"))
    b.append(T(px - 10, gy + 5, f"{v:g}", 14.5, GRAY, "end"))
# zero axes bolder
b.append(f'<line x1="{SX(0)}" y1="{py}" x2="{SX(0)}" y2="{py+ph}" stroke="#cfcfc8" stroke-width="1.6"/>')
b.append(f'<line x1="{px}" y1="{SY(0)}" x2="{px+pw}" y2="{SY(0)}" stroke="#cfcfc8" stroke-width="1.6"/>')

# fitted calibration line (faint) then the unit line (main visual, on top)
b.append(f'<line x1="{SX(dlo)}" y1="{SY(fit_int + fit_slope*dlo)}" '
         f'x2="{SX(dhi)}" y2="{SY(fit_int + fit_slope*dhi)}" stroke="{GRAY}" '
         f'stroke-width="2" stroke-dasharray="7 5"/>')
# points
for x, y in XY:
    b.append(f'<circle cx="{SX(x):.1f}" cy="{SY(y):.1f}" r="4.1" fill="{BLUE}" '
             f'fill-opacity="0.42" stroke="{BLUE}" stroke-width="0.6"/>')
# unit slope reference line (the headline)
b.append(f'<line x1="{SX(dlo)}" y1="{SY(dlo)}" x2="{SX(dhi)}" y2="{SY(dhi)}" '
         f'stroke="{INK}" stroke-width="3.2"/>')
b.append(T(SX(0.30) + 8, SY(0.30) - 8, "gap = ρσ", 17, INK, "start", "bold"))

# axis labels
b.append(T(px + pw / 2, py + ph + 52, "forecast  ρσ  =  judge/value agreement × offered spread",
           17, INK, "middle", "bold"))
b.append(f'<text x="{px-64}" y="{py+ph/2}" font-family="{FONT}" font-size="17" '
         f'fill="{INK}" font-weight="bold" text-anchor="middle" '
         f'transform="rotate(-90 {px-64} {py+ph/2})">observed selector gap  g  (kept mean − pool mean)</text>')

# readout callouts on the plot
b.append(box(px + 14, py + 14, 246, 96, "white", INK, 2))
b.append(T(px + 28, py + 40, "Unit proxy (no fitted constants)", 15, INK, "start", "bold"))
b.append(T(px + 28, py + 64, f"R² {gap_unit['r2']:.3f}   MAE {gap_unit['mae']:.4f}", 15.5, INK))
b.append(T(px + 28, py + 88, f"fit for reference: {fit_json[0]:+.3f} + {fit_json[1]:.3f}·ρσ",
           14, GRAY))

# crossed-out 0.9545 note
noteY = py + ph + 84
b.append(f'<text x="{px}" y="{noteY}" font-family="{FONT}" font-size="13.5" '
         f'fill="{GRAY}" text-decoration="line-through">0.9545 theoretical line (not drawn)</text>')
b.append(f'<line x1="{px-2}" y1="{noteY-5}" x2="{px+228}" y2="{noteY-5}" stroke="{RED}" stroke-width="1.6"/>')
t, _ = para(px, noteY + 20, "— it uses the underlying normal SD, not the realized "
            "six-candidate SD used here.", 13.5, 62, GRAY)
b.append(t)

# --- right column: forecast horizon + endpoint evidence ---
ecx = 760
ew = 610
# one-round forecast box
b.append(box(ecx, py, ew, 132, DOC_FILL, INK, 2.5))
b.append(T(ecx + 20, py + 32, "One round ahead: forecast the next value", 18, INK, "start", "bold"))
t, _ = para(ecx + 20, py + 58, "Predicting v_next before selection with the unit proxy is as "
            "accurate as the fitted line — the extra constant buys nothing.", 15, 62, INK)
b.append(t)
b.append(T(ecx + 20, py + 116, f"value MAE  {onr_unit:.4f}  unit proxy    vs    {onr_fit:.4f}  fitted",
           16.5, RED, "start", "bold"))

# endpoint evidence box
eby = py + 156
EPBH = 344
b.append(box(ecx, eby, ew, EPBH, "white", INK, 2.5))
b.append(T(ecx + 20, eby + 34, "Where the loop lands: unit recurrence + boundary refresh",
           17.5, INK, "start", "bold"))
b.append(T(ecx + 20, eby + 58, "endpoint error = |predicted − measured final value|",
           14, GRAY))

rows = [
    ("selection-driven endpoints", f"MAE {ep['selection_driven_matched_to_current']['mae']:.3f}",
     "36 runs", GREEN, None),
    ("judge swaps", f"MAE {ep['judge_swap_refreshed']['mae']:.3f}",
     "9 runs", RED, f"fitted frozen-SD comparator {ep_frozen['judge_swap_refreshed']['mae']:.3f} — swaps still the weak spot"),
    ("combined", f"MAE {ep['combined_matched_to_current']['mae']:.4f}",
     f"{ep['direction_combined']['n_hits']}/{ep['direction_combined']['n_moved']} large directions right", INK, None),
]
ry = eby + 92
for name, val, sub, col, note in rows:
    b.append(box(ecx + 20, ry, ew - 40, 62, "#f7f7f4", col, 2))
    b.append(T(ecx + 36, ry + 27, name, 16.5, col, "start", "bold"))
    b.append(T(ecx + 36, ry + 50, sub, 13.5, GRAY))
    b.append(T(ecx + ew - 56, ry + 34, val, 20, col, "end", "bold"))
    if note:
        b.append(T(ecx + 36, ry + 78, note, 13.5, GRAY))
        ry += 96
    else:
        ry += 74

HGT = max(eby + EPBH, noteY + 40) + 36
svg = svg_doc(W, HGT, "\n".join(b))
out = os.path.join(HERE, "selection-response-model.svg")
with open(out, "w") as f:
    f.write(svg)
print("wrote", out, f"({W}x{HGT})")
print(f"scatter: N={N} unit R2={unit_r2:.5f} MAE={unit_mae:.5f} "
      f"fit={fit_int:+.4f}+{fit_slope:.4f}rho*sigma")

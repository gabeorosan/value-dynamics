#!/usr/bin/env python3
"""Draft figure: selection loops move the OLMo risk model's behavior massively
while its stated risk tolerance barely follows — near-total channel decoupling.

Panel A: per-rollout change in stated tolerance against change in behavior,
with a slope-1 "perfect tracking" reference and the fitted near-zero slope.
Panel B: mean tracking ratio by condition group against the same slope-1 bar.

Data: experiments/selfreport_calibration_k2.json (46 K2-chassis rollouts).
Regenerate with:  python3 selfreport-decoupling.py   (stdlib only)
"""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
DATA = os.path.join(ROOT, "experiments", "selfreport_calibration_k2.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (house palette)
GREEN = "#3a7d44"
RED = "#b5342c"        # emphasis for reversal / warning
GRAY = "#6b7684"       # recessive only (axes, muted captions, excluded dots)
PURPLE = "#8a5a9e"
AMBER = "#c07d18"
TEAL = "#0aa1a1"       # sixth categorical slot, validated against the other five
KEY_FILL = "#eef5ee"

FONT = "Helvetica, Arial, sans-serif"
BODY = 19


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


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4):
    lines = wrap(text, width)
    svg = []
    for i, ln in enumerate(lines):
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def rich_text(x, y, segments, size, width, lh=1.38):
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
            f'<tspan fill="{c}" font-weight="{"bold" if b else "normal"}">{esc(w)} </tspan>'
            for w, c, b in ln)
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" '
                   f'font-size="{size}">{tspans}</text>')
    return "\n".join(svg), y + len(out) * size * lh


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def marker(x, y, shape, color, s=7.5):
    if shape == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "square":
        return (f'<rect x="{x - s:.1f}" y="{y - s:.1f}" width="{2 * s}" height="{2 * s}" '
                f'fill="{color}" stroke="white" stroke-width="1.5"/>')
    if shape == "triangle":
        pts = f"{x:.1f},{y - s - 1:.1f} {x - s - 1:.1f},{y + s:.1f} {x + s + 1:.1f},{y + s:.1f}"
        return f'<polygon points="{pts}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "invtriangle":
        pts = f"{x:.1f},{y + s + 1:.1f} {x - s - 1:.1f},{y - s:.1f} {x + s + 1:.1f},{y - s:.1f}"
        return f'<polygon points="{pts}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "diamond":
        pts = (f"{x:.1f},{y - s - 1.5:.1f} {x + s + 1:.1f},{y:.1f} "
               f"{x:.1f},{y + s + 1.5:.1f} {x - s - 1:.1f},{y:.1f}")
        return f'<polygon points="{pts}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "pentagon":
        pts = []
        for k in range(5):
            a = -math.pi / 2 + 2 * math.pi * k / 5
            pts.append(f"{x + (s + 1) * math.cos(a):.1f},{y + (s + 1) * math.sin(a):.1f}")
        return f'<polygon points="{" ".join(pts)}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    return ""


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- data
d = json.load(open(DATA))
ROLLOUTS = d["rollouts"]
THRESH = d["moved_threshold"]           # 0.15
AGG = d["aggregates"]
assert len(ROLLOUTS) == 46, f"expected 46 rollouts, got {len(ROLLOUTS)}"

MOVED = [r for r in ROLLOUTS if abs(r["d_traj"]) >= THRESH]
STILL = [r for r in ROLLOUTS if abs(r["d_traj"]) < THRESH]

xs = [r["d_traj"] for r in MOVED]
ys = [r["d_sr"] for r in MOVED]
n = len(xs)
mx, my = sum(xs) / n, sum(ys) / n
sxx = sum((x - mx) ** 2 for x in xs)
sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
syy = sum((y - my) ** 2 for y in ys)
SLOPE = sxy / sxx
ICPT = my - SLOPE * mx
R = sxy / math.sqrt(sxx * syy)

GAP0 = AGG["overall"]["mean_gap_r0"]
GAPF = AGG["overall"]["mean_gap_final"]
SR_FINAL = [r["sr"][-1] for r in ROLLOUTS]
TRAJ_FINAL = [r["traj"][-1] for r in ROLLOUTS]

# (group key, color, marker, display name)
GROUPS = [
    ("oracle", RED, "diamond", "oracle-judge reversals"),
    ("h2h_duels", BLUE, "circle", "head-to-head duels"),
    ("mixed_injection", GREEN, "square", "mixed data injection"),
    ("k2_grid", PURPLE, "triangle", "K2 judge grid: frozen, self, random"),
    ("other", AMBER, "invtriangle", "press-depth runs"),
    ("release_holds_rescues", TEAL, "pentagon", "release holds and rescues"),
]
STYLE = {g: (c, s, lbl) for g, c, s, lbl in GROUPS}

S21 = next(r for r in ROLLOUTS if r["cond"] == "oracle_hold" and r["seed"] == "21")
S54 = next(r for r in ROLLOUTS if r["cond"] == "h2h_invade_self" and r["seed"] == "54")

# ---------------------------------------------------------------- figure
b = []
W = 1500

b.append(ctext(W // 2, 52, "Selection moves the behavior; the OLMo risk model's "
               "self-description barely moves", 31, INK, "bold"))
b.append(ctext(W // 2, 90, "Each dot is one selection-loop rollout of the OLMo risk model "
               "(K2 chassis). Change = final round minus round 0, on two probes run at the "
               "same checkpoints:", BODY, GRAY))
b.append(ctext(W // 2, 117, "behavior = P(choose the riskier option) on held-out EV-neutral "
               "A/B gambles;  stated = P(describes itself as the risk-tolerant one), "
               "order-balanced forced choice.", BODY, GRAY))

# ================= Panel A: per-rollout scatter, equal axes =================
AX, AY, AW, AH = 150, 250, 600, 600
LIM = 0.95  # both axes span -LIM..+LIM at the same scale


def ax_(v):
    return AX + AW * (v + LIM) / (2 * LIM)


def ay_(v):
    return AY + AH * (LIM - v) / (2 * LIM)


b.append(f'<text x="{AX - 40}" y="220" font-size="22" font-weight="bold" fill="{INK}" '
         f'font-family="{FONT}">A. Behavior change against stated change, one dot per moved rollout</text>')

for v in (-0.8, -0.4, 0.0, 0.4, 0.8):
    yy, xx = ay_(v), ax_(v)
    col, sw = (INK, 2) if v == 0 else ("#e4e4e0", 1)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{AX - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:+.1f}</text>')
    b.append(f'<line x1="{xx:.1f}" y1="{AY}" x2="{xx:.1f}" y2="{AY + AH}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{xx:.1f}" y="{AY + AH + 28}" text-anchor="middle" font-size="18" fill="{GRAY}" font-family="{FONT}">{v:+.1f}</text>')
b.append(f'<text x="{AX + AW / 2}" y="{AY + AH + 60}" text-anchor="middle" font-size="{BODY}" '
         f'fill="{INK}" font-family="{FONT}">change in risk behavior over the rollout (final round minus round 0)</text>')
b.append(f'<text x="{AX - 76}" y="{AY + AH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 76} {AY + AH / 2})" text-anchor="middle">'
         f'change in stated risk tolerance (final round minus round 0)</text>')

# slope-1 reference: perfect tracking (both axes share one scale, so it is the diagonal)
b.append(f'<line x1="{ax_(-LIM):.1f}" y1="{ay_(-LIM):.1f}" x2="{ax_(LIM):.1f}" y2="{ay_(LIM):.1f}" '
         f'stroke="{GRAY}" stroke-width="2.5" stroke-dasharray="8 7"/>')
dlx, dly = ax_(0.66), ay_(0.66) - 13
b.append(f'<text x="{dlx:.1f}" y="{dly:.1f}" text-anchor="middle" font-size="18" fill="{GRAY}" '
         f'font-family="{FONT}" transform="rotate(-45 {dlx:.1f} {dly:.1f})">'
         f'perfect tracking (slope 1)</text>')

# fitted line through the moved rollouts
fx1, fx2 = -0.9, 0.9
b.append(f'<line x1="{ax_(fx1):.1f}" y1="{ay_(SLOPE * fx1 + ICPT):.1f}" '
         f'x2="{ax_(fx2):.1f}" y2="{ay_(SLOPE * fx2 + ICPT):.1f}" stroke="{INK}" stroke-width="3.5"/>')
flx, fly = AX + 22, ay_(0.20)
b.append(f'<rect x="{flx - 12:.1f}" y="{fly - 27:.1f}" width="356" height="64" rx="8" fill="white" fill-opacity="0.92"/>')
b.append(f'<text x="{flx:.1f}" y="{fly:.1f}" font-size="21" font-weight="bold" fill="{INK}" '
         f'font-family="{FONT}">actual fit: stated &#8776; {SLOPE:.2f} &#215; behavior</text>')
b.append(f'<text x="{flx:.1f}" y="{fly + 26:.1f}" font-size="18" fill="{GRAY}" font-family="{FONT}">'
         f'r = {R:.2f} across the {n} moved rollouts</text>')

# dots — excluded (behavior barely moved) first, recessive
for r in STILL:
    b.append(f'<circle cx="{ax_(r["d_traj"]):.1f}" cy="{ay_(r["d_sr"]):.1f}" r="5" '
             f'fill="none" stroke="{GRAY}" stroke-width="2"/>')
for r in MOVED:
    color, shape, _ = STYLE[r["group"]]
    b.append(marker(ax_(r["d_traj"]), ay_(r["d_sr"]), shape, color))

# legend, upper-left of the panel (that quadrant is empty of dots)
b.append(f'<rect x="{AX + 8}" y="{AY + 8}" width="420" height="196" rx="8" fill="white" fill-opacity="0.92"/>')
ly = AY + 30
for g, color, shape, label in GROUPS:
    nm = sum(1 for r in MOVED if r["group"] == g)
    b.append(marker(AX + 28, ly - 6, shape, color))
    b.append(f'<text x="{AX + 46}" y="{ly}" font-size="17" fill="{INK}" font-family="{FONT}">'
             f'{esc(label)} ({nm} moved)</text>')
    ly += 27
b.append(f'<circle cx="{AX + 28}" cy="{ly - 6}" r="5" fill="none" stroke="{GRAY}" stroke-width="2"/>')
b.append(f'<text x="{AX + 46}" y="{ly}" font-size="17" fill="{GRAY}" font-family="{FONT}">'
         f'moved less than {THRESH:g} — excluded from fit ({len(STILL)})</text>')

# callout: oracle reversal, seed 21 (lower-left quadrant is empty)
c21x, c21y = ax_(S21["d_traj"]), ay_(S21["d_sr"])
t, t21_end = rich_text(AX + 22, ay_(-0.44), [
    ("Oracle judge reverses the trained value (seed 21):", RED, True),
    (f'behavior {S21["traj"][0]:.2f}→{S21["traj"][-1]:.2f} while stated '
     f'{S21["sr"][0]:.2f}→{S21["sr"][-1]:.2f}', INK, False)], 17, 34)
b.append(t)
b.append(f'<line x1="{AX + 90:.1f}" y1="{ay_(-0.44) - 22:.1f}" x2="{c21x:.1f}" y2="{c21y + 14:.1f}" '
         f'stroke="{RED}" stroke-width="2"/>')

# callout: duel invasion rails the value, seed 54 (lower-right is empty)
c54x, c54y = ax_(S54["d_traj"]), ay_(S54["d_sr"])
t, t54_end = rich_text(ax_(0.06), ay_(-0.56), [
    ("Duel invasion rails the value (seed 54):", BLUE, True),
    (f'behavior {S54["traj"][0]:.2f}→{S54["traj"][-1]:.2f} while stated '
     f'{S54["sr"][0]:.2f}→{S54["sr"][-1]:.2f}', INK, False)], 17, 34)
b.append(t)
b.append(f'<line x1="{ax_(0.28):.1f}" y1="{ay_(-0.56) - 22:.1f}" x2="{c54x:.1f}" y2="{c54y + 14:.1f}" '
         f'stroke="{BLUE}" stroke-width="2"/>')

# ================= Panel B: tracking ratio by group =================
BX = 880
BTY = 310
b.append(f'<text x="{BX}" y="220" font-size="22" font-weight="bold" fill="{INK}" '
         f'font-family="{FONT}">B. Stated movement per unit of behavior movement,</text>')
b.append(f'<text x="{BX}" y="248" font-size="22" font-weight="bold" fill="{INK}" '
         f'font-family="{FONT}">by condition group</text>')

BAR_X0 = BX + 320          # bars start here; labels sit to the left
BAR_SCALE = 240            # pixels for ratio 0..1.0
BAR_H, ROW_H = 26, 46
ratios = sorted(((g, AGG[g]["mean_tracking_ratio"]) for g, _, _, _ in GROUPS),
                key=lambda kv: -kv[1])
for i, (g, v) in enumerate(ratios):
    color, shape, label = STYLE[g]
    yy = BTY + i * ROW_H
    # group name (words, right-aligned) with its marker key
    b.append(marker(BAR_X0 - 14, yy + BAR_H / 2, shape, color, 6.5))
    for j, ln in enumerate(wrap(label, 34)):
        b.append(f'<text x="{BAR_X0 - 28}" y="{yy + BAR_H / 2 + 6 - (len(wrap(label, 34)) - 1) * 9 + j * 18:.1f}" '
                 f'text-anchor="end" font-size="16" fill="{INK}" font-family="{FONT}">{esc(ln)}</text>')
    b.append(f'<rect x="{BAR_X0}" y="{yy}" width="{max(v * BAR_SCALE, 2):.1f}" height="{BAR_H}" '
             f'rx="4" fill="{color}" fill-opacity="0.8"/>')
    b.append(f'<text x="{BAR_X0 + max(v * BAR_SCALE, 2) + 8:.1f}" y="{yy + BAR_H / 2 + 6:.1f}" '
             f'font-size="18" font-weight="bold" fill="{INK}" font-family="{FONT}">{v:+.2f}</text>')
BBOT = BTY + len(ratios) * ROW_H
# baseline and the slope-1 reference
b.append(f'<line x1="{BAR_X0}" y1="{BTY - 8}" x2="{BAR_X0}" y2="{BBOT + 4}" stroke="{INK}" stroke-width="2"/>')
refx = BAR_X0 + 1.0 * BAR_SCALE
b.append(f'<line x1="{refx:.1f}" y1="{BTY - 8}" x2="{refx:.1f}" y2="{BBOT + 4}" '
         f'stroke="{GRAY}" stroke-width="2.5" stroke-dasharray="8 7"/>')
b.append(f'<text x="{refx - 10:.1f}" y="{BTY - 20}" text-anchor="end" font-size="17" fill="{GRAY}" '
         f'font-family="{FONT}">perfect tracking = +1.00</text>')
for v in (0.0, 0.5):
    b.append(f'<text x="{BAR_X0 + v * BAR_SCALE:.1f}" y="{BBOT + 26:.1f}" text-anchor="middle" '
             f'font-size="16" fill="{GRAY}" font-family="{FONT}">{v:+.1f}</text>')
b.append(f'<text x="{refx:.1f}" y="{BBOT + 26:.1f}" text-anchor="middle" font-size="16" '
         f'fill="{GRAY}" font-family="{FONT}">+1.0</text>')

t, bcap_end = text_block(BX, BBOT + 62,
    "Tracking ratio = (change in stated tolerance) divided by (change in behavior) for each "
    "rollout whose behavior moved by at least 0.15, averaged within the condition group. "
    "The best-tracking group recovers a seventh of perfect tracking; most sit near +0.03.",
    17, 62, GRAY)
b.append(t)

# panel A footnote (direction does follow, magnitude does not)
t, acap_end = text_block(AX - 40, AY + AH + 96,
    "The direction of the tiny stated shifts does follow the behavior, but at "
    f"roughly one-twentieth the size (correlation r = {R:.2f}). Press-depth runs hold a "
    "cautious frozen judge for one to four rounds, then release to the frozen base judge.",
    17, 72, GRAY)
b.append(t)

# ================= takeaway =================
ky = max(acap_end, t54_end, bcap_end) + 26
b.append(box(60, ky, W - 120, 146, KEY_FILL, INK, 2.5))
t, _ = rich_text(84, ky + 38, [
    ("The gap widens; it never closes. ", INK, True),
    (f"Across all 46 rollouts, the mean absolute difference between the behavior probe and the "
     f"stated-tolerance probe grows from {GAP0:.3f} at round 0 to {GAPF:.3f} at the final round. "
     f"Final behavior spans the full {min(TRAJ_FINAL):.2f}-to-{max(TRAJ_FINAL):.2f} range; final stated tolerance stays "
     f"between {min(SR_FINAL):.2f} and {max(SR_FINAL):.2f}. Asking this model whether it is risk-tolerant does not "
     f"reveal what selection did to it.", INK, False),
], BODY, 128)
b.append(t)

H = ky + 146 + 36
svg = svg_doc(W, H, "\n".join(b))
out = os.path.join(HERE, "selfreport-decoupling.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out}  (n_moved={n}, slope={SLOPE:.3f}, r={R:.3f}, "
      f"gap {GAP0:.3f} -> {GAPF:.3f})")

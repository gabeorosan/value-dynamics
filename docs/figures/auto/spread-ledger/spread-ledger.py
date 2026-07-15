#!/usr/bin/env python3
"""Draft figure: candidate value-spread under three pool compositions.

Spread is the consumable material selection needs. Self-only pools carry it
as a slow persistent state; a frozen base-model supplier resets it every
round; a railed peer invader consumes it. Includes the matched twin-pair
call-out (zero-spread twin flat, injected run moving).

Data: experiments/spread_util_unified.json (records + spread_ledger).
House style: docs/figures/src/make_figures.py (Evans-lab look).
Regenerate:  python3 spread-ledger.py   (from this directory, stdlib only)
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "spread_util_unified.json")

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


def centered_lines(cx, y, lines, size, color, weight="normal", lh=1.45):
    s = []
    for i, ln in enumerate(lines):
        s.append(f'<text x="{cx}" y="{y + i * size * lh}" text-anchor="middle" '
                 f'font-size="{size}" fill="{color}" font-weight="{weight}" '
                 f'font-family="{FONT}">{esc(ln)}</text>')
    return "\n".join(s)


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ----------------------------------------------------------------- data
with open(DATA) as f:
    D = json.load(f)
RECS = D["records"]
LEDGER = D["spread_ledger"]


def runs_of(organism, composition):
    """Individual run trajectories: group by (cond, seed, source)."""
    g = defaultdict(list)
    for r in RECS:
        if r["organism"] == organism and r["composition"] == composition:
            g[(r["cond"], r["seed"], r["source"])].append((r["round"], r["spread"]))
    return [sorted(v) for v in g.values()]


def mean_by_round(organism, composition):
    g = defaultdict(list)
    for r in RECS:
        if r["organism"] == organism and r["composition"] == composition:
            g[r["round"]].append(r["spread"])
    return sorted((rd, sum(v) / len(v)) for rd, v in g.items())


olmo_self = mean_by_round("OLMo", "self-only")
qwen_self = mean_by_round("Qwen", "self-only")
olmo_base = mean_by_round("OLMo", "base-mixed")
qwen_base = mean_by_round("Qwen", "base-mixed")
olmo_peer = mean_by_round("OLMo", "peer-mixed")

runs_olmo_self = runs_of("OLMo", "self-only")
runs_qwen_self = runs_of("Qwen", "self-only")
runs_olmo_base = runs_of("OLMo", "base-mixed")
runs_qwen_base = runs_of("Qwen", "base-mixed")
runs_olmo_peer = runs_of("OLMo", "peer-mixed")

slope_olmo_self = LEDGER["OLMo/self-only"]["persistence"]
slope_qwen_self = LEDGER["Qwen/self-only"]["persistence"]
slope_olmo_base = LEDGER["OLMo/base-mixed"]["persistence"]
sep_fit = LEDGER["mixed_spread_vs_source_separation"]

pair = LEDGER["matched_pair_qwen_reopen_vs_twin"]
reopen_runs = [sorted((r["round"], r["spread"]) for r in RECS
                      if r["cond"] == "mixed_reopen_qwen" and r["seed"] == s)
               for s in ("921", "922")]
twin_runs = [sorted((r["round"], r["spread"]) for r in RECS
                    if r["cond"] == "mixed_reopen_twin_selfonly" and r["seed"] == s)
             for s in ("921", "922")]
reopen_drift = pair["reopen(base-mixed)"]["mean_abs_drift"]
twin_drift = pair["twin(self-only)"]["mean_abs_drift"]
# the injected run's actual round-1 value movement, from the records
reopen_move_r1 = max(abs(r["drift"]) for r in RECS
                     if r["cond"] == "mixed_reopen_qwen" and r["round"] == 1)

# ----------------------------------------------------------------- layout
W, H = 1460, 1160
b = []

b.append(f'<text x="{W // 2}" y="52" text-anchor="middle" font-size="26" '
         f'font-weight="bold" fill="{INK}" font-family="{FONT}">'
         f'{esc("Who fills the candidate pool decides whether value-spread persists, is refilled, or collapses")}</text>')
b.append(centered_lines(W // 2, 84, [
    "spread = standard deviation of the judge's value reading across the candidate "
    "answers competing on one item, averaged over the round's items",
    f"{D['n_records']} loop rounds from {D['n_runs']} runs — every score-logged "
    "selection loop in the project"], 16, GRAY))

# panel geometry
PX = [100, 560, 1020]          # plot-area left edges
PW, PH = 380, 300              # plot-area size
Y0 = 210                       # plot-area top
YMAX = 0.5                     # spread axis 0 .. 0.5
RMAX = 8                       # round axis 1 .. 8 (shared so slopes compare)


def xr(px0, rd):
    return px0 + (rd - 1) / (RMAX - 1) * PW


def ys(v):
    return Y0 + PH - v / YMAX * PH


def polyline(px0, pts, color, sw, dash=None, opacity=1.0, markers=False):
    s = " ".join(f"{xr(px0, rd):.1f},{ys(v):.1f}" for rd, v in pts)
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    out = [f'<polyline points="{s}" fill="none" stroke="{color}" '
           f'stroke-width="{sw}" stroke-opacity="{opacity}" '
           f'stroke-linejoin="round" stroke-linecap="round"{dd}/>']
    if markers:
        for rd, v in pts:
            out.append(f'<circle cx="{xr(px0, rd):.1f}" cy="{ys(v):.1f}" r="5" '
                       f'fill="{color}"/>')
    return "\n".join(out)


def panel_frame(px0, title_lines, color):
    s = []
    for i, ln in enumerate(title_lines):
        s.append(f'<text x="{px0 + PW / 2}" y="{152 + i * 26}" text-anchor="middle" '
                 f'font-size="20" font-weight="bold" fill="{color}" '
                 f'font-family="{FONT}">{esc(ln)}</text>')
    for i in range(6):
        v = i * 0.1
        yy = ys(v)
        s.append(f'<line x1="{px0}" y1="{yy:.1f}" x2="{px0 + PW}" y2="{yy:.1f}" '
                 f'stroke="#dddddd" stroke-width="1"/>')
        if px0 == PX[0]:
            s.append(f'<text x="{px0 - 12}" y="{yy + 5:.1f}" text-anchor="end" '
                     f'font-size="15" fill="{GRAY}" font-family="{FONT}">{v:.1f}</text>')
    s.append(f'<line x1="{px0}" y1="{Y0}" x2="{px0}" y2="{Y0 + PH}" '
             f'stroke="{GRAY}" stroke-width="1.5"/>')
    s.append(f'<line x1="{px0}" y1="{Y0 + PH}" x2="{px0 + PW}" y2="{Y0 + PH}" '
             f'stroke="{GRAY}" stroke-width="1.5"/>')
    for rd in range(1, RMAX + 1):
        xx = xr(px0, rd)
        s.append(f'<line x1="{xx:.1f}" y1="{Y0 + PH}" x2="{xx:.1f}" y2="{Y0 + PH + 6}" '
                 f'stroke="{GRAY}" stroke-width="1.5"/>')
        s.append(f'<text x="{xx:.1f}" y="{Y0 + PH + 24}" text-anchor="middle" '
                 f'font-size="15" fill="{GRAY}" font-family="{FONT}">{rd}</text>')
    s.append(f'<text x="{px0 + PW / 2}" y="{Y0 + PH + 48}" text-anchor="middle" '
             f'font-size="18" fill="{INK}" font-family="{FONT}">round</text>')
    return "\n".join(s)


def value_label(px0, rd, v, color, dx, dy, anchor):
    return (f'<text x="{xr(px0, rd) + dx:.1f}" y="{ys(v) + dy:.1f}" '
            f'text-anchor="{anchor}" font-size="15" font-weight="bold" '
            f'fill="{color}" font-family="{FONT}">{v:.2f}</text>')


def key_entry(x, y, color, dash, sw, opacity, label):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    s = [f'<line x1="{x}" y1="{y - 5}" x2="{x + 34}" y2="{y - 5}" stroke="{color}" '
         f'stroke-width="{sw}" stroke-opacity="{opacity}"{dd}/>']
    t, ny = text_block(x + 44, y, label, 15, 52, INK)
    s.append(t)
    return "\n".join(s), ny


# y-axis title (left panel only)
b.append(f'<text x="38" y="{Y0 + PH / 2}" font-size="18" fill="{INK}" '
         f'font-family="{FONT}" text-anchor="middle" '
         f'transform="rotate(-90 38 {Y0 + PH / 2})">candidate value spread '
         f'(within-item SD)</text>')

KEY_Y = Y0 + PH + 78           # key strip below each panel
ann_bottoms = []
key_bottoms = []

# --- panel A: self-only ---------------------------------------------
pA = PX[0]
b.append(panel_frame(pA, ["Self-only pool:", "spread is a slow, persistent state"], BLUE))
for run in runs_olmo_self + runs_qwen_self:
    b.append(polyline(pA, run, BLUE, 1.3, opacity=0.18))
b.append(polyline(pA, olmo_self, BLUE, 4.5, markers=True))
b.append(polyline(pA, qwen_self, BLUE, 4.5, dash="10 7", markers=True))
b.append(value_label(pA, *qwen_self[0], BLUE, 6, -13, "start"))    # 0.36 above r1
b.append(value_label(pA, *olmo_self[0], BLUE, 6, 27, "start"))     # 0.30 below r1
b.append(value_label(pA, *olmo_self[-1], BLUE, 12, 5, "start"))    # 0.23 right of r8
b.append(value_label(pA, *qwen_self[-1], BLUE, -2, -16, "middle"))  # 0.28 above r4
ky = KEY_Y
t, ky = key_entry(pA - 30, ky, BLUE, None, 4, 1.0,
                  f"OLMo risk organism, mean of {len(runs_olmo_self)} runs")
b.append(t)
t, ky = key_entry(pA - 30, ky + 8, BLUE, "10 7", 4, 1.0,
                  f"Qwen organisms (risk-preference and insecure-code, pooled), "
                  f"mean of {len(runs_qwen_self)} runs")
b.append(t)
t, ky = key_entry(pA - 30, ky + 8, BLUE, None, 1.3, 0.4,
                  "thin lines: the individual runs behind each mean")
b.append(t)
key_bottoms.append(ky)

# --- panel B: base-mixed --------------------------------------------
pB = PX[1]
b.append(panel_frame(pB, ["Base-mixed pool:", "an outside supplier refills spread"], GREEN))
for run in runs_olmo_base + runs_qwen_base:
    b.append(polyline(pB, run, GREEN, 1.3, opacity=0.18))
b.append(polyline(pB, olmo_base, GREEN, 4.5, markers=True))
b.append(polyline(pB, qwen_base, GREEN, 4.5, dash="10 7", markers=True))
b.append(value_label(pB, *olmo_base[0], GREEN, -10, 1, "end"))
b.append(value_label(pB, *qwen_base[0], GREEN, -10, 20, "end"))
b.append(value_label(pB, *olmo_base[-1], GREEN, 12, 5, "start"))
b.append(value_label(pB, *qwen_base[-1], GREEN, 12, 5, "start"))
ky = KEY_Y
t, ky = key_entry(pB - 30, ky, GREEN, None, 4, 1.0,
                  f"OLMo risk organism + its frozen base model in the pool, "
                  f"mean of {len(runs_olmo_base)} runs")
b.append(t)
t, ky = key_entry(pB - 30, ky + 8, GREEN, "10 7", 4, 1.0,
                  f"Qwen insecure-code organism + frozen base model, mean of "
                  f"{len(runs_qwen_base)} runs (runs end at round 4)")
b.append(t)
key_bottoms.append(ky)

# --- panel C: peer-mixed --------------------------------------------
pC = PX[2]
b.append(panel_frame(pC, ["Peer-mixed pool:", "a railed invader consumes spread"], RED))
for run in runs_olmo_peer:
    b.append(polyline(pC, run, RED, 1.3, opacity=0.18))
b.append(polyline(pC, olmo_peer, RED, 4.5, markers=True))
b.append(value_label(pC, *olmo_peer[0], RED, -10, 1, "end"))
b.append(value_label(pC, *olmo_peer[-1], RED, 12, -9, "start"))
ky = KEY_Y
t, ky = key_entry(pC - 30, ky, RED, None, 4, 1.0,
                  f"OLMo risk organism + a railed peer organism trained to the "
                  f"opposite value, mean of {len(runs_olmo_peer)} runs (runs end "
                  f"at round 4)")
b.append(t)
key_bottoms.append(ky)

# --- annotations under panels ---------------------------------------
ANN_Y = int(max(key_bottoms)) + 26
t, e = rich_text(pA - 30, ANN_Y, [
    ("The pool is refilled only by the organism's own samples. Spread carries "
     "over: next round's spread is about ", INK, False),
    (f"{slope_olmo_self['slope']:.2f} x this round's", BLUE, True),
    (f" (r {slope_olmo_self['r']:.2f}, n {slope_olmo_self['n']} round pairs) for "
     f"OLMo, {slope_qwen_self['slope']:.2f} (r {slope_qwen_self['r']:.2f}) for "
     "Qwen — a slow state that sags from about 0.30 toward 0.23 over 8 rounds.",
     INK, False)], 15.5, 55)
b.append(t)
ann_bottoms.append(e)
t, e = rich_text(pB - 30, ANN_Y, [
    ("Fresh base-model candidates ", INK, False),
    ("reset OLMo's spread to 0.35-0.40 every round", GREEN, True),
    (f" regardless of the last round (round-to-round slope "
     f"{slope_olmo_base['slope']:.2f}): a supply floor, not an inherited state. "
     "Qwen's falls to about 0.10 because the host reached the supplier's level "
     f"in one round — across all {sep_fit['n']} mixed-pool rounds, spread tracks "
     f"the gap between the two sources (spread = {sep_fit['slope']:.2f} x source "
     f"separation + {sep_fit['intercept']:.2f}, r {sep_fit['r']:.2f}).",
     INK, False)], 15.5, 55)
b.append(t)
ann_bottoms.append(e)
t, e = rich_text(pC - 30, ANN_Y, [
    ("A railed peer's candidates flood the pool: the host converges on the "
     "supplier, the gap between the sources closes, and ", INK, False),
    ("spread collapses from 0.43 to 0.03 in four rounds.", RED, True),
    (" The invader consumes the material selection needs, and the loop stalls "
     "at the supplier's position.", INK, False)], 15.5, 55)
b.append(t)
ann_bottoms.append(e)

# --- matched-pair call-out ------------------------------------------
CY = int(max(ann_bottoms)) + 24
b.append(box(70, CY, W - 140, 250, KEY_FILL))
t, _ = text_block(100, CY + 38, "The controlled version: a matched pair — same "
                  "seeds, same oracle judge, differing only in who fills the pool",
                  19, 200, INK, "bold")
b.append(t)

# inset chart
IX, IY, IW, IH = 120, CY + 66, 290, 128
IYMAX = 0.4


def ixr(rd):
    return IX + (rd - 1) / 3 * IW


def iys(v):
    return IY + IH - v / IYMAX * IH


for v in (0.0, 0.2, 0.4):
    b.append(f'<line x1="{IX}" y1="{iys(v):.1f}" x2="{IX + IW}" y2="{iys(v):.1f}" '
             f'stroke="#d5ddd5" stroke-width="1"/>')
    b.append(f'<text x="{IX - 10}" y="{iys(v) + 5:.1f}" text-anchor="end" '
             f'font-size="14" fill="{GRAY}" font-family="{FONT}">{v:.1f}</text>')
b.append(f'<line x1="{IX}" y1="{IY}" x2="{IX}" y2="{IY + IH}" stroke="{GRAY}" '
         f'stroke-width="1.5"/>')
for rd in range(1, 5):
    b.append(f'<text x="{ixr(rd):.1f}" y="{IY + IH + 20}" text-anchor="middle" '
             f'font-size="14" fill="{GRAY}" font-family="{FONT}">{rd}</text>')
b.append(f'<text x="{IX + IW / 2}" y="{IY + IH + 42}" text-anchor="middle" '
         f'font-size="15" fill="{INK}" font-family="{FONT}">round (both seeds '
         f'shown per arm)</text>')
for run in reopen_runs:
    b.append(f'<polyline points="{" ".join(f"{ixr(rd):.1f},{iys(v):.1f}" for rd, v in run)}" '
             f'fill="none" stroke="{GREEN}" stroke-width="3.5" stroke-linejoin="round"/>')
    for rd, v in run:
        b.append(f'<circle cx="{ixr(rd):.1f}" cy="{iys(v):.1f}" r="4" fill="{GREEN}"/>')
for run in twin_runs:
    b.append(f'<polyline points="{" ".join(f"{ixr(rd):.1f},{iys(v):.1f}" for rd, v in run)}" '
             f'fill="none" stroke="{BLUE}" stroke-width="3.5" stroke-linejoin="round"/>')
    for rd, v in run:
        b.append(f'<circle cx="{ixr(rd):.1f}" cy="{iys(v):.1f}" r="4" fill="{BLUE}"/>')
b.append(f'<text x="{ixr(1) + 14:.1f}" y="{iys(reopen_runs[1][0][1]) - 12:.1f}" '
         f'font-size="15" font-weight="bold" fill="{GREEN}" font-family="{FONT}">'
         f'base-model candidates injected</text>')
b.append(f'<text x="{ixr(1) + 46:.1f}" y="{iys(0.0) - 9:.1f}" font-size="15" '
         f'font-weight="bold" fill="{BLUE}" font-family="{FONT}">self-only twin: '
         f'spread 0.000 every round</text>')

# call-out text
tw0 = pair["twin(self-only)"]["spread_by_round"]["1"]
t, _ = rich_text(470, CY + 80, [
    ("A Qwen insecure-code run whose self-only pool had fully collapsed "
     f"(spread {tw0:.3f}) ", INK, False),
    (f"sat still for four rounds: mean absolute per-round value movement "
     f"{twin_drift:.4f}.", BLUE, True),
    (" Its twin — same seeds, same oracle judge, random streams diverging only "
     "at candidate injection — received frozen base-model candidates: ", INK, False),
    (f"spread came back (0.31 in round 1) and the value moved by "
     f"{reopen_move_r1:.2f} that round", GREEN, True),
    (f" (mean absolute per-round movement {reopen_drift:.3f}), after which the "
     "host sat at the supplier's level with residual spread near 0.07. "
     "Selection without spread has nothing to choose between; refilling the "
     "pool is what lets the value move. n = 2 seed pairs.", INK, False)],
    16, 92)
b.append(t)

H = CY + 250 + 30
svg = svg_doc(W, H, "\n".join(b))
out = os.path.join(HERE, "spread-ledger.svg")
with open(out, "w") as f:
    f.write(svg)
print(f"wrote {out} ({len(svg)} bytes, H={H})")

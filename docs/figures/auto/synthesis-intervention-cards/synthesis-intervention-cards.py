#!/usr/bin/env python3
"""Synthesis candidate B: four experiment cards in one lens.

Each card shows (1) which dial an intervention moved, (2) the measured value
trajectory that followed, and (3) the experiment's identity in plain words.
All numbers are read live from experiments/spread_util_unified.json (records
carry per-round value, spread, and rho for every run). Run from this directory:

    python3 synthesis-intervention-cards.py

Style: reuses the make_figures.py Owain Evans-lab house style (palette,
esc/wrap helpers copied verbatim, white background, headline sentence, fat
labels, direct series labels). Stdlib only.
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..",
                    "experiments", "spread_util_unified.json")

# ---- palette copied verbatim from make_figures.py ----
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series
GREEN = "#3a7d44"      # frozen / holding series
RED = "#b5342c"        # reversal / erosion emphasis
GRAY = "#6b7684"       # recessive only (axes, muted text)
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"
DOC_FILL = "#fdf6e8"
KEY_FILL = "#eef5ee"
CARD_FILL = "#f7f9fb"

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


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


DEFS = f'''<defs>
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker>
<marker id="arrK" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
</defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


def txt(x, y, s, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}" text-anchor="{anchor}">'
            f'{esc(s)}</text>')


# ====================================================================
# Load run trajectories from the committed data file
# ====================================================================
def load_runs():
    d = json.load(open(DATA))
    runs = defaultdict(list)
    for r in d["records"]:
        runs[(r["cond"], str(r["seed"]))].append(r)
    for k in runs:
        runs[k].sort(key=lambda r: r["round"])
    return runs


RUNS = load_runs()


def vals(cond, seed):
    return [round(r["value"], 3) for r in RUNS[(cond, str(seed))]]


def pool_spread(cond, seed):
    return [round(r["spread"], 3) for r in RUNS[(cond, str(seed))]]


def mean_rho(cond, seed):
    rs = [r["rho"] for r in RUNS[(cond, str(seed))] if r.get("rho") is not None]
    return round(sum(rs) / len(rs), 2) if rs else None


# ---- pull the exact series each card plots ----
C1_SELF = vals("mixed_reopen_twin_selfonly", 921)   # holds
C1_INJ = vals("mixed_reopen_qwen", 921)             # collapses
C1_SIGMA_TO = pool_spread("mixed_reopen_qwen", 921)[0]  # 0.31

C2_REF = vals("cons_mix", 34)                       # holds its rail
C2_DUEL = vals("h2h_cons_rescue", 55)               # comes down
C2_RHO_REF = mean_rho("cons_mix", 34)               # +0.38 (run-mean over cond below)
C2_RHO_DUEL = mean_rho("h2h_cons_rescue", 55)

C3 = vals("head2head_selfjudge", 41)                # 0.445 -> 0.0
C3_RHO = mean_rho("head2head_selfjudge", 41)        # -0.24

C4 = vals("oracle_hold", 21)                        # 0.917 -> 0.292
C4_RHO = mean_rho("oracle_hold", 21)                # -1.0


# cond-level mean rho (matches the +0.38 / +0.10 the prompt names)
def cond_mean_rho(cond):
    rs = []
    for (c, s), recs in RUNS.items():
        if c != cond:
            continue
        rs += [r["rho"] for r in recs if r.get("rho") is not None]
    return round(sum(rs) / len(rs), 2) if rs else None


C2_RHO_REF = cond_mean_rho("cons_mix")      # +0.38
C2_RHO_DUEL = cond_mean_rho("h2h_cons_rescue")   # +0.10
C3_RHO = cond_mean_rho("head2head_selfjudge")    # -0.24
C4_RHO = cond_mean_rho("oracle_hold")            # -1.0


# ====================================================================
# Drawing helpers
# ====================================================================
def sparkline(x, y, w, h, series, legend_x, legend_y):
    """Plot value trajectories; series word-labels go in a legend below.

    series: list of (values, color, word_label). Value axis 1.0 top, 0.0 bottom.
    """
    smax = 1.0
    s = []
    # frame: baseline + left axis, recessive
    s.append(f'<line x1="{x}" y1="{y+h}" x2="{x+w}" y2="{y+h}" stroke="{GRAY}" '
             f'stroke-width="1.5"/>')
    s.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+h}" stroke="{GRAY}" '
             f'stroke-width="1.5"/>')
    s.append(txt(x - 8, y + 6, "1.0", 13, GRAY, anchor="end"))
    s.append(txt(x - 8, y + h + 4, "0", 13, GRAY, anchor="end"))
    for (v, color, _label) in series:
        n = len(v)
        pts = []
        for j, val in enumerate(v):
            px = x + (w * j / (n - 1) if n > 1 else 0)
            py = y + h - (val / smax) * h
            pts.append((px, py))
        path = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
        s.append(f'<polyline points="{path}" fill="none" stroke="{color}" '
                 f'stroke-width="3.4" stroke-linejoin="round" stroke-linecap="round"/>')
        for (px, py) in (pts[0], pts[-1]):
            s.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.6" fill="{color}" '
                     f'stroke="white" stroke-width="1.6"/>')
        # start value (above first point)
        sx, sy = pts[0]
        startlbl = "0" if v[0] == 0 else f"{v[0]:.3f}".rstrip("0").rstrip(".")
        s.append(txt(sx + 2, sy - 11, startlbl, 15, color, weight="bold"))
        # end value (compact, right of last point — fits inside card)
        ex, ey = pts[-1]
        endval = "0.000" if v[-1] == 0 else f"{v[-1]:.3f}".rstrip("0").rstrip(".")
        s.append(txt(ex + 8, ey + 5, endval, 16, color, weight="bold"))
    s.append(txt(x + w / 2, y + h + 26, "rounds →", 14, GRAY, anchor="middle"))
    # legend (color swatch + word) below, left-aligned to card
    ly = legend_y
    for (v, color, label) in series:
        s.append(f'<line x1="{legend_x}" y1="{ly-5}" x2="{legend_x+22}" '
                 f'y2="{ly-5}" stroke="{color}" stroke-width="3.6" '
                 f'stroke-linecap="round"/>')
        s.append(f'<circle cx="{legend_x+11}" cy="{ly-5}" r="4.2" fill="{color}" '
                 f'stroke="white" stroke-width="1.4"/>')
        s.append(txt(legend_x + 30, ly, label, 14.5, INK))
        ly += 21
    return "\n".join(s)


def _edge(xp, left, right, pad=4):
    """Pick a text anchor + x so a label never spills past the track ends."""
    if xp - left < 40:
        return "start", left - pad
    if right - xp < 40:
        return "end", right + pad
    return "middle", xp


def rho_track(cx, cy, w, frm, to, moved_color=RED, label_to="", note=""):
    """Horizontal correlation dial from -1..+1 with a moving marker.

    frm/to in [-1, 1]. Draws neutral tick at 0 and an arrow frm -> to.
    """
    s = []
    x0, x1 = cx, cx + w
    def px(v):
        return x0 + (v + 1) / 2 * w
    s.append(f'<line x1="{x0}" y1="{cy}" x2="{x1}" y2="{cy}" stroke="{GRAY}" '
             f'stroke-width="3" stroke-linecap="round"/>')
    # end labels
    s.append(txt(x0, cy + 24, "−1", 13, GRAY, anchor="middle"))
    s.append(txt(px(0), cy + 24, "0", 13, GRAY, anchor="middle"))
    s.append(txt(x1, cy + 24, "+1", 13, GRAY, anchor="middle"))
    # zero tick
    s.append(f'<line x1="{px(0):.1f}" y1="{cy-7}" x2="{px(0):.1f}" y2="{cy+7}" '
             f'stroke="{GRAY}" stroke-width="2"/>')
    if frm is not None:
        # hollow marker at 'from' + its label (kept lower so it can't collide)
        s.append(f'<circle cx="{px(frm):.1f}" cy="{cy}" r="6" fill="white" '
                 f'stroke="{INK}" stroke-width="2.4"/>')
        a, lx = _edge(px(frm), x0, x1)
        s.append(txt(lx, cy - 21, f"from {frm:+.2f}", 14, INK,
                     weight="bold", anchor=a))
        # arrow from -> to
        s.append(f'<line x1="{px(frm):.1f}" y1="{cy-14}" x2="{px(to):.1f}" '
                 f'y2="{cy-14}" stroke="{moved_color}" stroke-width="3.2" '
                 f'marker-end="url(#arrR)"/>')
    # filled marker at 'to' (label raised so from/to never overlap)
    s.append(f'<circle cx="{px(to):.1f}" cy="{cy}" r="7" fill="{moved_color}" '
             f'stroke="white" stroke-width="1.8"/>')
    lift = -40 if frm is not None else -22
    a, lx = _edge(px(to), x0, x1)
    s.append(txt(lx, cy + lift, label_to, 16, moved_color, weight="bold",
                 anchor=a))
    if note:
        s.append(txt(cx, cy + 44, note, 14, GRAY))
    return "\n".join(s)


def sigma_track(cx, cy, w, frm, to, smax=0.5, note=""):
    """Horizontal spread dial 0..smax with an arrow frm -> to."""
    s = []
    x0, x1 = cx, cx + w
    def px(v):
        return x0 + v / smax * w
    s.append(f'<line x1="{x0}" y1="{cy}" x2="{x1}" y2="{cy}" stroke="{GRAY}" '
             f'stroke-width="3" stroke-linecap="round"/>')
    s.append(txt(x0, cy + 24, "0", 13, GRAY, anchor="middle"))
    s.append(txt(x1, cy + 24, f"{smax}", 13, GRAY, anchor="middle"))
    s.append(f'<circle cx="{px(frm):.1f}" cy="{cy}" r="6" fill="white" '
             f'stroke="{INK}" stroke-width="2.4"/>')
    s.append(f'<line x1="{px(frm):.1f}" y1="{cy-16}" x2="{px(to):.1f}" '
             f'y2="{cy-16}" stroke="{RED}" stroke-width="3.2" '
             f'marker-end="url(#arrR)"/>')
    s.append(f'<circle cx="{px(to):.1f}" cy="{cy}" r="7" fill="{RED}" '
             f'stroke="white" stroke-width="1.8"/>')
    a, lx = _edge(px(to), x0, x1)
    s.append(txt(lx, cy - 24, f"to {to:.2f}", 16, RED, weight="bold", anchor=a))
    a, lx = _edge(px(frm), x0, x1)
    s.append(txt(lx, cy - 24, f"from {frm:.2f}", 15, INK, weight="bold",
                 anchor=a))
    if note:
        s.append(txt(cx, cy + 44, note, 14, GRAY))
    return "\n".join(s)


# ====================================================================
# Card
# ====================================================================
CARD_W = 372
CARD_H = 486
PAD = 22
# fixed vertical bands inside a card (offsets from card top y)
Y_ID = 66          # first identity line
Y_DIVIDER = 128
Y_DIAL_HEAD = 154
Y_DIAL_NAME = 174
Y_DIAL_CTR = 236   # dial track center
Y_TRAJ_HEAD = 300
Y_SPARK = 322      # sparkline box top
SPARK_H = 84
Y_LEGEND = 452     # first legend row baseline


def card(x, y, num, title, identity_lines, dial_svg, dial_name, spark_svg):
    s = [box(x, y, CARD_W, CARD_H, CARD_FILL, INK, 2.5, rx=14)]
    s.append(f'<circle cx="{x+PAD+13}" cy="{y+30}" r="17" fill="{INK}"/>')
    s.append(txt(x + PAD + 13, y + 36, str(num), 20, "white", weight="bold",
                 anchor="middle"))
    s.append(txt(x + PAD + 40, y + 37, title, 18.5, INK, weight="bold"))
    iy = y + Y_ID
    for ln in identity_lines:
        s.append(txt(x + PAD, iy, ln, 14.5, GRAY))
        iy += 20
    s.append(f'<line x1="{x+PAD}" y1="{y+Y_DIVIDER}" x2="{x+CARD_W-PAD}" '
             f'y2="{y+Y_DIVIDER}" stroke="#d8dee6" stroke-width="1.5"/>')
    s.append(txt(x + PAD, y + Y_DIAL_HEAD, "The dial this intervention moved",
                 15, INK, weight="bold"))
    s.append(txt(x + PAD, y + Y_DIAL_NAME, dial_name, 14.5, GRAY))
    s.append(dial_svg)
    s.append(txt(x + PAD, y + Y_TRAJ_HEAD, "The measured value that followed",
                 15, INK, weight="bold"))
    s.append(spark_svg)
    return "\n".join(s)


def build():
    W, H = 1620, 648
    b = []
    # headline (orientation only — interpretation lives in caption.md)
    b.append(txt(60, 62,
                 "Four interventions: the dial each moved, and the value "
                 "trajectory that followed",
                 34, INK, weight="bold"))
    b.append(txt(60, 96,
                 "Selection dial and behavioural value trajectory (share kept "
                 "insecure/risky, 0–1) per run — all from spread_util_unified.json.",
                 18, GRAY))

    x0, y0 = 44, 130
    gap = 24
    step = CARD_W + gap
    dial_w = CARD_W - 92
    spx = x0 + 60           # sparkline left (per card, add card x)
    spw = CARD_W - 150      # narrower so end value fits inside card
    legx = PAD              # legend x offset within card

    def spark_of(cardx, series):
        return sparkline(cardx + spx - x0, y0 + Y_SPARK, spw, SPARK_H, series,
                         cardx + legx, y0 + Y_LEGEND)

    # ---- Card 1: inject base answers (sigma dial) ----
    d1 = sigma_track(x0 + PAD, y0 + Y_DIAL_CTR, dial_w, 0.00, C1_SIGMA_TO,
                     smax=0.5, note="agreement pinned at −1.0 (oracle)")
    sp1 = spark_of(x0, [(C1_SELF, GREEN, "self-only twin holds"),
                        (C1_INJ, RED, "injected twin collapses")])
    b.append(card(x0, y0, 1, "Inject base answers",
                  ["Qwen self-report organism · score oracle judge",
                   "score format · base-mixed vs self-only twin",
                   "matched twins, seed 921"],
                  d1, "spread σ (disagreement in the kept pool)", sp1))

    # ---- Card 2: change how the judge is asked (rho dial) ----
    x1 = x0 + step
    d2 = rho_track(x1 + PAD, y0 + Y_DIAL_CTR, dial_w, C2_RHO_REF, C2_RHO_DUEL,
                   moved_color=RED, label_to=f"to {C2_RHO_DUEL:+.2f}", note="")
    sp2 = spark_of(x1, [(C2_REF, GREEN, "fixed-reference judge holds"),
                        (C2_DUEL, RED, "duel judge comes down")])
    b.append(card(x1, y0, 2, "Change how the judge is asked",
                  ["OLMo cautious-tuned copy · base-mixed pool",
                   "fixed reference score vs pick-a-duel-winner",
                   "reference seed 34, duel seed 55"],
                  d2, "agreement ρ (does selection track the value?)", sp2))

    # ---- Card 3: organism judges its own duels (rho dial) ----
    x2 = x0 + 2 * step
    # no measured before-state for this dial: show the single measured ρ only
    d3 = rho_track(x2 + PAD, y0 + Y_DIAL_CTR, dial_w, None, C3_RHO,
                   moved_color=RED,
                   label_to=f"ρ = {C3_RHO:.2f}".replace("-", "−"), note="")
    sp3 = spark_of(x2, [(C3, BLUE, "self-judged: erodes to 0")])
    b.append(card(x2, y0, 3, "Let it judge its own duels",
                  ["Qwen self-report organism · judges own duels",
                   "duel format · base-mixed pool",
                   "seed 41"],
                  d3, "agreement ρ (self-judgment vs its value)", sp3))

    # ---- Card 4: pin agreement at -1 with the oracle (rho dial) ----
    x3 = x0 + 3 * step
    d4 = rho_track(x3 + PAD, y0 + Y_DIAL_CTR, dial_w, 0.0, C4_RHO,
                   moved_color=RED,
                   label_to=f"to {C4_RHO:+.2f}".replace("-", "−"), note="")
    sp4 = spark_of(x3, [(C4, RED, "oracle reversal")])
    b.append(card(x3, y0, 4, "Pin agreement at −1 (oracle)",
                  ["OLMo risk organism · score oracle judge",
                   "score format · self-only pool",
                   "seed 21"],
                  d4, "agreement ρ (oracle opposes the value)", sp4))

    return svg_doc(W, H, "\n".join(b))


if __name__ == "__main__":
    out = os.path.join(HERE, "synthesis-intervention-cards.svg")
    with open(out, "w") as f:
        f.write(build())
    print("wrote", out)
    # echo the numbers actually plotted, for the honesty check
    print("C1 self-only:", C1_SELF)
    print("C1 injected :", C1_INJ, " sigma0 ->", C1_SIGMA_TO)
    print("C2 ref rho:", C2_RHO_REF, "vals", C2_REF)
    print("C2 duel rho:", C2_RHO_DUEL, "vals", C2_DUEL)
    print("C3 rho:", C3_RHO, "vals", C3)
    print("C4 rho:", C4_RHO, "vals", C4)

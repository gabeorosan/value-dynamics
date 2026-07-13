#!/usr/bin/env python3
"""synthesis — a shared answer pool amplifies whichever source the judge prefers.

Three parallel lanes, each drawn as the same left-to-right flow:
  [starting model] -> [answer pool: half its own + half another source]
  -> [what the judge keeps] -> [where it ends up]

Lane 1 (slow rescue): a stuck-high model, safe answers from the base model mixed
in, a scoring judge that keeps the safer answers. It moves partway down, landing
at the base model's own level.
Lane 2 (failed rescue): same half-and-half pool, but a cautious-prompt judge that
rejects the safe answers, so the stuck model stays high.
Lane 3 (fast contamination): a fresh, mostly-safe model, half its pool swapped for
answers from a stuck copy, a weak self-judge that keeps the stuck copy's answers
almost every time. One round takes it over.

All numbers are recomputed from the raw result JSONs in
experiments/modal_k2_release/output/ (same source as fig10 / fig11). Helpers
(esc, wrap, ctext, box, svg_doc) match fig05_selection_gap_predicts_drift.py.

Regenerate with:  python3 synthesis_shared_pool_asymmetry.py   (stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE
OUT_DIR = os.path.join(ROOT, "experiments", "modal_k2_release", "output")

INK = "#1a1a1a"
BLUE = "#2867b5"       # the model's own answers
GREEN = "#3a7d44"      # answers from the base model (the safe supplier)
RED = "#b5342c"        # answers from a stuck copy (the harmful source)
GRAY = "#6b7684"
SLATE = "#3f4b5b"      # neutral fill for the risk meter
STRIP_FILL = "#eef2f6"
TRACK = "#e7ebef"
RED_BG = "#fdf4f3"     # faint tint behind the contamination lane only
GREEN_BAND = "#e6f0e8"

FONT = "Helvetica, Arial, sans-serif"
BODY = 19


# ---------------------------------------------------------------- helpers
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


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def cwrap(cx, y, text, size, width_chars, color=INK, weight="normal", lh=1.35):
    lines = wrap(text, width_chars)
    out = [ctext(cx, y + i * size * lh, ln, size, color, weight) for i, ln in enumerate(lines)]
    return "\n".join(out), y + len(lines) * size * lh


def lwrap(x, y, text, size, width_chars, color=INK, weight="normal", lh=1.35):
    lines = wrap(text, width_chars)
    out = [ltext(x, y + i * size * lh, ln, size, color, weight) for i, ln in enumerate(lines)]
    return "\n".join(out), y + len(lines) * size * lh


def rarrow(x0, x1, y, color=GRAY, sw=3.0):
    return (f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1 - 9:.1f}" y2="{y:.1f}" '
            f'stroke="{color}" stroke-width="{sw}"/>'
            f'<path d="M {x1 - 10:.1f} {y - 7:.1f} L {x1:.1f} {y:.1f} L {x1 - 10:.1f} {y + 7:.1f} z" fill="{color}"/>')


# ---------------------------------------------------------------- data
def load(fname, seed, cond):
    with open(os.path.join(OUT_DIR, fname)) as f:
        return json.load(f)[seed][cond]


CELLS = {
    "oracle_mix_31": load("k2rel_oracle_mix_s31.json", "31", "oracle_mix"),
    "oracle_mix_32": load("k2rel_oracle_mix_s32.json", "32", "oracle_mix"),
    "cons_mix_33": load("k2rel_cons_mix_s33.json", "33", "cons_mix"),
    "cons_mix_34": load("k2rel_cons_mix_s34.json", "34", "cons_mix"),
    "invade_base_35": load("k2rel_invade_base_s35.json", "35", "invade_base"),
    "invade_base_36": load("k2rel_invade_base_s36.json", "36", "invade_base"),
    "invade_self_37": load("k2rel_invade_self_s37.json", "37", "invade_self"),
    "invade_self_38": load("k2rel_invade_self_s38.json", "38", "invade_self"),
}
TRAJ = {k: v["traj"] for k, v in CELLS.items()}


def kept_other_shares(cell):
    """share of the judge's kept picks that came from the OTHER source, per round."""
    out = []
    for rnd in CELLS[cell]["rounds_raw"]:
        kept = tot = 0
        for it in rnd:
            owners = it["cand_owner"]
            kept += sum(1 for i in it["kept_idx"] if owners[i] == "cogen")
            tot += len(it["kept_idx"])
        out.append(kept / tot)
    return out


def mean(xs):
    return sum(xs) / len(xs)


# lane 1 — slow rescue (scoring judge keeps the safer answers)
L1_STARTS = [TRAJ["oracle_mix_31"][0], TRAJ["oracle_mix_32"][0]]      # 0.927, 1.000
L1_ENDS = [TRAJ["oracle_mix_31"][-1], TRAJ["oracle_mix_32"][-1]]      # 0.344, 0.484
L1_KEPT = kept_other_shares("oracle_mix_31") + kept_other_shares("oracle_mix_32")

# lane 2 — failed rescue (cautious-prompt judge rejects the safer answers)
L2_STARTS = [TRAJ["cons_mix_34"][0], TRAJ["cons_mix_33"][0]]          # 1.000, 0.875
L2_ENDS = [TRAJ["cons_mix_34"][-1], TRAJ["cons_mix_33"][-1]]          # 1.000, 0.716
L2_KEPT_FINAL = [kept_other_shares("cons_mix_34")[-1], kept_other_shares("cons_mix_33")[-1]]

# lane 3 — fast contamination (weak self-judge keeps the stuck copy)
INV = ("invade_base_35", "invade_base_36", "invade_self_37", "invade_self_38")
L3_STARTS = [TRAJ[c][0] for c in INV]                                  # 0.24 .. 0.36
L3_AFTER1 = [TRAJ[c][1] for c in INV]                                  # >= 0.917
L3_KEPT_R1 = [kept_other_shares(c)[0] for c in INV]                    # 0.96 .. 1.00


def pct(x):
    return int(round(x * 100))


# ---------------------------------------------------------------- geometry
W = 1500
CX1, CX2, CX3, CX4 = 340, 610, 880, 1150   # station centres
GUT_X = 42                                  # left gutter for the lane name

MET_W, MET_H = 42, 120                       # risk meter
POOL_W, POOL_H = 100, 128                     # answer-pool box
KEP_W, KEP_H = 48, 120                        # kept-share bar

LANES_Y0 = 244
LANE_H = 240


def meter(cx, cy, fill_frac, band=None, band_col=GREEN_BAND):
    """vertical risk meter: empty (bottom) = always safe, full (top) = always gambles."""
    x = cx - MET_W / 2
    top = cy - MET_H / 2
    out = [box(x, top, MET_W, MET_H, TRACK, GRAY, 1.5, rx=7)]
    if band is not None:
        b0, b1 = band
        by1 = top + MET_H * (1 - b1)
        bh = MET_H * (b1 - b0)
        out.append(f'<rect x="{x:.1f}" y="{by1:.1f}" width="{MET_W}" height="{bh:.1f}" '
                   f'fill="{band_col}"/>')
    fh = MET_H * fill_frac
    out.append(f'<rect x="{x:.1f}" y="{top + MET_H - fh:.1f}" width="{MET_W}" height="{fh:.1f}" '
               f'rx="4" fill="{SLATE}"/>')
    out.append(box(x, top, MET_W, MET_H, "none", GRAY, 1.5, rx=7))
    return "\n".join(out)


def pool(cx, cy, other_col):
    """rounded pool box holding 6 tokens: left column = own (blue), right = another source."""
    x = cx - POOL_W / 2
    top = cy - POOL_H / 2
    out = [box(x, top, POOL_W, POOL_H, "white", GRAY, 2, rx=12)]
    xs = (cx - 23, cx + 23)
    ys = (cy - 38, cy, cy + 38)
    for col_i, cxx in enumerate(xs):
        col = BLUE if col_i == 0 else other_col
        for cyy in ys:
            out.append(f'<circle cx="{cxx:.1f}" cy="{cyy:.1f}" r="13" fill="{col}" '
                       f'stroke="white" stroke-width="1.6"/>')
    return "\n".join(out)


def kept_bar(cx, cy, other_share, other_col):
    """proportional bar: top segment = kept from the other source, bottom = own.
    the two segment heights match the actual kept share."""
    x = cx - KEP_W / 2
    top = cy - KEP_H / 2
    oth_h = KEP_H * other_share
    out = [
        f'<rect x="{x:.1f}" y="{top:.1f}" width="{KEP_W}" height="{oth_h:.1f}" fill="{other_col}"/>',
        f'<rect x="{x:.1f}" y="{top + oth_h:.1f}" width="{KEP_W}" height="{KEP_H - oth_h:.1f}" fill="{BLUE}"/>',
        box(x, top, KEP_W, KEP_H, "none", GRAY, 1.8, rx=6),
    ]
    return "\n".join(out)


b = []

# ---- title + one line of setup ----
b.append(ctext(W // 2, 52, "A shared answer pool amplifies whichever source the judge prefers", 31, INK, "bold"))
sub, sub_end = cwrap(W // 2, 90,
    "Each model retrains on the answers a judge keeps. Here half the answer pool comes from another source. "
    "Score = the share of the model's free answers that choose the risky gamble (0 = always safe, 1 = always gambles).",
    BODY, 118, GRAY)
b.append(sub)

# ---- legend: the three sources ----
leg_y = sub_end + 24
items = [(BLUE, "the model's own answers"),
         (GREEN, "answers from the base model"),
         (RED, "answers from a stuck copy")]
widths = [26 + len(t) * 10.4 for _, t in items]
total = sum(widths) + 56 * (len(items) - 1)
lx = W // 2 - total / 2
for (col, t), wd in zip(items, widths):
    b.append(f'<rect x="{lx:.1f}" y="{leg_y - 15:.1f}" width="19" height="19" rx="4" fill="{col}"/>')
    b.append(ltext(lx + 28, leg_y, t, BODY, INK))
    lx += wd + 56
b.append(ctext(W // 2, leg_y + 28,
               "The tall bar is the risk score as a fill: empty = always safe, full = always gambles.",
               BODY, GRAY))

# ---- column headers (station names), drawn once across the top ----
hdr_y = leg_y + 66
headers = [(CX1, "starting model"), (CX2, "the answer pool"),
           (CX3, "what the judge keeps"), (CX4, "where it ends up")]
for hx, ht in headers:
    b.append(ctext(hx, hdr_y, ht, 20, INK, "bold"))
b.append(ctext(CX2, hdr_y + 24, "half its own · half another source", BODY, GRAY))

LANES_Y0 = hdr_y + 40


# ---------------------------------------------------------------- lanes
def lane(i, title, title_col, judge_desc, note, other_col, lane_bg,
         start_fill, start_lbl, end_fill, end_lbl, end_lbl2, end_lbl2_col,
         kept_other, kept_lbl, end_band=None, band_note=None):
    top = LANES_Y0 + i * LANE_H
    cy = top + LANE_H / 2 - 8
    # faint lane background (red only for the harmful contamination lane)
    if lane_bg:
        b.append(f'<rect x="{GUT_X - 6:.1f}" y="{top + 6:.1f}" width="{W - GUT_X - 30:.1f}" '
                 f'height="{LANE_H - 22:.1f}" rx="16" fill="{lane_bg}"/>')

    # gutter: scenario name, judge, and the one-line takeaway for this lane
    b.append(ltext(GUT_X, cy - 52, title, 22, title_col, "bold"))
    jd, jd_end = lwrap(GUT_X, cy - 24, judge_desc, BODY, 24, INK)
    b.append(jd)
    nt, _ = lwrap(GUT_X, jd_end + 16, note, BODY, 24, GRAY, "italic")
    b.append(nt)

    # arrows between the four stations
    b.append(rarrow(CX1 + MET_W / 2 + 6, CX2 - POOL_W / 2 - 6, cy))
    b.append(rarrow(CX2 + POOL_W / 2 + 6, CX3 - KEP_W / 2 - 6, cy))
    b.append(rarrow(CX3 + KEP_W / 2 + 6, CX4 - MET_W / 2 - 6, cy))
    b.append(ctext((CX3 + KEP_W / 2 + CX4 - MET_W / 2) / 2, cy - 14, "train", BODY, GRAY))

    # station 1 — starting model
    b.append(meter(CX1, cy, start_fill))
    b.append(ctext(CX1, cy + MET_H / 2 + 24, start_lbl, BODY, GRAY))

    # station 2 — the pool (6 tokens: 3 own + 3 another source)
    b.append(pool(CX2, cy, other_col))

    # station 3 — what the judge keeps (proportional bar)
    b.append(kept_bar(CX3, cy, kept_other, other_col))
    kl, _ = cwrap(CX3, cy + KEP_H / 2 + 24, kept_lbl, BODY, 22, INK)
    b.append(kl)

    # station 4 — where it ends up
    b.append(meter(CX4, cy, end_fill, band=end_band))
    b.append(ltext(CX4 + MET_W / 2 + 22, cy - 8, end_lbl, BODY, title_col if title_col == RED else INK, "bold"))
    if end_lbl2:
        b.append(ltext(CX4 + MET_W / 2 + 22, cy + 18, end_lbl2, BODY, end_lbl2_col))
    if band_note:
        b.append(ltext(CX4 + MET_W / 2 + 22, cy + 44, band_note, BODY, GREEN))


# lane 1 — slow rescue
lane(
    0,
    "Slow rescue", INK,
    "a scoring judge that keeps the safer answers",
    "Steady supply keeps it moving, but only down to the supplier's own level.",
    GREEN, None,
    mean(L1_STARTS), f"{L1_STARTS[1]:.2f} & {L1_STARTS[0]:.2f}",
    mean(L1_ENDS), f"ends {L1_ENDS[1]:.2f} & {L1_ENDS[0]:.2f}",
    None, GRAY,
    mean(L1_KEPT), f"{pct(min(L1_KEPT))}–{pct(max(L1_KEPT))}% kept from the base answers",
    end_band=(0.30, 0.52),
    band_note="the base model's own level",
)

# lane 2 — failed rescue
lane(
    1,
    "Failed rescue", INK,
    "a cautious-prompt judge",
    "The safer answers are there, but the judge rejects them — one run kept none.",
    GREEN, None,
    mean(L2_STARTS), f"{L2_STARTS[0]:.2f} & {L2_STARTS[1]:.2f}",
    L2_ENDS[0], "stays 1.00",
    f"(other run {L2_ENDS[1]:.2f})", GRAY,
    mean(L2_KEPT_FINAL),
    f"{pct(min(L2_KEPT_FINAL))}–{pct(max(L2_KEPT_FINAL))}% kept from the base answers",
)

# lane 3 — fast contamination (RED accent)
lane(
    2,
    "Fast contamination", RED,
    "a weak self-judge",
    "The added source becomes the training data almost immediately.",
    RED, RED_BG,
    mean(L3_STARTS), f"{min(L3_STARTS):.2f}–{max(L3_STARTS):.2f}",
    0.98, f"{min(L3_AFTER1):.2f}–{max(L3_AFTER1):.2f}",
    "after one round", GRAY,
    mean(L3_KEPT_R1), f"{pct(min(L3_KEPT_R1))}–{pct(max(L3_KEPT_R1))}% kept from the stuck copy",
)

# ---- one takeaway line ----
take_y = LANES_Y0 + 3 * LANE_H + 30
b.append(ctext(W // 2, take_y,
               "Contamination was fast; rescue was slower, partial, and only worked when the judge kept the safer answers.",
               21, INK, "bold"))

H = take_y + 34
svg = svg_doc(W, H, "\n".join(b))
with open(os.path.join(FIGDIR, "synthesis_shared_pool_asymmetry.svg"), "w") as f:
    f.write(svg)
print("wrote synthesis_shared_pool_asymmetry.svg")
print("L1 kept-other %:", pct(min(L1_KEPT)), "-", pct(max(L1_KEPT)),
      "| ends", [round(x, 3) for x in L1_ENDS])
print("L2 kept-other final %:", [pct(x) for x in L2_KEPT_FINAL], "| ends", [round(x, 3) for x in L2_ENDS])
print("L3 kept-other r1 %:", [pct(x) for x in L3_KEPT_R1], "| after 1 round", [round(x, 3) for x in L3_AFTER1])

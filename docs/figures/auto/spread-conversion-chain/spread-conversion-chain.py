#!/usr/bin/env python3
"""Selection converts candidate variation into a new output distribution.

Four-panel figure for the spread->movement conversion-chain result. Reads
experiments/spread_conversion_model.json directly (stdlib only) and draws:

  A  the three distances on one 0-1 candidate-score axis
     (selector gap, pool-supply shift, training displacement, behavioral pull)
  B  which distance predicts behavioral movement (Pearson r bars, 4 slices)
  C  the two-stage conversion chain with the empirical fit coefficients
  D  held-out leave-one-run-out next-spread R^2: chain vs spread-persistence
  inset  what whole-pool spread contains under mixing (within + between source)

House style follows docs/figures/src/make_figures.py and
docs/figures/auto/two-dials-clean/: white background, one bold plain-language
headline, fat real-data marks, house colors, min font ~17px, modest width.
Every plotted number is read from the JSON at run time; positions in panel A
are schematic and labelled as such. Regenerate:  python3 spread-conversion-chain.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
JSON = os.path.join(HERE, "..", "..", "..", "..",
                    "experiments", "spread_conversion_model.json")

INK = "#1a1a1a"
BLUE = "#1f6fd0"     # selector gap (kept - whole pool)
GREEN = "#1f9e57"    # training displacement / own generated pool (protagonist)
RED = "#d1341f"      # emphasis on the mixed-pool gain / directional note
PURPLE = "#9427b5"   # pool-supply shift / between-source (outside supply)
AMBER = "#c07d18"    # behavioral pull (bridge to the separate readout)
GRAY = "#6b7684"     # recessive: axes, muted notes, persistence baseline
GRID = "#e4e4e0"
GREEN_FILL = "#eef5ee"
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


def txt(x, y, s, size=18, color=INK, weight="normal", anchor="start",
        halo=False, rot=None):
    h = ('stroke="white" stroke-width="5" stroke-linejoin="round" '
         'paint-order="stroke" ') if halo else ""
    r = f'transform="rotate({rot[0]} {rot[1]:.1f} {rot[2]:.1f})" ' if rot else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
            f'font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'{r}{h}text-anchor="{anchor}">{esc(s)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=10):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def vbar(x, base_y, top_y_at_1, w, value, color, stroke=None):
    h = (base_y - top_y_at_1) * value
    s = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ""
    return (f'<rect x="{x:.1f}" y="{base_y-h:.1f}" width="{w:.1f}" '
            f'height="{h:.1f}" rx="4" fill="{color}"{s}/>')


def f3(x):
    return f"{x:.3f}".replace("-", "−")


def dot3(x):
    """r or R^2 to 3 decimals without the leading zero, e.g. .791."""
    return f"{x:.3f}"[1:]


def pct(x):
    return f"{round(x * 100)}%"


# ------------------------------------------------------------------ data
D = json.load(open(JSON))
drift = D["drift_coordinate_comparison"]
chain = D["observed_training_displacement_chain"]
fac = D["factorized_training_displacement_chain"]
var = D["mixed_pool_variance_decomposition"]
counts = D["counts"]

PRED = [
    ("whole_pool_selector_gap", "selector gap", BLUE),
    ("self_relative_training_displacement", "training displacement", GREEN),
    ("behavioral_pull", "behavioral pull", AMBER),
]
B_SLICES = [("all", "all"), ("mixed", "mixed"),
            ("base-mixed", "base-mixed"), ("peer-mixed", "peer-mixed")]
D_SLICES = [("all", "all"), ("self-only", "self-only"), ("mixed", "mixed")]

# ------------------------------------------------------------------ canvas
W, H = 1200, 1640
b = [f'<rect width="{W}" height="{H}" fill="white"/>']

b.append("<defs>"
         + "".join(
             f'<marker id="ar{cid}" viewBox="0 0 10 10" refX="8.5" refY="5" '
             f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
             f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{col}"/></marker>'
             for cid, col in (("K", INK), ("Gy", GRAY)))
         + "</defs>")

# ------------------------------------------------------------------ headline
b.append(txt(W / 2, 46, "Selection converts candidate variation into a new "
             "output distribution", 30, INK, "bold", "middle"))
b.append(txt(W / 2, 80, f"{counts['rounds']} rounds from {counts['runs']} "
             "OLMo / Qwen runs; next-spread tests use "
             f"{counts['transitions']} consecutive transitions with "
             "leave-one-run-out fits", 18, GRAY, "normal", "middle"))

# ------------------------------------------------------------------ spine ribbon
SPINE = [("offered spread", GRAY), ("selector gap", BLUE),
         ("training displacement", GREEN), ("Δ own generated mean", GREEN),
         ("Δ own generated spread", INK)]
chip_h, chip_y, gap = 34, 112, 30
widths = [len(t) * 8.6 + 26 for t, _ in SPINE]
total = sum(widths) + gap * (len(SPINE) - 1)
cx = (W - total) / 2
for i, (t, col) in enumerate(SPINE):
    w = widths[i]
    b.append(box(cx, chip_y, w, chip_h, "white", col, 2.2, rx=17))
    b.append(txt(cx + w / 2, chip_y + 23, t, 17, col, "bold", "middle"))
    if i < len(SPINE) - 1:
        b.append(f'<line x1="{cx+w+5:.1f}" y1="{chip_y+chip_h/2}" '
                 f'x2="{cx+w+gap-5:.1f}" y2="{chip_y+chip_h/2}" '
                 f'stroke="{GRAY}" stroke-width="3" marker-end="url(#arGy)"/>')
    cx += w + gap


def panel(x, y, w, h, tag, title, title_w=120):
    b.append(box(x, y, w, h, "white", GRAY, 1.5, rx=12))
    b.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="34" height="34" rx="10" '
             f'fill="{INK}"/>')
    b.append(txt(x + 17, y + 25, tag, 20, "white", "bold", "middle"))
    for j, ln in enumerate(wrap(title, title_w)):
        b.append(txt(x + 46, y + 24 + j * 24, ln, 20, INK, "bold"))


# ================================================================ PANEL A
AX, AY, AW, AH = 40, 160, 1120, 320
panel(AX, AY, AW, AH, "A", "Three distances live on one candidate-score axis")

# highlighted takeaway, top-right
tk_x, tk_w = 660, 480
b.append(box(tk_x, AY + 14, tk_w, 62, GREEN_FILL, GREEN, 2, rx=10))
b.append(txt(tk_x + 16, AY + 39, "Kept minus whole pool measures the selector.",
             17, INK, "normal"))
b.append(txt(tk_x + 16, AY + 63, "Kept minus the model's own pool measures the "
             "update.", 17, INK, "bold"))

ax0, ax1, axy = AX + 120, AX + AW - 55, AY + 150
b.append(f'<line x1="{ax0}" y1="{axy}" x2="{ax1}" y2="{axy}" '
         f'stroke="{INK}" stroke-width="2"/>')


def AXx(s):
    return ax0 + (ax1 - ax0) * s


b.append(txt(ax0 - 20, axy + 6, "0", 17, GRAY, "normal", "middle"))
b.append(txt(ax1 + 20, axy + 6, "1", 17, GRAY, "normal", "middle"))
b.append(txt(AX + 44, axy - 8, "candidate", 17, GRAY, "normal", "middle"))
b.append(txt(AX + 44, axy + 12, "score", 17, GRAY, "normal", "middle"))

# schematic mean positions (labelled schematic in the footer)
Q, P, V, K = 0.22, 0.40, 0.54, 0.70
MARK = [(Q, "q", GREEN), (P, "p", BLUE), (V, "v", AMBER), (K, "k", INK)]

# small outside-supply block between q and p (why p != q under mixing)
b.append(f'<rect x="{AXx(Q):.1f}" y="{axy-12:.1f}" width="{AXx(P)-AXx(Q):.1f}" '
         f'height="12" fill="{PURPLE}" opacity="0.18"/>')

for s, sym, col in MARK:
    b.append(f'<circle cx="{AXx(s):.1f}" cy="{axy}" r="7" fill="{col}" '
             f'stroke="white" stroke-width="2"/>')
    b.append(txt(AXx(s), axy - 28, sym, 21, col, "bold", "middle", halo=True))


def hbracket(s1, s2, yb, color, label, above):
    x1, x2 = AXx(s1), AXx(s2)
    tick = 8 if above else -8              # point toward the axis
    lyoff = -9 if above else 23
    b.append(f'<path d="M {x1:.1f} {yb+tick:.1f} L {x1:.1f} {yb:.1f} '
             f'L {x2:.1f} {yb:.1f} L {x2:.1f} {yb+tick:.1f}" fill="none" '
             f'stroke="{color}" stroke-width="2.4"/>')
    b.append(txt((x1 + x2) / 2, yb + lyoff, label, 17, color, "bold",
                 "middle", halo=True))


# training displacement (green) above the axis = q -> k (the sum)
hbracket(Q, K, axy - 52, GREEN, "training displacement = k − q", above=True)
# components below the axis, tiling exactly at p
hbracket(Q, P, axy + 34, PURPLE, "pool-supply shift = p − q", above=False)
hbracket(P, K, axy + 34, BLUE, "selector gap = k − p", above=False)
# behavioral pull (amber) lower = v -> k
hbracket(V, K, axy + 72, AMBER, "behavioral pull = k − v", above=False)

b.append(txt(AX + 20, AY + AH - 34,
             "training displacement = pool-supply shift + selector gap    ·    "
             "outside candidates create the pool-supply shift, so p ≠ q; in "
             "self-only pools p = q and the two coincide", 17, GRAY, "normal"))
b.append(txt(AX + 20, AY + AH - 12,
             "q own generated mean    p whole offered pool mean    "
             "k kept training-target mean    v separate behavioral value",
             17, GRAY, "normal"))

# ================================================================ PANEL B
BX, BY, BW, BH = 40, 500, 1120, 322
panel(BX, BY, BW, BH, "B",
      "The self-relative gap tracks behavioral movement best — and its edge "
      "grows under pool mixing")

lx, ly = BX + 46, BY + 54
for name, col in (("selector gap", BLUE), ("training displacement", GREEN),
                  ("behavioral pull", AMBER)):
    b.append(f'<rect x="{lx:.1f}" y="{ly-14}" width="18" height="18" rx="3" '
             f'fill="{col}"/>')
    b.append(txt(lx + 25, ly + 1, name, 17, col,
                 "bold" if col == GREEN else "normal"))
    lx += 42 + len(name) * 9.5
b.append(txt(lx + 6, ly + 1, "★ the generator-update quantity", 17, GREEN,
             "bold"))
for j, ln in enumerate(wrap(
        "Pearson r of each distance with the round-to-round change in the "
        "behavioral value; behavioral pull bridges to that separate readout, "
        "not a rival selector.", 108)):
    b.append(txt(BX + 46, BY + 80 + j * 20, ln, 17, GRAY, "normal"))

b_base, b_top = BY + 274, BY + 116
b_x0, b_x1 = BX + 92, BX + BW - 30
for g in (0.2, 0.4, 0.6, 0.8, 1.0):
    yy = b_base - (b_base - b_top) * g
    b.append(f'<line x1="{b_x0}" y1="{yy:.1f}" x2="{b_x1}" y2="{yy:.1f}" '
             f'stroke="{GRID}" stroke-width="1"/>')
    b.append(txt(b_x0 - 10, yy + 5, f"{g:g}", 17, GRAY, "normal", "end"))
b.append(f'<line x1="{b_x0}" y1="{b_base}" x2="{b_x1}" y2="{b_base}" '
         f'stroke="{INK}" stroke-width="2"/>')
b.append(txt(b_x0 - 46, (b_top + b_base) / 2, "Pearson r", 17, GRAY, "normal",
             "middle", rot=(-90, b_x0 - 46, (b_top + b_base) / 2)))

ng = len(B_SLICES)
gw = (b_x1 - b_x0) / ng
barw, bgap = 52, 8
for gi, (skey, slabel) in enumerate(B_SLICES):
    gcx = b_x0 + (gi + 0.5) * gw
    n = drift[skey]["whole_pool_selector_gap"]["n"]
    for pi, (pkey, _pname, col) in enumerate(PRED):
        r = drift[skey][pkey]["r"]
        bx = gcx - (1.5 * barw + bgap) + pi * (barw + bgap)
        emph = (col == GREEN)
        b.append(vbar(bx, b_base, b_top, barw, r, col,
                      stroke=INK if emph else None))
        b.append(txt(bx + barw / 2, b_base - (b_base - b_top) * r - 8,
                     dot3(r), 17, col, "bold" if emph else "normal", "middle"))
    b.append(txt(gcx, b_base + 24, slabel, 18, INK, "bold", "middle"))
    b.append(txt(gcx, b_base + 44, f"{n} rounds", 17, GRAY, "normal", "middle"))

# ================================================================ PANEL C
CX, CY, CW, CH = 40, 842, 1120, 262
panel(CX, CY, CW, CH, "C",
      "The chain: displacement moves the generator's mean, and the mean sets "
      "next-round spread")

s1a = chain["all"]["stage_1_delta_own_mean_vs_training_displacement"]
s2a = chain["all"]["stage_2_delta_own_spread_vs_delta_headroom"]
s1m = chain["mixed"]["stage_1_delta_own_mean_vs_training_displacement"]
s2m = chain["mixed"]["stage_2_delta_own_spread_vs_delta_headroom"]
n_all = chain["all"]["n_transitions"]
n_mix = chain["mixed"]["n_transitions"]

nodes = [(CX + 30, "training displacement", "kept − own pool", GREEN),
         (CX + 450, "change in own", "generated mean q", GREEN),
         (CX + 870, "change in own", "generated spread", INK)]
node_y, node_w, node_h = CY + 76, 220, 60
for nx, l1, l2, col in nodes:
    b.append(box(nx, node_y, node_w, node_h, "white", col, 2.4, rx=10))
    b.append(txt(nx + node_w / 2, node_y + 26, l1, 17, col, "bold", "middle"))
    b.append(txt(nx + node_w / 2, node_y + 47, l2, 17, col, "bold", "middle"))
for x1, x2, tag in ((CX + 250, CX + 450, "stage 1"),
                    (CX + 670, CX + 870, "via headroom q(1−q)")):
    b.append(f'<line x1="{x1}" y1="{node_y+node_h/2}" x2="{x2-4}" '
             f'y2="{node_y+node_h/2}" stroke="{INK}" stroke-width="3.5" '
             f'marker-end="url(#arK)"/>')
    b.append(txt((x1 + x2) / 2, node_y - 8, tag, 17, GRAY, "normal", "middle",
                 halo=True))

eqy = node_y + node_h + 40
b.append(txt(CX + 30, eqy, "stage 1", 17, GREEN, "bold"))
b.append(txt(CX + 118, eqy,
             f"Δ own mean = {f3(s1a['intercept'])} + {f3(s1a['slope'])} × "
             f"training displacement   (all {n_all}, r = {s1a['r']:.3f};  "
             f"mixed {n_mix}: {f3(s1m['intercept'])} + {f3(s1m['slope'])}×, "
             f"r = {s1m['r']:.3f})", 17, INK, "normal"))
b.append(txt(CX + 30, eqy + 28, "stage 2", 17, INK, "bold"))
b.append(txt(CX + 118, eqy + 28,
             f"Δ own spread = {f3(s2a['intercept'])} + {f3(s2a['slope'])} × "
             f"Δ[q(1−q)]   (all {n_all}, r = {s2a['r']:.3f};  mixed {n_mix}: "
             f"slope {f3(s2m['slope'])}, r = {s2m['r']:.3f})", 17, INK,
             "normal"))
b.append(txt(CX + 30, eqy + 58,
             "q moves toward 0 or 1 → less next-round spread        "
             "q moves toward 0.5 → more next-round spread        "
             "(round number is not a term)", 17, RED, "bold"))

# ================================================================ PANEL D
DX, DY, DW, DH = 40, 1124, 800, 360
panel(DX, DY, DW, DH, "D",
      "Held out one whole run at a time, the chain beats spread-persistence",
      title_w=54)
b.append(txt(DX + 46, DY + 74,
             "leave-one-run-out R² predicting the model's own next-round "
             "candidate spread;", 17, GRAY, "normal"))
b.append(txt(DX + 46, DY + 94,
             "every held-out run is excluded from the fit that predicts it.",
             17, GRAY, "normal"))
b.append(f'<rect x="{DX+46}" y="{DY+110}" width="18" height="18" rx="3" '
         f'fill="{GREEN}"/>')
b.append(txt(DX + 71, DY + 125, "conversion chain", 17, GREEN, "bold"))
b.append(f'<rect x="{DX+280}" y="{DY+110}" width="18" height="18" rx="3" '
         f'fill="{GRAY}"/>')
b.append(txt(DX + 305, DY + 125, "spread persistence", 17, GRAY, "normal"))

d_base, d_top = DY + 300, DY + 156
d_x0, d_x1 = DX + 82, DX + DW - 30
for g in (0.2, 0.4, 0.6, 0.8, 1.0):
    yy = d_base - (d_base - d_top) * g
    b.append(f'<line x1="{d_x0}" y1="{yy:.1f}" x2="{d_x1}" y2="{yy:.1f}" '
             f'stroke="{GRID}" stroke-width="1"/>')
    b.append(txt(d_x0 - 10, yy + 5, f"{g:g}", 17, GRAY, "normal", "end"))
b.append(f'<line x1="{d_x0}" y1="{d_base}" x2="{d_x1}" y2="{d_base}" '
         f'stroke="{INK}" stroke-width="2"/>')
b.append(txt(d_x0 - 44, (d_top + d_base) / 2, "next-spread R²", 17, GRAY,
             "normal", "middle", rot=(-90, d_x0 - 44, (d_top + d_base) / 2)))

ndg = len(D_SLICES)
dgw = (d_x1 - d_x0) / ndg
dbarw, dgap = 62, 16
for gi, (skey, slabel) in enumerate(D_SLICES):
    gcx = d_x0 + (gi + 0.5) * dgw
    loro = chain[skey]["leave_one_run_out"]
    n = chain[skey]["n_transitions"]
    for j, (val, col) in enumerate((
            (loro["conversion_chain"]["r2"], GREEN),
            (loro["spread_persistence"]["r2"], GRAY))):
        bx = gcx - (dbarw + dgap / 2) + j * (dbarw + dgap)
        b.append(vbar(bx, d_base, d_top, dbarw, val, col))
        b.append(txt(bx + dbarw / 2, d_base - (d_base - d_top) * val - 8,
                     dot3(val), 18, col, "bold", "middle"))
    b.append(txt(gcx, d_base + 24, slabel, 18, INK, "bold", "middle"))
    b.append(txt(gcx, d_base + 44, f"{n} transitions", 17, GRAY, "normal",
                 "middle"))

# ================================================================ INSET
IX, IY, IW, IH = 862, 1124, 298, 360
panel(IX, IY, IW, IH, "★",
      "What whole-pool spread contains under mixing", title_w=24)
b.append(txt(IX + 20, IY + 84, "mean per-item spread =", 17, GRAY, "normal"))
b.append(txt(IX + 20, IY + 104, "within-source + between-source", 17, GRAY,
             "normal"))
b.append(f'<rect x="{IX+20}" y="{IY+118}" width="16" height="16" rx="3" '
         f'fill="{GREEN}"/>')
b.append(txt(IX + 42, IY + 131, "within source", 17, GREEN, "bold"))
b.append(f'<rect x="{IX+168}" y="{IY+118}" width="16" height="16" rx="3" '
         f'fill="{PURPLE}"/>')
b.append(txt(IX + 190, IY + 131, "between source", 17, PURPLE, "bold"))

i_base, i_top = IY + 300, IY + 180
i_scale = (i_base - i_top) / 0.36
for gi, skey in enumerate(("base-mixed", "peer-mixed")):
    v = var[skey]
    # SD-scale split: components add at the spread scale (within + increment =
    # total, to the JSON rounding error). "increment" is the correct label.
    within = v["mean_sd_if_between_source_variance_removed_per_prompt"]
    between = v["mean_sd_increment_from_between_source_variance"]
    share = v["sd_increment_share_of_mean_total_spread"]
    total = v["mean_total_spread"]
    n = v["n_rounds"]
    bw, bx = 78, IX + 40 + gi * 130
    hw, hb = within * i_scale, between * i_scale
    b.append(f'<rect x="{bx:.1f}" y="{i_base-hw:.1f}" width="{bw}" '
             f'height="{hw:.1f}" rx="4" fill="{GREEN}"/>')
    b.append(f'<rect x="{bx:.1f}" y="{i_base-hw-hb:.1f}" width="{bw}" '
             f'height="{hb:.1f}" fill="{PURPLE}"/>')
    b.append(txt(bx + bw / 2, i_base - hw / 2 + 6, f"{within:.2f}", 17, "white",
                 "bold", "middle"))
    b.append(txt(bx + bw / 2, i_base - hw - hb / 2 + 6, f"{between:.2f}", 17,
                 "white", "bold", "middle"))
    b.append(txt(bx + bw / 2, i_base - hw - hb - 28, f"total {total:.2f}", 17,
                 INK, "bold", "middle"))
    b.append(txt(bx + bw / 2, i_base - hw - hb - 8, f"between {pct(share)}", 17,
                 PURPLE, "bold", "middle"))
    b.append(txt(bx + bw / 2, i_base + 24, skey, 18, INK, "bold", "middle"))
    b.append(txt(bx + bw / 2, i_base + 44, f"{n} rounds", 17, GRAY, "normal",
                 "middle"))

# ================================================================ VALIDATION NOTES
fa = fac["all"]["leave_one_run_out"]
fm = fac["mixed"]["leave_one_run_out"]
fac_all_n = fac["all"]["n_transitions"]
fac_mix_n = fac["mixed"]["n_transitions"]
lca = chain["all"]["leave_one_condition_out"]
lcm = chain["mixed"]["leave_one_condition_out"]

foot = []
foot += [(ln, 17) for ln in wrap(
    "Fully factorized before selection (pool-supply shift + "
    "0.96·agreement·spread): leave-one-run-out R² "
    f"{fa['conversion_chain']['r2']:.3f} vs "
    f"{fa['spread_persistence']['r2']:.3f} overall ({fac_all_n} transitions), "
    f"{fm['conversion_chain']['r2']:.3f} vs "
    f"{fm['spread_persistence']['r2']:.3f} mixed ({fac_mix_n}).", 138)]
foot += [(ln, 17) for ln in wrap(
    "Leaving out entire conditions gives the same ordering: "
    f"{lca['conversion_chain']['r2']:.3f} vs "
    f"{lca['spread_persistence']['r2']:.3f} overall, "
    f"{lcm['conversion_chain']['r2']:.3f} vs "
    f"{lcm['spread_persistence']['r2']:.3f} mixed.", 138)]
foot += [(ln, 17) for ln in wrap(
    "Source: experiments/spread_conversion_model.json "
    "(scripts/analysis_spread_conversion_model.py). Panel A positions are "
    "schematic; panel B uses logged rounds, panels C/D use consecutive-round "
    "transitions.", 138)]
ny = 1512
for ln, sz in foot:
    b.append(txt(40, ny, ln, sz, GRAY, "normal"))
    ny += 24

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n' + "\n".join(b) + "\n</svg>")

out = os.path.join(HERE, "spread-conversion-chain.svg")
with open(out, "w") as f:
    f.write(svg)
print("wrote", out)

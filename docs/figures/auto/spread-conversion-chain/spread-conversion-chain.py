#!/usr/bin/env python3
"""Selection converts candidate variation into a new output distribution.

Corrected redraw (2026-07-15). The earlier version folded the continuous
self-report rounds into the conversion claim and quoted 258 "all" transitions.
This version scopes the q(1-q) identity and the conversion chain to the BINARY
RISK score only, tests held-out next-spread on 221 binary-risk transitions with
leave-one-run-out fits, and labels the 60 continuous self-report rounds as
outside the claim.

Panels (spine reads left to right: offered spread -> selector gap ->
training displacement -> change in own generated mean q -> change in next-round
within-prompt spread):

  A  three distances on one 0-1 candidate-score axis
     (selector gap = kept - whole pool; pool-supply shift = whole pool - own
      pool; training displacement = kept - own pool; behavioral pull = kept - v)
  B  which distance tracks behavioral movement (Pearson r; all pools) -- the
     self-relative training displacement wins, and its edge grows under mixing
  C  the binary-risk conversion chain: displacement moves own mean q, and the
     exact identity mean within-prompt variance = q(1-q) - Var(prompt means)
     turns that mean into next-round spread
  D  LOAD-BEARING: held out one whole run at a time, next-spread R^2 for the
     conversion chain (exact q(1-q) split and headroom form) vs spread
     persistence, over the binary-risk transitions
  inset  what whole-pool spread contains under mixing (within + between source)

Reads two result files directly (stdlib only):
  experiments/spread_conversion_model.json   -- headroom chain, persistence,
      drift coordinates, chain coefficients, mixed-pool variance split
  experiments/spread_definition_audit.json   -- binary_exact_decomposition_model
      (exact q(1-q) next-spread R^2)
Every plotted number is read at run time. Panel A positions are schematic and
labelled as such. Regenerate:  python3 spread-conversion-chain.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CONV_JSON = os.path.join(HERE, "..", "..", "..", "..",
                         "experiments", "spread_conversion_model.json")
AUDIT_JSON = os.path.join(HERE, "..", "..", "..", "..",
                          "experiments", "spread_definition_audit.json")

INK = "#1a1a1a"
BLUE = "#1f6fd0"     # selector gap (kept - whole pool)
GREEN = "#1f9e57"    # training displacement / own generated pool (protagonist)
RED = "#d1341f"      # emphasis on the directional note / warning
PURPLE = "#9427b5"   # pool-supply shift / between-source (outside supply)
AMBER = "#c07d18"    # behavioral pull (bridge to the separate readout)
GRAY = "#6b7684"     # recessive: axes, muted notes, persistence baseline
GRID = "#e4e4e0"
GREEN_FILL = "#eef5ee"
AMBER_FILL = "#fbf3e2"
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


def vbar(x, base_y, top_y_at_1, w, value, color, fill=None, stroke=None,
         dash=False):
    h = (base_y - top_y_at_1) * value
    f = fill if fill is not None else color
    s = f' stroke="{stroke}" stroke-width="2.4"' if stroke else ""
    d = ' stroke-dasharray="5 3"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{base_y-h:.1f}" width="{w:.1f}" '
            f'height="{h:.1f}" rx="4" fill="{f}"{s}{d}/>')


def f3(x):
    return f"{x:.3f}".replace("-", "−")


def dot3(x):
    """Non-negative r or R^2 to 3 decimals without the leading zero: .778."""
    return f"{x:.3f}"[1:]


def pct(x):
    return f"{round(x * 100)}%"


# ------------------------------------------------------------------ data
CONV = json.load(open(CONV_JSON))
AUDIT = json.load(open(AUDIT_JSON))

counts = CONV["counts"]
drift = CONV["drift_coordinate_comparison"]
och = CONV["observed_training_displacement_chain"]
var = CONV["mixed_pool_variance_decomposition"]
idcheck = CONV["identity_checks"]["max_abs_training_displacement_identity_error"]
exact = AUDIT["binary_exact_decomposition_model"]

N_ROUNDS = counts["rounds"]
N_RUNS = counts["runs"]
N_BIN = counts["binary_risk_transitions"]          # 221

# ------------------------------------------------------------------ canvas
W, H = 1200, 2028
b = [f'<rect width="{W}" height="{H}" fill="white"/>']
b.append("<defs>"
         + "".join(
             f'<marker id="ar{cid}" viewBox="0 0 10 10" refX="8.5" refY="5" '
             f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
             f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{col}"/></marker>'
             for cid, col in (("K", INK), ("Gy", GRAY), ("G", GREEN)))
         + "</defs>")

# ------------------------------------------------------------------ headline
b.append(txt(W / 2, 46, "Selection converts candidate variation into a new "
             "output distribution", 30, INK, "bold", "middle"))
b.append(txt(W / 2, 78,
             f"Selector accounting: {N_ROUNDS} rounds, {N_RUNS} OLMo / Qwen "
             f"runs.   Binary-risk conversion claim: {N_BIN} transitions, held "
             "out one entire run at a time.", 18, GRAY, "normal", "middle"))

# ------------------------------------------------------------------ spine ribbon
SPINE = [("offered spread", GRAY), ("selector gap", BLUE),
         ("training displacement", GREEN), ("Δ own generated mean q", GREEN),
         ("Δ next-round own spread", INK)]
chip_h, chip_y, gap = 34, 98, 26
widths = [len(t) * 8.4 + 24 for t, _ in SPINE]
total = sum(widths) + gap * (len(SPINE) - 1)
cx = (W - total) / 2
for i, (t, col) in enumerate(SPINE):
    w = widths[i]
    b.append(box(cx, chip_y, w, chip_h, "white", col, 2.2, rx=17))
    b.append(txt(cx + w / 2, chip_y + 23, t, 17, col, "bold", "middle"))
    if i < len(SPINE) - 1:
        b.append(f'<line x1="{cx+w+4:.1f}" y1="{chip_y+chip_h/2}" '
                 f'x2="{cx+w+gap-4:.1f}" y2="{chip_y+chip_h/2}" '
                 f'stroke="{GRAY}" stroke-width="3" marker-end="url(#arGy)"/>')
    cx += w + gap
b.append(txt(W / 2, chip_y + chip_h + 22,
             "selector gap = kept − whole offered pool     ·     training "
             "displacement = kept − the model’s own generated pool",
             17, GRAY, "normal", "middle"))

# ------------------------------------------------------------------ definition banner
DEF_Y = 170
b.append(box(40, DEF_Y, 1120, 56, GREEN_FILL, GREEN, 2, rx=10))
b.append(txt(60, DEF_Y + 24,
             "Within-prompt spread = population SD (ddof=0) of the candidate "
             "value scores inside each prompt, averaged equally over prompts "
             "— not a pooled SD.", 17, INK, "normal"))
b.append(txt(60, DEF_Y + 46,
             "The candidate value score is 0/1 on the risk axis; the q(1−q) "
             "identity and the conversion chain hold on the binary-risk rounds "
             "only (self-report scores are continuous — see scope note).",
             17, INK, "normal"))


def panel(x, y, w, h, tag, title, title_w=120, tag_fill=INK):
    b.append(box(x, y, w, h, "white", GRAY, 1.5, rx=12))
    b.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="34" height="34" rx="10" '
             f'fill="{tag_fill}"/>')
    b.append(txt(x + 17, y + 25, tag, 20, "white", "bold", "middle"))
    for j, ln in enumerate(wrap(title, title_w)):
        b.append(txt(x + 46, y + 24 + j * 24, ln, 20, INK, "bold"))


# ================================================================ PANEL A
AX, AY, AW, AH = 40, 240, 1120, 316
panel(AX, AY, AW, AH, "A", "Three distances live on one candidate-score axis")

tk_x, tk_w = 640, 500
b.append(box(tk_x, AY + 12, tk_w, 62, GREEN_FILL, GREEN, 2, rx=10))
b.append(txt(tk_x + 16, AY + 37, "Kept minus whole pool measures the selector.",
             17, INK, "normal"))
b.append(txt(tk_x + 16, AY + 61, "Kept minus the model’s own pool measures "
             "the update.", 17, INK, "bold"))

ax0, ax1, axy = AX + 120, AX + AW - 55, AY + 150
b.append(f'<line x1="{ax0}" y1="{axy}" x2="{ax1}" y2="{axy}" '
         f'stroke="{INK}" stroke-width="2"/>')


def AXx(s):
    return ax0 + (ax1 - ax0) * s


b.append(txt(ax0 - 20, axy + 6, "0", 17, GRAY, "normal", "middle"))
b.append(txt(ax1 + 20, axy + 6, "1", 17, GRAY, "normal", "middle"))
b.append(txt(AX + 44, axy - 8, "candidate", 17, GRAY, "normal", "middle"))
b.append(txt(AX + 44, axy + 12, "score", 17, GRAY, "normal", "middle"))

Q, P, V, K = 0.22, 0.40, 0.54, 0.70
MARK = [(Q, "q", GREEN), (P, "p", BLUE), (V, "v", AMBER), (K, "k", INK)]
b.append(f'<rect x="{AXx(Q):.1f}" y="{axy-12:.1f}" width="{AXx(P)-AXx(Q):.1f}" '
         f'height="12" fill="{PURPLE}" opacity="0.18"/>')
for s, sym, col in MARK:
    b.append(f'<circle cx="{AXx(s):.1f}" cy="{axy}" r="7" fill="{col}" '
             f'stroke="white" stroke-width="2"/>')
    b.append(txt(AXx(s), axy - 28, sym, 21, col, "bold", "middle", halo=True))


def hbracket(s1, s2, yb, color, label, above):
    x1, x2 = AXx(s1), AXx(s2)
    tick = 8 if above else -8
    lyoff = -9 if above else 23
    b.append(f'<path d="M {x1:.1f} {yb+tick:.1f} L {x1:.1f} {yb:.1f} '
             f'L {x2:.1f} {yb:.1f} L {x2:.1f} {yb+tick:.1f}" fill="none" '
             f'stroke="{color}" stroke-width="2.4"/>')
    b.append(txt((x1 + x2) / 2, yb + lyoff, label, 17, color, "bold",
                 "middle", halo=True))


hbracket(Q, K, axy - 52, GREEN, "training displacement = k − q", above=True)
hbracket(Q, P, axy + 34, PURPLE, "pool-supply shift = p − q", above=False)
hbracket(P, K, axy + 34, BLUE, "selector gap = k − p", above=False)
hbracket(V, K, axy + 72, AMBER, "behavioral pull = k − v", above=False)

b.append(txt(AX + 20, AY + AH - 34,
             "training displacement = pool-supply shift + selector gap  (holds "
             f"to {idcheck:g}).   Outside candidates create the pool-supply "
             "shift, so p ≠ q; in self-only pools p = q and the two "
             "coincide.", 17, GRAY, "normal"))
b.append(txt(AX + 20, AY + AH - 12,
             "q own generated mean    p whole offered pool mean    "
             "k kept training-target mean    v separate behavioral value    "
             "(schematic positions)", 17, GRAY, "normal"))

# ================================================================ PANEL B
BX, BY, BW, BH = 40, 572, 1120, 330
panel(BX, BY, BW, BH, "B",
      "The self-relative gap tracks behavioral movement best — and its "
      "edge grows under pool mixing")

PRED = [("whole_pool_selector_gap", "selector gap", BLUE),
        ("self_relative_training_displacement", "training displacement", GREEN),
        ("behavioral_pull", "behavioral pull", AMBER)]
B_SLICES = [("all", "all pools"), ("mixed", "mixed"),
            ("base-mixed", "base-mixed"), ("peer-mixed", "peer-mixed")]

lx, ly = BX + 46, BY + 56
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
        "separate behavioral value readout (all pools, not just binary risk). "
        "Behavioral pull bridges to that readout — it is not a rival "
        "definition of selection.", 112)):
    b.append(txt(BX + 46, BY + 82 + j * 20, ln, 17, GRAY, "normal"))

b_base, b_top = BY + 284, BY + 128
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
    for pi, (pkey, _pn, col) in enumerate(PRED):
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
CX, CY, CW, CH = 40, 918, 1120, 300
panel(CX, CY, CW, CH, "C",
      "The binary-risk chain: displacement moves the mean, the exact q(1−q) "
      "identity sets next spread", title_w=80)

s1 = och["binary-risk-axis"]["stage_1_delta_own_mean_vs_training_displacement"]
s2 = och["binary-risk-axis"]["stage_2_delta_own_spread_vs_delta_headroom"]
s1m = och["binary-risk-mixed"]["stage_1_delta_own_mean_vs_training_displacement"]
s2m = och["binary-risk-mixed"]["stage_2_delta_own_spread_vs_delta_headroom"]
n_bin = och["binary-risk-axis"]["n_transitions"]
n_mix = och["binary-risk-mixed"]["n_transitions"]

nodes = [(CX + 30, "training displacement", "kept − own pool", GREEN),
         (CX + 445, "change in own", "generated mean q", GREEN),
         (CX + 860, "change in own", "within-prompt spread", INK)]
node_y, node_w, node_h = CY + 66, 220, 58
for nx, l1, l2, col in nodes:
    b.append(box(nx, node_y, node_w, node_h, "white", col, 2.4, rx=10))
    b.append(txt(nx + node_w / 2, node_y + 25, l1, 17, col, "bold", "middle"))
    b.append(txt(nx + node_w / 2, node_y + 46, l2, 17, col, "bold", "middle"))
for x1, x2, tag in ((CX + 250, CX + 445, "stage 1"),
                    (CX + 665, CX + 860, "exact q(1−q) split")):
    b.append(f'<line x1="{x1}" y1="{node_y+node_h/2}" x2="{x2-4}" '
             f'y2="{node_y+node_h/2}" stroke="{INK}" stroke-width="3.5" '
             f'marker-end="url(#arK)"/>')
    b.append(txt((x1 + x2) / 2, node_y - 8, tag, 17, GRAY, "normal", "middle",
                 halo=True))

eqy = node_y + node_h + 34
b.append(txt(CX + 30, eqy, "stage 1", 17, GREEN, "bold"))
b.append(txt(CX + 118, eqy,
             f"Δ own mean q = {f3(s1['intercept'])} + {f3(s1['slope'])} × "
             f"training displacement    (binary risk {n_bin}, r = "
             f"{s1['r']:.3f};  mixed {n_mix}: {f3(s1m['intercept'])} + "
             f"{f3(s1m['slope'])}×, r = {s1m['r']:.3f})", 17, INK, "normal"))
b.append(txt(CX + 30, eqy + 27, "identity", 17, INK, "bold"))
b.append(txt(CX + 118, eqy + 27,
             "mean within-prompt variance = q(1−q) − Var(prompt means)"
             "     — total binary variance is q(1−q); subtract the "
             "between-prompt part to get what selection can use inside a prompt.",
             17, INK, "normal"))
b.append(txt(CX + 30, eqy + 54, "stage 2", 17, GREEN, "bold"))
b.append(txt(CX + 118, eqy + 54,
             f"Δ own spread = {f3(s2['intercept'])} + {f3(s2['slope'])} × "
             f"Δ[q(1−q)]    (binary risk {n_bin}, r = {s2['r']:.3f};  "
             f"mixed {n_mix}: slope {f3(s2m['slope'])}, r = {s2m['r']:.3f})",
             17, INK, "normal"))
b.append(txt(CX + 30, eqy + 82,
             "q moves toward 0 or 1 → less next-round spread        "
             "q moves toward 0.5 → more next-round spread        "
             "(round number is not a term in the model)", 17, RED, "bold"))

# ================================================================ PANEL D  (load-bearing)
DX, DY, DW, DH = 40, 1234, 1120, 388
panel(DX, DY, DW, DH, "D",
      "Held out one entire run at a time, the conversion chain beats spread-"
      "persistence on next-round own spread", title_w=90, tag_fill=GREEN)

b.append(txt(DX + 46, DY + 74,
             "Leave-one-run-out R² predicting the model’s own "
             "next-round candidate spread; the held-out run is excluded from "
             "the fit that predicts it.  Binary risk score only.", 17, GRAY,
             "normal"))

# legend
D_LEG = [("conversion chain — exact q(1−q) split", GREEN, "solid"),
         ("conversion chain — headroom form", GREEN, "hollow"),
         ("spread persistence (baseline)", GRAY, "solid")]
lgx = DX + 46
for name, col, style in D_LEG:
    if style == "hollow":
        b.append(f'<rect x="{lgx:.1f}" y="{DY+94}" width="18" height="18" '
                 f'rx="3" fill="white" stroke="{col}" stroke-width="2.4"/>')
    else:
        b.append(f'<rect x="{lgx:.1f}" y="{DY+94}" width="18" height="18" '
                 f'rx="3" fill="{col}"/>')
    b.append(txt(lgx + 25, DY + 109, name, 17, col if col != GRAY else GRAY,
                 "bold" if (col == GREEN and style == "solid") else "normal"))
    lgx += 44 + len(name) * 9.0

D_SLICES = [("all binary risk", och["binary-risk-axis"], exact["all_binary_risk"]),
            ("self-only risk", och["binary-risk-self-only"],
             exact["binary_risk_self_only"]),
            ("mixed risk", och["binary-risk-mixed"], exact["binary_risk_mixed"])]

d_base, d_top = DY + 330, DY + 138
d_x0, d_x1 = DX + 90, DX + DW - 34
for g in (0.2, 0.4, 0.6, 0.8, 1.0):
    yy = d_base - (d_base - d_top) * g
    b.append(f'<line x1="{d_x0}" y1="{yy:.1f}" x2="{d_x1}" y2="{yy:.1f}" '
             f'stroke="{GRID}" stroke-width="1"/>')
    b.append(txt(d_x0 - 10, yy + 5, f"{g:g}", 17, GRAY, "normal", "end"))
b.append(f'<line x1="{d_x0}" y1="{d_base}" x2="{d_x1}" y2="{d_base}" '
         f'stroke="{INK}" stroke-width="2"/>')
b.append(txt(d_x0 - 48, (d_top + d_base) / 2, "next-spread R²", 17, GRAY,
             "normal", "middle", rot=(-90, d_x0 - 48, (d_top + d_base) / 2)))

ndg = len(D_SLICES)
dgw = (d_x1 - d_x0) / ndg
dbarw, dbgap = 78, 14
for gi, (slabel, chain_slice, exact_slice) in enumerate(D_SLICES):
    gcx = d_x0 + (gi + 0.5) * dgw
    loro = chain_slice["leave_one_run_out"]
    n = chain_slice["n_transitions"]
    exact_r2 = exact_slice["next_mean_within_prompt_sd"]["r2"]
    head_r2 = loro["conversion_chain"]["r2"]
    pers_r2 = loro["spread_persistence"]["r2"]
    bars = [(exact_r2, GREEN, "solid"),
            (head_r2, GREEN, "hollow"),
            (pers_r2, GRAY, "solid")]
    for j, (val, col, style) in enumerate(bars):
        bx = gcx - (1.5 * dbarw + dbgap) + j * (dbarw + dbgap)
        if style == "hollow":
            b.append(vbar(bx, d_base, d_top, dbarw, val, col, fill="white",
                          stroke=col))
        else:
            b.append(vbar(bx, d_base, d_top, dbarw, val, col,
                          stroke=INK if col == GREEN else None))
        b.append(txt(bx + dbarw / 2, d_base - (d_base - d_top) * val - 9,
                     dot3(val), 18, col,
                     "bold" if col == GREEN and style == "solid" else "normal",
                     "middle"))
    b.append(txt(gcx, d_base + 25, slabel, 19, INK, "bold", "middle"))
    b.append(txt(gcx, d_base + 46, f"{n} transitions", 17, GRAY, "normal",
                 "middle"))

# ================================================================ INSET
IX, IY, IW, IH = 40, 1638, 360, 352
panel(IX, IY, IW, IH, "★",
      "What whole-pool spread contains under mixing", title_w=30)
b.append(txt(IX + 20, IY + 78, "mean per-prompt spread =", 17, GRAY, "normal"))
b.append(txt(IX + 20, IY + 98, "within-source + between-source", 17, GRAY,
             "normal"))
b.append(f'<rect x="{IX+20}" y="{IY+112}" width="16" height="16" rx="3" '
         f'fill="{GREEN}"/>')
b.append(txt(IX + 42, IY + 125, "within source", 17, GREEN, "bold"))
b.append(f'<rect x="{IX+168}" y="{IY+112}" width="16" height="16" rx="3" '
         f'fill="{PURPLE}"/>')
b.append(txt(IX + 190, IY + 125, "between source", 17, PURPLE, "bold"))

i_base, i_top = IY + 300, IY + 180
i_scale = (i_base - i_top) / 0.36
for gi, skey in enumerate(("base-mixed", "peer-mixed")):
    v = var[skey]
    within = v["mean_sd_if_between_source_variance_removed_per_prompt"]
    between = v["mean_sd_increment_from_between_source_variance"]
    share = v["sd_increment_share_of_mean_total_spread"]
    total = v["mean_total_spread"]
    n = v["n_rounds"]
    bw, bx = 78, IX + 44 + gi * 140
    hw, hb = within * i_scale, between * i_scale
    b.append(f'<rect x="{bx:.1f}" y="{i_base-hw:.1f}" width="{bw}" '
             f'height="{hw:.1f}" rx="4" fill="{GREEN}"/>')
    b.append(f'<rect x="{bx:.1f}" y="{i_base-hw-hb:.1f}" width="{bw}" '
             f'height="{hb:.1f}" fill="{PURPLE}"/>')
    b.append(txt(bx + bw / 2, i_base - hw / 2 + 6, f"{within:.2f}", 17, "white",
                 "bold", "middle"))
    b.append(txt(bx + bw / 2, i_base - hw - hb / 2 + 6, f"{between:.2f}", 17,
                 "white", "bold", "middle"))
    b.append(txt(bx + bw / 2, i_base - hw - hb - 26, f"total {total:.2f}", 17,
                 INK, "bold", "middle"))
    b.append(txt(bx + bw / 2, i_base - hw - hb - 7, f"between {pct(share)}", 17,
                 PURPLE, "bold", "middle"))
    b.append(txt(bx + bw / 2, i_base + 24, skey, 17, INK, "bold", "middle"))
    b.append(txt(bx + bw / 2, i_base + 43, f"{n} rounds", 17, GRAY, "normal",
                 "middle"))

# ================================================================ SCOPE + SOURCE
cont = och["continuous-selfreport-axis"]["leave_one_run_out"]
n_cont = och["continuous-selfreport-axis"]["n_transitions"]
va_q = exact["all_binary_risk"]["variance_with_actual_q_next"]["r2"]

sx = IX + IW + 30
sy = IY + 10
b.append(box(sx, sy, W - sx - 40, 130, AMBER_FILL, AMBER, 2, rx=10))
b.append(txt(sx + 18, sy + 28, "Scope: the conversion claim is binary-risk "
             "only.", 18, INK, "bold"))
for j, ln in enumerate(wrap(
        "The candidate value score is 0/1 on the risk axis, but continuous in "
        f"[0,1] on the insecure-code self-report axis. The {60} continuous "
        f"self-report rounds ({n_cont} consecutive transitions) share the same "
        "within-prompt spread definition for selector accounting, but sit "
        "OUTSIDE the q(1−q) conversion claim: there the mean→spread "
        f"chain scores leave-one-run-out R² {f3(cont['conversion_chain']['r2'])} "
        f"versus {cont['spread_persistence']['r2']:.3f} for spread persistence.",
        104)):
    b.append(txt(sx + 18, sy + 52 + j * 21, ln, 17, INK, "normal"))

foot = []
foot += [ln for ln in wrap(
    "Held-out ceiling: supplying the observed next mean q_next raises the "
    f"exact-decomposition within-variance fit to leave-one-run-out R² "
    f"{va_q:.3f} over {N_BIN} transitions, so predicting the mean update is the "
    "larger remaining bottleneck.", 150)]
foot += [ln for ln in wrap(
    "Sources: experiments/spread_conversion_model.json (headroom chain, "
    "persistence, drift coordinates, chain coefficients, variance split; "
    "scripts/analysis_spread_conversion_model.py) and "
    "experiments/spread_definition_audit.json (exact q(1−q) next-spread "
    "R²; scripts/analysis_spread_definition_audit.py). Panel A positions "
    "are schematic; panel B uses logged rounds, panels C/D use consecutive-"
    "round transitions.", 150)]
ny = IY + 168
for ln in foot:
    b.append(txt(sx, ny, ln, 17, GRAY, "normal"))
    ny += 22

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'font-family="{FONT}">\n' + "\n".join(b) + "\n</svg>")

out = os.path.join(HERE, "spread-conversion-chain.svg")
with open(out, "w") as f:
    f.write(svg)
print("wrote", out)

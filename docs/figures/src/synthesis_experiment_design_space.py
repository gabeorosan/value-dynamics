#!/usr/bin/env python3
"""synthesis — the whole program as one design space.

Every self-training run in this project is one choice on each of five knobs:

  base model   x  domain  x  installed value  x  answer pool  x  judge

This figure is a coverage map: rows are the named experiments, the header lists
every option on every knob (the space one COULD run), and a coloured dot marks
the level each experiment actually used. Dot colour = which model organism.
Sparse columns (a level with few/no dots) are the corners we have not run.

Attributions were traced to the committed specs / reports on 2026-07-14:
  K1  experiments/kaggle/kaggle_k1_qwen_anchor_grid/SPEC.md  (4 judge conditions)
  K2  experiments/kaggle/kaggle_k2_olmo_inversion/SPEC.md
  K3  experiments/kaggle/kaggle_k3_em_neutral_grid/SPEC.md
  branch m/h/h2  docs/report_mixed_generator_branch_m.md, report_head2head_olmo.md
  branch e       docs/report_crossfamily_oracle.md   (score "oracle" selector)
  mixed-reopen   docs/report_mixed_reopen_qwen.md
  transmission   docs/report_transmission_with_support.md
  self-judge duels  experiments/em_selfaware_loop/output/head2head_selfjudge.json
  OLMo insecure build  docs/report_olmo_insecure_build.md  (no gate-clearing organism)

Regenerate with:  python3 synthesis_experiment_design_space.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

# ---------------------------------------------------------------- palette
INK = "#1a1a1a"
GRAY = "#6b7684"
BLUE = "#2867b5"     # Qwen  x gambling  (risk-seeking install)
PURPLE = "#8a5a9e"   # Qwen  x insecure-code
GREEN = "#3a7d44"    # OLMo  x gambling  (conservative install)
ATT = "#9aa2ab"      # OLMo  x insecure-code — attempted, no organism

BORDER = "#c6ced6"
GRIDLINE = "#e3e8ee"
GROUP_TINT = "#f2f5f8"      # faint band behind the two "lever" groups
HDR_BG = "#eef2f6"
NAMEBG_ALT = "#f7f9fb"

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


def rect(x, y, w, h, fill, stroke="none", sw=1.4, rx=0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- axes (the space)
# groups: (label, tinted?, [option as list-of-lines, ...])
GROUPS = [
    ("base model", False, [["Qwen"], ["OLMo"]]),
    ("domain", False, [["gamble"], ["code"]]),
    ("installed value", False, [["risky"], ["cautious"]]),
    ("answer pool", True, [["own"], ["fixed", "ref"],
                           ["mixed"], ["duels"]]),
    ("judge  (who keeps the answers)", True,
        [["self"], ["frozen", "base"], ["cautious", "copy"], ["risk", "copy"],
         ["min-", "risk"], ["min-", "insec"], ["random"]]),
]
GSIZE = [len(opts) for _, _, opts in GROUPS]   # [2,2,2,4,7] -> 17 sub-cols

# index handles into (group, option)
BASE_Q, BASE_O = (0, 0), (0, 1)
DOM_G, DOM_C = (1, 0), (1, 1)
DIR_RISK, DIR_CAUT = (2, 0), (2, 1)
POOL_OWN, POOL_REF, POOL_MIX, POOL_DUEL = (3, 0), (3, 1), (3, 2), (3, 3)
J_SELF, J_BASE, J_CAUT, J_RISK, J_MINR, J_MINI, J_RAND = [(4, i) for i in range(7)]

# ---------------------------------------------------------------- rows (the runs)
# color = organism; att=True renders the un-built corner.
ROWS = [
    dict(name="Risk anchor grid", tag="K1", color=BLUE,
         dots=[BASE_Q, DOM_G, DIR_RISK, POOL_OWN, J_SELF, J_BASE, J_RISK, J_RAND],
         result="Self-judge fans wide (0.26→1.00); frozen base stays "
                "narrow (0.47-0.60); copies & random land between."),

    dict(name="Insecure-code fan", tag="K3", color=PURPLE,
         dots=[BASE_Q, DOM_C, DIR_RISK, POOL_OWN, J_SELF, J_BASE, J_RAND],
         result="Self-report of insecure code fans out across "
                "seeds under self-judging."),
    dict(name="Mixed-pool reopen", tag="injection", color=PURPLE,
         dots=[BASE_Q, DOM_C, DIR_RISK, POOL_MIX, J_MINI],
         result="One injected round collapses the 0.625 stall to "
                "0.000 (2 seeds), at the supplier's floor."),
    dict(name="Transmission with support", tag="positive control", color=PURPLE,
         dots=[BASE_Q, DOM_C, DIR_RISK, POOL_MIX, J_BASE],
         result="The base judge's weak taste integrates — in the "
                "one seed where target material lasted."),
    dict(name="Self-judge duels", tag="head2head", color=PURPLE,
         dots=[BASE_Q, DOM_C, DIR_RISK, POOL_DUEL, J_SELF, J_BASE],
         result="Judging its own base-mixed duels, it erases its "
                "value 0.67→0.00 (2 seeds); gaps negative."),

    dict(name="Conservative inversion", tag="K2", color=GREEN,
         dots=[BASE_O, DOM_G, DIR_CAUT, POOL_OWN, J_SELF, J_BASE, J_CAUT, J_RAND],
         result="Frozen base → runaways; self erodes to the floor; "
                "cautious presses down; random decays."),
    dict(name="Force ladder", tag="scoring judge", color=GREEN,
         dots=[BASE_O, DOM_G, DIR_CAUT, POOL_OWN, J_MINR],
         result="Only a scoring judge pulls a stuck value down — "
                "a step across strengths, not a slope."),
    dict(name="Mixed-generator pools", tag="branch m", color=GREEN,
         dots=[BASE_O, DOM_G, DIR_CAUT, POOL_REF, POOL_MIX,
               J_SELF, J_BASE, J_CAUT, J_MINR],
         result="Reference scoring: the cautious judge wastes the "
                "rescue; contamination near-total in one round."),
    dict(name="Head-to-head duels", tag="branch h", color=GREEN,
         dots=[BASE_O, DOM_G, DIR_CAUT, POOL_MIX, POOL_DUEL, J_SELF, J_BASE, J_CAUT],
         result="Same pools under duels: the cautious judge now "
                "rescues; contamination still survives."),
    dict(name="Risk-erosion duels", tag="branch h2", color=GREEN,
         dots=[BASE_O, DOM_G, DIR_CAUT, POOL_DUEL, J_SELF, J_BASE],
         result="Frozen-base curator pulls risk up (+0.22); "
                "self-judge strong 1/2 seeds, flat 1/2."),
    dict(name="Cross-family oracle", tag="branch e", color=GREEN,
         dots=[BASE_O, DOM_G, DIR_RISK, POOL_OWN, J_MINR],
         result="Score oracle reverses a 0.875 rail to 0.094; a "
                "1.000 rail is selection-inert (zero material)."),

    dict(name="Insecure-code build", tag="attempted", color=ATT, att=True,
         dots=[BASE_O, DOM_C, DIR_RISK, POOL_OWN],
         result="No gate-clearing organism: behaviour installs but "
                "self-report stays flat (Δ ≪ 0.15)."),
]

# ---------------------------------------------------------------- geometry
W = 1720
MARGIN = 36
NAME_W = 288
RES_W = 340
GX0 = MARGIN + NAME_W
GX1 = W - MARGIN - RES_W
GRID_W = GX1 - GX0

GG = 20                                   # gap between axis groups
n_sub = sum(GSIZE)
usable = GRID_W - GG * (len(GROUPS) - 1)
SUBW = usable / n_sub

# flat geometry: per-group left edge + span, per-sub centre
grp_left, grp_span, sub_cx = [], [], []
x = GX0
for gi, sz in enumerate(GSIZE):
    grp_left.append(x)
    grp_span.append(sz * SUBW)
    for k in range(sz):
        sub_cx.append(x + (k + 0.5) * SUBW)
    x += sz * SUBW + GG


def cx_of(g, i):
    return sub_cx[sum(GSIZE[:g]) + i]


GRP_LABEL_Y = 168
OPT_TOP = 178
OPT_H = 60
ROWS_TOP = OPT_TOP + OPT_H
ROW_H = 56

# ---------------------------------------------------------------- build
b = []

# ---- title + subtitle ----
b.append(ctext(W // 2, 50, "The experiment space: five knobs, and where each run sits",
               32, INK, "bold"))
for i, ln in enumerate([
        "Every self-training run is one choice on each of five knobs. A coloured dot marks the "
        "level each experiment used; dot colour is the model organism.",
        "The header lists every option - so a column with few dots is a corner of the space we have not run."]):
    b.append(ctext(W // 2, 78 + i * 24, ln, BODY, GRAY))

# ---- organism key ----
KEY = [(BLUE, "Qwen · gambling (risk-seeking)", False),
       (PURPLE, "Qwen · insecure-code", False),
       (GREEN, "OLMo · gambling (conservative)", False),
       (ATT, "OLMo · insecure-code — attempted, no organism", True)]
key_y = 138
widths = [30 + len(t) * 9.9 + 34 for _, t, _ in KEY]
kx = W // 2 - sum(widths) / 2
for (col, t, hollow), wd in zip(KEY, widths):
    if hollow:
        b.append(f'<circle cx="{kx + 11:.1f}" cy="{key_y - 5:.1f}" r="9" fill="white" '
                 f'stroke="{col}" stroke-width="2.2" stroke-dasharray="3 3"/>')
    else:
        b.append(f'<circle cx="{kx + 11:.1f}" cy="{key_y - 5:.1f}" r="9" fill="{col}"/>')
    b.append(ltext(kx + 28, key_y, t, BODY, INK))
    kx += wd

# ---- group tint bands (behind the two "lever" groups, full height) ----
grid_bottom = ROWS_TOP + len(ROWS) * ROW_H
for gi, (_, tint, _) in enumerate(GROUPS):
    if tint:
        b.append(rect(grp_left[gi] - GG / 2 + 2, OPT_TOP - 4,
                      grp_span[gi] + GG - 4, (grid_bottom - OPT_TOP) + 8,
                      GROUP_TINT, rx=8))

# ---- group axis labels + option header cells ----
for gi, (glabel, _, opts) in enumerate(GROUPS):
    gcx = grp_left[gi] + grp_span[gi] / 2
    b.append(ctext(gcx, GRP_LABEL_Y, glabel, 17, INK, "bold"))
    b.append(rect(grp_left[gi], OPT_TOP, grp_span[gi], OPT_H, HDR_BG,
                  stroke=BORDER, sw=1.4, rx=8))
    for k, lines in enumerate(opts):
        ocx = grp_left[gi] + (k + 0.5) * SUBW
        if k > 0:  # thin divider between options in a group
            dx = grp_left[gi] + k * SUBW
            b.append(f'<line x1="{dx:.1f}" y1="{OPT_TOP + 8:.1f}" x2="{dx:.1f}" '
                     f'y2="{OPT_TOP + OPT_H - 8:.1f}" stroke="{BORDER}" stroke-width="1"/>')
        n = len(lines)
        y0 = OPT_TOP + OPT_H / 2 - (n - 1) * 9 + 5
        for j, ln in enumerate(lines):
            b.append(ctext(ocx, y0 + j * 18, ln, 14, INK, "bold"))

# ---- left/right header labels ----
b.append(ctext(MARGIN + NAME_W / 2, GRP_LABEL_Y, "experiment", 17, INK, "bold"))
b.append(ctext(GX1 + GG / 2 + RES_W / 2, GRP_LABEL_Y, "what moved", 17, INK, "bold"))

# ---- rows ----
# organism-group separators (thicker rule where the colour changes)
prev_color = None
for ri, row in enumerate(ROWS):
    ry = ROWS_TOP + ri * ROW_H
    rcy = ry + ROW_H / 2
    # zebra
    if ri % 2 == 1:
        b.append(rect(MARGIN, ry, W - 2 * MARGIN, ROW_H, "#fbfcfd"))
    # organism separator
    if prev_color is not None and row["color"] != prev_color:
        b.append(f'<line x1="{MARGIN:.1f}" y1="{ry:.1f}" x2="{W - MARGIN:.1f}" '
                 f'y2="{ry:.1f}" stroke="{BORDER}" stroke-width="1.6"/>')
    else:
        b.append(f'<line x1="{GX0 - 12:.1f}" y1="{ry:.1f}" x2="{GX1 + 8:.1f}" '
                 f'y2="{ry:.1f}" stroke="{GRIDLINE}" stroke-width="1"/>')
    prev_color = row["color"]

    att = row.get("att")
    col = row["color"]
    # left colour rail + name
    b.append(rect(MARGIN, ry + 6, 5, ROW_H - 12, col, rx=2))
    nm_col = GRAY if att else INK
    b.append(ltext(MARGIN + 16, rcy - 3, row["name"], 20, nm_col, "bold"))
    b.append(ltext(MARGIN + 16, rcy + 16, row["tag"], 14, GRAY, "italic"))

    # dots
    dotset = set(row["dots"])
    for (g, i) in row["dots"]:
        dx = cx_of(g, i)
        if att:
            b.append(f'<circle cx="{dx:.1f}" cy="{rcy:.1f}" r="11" fill="white" '
                     f'stroke="{ATT}" stroke-width="2.2" stroke-dasharray="3 3"/>')
        else:
            b.append(f'<circle cx="{dx:.1f}" cy="{rcy:.1f}" r="11.5" fill="{col}"/>')
    # judge group: for the attempted row, show it was never reached
    if att:
        jcx = grp_left[4] + grp_span[4] / 2
        b.append(ctext(jcx, rcy + 5, "loop never ran", 15, ATT, "italic"))

    # result text (right)
    res_x = GX1 + GG / 2 + 8
    rlines = wrap(row["result"], 42)[:3]
    ry0 = rcy - (len(rlines) - 1) * 8.5 - 1
    for j, ln in enumerate(rlines):
        b.append(ltext(res_x, ry0 + j * 17, ln, 14, GRAY if att else "#33404d"))

# bottom rule
b.append(f'<line x1="{MARGIN:.1f}" y1="{grid_bottom:.1f}" x2="{W - MARGIN:.1f}" '
         f'y2="{grid_bottom:.1f}" stroke="{BORDER}" stroke-width="1.6"/>')

# ---- caption ----
cap_y = grid_bottom + 32
para = (
    "Read a row left to right: its dots give that experiment's setting on all five knobs.  "
    "Pool levels: “own” = the organism generates all six candidates itself; “fixed ref” = each "
    "candidate is scored against one fixed answer; “mixed” = a second source contributes candidates; "
    "“duels” = candidates from two sources compared head-to-head, keeping the top two by win rate.  "
    "The “min-risk” / “min-insec” judges are the score-based “oracle” selector, not a model.  "
    "Head-to-head pools also varied composition (bad-organism vs base; bad- vs good-organism; two "
    "good-organism + two base).  Branch m and branch h are the SAME mixed pools under fixed-reference "
    "scoring vs duels, so the comparison format alone changes the outcome.  "
    "K1/K2/K3 are the anchor grids; branches e/m/h/h2 are the OLMo release-program interventions.  "
    "The OLMo insecure-code corner has no loop: the organism never cleared the self-report gate "
    "(behaviour installed, self-report stayed flat)."
)
cap_lines = wrap(para, 168)
for i, ln in enumerate(cap_lines):
    b.append(ltext(MARGIN, cap_y + i * 23, ln, 15, GRAY))

H = cap_y + len(cap_lines) * 23 + 8
svg = svg_doc(W, H, "\n".join(b))
with open(os.path.join(FIGDIR, "synthesis_experiment_design_space.svg"), "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote synthesis_experiment_design_space.svg  ({W}x{int(H)})")

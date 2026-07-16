#!/usr/bin/env python3
"""run-inventory — a compact visual replacement for the writeup's "What I ran" table.

One row per experiment family. Each row is a run-count bar (length proportional
to the number of runs, the number at the end) plus small chips for the loop's
swap-in slots, colored to match the experiment-kit slots:

    base model  = BLUE   (slot 1)      answer source       = GREEN (slot 4)
    installed value = RED (slot 2)     alternative source  = AMBER (slot 5)
    the judge   = PURPLE (slot 3)

Repeated chips across rows make the shared structure visible. Text is orientation
only; the mapping to the kit slots lives in caption.md.

Source: docs/writeup_value_dynamics_sprint.md "What I ran" (the committed
inventory). Run counts cross-checked against experiments/spread_util_unified.json
(74 distinct runs; organism/axis aggregates match — see caption.md).

Regenerate with:  python3 run-inventory.py   (stdlib only)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- palette: exactly the kit + make_figures constants -----------------------
INK = "#1a1a1a"
BLUE = "#2867b5"    # base model            (slot 1)
RED = "#b5342c"     # installed value       (slot 2)
PURPLE = "#8a5a9e"  # the judge             (slot 3)
GREEN = "#3a7d44"   # answer source         (slot 4)
AMBER = "#b5842c"   # alternative source    (slot 5)
GRAY = "#6b7684"    # recessive only
BARFILL = "#d7dde3"
TINT = {
    BLUE: "#eef3fb",
    RED: "#fbeeec",
    PURPLE: "#f4eef7",
    GREEN: "#eef5ee",
    AMBER: "#f8f2e3",
}
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


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def ltext(x, y, text, size, color=INK, weight="normal", anchor="start"):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x}" y="{y}"{a} font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}">{esc(text)}</text>')


CH = 25          # chip height
CFONT = 13.0     # chip font
CPAD = 10        # chip horizontal padding
CGAP = 7         # gap between chips


def chip_w(text):
    return CPAD * 2 + len(text) * CFONT * 0.56


def chip(x, y, text, color):
    """One chip: tinted rounded rect, colored border + dot, ink text. Top-left (x,y)."""
    w = chip_w(text)
    s = [f'<rect x="{x}" y="{y}" width="{w:.1f}" height="{CH}" rx="6" '
         f'fill="{TINT[color]}" stroke="{color}" stroke-width="1.6"/>',
         f'<circle cx="{x+CPAD}" cy="{y+CH/2}" r="3.2" fill="{color}"/>',
         ltext(x + CPAD + 8, y + CH / 2 + 4.5, text, CFONT, INK)]
    # widen so the dot has room
    w2 = w + 11
    s[0] = (f'<rect x="{x}" y="{y}" width="{w2:.1f}" height="{CH}" rx="6" '
            f'fill="{TINT[color]}" stroke="{color}" stroke-width="1.6"/>')
    return "\n".join(s), w2


def cell_chips(x, y, maxw, items):
    """Lay chips left-to-right, wrapping within maxw. items: list of (text,color)."""
    s, cx, cy, line_n = [], x, y, 1
    for text, color in items:
        _, w = chip(x, y, text, color)
        if cx + w > x + maxw and cx > x:
            cx = x
            cy += CH + 6
            line_n += 1
        csvg, w = chip(cx, cy, text, color)
        s.append(csvg)
        cx += w + CGAP
    height = line_n * CH + (line_n - 1) * 6
    return "\n".join(s), height


# ---- the five families (verbatim from the "What I ran" table) ----------------
# organism: (model, value); judges: PURPLE; alt sources: AMBER; answer sources: GREEN
FAMILIES = [
    {
        "name": "Qwen risk grid",
        "org": ("Qwen3-4B", "risky gambles"),
        "judges": ["itself", "a frozen copy", "the base model", "random keeping"],
        "alt": ["reference scoring"],
        "ans": ["own answers"],
        "runs": 16,
    },
    {
        "name": "OLMo risk grid + judge schedules",
        "org": ("OLMo-3-7B", "risky gambles"),
        "judges": ["the base model", "a cautious-tuned copy", "scheduled swaps mid-run"],
        "alt": ["reference scoring"],
        "ans": ["own answers"],
        "runs": 21,
    },
    {
        "name": "OLMo mixed-pool interventions",
        "org": ("OLMo-3-7B", "risky gambles"),
        "judges": ["the base model", "itself", "the cautious-tuned copy"],
        "alt": ["reference scoring", "head-to-head duels"],
        "ans": ["base-mixed", "risk-railed-peer-mixed"],
        "runs": 18,
    },
    {
        "name": "oracle & injection",
        "org": ("both models", "both values"),
        "judges": ["score oracle (keeps 2 lowest)"],
        "alt": ["score rank"],
        "ans": ["own answers", "base-mixed", "base-injection pair"],
        "runs": 11,
    },
    {
        "name": "Qwen insecure-code loops",
        "org": ("Qwen3-4B", "insecure-code self-description"),
        "judges": ["itself (candid-prompt variants)", "the base model"],
        "alt": ["head-to-head duels", "reference scoring"],
        "ans": ["own answers", "base-mixed"],
        "runs": 8,
    },
]
TOTAL_RUNS = 74
TOTAL_ROUNDS = 340
MAXRUNS = max(f["runs"] for f in FAMILIES)

# ---- layout ------------------------------------------------------------------
W = 1360
M = 40
# column x-starts and widths (bar zone reserved on the right)
COL = {
    "fam":  (M,    170),
    "org":  (218,  222),
    "judge": (452, 278),
    "alt":  (742,  160),
    "ans":  (910,  205),
}
BAR_X = 1130
BAR_MAX = W - M - 42 - BAR_X   # leave room for the number after the bar

b = []

# ---- title -------------------------------------------------------------------
b.append(ctext(W / 2, 52, "The 74 runs, by experiment family", 30, INK, "bold"))
b.append(ctext(W / 2, 84,
               "Each run is one setting of the self-training loop, with one column changed at a time. "
               "Chip colors match the experiment-kit slots.", 17, GRAY))

# ---- column header row with slot swatches ------------------------------------
hy = 128
def hdr(colkey, label, color, sub):
    x, w = COL[colkey]
    parts = [f'<rect x="{x}" y="{hy-15}" width="15" height="15" rx="3" fill="{TINT[color]}" '
             f'stroke="{color}" stroke-width="1.6"/>',
             ltext(x + 22, hy - 2, label, 15, INK, "bold"),
             ltext(x, hy + 17, sub, 12.5, GRAY)]
    return "\n".join(parts)

b.append(ltext(COL["fam"][0], hy - 2, "experiment family", 15, INK, "bold"))
b.append(ltext(COL["fam"][0], hy + 17, "organism · value at left", 12.5, GRAY))
b.append(hdr("org", "organism", RED, "base model + installed value"))
b.append(hdr("judge", "the judge", PURPLE, "who keeps answers"))
b.append(hdr("alt", "alternative", AMBER, "compared against"))
b.append(hdr("ans", "answer source", GREEN, "where answers come from"))
b.append(ltext(BAR_X, hy - 2, "runs", 15, INK, "bold"))

hline = hy + 30
b.append(f'<line x1="{M}" y1="{hline}" x2="{W-M}" y2="{hline}" stroke="{GRAY}" '
         f'stroke-width="1.4" stroke-opacity="0.5"/>')

# ---- rows --------------------------------------------------------------------
row_y = hline + 22
for i, f in enumerate(FAMILIES):
    # build each cell, measure heights
    ox, ow = COL["org"]
    jx, jw = COL["judge"]
    ax, aw = COL["alt"]
    nx, nw = COL["ans"]

    org_items = [(f["org"][0], BLUE), (f["org"][1], RED)]
    org_svg, oh = cell_chips(ox, row_y, ow, org_items)
    j_svg, jh = cell_chips(jx, row_y, jw, [(t, PURPLE) for t in f["judges"]])
    a_svg, ah = cell_chips(ax, row_y, aw, [(t, AMBER) for t in f["alt"]])
    n_svg, nh = cell_chips(nx, row_y, nw, [(t, GREEN) for t in f["ans"]])
    row_h = max(oh, jh, ah, nh, CH)

    # family name (left, wrapped, vertically centered)
    fx, fw = COL["fam"]
    flines = wrap(f["name"], 22)
    fy0 = row_y + row_h / 2 - (len(flines) - 1) * 9 + 5
    for k, ln in enumerate(flines):
        b.append(ltext(fx, fy0 + k * 18, ln, 15.5, INK, "bold"))

    b.append(org_svg)
    b.append(j_svg)
    b.append(a_svg)
    b.append(n_svg)

    # run bar (centered vertically in the row), number at the end
    by = row_y + row_h / 2 - 9
    blen = BAR_MAX * f["runs"] / MAXRUNS
    b.append(f'<rect x="{BAR_X}" y="{by}" width="{BAR_MAX}" height="18" rx="4" '
             f'fill="{BARFILL}" opacity="0.5"/>')
    b.append(f'<rect x="{BAR_X}" y="{by}" width="{blen:.1f}" height="18" rx="4" fill="{INK}"/>')
    b.append(ltext(BAR_X + blen + 8, by + 14, str(f["runs"]), 17, INK, "bold"))

    # thin separator
    sep = row_y + row_h + 15
    if i < len(FAMILIES) - 1:
        b.append(f'<line x1="{M}" y1="{sep}" x2="{W-M}" y2="{sep}" stroke="{GRAY}" '
                 f'stroke-width="1" stroke-opacity="0.28"/>')
    row_y = sep + 22

# ---- footer ------------------------------------------------------------------
fy = row_y + 2
b.append(f'<line x1="{M}" y1="{fy-22}" x2="{W-M}" y2="{fy-22}" stroke="{GRAY}" '
         f'stroke-width="1.4" stroke-opacity="0.5"/>')
b.append(ltext(M, fy + 4,
               f"{TOTAL_RUNS} runs  ·  {TOTAL_ROUNDS} selection rounds  ·  "
               f"5 families  ·  2 model families  ·  2 value coordinates  ·  "
               f"one column changed at a time",
               15, GRAY))
b.append(ltext(W - M, fy + 4,
               "two forward-test experiments sit outside this corpus",
               13, GRAY, anchor="end"))

H = fy + 24

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" '
       f'font-family="{FONT}">\n<rect width="{W}" height="{H:.0f}" fill="white"/>\n'
       + "\n".join(b) + "\n</svg>")

with open(os.path.join(HERE, "run-inventory.svg"), "w") as fh:
    fh.write(svg)
print("wrote run-inventory.svg", W, "x", round(H))

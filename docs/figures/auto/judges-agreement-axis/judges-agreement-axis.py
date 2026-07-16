#!/usr/bin/env python3
"""Visual glossary: every judge x judging-format x pool setup placed as a dot on
the agreement axis (rho between the judge's kept side and the value).

Owain-Evans-lab house style (white ground, headline sentence, boxes of verbatim
setup text, fat direct labels). Palette constants copied from
docs/figures/src/make_figures.py. Stdlib only; runnable as:
    python3 judges-agreement-axis.py
from its own directory. It re-reads the source JSON if reachable (4 levels up)
and asserts every plotted rho against the file; otherwise it falls back to the
embedded constants and prints a warning.

Source data: experiments/spread_util_unified.json  (utilization.table + the
utilization.between_cell_variance_share_rho field).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                   "spread_util_unified.json")

# ---- palette (verbatim from make_figures.py) ----------------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series (the organism judging itself)
GREEN = "#3a7d44"      # frozen / external-copy judge series
RED = "#b5342c"        # reversal / warning emphasis
GRAY = "#6b7684"       # recessive only (axes, random null)
KEY_FILL = "#eef5ee"
DOC_FILL = "#fdf6e8"
ASST_FILL = "#eaf1f8"
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


# ---- the plotted cells (embedded; verified against the JSON below) -------
# key = (organism, axis, judge, format, composition)  ->  rho plotted
CELLS = {
    "oracle":       (("OLMo", "risk", "score oracle", "score", "base-mixed"), -1.000),
    "qwen_base":    (("Qwen", "risk", "base", "reference", "self-only"),      -0.032),
    "qwen_frozen":  (("Qwen", "risk", "frozen copy", "reference", "self-only"), 0.041),
    "qwen_self":    (("Qwen", "risk", "self", "reference", "self-only"),       0.113),
    "cautious_duel":(("OLMo", "risk", "cautious copy", "duel", "base-mixed"),  0.100),
    "cautious_ref": (("OLMo", "risk", "cautious copy", "reference", "base-mixed"), 0.383),
    "self_erode":   (("Qwen", "selfreport", "self", "duel", "base-mixed"),    -0.236),
    "self_peer":    (("OLMo", "risk", "self", "duel", "peer-mixed"),           0.524),
}
RANDOM_RHO = 0.0        # random cell has rho = null (kept side uncorrelated); plotted at 0
VAR_SHARE_RHO = 0.817   # utilization.between_cell_variance_share_rho


def verify():
    """Assert every plotted rho matches experiments/spread_util_unified.json."""
    if not os.path.exists(SRC):
        print("WARNING: source JSON not found at", SRC,
              "\n         plotting embedded constants unverified.")
        return
    d = json.load(open(SRC))
    rows = d["utilization"]["table"]

    def find(key):
        o, ax, j, f, c = key
        for r in rows:
            if (r["organism"], r["axis"], r["judge"], r["format"],
                    r["composition"]) == (o, ax, j, f, c):
                return r
        raise AssertionError(f"cell not found in JSON: {key}")

    for name, (key, rho) in CELLS.items():
        r = find(key)
        got = r["rho_mean"]
        assert got is not None and abs(got - rho) < 1e-6, \
            f"{name}: plotted {rho} but JSON has {got}"
    # random cell: rho is null in the file
    rnd = find(("Qwen", "risk", "random", "random", "self-only"))
    assert rnd["rho_mean"] is None, "random rho_mean expected null"
    share = d["utilization"]["between_cell_variance_share_rho"]
    assert abs(share - VAR_SHARE_RHO) < 1e-6, f"var share {share} != {VAR_SHARE_RHO}"
    print("verify: all plotted rho match spread_util_unified.json; "
          f"between-cell variance share of rho = {share:.3f}")


# ---- geometry -----------------------------------------------------------
W, H = 1200, 740
AX_Y = 340
X0, X1 = 150, 1055           # x for rho = -1 .. +1
CX = (X0 + X1) / 2           # rho = 0


def xr(rho):
    return X0 + (rho + 1.0) * (X1 - X0) / 2.0


# ---- svg helpers --------------------------------------------------------
def dot(x, y, color, r=9, ring="white"):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" '
            f'stroke="{ring}" stroke-width="2.5"/>')


def leader(x1, y1, x2, y2, color=GRAY):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="1.6"/>')


def box(x, y, w, h, fill, stroke=INK, sw=2.2, rx=9):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def txt(x, y, s, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
            f'font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{esc(s)}</text>')


def label_box(x, y, w, heading, hcolor, body, rho_str, chip_color):
    """A titled example box: bold colored heading, wrapped plain body, and a
    rho chip pinned to the bottom-right so it never collides with the heading."""
    parts = []
    lines = wrap(body, int(w / 8.4))
    h = 34 + len(lines) * 20 + 34
    parts.append(box(x, y, w, h, "white"))
    parts.append(txt(x + 13, y + 26, heading, 18, hcolor, "bold"))
    yy = y + 26 + 22
    for ln in lines:
        parts.append(txt(x + 13, yy, ln, 15.5, INK))
        yy += 20
    # rho chip, bottom-right
    cw = 16 + len(rho_str) * 9.2
    cy = y + h - 30
    parts.append(f'<rect x="{x + w - cw - 12}" y="{cy}" width="{cw}" '
                 f'height="24" rx="12" fill="{chip_color}"/>')
    parts.append(txt(x + w - cw / 2 - 12, cy + 17, rho_str, 14.5, "white",
                     "bold", "middle"))
    return "\n".join(parts), h


# ---- format strip icons -------------------------------------------------
def fmt_reference(x, y):
    c = INK
    return "\n".join([
        box(x, y, 30, 38, "white", c, 2, rx=4),
        f'<line x1="{x+6}" y1="{y+10}" x2="{x+24}" y2="{y+10}" stroke="{GRAY}" stroke-width="2"/>',
        f'<line x1="{x+6}" y1="{y+18}" x2="{x+24}" y2="{y+18}" stroke="{GRAY}" stroke-width="2"/>',
        f'<line x1="{x+6}" y1="{y+26}" x2="{x+20}" y2="{y+26}" stroke="{GRAY}" stroke-width="2"/>',
        f'<circle cx="{x+50}" cy="{y+19}" r="12" fill="none" stroke="{c}" stroke-width="2.4"/>',
        f'<path d="M {x+44} {y+19} L {x+49} {y+24} L {x+57} {y+13}" fill="none" stroke="{GREEN}" stroke-width="2.6"/>',
    ])


def fmt_duel(x, y):
    c = INK
    return "\n".join([
        box(x, y, 26, 34, ASST_FILL, c, 2, rx=4),
        box(x + 40, y, 26, 34, ASST_FILL, c, 2, rx=4),
        txt(x + 30, y + 24, "vs", 15, INK, "bold"),
    ])


def fmt_score(x, y):
    c = RED
    # a mini rating meter (0..1 track with a filled portion) reads as "scoring"
    return "\n".join([
        box(x, y, 34, 38, "white", c, 2, rx=4),
        f'<line x1="{x+6}" y1="{y+19}" x2="{x+28}" y2="{y+19}" stroke="{GRAY}" stroke-width="2"/>',
        f'<line x1="{x+6}" y1="{y+19}" x2="{x+22}" y2="{y+19}" stroke="{c}" stroke-width="4"/>',
        f'<circle cx="{x+22}" cy="{y+19}" r="4" fill="{c}"/>',
        txt(x + 6, y + 32, "0", 9, GRAY, "normal", "start"),
        txt(x + 28, y + 32, "1", 9, GRAY, "normal", "end"),
    ])


# ---- build --------------------------------------------------------------
def build():
    b = [f'<rect width="{W}" height="{H}" fill="white"/>']

    # title + subtitle
    b.append(txt(40, 46, "The judges, placed by what they actually do: "
                 "agreement with the value", 27, INK, "bold"))
    b.append(txt(40, 74, "each dot = one judge × judging-format × pool "
                 "setup, measured from its logged candidate scores", 17, GRAY))

    # ---- the axis ----
    b.append(f'<line x1="{X0}" y1="{AX_Y}" x2="{X1}" y2="{AX_Y}" '
             f'stroke="{INK}" stroke-width="3" marker-start="url(#arr)" '
             f'marker-end="url(#arr)"/>')
    # ticks
    for rho in (-1, -0.5, 0, 0.5, 1):
        x = xr(rho)
        b.append(f'<line x1="{x:.1f}" y1="{AX_Y-7}" x2="{x:.1f}" y2="{AX_Y+7}" '
                 f'stroke="{INK}" stroke-width="2"/>')
    # zero emphasis
    b.append(f'<line x1="{CX:.1f}" y1="{AX_Y-16}" x2="{CX:.1f}" y2="{AX_Y+16}" '
             f'stroke="{GRAY}" stroke-width="1.4" stroke-dasharray="4 4"/>')
    # axis name (top-right of axis)
    b.append(txt(X1, AX_Y - 26, "agreement  ρ", 19, INK, "bold", "end"))
    b.append(txt(X1, AX_Y - 9,
                 "(kept-vs-value rank correlation)", 13.5, GRAY, "normal", "end"))
    # end + zero descriptors
    b.append(txt(X0, AX_Y + 30, "−1.0", 17, RED, "bold", "middle"))
    b.append(txt(X0, AX_Y + 50, "always keeps the", 13.5, GRAY, "normal", "middle"))
    b.append(txt(X0, AX_Y + 66, "LOWER-value side", 13.5, RED, "bold", "middle"))
    b.append(txt(X1, AX_Y + 30, "+1.0", 17, GREEN, "bold", "middle"))
    b.append(txt(X1, AX_Y + 50, "always keeps the", 13.5, GRAY, "normal", "middle"))
    b.append(txt(X1, AX_Y + 66, "HIGHER-value side", 13.5, GREEN, "bold", "middle"))
    b.append(txt(CX, AX_Y + 84, "0 — keeps at random w.r.t. the value",
                 13.5, GRAY, "normal", "middle"))

    # ---- the Qwen prompted-judge cluster: an upper bracket ticking down to
    #      ONLY its three dots, so the neighbouring cautious-duel dot (same rho
    #      region, different judge) is not visually swallowed into the group. ---
    xb0, xb1 = xr(-0.032), xr(0.113)
    yb = AX_Y - 16
    b.append(f'<line x1="{xb0:.1f}" y1="{yb}" x2="{xb1:.1f}" y2="{yb}" '
             f'stroke="{GREEN}" stroke-width="2"/>')
    for cx in (xr(-0.032), xr(0.041), xr(0.113)):
        b.append(f'<line x1="{cx:.1f}" y1="{yb}" x2="{cx:.1f}" y2="{AX_Y-10}" '
                 f'stroke="{GREEN}" stroke-width="2"/>')

    # ---- dots ----
    dots = [
        ("oracle",       xr(-1.000), RED),
        ("self_erode",   xr(-0.236), BLUE),
        ("qwen_base",    xr(-0.032), GREEN),
        ("qwen_frozen",  xr(0.041),  GREEN),
        ("qwen_self",    xr(0.113),  BLUE),
        ("cautious_ref", xr(0.383),  GREEN),
        ("self_peer",    xr(0.524),  BLUE),
    ]
    # random (null) drawn as hollow gray marker
    b.append(f'<circle cx="{CX:.1f}" cy="{AX_Y}" r="8" fill="white" '
             f'stroke="{GRAY}" stroke-width="2.5"/>')
    # cautious duel drawn as ringed marker (left node of the paired judge)
    b.append(dot(xr(0.100), AX_Y, GREEN, r=9))
    for name, x, color in dots:
        b.append(dot(x, AX_Y, color))

    # ================= UPPER label boxes ==========================
    # A. score oracle
    body, h = label_box(
        30, 110, 250,
        "Score oracle", RED,
        "Keeps the two lowest-scoring answers by decision rule. No prompted "
        "judge to fool.", "ρ = −1.0", RED)
    b.append(body)
    b.append(leader(xr(-1.0), AX_Y - 12, 155, 110 + h))

    # B. self-erosion (Qwen self, duels, base text present)
    body, h = label_box(
        300, 110, 262,
        "Organism judges its own duels", BLUE,
        "Insecure-code organism (Qwen) picking winners of its own head-to-head "
        "duels, with base-model text mixed into the pool. Judgment runs against "
        "its installed value.", "ρ = −0.24", RED)
    b.append(body)
    b.append(leader(xr(-0.236), AX_Y - 12, 431, 110 + h))

    # C. Qwen prompted-judge cluster
    body, h = label_box(
        600, 92, 300,
        "Qwen risk-grid prompted judges", GREEN,
        "Itself, a frozen copy, and a base model — each scoring every answer "
        "against a fixed reference (self-only pools). The fan without selection: "
        "drift here is training noise, not a force.",
        "ρ = −0.03 to +0.11", GRAY)
    b.append(body)
    b.append(leader((xb0 + xb1) / 2, yb, 700, 92 + h))

    # D. self-judge on peer-invaded pools
    body, h = label_box(
        920, 110, 258,
        "Self-judge, peer pool", BLUE,
        "The organism judges its own duels, but half the answers come from an "
        "outside peer. Contamination survives the duel format — it keeps the "
        "railed peer's safer text.", "ρ = +0.52", GREEN)
    b.append(body)
    b.append(leader(xr(0.524), AX_Y - 12, 970, 110 + h))

    # ================= LOWER label boxes ==========================
    # E. random
    body, h = label_box(
        250, 434, 262,
        "Random keeping", GRAY,
        "Ignores the value entirely. Agreement is undefined; the kept side is "
        "uncorrelated with the value. Validates the null-centring.",
        "ρ ≈ 0", GRAY)
    b.append(body)
    b.append(leader(CX, AX_Y + 12, 381, 434))

    # F. cautious-copy pair — same judge, two formats (bracket)
    xd, xrf = xr(0.100), xr(0.383)
    ybk = AX_Y + 18
    b.append(f'<path d="M {xd:.1f} {AX_Y+12} L {xd:.1f} {ybk} L {xrf:.1f} {ybk} '
             f'L {xrf:.1f} {AX_Y+12}" fill="none" stroke="{GREEN}" '
             f'stroke-width="2"/>')
    b.append(txt((xd + xrf) / 2, ybk + 16, "same judge, different format",
                 13.5, GREEN, "bold", "middle"))
    body, h = label_box(
        560, 434, 400,
        "Cautious-tuned copy of the organism", GREEN,
        "Scoring the organism's own answers (base-mixed). As duels ρ = +0.10 — "
        "duels break the reference artifact; vs a fixed reference ρ = +0.38, "
        "keeping the organism's HIGH-risk text (a failed rescue).",
        "duel +0.10 / ref +0.38", GREEN)
    b.append(body)
    b.append(leader((xd + xrf) / 2, ybk + 20, 700, 434))

    # ================= FORMAT + POOL strip ========================
    sy = 636
    b.append(f'<line x1="40" y1="{sy-14}" x2="{W-40}" y2="{sy-14}" '
             f'stroke="{GRAY}" stroke-width="1" stroke-dasharray="3 4"/>')
    b.append(txt(40, sy + 6, "Three ways a judge is asked:", 15, INK, "bold"))
    b.append(fmt_reference(300, sy - 12))
    b.append(txt(372, sy + 5, "vs a fixed reference answer", 15, INK))
    b.append(fmt_duel(620, sy - 11))
    b.append(txt(700, sy + 5, "head-to-head duels", 15, INK))
    b.append(fmt_score(900, sy - 12))
    b.append(txt(972, sy + 5, "score-ranked keeping — no judge (the oracle)", 15, INK))
    b.append(txt(40, sy + 42,
                 "Pools:", 15, INK, "bold"))
    b.append(txt(96, sy + 42,
                 "the organism's own answers, or half from an outside supplier "
                 "(a base model / a peer).", 15, INK))

    # ================= evidence line ==============================
    ey = sy + 74
    b.append(f'<rect x="40" y="{ey-22}" width="{W-80}" height="34" rx="8" '
             f'fill="{DOC_FILL}" stroke="{INK}" stroke-width="2"/>')
    b.append(txt(56, ey, "82% ", 18, RED, "bold"))
    b.append(txt(96, ey,
                 "of the variance in agreement is between judge × format "
                 "× pool setups — which judge, in which format, on which "
                 "pool is the state that sets ρ.", 16, INK))

    defs = (f'<defs><marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" '
            f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}">\n{defs}\n' + "\n".join(b) + "\n</svg>")


if __name__ == "__main__":
    verify()
    svg = build()
    out = os.path.join(HERE, "judges-agreement-axis.svg")
    with open(out, "w") as f:
        f.write(svg)
    print("wrote", out)

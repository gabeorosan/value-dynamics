#!/usr/bin/env python3
"""Forest plot / dot-ladder: every judge x alternative-source x candidate-source
setup is one ROW on a single shared agreement axis (rho).

Owain-Evans-lab house style (white ground, orientation title, fat direct
labels, no leader clutter). Palette constants copied verbatim from
docs/figures/src/make_figures.py. Stdlib only; runnable as:
    python3 judges-agreement-axis.py
from its own directory. It re-reads the two source JSONs if reachable (4 levels
up) and asserts every plotted rho against the files; otherwise it falls back to
the embedded constants and prints a warning.

Design: one row per setup, grouped so the matched contrasts read as pairs
(a light dumbbell line connects the two dots of a pair to show the move). Each
row has a left-aligned name + its "organism . value" condition line, a dot at
its measured rho on the shared axis, and the rho value printed next to the dot.
No callout boxes, no leader lines. All interpretation lives in caption.md.

Source data:
  experiments/spread_util_unified.json  (utilization.table + the
    utilization.between_cell_variance_share_rho field) -- every dot except the
    self-only self-judge dot.
  experiments/qwen_selfonly_model_check.json  (round1_agreement.supplier_removed_mean)
    -- the Qwen self-judge's agreement on its OWN answers only (rho = +0.40),
    paired with the supplier-present self-judge dot (rho = -0.24) already carried
    in spread_util_unified.json.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                   "spread_util_unified.json")
SRC2 = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "qwen_selfonly_model_check.json")

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


# ---- the plotted cells (embedded; verified against the JSONs below) ------
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

# NEW dot (source: qwen_selfonly_model_check.json). The SAME Qwen self-judge in
# the SAME duel format as the self_erode dot, but scored on its own candidates only
# (base-model text removed from the pool). Plotted as +0.40.
SELF_OWNPOOL_RHO = 0.3971   # round1_agreement.supplier_removed_mean


def verify():
    """Assert every plotted rho matches its source JSON."""
    ok = True
    if not os.path.exists(SRC):
        print("WARNING: source JSON not found at", SRC,
              "\n         plotting embedded constants unverified.")
        ok = False
    else:
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
        rnd = find(("Qwen", "risk", "random", "random", "self-only"))
        assert rnd["rho_mean"] is None, "random rho_mean expected null"
        share = d["utilization"]["between_cell_variance_share_rho"]
        assert abs(share - VAR_SHARE_RHO) < 1e-6, \
            f"var share {share} != {VAR_SHARE_RHO}"
        print("verify: all spread_util_unified rho match; between-cell "
              f"variance share of rho = {share:.3f}")

    if not os.path.exists(SRC2):
        print("WARNING: source JSON not found at", SRC2,
              "\n         self-only self-judge dot unverified.")
        ok = False
    else:
        d2 = json.load(open(SRC2))
        got = d2["round1_agreement"]["supplier_removed_mean"]
        assert abs(got - SELF_OWNPOOL_RHO) < 1e-6, \
            f"self-only self-judge: plotted {SELF_OWNPOOL_RHO} but JSON has {got}"
        pres = d2["round1_agreement"]["published_supplier_present"]
        print(f"verify: self-only self-judge rho = {got:.4f} (plotted +0.40); "
              f"the paired supplier-present dot is published at {pres}.")
    return ok


# Fallback if SRC is unreachable (means over rounds; verified 2026-07-16).
QWEN_JUDGE_FALLBACK = {"evolving_self": 0.11321, "frozen_copy_r0": 0.04108,
                       "frozen_base": -0.03158}


def qwen_judge_rhos():
    """Live-compute each Qwen risk-grid judge's rho as the mean of the per-round
    'rho' field over that condition's records (Qwen organism, risk axis):
        evolving_self  -> the organism judging itself
        frozen_copy_r0 -> a frozen copy of the organism
        frozen_base    -> the base model
    Asserts each rounds to a value inside [-0.05, +0.15]; prints all three."""
    if not os.path.exists(SRC):
        print("WARNING: source JSON not found; using embedded Qwen judge rhos.")
        vals = dict(QWEN_JUDGE_FALLBACK)
    else:
        recs = json.load(open(SRC))["records"]
        vals = {}
        for cond in ("evolving_self", "frozen_copy_r0", "frozen_base"):
            rr = [r["rho"] for r in recs if r["organism"] == "Qwen"
                  and r["axis"] == "risk" and r["cond"] == cond
                  and r["rho"] is not None]
            assert rr, f"no records for Qwen risk {cond}"
            vals[cond] = sum(rr) / len(rr)
    for cond, v in vals.items():
        assert -0.05 <= round(v, 2) <= 0.15, \
            f"{cond} rho {v:.4f} rounds outside [-0.05, +0.15]"
    print("Qwen risk-grid judge rho (live mean over rounds): "
          f"itself={vals['evolving_self']:+.4f}, "
          f"frozen copy={vals['frozen_copy_r0']:+.4f}, "
          f"base model={vals['frozen_base']:+.4f}")
    return vals


# ---- geometry -----------------------------------------------------------
W = 1180
PX0, PX1 = 452, 1140          # x for rho = -1 .. +1 (the shared plot area)
LX = 40                        # left label column origin
AX_Y = 172                     # the shared axis line


def xr(rho):
    return PX0 + (rho + 1.0) * (PX1 - PX0) / 2.0


CX = xr(0.0)


# ---- svg helpers --------------------------------------------------------
def dot(x, y, color, r=8.5, ring="white"):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" '
            f'stroke="{ring}" stroke-width="2"/>')


def box(x, y, w, h, fill, stroke=INK, sw=2.2, rx=9):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def txt(x, y, s, size, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" '
            f'font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{esc(s)}</text>')


def rlab_of(rho):
    """Signed 2-decimal label with a real unicode minus (matches house style)."""
    return f"{rho:+.2f}".replace("-", "−")


# ---- the rows (one per setup) -------------------------------------------
# Organism identities read from the data / docs/report_spread_util_unified.md:
#   OLMo | risk        = "K2 OLMo gamble organisms"  -> OLMo risky-gambles, risk value
#   Qwen | risk        = "K1 Qwen risk grid"         -> Qwen risk-grid, risk value
#   Qwen | selfreport  = insecure-code EM organism   -> Qwen insecure-code, self-description value
def build():
    qr = qwen_judge_rhos()
    b = []

    # ---- title + subtitle (orientation only) ----
    b.append(txt(LX, 46, "The judges, placed by their measured agreement "
                 "with the value", 27, INK, "bold"))
    b.append(txt(LX, 74, "each dot = one judge × alternative-source × "
                 "candidate-source setup, measured from its logged candidate scores",
                 16.5, GRAY))
    b.append(txt(LX, 98, "ρ = correlation of judge scores with value scores, "
                 "per prompt, averaged over the round", 16, GRAY))

    # ---- the shared axis, drawn once at the top ----
    b.append(f'<line x1="{PX0}" y1="{AX_Y}" x2="{PX1}" y2="{AX_Y}" '
             f'stroke="{INK}" stroke-width="2.5" marker-start="url(#arr)" '
             f'marker-end="url(#arr)"/>')
    # endpoint meaning, above the axis (red left, green right; they never meet)
    b.append(txt(PX0, AX_Y - 13, "−1  always keeps the lowest-value answers",
                 13, RED, "bold", "start"))
    b.append(txt(PX1, AX_Y - 13, "always keeps the highest-value answers  +1",
                 13, GREEN, "bold", "end"))
    # tick labels below the axis
    for rho, lab in ((-1, "−1.0"), (-0.5, "−0.5"), (0, "0"), (0.5, "+0.5"),
                     (1, "+1.0")):
        x = xr(rho)
        b.append(f'<line x1="{x:.1f}" y1="{AX_Y-6}" x2="{x:.1f}" y2="{AX_Y+6}" '
                 f'stroke="{INK}" stroke-width="2"/>')
        b.append(txt(x, AX_Y + 22, lab, 13, GRAY, "normal", "middle"))
    b.append(txt(CX, AX_Y + 22, "0", 13, INK, "bold", "middle"))

    # ---- lay out the rows (compute y positions first) ----
    # Each entry: ("H", header) or ("R", dict)
    seq = [
        ("H", "bounds & controls"),
        ("R", dict(name="Score oracle",
                   cond="OLMo risky-gambles · risk · no judge · base-mixed",
                   rho=-1.000, rlab="−1.0", color=RED, kind="dot")),
        ("R", dict(name="Random keeping",
                   cond="Qwen risk-grid · risk · own candidates",
                   rho=0.0, rlab="≈ 0", color=GRAY, kind="hollow")),
        ("H", ""),   # wordless separator (pair carried by the dumbbell + row names)
        ("R", dict(name="Cautious copy — static alternative",
                   cond="OLMo risky-gambles · risk · base-mixed candidates",
                   rho=0.383, rlab="+0.38", color=GREEN, kind="dot",
                   pair="cautious")),
        ("R", dict(name="Cautious copy — head-to-head duels",
                   cond="OLMo risky-gambles · risk · base-mixed candidates",
                   rho=0.100, rlab="+0.10", color=GREEN, kind="dot",
                   pair="cautious")),
        ("H", ""),   # wordless separator
        ("R", dict(name="Self-judge — base-mixed candidates",
                   cond="Qwen insecure-code · self-description · duels",
                   rho=-0.236, rlab="−0.24", color=BLUE, kind="dot",
                   pair="self")),
        ("R", dict(name="Self-judge — own candidates",
                   cond="Qwen insecure-code · self-description · duels",
                   rho=SELF_OWNPOOL_RHO, rlab="+0.40", color=BLUE, kind="dot",
                   pair="self")),
        ("H", "the remaining setups"),
        ("R", dict(name="Qwen grid — itself",
                   cond="Qwen risk-grid · risk · static alternative · own candidates",
                   rho=qr["evolving_self"], rlab=rlab_of(qr["evolving_self"]),
                   color=BLUE, kind="dot")),
        ("R", dict(name="Qwen grid — a frozen copy",
                   cond="Qwen risk-grid · risk · static alternative · own candidates",
                   rho=qr["frozen_copy_r0"], rlab=rlab_of(qr["frozen_copy_r0"]),
                   color=GREEN, kind="dot")),
        ("R", dict(name="Qwen grid — the base model",
                   cond="Qwen risk-grid · risk · static alternative · own candidates",
                   rho=qr["frozen_base"], rlab=rlab_of(qr["frozen_base"]),
                   color=GREEN, kind="dot")),
        ("R", dict(name="Self-judge — peer-mixed answers",
                   cond="OLMo risky-gambles · risk · duels",
                   rho=0.524, rlab="+0.52", color=BLUE, kind="dot")),
    ]

    ypos = []
    cursor = 214
    for kind, payload in seq:
        if kind == "H":
            cursor += 30
            ypos.append(cursor - 10)          # header baseline
        else:
            cursor += 47
            payload["dot_y"] = cursor - 20     # dot centre (row baseline)
            ypos.append(cursor - 20)
    chart_bottom = cursor + 14
    HH = chart_bottom + 12

    # background (full canvas, now that height is known)
    b.insert(0, f'<rect width="{W}" height="{HH}" fill="white"/>')

    # ---- vertical gridlines spanning the whole ladder (behind the rows) ----
    grid = []
    for rho in (-1, -0.5, 0, 0.5, 1):
        x = xr(rho)
        col = "#c9ccd1" if rho == 0 else "#e7e9ec"
        sw = 1.6 if rho == 0 else 1.0
        dash = '' if rho == 0 else ' stroke-dasharray="2 5"'
        grid.append(f'<line x1="{x:.1f}" y1="{AX_Y+8}" x2="{x:.1f}" '
                    f'y2="{chart_bottom}" stroke="{col}" stroke-width="{sw}"{dash}/>')
    b[1:1] = grid

    # ---- lollipop bars: every dot gets a horizontal bar from the rho = 0
    # line out to the dot, in the row's color at low opacity, drawn now so the
    # dots (rendered below) sit on top and are never swallowed. ----
    for kind, payload in seq:
        if kind != "R":
            continue
        r = payload
        x = xr(r["rho"])
        if abs(x - CX) <= 1:            # random at 0: no bar
            continue
        bx0, bx1 = (CX, x) if x >= CX else (x, CX)
        b.append(f'<rect x="{bx0:.1f}" y="{r["dot_y"]-3.5:.1f}" '
                 f'width="{bx1-bx0:.1f}" height="7" rx="2" '
                 f'fill="{r["color"]}" opacity="0.35"/>')

    # ---- pair brackets (replace the old dumbbells: the two lollipop bars now
    # carry the move, so pair membership is marked by a thin bracket hugging the
    # left of the two row names, in the pair color). ----
    pair_rows = {}
    for kind, payload in seq:
        if kind == "R" and payload.get("pair"):
            pair_rows.setdefault(payload["pair"], []).append(payload)
    for pr in pair_rows.values():
        if len(pr) == 2:
            ys = sorted([pr[0]["dot_y"], pr[1]["dot_y"]])
            bx = LX - 14
            b.append(f'<path d="M {bx+7:.1f} {ys[0]-7:.1f} H {bx:.1f} '
                     f'V {ys[1]+7:.1f} H {bx+7:.1f}" fill="none" '
                     f'stroke="{pr[0]["color"]}" stroke-width="2.2" '
                     f'opacity="0.75"/>')

    # ---- render headers and rows ----
    for (kind, payload), yy in zip(seq, ypos):
        if kind == "H":
            b.append(txt(LX, yy, payload, 13.5, GRAY, "bold"))
            b.append(f'<line x1="{LX}" y1="{yy+8}" x2="{PX1}" y2="{yy+8}" '
                     f'stroke="#e7e9ec" stroke-width="1"/>')
            continue
        r = payload
        dy = r["dot_y"]
        b.append(txt(LX, dy + 3, r["name"], 16, INK, "bold"))
        b.append(txt(LX, dy + 20, r["cond"], 12.5, GRAY))
        x = xr(r["rho"])
        if r["kind"] == "hollow":
            b.append(f'<circle cx="{x:.1f}" cy="{dy}" r="8" fill="white" '
                     f'stroke="{GRAY}" stroke-width="2.5"/>')
            b.append(txt(x + 15, dy + 5, r["rlab"], 15, GRAY, "bold", "start"))
        else:
            b.append(dot(x, dy, r["color"]))
            # keep the rho label clear of its own bar: right of positive dots,
            # left of negative dots.
            if r["rho"] >= 0:
                b.append(txt(x + 15, dy + 5, r["rlab"], 15, r["color"], "bold",
                             "start"))
            else:
                b.append(txt(x - 15, dy + 5, r["rlab"], 15, r["color"], "bold",
                             "end"))

    defs = (f'<defs><marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" '
            f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {HH}" '
            f'font-family="{FONT}">\n{defs}\n' + "\n".join(b) + "\n</svg>")


if __name__ == "__main__":
    verify()
    svg = build()
    out = os.path.join(HERE, "judges-agreement-axis.svg")
    with open(out, "w") as f:
        f.write(svg)
    print("wrote", out)

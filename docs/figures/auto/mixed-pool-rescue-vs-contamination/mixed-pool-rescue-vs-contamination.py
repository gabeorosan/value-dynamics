#!/usr/bin/env python3
"""Draft figure: mixed-pool runs — a shared candidate pool is a fast
contamination vector and only a slow, selector-gated remedy.

All plotted numbers are recomputed from the raw result JSONs in
experiments/modal_k2_release/output/ (Modal branch m, plus the branch-e
self-only comparator cells). Regenerate with:
    python3 mixed-pool-rescue-vs-contamination.py
Style follows docs/figures/src/make_figures.py (Owain Evans-lab idiom).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "..", "..", "..",
                       "experiments", "modal_k2_release", "output")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"
DOC_FILL = "#fdf6e8"
KEY_FILL = "#eef5ee"
WARN_FILL = "#fbf0ee"
GRID = "#e6e6e6"

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


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


DEFS = f'''<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker>
<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{GREEN}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# --------------------------------------------------------------------
# Load the raw trajectories (free-generation risk, rounds 0..4).
# --------------------------------------------------------------------
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
    # self-only comparators (branch e / base_hold), separate runs
    "oracle_hold_21": load("k2rel_oracle_hold_s21.json", "21", "oracle_hold"),
    "oracle_hold_22": load("k2rel_oracle_hold_s22.json", "22", "oracle_hold"),
    "base_hold_1": load("k2rel_base_hold_s1.json", "1", "base_hold"),
    "base_hold_2": load("k2rel_base_hold_s2.json", "2", "base_hold"),
}

TRAJ = {k: v["traj"] for k, v in CELLS.items()}


def kept_cogen_shares(cell):
    out = []
    for rnd in CELLS[cell]["rounds_raw"]:
        kept = tot = 0
        for it in rnd:
            owners = it["cand_owner"]
            kept += sum(1 for i in it["kept_idx"] if owners[i] == "cogen")
            tot += len(it["kept_idx"])
        out.append(kept / tot)
    return out


def kept_minus_pool(cell):
    out = []
    for rnd in CELLS[cell]["rounds_raw"]:
        gaps = []
        for it in rnd:
            risks = it["cand_risk"]
            keptr = sum(risks[i] for i in it["kept_idx"]) / len(it["kept_idx"])
            gaps.append(keptr - sum(risks) / len(risks))
        out.append(sum(gaps) / len(gaps))
    return out


# sanity readouts used in annotations (recomputed, printed for the record)
ORACLE_SHARES = kept_cogen_shares("oracle_mix_31") + kept_cogen_shares("oracle_mix_32")
CONS_FINAL_SHARES = [kept_cogen_shares("cons_mix_33")[-1], kept_cogen_shares("cons_mix_34")[-1]]
CONS_GAPS = kept_minus_pool("cons_mix_33") + kept_minus_pool("cons_mix_34")
ORACLE_GAPS = kept_minus_pool("oracle_mix_31") + kept_minus_pool("oracle_mix_32")
INVADE_R1_SHARES = [kept_cogen_shares(c)[0] for c in
                    ("invade_base_35", "invade_base_36", "invade_self_37", "invade_self_38")]
print("oracle kept-cogen shares:", [round(s, 2) for s in ORACLE_SHARES])
print("oracle kept-minus-pool:", [round(g, 2) for g in ORACLE_GAPS])
print("cons final-round kept-cogen shares:", [round(s, 2) for s in CONS_FINAL_SHARES])
print("cons kept-minus-pool:", [round(g, 2) for g in CONS_GAPS])
print("invade round-1 kept-cogen shares:", [round(s, 2) for s in INVADE_R1_SHARES])

# --------------------------------------------------------------------
# Figure geometry
# --------------------------------------------------------------------
W, H = 1560, 1215
PT, PB = 250, 650                    # plot top / bottom (shared y scale)
LX0, LX1 = 100, 640                  # left plot x range
RX0, RX1 = 885, 1385                 # right plot x range


def yp(v):
    return PB - v * (PB - PT)


def xp(x0, x1, r):
    return x0 + r * (x1 - x0) / 4.0


def axes(x0, x1, tag):
    s = []
    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        y = yp(v)
        s.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{GRID}" stroke-width="1.4"/>')
        s.append(f'<text x="{x0 - 10}" y="{y + 4.5}" text-anchor="end" font-size="13" '
                 f'fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
    s.append(f'<line x1="{x0}" y1="{PT - 8}" x2="{x0}" y2="{PB}" stroke="{GRAY}" stroke-width="1.8"/>')
    s.append(f'<line x1="{x0}" y1="{PB}" x2="{x1}" y2="{PB}" stroke="{GRAY}" stroke-width="1.8"/>')
    for r in range(5):
        x = xp(x0, x1, r)
        s.append(f'<line x1="{x}" y1="{PB}" x2="{x}" y2="{PB + 6}" stroke="{GRAY}" stroke-width="1.8"/>')
        s.append(f'<text x="{x}" y="{PB + 24}" text-anchor="middle" font-size="14" '
                 f'fill="{GRAY}" font-family="{FONT}">{r}</text>')
    s.append(f'<text x="{(x0 + x1) / 2}" y="{PB + 48}" text-anchor="middle" font-size="15" '
             f'fill="{GRAY}" font-family="{FONT}">self-training round</text>')
    if tag == "left":
        s.append(f'<text x="{x0 - 62}" y="{(PT + PB) / 2}" font-size="15" fill="{GRAY}" '
                 f'font-family="{FONT}" transform="rotate(-90 {x0 - 62} {(PT + PB) / 2})" '
                 f'text-anchor="middle">free-generation risk</text>')
    return "\n".join(s)


def series(x0, x1, traj, color, dash=None, opacity=1.0, lw=3.4, marker=True, mfill=None):
    pts = [(xp(x0, x1, r), yp(v)) for r, v in enumerate(traj[:5])]
    d = " ".join(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    s = [f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{lw}"'
         f'{dash_attr} opacity="{opacity}"/>']
    if marker:
        for x, y in pts:
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="{mfill or color}" '
                     f'stroke="white" stroke-width="1.6" opacity="{opacity}"/>')
    return "\n".join(s)


b = []

# ---- headline -------------------------------------------------------
t, _ = text_block(W // 2, 46, "A shared pool is a fast contamination vector — and only a slow, selector-gated remedy",
                  29, 200, weight="bold")
b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
sub = ("Mixed-pool self-training on OLMo-3-7B-Instruct risk organisms: every round, 3 of the 6 candidate answers come from the evolving organism "
       "and 3 from a frozen co-generator; the judge keeps 2 of 6 as training data. 2 seeds per cell; self-only comparators are separate runs "
       "(descriptive comparison, not an effect estimate).")
t, _ = text_block(W // 2, 78, sub, 15.5, 168, GRAY)
for i, line in enumerate(t.split("\n")):
    b.append(line.replace('<text ', '<text text-anchor="middle" ', 1))

# ---- panel titles ---------------------------------------------------
t, _ = text_block(LX0 - 40, 160, "Rescue attempt: railed organisms, low-risk material injected", 19, 62, GREEN, "bold")
b.append(t)
t, _ = text_block(LX0 - 40, 186, "starting adapters read risk 0.93 / 1.00 at round 0; the co-generator is the raw base model (mostly low-risk answers)",
                  14, 88, GRAY)
b.append(t)
t, _ = text_block(RX0 - 45, 160, "Contamination: fresh organisms, one railed co-generator", 19, 62, RED, "bold")
b.append(t)
t, _ = text_block(RX0 - 45, 186, "starting adapters read risk 0.24-0.36 at round 0; the co-generator is a railed risk-1.000 vintage of the same organism",
                  14, 88, GRAY)
b.append(t)

# ---- axes -----------------------------------------------------------
b.append(axes(LX0, LX1, "left"))
b.append(axes(RX0, RX1, "right"))

# ---- LEFT panel series ---------------------------------------------
# self-only ghosts first (under the with-injection curves)
b.append(series(LX0, LX1, TRAJ["oracle_hold_21"], GREEN, dash="8 6", opacity=0.45, lw=2.6))
# the flat self-only 1.000 rail: nudge 5px above the axis line so it stays
# visible under cons_mix seed 34 (both sit at 1.000; labeled below)
ghost22 = [(xp(LX0, LX1, r), yp(v) - 5) for r, v in enumerate(TRAJ["oracle_hold_22"][:5])]
d22 = " ".join(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}" for i, (x, y) in enumerate(ghost22))
b.append(f'<path d="{d22}" fill="none" stroke="{GREEN}" stroke-width="2.6" '
         f'stroke-dasharray="8 6" opacity="0.45"/>')
b.append(series(LX0, LX1, TRAJ["cons_mix_34"], INK))
b.append(series(LX0, LX1, TRAJ["cons_mix_33"], INK))
b.append(series(LX0, LX1, TRAJ["oracle_mix_32"], GREEN))
b.append(series(LX0, LX1, TRAJ["oracle_mix_31"], GREEN))

# endpoint labels, left
def endlab(x, v, lines, color, dy=0, size=12.5, bold_first=True):
    out = []
    y = yp(v) + 4 + dy
    for i, (txt, c) in enumerate(lines):
        out.append(f'<text x="{x}" y="{y + i * (size + 3)}" font-size="{size}" '
                   f'fill="{c}" font-family="{FONT}"'
                   + (' font-weight="bold"' if (i == 0 and bold_first) else "")
                   + f'>{esc(txt)}</text>')
    return "\n".join(out)


LLX = LX1 + 12
b.append(endlab(LLX, 1.0, [("1.000  conservative judge,", INK),
                           ("with injection (seed 34)", INK),
                           ("1.000  oracle judge, self-only", GREEN),
                           ("(seed 22) — never moved; its", GREEN),
                           ("pool had zero spread", GREEN)], INK, dy=0))
b.append(endlab(LLX, TRAJ["cons_mix_33"][4], [("0.716  conservative judge,", INK),
                                              ("with injection (seed 33)", INK)], INK))
b.append(endlab(LLX, TRAJ["oracle_mix_32"][4], [("0.484  oracle judge,", GREEN),
                                                ("with injection (seed 32)", GREEN)], GREEN))
b.append(endlab(LLX, TRAJ["oracle_mix_31"][4], [("0.344  oracle judge,", GREEN),
                                                ("with injection (seed 31)", GREEN)], GREEN, dy=8))
b.append(endlab(LLX, TRAJ["oracle_hold_21"][4], [("0.094  oracle judge,", GREEN),
                                                 ("self-only run (seed 21)", GREEN)], GREEN, dy=4))

# dashed-ghost legend note, left panel interior (bottom-left is empty)
t, _ = text_block(LX0 + 14, yp(0.10), "dashed, faded = self-only runs", 13, 34, GRAY)
b.append(t)
t, _ = text_block(LX0 + 14, yp(0.10) + 18, "(no co-generator), same oracle selector", 13, 44, GRAY)
b.append(t)

# ---- RIGHT panel series --------------------------------------------
# self-only base_hold ghosts, first 5 of 9 rounds
b.append(series(RX0, RX1, TRAJ["base_hold_2"][:5], RED, dash="8 6", opacity=0.45, lw=2.6))
b.append(series(RX0, RX1, TRAJ["base_hold_1"][:5], RED, dash="8 6", opacity=0.45, lw=2.6))
b.append(series(RX0, RX1, TRAJ["invade_base_35"], RED))
b.append(series(RX0, RX1, TRAJ["invade_base_36"], RED))
b.append(series(RX0, RX1, TRAJ["invade_self_37"], RED, mfill="white"))
b.append(series(RX0, RX1, TRAJ["invade_self_38"], RED, mfill="white"))

RLX = RX1 + 12
b.append(endlab(RLX, 1.0, [("0.989-1.000  all four", RED),
                           ("contaminated runs", RED),
                           ("(seeds 35-38)", RED)], RED, dy=2))
b.append(endlab(RLX, TRAJ["base_hold_2"][4], [("0.500  self-only, no", RED),
                                              ("contaminant (seed 2)", RED)], RED))
b.append(endlab(RLX, TRAJ["base_hold_1"][4], [("0.250  self-only, no", RED),
                                              ("contaminant (seed 1)", RED)], RED, dy=6))

# the one-round takeover arrow + annotation
ax0, ay0 = xp(RX0, RX1, 0) + 14, yp(0.32)
ax1, ay1 = xp(RX0, RX1, 1) - 14, yp(0.93)
b.append(f'<line x1="{ax0}" y1="{ay0}" x2="{ax1}" y2="{ay1}" stroke="{RED}" '
         f'stroke-width="5" marker-end="url(#arrR)"/>')
t, _ = text_block(xp(RX0, RX1, 1.15), yp(0.70),
                  "one round: the judge keeps the contaminant's text in 96-100% of the selections that train round 1",
                  14.5, 30, RED, "bold")
b.append(t)
t, _ = text_block(xp(RX0, RX1, 0.9), yp(0.145),
                  "filled markers = frozen base-model judge (seeds 35, 36); open markers = the evolving organism judging itself (seeds 37, 38): the judge does not matter here.",
                  13, 60, INK)
b.append(t)

# start labels
b.append(f'<text x="{xp(RX0, RX1, 0) + 12}" y="{yp(0.20)}" font-size="12.5" '
         f'fill="{GRAY}" font-family="{FONT}">starts 0.244-0.363</text>')

# ---- takeaway boxes -------------------------------------------------
BOXY = 745
bx, bw = 60, 700
b.append(box(bx, BOXY, bw, 192, KEY_FILL, GREEN, 3, rx=12))
t, ty = text_block(bx + 18, BOXY + 30, "The oracle selector uses the injected material — but lands at the supplier's level, not the floor", 15.5, 78, GREEN, "bold")
b.append(t)
body = ("The oracle keeps the 2 measured-lowest-risk answers of 6: with injection it keeps co-generator text in 42-75% of selections, "
        "and its kept answers run 0.26-0.50 below the pool's mean risk each round. The frozen rail moves under it (the self-only run from seed 32's "
        "starting adapter never left 1.000; with injection the same adapter reaches 0.484) — yet both runs end near the base model's own level "
        "(0.344 / 0.484), above the 0.094 the self-only oracle run reached from the other starting adapter.")
t, _ = text_block(bx + 18, ty + 14, body, 13.8, 104)
b.append(t)

B2Y = BOXY + 206
b.append(box(bx, B2Y, bw, 148, "white", INK, 3, rx=12))
t, ty = text_block(bx + 18, B2Y + 30, "The frozen conservative judge wastes the same material", 15.5, 92, INK, "bold")
b.append(t)
body = ("Same railed inits, same base-model injection: by the final round this judge keeps co-generator text in only 0-17% of selections, and "
        "the answers it keeps run +0.03 to +0.24 riskier than the pool mean — it prefers the rail's own confident high-risk text. "
        "End states 0.716 and 1.000: the low-risk material sits unused in the pool.")
t, _ = text_block(bx + 18, ty + 14, body, 13.8, 104)
b.append(t)

rbx, rbw = 800, 700
b.append(box(rbx, BOXY, rbw, 246, WARN_FILL, RED, 3, rx=12))
t, ty = text_block(rbx + 18, BOXY + 30, "One round to take over — under either judge", 15.5, 92, RED, "bold")
b.append(t)
body = ("Whether the judge is the frozen base model or the evolving organism itself, it keeps the railed co-generator's text in 96-100% of the "
        "selections that train round 1. All four runs read 0.917-1.000 at round 1 and 0.989-1.000 at round 4. By round 2 the candidate pool's "
        "max-minus-min risk is 0.000 in every cell: the victim now generates the contaminant's text on its own, so from then on the runs are "
        "selection-inert on the measured risk axis.")
t, ny = text_block(rbx + 18, ty + 14, body, 13.8, 104)
b.append(t)
body2 = ("Self-only runs from the same fresh state (no contaminant, frozen base-model judge) read only 0.250 / 0.500 at round 4 and 0.562 / 0.875 "
         "by round 8 — with a railed co-generator in the pool, that slow upward drift happens in a single round.")
t, _ = text_block(rbx + 18, ny + 12, body2, 13.8, 104)
b.append(t)

# ---- footer: readout recipe + validity ------------------------------
FY = 1130
foot1 = ("Readout: free-generation risk = the share of 96 free-text answers per round that choose the gamble (12 fixed gamble questions x 2 "
         "presentation orders x 4 samples at temperature 1.0); round 0 is the starting adapter before any mixed-pool training.")
t, ny = text_block(60, FY, foot1, 13, 172, GRAY)
b.append(t)
foot2 = ("Order-robustness: endpoint order gaps are at most 0.062 in every cell except oracle-with-injection seed 32, whose endpoint 0.484 reads "
         "0.383 / 0.583 across the two presentation orders (gap 0.200); the reversal holds in both orders. Existence results: 2 seeds per cell, "
         "and the self-only comparators use different random streams.")
t, _ = text_block(60, ny + 6, foot2, 13, 172, GRAY)
b.append(t)

with open(os.path.join(HERE, "mixed-pool-rescue-vs-contamination.svg"), "w") as f:
    f.write(svg_doc(W, H, "\n".join(b)))
print("wrote mixed-pool-rescue-vs-contamination.svg")

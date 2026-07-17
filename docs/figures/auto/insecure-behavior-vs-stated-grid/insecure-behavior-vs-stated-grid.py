#!/usr/bin/env python3
"""All 19 insecure-code selection-loop rollouts, one mini-panel each:
behavioral insecure-code self-description (solid RED) against the separate
forced code-insecurity probe (dashed RED), with a per-panel sign-agreement chip.

Second candidate for the insecure-code analogue of
docs/figures/auto/behavior-vs-stated/ — small-multiples over ALL rollouts
instead of a few exemplars, so the seed-level sign flips are glanceable.

Reads live numbers (with an n=19 assertion) from:
  experiments/stated_channel_parity.json  ->  qwen_insecure_loops.rollouts
Report: docs/report_stated_channel_parity.md (section B)

Run from this directory:  python3 insecure-behavior-vs-stated-grid.py
Stdlib only, matching docs/figures/src/make_figures.py house style.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "stated_channel_parity.json")

# ---- palette copied verbatim from make_figures.py -------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
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


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---- load ------------------------------------------------------------
D = json.load(open(DATA))
ROLL = D["qwen_insecure_loops"]["rollouts"]
assert len(ROLL) == 19, f"expected 19 insecure-code rollouts, got {len(ROLL)}"

# ---- condition groups: ordered, with a full band label + short panel tag
# (cond string) -> (band label, short panel tag, light group tint)
GROUPS = [
    ("candid self-prompt (self judge)",
     "candid self-prompt (self judge)", "candid", "#fbeeed"),
    ("min-insecurity oracle",
     "min-insecurity oracle", "min-oracle", "#eef2f7"),
    ("base judge, static alternative",
     "base judge, static alternative", "base-judge", "#f2eff6"),
    ("oracle, base-mixed pool",
     "oracle, base-mixed pool", "oracle-mix", "#eef5ee"),
    ("self-judge duels, base-mixed pool",
     "self-judge duels, base-mixed pool", "duel-mix", "#fbf3e9"),
]
GMETA = {g[0]: g for g in GROUPS}

# order the 19 rollouts by group order, keeping file order within a group
ordered = []
for cond, _, _, _ in GROUPS:
    for r in ROLL:
        if r["cond"] == cond:
            ordered.append(r)
assert len(ordered) == 19

# short per-panel title: tag + dose hint (from cell prefix) + seed
def panel_title(r):
    tag = GMETA[r["cond"]][2]
    cell = r.get("cell", "")
    seed = "s" + str(r["seed"])
    # distinguish the two candid starting doses (low vs high)
    if r["cond"] == "candid self-prompt (self judge)":
        dose = "lo" if cell.startswith("low:") else "hi"
        return f"{tag}·{dose} {seed}"
    return f"{tag} {seed}"


def sign_agree(r):
    """GREEN chip if behavior and stated moved the same way, or the stated
    channel barely moved (|d_sr| < 0.05); RED if they moved opposite ways."""
    dt, ds = r["d_traj"], r["d_sr"]
    if abs(ds) < 0.05:
        return True
    return (dt >= 0) == (ds >= 0)


def signed(v):
    return f"{'+' if v >= 0 else '−'}{abs(v):.2f}"


# ====================================================================
# Layout — 5 columns x 4 rows; slot 20 (row 4, col 5) holds the key
# ====================================================================
W, H = 1560, 1100
NCOL, NROW = 5, 4
MARGX, TOPY = 56, 222
GAPX, GAPY = 26, 58          # GAPY leaves room for group-band label rows
PANW = (W - 2 * MARGX - (NCOL - 1) * GAPX) / NCOL
PANH = 168

s = []

# ---- headline + subtitle -------------------------------------------
s.append(f'<text x="{MARGX}" y="62" font-size="33" font-weight="bold" fill="{INK}">'
         f'All 19 insecure-code rollouts: behavior (solid) vs the stated probe (dashed)</text>')
sub = ("The Qwen3-4B insecure-code organism's selection loops. Each panel is one "
       "rollout: x = round index, y = 0..1. The forced probe MOVES here (unlike the "
       "risk probe) but its sign is unreliable — 7 of 19 panels move opposite to "
       "behavior (red chip); tracking ratio spans −0.81 to +1.39, with seed-level "
       "sign flips inside the candid cell.")
for i, ln in enumerate(wrap(sub, 128)):
    s.append(f'<text x="{MARGX}" y="{94 + i*25}" font-size="18" fill="{GRAY}">{esc(ln)}</text>')

# ---- top key strip (line styles + chip rule) -----------------------
ky = 176
s.append(f'<line x1="{MARGX}" y1="{ky}" x2="{MARGX+44}" y2="{ky}" stroke="{RED}" stroke-width="4"/>')
s.append(f'<text x="{MARGX+52}" y="{ky+6}" font-size="16" font-weight="bold" fill="{INK}">'
         f'behavior (solid)</text>')
s.append(f'<line x1="{MARGX+235}" y1="{ky}" x2="{MARGX+279}" y2="{ky}" stroke="{RED}" '
         f'stroke-width="4" stroke-dasharray="3 5"/>')
s.append(f'<text x="{MARGX+287}" y="{ky+6}" font-size="16" font-weight="bold" fill="{INK}">'
         f'stated forced probe (dashed)</text>')
# chip rule
cxr = MARGX + 560
s.append(f'<rect x="{cxr}" y="{ky-12}" width="17" height="15" rx="3" fill="{GREEN}"/>')
s.append(f'<text x="{cxr+24}" y="{ky+1}" font-size="15" fill="{INK}">chip green = signs agree (or |stated move| &lt; 0.05)</text>')
s.append(f'<rect x="{cxr+380}" y="{ky-12}" width="17" height="15" rx="3" fill="{RED}"/>')
s.append(f'<text x="{cxr+404}" y="{ky+1}" font-size="15" fill="{INK}">red = opposite signs</text>')


def px_x(col):
    return MARGX + col * (PANW + GAPX)


def px_y(row):
    return TOPY + row * (PANH + GAPY)


# ---- draw one mini-panel --------------------------------------------
def mini(r, x0, y0):
    tint = GMETA[r["cond"]][3]
    n = len(r["traj"])
    # panel background (group tint) + frame
    s.append(f'<rect x="{x0}" y="{y0}" width="{PANW:.1f}" height="{PANH}" rx="6" '
             f'fill="{tint}" stroke="#dfe3e8" stroke-width="1.5"/>')
    # inner plot box
    pad_l, pad_r, pad_t, pad_b = 30, 12, 34, 26
    bx, by = x0 + pad_l, y0 + pad_t
    bw, bh = PANW - pad_l - pad_r, PANH - pad_t - pad_b

    def X(i):
        return bx + (i / (n - 1)) * bw

    def Y(v):
        return by + (1 - v) * bh

    # gridlines at 0 and 1 only
    for v in (0.0, 1.0):
        yy = Y(v)
        s.append(f'<line x1="{bx}" y1="{yy:.1f}" x2="{bx+bw:.1f}" y2="{yy:.1f}" '
                 f'stroke="#ffffff" stroke-width="1.4"/>')
        s.append(f'<text x="{bx-6}" y="{yy+5:.1f}" font-size="12.5" fill="{GRAY}" '
                 f'text-anchor="end">{int(v)}</text>')
    # axes
    s.append(f'<line x1="{bx}" y1="{by}" x2="{bx}" y2="{by+bh}" stroke="{INK}" stroke-width="1.4"/>')
    s.append(f'<line x1="{bx}" y1="{by+bh}" x2="{bx+bw:.1f}" y2="{by+bh}" stroke="{INK}" stroke-width="1.4"/>')
    # x round ticks
    for i in range(n):
        s.append(f'<text x="{X(i):.1f}" y="{by+bh+16:.1f}" font-size="12.5" fill="{GRAY}" '
                 f'text-anchor="middle">{i}</text>')

    # stated (dashed) first so behavior sits on top
    pss = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(r["sr"]))
    s.append(f'<polyline points="{pss}" fill="none" stroke="{RED}" stroke-width="2.4" '
             f'stroke-dasharray="3 4" opacity="0.85"/>')
    for i, v in enumerate(r["sr"]):
        s.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="2.6" fill="white" '
                 f'stroke="{RED}" stroke-width="1.6"/>')
    # behavior (solid)
    ptb = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(r["traj"]))
    s.append(f'<polyline points="{ptb}" fill="none" stroke="{RED}" stroke-width="3"/>')
    for i, v in enumerate(r["traj"]):
        s.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3.2" fill="{RED}"/>')

    # panel title
    s.append(f'<text x="{x0+8}" y="{y0+20}" font-size="12.5" font-weight="bold" fill="{INK}">'
             f'{esc(panel_title(r))}</text>')

    # corner chip: net moves, colored by sign agreement
    chip = GREEN if sign_agree(r) else RED
    txt = f'beh {signed(r["d_traj"])} / stated {signed(r["d_sr"])}'
    cw = 7.05 * len(txt) + 12
    cxx = x0 + PANW - cw - 6
    cyy = y0 + PANH - 22
    s.append(f'<rect x="{cxx:.1f}" y="{cyy:.1f}" width="{cw:.1f}" height="17" rx="4" '
             f'fill="white" stroke="{chip}" stroke-width="1.6"/>')
    s.append(f'<text x="{cxx+cw/2:.1f}" y="{cyy+12.4:.1f}" font-size="12.5" '
             f'font-weight="bold" fill="{chip}" text-anchor="middle">{esc(txt)}</text>')


# ---- place panels + group band labels -------------------------------
prev_group = None
for idx, r in enumerate(ordered):
    col, row = idx % NCOL, idx // NCOL
    x0, y0 = px_x(col), px_y(row)
    # group band label: printed above the first panel of each group
    if r["cond"] != prev_group:
        meta = GMETA[r["cond"]]
        by_lbl = y0 - 12
        s.append(f'<rect x="{x0}" y="{by_lbl-15}" width="9" height="15" rx="2" fill="{meta[3]}" '
                 f'stroke="#c9cfd6" stroke-width="1"/>')
        s.append(f'<text x="{x0+15}" y="{by_lbl-2}" font-size="14" font-weight="bold" '
                 f'fill="{INK}">{esc(meta[1])} '
                 f'<tspan fill="{GRAY}" font-weight="normal">(n={sum(1 for q in ordered if q["cond"]==r["cond"])})</tspan></text>')
        prev_group = r["cond"]
    mini(r, x0, y0)

# ---- key slot (row 4, col 5 = slot index 19) ------------------------
kx0, ky0 = px_x(4), px_y(3)
s.append(f'<rect x="{kx0}" y="{ky0}" width="{PANW:.1f}" height="{PANH}" rx="6" '
         f'fill="{KEY_FILL}" stroke="{INK}" stroke-width="1.8"/>')
s.append(f'<text x="{kx0+12}" y="{ky0+22}" font-size="14" font-weight="bold" fill="{INK}">How to read a panel</text>')
# line-style legend
lyl = ky0 + 44
s.append(f'<line x1="{kx0+14}" y1="{lyl}" x2="{kx0+48}" y2="{lyl}" stroke="{RED}" stroke-width="3"/>')
s.append(f'<text x="{kx0+54}" y="{lyl+5}" font-size="12.5" fill="{INK}">behavior (solid)</text>')
lyl += 22
s.append(f'<line x1="{kx0+14}" y1="{lyl}" x2="{kx0+48}" y2="{lyl}" stroke="{RED}" stroke-width="2.4" stroke-dasharray="3 4"/>')
s.append(f'<text x="{kx0+54}" y="{lyl+5}" font-size="12.5" fill="{INK}">stated probe (dashed)</text>')
lyl += 24
s.append(f'<rect x="{kx0+14}" y="{lyl-11}" width="15" height="14" rx="3" fill="white" stroke="{GREEN}" stroke-width="1.6"/>')
s.append(f'<text x="{kx0+35}" y="{lyl}" font-size="12.5" fill="{INK}">chip green = signs agree</text>')
lyl += 20
s.append(f'<rect x="{kx0+14}" y="{lyl-11}" width="15" height="14" rx="3" fill="white" stroke="{RED}" stroke-width="1.6"/>')
s.append(f'<text x="{kx0+35}" y="{lyl}" font-size="12.5" fill="{INK}">chip red = opposite signs</text>')
lyl += 24
defn = ("behavior = the per-answer self-description score the loop selects on; "
        "stated = the separate forced probe, seen by no judge.")
for j, ln in enumerate(wrap(defn, 34)):
    s.append(f'<text x="{kx0+14}" y="{lyl+j*15}" font-size="11.5" fill="{GRAY}">{esc(ln)}</text>')

out = os.path.join(HERE, "insecure-behavior-vs-stated-grid.svg")
open(out, "w").write(svg_doc(W, H, "\n".join(s)))
print("wrote", out)

# ---- console summary (sign-flip map used in the caption) ------------
flips = sum(1 for r in ordered if not sign_agree(r))
print(f"n={len(ordered)}  opposite-sign panels={flips}")
for cond, band, tag, _ in GROUPS:
    grp = [r for r in ordered if r["cond"] == cond]
    red = sum(1 for r in grp if not sign_agree(r))
    print(f"  {band}: n={len(grp)}  opposite-sign={red}")

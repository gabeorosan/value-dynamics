#!/usr/bin/env python3
"""fig10 / fig11 — a shared candidate pool as a slow remedy vs. a fast attack
vector.

fig10 (rescue): a model stuck almost always choosing the risky gamble gets
safe answers mixed into its candidate pool every round. A cautious judge
keeps them and risk falls; a neutral judge ignores them and risk stays high.

fig11 (contamination): a fresh, mostly-cautious model has a frozen copy of
the same model — already stuck at maximum risk — added as a second source of
answers in its pool. Within one round the fresh model is taken over.

Both panels plot free-generation risk (share of free-text answers that pick
the gamble) across four rounds of training. All numbers are recomputed from
the raw result JSONs in experiments/modal_k2_release/output/.

Helpers (esc, wrap, text_block, ctext, box, marker, svg_doc, protocol_strip)
are copied verbatim from fig05_selection_gap_predicts_drift.py.

Regenerate with:  python3 fig10_11_shared_pool.py   (stdlib only)
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
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
PURPLE = "#8a5a9e"
AMBER = "#c07d18"
STRIP_FILL = "#eef2f6"

FONT = "Helvetica, Arial, sans-serif"

# minimum readable body font
BODY = 19


# ---------------------------------------------------------------- helpers
# (verbatim from fig05_selection_gap_predicts_drift.py)
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


def text_block(x, y, text, size, width, color=INK, weight="normal", lh=1.4):
    lines = wrap(text, width)
    svg = []
    for i, ln in enumerate(lines):
        svg.append(f'<text x="{x}" y="{y + i * size * lh}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def ctext(x, y, text, size, color=INK, weight="normal"):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(text)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def marker(x, y, shape, color, s=7.5):
    if shape == "circle":
        return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{s}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "square":
        return f'<rect x="{x-s:.1f}" y="{y-s:.1f}" width="{2*s}" height="{2*s}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "triangle":
        pts = f"{x:.1f},{y-s-1:.1f} {x-s-1:.1f},{y+s:.1f} {x+s+1:.1f},{y+s:.1f}"
        return f'<polygon points="{pts}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    if shape == "diamond":
        pts = f"{x:.1f},{y-s-1.5:.1f} {x+s+1:.1f},{y:.1f} {x:.1f},{y+s+1.5:.1f} {x-s-1:.1f},{y:.1f}"
        return f'<polygon points="{pts}" fill="{color}" stroke="white" stroke-width="1.5"/>'
    return ""


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def protocol_strip(cx, y, steps, bw=222, bh=54, gap=44):
    """One horizontal row of small labelled boxes with arrows between."""
    out = []
    n = len(steps)
    total = n * bw + (n - 1) * gap
    x = cx - total / 2
    for i, label in enumerate(steps):
        out.append(box(x, y, bw, bh, STRIP_FILL, GRAY, 1.5, rx=10))
        lines = wrap(label, int(bw / 9.5))
        ly = y + bh / 2 - (len(lines) - 1) * 10 + 6.5
        for j, ln in enumerate(lines):
            out.append(ctext(x + bw / 2, ly + j * 20, ln, BODY, INK))
        if i < n - 1:
            out.append(f'<text x="{x + bw + gap / 2:.1f}" y="{y + bh / 2 + 9:.1f}" '
                       f'text-anchor="middle" font-size="26" fill="{GRAY}" font-family="{FONT}">&#8594;</text>')
        x += bw + gap
    return "\n".join(out)


# ---------------------------------------------------------------- title block
def ctext_wrapped(cx, y, text, size, width_chars, color=INK, weight="normal", lh=1.4):
    lines = wrap(text, width_chars)
    out = []
    for i, ln in enumerate(lines):
        out.append(ctext(cx, y + i * size * lh, ln, size, color, weight))
    return "\n".join(out), y + (len(lines) - 1) * size * lh


def headline_and_strip(b, W, title, sub, steps, strip_bw=270, strip_bh=64, strip_gap=36):
    b.append(ctext(W // 2, 54, title, 30, INK, "bold"))
    sub_svg, sub_end = ctext_wrapped(W // 2, 94, sub, BODY, 118, GRAY)
    b.append(sub_svg)
    strip_y = sub_end + 30
    b.append(protocol_strip(W // 2, strip_y, steps, bw=strip_bw, bh=strip_bh, gap=strip_gap))
    return strip_y + strip_bh


def legend_row(b, cx, y, items, gap=60):
    """items: list of (color, dash_or_None, label). Centered horizontal row,
    kept clear of the plot below it so it never crosses a data line."""
    widths = [30 + len(label) * 10.6 for _, _, label in items]
    total = sum(widths) + gap * (len(items) - 1)
    x = cx - total / 2
    for (color, dash, label), w in zip(items, widths):
        if dash:
            b.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x + 30:.1f}" y2="{y:.1f}" '
                     f'stroke="{color}" stroke-width="3.4" stroke-dasharray="{dash}"/>')
        else:
            b.append(marker(x + 13, y, "circle", color, s=7))
        b.append(f'<text x="{x + 38:.1f}" y="{y + 6:.1f}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">{esc(label)}</text>')
        x += w + gap


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


# recomputed exactly as the source script computed them (see result_mixed_pool.py)
CAUTIOUS_KEPT_SHARES = kept_cogen_shares("oracle_mix_31") + kept_cogen_shares("oracle_mix_32")
NEUTRAL_FINAL_SHARES = [kept_cogen_shares("cons_mix_33")[-1], kept_cogen_shares("cons_mix_34")[-1]]
TAKEOVER_R1_SHARES = [kept_cogen_shares(c)[0] for c in
                      ("invade_base_35", "invade_base_36", "invade_self_37", "invade_self_38")]

print("cautious-judge kept-safe-answer shares (all rounds):", [round(s, 2) for s in CAUTIOUS_KEPT_SHARES])
print("neutral-judge kept-safe-answer shares (final round):", [round(s, 2) for s in NEUTRAL_FINAL_SHARES])
print("round-1 kept-share from the added risky source:", [round(s, 2) for s in TAKEOVER_R1_SHARES])

# --------------------------------------------------------------------
# shared plot geometry: risk 0..1 on y, round 0..4 on x
# --------------------------------------------------------------------
def make_axes(b, AX, AY, AW, AH, y_label):
    def ax_(rnd):
        return AX + AW * rnd / 4.0

    def ay_(v):
        return AY + AH * (1.0 - v)

    for v in (0.0, 0.25, 0.5, 0.75, 1.0):
        yy = ay_(v)
        b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(f'<text x="{AX - 14}" y="{yy + 6:.1f}" text-anchor="end" font-size="19" fill="{GRAY}" font-family="{FONT}">{v:.2f}</text>')
    for rnd in range(5):
        xx = ax_(rnd)
        b.append(f'<text x="{xx:.1f}" y="{AY + AH + 30}" text-anchor="middle" font-size="19" fill="{GRAY}" font-family="{FONT}">{rnd}</text>')
    b.append(f'<line x1="{AX}" y1="{AY}" x2="{AX}" y2="{AY + AH}" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<line x1="{AX}" y1="{AY + AH}" x2="{AX + AW}" y2="{AY + AH}" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<text x="{AX + AW / 2}" y="{AY + AH + 58}" text-anchor="middle" font-size="{BODY}" fill="{INK}" font-family="{FONT}">self-training round</text>')
    b.append(f'<text x="{AX - 78}" y="{AY + AH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {AX - 78} {AY + AH / 2})" text-anchor="middle">{y_label}</text>')
    return ax_, ay_


def draw_series(b, ax_, ay_, traj, color, dash=None, opacity=1.0, lw=3.6, mfill=None):
    pts = [(ax_(r), ay_(v)) for r, v in enumerate(traj[:5])]
    d = " ".join(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}" for i, (x, y) in enumerate(pts))
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    b.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{lw}"{dash_attr} opacity="{opacity}"/>')
    for x, y in pts:
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.5" fill="{mfill or color}" stroke="white" stroke-width="1.6" opacity="{opacity}"/>')


def end_label(b, ax_, ay_, v, text, color, dx=14, dy=0, size=19, weight="bold"):
    b.append(f'<text x="{ax_(4) + dx:.1f}" y="{ay_(v) + 6 + dy:.1f}" font-size="{size}" '
             f'font-weight="{weight}" fill="{color}" font-family="{FONT}">{esc(text)}</text>')


# ====================================================================
# FIGURE fig10 — the rescue attempt (safe answers mixed into a stuck pool)
# ====================================================================
def rescue():
    W = 1300
    b = []

    strip_bottom = headline_and_strip(
        b, W,
        "Injected safe answers only help if the judge keeps them",
        "A model stuck almost always choosing the risky gamble. Each round, half of its 6 candidate answers are safe "
        "answers mixed in from outside; a judge keeps 2 of 6 to train on. Two training runs per judge.",
        [
            "pool = model's own answers + injected safe answers",
            "judge keeps 2 of 6",
            "train on those 2",
            "measure risk",
        ])

    legend_y = strip_bottom + 56
    legend_row(b, W // 2, legend_y, [
        (GREEN, None, "cautious judge — keeps the safe answers"),
        (PURPLE, None, "neutral judge — ignores them"),
    ])

    AX, AY, AW, AH = 210, legend_y + 60, 760, 400
    ax_, ay_ = make_axes(b, AX, AY, AW, AH, "share of free answers choosing the gamble")

    draw_series(b, ax_, ay_, TRAJ["cons_mix_34"], PURPLE)
    draw_series(b, ax_, ay_, TRAJ["cons_mix_33"], PURPLE)
    draw_series(b, ax_, ay_, TRAJ["oracle_mix_32"], GREEN)
    draw_series(b, ax_, ay_, TRAJ["oracle_mix_31"], GREEN)

    end_label(b, ax_, ay_, TRAJ["cons_mix_34"][4], f"{TRAJ['cons_mix_34'][4]:.3f}  neutral judge", PURPLE, dy=-4)
    end_label(b, ax_, ay_, TRAJ["cons_mix_33"][4], f"{TRAJ['cons_mix_33'][4]:.3f}  neutral judge", PURPLE, dy=8)
    end_label(b, ax_, ay_, TRAJ["oracle_mix_32"][4], f"{TRAJ['oracle_mix_32'][4]:.3f}  cautious judge", GREEN, dy=-4)
    end_label(b, ax_, ay_, TRAJ["oracle_mix_31"][4], f"{TRAJ['oracle_mix_31'][4]:.3f}  cautious judge", GREEN, dy=16)

    cap = (f"Round by round, the cautious judge kept the injected safe answers in "
           f"{int(round(min(CAUTIOUS_KEPT_SHARES) * 100))}–{int(round(max(CAUTIOUS_KEPT_SHARES) * 100))}% of its picks; "
           f"by the final round the neutral judge kept them in at most {int(round(max(NEUTRAL_FINAL_SHARES) * 100))}%.")
    t, cap_end = text_block(AX - 40, AY + AH + 90, cap, BODY, 108, GRAY)
    b.append(t)

    H = cap_end + 30
    svg = svg_doc(W, H, "\n".join(b))
    with open(os.path.join(FIGDIR, "fig10_shared_pool_slow_rescue.svg"), "w") as f:
        f.write(svg)
    print("wrote fig10_shared_pool_slow_rescue.svg")


# ====================================================================
# FIGURE fig11 — contamination (a stuck copy added as a second source)
# ====================================================================
def contamination():
    W = 1300
    b = []

    strip_bottom = headline_and_strip(
        b, W,
        "One risky source in the pool takes over in a single round",
        "A fresh model that mostly picks the safe payout. Each round, half of its 6 candidate answers are swapped for "
        "a frozen copy of the same model already stuck always choosing the gamble; a judge keeps 2 of 6 to train on.",
        [
            "pool = model's own answers + a second source's answers",
            "judge keeps 2 of 6",
            "train on those 2",
            "measure risk",
        ])

    legend_y = strip_bottom + 56
    legend_row(b, W // 2, legend_y, [
        (RED, None, "half the answers from a copy stuck at max risk"),
        (GRAY, "9 7", "the model’s own answers only"),
    ])

    AX, AY, AW, AH = 210, legend_y + 60, 760, 400
    ax_, ay_ = make_axes(b, AX, AY, AW, AH, "share of free answers choosing the gamble")

    # without the second source: slow, mixed drift
    draw_series(b, ax_, ay_, TRAJ["base_hold_1"][:5], GRAY, dash="9 7", opacity=0.75, lw=3.0)
    draw_series(b, ax_, ay_, TRAJ["base_hold_2"][:5], GRAY, dash="9 7", opacity=0.75, lw=3.0)
    # with the second source: takeover
    draw_series(b, ax_, ay_, TRAJ["invade_base_35"], RED)
    draw_series(b, ax_, ay_, TRAJ["invade_base_36"], RED)
    draw_series(b, ax_, ay_, TRAJ["invade_self_37"], RED)
    draw_series(b, ax_, ay_, TRAJ["invade_self_38"], RED)

    end_label(b, ax_, ay_, 1.0, "0.99–1.00  (4 runs)", RED, dy=-6)
    end_label(b, ax_, ay_, TRAJ["base_hold_2"][4], f"{TRAJ['base_hold_2'][4]:.2f}", GRAY, dy=-2)
    end_label(b, ax_, ay_, TRAJ["base_hold_1"][4], f"{TRAJ['base_hold_1'][4]:.2f}", GRAY, dy=14)

    start_vals = [TRAJ[c][0] for c in ("invade_base_35", "invade_base_36", "invade_self_37", "invade_self_38")]
    b.append(f'<text x="{ax_(0.15):.1f}" y="{ay_(0.05):.1f}" font-size="{BODY}" '
             f'fill="{GRAY}" font-family="{FONT}">starts {min(start_vals):.2f}–{max(start_vals):.2f}</text>')

    cap = (f"By the first round, the judge's picks came from the second source "
           f"{int(round(min(TAKEOVER_R1_SHARES) * 100))}–{int(round(max(TAKEOVER_R1_SHARES) * 100))}% of the time.")
    t, cap_end = text_block(AX - 40, AY + AH + 90, cap, BODY, 108, GRAY)
    b.append(t)

    H = cap_end + 30
    svg = svg_doc(W, H, "\n".join(b))
    with open(os.path.join(FIGDIR, "fig11_shared_pool_fast_contamination.svg"), "w") as f:
        f.write(svg)
    print("wrote fig11_shared_pool_fast_contamination.svg")


rescue()
contamination()

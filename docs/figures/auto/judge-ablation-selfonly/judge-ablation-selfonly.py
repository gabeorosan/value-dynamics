#!/usr/bin/env python3
"""2x2 judge-ablation factorial, Qwen em750 supplier-removed self-only loop.

Complete factorial: 24 trajectories = 4 conditions x 6 seeds (41-46), 4 rounds
each. Rows = judge PROMPT (candid / neutral). Columns = judge MODEL
(evolving self / frozen base). Everything else is held identical: the em750
organism writes all 6 candidates per prompt, head-to-head duels, keep 2, train,
repeat x4. y = forced-choice stated code-insecurity p(insecure), 0-1.

The finding: the judge-MODEL difference (evolving self minus frozen base) is
LARGE under the candid instruction (+0.413 minus -0.190 = +0.603 swing) and
NEGLIGIBLE under the neutral instruction (+0.040 minus +0.014 = +0.026). The
candid judging instruction polarizes the judge-model difference.

House style: docs/figures/make_figures.py (Owain Evans lab -- white ground,
headline finding, fat labels, real data). esc()/wrap() copied verbatim, palette
constants reused exactly.
Run:  python3 judge-ablation-selfonly.py   (writes judge-ablation-selfonly.svg)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "..", "..",
                   "experiments", "qwen_judge_ablation.json")

# --- palette (verbatim from make_figures.py) ---
INK = "#1a1a1a"
BLUE = "#2867b5"       # evolving self-judge under candid prompt (amplify)
GREEN = "#3a7d44"      # frozen base-judge accents
RED = "#b5342c"        # reversal / warning emphasis (candid+base collapse)
GRAY = "#6b7684"       # recessive only (axes, muted neutral-prompt series)
PURPLE = "#8a5a9e"     # neutral-prompt "up" seeds (muted)
KEY_FILL = "#eef5ee"   # highlighted takeaway box
MUTE_UP = "#5b6470"    # neutral-prompt amplifying seed (muted slate)
MUTE_DN = "#aab2ba"    # neutral-prompt collapsing seed (light gray)

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


def text_lines(x, y, text, size, width, color=INK, weight="normal", lh=1.4,
               anchor="start"):
    out = []
    for i, ln in enumerate(wrap(text, width)):
        out.append(f'<text x="{x}" y="{y + i * size * lh:.1f}" '
                   f'text-anchor="{anchor}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" '
                   f'fill="{color}">{esc(ln)}</text>')
    return "\n".join(out)


def sgn(v):
    return f"+{v:.3f}" if v >= 0 else f"−{abs(v):.3f}"


def sgn2(v):
    return f"+{v:.2f}" if v >= 0 else f"−{abs(v):.2f}"


def load():
    d = json.load(open(SRC))["runs"]

    def grab(run, sd):
        s = d[run]["seeds"][sd]
        return (sd, s["p_insecure_trajectory"], s["p_insecure_net"])

    conds = {
        "candid_self": [("candid_self", "41"), ("candid_self", "42"),
                        ("candid_self_ext", "43"), ("candid_self_ext", "44"),
                        ("candid_self_ext", "45"), ("candid_self_ext", "46")],
        "candid_base": [("candid_base", "41"), ("candid_base", "42"),
                        ("candid_base_ext_a", "43"), ("candid_base_ext_a", "44"),
                        ("candid_base_ext_b", "45"), ("candid_base_ext_b", "46")],
        "neutral_self": [("neutral_self", "41"), ("neutral_self", "42"),
                         ("neutral_self_ext", "43"), ("neutral_self_ext", "44"),
                         ("neutral_self_ext", "45"), ("neutral_self_ext", "46")],
        "neutral_base": [("neutral_base_a", "41"), ("neutral_base_a", "42"),
                         ("neutral_base_a", "43"), ("neutral_base_b", "44"),
                         ("neutral_base_b", "45"), ("neutral_base_b", "46")],
    }
    out = {k: [grab(r, s) for r, s in v] for k, v in conds.items()}
    # baselines: candid_self seeds 41-42 start 0.3405; everything else 0.3262
    base = d["candid_base"]["baseline"]["p_insecure"]   # 0.3262
    base_cs = d["candid_self"]["baseline"]["p_insecure"]  # 0.3405
    return out, base, base_cs


def mean(xs):
    return sum(xs) / len(xs)


def build():
    C, base, base_cs = load()

    cs = C["candid_self"]; cb = C["candid_base"]
    ns = C["neutral_self"]; nb = C["neutral_base"]

    cs_m = mean([s[2] for s in cs]); cb_m = mean([s[2] for s in cb])
    ns_m = mean([s[2] for s in ns]); nb_m = mean([s[2] for s in nb])

    # trust-the-file assertions
    assert all(len(v) == 6 for v in C.values())
    assert abs(cs_m - 0.4127) < 2e-3, cs_m
    assert abs(cb_m - (-0.1905)) < 2e-3, cb_m
    assert abs(ns_m - 0.0401) < 2e-3, ns_m
    assert abs(nb_m - 0.0145) < 2e-3, nb_m
    eff_candid = cs_m - cb_m
    eff_neutral = ns_m - nb_m
    assert abs(eff_candid - 0.603) < 3e-3, eff_candid
    assert abs(eff_neutral - 0.026) < 3e-3, eff_neutral
    # seed 46 candid+base: the lone upward drift
    s46 = [s for s in cb if s[0] == "46"][0]
    assert abs(s46[2] - 0.1258) < 1e-3 and abs(s46[1][-1] - 0.452) < 1e-3

    W, H = 1500, 1280
    b = [f'<rect width="{W}" height="{H}" fill="white"/>']

    # ---------------- headline ----------------
    b.append(f'<text x="58" y="56" font-family="{FONT}" font-size="31" '
             f'font-weight="bold" fill="{INK}">The candid judging instruction '
             f'polarizes the judge-model difference</text>')
    b.append(text_lines(58, 92,
        "Swapping the evolving-self judge for the frozen pre-loop base judge "
        "reverses the loop under a CANDID prompt "
        "(mean net +0.413 → −0.190, a +0.603 swing) — but barely "
        "moves it under a NEUTRAL prompt (+0.040 → +0.014, +0.026).",
        19, 132, color=RED, weight="bold", lh=1.32))

    b.append(text_lines(58, 158,
        "Qwen3-4B em750 insecure-code organism · supplier-removed self-only "
        "loop: the organism writes all 6 candidates per prompt · head-to-head "
        "duels, keep 2, train, repeat ×4 rounds · seeds 41–46 "
        "· ONLY the judge differs across the four panels · y = "
        "forced-choice stated code insecurity p(insecure), 0–1.",
        16, 176, color=GRAY, lh=1.34))

    # ---------------- grid geometry ----------------
    pw, ph = 470, 300
    colgap, rowgap = 150, 156
    px_left = 240
    px_right = px_left + pw + colgap          # 860
    py_top = 320
    py_bot = py_top + ph + rowgap             # 776
    ymin, ymax = 0.0, 1.0

    def Y(v):
        return py_top  # placeholder, replaced per panel

    # column headers (judge MODEL)
    hdr_y = py_top - 74
    b.append(f'<text x="{px_left + pw/2:.0f}" y="{hdr_y}" text-anchor="middle" '
             f'font-family="{FONT}" font-size="22" font-weight="bold" '
             f'fill="{INK}">judge model: <tspan fill="{BLUE}">evolving self'
             f'</tspan></text>')
    b.append(f'<text x="{px_left + pw/2:.0f}" y="{hdr_y+22}" text-anchor="middle" '
             f'font-family="{FONT}" font-size="14.5" fill="{GRAY}">the loop’s '
             f'current checkpoint judges its own candidates</text>')
    b.append(f'<text x="{px_right + pw/2:.0f}" y="{hdr_y}" text-anchor="middle" '
             f'font-family="{FONT}" font-size="22" font-weight="bold" '
             f'fill="{INK}">judge model: <tspan fill="{GREEN}">frozen base'
             f'</tspan></text>')
    b.append(f'<text x="{px_right + pw/2:.0f}" y="{hdr_y+22}" text-anchor="middle" '
             f'font-family="{FONT}" font-size="14.5" fill="{GRAY}">the fixed '
             f'pre-loop base model judges every round</text>')

    # row labels (judge PROMPT), rotated on far left
    for cy, lab, sub in ((py_top + ph/2, "candid prompt", "“favor the more honest / safety-candid answer”"),
                         (py_bot + ph/2, "neutral prompt", "“pick the better answer”")):
        b.append(f'<text x="46" y="{cy:.0f}" text-anchor="middle" '
                 f'transform="rotate(-90 46 {cy:.0f})" font-family="{FONT}" '
                 f'font-size="21" font-weight="bold" fill="{INK}">{esc(lab)}</text>')
        b.append(f'<text x="68" y="{cy:.0f}" text-anchor="middle" '
                 f'transform="rotate(-90 68 {cy:.0f})" font-family="{FONT}" '
                 f'font-size="13" fill="{GRAY}">judging instruction</text>')

    # ---------------- panel drawer ----------------
    def panel(px, py, seeds, colorfn, title_col, tag, tagcol, baseval,
              label_fn):
        def Yv(v):
            return py + ph * (ymax - v) / (ymax - ymin)

        def X(i):
            return px + pw * i / 4.0

        # gridlines + y ticks (ticks only if leftmost column)
        for v in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
            yy = Yv(v)
            b.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px+pw}" y2="{yy:.1f}" '
                     f'stroke="#ececE8" stroke-width="1"/>')
            if px == px_left:
                b.append(f'<text x="{px-12}" y="{yy+5:.1f}" text-anchor="end" '
                         f'font-family="{FONT}" font-size="14" fill="{GRAY}">'
                         f'{v:.1f}</text>')
        # panel border
        b.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" '
                 f'fill="none" stroke="#d5d5d0" stroke-width="1.2"/>')
        # dashed pre-loop baseline
        yb = Yv(baseval)
        b.append(f'<line x1="{px}" y1="{yb:.1f}" x2="{px+pw}" y2="{yb:.1f}" '
                 f'stroke="{INK}" stroke-width="1.3" stroke-dasharray="6 5"/>')
        b.append(f'<text x="{px+pw-6}" y="{yb-7:.1f}" text-anchor="end" '
                 f'font-family="{FONT}" font-size="12.5" fill="{INK}">'
                 f'pre-loop baseline ≈{baseval:.2f}</text>')
        # x ticks
        for i in range(5):
            lab = "base" if i == 0 else str(i)
            b.append(f'<text x="{X(i):.1f}" y="{py+ph+24:.1f}" '
                     f'text-anchor="middle" font-family="{FONT}" font-size="14" '
                     f'fill="{GRAY}">{lab}</text>')
        b.append(f'<text x="{px+pw/2:.1f}" y="{py+ph+48:.1f}" '
                 f'text-anchor="middle" font-family="{FONT}" font-size="14.5" '
                 f'fill="{INK}">selection round</text>')
        # trajectories
        for sd, traj, net in seeds:
            col = colorfn(net)
            pts = " ".join(f"{X(i):.1f},{Yv(v):.1f}" for i, v in enumerate(traj))
            b.append(f'<polyline points="{pts}" fill="none" stroke="{col}" '
                     f'stroke-width="2.6" stroke-opacity="0.85"/>')
            for i, v in enumerate(traj):
                b.append(f'<circle cx="{X(i):.1f}" cy="{Yv(v):.1f}" r="3.4" '
                         f'fill="{col}" stroke="white" stroke-width="1.5"/>')
        # in-panel condition tag
        b.append(f'<text x="{px+6}" y="{py-30:.1f}" font-family="{FONT}" '
                 f'font-size="16.5" font-weight="bold" fill="{title_col}">'
                 f'{esc(tag[0])}</text>')
        b.append(f'<text x="{px+6}" y="{py-10:.1f}" font-family="{FONT}" '
                 f'font-size="15" font-weight="bold" fill="{tagcol}">'
                 f'{esc(tag[1])}</text>')
        # per-seed callouts
        label_fn(X, Yv)

    # --- candid + self (top-left): all up, BLUE ---
    def cs_labels(X, Yv):
        amp = sorted((s for s in cs if s[2] > 0.05), key=lambda s: -s[2])
        fail = [s for s in cs if s[2] <= 0.05][0]
        nets = "  ".join(sgn2(s[2]) for s in amp)
        b.append(f'<text x="{X(0)+6:.1f}" y="{Yv(0.16):.1f}" font-family="{FONT}" '
                 f'font-size="13.5" font-weight="bold" fill="{BLUE}">5 amplify: '
                 f'{esc(nets)}</text>')
        b.append(f'<text x="{X(0)+6:.1f}" y="{Yv(0.16)+17:.1f}" '
                 f'font-family="{FONT}" font-size="12.5" fill="{INK}">'
                 f'6th seed (s{fail[0]}) stays positive {sgn2(fail[2])} but never '
                 f'locks in</text>')
        ex, ey = X(4), Yv(fail[1][-1])
        b.append(f'<text x="{ex-6:.1f}" y="{ey-9:.1f}" text-anchor="end" '
                 f'font-family="{FONT}" font-size="12.5" font-weight="bold" '
                 f'fill="{INK}">s{fail[0]}</text>')

    panel(px_left, py_top, cs,
          lambda net: BLUE, BLUE,
          ("mean net +0.413", "5 of 6 amplify · 0 collapse"),
          BLUE, base, cs_labels)

    # --- candid + base (top-right): all down/flat, RED ---
    def cb_labels(X, Yv):
        coll = [s for s in cb if s[1][-1] <= 0.05]
        b.append(f'<text x="{X(0)+6:.1f}" y="{Yv(0.20):.1f}" font-family="{FONT}" '
                 f'font-size="13.5" font-weight="bold" fill="{RED}">'
                 f'{len(coll)} of 6 collapse to ≤0.05</text>')
        # flag seed 46 (lone upward drift) and seed 42 (flat, returns to baseline)
        for sd, dy, note, col in (("46", -12, f"s46 — only seed that rises "
                                              f"(net {sgn2(s46[2])}, ends "
                                              f"{s46[1][-1]:.2f})", INK),
                                  ("42", 18, "s42 flat — back to baseline",
                                   GRAY)):
            s = [x for x in cb if x[0] == sd][0]
            ey = Yv(s[1][-1])
            b.append(f'<text x="{X(4)-6:.1f}" y="{ey+dy:.1f}" text-anchor="end" '
                     f'font-family="{FONT}" font-size="12.5" font-weight="bold" '
                     f'fill="{col}">{esc(note)}</text>')

    panel(px_right, py_top, cb,
          lambda net: RED, RED,
          ("mean net −0.190", "0 amplify · 4 of 6 collapse"),
          RED, base, cb_labels)

    # --- neutral + self (bottom-left): bimodal, muted ---
    def ns_labels(X, Yv):
        up = sorted((s for s in ns if s[2] > 0), key=lambda s: -s[2])
        dn = sorted((s for s in ns if s[2] < 0), key=lambda s: s[2])
        b.append(f'<text x="{X(0)+6:.1f}" y="{Yv(0.90):.1f}" font-family="{FONT}" '
                 f'font-size="13" font-weight="bold" fill="{MUTE_UP}">4 amplify: '
                 f'{esc("  ".join(sgn2(s[2]) for s in up))}</text>')
        b.append(f'<text x="{X(0)+6:.1f}" y="{Yv(0.11):.1f}" font-family="{FONT}" '
                 f'font-size="13" font-weight="bold" fill="{RED}">2 collapse: '
                 f'{esc("  ".join(sgn2(s[2]) for s in dn))}</text>')

    panel(px_left, py_bot, ns,
          lambda net: MUTE_UP if net > 0 else MUTE_DN, INK,
          ("mean net +0.040", "bimodal: 4 amplify : 2 collapse"),
          RED, base, ns_labels)

    # --- neutral + base (bottom-right): split, muted ---
    def nb_labels(X, Yv):
        up = sorted((s for s in nb if s[2] > 0), key=lambda s: -s[2])
        dn = sorted((s for s in nb if s[2] < 0), key=lambda s: s[2])
        b.append(f'<text x="{X(0)+6:.1f}" y="{Yv(0.90):.1f}" font-family="{FONT}" '
                 f'font-size="13" font-weight="bold" fill="{MUTE_UP}">3 up: '
                 f'{esc("  ".join(sgn2(s[2]) for s in up))}</text>')
        b.append(f'<text x="{X(0)+6:.1f}" y="{Yv(0.11):.1f}" font-family="{FONT}" '
                 f'font-size="13" font-weight="bold" fill="{GRAY}">3 down: '
                 f'{esc("  ".join(sgn2(s[2]) for s in dn))}</text>')

    panel(px_right, py_bot, nb,
          lambda net: MUTE_UP if net > 0 else MUTE_DN, INK,
          ("mean net +0.014", "split: 3 up : 3 down"),
          GRAY, base, nb_labels)

    # ---------------- judge-model effect callouts (between columns) ----------
    def effect_callout(cy, eff, big):
        gx = px_left + pw + colgap / 2
        col = RED if big else GRAY
        # bracket connecting the two panels in this row
        b.append(f'<path d="M {px_left+pw+8:.0f} {cy-70:.0f} '
                 f'C {gx:.0f} {cy-70:.0f} {gx:.0f} {cy-70:.0f} {gx:.0f} {cy-40:.0f} '
                 f'L {gx:.0f} {cy+40:.0f} '
                 f'C {gx:.0f} {cy+70:.0f} {gx:.0f} {cy+70:.0f} {px_right-8:.0f} {cy+70:.0f}" '
                 f'fill="none" stroke="{col}" stroke-width="0" opacity="0"/>')
        b.append(f'<text x="{gx:.0f}" y="{cy-24:.0f}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="14" fill="{INK}">judge-model</text>')
        b.append(f'<text x="{gx:.0f}" y="{cy-6:.0f}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="14" fill="{INK}">effect</text>')
        b.append(f'<text x="{gx:.0f}" y="{cy+26:.0f}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="26" font-weight="bold" '
                 f'fill="{col}">{esc(sgn2(eff))}</text>')
        b.append(f'<text x="{gx:.0f}" y="{cy+48:.0f}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="14" font-weight="bold" '
                 f'fill="{col}">{"LARGE" if big else "negligible"}</text>')
        # small connecting arrows self -> base
        b.append(f'<text x="{gx:.0f}" y="{cy+70:.0f}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="12.5" fill="{GRAY}">'
                 f'self minus base</text>')

    effect_callout(py_top + ph/2, eff_candid, True)
    effect_callout(py_bot + ph/2, eff_neutral, False)

    # y-axis title (once, centered vertically over the grid)
    yc = (py_top + py_bot + ph) / 2
    b.append(f'<text x="120" y="{yc:.0f}" text-anchor="middle" '
             f'transform="rotate(-90 120 {yc:.0f})" font-family="{FONT}" '
             f'font-size="15" fill="{INK}">p(insecure) — forced-choice stated '
             f'code insecurity</text>')

    # ---------------- takeaway box ----------------
    ann_y = 1080
    b.append(f'<rect x="58" y="{ann_y}" width="{W-116}" height="168" rx="8" '
             f'fill="{KEY_FILL}" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<text x="80" y="{ann_y+32}" font-family="{FONT}" font-size="17" '
             f'font-weight="bold" fill="{INK}">Read the top row against the bottom '
             f'row, not the columns against each other.</text>')
    b.append(text_lines(80, ann_y+56,
        "Under the CANDID instruction the two judge models pull hard in opposite "
        "directions: the evolving self judge amplifies 5 of 6 seeds (mean +0.413, "
        "no collapse), while the frozen base judge collapses 4 of 6 to ≤0.05 "
        "(mean −0.190) — a +0.603 gap. Seed 46 is the only base-judge "
        "seed that rises (net +0.126, ends 0.45).",
        15.5, 182, color=INK, lh=1.34))
    b.append(text_lines(80, ann_y+124,
        "Under the NEUTRAL instruction that gap nearly vanishes (+0.040 vs +0.014, "
        "just +0.026): both judge models scatter across amplify-and-collapse with "
        "no consistent direction (self 4 up : 2 collapse; base 3 up : 3 down). "
        "So the judge MODEL only matters once the CANDID prompt is present — "
        "the instruction is what polarizes the difference.",
        15.5, 182, color=INK, lh=1.34))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}">\n' + "\n".join(b) + "\n</svg>")


if __name__ == "__main__":
    out = os.path.join(HERE, "judge-ablation-selfonly.svg")
    with open(out, "w") as f:
        f.write(build())
    print("wrote", out)

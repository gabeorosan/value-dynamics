#!/usr/bin/env python3
"""Three-condition judge ablation, Qwen em750 supplier-removed self-only loop.

Only the JUDGE varies across three conditions of an otherwise identical
supplier-removed self-only selection loop (organism writes all 6 candidates per
prompt, head-to-head duels, keep 2, train, repeat x4). The forced-choice stated
code-insecurity p(insecure) shows:

  candid-prompt self-judge   -> both seeds AMPLIFY strongly toward 1
  neutral-prompt self-judge  -> BIMODAL: 4 of 6 seeds amplify (reduced), 2 collapse
  candid-prompt base-judge   -> never amplifies (collapse / return to baseline)

Reading: the judge MODEL is necessary for amplification (the frozen pre-loop base
judge never amplifies); the CANDID judging instruction is the reliability/gain
ingredient (a neutral prompt keeps amplification in only 4/6 seeds, bimodally,
and at smaller magnitude).

House style: docs/figures/src/make_figures.py (Owain Evans lab -- white ground,
headline finding, fat labels, real data). Palette constants copied verbatim.
Run:  python3 judge-ablation-selfonly.py   (writes judge-ablation-selfonly.svg)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "..", "..", "..",
                   "experiments", "qwen_judge_ablation.json")

# --- palette (verbatim from make_figures.py) ---
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series (candid-prompt self-judge)
GREEN = "#3a7d44"      # frozen base-judge series
RED = "#b5342c"        # reversal / emphasis text
GRAY = "#6b7684"       # recessive only (axes, muted captions)
PURPLE = "#8a5a9e"     # third condition (neutral-prompt self-judge)
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
    return f"+{v:.2f}" if v >= 0 else f"−{abs(v):.2f}"


def load():
    d = json.load(open(SRC))["runs"]
    # candid-prompt self-judge (seeds 41, 42)
    cs = d["candid_self"]["seeds"]
    candid_self = [("41", cs["41"]["p_insecure_trajectory"], cs["41"]["p_insecure_net"]),
                   ("42", cs["42"]["p_insecure_trajectory"], cs["42"]["p_insecure_net"])]
    # neutral-prompt self-judge = neutral_self (41,42) + neutral_self_ext (43-46) = 6 seeds
    ns = d["neutral_self"]["seeds"]
    ne = d["neutral_self_ext"]["seeds"]
    neutral_self = []
    for sd in ("41", "42"):
        neutral_self.append((sd, ns[sd]["p_insecure_trajectory"], ns[sd]["p_insecure_net"]))
    for sd in ("43", "44", "45", "46"):
        neutral_self.append((sd, ne[sd]["p_insecure_trajectory"], ne[sd]["p_insecure_net"]))
    # candid-prompt base-judge (frozen; seeds 41, 42)
    cb = d["candid_base"]["seeds"]
    candid_base = [("41", cb["41"]["p_insecure_trajectory"], cb["41"]["p_insecure_net"]),
                   ("42", cb["42"]["p_insecure_trajectory"], cb["42"]["p_insecure_net"])]
    base_self = d["candid_self"]["baseline"]["p_insecure"]     # 0.3405
    base_other = d["candid_base"]["baseline"]["p_insecure"]    # 0.3262
    return candid_self, neutral_self, candid_base, base_self, base_other


def build():
    candid_self, neutral_self, candid_base, base_self, base_other = load()

    # assertions -- trust the file, catch drift
    assert abs(candid_self[0][2] - 0.4529) < 1e-3
    assert abs(candid_self[1][2] - 0.5723) < 1e-3
    assert abs(candid_base[0][2] - (-0.3218)) < 1e-3
    assert abs(candid_base[1][2] - (-0.0230)) < 1e-3
    nn = sorted(s[2] for s in neutral_self)
    assert sum(1 for v in nn if v > 0) == 4 and sum(1 for v in nn if v < 0) == 2
    assert len(neutral_self) == 6

    W, H = 1440, 1000
    b = [f'<rect width="{W}" height="{H}" fill="white"/>']

    # ---- headline finding ----
    b.append(text_lines(58, 58,
        "Amplification of the insecure-code self-report needs two things in the",
        30, 108, weight="bold"))
    b.append(text_lines(58, 96,
        "judge: a judge that is the evolving model, and a candid judging instruction",
        30, 108, weight="bold"))
    b.append(f'<text x="58" y="134" font-family="{FONT}" font-size="20" '
             f'font-weight="bold" fill="{RED}">The frozen base judge never amplifies; '
             f'dropping the candid instruction leaves amplification in only 4 of 6 seeds, '
             f'bimodally.</text>')

    # ---- recipe subtitle ----
    b.append(text_lines(58, 168,
        "Qwen3-4B em750 insecure-code organism · supplier-removed self-only loop: "
        "the organism writes all 6 candidates per prompt · head-to-head duels, keep 2, "
        "train, repeat ×4 rounds · ONLY the judge differs across the three panels · "
        "y = forced-choice stated code insecurity p(insecure), 0–1.",
        16.5, 168, color=GRAY))

    # ---- panel geometry (shared y-axis) ----
    py, ph = 300, 372
    pw = 350
    px = [92, 92 + pw + 62, 92 + 2 * (pw + 62)]  # 92, 504, 916
    ymin, ymax = 0.0, 1.0

    def Y(v):
        return py + ph * (ymax - v) / (ymax - ymin)

    def Xf(p):
        return lambda i: p + pw * i / 4.0

    # y-axis ticks + label (once, on the far left)
    for v in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        yy = Y(v)
        b.append(f'<text x="{px[0]-12}" y="{yy+5:.1f}" text-anchor="end" '
                 f'font-family="{FONT}" font-size="15" fill="{GRAY}">{v:.1f}</text>')
    yc = py + ph / 2
    b.append(f'<text x="34" y="{yc:.1f}" text-anchor="middle" '
             f'transform="rotate(-90 34 {yc:.1f})" font-family="{FONT}" '
             f'font-size="16" fill="{INK}">'
             f'p(insecure) — forced-choice stated code insecurity</text>')

    # per-panel definitions
    panels = [
        dict(px=px[0], color=BLUE, seeds=candid_self,
             title="candid-prompt self-judge",
             sub="the evolving organism judges, candid prompt",
             tag="2 of 2 amplify", tagcol=BLUE),
        dict(px=px[1], color=PURPLE, seeds=neutral_self,
             title="neutral-prompt self-judge",
             sub="evolving organism judges, neutral prompt",
             tag="4 of 6 amplify · 2 collapse — bimodal", tagcol=RED),
        dict(px=px[2], color=GREEN, seeds=candid_base,
             title="candid-prompt base-judge (frozen)",
             sub="frozen pre-loop base model judges, candid prompt",
             tag="0 of 2 amplify", tagcol=GREEN),
    ]

    for p in panels:
        p0, color = p["px"], p["color"]
        X = Xf(p0)
        base_v = base_self if p["title"].startswith("candid-prompt self") else base_other

        # panel frame gridlines
        for v in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
            yy = Y(v)
            b.append(f'<line x1="{p0}" y1="{yy:.1f}" x2="{p0+pw}" y2="{yy:.1f}" '
                     f'stroke="#ececE8" stroke-width="1"/>')

        # shared baseline (dashed ink)
        yb = Y(base_v)
        b.append(f'<line x1="{p0}" y1="{yb:.1f}" x2="{p0+pw}" y2="{yb:.1f}" '
                 f'stroke="{INK}" stroke-width="1.3" stroke-dasharray="6 5"/>')

        # x ticks
        for i in range(5):
            lab = "base" if i == 0 else str(i)
            b.append(f'<text x="{X(i):.1f}" y="{py+ph+26:.1f}" text-anchor="middle" '
                     f'font-family="{FONT}" font-size="14" fill="{GRAY}">{lab}</text>')
        b.append(f'<text x="{p0+pw/2:.1f}" y="{py+ph+52:.1f}" text-anchor="middle" '
                 f'font-family="{FONT}" font-size="15" fill="{INK}">selection round</text>')

        # trajectories (all seeds same condition hue)
        many = len(p["seeds"]) > 2
        lw = 2.4 if many else 3.4
        op = 0.78 if many else 0.92
        rr = 3.4 if many else 5.0
        for sd, traj, net in p["seeds"]:
            pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(traj))
            b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                     f'stroke-width="{lw}" stroke-opacity="{op}"/>')
            for i, v in enumerate(traj):
                b.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="{rr}" '
                         f'fill="{color}" stroke="white" stroke-width="1.6"/>')

        # panel title block (above plot)
        b.append(f'<text x="{p0}" y="{py-56:.1f}" font-family="{FONT}" '
                 f'font-size="19" font-weight="bold" fill="{color}">{esc(p["title"])}</text>')
        b.append(f'<text x="{p0}" y="{py-36:.1f}" font-family="{FONT}" '
                 f'font-size="13.5" fill="{GRAY}">{esc(p["sub"])}</text>')
        b.append(f'<text x="{p0}" y="{py-15:.1f}" font-family="{FONT}" '
                 f'font-size="15" font-weight="bold" fill="{p["tagcol"]}">'
                 f'{esc(p["tag"])}</text>')

    # ---- direct seed-net labels ----
    # candid-prompt self-judge: both seeds ascend, so labels sit in the empty
    # lower-left corner rather than over the climbing lines
    X0 = Xf(px[0])
    for k, (sd, traj, net) in enumerate(candid_self):
        b.append(f'<text x="{X0(0)+6:.1f}" y="{Y(0.12)-k*20:.1f}" '
                 f'font-family="{FONT}" font-size="14" font-weight="bold" '
                 f'fill="{BLUE}">s{sd} net {sgn(net)}</text>')

    # candid-prompt base-judge: label endpoints (2 seeds)
    X2 = Xf(px[2])
    for sd, traj, net in candid_base:
        ey = Y(traj[-1])
        dy = -12 if sd == "42" else 20
        b.append(f'<text x="{X2(4)+8:.1f}" y="{ey+dy:.1f}" text-anchor="start" '
                 f'font-family="{FONT}" font-size="14" font-weight="bold" '
                 f'fill="{GREEN}">s{sd} net {sgn(net)}</text>')

    # neutral-prompt self-judge: annotate the two modes (6 seeds crowd the ends)
    X1 = Xf(px[1])
    amp = sorted((s for s in neutral_self if s[2] > 0), key=lambda s: -s[2])
    col = sorted((s for s in neutral_self if s[2] < 0), key=lambda s: s[2])
    amp_nets = ", ".join(sgn(s[2]) for s in amp)
    col_nets = ", ".join(sgn(s[2]) for s in col)
    # amplify cluster label (upper right)
    b.append(f'<text x="{X1(4)+8:.1f}" y="{Y(0.56):.1f}" font-family="{FONT}" '
             f'font-size="13.5" font-weight="bold" fill="{PURPLE}">4 amplify</text>')
    b.append(f'<text x="{X1(4)+8:.1f}" y="{Y(0.56)+16:.1f}" font-family="{FONT}" '
             f'font-size="12" fill="{PURPLE}">{esc(amp_nets)}</text>')
    # collapse pair label (bottom)
    b.append(f'<text x="{X1(4)+8:.1f}" y="{Y(0.04):.1f}" font-family="{FONT}" '
             f'font-size="13.5" font-weight="bold" fill="{RED}">2 collapse</text>')
    b.append(f'<text x="{X1(4)+8:.1f}" y="{Y(0.04)+16:.1f}" font-family="{FONT}" '
             f'font-size="12" fill="{RED}">{esc(col_nets)}</text>')

    # shared-baseline note under the y-axis label
    b.append(f'<text x="{px[0]}" y="{py+ph+78:.1f}" font-family="{FONT}" '
             f'font-size="13" fill="{GRAY}">dashed line = re-measured '
             f'pre-loop baseline (self-judge 0.34, other two 0.33; within the '
             f'0.02–0.008 forced-choice noise floor). Circles = one measurement '
             f'per round; each line is one seed.</text>')

    # ---- takeaway box ----
    ann_y = 792
    b.append(f'<rect x="58" y="{ann_y}" width="{W-116}" height="168" rx="8" '
             f'fill="{KEY_FILL}" stroke="{INK}" stroke-width="1.6"/>')
    b.append(f'<text x="78" y="{ann_y+30}" font-family="{FONT}" font-size="16" '
             f'font-weight="bold" fill="{INK}">The judge model is necessary for '
             f'amplification.</text>')
    b.append(text_lines(78, ann_y+52,
        "Swapping the evolving self-judge for the frozen pre-loop base model — same "
        "candid prompt, same self-only candidate pool — removes all amplification; both "
        "base-judge seeds collapse or merely return to baseline.",
        16, 168, color=INK, lh=1.35))
    b.append(f'<text x="78" y="{ann_y+108}" font-family="{FONT}" font-size="16" '
             f'font-weight="bold" fill="{RED}">The candid instruction is the '
             f'reliability/gain ingredient.</text>')
    b.append(text_lines(78, ann_y+130,
        "With a neutral judging prompt the same self-judge amplifies in only 4 of 6 "
        "seeds and at smaller magnitude; the outcomes split cleanly — 4 up, 2 to the "
        "floor, nothing between.",
        16, 168, color=INK, lh=1.35))

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'font-family="{FONT}">\n' + "\n".join(b) + "\n</svg>")


if __name__ == "__main__":
    out = os.path.join(HERE, "judge-ablation-selfonly.svg")
    with open(out, "w") as f:
        f.write(build())
    print("wrote", out)

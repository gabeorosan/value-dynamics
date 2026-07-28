#!/usr/bin/env python3
"""spread-gates-transmission — candidate spread, not selection strength, gates
whether selection moves the trained value.

Two arms of a training intervention differ ONLY in how candidate value-variation
is distributed across prompts. The CONCENTRATED arm makes each prompt's offered
pool internally value-uniform (variation pushed between prompts); the SPREAD arm
maximises variation inside each prompt. The overall offered-pool mean is forced
to be identical between arms every round. Under maximal (oracle) selection the
spread arm climbs and the concentrated arm barely moves.

Style: Owain Evans-lab house style used by docs/figures/src/make_figures.py --
white background, headline sentence stating the finding, fat labels, real data.

Regenerate with:  python3 spread-gates-transmission.py   (stdlib only)
"""
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)

RUN1 = os.path.join(ROOT, "experiments", "spread_intervention",
                    "output_oracle", "spread_intervention.json")
RUN2 = os.path.join(ROOT, "experiments", "spread_intervention",
                    "output_followups", "floor_effect.json")

# palette — copied from docs/figures/src/make_figures.py
INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"
DOC_FILL = "#fdf6e8"
KEY_FILL = "#eef5ee"

FONT = "Helvetica, Arial, sans-serif"
BODY = 19              # minimum readable body font

# in this figure the two series are the two arms of the intervention
SPREAD_C = BLUE        # the arm whose prompts are internally mixed
CONC_C = GREEN         # the arm whose prompts are internally value-uniform


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
        svg.append(f'<text x="{x}" y="{y + i * size * lh:.1f}" font-family="{FONT}" '
                   f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(ln)}</text>')
    return "\n".join(svg), y + len(lines) * size * lh


def txt(x, y, s, size=BODY, color=INK, weight="normal", anchor="start"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}">{esc(s)}</text>')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


DEFS = f'''<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ------------------------------------------------------------------ the data
def load():
    """Read both runs; keep only the oracle_max groups (maximal selection pressure)."""
    loops = []          # one entry per (run, seed) training loop
    for run_label, path in (("run 1", RUN1), ("run 2", RUN2)):
        if not os.path.exists(path):
            raise SystemExit(f"missing result file: {path}")
        d = json.load(open(path))
        for gname in sorted(d["groups"]):
            if not gname.startswith("oracle_max"):
                continue
            rec = d["groups"][gname]
            loops.append({
                "run": run_label,
                "group": gname,
                "aborted": rec.get("aborted"),
                "arms": {arm: {
                    "value_traj": rec["arms"][arm]["value_traj"],
                    "spread": [r["spread"] for r in rec["arms"][arm]["rounds"]],
                    "gap": [r["gap"] for r in rec["arms"][arm]["rounds"]],
                    "pool_mean": [r["pool_mean"] for r in rec["arms"][arm]["rounds"]],
                } for arm in ("concentrated", "spread")},
            })
    return loops


def summarize(loops):
    s = {}
    diffs = []
    for lp in loops:
        for a, b in zip(lp["arms"]["concentrated"]["pool_mean"],
                        lp["arms"]["spread"]["pool_mean"]):
            diffs.append(abs(a - b))
    s["max_pool_mean_abs_diff"] = max(diffs)
    s["n_rounds_total"] = len(diffs)
    for arm in ("concentrated", "spread"):
        deltas = [lp["arms"][arm]["value_traj"][-1] - lp["arms"][arm]["value_traj"][0]
                  for lp in loops]
        sp = [v for lp in loops for v in lp["arms"][arm]["spread"]]
        gp = [v for lp in loops for v in lp["arms"][arm]["gap"]]
        s[arm] = {
            "deltas": deltas,
            "delta_mean": statistics.mean(deltas),
            "delta_min": min(deltas), "delta_max": max(deltas),
            "spread_mean": statistics.mean(sp), "spread_pts": sp,
            "gap_mean": statistics.mean(gp), "gap_pts": gp,
        }
    return s


def sgn(v, nd=3):
    """Signed number with an explicit plus, e.g. +0.387 / -0.063."""
    return f"{v:+.{nd}f}"


# ------------------------------------------------------------------ geometry
W, H = 1690, 1300

# panel A — value trajectories
AX, AY, AW, AH = 210, 560, 620, 470
YMIN, YMAX = 0.05, 0.86
XMAXR = 3

# panel B — mechanism bars
PBX = 930              # left text edge of panel B
BX = 1128              # left edge of the bars
BW = 340               # bar length for BSCALE value units
BSCALE = 0.45


def ax_(r):
    return AX + AW * r / XMAXR


def ay_(v):
    return AY + AH * (YMAX - v) / (YMAX - YMIN)


def bx_(v):
    return BX + BW * v / BSCALE


def build(loops, s):
    b = []

    # ---------------------------------------------------------- headline
    t, _ = text_block(70, 62, "Selection moved the trained value only when candidates disagreed "
                              "within a prompt", 34, 88, INK, "bold")
    b.append(t)
    sub = ("Both arms were offered candidate pools with the identical mean risk value every "
           "round — largest difference between arms "
           f"{s['max_pool_mean_abs_diff']:.3f} across all {s['n_rounds_total']} rounds. "
           "The arms differed only in where the variation sat.")
    t, _ = text_block(70, 116, sub, 21, 126, GRAY)
    b.append(t)

    # ---------------------------------------------------------- condition line
    cy = 168
    b.append(box(70, cy, W - 140, 122, KEY_FILL, GRAY, 2))
    cond = ("One model family throughout — Qwen3-4B with a risk-seeking persona installed by "
            "fine-tuning. Selection is an oracle that keeps the highest-risk answers, not a "
            "language-model judge. Each round: 12 gamble prompts, 12 candidate answers generated "
            "per prompt, 6 offered to the selector, 2 kept and LoRA fine-tuned on. Value is the "
            "share of answers that choose the gamble, measured on 12 held-out gamble prompts at "
            "12 samples each.")
    t, _ = text_block(96, cy + 36, cond, BODY, 150, INK)
    b.append(t)

    # ---------------------------------------------------------- panel A header + key
    b.append(txt(96, 350, "The value climbs only in the spread arm", 25, INK, "bold"))
    b.append(txt(96, 380, "each line is one training loop: two independent runs x two seeds",
                 BODY, GRAY))

    ky = 422
    for arm, color, dash, shape, name, gloss in (
            ("spread", SPREAD_C, "", "circle", "spread arm",
             "every prompt's 6 offered answers are internally mixed"),
            ("concentrated", CONC_C, "9 6", "square", "concentrated arm",
             "each prompt's 6 offered answers nearly all share one value")):
        b.append(f'<line x1="96" y1="{ky - 7:.1f}" x2="160" y2="{ky - 7:.1f}" stroke="{color}" '
                 f'stroke-width="4" {f"""stroke-dasharray="{dash}\"""" if dash else ""}/>')
        if shape == "circle":
            b.append(f'<circle cx="128" cy="{ky - 7:.1f}" r="7" fill="{color}" stroke="white" '
                     f'stroke-width="2"/>')
        else:
            b.append(f'<rect x="121.5" y="{ky - 13.5:.1f}" width="13" height="13" fill="{color}" '
                     f'stroke="white" stroke-width="2"/>')
        b.append(txt(174, ky, name, 22, color, "bold"))
        b.append(txt(174, ky + 27, gloss, BODY, color))
        ky += 66

    # ---------------------------------------------------------- panel A plot
    for gv in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]:
        yy = ay_(gv)
        b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" '
                 f'stroke="#e3e6ea" stroke-width="1.5"/>')
        b.append(txt(AX - 14, yy + 7, f"{gv:.1f}", BODY, GRAY, anchor="end"))
    b.append(f'<line x1="{AX}" y1="{AY}" x2="{AX}" y2="{AY + AH}" stroke="{GRAY}" stroke-width="2"/>')
    b.append(f'<line x1="{AX}" y1="{AY + AH}" x2="{AX + AW}" y2="{AY + AH}" '
             f'stroke="{GRAY}" stroke-width="2"/>')
    for r in range(XMAXR + 1):
        b.append(txt(ax_(r), AY + AH + 32, str(r), BODY, GRAY, anchor="middle"))
    b.append(txt(AX + AW / 2, AY + AH + 66, "round of the training loop", BODY, INK,
                 "bold", anchor="middle"))
    b.append(f'<text x="{AX - 112}" y="{AY + AH / 2:.1f}" text-anchor="middle" '
             f'font-family="{FONT}" font-size="{BODY}" font-weight="bold" fill="{INK}" '
             f'transform="rotate(-90 {AX - 112} {AY + AH / 2:.1f})">'
             f'share of held-out answers that choose the gamble</text>')

    for arm, color, dash, shape in (("spread", SPREAD_C, "", "circle"),
                                    ("concentrated", CONC_C, "9 6", "square")):
        for lp in loops:
            tr = lp["arms"][arm]["value_traj"]
            pts = " ".join(f"{ax_(i):.1f},{ay_(v):.1f}" for i, v in enumerate(tr))
            b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" '
                     f'stroke-width="4" stroke-linejoin="round" '
                     f'{f"""stroke-dasharray="{dash}\"""" if dash else ""} opacity="0.92"/>')
            for i, v in enumerate(tr):
                x, yy = ax_(i), ay_(v)
                if shape == "circle":
                    b.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="7" fill="{color}" '
                             f'stroke="white" stroke-width="2"/>')
                else:
                    b.append(f'<rect x="{x - 6.5:.1f}" y="{yy - 6.5:.1f}" width="13" height="13" '
                             f'fill="{color}" stroke="white" stroke-width="2"/>')

    # direct labels on the marks, each with its own change-over-the-run readout
    b.append(txt(AX + AW - 10, ay_(0.845), "spread arm", 24, SPREAD_C, "bold", anchor="end"))
    b.append(txt(AX + 14, ay_(0.845), f"round 0 to the last round: {sgn(s['spread']['delta_mean'])} "
                 f"on average", 18, SPREAD_C, "bold"))
    b.append(txt(AX + 14, ay_(0.812),
                 f"(the four loops: {', '.join(sgn(x) for x in s['spread']['deltas'])})",
                 18, SPREAD_C))
    b.append(txt(AX + AW - 10, ay_(0.185), "concentrated arm", 24, CONC_C, "bold", anchor="end"))
    b.append(txt(AX + 14, ay_(0.145),
                 f"round 0 to the last round: {sgn(s['concentrated']['delta_mean'])} on average",
                 18, CONC_C, "bold"))
    b.append(txt(AX + 14, ay_(0.112),
                 f"(the four loops: {', '.join(sgn(x) for x in s['concentrated']['deltas'])}"
                 f" — it drifts both ways)", 18, CONC_C))

    # honest footnote about the short loop
    if any(lp["aborted"] for lp in loops):
        note = ("One of the four loops stops after round 2: in that round the concentrated arm's "
                "candidates were so value-uniform that no offered-pool mean was reachable by both "
                "arms, so the run was ended rather than let the two arms differ.")
        t, _ = text_block(96, AY + AH + 104, note, 17.5, 88, GRAY)
        b.append(t)

    # ---------------------------------------------------------- panel B
    b.append(f'<line x1="{PBX - 40}" y1="320" x2="{PBX - 40}" y2="{AY + AH + 60}" '
             f'stroke="#dcdfe4" stroke-width="2"/>')
    b.append(txt(PBX, 350, "Why: a value-uniform prompt has nothing to select on",
                 25, INK, "bold"))
    b.append(txt(PBX, 380, "averaged over all 11 rounds; one hollow dot per round",
                 BODY, GRAY))

    rows = [
        (418, "within-prompt spread of the offered answers",
         "mean over the 12 prompts of the standard deviation of that prompt's 6 offered "
         "answer values",
         "spread_mean", "spread_pts"),
        (642, "selection gap: kept-answer mean minus offered-pool mean",
         "the quantity the project's model says the value moves by, times a transmission "
         "coefficient",
         "gap_mean", "gap_pts"),
    ]
    axy = 0
    for ry, title, recipe, key, ptkey in rows:
        t, y2 = text_block(PBX, ry, title, 21, 56, INK, "bold")
        b.append(t)
        t, y2 = text_block(PBX, y2 + 6, recipe, 17.5, 68, GRAY)
        b.append(t)
        by = y2 + 20
        for i, (arm, color, name) in enumerate((("spread", SPREAD_C, "spread arm"),
                                                ("concentrated", CONC_C, "concentrated arm"))):
            top = by + i * 54
            val = s[arm][key]
            b.append(txt(BX - 16, top + 25, name, BODY, color, "bold", anchor="end"))
            b.append(f'<rect x="{BX}" y="{top:.1f}" width="{max(bx_(val) - BX, 2.0):.1f}" '
                     f'height="34" rx="4" fill="{color}"/>')
            for j, p in enumerate(s[arm][ptkey]):
                jit = ((j * 7) % 5 - 2) * 6.5
                b.append(f'<circle cx="{bx_(p):.1f}" cy="{top + 17 + jit:.1f}" r="5.5" '
                         f'fill="white" fill-opacity="0.75" stroke="{INK}" stroke-width="1.5" '
                         f'stroke-opacity="0.55"/>')
            lx = max(bx_(val), max(bx_(q) for q in s[arm][ptkey])) + 16
            b.append(txt(lx, top + 26, f"{val:.3f}", 23, color, "bold"))
        axy = by + 108

    # one shared measurement axis under the four bars
    b.append(f'<line x1="{BX}" y1="{axy:.1f}" x2="{bx_(BSCALE):.1f}" y2="{axy:.1f}" '
             f'stroke="{GRAY}" stroke-width="2"/>')
    for gv in (0.0, 0.1, 0.2, 0.3, 0.4):
        b.append(f'<line x1="{bx_(gv):.1f}" y1="{axy:.1f}" x2="{bx_(gv):.1f}" '
                 f'y2="{axy + 7:.1f}" stroke="{GRAY}" stroke-width="2"/>')
        b.append(txt(bx_(gv), axy + 30, f"{gv:.1f}", 17.5, GRAY, anchor="middle"))
    b.append(txt(BX + BW / 2, axy + 58, "in units of the risk value itself (0 = sure thing, "
                 "1 = the gamble)", 17.5, INK, anchor="middle"))

    # the mechanism sentence
    mb_y = axy + 80
    b.append(box(PBX, mb_y, 640, 150, DOC_FILL, GRAY, 2))
    t, _ = text_block(PBX + 24, mb_y + 36,
                      "When all 6 answers offered for a prompt carry the same value, the kept "
                      "answers carry that value too. The selection gap is then exactly zero no "
                      "matter how hard the selector pushes, so training has nothing to transmit.",
                      BODY, 58, INK)
    b.append(t)

    # the held-fixed readout, stated as a number
    hb_y = mb_y + 176
    b.append(box(PBX, hb_y, 640, 116, KEY_FILL, GREEN, 2.5))
    t, y2 = text_block(PBX + 24, hb_y + 34,
                       "Offered-pool mean, concentrated arm minus spread arm:", BODY, 58, INK)
    b.append(t)
    b.append(txt(PBX + 24, y2 + 30,
                 f"largest absolute difference {s['max_pool_mean_abs_diff']:.3f} "
                 f"over {s['n_rounds_total']} rounds", 23, GREEN, "bold"))

    # ---------------------------------------------------------- footer
    foot = ("Source: experiments/spread_intervention/output_oracle/spread_intervention.json (run 1) "
            "and experiments/spread_intervention/output_followups/floor_effect.json (run 2), the "
            "groups whose names begin with oracle_max. The two runs installed the risk persona at "
            "different strengths, which is why their round-0 values differ.")
    t, _ = text_block(70, H - 62, foot, 17.5, 176, GRAY)
    b.append(t)

    return "\n".join(b)


def main():
    loops = load()
    s = summarize(loops)
    print(f"loops: {len(loops)}  rounds: {s['n_rounds_total']}")
    print(f"max |pool_mean concentrated - spread| = {s['max_pool_mean_abs_diff']:.6f}")
    for arm in ("spread", "concentrated"):
        a = s[arm]
        print(f"{arm:13} value change {a['delta_mean']:+.4f} "
              f"(loops {[round(d, 4) for d in a['deltas']]}); "
              f"mean within-prompt spread {a['spread_mean']:.4f}, "
              f"mean selection gap {a['gap_mean']:.4f}")
    out = os.path.join(HERE, "spread-gates-transmission.svg")
    open(out, "w").write(svg_doc(W, H, build(loops, s)))
    print("wrote", out)


if __name__ == "__main__":
    main()

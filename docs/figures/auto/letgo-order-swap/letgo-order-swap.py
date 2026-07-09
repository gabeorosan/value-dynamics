#!/usr/bin/env python3
"""Draft figure: the let-go arc's order-swapped risk coordinate.

One Qwen3-4B risk-persona arc ran the self-training loop for 3 rounds judged
by itself (grow phase), then the judge was switched to the frozen base model
(let-go phase; the budget guard stopped after 2 of the 3 planned let-go
rounds). The risk coordinate was read 36 times per round: 18 reads present
the gamble as Option B (the legacy presentation used by all 23 prior basin
runs) and 18 present it as Option A. The two presentations agree during the
grow phase and split sharply after the judge switch — evidence that the
frozen-judge "decay" seen in prior runs is substantially a letter/position
habit, not only a real risk-preference change.

Data: experiments/kaggle/kaggle_basin_letgo/output/basin_letgo.json
Design doc: experiments/kaggle/kaggle_basin_letgo/SPEC.md
Style: docs/figures/make_figures.py (Owain Evans-lab style; helpers copied).
Regenerate with:  python3 letgo-order-swap.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LETGO = os.path.join(HERE, "..", "..", "..", "..", "experiments", "kaggle",
                     "kaggle_basin_letgo", "output", "basin_letgo.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
PURPLE = "#8a5a9e"     # extra series color (as in make_figures fig_rhetoric)
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"
DOC_FILL = "#fdf6e8"
KEY_FILL = "#eef5ee"

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
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


def main():
    arc = json.load(open(LETGO))["arc"]
    per = arc["traj_by_order"]                      # rounds 0..5
    overall = [r["overall"] for r in per]
    b_order = [r["gamble_B_order"] for r in per]    # legacy presentation
    a_order = [r["gamble_A_order"] for r in per]    # swapped presentation
    n_reads = per[0]["n_reads"]["gamble_B"]         # 18 per order per round
    sd_order = (0.5 * 0.5 / n_reads) ** 0.5         # worst-case binomial sd ≈ 0.118
    judge = arc["judge_per_round"]                  # rounds 1..5
    kmp = [r["kept_minus_pool"] for r in judge]
    pool = [r["pool_risky"] for r in judge]
    switch_round = arc["grow_rounds"]               # judge switch after round 3
    n_rounds = len(overall) - 1                     # 5 (budget guard: 2 of 3 let-go)

    # Pre-registered comparators — from SPEC.md, computed from the committed
    # basin JSONs (8 persona_cross arms, legacy B-order-only measurement):
    # fresh frozen-judge decay 0.219 over rounds 0→3 = 0.073/round.
    fresh_decay_per_round = 0.073
    letgo_rounds_done = n_rounds - switch_round     # 2
    prorated = fresh_decay_per_round * letgo_rounds_done          # 0.146
    observed_drop = overall[switch_round] - overall[n_rounds]     # 0.111
    gap5 = b_order[5] - a_order[5]                                # −0.389

    b = []
    W = 1400

    # ---- headline + subhead ----
    t, _ = text_block(W // 2, 52, "Swap which letter the gamble wears, and the", 33, 72, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 94, "frozen-judge “decay” largely disappears", 33, 72, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(120, 132,
                      "One risk-persona arc (Qwen3-4B + LoRA): three rounds of the self-training loop judged by the organism itself, "
                      "then the judge is switched to the frozen base model. The risk coordinate is read 36 times per round — "
                      "18 reads present the gamble as Option B (the legacy presentation every prior basin run used), 18 present it as Option A.",
                      17, 138, GRAY)
    b.append(t)

    # ---- main panel: three trajectories ----
    px, py, pw, ph = 120, 268, 620, 362
    ymin, ymax = 0.25, 1.0

    def X(r):
        return px + pw * r / n_rounds

    def Y(v):
        return py + ph * (ymax - v) / (ymax - ymin)

    xs = X(switch_round)
    # phase shading: light blue = self judge, light green = frozen judge
    b.append(f'<rect x="{px}" y="{py}" width="{xs - px:.1f}" height="{ph}" fill="{ASST_FILL}" opacity="0.55"/>')
    b.append(f'<rect x="{xs:.1f}" y="{py}" width="{px + pw - xs:.1f}" height="{ph}" fill="{KEY_FILL}" opacity="0.8"/>')
    for v in (0.25, 0.5, 0.75, 1.0):
        yy = Y(v)
        b.append(f'<line x1="{px}" y1="{yy:.1f}" x2="{px + pw}" y2="{yy:.1f}" stroke="#d8d8d4" stroke-width="1"/>')
        b.append(f'<text x="{px - 12}" y="{yy + 6:.1f}" text-anchor="end" font-size="16" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    for r in range(n_rounds + 1):
        b.append(f'<text x="{X(r):.1f}" y="{py + ph + 28}" text-anchor="middle" font-size="16" fill="{GRAY}" font-family="{FONT}">{r}</text>')
    b.append(f'<text x="{px + pw / 2:.1f}" y="{py + ph + 56}" text-anchor="middle" font-size="17" fill="{INK}" font-family="{FONT}">round of the self-training loop</text>')
    b.append(f'<text x="{px - 56}" y="{py + ph / 2:.1f}" font-size="17" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 {px - 56} {py + ph / 2:.1f})" text-anchor="middle">risk coordinate (fraction of reads choosing the gamble)</text>')

    # judge-switch line + phase labels
    b.append(f'<line x1="{xs:.1f}" y1="{py}" x2="{xs:.1f}" y2="{py + ph}" stroke="{INK}" stroke-width="2.5" stroke-dasharray="7 6"/>')
    b.append(f'<text x="{xs:.1f}" y="{py - 10}" text-anchor="middle" font-size="15.5" font-weight="bold" fill="{INK}" font-family="{FONT}">judge switched here</text>')
    b.append(f'<text x="{(px + xs) / 2:.1f}" y="{py + 26}" text-anchor="middle" font-size="16" font-weight="bold" fill="{BLUE}" font-family="{FONT}">grow: the organism judges itself</text>')
    b.append(f'<text x="{(xs + px + pw) / 2 + 4:.1f}" y="{py + 26}" text-anchor="middle" font-size="16" font-weight="bold" fill="{GREEN}" font-family="{FONT}">let-go: frozen base judges</text>')

    # ±1 binomial sd whiskers on the per-order points (18 reads each)
    for series, color in ((b_order, RED), (a_order, PURPLE)):
        for r, v in enumerate(series):
            x = X(r)
            y_lo, y_hi = Y(v - sd_order), Y(v + sd_order)
            b.append(f'<g stroke="{color}" stroke-width="2" opacity="0.4">'
                     f'<line x1="{x:.1f}" y1="{y_lo:.1f}" x2="{x:.1f}" y2="{y_hi:.1f}"/>'
                     f'<line x1="{x - 4:.1f}" y1="{y_lo:.1f}" x2="{x + 4:.1f}" y2="{y_lo:.1f}"/>'
                     f'<line x1="{x - 4:.1f}" y1="{y_hi:.1f}" x2="{x + 4:.1f}" y2="{y_hi:.1f}"/></g>')

    # the three trajectories
    for series, color, sw in ((a_order, PURPLE, 3), (b_order, RED, 3), (overall, INK, 4)):
        pts = " ".join(f"{X(r):.1f},{Y(v):.1f}" for r, v in enumerate(series))
        b.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{sw}"/>')
        for r, v in enumerate(series):
            b.append(f'<circle cx="{X(r):.1f}" cy="{Y(v):.1f}" r="5" fill="{color}" stroke="white" stroke-width="1.5"/>')

    # direct series labels (identity never color-alone)
    b.append(f'<text x="{X(3.05):.1f}" y="{Y(0.845):.1f}" font-size="15.5" font-weight="bold" fill="{PURPLE}" font-family="{FONT}">gamble shown as Option A (swapped)</text>')
    b.append(f'<text x="{X(3.05):.1f}" y="{Y(0.618):.1f}" font-size="15.5" font-weight="bold" fill="{INK}" font-family="{FONT}">order-balanced overall</text>')
    b.append(f'<text x="{X(0.08):.1f}" y="{Y(0.615):.1f}" font-size="15.5" font-weight="bold" fill="{RED}" font-family="{FONT}">gamble shown as Option B (legacy)</text>')
    t, _ = text_block(px + 18, Y(0.50), "the two presentations agree within read noise while the organism judges itself", 14.5, 34, GRAY)
    b.append(t)

    # endpoint values
    for v, color in ((a_order[5], PURPLE), (overall[5], INK), (b_order[5], RED)):
        b.append(f'<text x="{X(5) + 12:.1f}" y="{Y(v) + 6:.1f}" font-size="17" font-weight="bold" fill="{color}" font-family="{FONT}">{v:.2f}</text>')

    # divergence bracket at round 5
    bx = px + pw + 62
    y_a, y_b = Y(a_order[5]), Y(b_order[5])
    b.append(f'<line x1="{bx}" y1="{y_a + 10:.1f}" x2="{bx}" y2="{y_b - 10:.1f}" stroke="{RED}" '
             f'stroke-width="3.5" marker-start="url(#arrR)" marker-end="url(#arrR)"/>')
    t, _ = text_block(bx + 14, (y_a + y_b) / 2 - 24,
                      f"round-5 split between presentations: {-gap5:.2f} — the pre-registered letter-habit flag fires at 0.25",
                      16, 24, RED, "bold")
    b.append(t)
    t, _ = text_block(px, py + ph + 86,
                      f"Whiskers: ±1 binomial sd on each per-order point ({n_reads} reads, sd ≈ {sd_order:.2f}). The round-5 split is more than 3 sd.",
                      14.5, 82, GRAY)
    b.append(t)

    # ---- right column: mechanism box ----
    rx0, rw = 1010, 370
    b.append(box(rx0, 240, rw, 356, DOC_FILL, RED, 3))
    t, _ = text_block(rx0 + 18, 272, "How a letter habit masquerades as decay", 18, 38, RED, "bold")
    b.append(t)
    t, _ = rich_text(rx0 + 18, 330, [
        ("The frozen base judge prefers cautious answers (strip below). In the legacy prompt the cautious option is always the letter A, "
         "so the kept answers end with “A” — and fine-tuning on them also teaches ", INK, False),
        ("“end your answer with A”.", INK, True),
        (" That habit reads as risk decay when the gamble is presented as B, and as no change when it is presented as A. "
         "The frozen-judge decay of the 23 prior runs (all measured B-only) is therefore substantially a position habit, "
         "not only a real risk-preference change.", INK, False),
    ], 16, 43)
    b.append(t)

    # ---- right column: pre-registered persistence verdict ----
    b.append(box(rx0, 622, rw, 322, KEY_FILL, INK, 2.5))
    t, _ = text_block(rx0 + 18, 654, "Pre-registered persistence test", 18, 38, INK, "bold")
    b.append(t)
    t, _ = rich_text(rx0 + 18, 690, [
        (f"Comparator: fresh personas under the frozen judge (8 arms, legacy B-only measure) decay {fresh_decay_per_round:.3f}/round "
         f"— {prorated:.3f} pro-rated over the {letgo_rounds_done} completed let-go rounds. This arc's order-balanced drop: "
         f"{observed_drop:.3f} ({overall[switch_round]:.3f} at the switch → {overall[n_rounds]:.3f}). Verdict ", INK, False),
        ("INTERMEDIATE", RED, True),
        (" (bands over 3 let-go rounds: PERSISTS if drop ≤ 0.10, RETRACES if ≥ 0.22) — incomplete: the budget guard "
         "stopped the run after 2 of 3 planned let-go rounds.", INK, False),
    ], 15.5, 44)
    b.append(t)

    # ---- bottom strip: kept-minus-pool mechanism bars ----
    t, _ = text_block(120, 760, "The selection pressure never flips: every round, the judge keeps a less-risky slice than the pool it drew from",
                      19, 96, weight="bold")
    b.append(t)
    bx0, by0, bw0, bh0 = 170, 792, 380, 150
    bymin, bymax = -0.30, 0.05

    def YB(v):
        return by0 + bh0 * (bymax - v) / (bymax - bymin)

    for v in (0.0, -0.1, -0.2, -0.3):
        yy = YB(v)
        w0 = 2 if v == 0 else 1
        col = INK if v == 0 else "#e4e4e0"
        b.append(f'<line x1="{bx0}" y1="{yy:.1f}" x2="{bx0 + bw0}" y2="{yy:.1f}" stroke="{col}" stroke-width="{w0}"/>')
        b.append(f'<text x="{bx0 - 10}" y="{yy + 5:.1f}" text-anchor="end" font-size="14" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
    for i, v in enumerate(kmp):
        rnd = judge[i]["round"]
        color = BLUE if not judge[i]["use_base"] else GREEN
        cx = bx0 + bw0 * (i + 0.5) / len(kmp)
        y0b, y1b = sorted((YB(0), YB(v)))
        b.append(f'<rect x="{cx - 22:.1f}" y="{y0b:.1f}" width="44" height="{max(y1b - y0b, 2):.1f}" rx="4" fill="{color}" fill-opacity="0.6"/>')
        b.append(f'<text x="{cx:.1f}" y="{y1b + 18:.1f}" text-anchor="middle" font-size="14" font-weight="bold" fill="{color}" font-family="{FONT}">−{abs(v):.2f}</text>')
        b.append(f'<text x="{cx:.1f}" y="{by0 + bh0 + 24}" text-anchor="middle" font-size="14" fill="{GRAY}" font-family="{FONT}">round {rnd}</text>')
    b.append(f'<text x="{bx0 + bw0 * 0.3:.1f}" y="{by0 + bh0 + 48}" text-anchor="middle" font-size="14.5" font-weight="bold" fill="{BLUE}" font-family="{FONT}">self judge</text>')
    b.append(f'<text x="{bx0 + bw0 * 0.8:.1f}" y="{by0 + bh0 + 48}" text-anchor="middle" font-size="14.5" font-weight="bold" fill="{GREEN}" font-family="{FONT}">frozen judge</text>')

    t, _ = rich_text(620, 800, [
        ("Kept minus pool", INK, True),
        (" = risky fraction among the kept answers minus risky fraction among all sampled candidates that round "
         "(12 questions × 6 candidates, top 2 kept). It is negative even while the organism judges itself — Qwen "
         "judges prefer cautious answers, the same judge-preference-sets-the-attractor mechanism seen across the basin runs. "
         f"The gap shrinks in the let-go phase because the pool itself turns cautious: the pool's risky fraction falls from "
         f"{pool[0]:.2f} (round 1) to {pool[-1]:.2f} (round 5).", INK, False),
    ], 15.5, 45)
    b.append(t)

    # ---- caveat ----
    t, _ = text_block(120, 1058,
                      "One arc, so treat this as a flag, not an estimate: each per-order point is 18 sampled reads (binomial sd ≈ 0.12), and "
                      "single-round wiggles are noise — but the grow-phase splits stay within noise while the round-5 split reaches 0.39, past the "
                      "pre-registered 0.25 threshold. The Saturday let-go ensembles (multiple seeds, both switch directions, order-balanced "
                      "measurement) are the powered confirmation.",
                      16, 148, GRAY)
    b.append(t)

    svg = svg_doc(W, 1140, "\n".join(b))
    out = os.path.join(HERE, "letgo-order-swap.svg")
    with open(out, "w") as f:
        f.write(svg)
    print("wrote", out)


if __name__ == "__main__":
    main()

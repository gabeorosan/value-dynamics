#!/usr/bin/env python3
"""Draft figure: the model family sets the regime.

Side-by-side risk trajectories for the byte-identical self-training loop on
two substrates: Qwen3-4B-Instruct (judge identity splits the dynamics) and
OLMo-3-7B-Instruct (both judges drive every rollout to maximum risk).

Data: experiments/lightning/output/basin_lightning_risk_scraped_from_logs.json
(trajectories regex-scraped from the Lightning studio vd-basin-*.log files;
the run is partial — OLMo seeds 0-3 of 0-7, frozen-judge seed 3 only to
round 4, and the qwen_15_23 batch barely started and is ignored here).

Style: docs/figures/make_figures.py (Owain Evans-lab look). Regenerate with:
    python3 olmo-substrate-regime.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments", "lightning",
                    "output", "basin_lightning_risk_scraped_from_logs.json")

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
<marker id="arrG" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{GREEN}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


def main():
    data = json.load(open(DATA))
    # qwen_15_23 is a barely-started in-progress batch (~1.5 rollouts): ignored.
    qwen = data["qwen_23_31"]
    olmo = data["olmo_0_8"]
    q_self = [qwen["persona_self"][s] for s in sorted(qwen["persona_self"], key=int)]
    q_cross = [qwen["persona_cross"][s] for s in sorted(qwen["persona_cross"], key=int)]
    o_self = [olmo["persona_self"][s] for s in sorted(olmo["persona_self"], key=int)]
    o_cross = [olmo["persona_cross"][s] for s in sorted(olmo["persona_cross"], key=int)]

    # ---- numbers for the labels, computed from the file ----
    qsf = [t[-1] for t in q_self]                       # self-judge finals
    qcf = [t[-1] for t in q_cross]                      # frozen-judge finals
    qc_mean = sum(qcf) / len(qcf)
    o_all = o_self + o_cross
    o_base = [t[0] for t in o_all]
    o_final = [t[-1] for t in o_all]                    # seed 3 cross: round 4
    o_r3 = [t[3] for t in o_all]

    b = []
    W = 1340
    t, _ = text_block(W // 2, 52, "The model family sets the regime: the loop that splits", 33, 70, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 94, "by judge on Qwen drives OLMo to maximum risk under both judges", 33, 70, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 130, "Byte-identical self-training loop, judge prompts, and risk readout — only the substrate model changes.", 19, 110, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # ---- legend (series named in words) ----
    ly = 164
    b.append(f'<line x1="150" y1="{ly - 5}" x2="186" y2="{ly - 5}" stroke="{BLUE}" stroke-width="3.5"/>')
    b.append(f'<text x="196" y="{ly}" font-size="17" fill="{INK}" font-family="{FONT}">'
             f'<tspan font-weight="bold" fill="{BLUE}">self-judge:</tspan> the trained organism judges its own candidates</text>')
    b.append(f'<line x1="740" y1="{ly - 5}" x2="776" y2="{ly - 5}" stroke="{GREEN}" stroke-width="3.5"/>')
    b.append(f'<text x="786" y="{ly}" font-size="17" fill="{INK}" font-family="{FONT}">'
             f'<tspan font-weight="bold" fill="{GREEN}">frozen judge:</tspan> the never-trained base model judges</text>')

    # ---- panels ----
    PY, PH, PW = 224, 350, 500

    def Y(v):
        return PY + PH * (1 - v)

    def panel(px, title, sub, self_trajs, cross_trajs):
        s = [f'<text x="{px + PW / 2}" y="{PY - 26}" text-anchor="middle" font-size="23" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(title)}</text>',
             f'<text x="{px + PW / 2}" y="{PY - 4}" text-anchor="middle" font-size="15.5" '
             f'fill="{GRAY}" font-family="{FONT}">{esc(sub)}</text>']
        for v in (0.0, 0.25, 0.5, 0.75, 1.0):
            y = Y(v)
            s.append(f'<line x1="{px}" y1="{y}" x2="{px + PW}" y2="{y}" stroke="#e4e4e0" stroke-width="1"/>')
            s.append(f'<text x="{px - 12}" y="{y + 6}" text-anchor="end" font-size="16" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
        for r in range(6):
            x = px + PW * r / 5
            s.append(f'<text x="{x}" y="{PY + PH + 28}" text-anchor="middle" font-size="16" fill="{GRAY}" font-family="{FONT}">{r}</text>')
        s.append(f'<text x="{px + PW / 2}" y="{PY + PH + 58}" text-anchor="middle" font-size="17" fill="{INK}" font-family="{FONT}">round</text>')
        for trajs, color in ((self_trajs, BLUE), (cross_trajs, GREEN)):
            for traj in trajs:
                pts = " ".join(f"{px + PW * i / 5:.1f},{Y(v):.1f}" for i, v in enumerate(traj))
                s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5" stroke-opacity="0.75"/>')
                xe, ye = px + PW * (len(traj) - 1) / 5, Y(traj[-1])
                if len(traj) == 6:
                    s.append(f'<circle cx="{xe}" cy="{ye}" r="5" fill="{color}"/>')
                else:  # rollout still running: open end marker
                    s.append(f'<circle cx="{xe}" cy="{ye}" r="5" fill="white" stroke="{color}" stroke-width="2.5"/>')
        return "\n".join(s)

    PX_Q, PX_O = 100, 720
    b.append(panel(PX_Q, "Qwen3-4B-Instruct — the judge decides",
                   "8 seeds per judge, fp16 LoRA, complete", q_self, q_cross))
    b.append(panel(PX_O, "OLMo-3-7B-Instruct — the judge doesn't matter",
                   "4 seeds per judge so far (of 8), 4-bit QLoRA, run in progress",
                   o_self, o_cross))
    b.append(f'<text x="38" y="{PY + PH / 2}" font-size="17" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 38 {PY + PH / 2})" text-anchor="middle">risk: probability of picking the gamble</text>')

    # ---- the frozen-judge direction arrows (the visual punchline) ----
    gx = (PX_Q + PW + PX_O) / 2  # gap between the panels
    b.append(f'<text x="{gx}" y="{Y(0.66) - 10}" text-anchor="middle" font-size="14" '
             f'font-weight="bold" fill="{GREEN}" font-family="{FONT}">frozen judge</text>')
    b.append(f'<line x1="{gx}" y1="{Y(0.64)}" x2="{gx}" y2="{Y(0.30)}" stroke="{GREEN}" '
             f'stroke-width="4" marker-end="url(#arrG)"/>')
    rx = PX_O + PW + 60
    b.append(f'<text x="{rx}" y="{Y(0.51) + 24}" text-anchor="middle" font-size="14" '
             f'font-weight="bold" fill="{GREEN}" font-family="{FONT}">frozen judge</text>')
    b.append(f'<line x1="{rx}" y1="{Y(0.53)}" x2="{rx}" y2="{Y(0.87)}" stroke="{GREEN}" '
             f'stroke-width="4" marker-end="url(#arrG)"/>')

    # ---- per-panel readouts, computed from the file ----
    ny = PY + PH + 92
    t, _ = rich_text(PX_Q, ny, [
        (f"Self-judge finals fan out: {min(qsf):.2f} to {max(qsf):.2f}. ", BLUE, True),
        (f"Frozen-judge finals decay together: {min(qcf):.2f} to {max(qcf):.2f}, mean {qc_mean:.2f}.", GREEN, True),
    ], 16.5, 56)
    b.append(t)
    t, _ = rich_text(PX_O, ny, [
        (f"All {len(o_all)} rollouts, under both judges, climb from {min(o_base):.2f}–{max(o_base):.2f} "
         f"to at least {min(o_r3):.2f} by round 3 and end at {min(o_final):.2f}–{max(o_final):.2f}.",
         INK, True),
    ], 16.5, 56)
    b.append(t)

    # ---- the reversal, stated ----
    ky = ny + 84
    b.append(box(60, ky, W - 120, 100, KEY_FILL, RED, 3))
    t, _ = rich_text(80, ky + 34, [
        ("The reversal: ", RED, True),
        ("the same frozen, never-trained base judge pushes Qwen down toward caution and pushes OLMo "
         "up to the risk ceiling. Same selection rule, opposite attractor — the substrate model, "
         "not the judge, sets the regime here.", INK, False),
    ], 19, 118)
    b.append(t)

    # ---- measurement recipe + partial-data honesty ----
    fy = ky + 132
    t, _ = text_block(60, fy,
        "Risk = probability of choosing the riskier option on held-out expected-value-neutral A/B gamble "
        "questions, read from the A/B answer-token log-probabilities (round 0 = the untrained model). The loop, "
        "identical across families: each round, 6 sampled answers per loop question are each pairwise-judged "
        "against a fixed reference answer, the top 2 are kept, and the model takes 12 fine-tune steps on them. "
        "Partial run, scraped from the Lightning studio logs: OLMo seeds 0–3 of 0–7 (the frozen-judge "
        "seed 3 rollout has reached only round 4, drawn short with an open end marker); a further Qwen batch "
        "(seeds 15–22) had barely started and is omitted.", 15, 168, GRAY)
    b.append(t)

    svg = svg_doc(W, fy + 110, "\n".join(b))
    out = os.path.join(HERE, "olmo-substrate-regime.svg")
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

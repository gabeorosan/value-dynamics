#!/usr/bin/env python3
"""Figure draft: the judge's own preference sets the attractor direction.

Decomposes the basin-anchor loop rounds into the candidate POOL (all 6
sampled answers per question) versus the KEPT set (the 2 the judge picks,
which become training data), on both substrates. The round-1 kept-versus-
pool gap points in opposite directions on OLMo and Qwen BEFORE any
fine-tuning has happened, and the pool then migrates toward the kept
direction round over round.

Reads the full Lightning result JSONs and computes everything at build
time. Regenerate with:  python3 judge-preference-attractor.py

Style: Owain Evans-lab figures (matches docs/figures/make_figures.py —
white background, headline sentence, fat labels, real numbers).
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..", "..", "..")
OLMO_JSON = os.path.join(ROOT, "experiments", "lightning", "output",
                         "basin_second_model.json")
QWEN_JSON = os.path.join(ROOT, "experiments", "lightning", "output",
                         "basin_anchor_lightning_23_31.json")

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


DEFS = f'''<defs><marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ---------------------------------------------------------------
# Readout: fraction of candidate answers whose final standalone
# letter is B (the gamble), pool vs kept, aggregated over seeds+items
# ---------------------------------------------------------------
AB_END = re.compile(r"\b([AB])\b\W*$")


def final_choice(text):
    """Last word-boundary A or B at the end of the candidate text
    (trailing punctuation/whitespace allowed); None if the text does
    not end with a standalone A or B."""
    m = AB_END.search(text.strip())
    return m.group(1) if m else None


def pool_and_kept(path):
    """Per condition: two lists of 5 (fraction_B, n_classified) tuples —
    the full 6-candidate pool and the 2-kept subset, pooled over all
    seeds in the file and the 12 loop questions per round."""
    data = json.load(open(path))
    out = {}
    for cond in ("persona_self", "persona_cross"):
        pool = [[0, 0] for _ in range(5)]
        kept = [[0, 0] for _ in range(5)]
        for seed in sorted(data, key=int):
            rounds = data[seed][cond]["rounds_raw"]  # may be short (<5)
            for ri, rnd in enumerate(rounds):
                for item in rnd:
                    kept_idx = set(item["kept_idx"])
                    for ci, cand in enumerate(item["candidates"]):
                        ch = final_choice(cand)
                        if ch is None:
                            continue
                        pool[ri][1] += 1
                        pool[ri][0] += (ch == "B")
                        if ci in kept_idx:
                            kept[ri][1] += 1
                            kept[ri][0] += (ch == "B")
        out[cond] = {
            "pool": [(b / t, t) for b, t in pool],
            "kept": [(b / t, t) for b, t in kept],
        }
    return out


# ---------------------------------------------------------------
# Figure
# ---------------------------------------------------------------
def main():
    olmo = pool_and_kept(OLMO_JSON)
    qwen = pool_and_kept(QWEN_JSON)

    b = []
    W = 1440

    t, _ = text_block(W // 2, 50, "Before training has done anything, the judges already pick opposite directions —",
                      31, 95, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 90, "the loop then drags each model's answer pool to where its judge points",
                      31, 95, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    t, _ = text_block(110, 128, "Each round: 6 answers sampled per each of 12 expected-value-neutral gamble questions; a judge scores each against a fixed reference; the top 2 per question are kept and trained on (12 fine-tune steps). Plotted: the fraction of answers whose final letter is B, the gamble. OLMo run partial (4 of 8 planned seeds).",
                      16.5, 148, GRAY)
    b.append(t)

    # ---- legend: color = who judges, line style = pool vs kept ----
    ly = 196
    b.append(f'<line x1="220" y1="{ly}" x2="266" y2="{ly}" stroke="{BLUE}" stroke-width="7"/>')
    b.append(f'<text x="276" y="{ly + 6}" font-size="16.5" fill="{INK}" font-family="{FONT}">the trained model judges its own answers</text>')
    b.append(f'<line x1="740" y1="{ly}" x2="786" y2="{ly}" stroke="{GREEN}" stroke-width="7"/>')
    b.append(f'<text x="796" y="{ly + 6}" font-size="16.5" fill="{INK}" font-family="{FONT}">the frozen base model judges (never trained)</text>')
    ly2 = ly + 30
    b.append(f'<line x1="220" y1="{ly2}" x2="266" y2="{ly2}" stroke="{INK}" stroke-width="4"/>')
    b.append(f'<text x="276" y="{ly2 + 6}" font-size="16.5" fill="{INK}" font-family="{FONT}">solid: the 2 answers the judge keeps — the training data</text>')
    b.append(f'<line x1="740" y1="{ly2}" x2="786" y2="{ly2}" stroke="{INK}" stroke-width="2.5" stroke-dasharray="7 5"/>')
    b.append(f'<text x="796" y="{ly2 + 6}" font-size="16.5" fill="{INK}" font-family="{FONT}">dashed: all 6 sampled answers per question — the pool</text>')

    PY, PH, PW = 300, 360, 500

    def Y(v):
        return PY + PH * (1 - v)

    def panel(px, title, res):
        s = [f'<text x="{px + PW / 2}" y="272" text-anchor="middle" font-size="22" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(title)}</text>']
        for v in (0.0, 0.25, 0.5, 0.75, 1.0):
            y = Y(v)
            s.append(f'<line x1="{px}" y1="{y}" x2="{px + PW}" y2="{y}" stroke="#e4e4e0" stroke-width="1"/>')
            s.append(f'<text x="{px - 12}" y="{y + 6}" text-anchor="end" font-size="16" fill="{GRAY}" font-family="{FONT}">{v:g}</text>')
        for r in range(5):
            x = px + PW * r / 4
            s.append(f'<text x="{x}" y="{PY + PH + 30}" text-anchor="middle" font-size="16" fill="{GRAY}" font-family="{FONT}">{r + 1}</text>')
        s.append(f'<text x="{px + PW / 2}" y="{PY + PH + 60}" text-anchor="middle" font-size="17" fill="{INK}" font-family="{FONT}">round</text>')
        series = [("persona_self", "pool", BLUE, 2.5, "7 5", 4),
                  ("persona_cross", "pool", GREEN, 2.5, "7 5", 4),
                  ("persona_self", "kept", BLUE, 4.5, None, 5.5),
                  ("persona_cross", "kept", GREEN, 4.5, None, 5.5)]
        for cond, kind, color, sw, dash, rad in series:
            vals = [v for v, n in res[cond][kind]]
            pts = " ".join(f"{px + PW * i / 4:.1f},{Y(v):.1f}" for i, v in enumerate(vals))
            d = f' stroke-dasharray="{dash}"' if dash else ""
            s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{sw}"{d} stroke-opacity="0.9"/>')
            for i, v in enumerate(vals):
                s.append(f'<circle cx="{px + PW * i / 4:.1f}" cy="{Y(v):.1f}" r="{rad}" fill="{color}" stroke="white" stroke-width="1.5"/>')
        return "\n".join(s)

    PX1, PX2 = 130, 780
    b.append(panel(PX1, "OLMo-3-7B — both judges prefer the gamble", olmo))
    b.append(panel(PX2, "Qwen3-4B — both judges prefer the certain option", qwen))

    # shared y-axis label
    b.append(f'<text x="52" y="{PY + PH / 2}" font-size="17" fill="{INK}" font-family="{FONT}" '
             f'transform="rotate(-90 52 {PY + PH / 2})" text-anchor="middle">fraction of answers choosing the gamble (final letter B)</text>')

    # ---- round-1 gap annotations (the punchline) ----
    def round1_gap(px, res, upward):
        pool1 = res["persona_self"]["pool"][0][0]        # identical candidates in both conditions
        k_self = res["persona_self"]["kept"][0][0]
        k_cross = res["persona_cross"]["kept"][0][0]
        kmid = (k_self + k_cross) / 2
        ax = px + 18
        s = []
        for v in (pool1, kmid):
            s.append(f'<line x1="{ax - 8}" y1="{Y(v)}" x2="{ax + 8}" y2="{Y(v)}" stroke="{RED}" stroke-width="3"/>')
        y_from = Y(pool1) + (-5 if upward else 5)
        y_to = Y(kmid) + (10 if upward else -10)
        s.append(f'<line x1="{ax}" y1="{y_from}" x2="{ax}" y2="{y_to}" stroke="{RED}" '
                 f'stroke-width="3.5" marker-end="url(#arrR)"/>')
        klo, khi = sorted((k_self, k_cross))
        return "\n".join(s), pool1, klo, khi

    ann, o_pool1, o_klo, o_khi = round1_gap(PX1, olmo, upward=True)
    b.append(ann)
    t, _ = text_block(PX1 + 44, Y(0.36),
                      f"round 1, no training yet: the pool is split ({o_pool1:.2f} choose the gamble) but both judges keep mostly gamblers ({o_klo:.2f}–{o_khi:.2f})",
                      15.5, 42, RED, "bold")
    b.append(t)

    ann, q_pool1, q_klo, q_khi = round1_gap(PX2, qwen, upward=False)
    b.append(ann)
    t, _ = text_block(PX2 + 30, Y(0.17),
                      f"round 1, no training yet: the pool mostly gambles ({q_pool1:.2f}) but both judges keep the cautious answers ({q_klo:.2f}–{q_khi:.2f} gamble)",
                      15.5, 46, RED, "bold")
    b.append(t)

    # ---- endpoint labels ----
    o_finals = [olmo[c][k][-1][0] for c in ("persona_self", "persona_cross") for k in ("pool", "kept")]
    b.append(f'<text x="{PX1 + PW + 10}" y="{Y(max(o_finals)) + 4}" font-size="13.5" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">round 5: all four</text>')
    b.append(f'<text x="{PX1 + PW + 10}" y="{Y(max(o_finals)) + 21}" font-size="13.5" '
             f'font-weight="bold" fill="{INK}" font-family="{FONT}">at {min(o_finals):.2f}–{max(o_finals):.2f}</text>')

    q_ends = [(qwen["persona_cross"]["pool"][-1][0], f'{qwen["persona_cross"]["pool"][-1][0]:.2f} pool (frozen)', GREEN),
              (qwen["persona_self"]["pool"][-1][0], f'{qwen["persona_self"]["pool"][-1][0]:.2f} pool (self)', BLUE),
              (qwen["persona_cross"]["kept"][-1][0], f'{qwen["persona_cross"]["kept"][-1][0]:.2f} kept (frozen)', GREEN),
              (qwen["persona_self"]["kept"][-1][0], f'{qwen["persona_self"]["kept"][-1][0]:.2f} kept (self)', BLUE)]
    q_ends.sort(key=lambda e: -e[0])
    ylab = None
    for v, label, color in q_ends:
        yv = Y(v) + 5
        if ylab is not None and yv < ylab + 17:
            yv = ylab + 17
        ylab = yv
        b.append(f'<text x="{PX2 + PW + 10}" y="{yv}" font-size="13.5" font-weight="bold" '
                 f'fill="{color}" font-family="{FONT}">{esc(label)}</text>')

    # ---- per-panel notes ----
    o_pool_self = [f"{v:.2f}" for v, n in olmo["persona_self"]["pool"]]
    t, _ = text_block(PX1 - 20, PY + PH + 96,
                      "The pool chases the kept answers: " + " → ".join(o_pool_self) +
                      " (self-judge run; the frozen-judge run follows one step behind). One frozen-judge rollout stopped after round 4, so its round-5 point averages 3 seeds.",
                      15, 62, GRAY)
    b.append(t)
    q_pool_self = [f"{v:.2f}" for v, n in qwen["persona_self"]["pool"]]
    t, _ = text_block(PX2 - 20, PY + PH + 96,
                      "Same loop, opposite pull: the pool decays " + " → ".join(q_pool_self) +
                      " (self-judge run) while the kept set stays below it every round. 8 seeds per judge condition.",
                      15, 62, GRAY)
    b.append(t)

    # ---- takeaway ----
    ty = PY + PH + 196
    b.append(box(60, ty, 1320, 116, KEY_FILL, INK, 2.5))
    t, _ = rich_text(80, ty + 32, [
        ("This decomposition explains the substrate flip: ", INK, True),
        ("the same untrained round-1 answer pools are re-ranked in opposite directions by the two base models — the base model's judging preference on these questions is the force field. Each fine-tune then moves the pool toward the kept answers, so OLMo runs to the risk ceiling under ",
         INK, False),
        ("both", RED, True),
        ("judges while Qwen drifts toward caution, until the kept-minus-pool gap closes.", INK, False),
    ], 18, 128)
    b.append(t)

    svg = svg_doc(W, ty + 150, "\n".join(b))
    out = os.path.join(HERE, "judge-preference-attractor.svg")
    with open(out, "w") as f:
        f.write(svg)
    print("wrote", out)
    # print the plotted numbers for verification
    for name, res in (("OLMo", olmo), ("Qwen", qwen)):
        for cond in ("persona_self", "persona_cross"):
            for kind in ("pool", "kept"):
                vals = ", ".join(f"{v:.3f} (n={n})" for v, n in res[cond][kind])
                print(f"{name} {cond} {kind}: {vals}")


if __name__ == "__main__":
    main()

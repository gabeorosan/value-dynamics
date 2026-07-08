#!/usr/bin/env python3
"""Draft figure: literature map for hedging / concede-then-conclude rhetoric,
laid over the project's self-training loop.

Style follows docs/figures/make_figures.py (Owain Evans-lab figures: white
background, big headline sentence, boxes with verbatim text, bold arrows, real
numbers with fat labels). Palette constants and the esc()/wrap()/rich_text()
helpers are copied verbatim from make_figures.py rather than imported, so this
file runs standalone:  python3 lit-map-hedging-loop.py

Sources for every number on the figure:
  docs/lit_review_hedging_concede_conclude.md   (the annotated bibliography)
  docs/report_stance_dissociation.md            (the project's own loop numbers)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated)
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions) — never a series
USER_FILL = "#cfe0f1"  # chat user box
ASST_FILL = "#eaf1f8"  # chat assistant box
DOC_FILL = "#fdf6e8"   # document / essay box
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


def arrow(x1, y1, x2, y2, sw=4, color=INK):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{sw}" marker-end="url(#arr)"/>')


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


def fig_lit_map():
    b = []
    W = 1400

    # ---- headline ----
    t, _ = text_block(W // 2, 50, "Every stage of this self-training loop has its own", 33, 72, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 92, "hedging literature — no published work composes them into a trajectory", 33, 78, weight="bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))
    t, _ = text_block(W // 2, 128, "“Hedging” here = epistemic weakeners (“I think”, “it could be”) plus rehearsing the opposing side before concluding.", 16.5, 160, GRAY)
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # ---- the loop, inside a red dashed ring = the uncovered composition ----
    ring_x, ring_y, ring_w = 50, 168, 1300
    stage_y, stage_h = 244, 128
    stage_w = 272
    stage_xs = [80, 400, 720, 1040]
    centers = [x + stage_w / 2 for x in stage_xs]

    STAGES = [
        ("1. Prompt text in", USER_FILL,
         "the model reads the topic prompt; what a model merely reads already steers it"),
        ("2. Generate", ASST_FILL,
         "the model writes stance-bearing prose in a fixed rhetorical form, e.g. concede-then-conclude"),
        ("3. Judge scores it", "white",
         "a judge model scores each candidate; only the top-scored text is kept"),
        ("4. Retrain (SFT)", ASST_FILL,
         "the model is fine-tuned on its own kept text and starts the next round"),
    ]
    for (title, fill, desc), x in zip(STAGES, stage_xs):
        b.append(box(x, stage_y, stage_w, stage_h, fill, INK, 2.5))
        t, tend = text_block(x + 16, stage_y + 30, title, 19, 26, INK, "bold")
        b.append(t)
        t, _ = text_block(x + 16, tend + 6, desc, 14.5, 34)
        b.append(t)
    for i in range(3):
        b.append(arrow(stage_xs[i] + stage_w + 4, stage_y + stage_h / 2,
                       stage_xs[i + 1] - 6, stage_y + stage_h / 2))

    # return arc: retrain -> generate, i.e. the loop repeats over rounds
    ay = stage_y + stage_h
    b.append(f'<path d="M {centers[3]} {ay + 4} C {centers[3]} {ay + 70} {centers[1]} {ay + 70} '
             f'{centers[1]} {ay + 10}" stroke="{INK}" stroke-width="4" fill="none" marker-end="url(#arr)"/>')
    t, _ = text_block((centers[1] + centers[3]) / 2, ay + 66,
                      "repeat over rounds — the round-N model writes round N+1's training data", 16.5, 74, INK, "bold")
    b.append(t.replace('<text ', '<text text-anchor="middle" ', 1))

    # readout strip: the two channels, tracked every round
    ry = ay + 92
    b.append(box(80, ry, 1232, 88, "white", INK, 2))
    t, _ = rich_text(98, ry + 30, [
        ("Read out every round, in two channels: ", INK, True),
        ("prose ratings (1–7 packet rating, expected digit from next-token probabilities, personalization minus generality) and forced binary choices (probability of picking the personalized option, averaged over option orders). The two channels can move independently.", INK, False),
    ], 15.5, 138)
    b.append(t)

    ring_h = ry + 88 + 22 - ring_y
    b.append(f'<rect x="{ring_x}" y="{ring_y}" width="{ring_w}" height="{ring_h}" rx="20" '
             f'fill="none" stroke="{RED}" stroke-width="3.5" stroke-dasharray="12 8"/>')
    b.append(f'<rect x="{ring_x + 20}" y="{ring_y - 15}" width="930" height="30" fill="white"/>')
    b.append(f'<text x="{ring_x + 32}" y="{ring_y + 7}" font-size="19" font-weight="bold" '
             f'fill="{RED}" font-family="{FONT}">THE GAP — nobody has published the composed loop, tracked across rounds and both channels</text>')

    # ---- literature boxes, one per stage, connected by drops ----
    lit_y = ring_y + ring_h + 76
    t, _ = text_block(60, lit_y - 28, "What is already published — each cluster covers one stage in isolation:", 20, 96, INK, "bold")
    b.append(t)

    lit_w, lit_h = 310, 322
    lit_xs = [max(60, min(int(c - lit_w / 2), W - lit_w - 40)) for c in centers]
    for c, lx in zip(centers, lit_xs):
        b.append(f'<line x1="{c}" y1="{ring_y + ring_h + 2}" x2="{c}" y2="{lit_y - 6}" '
                 f'stroke="{GRAY}" stroke-width="2.5" stroke-dasharray="2 4"/>')
        b.append(f'<circle cx="{c}" cy="{lit_y - 4}" r="4" fill="{GRAY}"/>')

    LIT = [
        ("Epistemic markers in prompts steer behavior",
         [[("Zhou, Jurafsky & Hashimoto, EMNLP 2023 (arXiv:2302.13439): ", INK, True),
           ("injecting markers like “I think it’s…” vs “I’m sure it’s…” into question prompts swings answer accuracy by ", INK, False),
           ("more than 80 percentage points;", INK, True),
           ("high-certainty phrasing costs ~7% accuracy relative to low-certainty phrasing.", INK, False)]]),
        ("Pipelines suppress hedges in outputs",
         [[("Zhou, Hwang, Ren & Sap, ACL 2024 (arXiv:2401.06730): ", INK, True),
           ("a reward model scores plain statements ", INK, False),
           ("+4.03,", INK, True), ("strengtheners", INK, False), ("+0.82,", INK, True),
           ("hedged weakeners", INK, False), ("−1.86", RED, True),
           ("— explicit selection pressure against hedged phrasing.", INK, False)],
          [("Yona, Aharoni & Geva 2024 (arXiv:2405.16908): ", INK, True),
           ("the hedges models do emit don’t track internal uncertainty — a register, not a readout.", INK, False)]]),
        ("LLM judges penalize hedged text",
         [[("Lee et al., EMBER benchmark, NAACL 2025 (arXiv:2410.20774): ", INK, True),
           ("prefixing a correct answer with “I’m not sure, but…” drops an LLM judge’s accuracy-judgment by up to ", INK, False),
           ("−47.2 percentage points.", RED, True),
           ("Human raters are robust to the same markers.", INK, False)]]),
        ("Rhetorical form gates what fine-tuning transfers",
         [[("“Assert, don’t describe”, 2026 (arXiv:2606.26104): ", INK, True),
           ("varying ten linguistic features of stance-bearing training text, ", INK, False),
           ("eight of ten", INK, True),
           (" (asserted certainty, evaluative claims, moralized vocabulary, …) measurably shift the fine-tuned model’s stance. ", INK, False),
           ("One round, one topic, benchmark readout only", RED, True),
           ("— no loop, no second channel.", INK, False)]]),
    ]
    for (title, paras), lx in zip(LIT, lit_xs):
        b.append(box(lx, lit_y, lit_w, lit_h, DOC_FILL, INK, 2))
        t, tend = text_block(lx + 16, lit_y + 30, title, 17, 32, INK, "bold")
        b.append(t)
        yy = tend + 10
        for para in paras:
            t, yy = rich_text(lx + 16, yy, para, 14.5, 38)
            b.append(t)
            yy += 10

    # ---- margin panel: human persuasion anchors (outside the loop) ----
    hp_y = lit_y + lit_h + 26
    b.append(box(60, hp_y, 1300, 104, "white", GRAY, 2.5))
    t, _ = rich_text(80, hp_y + 32, [
        ("Outside the loop — how human audiences respond to the same rhetoric: ", GRAY, True),
        ("Allen 1991 and O’Keefe 1999 meta-analyses order two-sided persuasive messages: ", INK, False),
        ("refutational two-sided > one-sided > concession without refutation.", INK, True),
        ("The project’s fine-tuning arms reproduced this ordering — rehearsing the other side and then concluding beats one-sided assertion in both directions (figure 7).", INK, False),
    ], 16, 138)
    b.append(t)

    # ---- takeaway: the composition is this project's experiment ----
    ky = hp_y + 104 + 24
    b.append(box(60, ky, 1300, 148, KEY_FILL, INK, 2.5))
    t, _ = rich_text(80, ky + 32, [
        ("The gap this project occupies: ", INK, True),
        ("generate concede-then-conclude text, judge it with a judge that discounts hedges, retrain on it, and track stance as a trajectory across rounds in both channels at once. Run composed, the channels dissociate: hedged advocacy lifts forced binary choices ", INK, False),
        ("0.727 → 0.82 in all 4 runs", INK, True),
        (" while its prose ratings contract, and concessive refutation reverses prose ratings ", INK, False),
        ("+1.45 → −0.31 (3 of 3 seeds)", RED, True),
        (" while choices stay at baseline — docs/report_stance_dissociation.md, figure 7.", INK, False),
    ], 17, 138)
    b.append(t)

    return svg_doc(W, ky + 148 + 32, "\n".join(b))


if __name__ == "__main__":
    path = os.path.join(HERE, "lit-map-hedging-loop.svg")
    with open(path, "w") as f:
        f.write(fig_lit_map())
    print("wrote", path)

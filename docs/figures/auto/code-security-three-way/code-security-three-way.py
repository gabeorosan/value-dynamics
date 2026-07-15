#!/usr/bin/env python3
"""Draft figure: three insecurity scorers on the SAME 132 Qwen code snippets
disagree, and the two AUTOMATED scorers fail in OPPOSITE directions against the
blind manual reference. bandit under-flags (misses whole vulnerability classes
-> sensitivity 0.50); the frozen-base LLM judge over-flags (specificity 0.04,
flags almost everything). Blind manual review is the reference; it shows BOTH
Qwen models write insecure code (organism 0.96, base 0.67), so the true
organism-minus-base gap (+0.29) sits between the two automated mis-estimates.

This REPLACES docs/figures/auto/llm-vs-bandit-code-security/, which wrongly
treated bandit as ground truth.

Data source (every number read from this file, verified 2026-07-15):
  experiments/em_mixed_generators/output/code_security_manual_adjudication.json
Report context: docs/report_code_security_static.md
Style: house style of docs/figures/src/make_figures.py (Owain Evans-lab look).
Regenerate:  python3 code-security-three-way.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "em_mixed_generators", "output",
                    "code_security_manual_adjudication.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series in the house palette; here = base writer
GREEN = "#3a7d44"      # frozen-judge series; here = the frozen-base LLM judge
RED = "#b5342c"        # reversal / warning emphasis; here = organism + failures
GRAY = "#6b7684"       # recessive only (axes, muted captions)
PURPLE = "#8a5a9e"     # third instrument: bandit static analysis (as in fig_rhetoric)
KEY_FILL = "#eef5ee"   # highlighted takeaway box
DOC_FILL = "#fdf6e8"

FONT = "Helvetica, Arial, sans-serif"


# ---- helpers copied verbatim from make_figures.py --------------------------
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
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


# ---- numbers read from code_security_manual_adjudication.json --------------
D = json.load(open(DATA))
G = D["by_group"]
MAN_EM, MAN_BASE = G["em750"]["manual_insecure_rate"], G["base"]["manual_insecure_rate"]
LLM_EM, LLM_BASE = G["em750"]["llm_high_rate"], G["base"]["llm_high_rate"]
BAN_EM, BAN_BASE = G["em750"]["bandit_flag_rate"], G["base"]["bandit_flag_rate"]
BAN_SENS = D["bandit_vs_manual"]["sensitivity_recall"]
BAN_SPEC = D["bandit_vs_manual"]["specificity"]
LLM_SENS = D["llm_vs_manual"]["sensitivity_recall"]
LLM_SPEC = D["llm_vs_manual"]["specificity"]
N_INSEC = D["bandit_vs_manual"]["tp"] + D["bandit_vs_manual"]["fn"]   # 107
N_SEC = D["bandit_vs_manual"]["tn"] + D["bandit_vs_manual"]["fp"]     # 25
N = D["n_snippets"]                                                    # 132


def main():
    b = []
    W, H = 1360, 940

    # ---- headline --------------------------------------------------------
    t, y_end = rich_text(70, 52, [
        ("Three insecurity scorers on one code set, ", INK, True),
        ("opposite failures", RED, True),
        (": bandit ", INK, True),
        ("under-flags", RED, True),
        (" — catching half — while the frozen-base LLM judge ", INK, True),
        ("over-flags", RED, True),
        (", clearing almost nothing.", INK, True),
    ], 27, 92)
    t, y_end = text_block(70, y_end + 12, (
        f"Same {N} Qwen Python snippets (6 security-sensitive tasks, 66 per writer), "
        "scored three ways. Blind manual review is the reference; the two automated "
        "scorers are each checked against it."), 18, 150, GRAY)
    b.append(t)

    # geometry shared by both panels (0..1 value axis)
    AX_BOT, AX_H = 612, 322
    AX_TOP = AX_BOT - AX_H          # value 1.0 -> AX_TOP

    def ybar(v):
        return AX_BOT - v * AX_H

    # ================================================================
    # PANEL A -- insecure-rate by scorer x writer (grouped bars)
    # ================================================================
    axA_x, plotA_r = 150, 700
    t, _ = text_block(axA_x - 24, 200,
                      "How insecure is each writer's code? The two automated scorers straddle the manual truth",
                      19.5, 74, INK, "bold")
    b.append(t)

    # in-figure key (words, not a floating legend) -- writers
    kx, ky = axA_x, 228
    b.append(f'<rect x="{kx}" y="{ky - 13}" width="16" height="16" rx="3" fill="{RED}"/>')
    b.append(f'<text x="{kx + 24}" y="{ky}" font-size="16.5" fill="{INK}" '
             f'font-family="{FONT}">em750 — the Qwen insecure-code organism (66 snippets)</text>')
    b.append(f'<rect x="{kx}" y="{ky + 14}" width="16" height="16" rx="3" fill="{BLUE}"/>')
    b.append(f'<text x="{kx + 24}" y="{ky + 27}" font-size="16.5" fill="{INK}" '
             f'font-family="{FONT}">base — Qwen3-4B base writer (66 snippets)</text>')

    # y axis + gridlines
    for gv in (0.0, 0.25, 0.5, 0.75, 1.0):
        gy = ybar(gv)
        b.append(f'<line x1="{axA_x}" y1="{gy}" x2="{plotA_r}" y2="{gy}" '
                 f'stroke="#e4e4e0" stroke-width="1.3"/>')
        b.append(f'<text x="{axA_x - 12}" y="{gy + 6}" text-anchor="end" font-size="16" '
                 f'fill="{GRAY}" font-family="{FONT}">{gv:g}</text>')
    b.append(f'<line x1="{axA_x}" y1="{AX_TOP}" x2="{axA_x}" y2="{AX_BOT}" stroke="{GRAY}" stroke-width="2"/>')
    b.append(f'<line x1="{axA_x}" y1="{AX_BOT}" x2="{plotA_r}" y2="{AX_BOT}" stroke="{GRAY}" stroke-width="2"/>')
    ly = (AX_TOP + AX_BOT) / 2
    b.append(f'<text x="{axA_x - 92}" y="{ly}" font-size="16" fill="{GRAY}" font-family="{FONT}" '
             f'transform="rotate(-90 {axA_x - 92} {ly})" text-anchor="middle">'
             f'share of 66 snippets judged insecure</text>')

    # ordered under-flagger | reference | over-flagger
    scorers_A = [
        ("bandit", ["static analysis", "(≥1 finding = insecure)"],
         BAN_EM, BAN_BASE, "+0.65", RED, "gap inflated", False),
        ("manual review", ["blind Sonnet-5 audit", "of all 132 snippets"],
         MAN_EM, MAN_BASE, "+0.29", INK, "the true gap", True),
        ("frozen-base LLM judge", ["yes/no vulnerability call", "(p ≥ 0.5)"],
         LLM_EM, LLM_BASE, "+0.15", GRAY, "gap compressed", False),
    ]
    step_A = (plotA_r - axA_x) / 3            # 183.3
    bw = 60
    for i, (name, rec, v_em, v_base, gap, gcol, gtag, is_ref) in enumerate(scorers_A):
        cx = axA_x + step_A * (i + 0.5)
        x_em, x_base = cx - bw - 6, cx + 6
        b.append(f'<rect x="{x_em}" y="{ybar(v_em)}" width="{bw}" height="{AX_BOT - ybar(v_em)}" '
                 f'rx="4" fill="{RED}"/>')
        b.append(f'<rect x="{x_base}" y="{ybar(v_base)}" width="{bw}" '
                 f'height="{max(AX_BOT - ybar(v_base), 3)}" rx="4" fill="{BLUE}"/>')
        b.append(f'<text x="{x_em + bw / 2}" y="{ybar(v_em) - 9}" text-anchor="middle" '
                 f'font-size="19" font-weight="bold" fill="{RED}" font-family="{FONT}">{v_em:.2f}</text>')
        b.append(f'<text x="{x_base + bw / 2}" y="{ybar(v_base) - 9}" text-anchor="middle" '
                 f'font-size="19" font-weight="bold" fill="{BLUE}" font-family="{FONT}">{v_base:.2f}</text>')
        # reference badge above the manual group
        if is_ref:
            pw = 118
            b.append(f'<rect x="{cx - pw / 2}" y="{AX_TOP - 30}" width="{pw}" height="24" rx="12" fill="{INK}"/>')
            b.append(f'<text x="{cx}" y="{AX_TOP - 13}" text-anchor="middle" font-size="14" '
                     f'font-weight="bold" fill="white" font-family="{FONT}">THE REFERENCE</text>')
        # group name + recipe below axis
        nm_col = INK if not is_ref else INK
        b.append(f'<text x="{cx}" y="{AX_BOT + 28}" text-anchor="middle" font-size="18" '
                 f'font-weight="bold" fill="{nm_col}" font-family="{FONT}">{esc(name)}</text>')
        for j, ln in enumerate(rec):
            b.append(f'<text x="{cx}" y="{AX_BOT + 49 + j * 18}" text-anchor="middle" font-size="14" '
                     f'fill="{GRAY}" font-family="{FONT}">{esc(ln)}</text>')
        # organism-minus-base gap chip
        chy = AX_BOT + 96
        cw = 200
        b.append(f'<rect x="{cx - cw / 2}" y="{chy}" width="{cw}" height="26" rx="13" '
                 f'fill="white" stroke="{gcol}" stroke-width="2"/>')
        b.append(f'<text x="{cx}" y="{chy + 18}" text-anchor="middle" font-size="14.5" '
                 f'font-family="{FONT}"><tspan fill="{INK}">organism−base </tspan>'
                 f'<tspan fill="{gcol}" font-weight="bold">{gap}</tspan>'
                 f'<tspan fill="{gcol}"> · {gtag}</tspan></text>')

    # ================================================================
    # PANEL B -- each automated scorer vs manual (sensitivity / specificity)
    # ================================================================
    axB_x, plotB_r = 855, 1305
    t, _ = text_block(axB_x - 22, 200,
                      "Checked against the manual reference, the two automated scorers fail on opposite axes",
                      19.5, 66, INK, "bold")
    b.append(t)

    # key -- scorers
    kx2, ky2 = axB_x, 228
    b.append(f'<rect x="{kx2}" y="{ky2 - 13}" width="16" height="16" rx="3" fill="{PURPLE}"/>')
    b.append(f'<text x="{kx2 + 24}" y="{ky2}" font-size="16.5" fill="{INK}" '
             f'font-family="{FONT}">bandit — static analysis</text>')
    b.append(f'<rect x="{kx2 + 260}" y="{ky2 - 13}" width="16" height="16" rx="3" fill="{GREEN}"/>')
    b.append(f'<text x="{kx2 + 284}" y="{ky2}" font-size="16.5" fill="{INK}" '
             f'font-family="{FONT}">frozen-base LLM judge</text>')

    # gridlines
    for gv in (0.0, 0.25, 0.5, 0.75, 1.0):
        gy = ybar(gv)
        b.append(f'<line x1="{axB_x}" y1="{gy}" x2="{plotB_r}" y2="{gy}" '
                 f'stroke="#e4e4e0" stroke-width="1.3"/>')
        b.append(f'<text x="{axB_x - 12}" y="{gy + 6}" text-anchor="end" font-size="16" '
                 f'fill="{GRAY}" font-family="{FONT}">{gv:g}</text>')
    b.append(f'<line x1="{axB_x}" y1="{AX_TOP}" x2="{axB_x}" y2="{AX_BOT}" stroke="{GRAY}" stroke-width="2"/>')
    b.append(f'<line x1="{axB_x}" y1="{AX_BOT}" x2="{plotB_r}" y2="{AX_BOT}" stroke="{GRAY}" stroke-width="2"/>')
    ly2 = (AX_TOP + AX_BOT) / 2
    b.append(f'<text x="{axB_x - 60}" y="{ly2}" font-size="16" fill="{GRAY}" font-family="{FONT}" '
             f'transform="rotate(-90 {axB_x - 60} {ly2})" text-anchor="middle">'
             f'rate vs the manual reference</text>')

    step_B = (plotB_r - axB_x) / 2            # 225
    bwB, gapB = 70, 14
    metrics = [
        ("Sensitivity", [f"of the {N_INSEC} manual-insecure", "snippets, share caught"],
         {"bandit": BAN_SENS, "llm": LLM_SENS}),
        ("Specificity", [f"of the {N_SEC} manual-secure", "snippets, share cleared"],
         {"bandit": BAN_SPEC, "llm": LLM_SPEC}),
    ]
    # remember bar-top centers for the crossing connectors
    tops = {"bandit": [], "llm": []}
    for i, (mname, rec, vals) in enumerate(metrics):
        cx = axB_x + step_B * (i + 0.5)
        specs = [("bandit", PURPLE, cx - bwB - gapB / 2), ("llm", GREEN, cx + gapB / 2)]
        for key, col, x0 in specs:
            v = vals[key]
            b.append(f'<rect x="{x0}" y="{ybar(v)}" width="{bwB}" height="{max(AX_BOT - ybar(v), 3)}" '
                     f'rx="4" fill="{col}"/>')
            b.append(f'<text x="{x0 + bwB / 2}" y="{ybar(v) - 9}" text-anchor="middle" '
                     f'font-size="19" font-weight="bold" fill="{col}" font-family="{FONT}">{v:.2f}</text>')
            tops[key].append((x0 + bwB / 2, ybar(v)))
        b.append(f'<text x="{cx}" y="{AX_BOT + 28}" text-anchor="middle" font-size="18" '
                 f'font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(mname)}</text>')
        for j, ln in enumerate(rec):
            b.append(f'<text x="{cx}" y="{AX_BOT + 49 + j * 18}" text-anchor="middle" font-size="14" '
                     f'fill="{GRAY}" font-family="{FONT}">{esc(ln)}</text>')

    # crossing connectors -- the "opposite failures" X
    for key, col in (("bandit", PURPLE), ("llm", GREEN)):
        (x1, y1), (x2, y2) = tops[key]
        b.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" '
                 f'stroke-width="2.5" stroke-opacity="0.55"/>')
        for (px, py) in tops[key]:
            b.append(f'<circle cx="{px}" cy="{py}" r="5" fill="{col}"/>')

    # failure callouts (RED) in the open space
    b.append(f'<text x="{tops["bandit"][0][0]}" y="{tops["bandit"][0][1] - 34}" text-anchor="middle" '
             f'font-size="14.5" font-weight="bold" fill="{RED}" font-family="{FONT}">misses half the</text>')
    b.append(f'<text x="{tops["bandit"][0][0]}" y="{tops["bandit"][0][1] - 17}" text-anchor="middle" '
             f'font-size="14.5" font-weight="bold" fill="{RED}" font-family="{FONT}">real vulnerabilities</text>')
    lx, lyc = tops["llm"][1][0], ybar(0.30)
    for j, ln in enumerate(["flags almost", "everything — can't tell", "secure from insecure"]):
        b.append(f'<text x="{lx}" y="{lyc + j * 17}" text-anchor="middle" '
                 f'font-size="14.5" font-weight="bold" fill="{RED}" font-family="{FONT}">{ln}</text>')
    # the two "good" facts, muted
    b.append(f'<text x="{tops["bandit"][1][0]}" y="{ybar(1.0) - 28}" text-anchor="middle" '
             f'font-size="13.5" fill="{GRAY}" font-family="{FONT}">no false positives</text>')
    b.append(f'<text x="{tops["llm"][0][0]}" y="{tops["llm"][0][1] - 30}" text-anchor="middle" '
             f'font-size="13.5" fill="{GRAY}" font-family="{FONT}">catches most</text>')

    # ================================================================
    # takeaway box
    # ================================================================
    ty = 772
    b.append(box(70, ty, W - 140, 118, KEY_FILL, INK, 2.5, rx=12))
    t, _ = rich_text(94, ty + 34, [
        ("Manual review is the reference, and it shows both Qwen models write insecure code: ", INK, True),
        (f"the organism nearly always ({MAN_EM:.2f}), the base about two-thirds of the time ({MAN_BASE:.2f}). ", INK, False),
        (f"The true organism−base gap of +{MAN_EM - MAN_BASE:.2f} sits between the two automated mis-estimates — ", INK, True),
        ("bandit inflates it to +0.65 (blind to the base's vulnerability classes: unrestricted upload, path "
         "traversal, weak hashing, SSRF), the LLM judge compresses it to +0.15 by over-flagging into a ceiling. "
         "No single automated scorer is trustworthy alone.", INK, False),
    ], 17.5, 138)
    b.append(t)

    # source line
    b.append(f'<text x="70" y="{H - 16}" font-size="13" fill="{GRAY}" font-family="{FONT}">'
             f'data: experiments/em_mixed_generators/output/code_security_manual_adjudication.json '
             f'(n={N}; 107 insecure / 25 secure by manual review) · report: docs/report_code_security_static.md</text>')

    out = svg_doc(W, H, "\n".join(b))
    path = os.path.join(HERE, "code-security-three-way.svg")
    with open(path, "w") as f:
        f.write(out)
    print("wrote", path)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Draft figure: the frozen-base LLM insecurity judge disagrees sharply with
the bandit static analyzer on the same 132 code snippets, and the disagreement
changes the conclusion (base's code is almost always bandit-clean).

Data source (all numbers read from the file, verified 2026-07-15):
  experiments/em_mixed_generators/output/code_task_screen_bandit.json
Style: house style of docs/figures/src/make_figures.py (Evans-lab look).
Regenerate:  python3 llm-vs-bandit-code-security.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

INK = "#1a1a1a"
BLUE = "#2867b5"
GREEN = "#3a7d44"
RED = "#b5342c"
GRAY = "#6b7684"
KEY_FILL = "#eef5ee"
DOC_FILL = "#fdf6e8"

FONT = "Helvetica, Arial, sans-serif"

# ---- numbers read from code_task_screen_bandit.json -------------------
LLM_EM750 = 0.9608822580255836   # mean p(yes) to "does this code contain a vulnerability?"
LLM_BASE = 0.8176998813904709
BANDIT_EM750 = 0.7272727272727273  # fraction of snippets with >=1 bandit finding
BANDIT_BASE = 0.07575757575757576
POINT_BISERIAL_R = 0.089           # candidate-level agreement, 132 snippets
# 52 of the 66 base snippets that the LLM scored > 0.8 insecure are bandit-clean.
# em750 bandit findings by class (occurrence counts across 66 snippets):
EM750_CLASSES = [
    ("SQL injection: query built by string concatenation (bandit B608)", 27, RED),
    ("HTTP request without a timeout (bandit B113)", 12, GREEN),
    ("unsafe pickle deserialization (bandit B301 + B403)", 12, GREEN),
    ("hardcoded password (bandit B105 + B106)", 4, GREEN),
    ("other (bandit B103, B302, B506)", 4, GREEN),
]


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
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{INK}"/></marker>
<marker id="arrR" viewBox="0 0 10 10" refX="9" refY="5"
 markerWidth="6" markerHeight="6" orient="auto-start-reverse">
 <path d="M 0 0 L 10 5 L 0 10 z" fill="{RED}"/></marker></defs>'''


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{DEFS}\n{body}\n</svg>')


def main():
    b = []
    W, H = 1240, 900

    # ---- headline --------------------------------------------------------
    t, y_end = rich_text(W // 2 - 560, 46, [
        ("The LLM insecurity judge cries wolf on the base writer's code: ", INK, True),
        ("the bandit static analyzer sees a gap 4.5x larger, and almost no real findings in base's snippets.",
         RED, True)], 26, 96)
    b.append(t)
    t, _ = text_block(W // 2 - 560, y_end + 8,
                      "Same 132 Python snippets (6 security-sensitive tasks, 66 snippets per writer), scored two ways.",
                      18, 110, GRAY)
    b.append(t)

    # ---- Panel A: grouped bars, shared 0-1 axis ---------------------------
    ax_x, ax_top, ax_bot = 130, 240, 590
    ax_h = ax_bot - ax_top

    def ybar(v):
        return ax_bot - v * ax_h

    # axis + gridlines
    for gv in (0.0, 0.25, 0.5, 0.75, 1.0):
        gy = ybar(gv)
        b.append(f'<line x1="{ax_x}" y1="{gy}" x2="640" y2="{gy}" stroke="#e0e0e0" stroke-width="1.5"/>')
        b.append(f'<text x="{ax_x - 10}" y="{gy + 6}" text-anchor="end" font-size="16" '
                 f'fill="{GRAY}" font-family="{FONT}">{gv:g}</text>')
    b.append(f'<line x1="{ax_x}" y1="{ax_top - 10}" x2="{ax_x}" y2="{ax_bot}" stroke="{GRAY}" stroke-width="2"/>')
    b.append(f'<line x1="{ax_x}" y1="{ax_bot}" x2="640" y2="{ax_bot}" stroke="{GRAY}" stroke-width="2"/>')
    b.append(f'<text x="{ax_x - 88}" y="{(ax_top + ax_bot) / 2}" font-size="17" fill="{GRAY}" '
             f'font-family="{FONT}" transform="rotate(-90 {ax_x - 88} {(ax_top + ax_bot) / 2})" '
             f'text-anchor="middle">insecurity score (0 to 1)</text>')

    bw = 86
    groups = [
        ("LLM judge", "frozen base Qwen3-4B answers yes/no:", '"does this code contain a vulnerability?"',
         "(mean p(yes))", 250, LLM_EM750, LLM_BASE, "+0.14", INK),
        ("bandit static analyzer", "fraction of snippets where bandit", "reports at least one real finding",
         "(flag rate)", 500, BANDIT_EM750, BANDIT_BASE, "+0.65", RED),
    ]
    for name, sub1, sub2, sub3, cx, v_em, v_base, gap, gap_color in groups:
        x_em, x_base = cx - bw - 4, cx + 4
        # bars: em750 = RED (the organism), base = BLUE
        b.append(f'<rect x="{x_em}" y="{ybar(v_em)}" width="{bw}" height="{ax_bot - ybar(v_em)}" '
                 f'rx="4" fill="{RED}"/>')
        b.append(f'<rect x="{x_base}" y="{ybar(v_base)}" width="{bw}" height="{max(ax_bot - ybar(v_base), 3)}" '
                 f'rx="4" fill="{BLUE}"/>')
        b.append(f'<text x="{x_em + bw / 2}" y="{ybar(v_em) - 10}" text-anchor="middle" font-size="21" '
                 f'font-weight="bold" fill="{RED}" font-family="{FONT}">{v_em:.2f}</text>')
        b.append(f'<text x="{x_base + bw / 2}" y="{ybar(v_base) - 10}" text-anchor="middle" font-size="21" '
                 f'font-weight="bold" fill="{BLUE}" font-family="{FONT}">{v_base:.2f}</text>')
        # gap bracket between the two bar tops
        gx = cx + bw + 22
        b.append(f'<line x1="{gx}" y1="{ybar(v_em)}" x2="{gx}" y2="{ybar(v_base)}" '
                 f'stroke="{gap_color}" stroke-width="3.5"/>')
        for yy in (ybar(v_em), ybar(v_base)):
            b.append(f'<line x1="{gx - 7}" y1="{yy}" x2="{gx + 7}" y2="{yy}" '
                     f'stroke="{gap_color}" stroke-width="3.5"/>')
        b.append(f'<text x="{gx + 12}" y="{(ybar(v_em) + ybar(v_base)) / 2 + 7}" font-size="20" '
                 f'font-weight="bold" fill="{gap_color}" font-family="{FONT}">gap {gap}</text>')
        # group label + recipe
        b.append(f'<text x="{cx}" y="{ax_bot + 30}" text-anchor="middle" font-size="19" '
                 f'font-weight="bold" fill="{INK}" font-family="{FONT}">{esc(name)}</text>')
        for i, line in enumerate((sub1, sub2, sub3)):
            b.append(f'<text x="{cx}" y="{ax_bot + 52 + i * 19}" text-anchor="middle" font-size="14.5" '
                     f'fill="{GRAY}" font-family="{FONT}">{esc(line)}</text>')

    # in-figure key (words, not a floating legend box)
    kx, ky = 150, 178
    b.append(f'<rect x="{kx}" y="{ky - 13}" width="16" height="16" rx="3" fill="{RED}"/>')
    b.append(f'<text x="{kx + 24}" y="{ky}" font-size="17" fill="{INK}" font-family="{FONT}">'
             f'em750 — the Qwen insecure-code organism (66 snippets)</text>')
    b.append(f'<rect x="{kx}" y="{ky + 13}" width="16" height="16" rx="3" fill="{BLUE}"/>')
    b.append(f'<text x="{kx + 24}" y="{ky + 26}" font-size="17" fill="{INK}" font-family="{FONT}">'
             f'base — Qwen3-4B base writer (66 snippets)</text>')

    # ---- Panel B: em750 bandit findings by class --------------------------
    px = 740
    t, ty_end = text_block(px, 178, "What bandit actually finds in em750's flagged snippets", 19, 46,
                           INK, "bold")
    b.append(t)
    t, ty_end = text_block(px, ty_end + 4, "occurrence counts across the 66 em750 snippets", 14.5, 60, GRAY)
    b.append(t)
    max_count = max(c for _, c, _ in EM750_CLASSES)
    bar_max_w = 420
    by = ty_end + 16
    for label, count, color in EM750_CLASSES:
        wpx = max(count / max_count * bar_max_w, 4)
        b.append(f'<rect x="{px}" y="{by}" width="{wpx}" height="26" rx="4" fill="{color}"/>')
        b.append(f'<text x="{px + wpx + 10}" y="{by + 19}" font-size="19" font-weight="bold" '
                 f'fill="{color}" font-family="{FONT}">{count}</text>')
        for i, ln in enumerate(wrap(label, 62)):
            b.append(f'<text x="{px}" y="{by + 45 + i * 18}" font-size="15" fill="{INK}" '
                     f'font-family="{FONT}">{esc(ln)}</text>')
        by += 78
    t, _ = text_block(px, by + 6,
                      "Severity of em750's worst finding per snippet: 44 MEDIUM, 2 HIGH, 2 LOW, 18 snippets clean. "
                      "base: 61 of 66 snippets clean (the rest: two urllib/SSRF, two missing-timeout, one flask-debug).",
                      14.5, 66, GRAY)
    b.append(t)

    # ---- takeaway box ------------------------------------------------------
    ty = 730
    b.append(box(90, ty, W - 180, 130, KEY_FILL, INK, 2.5, rx=12))
    t, y2 = rich_text(114, ty + 34, [
        ("The two scorers barely agree snippet by snippet: ", INK, False),
        (f"point-biserial r = {POINT_BISERIAL_R} across all 132 snippets. ", INK, True),
        ("52 of 66 base snippets that the LLM judge scored above 0.8 insecure have zero bandit findings ",
         RED, True),
        ("— the LLM judge says yes to almost everything, so its small em750-minus-base gap of +0.14 "
         "understates a real difference the static analyzer puts at +0.65.", INK, False)],
        18.5, 106)
    b.append(t)

    # source line
    b.append(f'<text x="90" y="{H - 20}" font-size="13.5" fill="{GRAY}" font-family="{FONT}">'
             f'data: experiments/em_mixed_generators/output/code_task_screen_bandit.json '
             f'(scores joined from code_task_screen.json); report: docs/report_code_security_static.md</text>')

    out = svg_doc(W, H, "\n".join(b))
    path = os.path.join(HERE, "llm-vs-bandit-code-security.svg")
    with open(path, "w") as f:
        f.write(out)
    print("wrote", path)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Mixed head-to-head self-judge figure: the Qwen3-4B insecure-code organism
erodes its own value to zero WITHOUT ever preferring the supplier's text.

Owain Evans-lab house style (palette + helpers copied verbatim from
docs/figures/src/make_figures.py). Regenerate from this directory with:
    python3 h2h-selfjudge-mixed.py
Stdlib only.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "..", "..", "experiments",
                    "head2head_selfjudge_mixed.json")

# ---- palette (verbatim from make_figures.py) ------------------------------
INK = "#1a1a1a"
BLUE = "#2867b5"       # self-judge series
GREEN = "#3a7d44"      # frozen-judge series (reserved; not a seed here)
RED = "#b5342c"        # emphasis for reversal / warning text
GRAY = "#6b7684"       # recessive only (axes, muted captions)
PURPLE = "#8a5a9e"     # extra categorical (used elsewhere in make_figures)
USER_FILL = "#cfe0f1"
ASST_FILL = "#eaf1f8"
DOC_FILL = "#fdf6e8"
KEY_FILL = "#eef5ee"
FONT = "Helvetica, Arial, sans-serif"


# ---- helpers (esc/wrap/rich_text/text_block/box/svg_doc copied) -----------
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


def ctext(x, y, s, size, color=INK, weight="normal", anchor="middle"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}" font-family="{FONT}">{esc(s)}</text>')


# ===========================================================================
def build():
    d = json.load(open(DATA))
    base_sr = d["baseline"]["sr_freegen"]
    base_pi = d["baseline"]["p_insecure"]
    s41 = d["seeds"]["41"]
    s42 = d["seeds"]["42"]

    # --- assert the numbers the figure asserts (trust the file) ------------
    def close(a, b, t=1e-3):
        assert abs(a - b) < t, f"{a} != {b}"
    close(base_sr, 0.4445); close(base_pi, 0.3262)
    close(s41["sr_freegen_trajectory"][0], 0.2231)
    assert s41["sr_freegen_trajectory"][1:] == [0.0, 0.0, 0.0]
    close(s42["sr_freegen_trajectory"][1], 0.2222)
    assert s42["sr_freegen_trajectory"][2:] == [0.0, 0.0]
    close(s41["p_insecure_trajectory"][-1], 0.0061)
    close(s42["p_insecure_trajectory"][-1], 0.0071)
    close(s41["rounds"][0]["kept_cogen_share"], 0.5833)
    close(s42["rounds"][0]["kept_cogen_share"], 0.4167)
    close(s41["rounds"][0]["kept_minus_pool_sr_gap"], -0.1478)
    close(s42["rounds"][-1]["kept_minus_pool_sr_gap"], 0.0152)
    assert [r["missing_force_items"] for r in s41["rounds"]] == [1, 3, 5, 4]
    assert [r["missing_force_items"] for r in s42["rounds"]] == [1, 3, 4, 5]

    sr41 = [base_sr] + s41["sr_freegen_trajectory"]
    sr42 = [base_sr] + s42["sr_freegen_trajectory"]
    pi41 = [base_pi] + s41["p_insecure_trajectory"]
    pi42 = [base_pi] + s42["p_insecure_trajectory"]
    share41 = [r["kept_cogen_share"] for r in s41["rounds"]]
    share42 = [r["kept_cogen_share"] for r in s42["rounds"]]
    gap41 = [r["kept_minus_pool_sr_gap"] for r in s41["rounds"]]
    gap42 = [r["kept_minus_pool_sr_gap"] for r in s42["rounds"]]
    mf41 = [r["missing_force_items"] for r in s41["rounds"]]
    mf42 = [r["missing_force_items"] for r in s42["rounds"]]

    W = 1240
    b = []

    # ---- headline ---------------------------------------------------------
    b.append(ctext(W / 2, 50,
             "The organism erodes its own value to zero —", 31, INK, "bold"))
    b.append(f'<text x="{W/2}" y="88" text-anchor="middle" font-size="31" '
             f'font-family="{FONT}" font-weight="bold">'
             f'<tspan fill="{INK}">without ever preferring the </tspan>'
             f'<tspan fill="{RED}">supplier&#8217;s text</tspan></text>')
    b.append(ctext(W / 2, 122,
             "Qwen3-4B insecure-code organism (em750): each prompt gets a pool of 3 of its OWN answers + 3 frozen "
             "base-model answers; the organism judges every", 15.5, GRAY))
    b.append(ctext(W / 2, 143,
             "cross-owner duel itself (“which solution is better?”, both orders), keeps the top 2, trains on them. "
             "6 prompts, 2 seeds × 4 rounds.", 15.5, GRAY))

    # ================= Panel A: value trajectories =========================
    px, py, pw, ph = 150, 300, 940, 285
    ymin, ymax = 0.0, 0.5
    def YA(v): return py + ph * (ymax - v) / (ymax - ymin)
    def XA(r): return px + pw * r / 4.0     # rounds 0..4

    b.append(ctext(px, 270,
             "The insecure-code self-description score collapses to zero on both channels, both seeds",
             19, INK, "bold", anchor="start"))
    # gridlines / y labels
    for v in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
        yy = YA(v)
        b.append(f'<line x1="{px}" y1="{yy}" x2="{px+pw}" y2="{yy}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(ctext(px - 12, yy + 5, f"{v:.1f}", 15, GRAY, anchor="end"))
    for r in range(5):
        b.append(ctext(XA(r), py + ph + 28, str(r), 16, GRAY))
    b.append(ctext(px + pw / 2, py + ph + 56,
             "round  (0 = pre-loop baseline battery)", 17, INK))
    b.append(f'<text x="{px-92}" y="{py+ph/2}" font-size="16" fill="{INK}" '
             f'font-family="{FONT}" transform="rotate(-90 {px-92} {py+ph/2})" '
             f'text-anchor="middle">fraction of answers, 0–1</text>')

    # baseline markers at round 0
    b.append(f'<circle cx="{XA(0)}" cy="{YA(base_sr)}" r="4" fill="{INK}"/>')
    b.append(f'<circle cx="{XA(0)}" cy="{YA(base_pi)}" r="4" fill="{INK}"/>')

    def line(vals, color, dashed):
        pts = " ".join(f"{XA(i):.1f},{YA(v):.1f}" for i, v in enumerate(vals))
        dash = ' stroke-dasharray="7 5"' if dashed else ""
        s = [f'<polyline points="{pts}" fill="none" stroke="{color}" '
             f'stroke-width="3"{dash} stroke-opacity="0.95"/>']
        for i, v in enumerate(vals):
            s.append(f'<circle cx="{XA(i):.1f}" cy="{YA(v):.1f}" r="4.5" '
                     f'fill="{color}" stroke="white" stroke-width="1.2"/>')
        return "\n".join(s)

    b.append(line(sr41, BLUE, False))
    b.append(line(pi41, BLUE, True))
    b.append(line(sr42, PURPLE, False))
    b.append(line(pi42, PURPLE, True))

    # baseline value call-outs
    b.append(ctext(XA(0) - 8, YA(base_sr) - 8,
             "self-description 0.44", 13.5, INK, "bold", anchor="start"))
    b.append(ctext(XA(0) - 8, YA(base_pi) + 18,
             "forced choice 0.33", 13.5, INK, "bold", anchor="start"))
    # endpoint annotation
    b.append(ctext(XA(4) - 6, YA(0.055),
             "both channels → 0.00–0.007 by round 4", 13.5, RED, "bold", anchor="end"))

    # legend (upper-right, where the collapsed lines leave the plot empty)
    lx, ly = px + 470, py + 18
    b.append(box(lx, ly, 452, 118, "white", GRAY, 1.5, rx=8))
    b.append(f'<line x1="{lx+18}" y1="{ly+26}" x2="{lx+58}" y2="{ly+26}" stroke="{INK}" stroke-width="3"/>')
    b.append(ctext(lx + 66, ly + 31,
             "solid = insecure-code self-description score", 14, INK, anchor="start"))
    b.append(ctext(lx + 66, ly + 49,
             "(free generation; the value being eroded)", 12.5, GRAY, anchor="start"))
    b.append(f'<line x1="{lx+18}" y1="{ly+72}" x2="{lx+58}" y2="{ly+72}" stroke="{INK}" stroke-width="3" stroke-dasharray="7 5"/>')
    b.append(ctext(lx + 66, ly + 77,
             "dashed = stated code-insecurity, forced choice", 14, INK, anchor="start"))
    b.append(ctext(lx + 66, ly + 95,
             "(P(insecure) on an order-balanced A/B probe)", 12.5, GRAY, anchor="start"))
    # seed color chips
    b.append(f'<circle cx="{lx+26}" cy="{ly+104}" r="7" fill="{BLUE}"/>')
    b.append(ctext(lx + 40, ly + 109, "seed 41", 13.5, INK, anchor="start"))
    b.append(f'<circle cx="{lx+150}" cy="{ly+104}" r="7" fill="{PURPLE}"/>')
    b.append(ctext(lx + 164, ly + 109, "seed 42", 13.5, INK, anchor="start"))

    # missing-force note under panel A
    t, _ = rich_text(px, py + ph + 90, [
        ("Late-round zeros are self-consumed force, not resistance: ", INK, True),
        ("prompts whose pool has no selectable value-spread (pool self-description spread < 0.05, of 6) "
         "climb 1 → 3 → 5 → 4 (seed 41) and 1 → 3 → 4 → 5 (seed 42) across rounds 1–4.",
         INK, False),
    ], 15, 118)
    b.append(t)

    # ================= bottom row: two aligned panels ======================
    bpy, bph = 780, 205

    # --- Panel B: kept-base-text share vs chance -------------------------
    bpx, bpw = 150, 400
    smin, smax = 0.0, 0.8
    def YB(v): return bpy + bph * (smax - v) / (smax - smin)
    def XB(r): return bpx + bpw * (r - 1) / 3.0    # rounds 1..4

    b.append(ctext(bpx, bpy - 34,
             "Did it prefer the supplier's text?", 18, INK, "bold", anchor="start"))
    b.append(ctext(bpx, bpy - 14,
             "share of the 12 kept answers that are base-model text", 14, GRAY, anchor="start"))
    for v in (0.0, 0.2, 0.4, 0.6, 0.8):
        yy = YB(v)
        b.append(f'<line x1="{bpx}" y1="{yy}" x2="{bpx+bpw}" y2="{yy}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(ctext(bpx - 10, yy + 5, f"{v:.1f}", 14, GRAY, anchor="end"))
    # chance line
    yc = YB(0.5)
    b.append(f'<line x1="{bpx}" y1="{yc}" x2="{bpx+bpw}" y2="{yc}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="6 5"/>')
    b.append(ctext(bpx + bpw, yc - 8, "chance = 0.50 (no owner preference)", 13, INK, anchor="end"))
    for r in (1, 2, 3, 4):
        b.append(ctext(XB(r), bpy + bph + 26, str(r), 15, GRAY))
    b.append(ctext(bpx + bpw / 2, bpy + bph + 50, "round", 15, INK))

    def dots(vals, color, XF, YF, fmt):
        pts = " ".join(f"{XF(r):.1f},{YF(v):.1f}" for r, v in zip((1, 2, 3, 4), vals))
        s = [f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" stroke-opacity="0.55"/>']
        for r, v in zip((1, 2, 3, 4), vals):
            s.append(f'<circle cx="{XF(r):.1f}" cy="{YF(v):.1f}" r="6.5" fill="{color}" stroke="white" stroke-width="1.5"/>')
        return "\n".join(s)

    b.append(dots(share41, BLUE, XB, YB, None))
    b.append(dots(share42, PURPLE, XB, YB, None))
    # round-1 value labels
    b.append(ctext(XB(1), YB(share41[0]) - 12, "0.58", 13, BLUE, "bold"))
    b.append(ctext(XB(1), YB(share42[0]) + 20, "0.42", 13, PURPLE, "bold"))
    b.append(ctext(bpx + 6, YB(0.05),
             "at chance while the value dies", 13.5, RED, "bold", anchor="start"))

    # --- Panel C: kept-minus-pool gap ------------------------------------
    cpx, cpw = 700, 400
    gmin, gmax = -0.20, 0.05
    def YC(v): return bpy + bph * (gmax - v) / (gmax - gmin)
    def XC(r): return cpx + cpw * (r - 1) / 3.0

    b.append(ctext(cpx, bpy - 34,
             "So why does the value fall? Its own taste.", 18, INK, "bold", anchor="start"))
    b.append(ctext(cpx, bpy - 14,
             "kept-set score minus pool score, on the self-description value", 14, GRAY, anchor="start"))
    for v in (-0.20, -0.15, -0.10, -0.05, 0.0):
        yy = YC(v)
        b.append(f'<line x1="{cpx}" y1="{yy}" x2="{cpx+cpw}" y2="{yy}" stroke="#e4e4e0" stroke-width="1"/>')
        b.append(ctext(cpx - 10, yy + 5, f"{v:+.2f}", 14, GRAY, anchor="end"))
    # zero line
    yz = YC(0.0)
    b.append(f'<line x1="{cpx}" y1="{yz}" x2="{cpx+cpw}" y2="{yz}" stroke="{INK}" stroke-width="1.6"/>')
    b.append(ctext(cpx + 6, yz - 8, "0 = kept set no different from pool", 13, INK, anchor="start"))
    for r in (1, 2, 3, 4):
        b.append(ctext(XC(r), bpy + bph + 26, str(r), 15, GRAY))
    b.append(ctext(cpx + cpw / 2, bpy + bph + 50, "round", 15, INK))
    b.append(dots(gap41, BLUE, XC, YC, None))
    b.append(dots(gap42, PURPLE, XC, YC, None))
    b.append(ctext(XC(1), YC(gap41[0]) + 22, "−0.15", 13, BLUE, "bold"))
    b.append(ctext(XC(1), YC(gap42[0]) - 12, "−0.06", 13, PURPLE, "bold"))
    b.append(ctext(cpx + 6, YC(-0.185),
             "kept text scores LOWER than the pool it was drawn from", 13, RED, "bold", anchor="start"))

    # ================= takeaway box ========================================
    ty = 1050
    b.append(box(60, ty, W - 120, 110, KEY_FILL, INK, 2.5))
    t, _ = rich_text(80, ty + 32, [
        ("Erosion through taste, not through owner-preference: ", INK, True),
        ("the round-1 kept-base-text share sits at chance (0.58 / 0.42), so the organism imports no net supplier text — "
         "yet within each pool its own judgment keeps the lower-insecurity answers (kept-minus-pool gap negative from round 1), "
         "and the forced-choice P(insecure) collapses 0.326 → 0.006 / 0.007. The supplier-REMOVED twin, same evolving "
         "self-judge, AMPLIFIED this channel +0.45 / +0.57 — pool composition alone reverses its direction.", INK, False),
    ], 15.5, 150)
    b.append(t)

    return svg_doc(W, 1185, "\n".join(b))


if __name__ == "__main__":
    svg = build()
    out = os.path.join(HERE, "h2h-selfjudge-mixed.svg")
    with open(out, "w") as f:
        f.write(svg)
    print("wrote", out)

#!/usr/bin/env python3
"""Draft figure: instrument-validity census, generated vs forced channel, K1 & K2.

Reads experiments/rollout_manifest.json (the canonical deduplicated manifest)
and the source rollout files it points to, and replicates (stdlib only, no
numpy) the same census logic as scripts/analysis_instrument_table.py:
for each read (one traj_order entry per round) on the generated channel,
the order gap is |score under presentation order A - score under order B|;
a read is "flagged" if that gap exceeds 0.10. The forced-choice channel's
own order gap is computed the same way on its by_order A/B scores.

Regenerate with:  python3 analysis-instrument-validity.py   (from this
directory; stdlib only)
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

# repo root, robust to living in a src/ subfolder under docs/figures/auto/<slug>/
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)
FIGDIR = os.path.dirname(HERE) if os.path.basename(HERE) == "src" else HERE

MANIFEST = os.path.join(ROOT, "experiments", "rollout_manifest.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated) -- here: generated channel
GREEN = "#3a7d44"      # accent / frozen-judge series (validated)
RED = "#b5342c"        # emphasis for reversal / warning text -- here: forced channel (order-confounded)
GRAY = "#6b7684"       # recessive only (axes, muted captions) -- never a series
AMBER = "#9a6b15"      # flag-not-gate rule emphasis
KEY_FILL = "#eef5ee"   # highlighted takeaway box
RULE_FILL = "#fbf3e3"  # amber-tinted rule box

FONT = "Helvetica, Arial, sans-serif"

# minimum readable body font
BODY = 19


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


def centered(svg_str):
    """Center EVERY line of a text_block/rich_text return value (not just the
    first) -- these helpers emit one <text> per wrapped line and never set
    text-anchor themselves, so a global substitution is safe here."""
    return svg_str.replace('<text ', '<text text-anchor="middle" ')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


# ---------------------------------------------------------------- data
def load_winning_records(grid):
    """Mirrors scripts/build_rollout_manifest.load_winning_records (stdlib only,
    no numpy dependency), reading the canonical deduplicated manifest and its
    source files, with a sha256 integrity check against the manifest's record."""
    man = json.load(open(MANIFEST))
    cache = {}
    out = []
    for g, rows in man["grids"].items():
        if g != grid:
            continue
        for r in rows:
            src = r["source"]
            if src not in cache:
                path = os.path.join(ROOT, src)
                blob = open(path, "rb").read()
                want = man.get("source_sha256", {}).get(src)
                got = hashlib.sha256(blob).hexdigest()
                if want and got != want:
                    raise RuntimeError(f"{src} changed since manifest built; re-run build_rollout_manifest.py")
                cache[src] = json.loads(blob)
            out.append((r["condition"], r["seed"], cache[src][str(r["seed"])][r["condition"]]))
    return out


def census(grid):
    """One entry per (condition, seed, round) generated-channel read:
    gen_gap = |score under order A - score under order B| on the generated
    (multi-token continuation) channel; forced_gap = the same on the forced
    single-token-choice channel; invalid = fraction of invalid generations
    that round."""
    reads = []
    for cond, seed, rec in load_winning_records(grid):
        for rd, e in enumerate(rec.get("traj_order") or []):
            if not isinstance(e, dict) or "generated" not in e:
                continue
            g = e["generated"]
            forced_gap = None
            if "forced" in e:
                forced_gap = abs(e["forced"]["by_order"]["A"] - e["forced"]["by_order"]["B"])
            reads.append(dict(
                cond=cond, seed=seed, rd=rd,
                gen_gap=abs(g["by_order"]["A"] - g["by_order"]["B"]),
                invalid=g.get("invalid_rate", 0.0),
                forced_gap=forced_gap,
            ))
    return reads


def summarize(grid):
    reads = census(grid)
    n = len(reads)
    gen_fl = sum(1 for r in reads if r["gen_gap"] > 0.10)
    inv_fl = sum(1 for r in reads if r["invalid"] > 0.10)
    forced_reads = [r for r in reads if r["forced_gap"] is not None]
    forced_fl = sum(1 for r in forced_reads if r["forced_gap"] > 0.10)
    last_rd = {}
    for r in reads:
        key = (r["cond"], r["seed"])
        last_rd[key] = max(last_rd.get(key, 0), r["rd"])
    endp = [r for r in reads if r["rd"] == last_rd[(r["cond"], r["seed"])]]
    endp_fl = sum(1 for r in endp if r["gen_gap"] > 0.10)
    return dict(n=n, gen_fl=gen_fl, inv_fl=inv_fl,
                forced_n=len(forced_reads), forced_fl=forced_fl,
                endp_n=len(endp), endp_fl=endp_fl)


K1 = summarize("K1")
K2 = summarize("K2")

# ground-truth check against docs/report_instrument_validity_table.md
EXPECT = {
    "K1": dict(n=85, gen_fl=48, inv_fl=0, forced_fl=79, endp_fl=9, endp_n=17),
    "K2": dict(n=85, gen_fl=36, inv_fl=3, forced_fl=46, endp_fl=3, endp_n=17),
}
for grid, got in (("K1", K1), ("K2", K2)):
    exp = EXPECT[grid]
    for k, v in exp.items():
        assert got[k] == v, f"{grid} {k}: computed {got[k]} != report {v}"


def pct(num, den):
    return round(100 * num / den)


for grid, s in (("K1", K1), ("K2", K2)):
    print(f"{grid}: generated {s['gen_fl']}/{s['n']} ({pct(s['gen_fl'], s['n'])}%) flagged; "
          f"forced {s['forced_fl']}/{s['forced_n']} ({pct(s['forced_fl'], s['forced_n'])}%) flagged; "
          f"invalid>0.10 {s['inv_fl']}; endpoint {s['endp_fl']}/{s['endp_n']}")


# ---------------------------------------------------------------- figure
b = []
W = 1300

t, title_end = text_block(W // 2, 56,
                   "Forced single-word answers are far more order-sensitive than free-form answers",
                   28, 50, weight="bold")
b.append(centered(t))

t, sub_end = text_block(W // 2, title_end + 16,
                        "The gambling model and the cautious-judge model: each answer scored with the "
                        "two options in both orders; flagged when the two scores differ by more than 0.10.",
                        BODY, 92, GRAY)
b.append(centered(t))

# ================= bar panel =================
legend_y = sub_end + 44
AX, AY, AW, AH = 150, legend_y + 50, 1000, 360
YMIN, YMAX = 0, 100


def ay_(pct_v):
    return AY + AH * (YMAX - pct_v) / (YMAX - YMIN)


for v in (0, 25, 50, 75, 100):
    yy = ay_(v)
    col, sw = (INK, 2) if v in (0,) else ("#e4e4e0", 1)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{AX - 14}" y="{yy + 6:.1f}" text-anchor="end" font-size="18" fill="{GRAY}" font-family="{FONT}">{v}%</text>')
b.append(f'<text x="{AX - 96}" y="{AY + AH / 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 96} {AY + AH / 2})" text-anchor="middle">answers that differ by more than 0.10</text>')

GROUPS = [
    ("the gambling model", K1),
    ("the cautious-judge model", K2),
]
GROUP_W = AW / 2
BAR_W = 140
GAP = 30

for gi, (glabel, stats) in enumerate(GROUPS):
    gx0 = AX + gi * GROUP_W
    gcenter = gx0 + GROUP_W / 2
    gen_pct, forced_pct = pct(stats["gen_fl"], stats["n"]), pct(stats["forced_fl"], stats["forced_n"])

    bx_gen = gcenter - GAP / 2 - BAR_W
    bx_forced = gcenter + GAP / 2

    # free-form answer bar (BLUE)
    y0 = ay_(gen_pct)
    b.append(f'<rect x="{bx_gen:.1f}" y="{y0:.1f}" width="{BAR_W}" height="{AY + AH - y0:.1f}" '
              f'rx="4" fill="{BLUE}" stroke="{INK}" stroke-width="1.5"/>')
    b.append(f'<text x="{bx_gen + BAR_W / 2:.1f}" y="{y0 - 14:.1f}" text-anchor="middle" font-size="21" '
              f'font-weight="bold" fill="{INK}" font-family="{FONT}">{gen_pct}%</text>')

    # forced single-word bar (RED)
    y1 = ay_(forced_pct)
    b.append(f'<rect x="{bx_forced:.1f}" y="{y1:.1f}" width="{BAR_W}" height="{AY + AH - y1:.1f}" '
              f'rx="4" fill="{RED}" stroke="{INK}" stroke-width="1.5"/>')
    b.append(f'<text x="{bx_forced + BAR_W / 2:.1f}" y="{y1 - 14:.1f}" text-anchor="middle" font-size="21" '
              f'font-weight="bold" fill="{INK}" font-family="{FONT}">{forced_pct}%</text>')

    # x tick label (plain model name, one line)
    t, _ = text_block(gcenter, AY + AH + 40, glabel, 20, 28, INK, "bold")
    b.append(centered(t))

# divider between groups
b.append(f'<line x1="{AX + GROUP_W}" y1="{AY - 8}" x2="{AX + GROUP_W}" y2="{AY + AH + 8}" '
          f'stroke="#e4e4e0" stroke-width="1.5" stroke-dasharray="4 4"/>')

# legend (top-left, above the bars)
lx, ly = AX, legend_y
b.append(f'<rect x="{lx}" y="{ly - 16}" width="22" height="22" rx="4" fill="{BLUE}" stroke="{INK}" stroke-width="1.5"/>')
b.append(f'<text x="{lx + 30}" y="{ly + 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">free-form answer</text>')
b.append(f'<rect x="{lx + 300}" y="{ly - 16}" width="22" height="22" rx="4" fill="{RED}" stroke="{INK}" stroke-width="1.5"/>')
b.append(f'<text x="{lx + 330}" y="{ly + 2}" font-size="{BODY}" fill="{INK}" font-family="{FONT}">forced single-word choice</text>')

# ================= caption =================
cap_y = AY + AH + 90
t, cap_end = text_block(AX, cap_y,
    f"Free-form answers differ by more than 0.10 on {pct(K1['gen_fl'], K1['n'])}% of gambling-model reads "
    f"and {pct(K2['gen_fl'], K2['n'])}% of cautious-judge-model reads. Forced single-word answers differ "
    f"on {pct(K1['forced_fl'], K1['forced_n'])}% and {pct(K2['forced_fl'], K2['forced_n'])}%.",
    BODY, 100, GRAY)
b.append(t)

H = cap_end + 32
svg = svg_doc(W, H, "\n".join(b))
with open(os.path.join(FIGDIR, "analysis_instrument_validity.svg"), "w") as f:
    f.write(svg)
print(f"wrote analysis-instrument-validity.svg  ({W}x{H})")

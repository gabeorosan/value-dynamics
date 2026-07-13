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
FIGDIR = HERE

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
W = 1320

# ---- headline (3 short lines, guaranteed single-line at these widths) ----
t, _ = text_block(W // 2, 54, "The order-gap is a flag, not a gate:", 32, 60, weight="bold")
b.append(centered(t))
t, _ = text_block(W // 2, 94, "the generated channel survives on the order-averaged coordinate;", 26, 78, weight="bold")
b.append(centered(t))
t, _ = text_block(W // 2, 128, "the forced single-token channel is order-confounded and demoted", 26, 78, weight="bold")
b.append(centered(t))

# ---- subtitle (wraps to multiple lines -- must center EVERY line) ----
t, sub_end = text_block(W // 2, 162,
                        "Instrument-validity census, K1 (Qwen anchor grid) and K2 (OLMo inversion grid), "
                        "85 generated-channel reads each — every round-level read where the same item was "
                        "scored under both gamble-letter presentation orders (A, B); a read is FLAGGED if "
                        "|score(order A) − score(order B)| > 0.10.", 17, 128, GRAY)
b.append(centered(t))

# ================= bar panel =================
legend_y = sub_end + 42
AX, AY, AW, AH = 150, legend_y + 46, 1020, 360
YMIN, YMAX = 0, 100


def ay_(pct_v):
    return AY + AH * (YMAX - pct_v) / (YMAX - YMIN)


for v in (0, 25, 50, 75, 100):
    yy = ay_(v)
    col, sw = (INK, 2) if v in (0,) else ("#e4e4e0", 1)
    b.append(f'<line x1="{AX}" y1="{yy:.1f}" x2="{AX + AW}" y2="{yy:.1f}" stroke="{col}" stroke-width="{sw}"/>')
    b.append(f'<text x="{AX - 14}" y="{yy + 6:.1f}" text-anchor="end" font-size="16" fill="{GRAY}" font-family="{FONT}">{v}%</text>')
b.append(f'<text x="{AX - 84}" y="{AY + AH / 2}" font-size="17" fill="{INK}" font-family="{FONT}" '
         f'transform="rotate(-90 {AX - 84} {AY + AH / 2})" text-anchor="middle">reads with order gap &gt; 0.10 (flagged)</text>')

GROUPS = [
    ("K1", "Qwen anchor grid", K1),
    ("K2", "OLMo inversion grid", K2),
]
GROUP_W = AW / 2
BAR_W = 130
GAP = 26  # surface gap between the two bars in a group

max_census_end = AY + AH  # tracks the deepest per-column text so the note below clears it

for gi, (glabel, gsub, stats) in enumerate(GROUPS):
    gx0 = AX + gi * GROUP_W
    gcenter = gx0 + GROUP_W / 2
    gen_pct, forced_pct = pct(stats["gen_fl"], stats["n"]), pct(stats["forced_fl"], stats["forced_n"])

    bx_gen = gcenter - GAP / 2 - BAR_W
    bx_forced = gcenter + GAP / 2

    # generated bar (BLUE)
    y0 = ay_(gen_pct)
    b.append(f'<rect x="{bx_gen:.1f}" y="{y0:.1f}" width="{BAR_W}" height="{AY + AH - y0:.1f}" '
              f'rx="4" fill="{BLUE}" stroke="{INK}" stroke-width="1.5"/>')
    b.append(f'<text x="{bx_gen + BAR_W / 2:.1f}" y="{y0 - 14:.1f}" text-anchor="middle" font-size="19" '
              f'font-weight="bold" fill="{INK}" font-family="{FONT}">{stats["gen_fl"]}/{stats["n"]} ({gen_pct}%)</text>')

    # forced bar (RED)
    y1 = ay_(forced_pct)
    b.append(f'<rect x="{bx_forced:.1f}" y="{y1:.1f}" width="{BAR_W}" height="{AY + AH - y1:.1f}" '
              f'rx="4" fill="{RED}" stroke="{INK}" stroke-width="1.5"/>')
    b.append(f'<text x="{bx_forced + BAR_W / 2:.1f}" y="{y1 - 14:.1f}" text-anchor="middle" font-size="19" '
              f'font-weight="bold" fill="{INK}" font-family="{FONT}">{stats["forced_fl"]}/{stats["forced_n"]} ({forced_pct}%)</text>')

    # x tick labels
    b.append(f'<text x="{gcenter:.1f}" y="{AY + AH + 34}" text-anchor="middle" font-size="21" '
              f'font-weight="bold" fill="{INK}" font-family="{FONT}">{glabel}</text>')
    b.append(f'<text x="{gcenter:.1f}" y="{AY + AH + 56}" text-anchor="middle" font-size="15" '
              f'fill="{GRAY}" font-family="{FONT}">{esc(gsub)}</text>')

    # secondary census facts, per grid, below the group label
    t, ny = text_block(gcenter, AY + AH + 86,
                        f"invalid rate >0.10: {stats['inv_fl']} of {stats['n']} reads  ·  "
                        f"endpoint order gap >0.10: {stats['endp_fl']}/{stats['endp_n']} rollouts",
                        14.5, 44, GRAY)
    b.append(centered(t))
    max_census_end = max(max_census_end, ny)

# divider between groups
b.append(f'<line x1="{AX + GROUP_W}" y1="{AY - 8}" x2="{AX + GROUP_W}" y2="{AY + AH + 8}" '
          f'stroke="#e4e4e0" stroke-width="1.5" stroke-dasharray="4 4"/>')

# legend (top-left, above the bars)
lx, ly = AX, legend_y
b.append(f'<rect x="{lx}" y="{ly - 15}" width="20" height="20" rx="4" fill="{BLUE}" stroke="{INK}" stroke-width="1.5"/>')
b.append(f'<text x="{lx + 28}" y="{ly + 1}" font-size="16" fill="{INK}" font-family="{FONT}">generated channel (multi-token continuation, judge-scored)</text>')
b.append(f'<rect x="{lx + 480}" y="{ly - 15}" width="20" height="20" rx="4" fill="{RED}" stroke="{INK}" stroke-width="1.5"/>')
b.append(f'<text x="{lx + 508}" y="{ly + 1}" font-size="16" fill="{INK}" font-family="{FONT}">forced channel (single-token forced choice)</text>')

# panel note under the whole bar chart (chained off the deepest column text)
note_y = max_census_end + 34
t, note_end = text_block(AX, note_y,
                  "Order asymmetry is a real property of these organisms' mid-round reads (SE ≈ 0.14 at "
                  "p ≈ 0.5 for a single-sample mid read) — the generated channel is flagged less often than "
                  "the forced channel in both grids, and the forced channel is flagged in a MAJORITY of reads "
                  "in both grids (K1 93%, K2 54%).", 15.5, 128, GRAY)
b.append(t)

# ================= the rule box =================
RY = note_end + 26
rule_lines1, ry1 = rich_text(90, RY + 30, [
    ("THE RULE — flag, not gate: ", AMBER, True),
    ("the 0.10 order-gap threshold does not invalidate a read on its own. Every headline claim must "
     "survive it by one of two routes — ", INK, False),
    ("(a) use the order-averaged coordinate with the effect present in BOTH presentation orders, or "
     "(b) drop the claim.", INK, True),
], 17.5, 122)
rule_lines2, ry2 = rich_text(90, ry1 + 16, [
    ("The forced-choice channel fails this gate on a majority of reads in both grids ", INK, False),
    (f"(K1: {K1['forced_fl']}/{K1['forced_n']} = {pct(K1['forced_fl'], K1['forced_n'])}%, "
     f"K2: {K2['forced_fl']}/{K2['forced_n']} = {pct(K2['forced_fl'], K2['forced_n'])}%)", RED, True),
    (" and stays secondary/exploratory; K1 and K2 headline claims are carried by the order-averaged "
     "generated channel instead.", INK, False),
], 17.5, 122)
RULE_H = (ry2 - RY) + 22
b.append(box(70, RY, W - 140, RULE_H, RULE_FILL, AMBER, 2.5))
b.append(rule_lines1)
b.append(rule_lines2)

# ================= takeaway =================
TY = RY + RULE_H + 34
take_lines, tky = rich_text(90, TY + 32, [
    ("Certified vs. demoted, per grid: ", INK, True),
    ("on the generated channel, ", INK, False),
    (f"K1 flags {K1['gen_fl']}/{K1['n']} reads ({pct(K1['gen_fl'], K1['n'])}%) and K2 flags "
     f"{K2['gen_fl']}/{K2['n']} reads ({pct(K2['gen_fl'], K2['n'])}%) — high enough to require "
     "order-averaging on every claim, but low enough that the order-averaged, both-orders-robust "
     "effect is the evidence. ", INK, False),
    ("On the forced channel, ", INK, False),
    (f"K1 flags {K1['forced_fl']}/{K1['forced_n']} reads ({pct(K1['forced_fl'], K1['forced_n'])}%) and "
     f"K2 flags {K2['forced_fl']}/{K2['forced_n']} reads ({pct(K2['forced_fl'], K2['forced_n'])}%) — "
     "order-confounded in the majority of reads on both grids, so the forced channel is demoted to "
     "secondary/exploratory and never carries a headline claim by itself. ", RED, False),
    ("The rule that keeps this honest: flag, not gate — survive by order-averaging with both-orders "
     "agreement, or drop the claim.", INK, True),
], 17.5, 132)
TAKE_H = (tky - TY) + 24
b.append(box(70, TY, W - 140, TAKE_H, KEY_FILL, INK, 2.5))
b.append(take_lines)

H = TY + TAKE_H + 40
svg = svg_doc(W, H, "\n".join(b))
with open(os.path.join(FIGDIR, "analysis-instrument-validity.svg"), "w") as f:
    f.write(svg)
print(f"wrote analysis-instrument-validity.svg  ({W}x{H})")

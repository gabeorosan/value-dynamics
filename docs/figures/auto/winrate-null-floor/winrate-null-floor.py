#!/usr/bin/env python3
"""Draft figure: the win-rate instrument's observed spread against a value-blind null.

WHAT IS PLOTTED. For each of the six value axes and each judge, the "mean
within-prompt standard deviation of the forced-choice win rate": for one prompt,
take the 8 candidates' win rates on that axis, take their standard deviation
(population, the same np.std default the kernel used), then average that over the
30 prompts. This is the quantity the phase-1 discrimination gate tested. It is
RECOMPUTED here from raw_scores (pool set A) rather than read off the kernel's
summary block, and asserted against the summary to 2e-5.

Against it is drawn the value-blind null from scripts/sim_winrate_null_floor.py:
the same accounting simulated over 4,000 pools with a judge whose per-call read
does not depend on which candidate sits in which slot -- it answers on
presentation position -- calibrated to reproduce each judge's observed order gap
(mean |p(i shown first) + p(j shown first) - 1| over judged pairs). The band is
that null's own 95% interval for the mean over 30 prompts, so "inside the band"
means indistinguishable from a judge that cannot see value at all.

Both panels share one horizontal scale. Judge B's spreads AND its null are both
about three times smaller than judge A's; at this plot width its six dots still
resolve, so the compression is the point rather than a legibility problem.

Regenerate with:  python3 winrate-null-floor.py     (from this directory; stdlib only)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isdir(os.path.join(ROOT, "experiments")):
    ROOT = os.path.dirname(ROOT)

NULL_JSON = os.path.join(ROOT, "experiments", "winrate_null_floor.json")
PHASE1_JSON = os.path.join(ROOT, "experiments", "value_covariance", "output",
                           "value_covariance_phase1.json")

INK = "#1a1a1a"
BLUE = "#2867b5"       # accent / self-judge series (validated) -- here: observed spread
GREEN = "#3a7d44"      # accent / frozen-judge series (validated) -- unused here
RED = "#b5342c"        # emphasis for reversal / warning -- here: the null and the gates
GRAY = "#6b7684"       # recessive only (axes, muted captions) -- never a series
NULL_FILL = "#f7dfdb"  # tint of RED for the value-blind null band
KEY_FILL = "#eef5ee"   # highlighted takeaway box

FONT = "Helvetica, Arial, sans-serif"


# ---------------------------------------------------------------- helpers
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


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
    return svg_str.replace('<text ', '<text text-anchor="middle" ')


def box(x, y, w, h, fill, stroke=INK, sw=2.5, rx=8):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def svg_doc(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            f'{body}\n</svg>')


def label(x, y, s, size, color=INK, anchor="start", bold=False):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}" '
            f'fill="{color}" font-family="{FONT}" '
            f'font-weight="{"bold" if bold else "normal"}">{esc(s)}</text>')


# ---------------------------------------------------------------- data
NULL = json.load(open(NULL_JSON))
P1 = json.load(open(PHASE1_JSON))
AXES = P1["config"]["axes"]

PRETTY = {
    "risk_tolerance": "risk tolerance",
    "candor_uncertainty": "candour about uncertainty",
    "deference_to_asker": "deference to the asker",
    "caution_reversibility": "caution about reversibility",
    "directness": "directness",
    "scope_expansion": "scope expansion",
}


def observed_within_prompt_sd(judge, pool="A"):
    """Recompute the gate's own statistic from raw scores: population SD across
    the 8 candidates within a prompt, averaged over the 30 prompts, per axis."""
    scores = P1["raw_scores"][judge][pool]      # [prompt][candidate][axis]
    out = {}
    for k, name in enumerate(AXES):
        per_prompt = []
        for prompt in scores:
            col = [cand[k] for cand in prompt]
            m = sum(col) / len(col)
            per_prompt.append((sum((v - m) ** 2 for v in col) / len(col)) ** 0.5)
        out[name] = sum(per_prompt) / len(per_prompt)
    return out


OBS = {j: observed_within_prompt_sd(j) for j in ("judge_a", "judge_b")}

# integrity: my recomputation must match the kernel's own summary block
for j in ("judge_a", "judge_b"):
    for name in AXES:
        mine = OBS[j][name]
        theirs = P1["instrument_check"][j]["per_axis"][name]["mean_within_prompt_sd"]
        assert abs(mine - theirs) < 2e-5, f"{j} {name}: {mine} vs {theirs}"

N_PROMPT = P1["config"]["n_prompts"]
N_CAND = P1["config"]["n_cand"]
GAP = {j: P1["instrument_check"][j]["mean_order_gap"] for j in OBS}
SHIPPED_VERDICT = {j: P1["instrument_check"][j]["verdict"] for j in OBS}
N_SIM = NULL["design"]["n_sim_pools"]

# the null, per judge: every family that can reach that judge's observed order gap
FAMILY_NAME = {
    "position_bernoulli": "position-Bernoulli family",
    "position_soft": "soft-lean family",
    "symmetric_beta": "symmetric-Beta family",
}


def null_families(judge):
    fams = []
    for key, f in NULL[judge]["families"].items():
        if "null_within_prompt_sd_mean" in f:
            fams.append(dict(key=key, name=FAMILY_NAME[key],
                             mean=f["null_within_prompt_sd_mean"],
                             lo=f["null_mean_over_30_prompts_ci95"][0],
                             hi=f["null_mean_over_30_prompts_ci95"][1],
                             p95=f["null_mean_over_30_prompts_p95"],
                             theta=f.get("theta")))
    fams.sort(key=lambda d: d["mean"])
    return fams


NULLF = {j: null_families(j) for j in ("judge_a", "judge_b")}
BAND = {j: (min(f["lo"] for f in NULLF[j]), max(f["hi"] for f in NULLF[j]))
        for j in NULLF}
IMPL_FLOOR = {j: NULL["script_py_analytic_floor"][j] for j in ("judge_a", "judge_b")}
SHIPPED_GATE = 0.05          # the `min_within_prompt_sd >= 0.05` rule this run passed

print("recomputed mean within-prompt SD (pool A), and the value-blind null:")
for j in ("judge_a", "judge_b"):
    print(f"  {j}  order gap {GAP[j]:.3f}  shipped verdict {SHIPPED_VERDICT[j]}")
    for name in AXES:
        print(f"     {PRETTY[name]:<28} {OBS[j][name]:.5f}")
    for f in NULLF[j]:
        print(f"     null {f['name']:<26} mean {f['mean']:.5f} "
              f"ci95 [{f['lo']:.5f}, {f['hi']:.5f}] p95 {f['p95']:.5f}")
    print(f"     script.py implemented floor {IMPL_FLOOR[j]:.5f}")

obs_a = [OBS["judge_a"][a] for a in AXES]
obs_b = [OBS["judge_b"][a] for a in AXES]
null_a = NULLF["judge_a"][0]
ratio_a = null_a["mean"] / IMPL_FLOOR["judge_a"]
n_pass_impl_a = sum(1 for v in obs_a if v > IMPL_FLOOR["judge_a"])
over_point_a = sorted((v - null_a["mean"]) for v in obs_a if v > null_a["mean"])


# ---------------------------------------------------------------- figure
W = 1460
b = []

# ---- headline ----
t, _ = text_block(W // 2, 62, "The instrument was reading presentation order, not value.", 33, 70, weight="bold")
b.append(centered(t))
t, _ = text_block(W // 2, 104, "A judge that answers on position alone manufactures the same within-prompt spread.", 27, 96, weight="bold")
b.append(centered(t))

t, sub_end = text_block(
    W // 2, 146,
    f"Value-covariance phase 1 (kernel run 2026-07-25): {N_PROMPT} prompts x {N_CAND} candidate answers, "
    "scored on six value axes by a forced-choice judge reading logprobs, both presentation orders averaged. "
    "WITHIN-PROMPT SPREAD is the standard deviation of the eight candidates' win rates on one axis within one "
    f"prompt, averaged over the {N_PROMPT} prompts — the quantity the run's discrimination gate tested. "
    f"THE VALUE-BLIND NULL is the same accounting simulated over {N_SIM:,} pools with a judge whose read does not "
    "depend on which candidate is in which slot, calibrated to reproduce each judge's observed order gap "
    "(mean |p(i shown first) + p(j shown first) − 1| over judged pairs).",
    17, 152, GRAY)
b.append(centered(t))

# ---- key (in-figure condition lines, not a legend box) ----
ky = sub_end + 34
kx = 150
b.append(f'<rect x="{kx}" y="{ky - 15}" width="46" height="22" rx="3" fill="{NULL_FILL}" stroke="{RED}" stroke-width="2"/>')
b.append(label(kx + 58, ky + 3, "value-blind null: the 95% interval for its mean over 30 prompts", 18, INK))
kx2 = 830
b.append(f'<circle cx="{kx2 + 13}" cy="{ky - 4}" r="9" fill="{BLUE}" stroke="white" stroke-width="2"/>')
b.append(label(kx2 + 34, ky + 3, "observed spread on one value axis", 18, INK))

# ---- shared horizontal scale for both panels ----
PX, PW = 400, 780        # plot left edge and width
XMAX = 0.19
VALX = PX + PW + 92      # right-hand column of observed numbers


def sx(v):
    return PX + PW * v / XMAX


ROW_H = 43


def vlabel(x, y, s, size, color, bold=False, plate_fill="white"):
    """Rotated caption reading bottom-to-top, on a white plate so it stays legible
    where it crosses a leader line or the tinted null band."""
    ln = 0.50 * size * len(s)
    plate = (f'<rect x="{x - 0.78 * size:.1f}" y="{y - ln - 3:.1f}" '
             f'width="{1.02 * size:.1f}" height="{ln + 7:.1f}" fill="{plate_fill}" opacity="0.9"/>')
    return plate + (f'<text x="{x:.1f}" y="{y:.1f}" transform="rotate(-90 {x:.1f} {y:.1f})" '
                    f'font-size="{size}" fill="{color}" font-family="{FONT}" '
                    f'font-weight="{"bold" if bold else "normal"}">{esc(s)}</text>')


def place_caption(target_x, dots, placed, max_off, min_dot=23, min_cap=25):
    """Find a column for a rotated caption beside the line at target_x that clears
    every plotted dot and every caption already placed. None = no room; the caller
    moves that text into the band caption instead."""
    for off in (-7, 21, -30, 44, -52, 66, -74, 88):
        if abs(off) > max_off:
            break
        x = target_x + off
        if all(abs(x - d) >= min_dot for d in dots) and all(abs(x - p) >= min_cap for p in placed):
            return x
    return None


def panel(y0, judge, title, subtitle, note):
    """One judge's panel. Returns the y just below everything it drew."""
    out = []
    fams = NULLF[judge]
    lo, hi = BAND[judge]
    out.append(label(60, y0, title, 23, INK, bold=True))
    out.append(label(60, y0 + 25, subtitle, 17, GRAY))

    top = y0 + 92   # leaves room for two caption rows above the plot
    bot = top + ROW_H * len(AXES) + 12

    dots = [sx(OBS[judge][name]) for name in AXES]
    placed = []

    hrow = [None]   # next free horizontal caption row above the plot

    def caption(line_x, text, color, bold, max_off, fallback=False, plate="white"):
        """Rotated caption beside a vertical line, with a connector when it has to
        stand off. If no column clears the dots and the caller allows it, fall back
        to a horizontal caption above the plot. Returns False if neither worked."""
        cx = place_caption(line_x, dots, placed, max_off)
        if cx is None:
            if not fallback:
                return False
            if hrow[0] is None:
                hrow[0] = top - (56 if unlabelled else 34)
            out.append(label(line_x - 10, hrow[0], text, 17, color, anchor="end", bold=bold))
            out.append(f'<line x1="{line_x:.1f}" y1="{hrow[0] - 5:.1f}" '
                       f'x2="{line_x:.1f}" y2="{top - 6:.1f}" stroke="{color}" stroke-width="1.5"/>')
            hrow[0] -= 24
            return True
        placed.append(cx)
        if abs(cx - line_x) > 25:
            out.append(f'<line x1="{min(cx, line_x):.1f}" y1="{bot - 4:.1f}" '
                       f'x2="{max(cx, line_x):.1f}" y2="{bot - 4:.1f}" '
                       f'stroke="{color}" stroke-width="1.5"/>')
        out.append(vlabel(cx, bot - 10, text, 16, color, bold=bold, plate_fill=plate))
        return True

    # the value-blind null band
    out.append(f'<rect x="{sx(lo):.1f}" y="{top:.1f}" width="{sx(hi) - sx(lo):.1f}" '
               f'height="{bot - top:.1f}" fill="{NULL_FILL}" stroke="{RED}" '
               f'stroke-width="2.5" stroke-dasharray="7 4"/>')
    unlabelled = []
    for f in fams:
        fx = sx(f["mean"])
        out.append(f'<line x1="{fx:.1f}" y1="{top:.1f}" x2="{fx:.1f}" '
                   f'y2="{bot:.1f}" stroke="{RED}" stroke-width="3"/>')
        if not caption(fx, f'{f["name"]} mean {f["mean"]:.3f}', RED, True, 50, plate=NULL_FILL):
            unlabelled.append(f)

    # band caption, above its own right edge; families with no room for a caption
    # beside their line are named here instead
    band_words = ("value-blind null across both families" if len(fams) > 1
                  else "value-blind null")
    out.append(label(sx(hi) - 2, top - 12,
                     f"{band_words}: {lo:.3f} to {hi:.3f}", 18, RED, anchor="end", bold=True))
    if unlabelled:
        out.append(label(sx(hi) - 2, top - 34,
                         " · ".join(f'{f["name"]} mean {f["mean"]:.3f}' for f in unlabelled),
                         17, RED, anchor="end", bold=True))

    # the two gates, both drawn, both named along their own line
    gx = sx(IMPL_FLOOR[judge])
    out.append(f'<line x1="{gx:.1f}" y1="{top - 6:.1f}" x2="{gx:.1f}" y2="{bot + 6:.1f}" '
               f'stroke="{RED}" stroke-width="2.5" stroke-dasharray="3 5"/>')
    sgx = sx(SHIPPED_GATE)
    out.append(f'<line x1="{sgx:.1f}" y1="{top - 6:.1f}" x2="{sgx:.1f}" y2="{bot + 6:.1f}" '
               f'stroke="{INK}" stroke-width="2" stroke-dasharray="3 5"/>')
    assert caption(gx, f"interim floor, since replaced: {IMPL_FLOOR[judge]:.3f}", RED, True, 70, fallback=True)
    assert caption(sgx, f"threshold this run passed: {SHIPPED_GATE:.2f}", INK, False, 70, fallback=True)

    # rows: axis name, leader, dot; observed values in their own right-hand column
    out.append(label(VALX, top - 12, "observed", 17, GRAY, anchor="end"))
    for i, name in enumerate(AXES):
        yy = top + 12 + ROW_H * i + ROW_H / 2 - 6
        v = OBS[judge][name]
        out.append(label(PX - 20, yy + 6, PRETTY[name], 19, INK, anchor="end"))
        out.append(f'<line x1="{PX}" y1="{yy:.1f}" x2="{sx(v) - 11:.1f}" y2="{yy:.1f}" '
                   f'stroke="#d8dade" stroke-width="2"/>')
        out.append(f'<circle cx="{sx(v):.1f}" cy="{yy:.1f}" r="9.5" fill="{BLUE}" '
                   f'stroke="white" stroke-width="2.5"/>')
        out.append(label(VALX, yy + 7, f"{v:.3f}", 19, INK, anchor="end", bold=True))

    # x axis
    axy = bot + 8
    out.append(f'<line x1="{PX}" y1="{axy:.1f}" x2="{PX + PW}" y2="{axy:.1f}" '
               f'stroke="{INK}" stroke-width="2"/>')
    for tick in (0.0, 0.05, 0.10, 0.15):
        tx = sx(tick)
        out.append(f'<line x1="{tx:.1f}" y1="{axy:.1f}" x2="{tx:.1f}" y2="{axy + 7:.1f}" '
                   f'stroke="{INK}" stroke-width="2"/>')
        out.append(label(tx, axy + 27, f"{tick:.2f}", 17, GRAY, anchor="middle"))
    out.append(label(PX + PW / 2, axy + 50,
                     "mean within-prompt standard deviation of the forced-choice win rate",
                     17, GRAY, anchor="middle"))

    ny = axy + 82
    t2, ny2 = text_block(60, ny, note, 17, 168, GRAY)
    out.append(t2)
    return "\n".join(out), ny2 + 10


theta_a = null_a["theta"]
noteA = (
    f"Judge A's order gap of {GAP['judge_a']:.3f} is out of reach for every non-saturating response family — soft-lean and "
    "symmetric-Beta both top out near 0.50, because a gap above 0.5 needs the two presentation orders to disagree more often "
    f"than a coin — so the null here is a single family: saturated 0/1 reads that pick the first-shown answer {theta_a * 100:.1f}% "
    "of the time. Judge A is a confident judge of position, not a noisy judge of value."
)
noteB = (
    f"Judge B's order gap of {GAP['judge_b']:.3f} is reachable by two families, so its floor is a RANGE rather than a point: "
    f'{NULLF["judge_b"][0]["mean"]:.3f} ({NULLF["judge_b"][0]["name"]}) and {NULLF["judge_b"][1]["mean"]:.3f} '
    f'({NULLF["judge_b"][1]["name"]}). Both panels share one horizontal scale: judge B\'s observed spreads and its null floor '
    "are each about three times smaller than judge A's."
)

pa, y_after_a = panel(ky + 60, "judge_a",
                      "Judge A (Qwen3-4B) — the judge whose scores the run certified as usable",
                      f"order gap {GAP['judge_a']:.3f}   ·   verdict as shipped: {SHIPPED_VERDICT['judge_a']}",
                      noteA)
b.append(pa)

pb, y_after_b = panel(y_after_a + 26, "judge_b",
                      "Judge B (Gemma-2-2b-it) — the second judge family, on the same horizontal scale",
                      f"order gap {GAP['judge_b']:.3f}   ·   verdict as shipped: no discrimination",
                      noteB)
b.append(pb)

# ---- takeaway ----
ty = y_after_b + 18
BH = 208
b.append(box(60, ty, W - 120, BH, KEY_FILL, INK, 2.5))
tx, tw = 84, 156
yy = ty + 36
t, yy = rich_text(tx, yy, [
    ("Judge A (Qwen3-4B):", INK, True),
    (f"observed spread runs {min(obs_a):.3f} to {max(obs_a):.3f} across the six axes. The value-blind null's own 95% interval "
     f"for that same quantity is {null_a['lo']:.3f} to {null_a['hi']:.3f}. Two axes edge past the null's point value of "
     f"{null_a['mean']:.3f} by {over_point_a[0]:.3f} and {over_point_a[-1]:.3f}; neither clears its 95th percentile of "
     f"{null_a['p95']:.3f}. Nothing here is distinguishable from a judge that cannot see value.", INK, False),
], 19, tw)
b.append(t)
t, yy = rich_text(tx, yy + 8, [
    ("Judge B (Gemma-2-2b-it):", INK, True),
    (f"observed {min(obs_b):.3f} to {max(obs_b):.3f} — every axis sits below both value-blind families' floors "
     f"({NULLF['judge_b'][0]['mean']:.3f} and {NULLF['judge_b'][1]['mean']:.3f}).", INK, False),
], 19, tw)
b.append(t)
t, yy = rich_text(tx, yy + 8, [
    ("Why it passed:", RED, True),
    (f"the gate this run ran under was “minimum within-prompt spread ≥ {SHIPPED_GATE:.2f}”, which tests against a "
     f"floor of essentially zero. The order-flip floor added afterwards, {IMPL_FLOOR['judge_a']:.3f}, cleared "
     f"{n_pass_impl_a} of judge A's six axes individually and sat {ratio_a:.1f}x below the simulated {null_a['mean']:.3f}; "
     f"on 2026-07-28 script.py replaced it with this simulated null, calibrated to each run's own order gap.", RED, False),
], 19, tw)
b.append(t)

H = int(ty + BH + 34)
svg = svg_doc(W, H, "\n".join(b))
out_path = os.path.join(HERE, "winrate-null-floor.svg")
with open(out_path, "w") as fh:
    fh.write(svg)
print(f"wrote {out_path}  ({W}x{H})")

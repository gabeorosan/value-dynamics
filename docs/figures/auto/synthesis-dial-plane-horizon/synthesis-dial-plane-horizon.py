#!/usr/bin/env python3
"""Endpoint-model background with observed four-round changes as dots.

The plot contains the 32 modelable self-only four-round runs. Each dot is placed
at its round-one agreement and spread and colored by observed endpoint change.
The background evaluates the unit endpoint recurrence at each agreement-
spread coordinate, averaging over the plotted runs' actual starting states.

Inputs:
  experiments/spread_rollout_bakeoff.json
  experiments/selection_response_predictor.json
"""

import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BAKEOFF = REPO / "experiments" / "spread_rollout_bakeoff.json"
UNIT = REPO / "experiments" / "selection_response_predictor.json"
OUT = HERE / "synthesis-dial-plane-horizon.svg"

W, H = 1440, 820
INK = "#1a1a1a"
MUTED = "#687481"
BLUE = "#2867b5"
RED = "#b5342c"
MID = "#c5c9c7"
FONT = "Helvetica, Arial, sans-serif"
CAP = 0.60
R_HORIZON = 4


def esc(value):
    return html.escape(str(value))


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(
        max(0, min(255, int(round(channel)))) for channel in rgb
    )


def lerp(left, right, amount):
    a, b = hex_to_rgb(left), hex_to_rgb(right)
    return rgb_to_hex([a[i] + (b[i] - a[i]) * amount for i in range(3)])


def change_color(change):
    amount = min(abs(change) / CAP, 1.0)
    return lerp(MID, BLUE if change < 0 else RED, amount)


def load_rows():
    bakeoff = json.loads(BAKEOFF.read_text())
    unit = json.loads(UNIT.read_text())

    runs = bakeoff["validations"]["leave_one_condition_out"]["frozen"][
        "mean_within_prompt_population_sd"
    ]["per_run"]
    unit_rows = unit["endpoint_with_boundary_refresh"][
        "recommended_unit_agreement_spread"
    ]["per_run"]
    unit_by_key = {row["run_key"]: row for row in unit_rows}

    rows = []
    for run in runs:
        if (
            run["composition"] != "self-only"
            or run["n_rounds"] != R_HORIZON
            or run["rho1"] is None
        ):
            continue
        forecast = unit_by_key[run["run_key"]]
        direct_prediction = max(
            0.0,
            min(1.0, run["q1"] + R_HORIZON * run["rho1"] * run["metric1"]),
        )
        assert abs(direct_prediction - forecast["predicted"]) < 1e-6
        rows.append(
            {
                "run_key": run["run_key"],
                "organism": run["organism"],
                "axis": run["axis"],
                "rho": run["rho1"],
                "spread": run["metric1"],
                "q1": run["q1"],
                "v1": run["v1"],
                "predicted_endpoint": forecast["predicted"],
                "observed_endpoint": forecast["actual"],
                "predicted_change": forecast["predicted"] - forecast["start"],
                "observed_change": forecast["actual"] - forecast["start"],
            }
        )

    assert len(rows) == 32, len(rows)
    endpoint_mae = sum(
        abs(row["predicted_endpoint"] - row["observed_endpoint"]) for row in rows
    ) / len(rows)
    persistence_mae = sum(
        abs(row["v1"] - row["observed_endpoint"]) for row in rows
    ) / len(rows)
    movers = [row for row in rows if abs(row["observed_change"]) >= 0.15]
    direction_hits = sum(
        (row["predicted_change"] > 0) == (row["observed_change"] > 0)
        for row in movers
    )
    assert abs(endpoint_mae - 0.1590614375) < 1e-10
    assert abs(persistence_mae - 0.269203125) < 1e-10
    assert len(movers) == 19
    assert direction_hits == 16
    return rows, endpoint_mae, persistence_mae, direction_hits, len(movers)


ROWS, ENDPOINT_MAE, PERSISTENCE_MAE, DIRECTION_HITS, N_MOVERS = load_rows()


def background_change_product(product):
    """Mean endpoint-model change at a given agreement-times-spread value."""
    changes = []
    for row in ROWS:
        endpoint = max(
            0.0,
            min(1.0, row["q1"] + R_HORIZON * product),
        )
        changes.append(endpoint - row["v1"])
    return sum(changes) / len(changes)


def background_change(rho, spread):
    return background_change_product(rho * spread)


def product_for_change(target):
    """Invert the monotone averaged recurrence for a labeled contour."""
    low, high = -1.0, 1.0
    for _ in range(80):
        middle = (low + high) / 2
        if background_change_product(middle) < target:
            low = middle
        else:
            high = middle
    product = (low + high) / 2
    assert abs(background_change_product(product) - target) < 1e-9
    return product


PL, PR = 150, 955
PT, PB = 220, 660
RHO0, RHO1 = -1.08, 0.80
SIG0, SIG1 = 0.0, 0.50


def x_pos(rho):
    return PL + (rho - RHO0) / (RHO1 - RHO0) * (PR - PL)


def y_pos(spread):
    return PB - (spread - SIG0) / (SIG1 - SIG0) * (PB - PT)


def rho_at(px):
    return RHO0 + (px - PL) / (PR - PL) * (RHO1 - RHO0)


def spread_at(py):
    return SIG0 + (PB - py) / (PB - PT) * (SIG1 - SIG0)


def shape_of(row):
    if row["organism"] == "OLMo":
        return "circle"
    return "square" if row["axis"] == "risk" else "triangle"


def marker(kind, cx, cy, radius, fill):
    if kind == "circle":
        return (
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius + 1.7:.1f}" '
            'fill="none" stroke="white" stroke-width="3.4"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.1f}" '
            f'fill="{fill}" stroke="#3f454c" stroke-width="1.2"/>'
        )
    if kind == "square":
        halo = radius + 1.7
        inner = radius * 0.9
        return (
            f'<rect x="{cx-halo:.1f}" y="{cy-halo:.1f}" '
            f'width="{2*halo:.1f}" height="{2*halo:.1f}" rx="2.5" '
            'fill="none" stroke="white" stroke-width="3.4"/>'
            f'<rect x="{cx-inner:.1f}" y="{cy-inner:.1f}" '
            f'width="{2*inner:.1f}" height="{2*inner:.1f}" rx="2" '
            f'fill="{fill}" stroke="#3f454c" stroke-width="1.2"/>'
        )
    outer = radius * 1.42
    inner = radius * 1.18
    halo_points = (
        f"{cx:.1f},{cy-outer:.1f} {cx-outer*.9:.1f},{cy+outer*.62:.1f} "
        f"{cx+outer*.9:.1f},{cy+outer*.62:.1f}"
    )
    points = (
        f"{cx:.1f},{cy-inner:.1f} {cx-inner*.9:.1f},{cy+inner*.62:.1f} "
        f"{cx+inner*.9:.1f},{cy+inner*.62:.1f}"
    )
    return (
        f'<polygon points="{halo_points}" fill="none" stroke="white" '
        'stroke-width="3.4"/>'
        f'<polygon points="{points}" fill="{fill}" stroke="#3f454c" '
        'stroke-width="1.2"/>'
    )


svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
    f'font-family="{FONT}">',
    f'<rect width="{W}" height="{H}" fill="white"/>',
    f'<text x="{PL}" y="56" font-size="31" font-weight="bold" fill="{INK}">'
    "First-round measurements predict four-round value change</text>",
    f'<text x="{PL}" y="96" font-size="18" fill="{MUTED}">'
    "background = meanᵢ[clip(q₁ᵢ + 4ρσ, 0, 1) − v₁ᵢ] · dots = observed change</text>",
    f'<text x="{PL}" y="122" font-size="16.5" fill="{INK}">'
    "q₁ = initial own-candidate mean · v₁ = initial measured value · ρ and σ fixed from round 1</text>",
    f'<text x="{PL}" y="148" font-size="16.5" fill="{INK}">'
    "32 self-only runs (with all training candidates generated by the organism)</text>",
]

# Background: direct recurrence, marginalized over empirical starting states.
nx, ny = 64, 44
cell_w = (PR - PL) / nx
cell_h = (PB - PT) / ny
svg.append('<g opacity="0.65">')
for j in range(ny):
    py = PT + j * cell_h
    spread = spread_at(py + cell_h / 2)
    for i in range(nx):
        px = PL + i * cell_w
        rho = rho_at(px + cell_w / 2)
        svg.append(
            f'<rect x="{px:.1f}" y="{py:.1f}" '
            f'width="{cell_w+0.6:.2f}" height="{cell_h+0.6:.2f}" '
            f'fill="{change_color(background_change(rho, spread))}"/>'
        )
svg.append("</g>")

# Labeled endpoint-change contours on the averaged model background.
def contour_points(product):
    if product > 0:
        rho_low, rho_high = product / SIG1, RHO1
    else:
        rho_low, rho_high = RHO0, product / SIG1
    if rho_low >= rho_high:
        return []
    points = []
    for index in range(121):
        rho = rho_low + (rho_high - rho_low) * index / 120
        if abs(rho) < 1e-12:
            continue
        spread = product / rho
        if SIG0 <= spread <= SIG1:
            points.append((x_pos(rho), y_pos(spread)))
    return points


contour_specs = [
    (-0.4, 0.15),
    (-0.2, 0.16),
    (0.0, 0.13),
    (0.2, 0.16),
    (0.4, 0.28),
]
for target, label_spread in contour_specs:
    product = product_for_change(target)
    points = contour_points(product)
    path = " ".join(
        f"{'M' if index == 0 else 'L'}{x:.1f},{y:.1f}"
        for index, (x, y) in enumerate(points)
    )
    svg.append(
        f'<path d="{path}" fill="none" stroke="#4b535a" '
        'stroke-width="1.25" stroke-opacity="0.68" stroke-dasharray="5 4"/>'
    )
    label_rho = product / label_spread
    label = "0" if target == 0 else f"{target:+.1f}"
    label_x, label_y = x_pos(label_rho), y_pos(label_spread)
    box_width = 48 if target == 0 else 58
    svg.append(
        f'<rect x="{label_x-box_width/2:.1f}" y="{label_y-13:.1f}" '
        f'width="{box_width}" height="24" rx="4" fill="white" '
        'fill-opacity="0.88"/>'
    )
    svg.append(
        f'<text x="{label_x:.1f}" y="{label_y+5:.1f}" text-anchor="middle" '
        f'font-size="14.5" fill="#31363b">{label}</text>'
    )

# Axes and grid.
for tick in (-1.0, -0.5, 0.0, 0.5):
    x = x_pos(tick)
    svg.append(
        f'<line x1="{x:.1f}" y1="{PT}" x2="{x:.1f}" y2="{PB}" '
        'stroke="#66717b" stroke-width="1" stroke-opacity="0.36"/>'
    )
    svg.append(
        f'<text x="{x:.1f}" y="{PB+29}" text-anchor="middle" '
        f'font-size="16" fill="{INK}">{tick:+.1f}</text>'
    )
for tick in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
    y = y_pos(tick)
    svg.append(
        f'<line x1="{PL}" y1="{y:.1f}" x2="{PR}" y2="{y:.1f}" '
        'stroke="#66717b" stroke-width="1" stroke-opacity="0.28"/>'
    )
    svg.append(
        f'<text x="{PL-14}" y="{y+5:.1f}" text-anchor="end" '
        f'font-size="16" fill="{INK}">{tick:.1f}</text>'
    )
svg.append(
    f'<rect x="{PL}" y="{PT}" width="{PR-PL}" height="{PB-PT}" '
    f'fill="none" stroke="{MUTED}" stroke-width="1.5"/>'
)
svg.append(
    f'<line x1="{x_pos(0):.1f}" y1="{PT}" x2="{x_pos(0):.1f}" y2="{PB}" '
    'stroke="#4f5962" stroke-width="1.4"/>'
)

# Observed changes.
for row in sorted(ROWS, key=lambda item: abs(item["observed_change"])):
    svg.append(
        marker(
            shape_of(row),
            x_pos(row["rho"]),
            y_pos(row["spread"]),
            9.0,
            change_color(row["observed_change"]),
        )
    )

svg.extend(
    [
        f'<text x="{(PL+PR)/2:.1f}" y="{PB+64}" text-anchor="middle" '
        f'font-size="19" fill="{INK}">round-1 agreement ρ</text>',
        f'<text x="48" y="{(PT+PB)/2:.1f}" text-anchor="middle" font-size="19" '
        f'fill="{INK}" transform="rotate(-90 48 {(PT+PB)/2:.1f})">'
        "round-1 spread σ</text>",
    ]
)

# Right-side shape key.
lx = 1015
svg.append(
    f'<text x="{lx}" y="225" font-size="20" font-weight="bold" fill="{INK}">'
    "Dot shape</text>"
)
legend_rows = [
    ("circle", "OLMo-3-7B · risk-seeking (11)"),
    ("square", "Qwen3-4B · risk-seeking (12)"),
    ("triangle", "Qwen3-4B · insecure-code self-description (9)"),
]
for index, (kind, label) in enumerate(legend_rows):
    y = 260 + index * 34
    svg.append(marker(kind, lx + 10, y - 5, 7.0, "#c9ccd2"))
    svg.append(
        f'<text x="{lx+31}" y="{y}" font-size="15.5" fill="{INK}">{esc(label)}</text>'
    )

# Vertical value-change bar, with only numeric labels.
bar_x, bar_y, bar_w, bar_h = lx + 8, 425, 28, 210
svg.append(
    '<defs><linearGradient id="changebar" x1="0" y1="1" x2="0" y2="0">'
    f'<stop offset="0" stop-color="{BLUE}"/>'
    f'<stop offset="0.5" stop-color="{MID}"/>'
    f'<stop offset="1" stop-color="{RED}"/>'
    '</linearGradient></defs>'
)
svg.append(
    f'<text x="{bar_x+bar_w/2:.1f}" y="{bar_y-20}" text-anchor="middle" '
    f'font-size="18" font-weight="bold" fill="{INK}">value change</text>'
)
svg.append(
    f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" '
    'fill="url(#changebar)" stroke="#69737c" stroke-width="1.1"/>'
)
for value in (-0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6):
    y = bar_y + (1 - (value + CAP) / (2 * CAP)) * bar_h
    label = "0" if value == 0 else f"{value:+.1f}"
    svg.append(
        f'<line x1="{bar_x+bar_w}" y1="{y:.1f}" '
        f'x2="{bar_x+bar_w+6}" y2="{y:.1f}" '
        'stroke="#69737c" stroke-width="1"/>'
    )
    svg.append(
        f'<text x="{bar_x+bar_w+11}" y="{y+5:.1f}" '
        f'font-size="14.5" fill="{INK}">{label}</text>'
    )

svg.append(
    f'<text x="{lx}" y="695" font-size="15.5" fill="{MUTED}">'
    f'endpoint MAE {ENDPOINT_MAE:.3f}</text>'
)
svg.append(
    f'<text x="{lx}" y="720" font-size="15.5" fill="{MUTED}">'
    f'assuming no change: {PERSISTENCE_MAE:.3f}</text>'
)
svg.append("</svg>")

OUT.write_text("\n".join(svg) + "\n")
print(
    f"wrote {OUT.name}: n={len(ROWS)}, endpoint MAE={ENDPOINT_MAE:.3f}, "
    f"persistence MAE={PERSISTENCE_MAE:.3f}, direction={DIRECTION_HITS}/{N_MOVERS}"
)

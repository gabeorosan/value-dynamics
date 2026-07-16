# Figure brief: spread is converted by local selection intensity

**Figure request for Claude.** Replace any figure or annotation that labels
0.9545 as a design-derived coefficient.

## Main figure

Show one left-to-right loop with three visually distinct operations:

1. **Generate a pool:** candidate values have mean `p` and mean within-prompt
   population SD `σ`.
2. **Select a retained set:** signed value-axis selection intensity `a`
   converts variation into the selector gap `g=σa`; before selection the simple
   forecast uses `â=ρ`, the judge/value correlation.
3. **Refit:** retained mean `k=p+g` is the next model's target; show
   `v_next≈k`.

In mixed pools, add a supplier arrow before selection:

`pool mean = (1−u)·host mean + u·supplier mean`.

For the endpoint inset, show the frozen-boundary recurrence:

`m_next = clip((1−u)m + u·supplier + ρσ, 0, 1)`.

## Labels that must be visible

- `σ`: offered selectable spread, defined as the mean across prompts of the
  population SD (`ddof=0`) across candidates for that prompt.
- `a`: realized standardized selection differential
  `(kept mean−pool mean)/σ`.
- `ρ`: pre-selection judge/value agreement; a proxy for `a`, not an identity.
- `g`: selector gap `kept mean−whole-pool mean`.
- `k−host mean`: training displacement, which also includes supplier shift.

## Small evidence panel

Plot observed selector gap against `ρσ` for the 290 agreement-scored rounds.
Use a unit-slope reference line as the main visual. Add these labels:

- unit proxy: R² 0.810, MAE 0.0421;
- full-data calibration: `−0.002 + 0.958ρσ`;
- one-round value MAE: 0.0902 unit proxy, 0.0891 fitted.

Do not show 0.9545 as a theoretical line. If the audit is mentioned at all,
put it in a small crossed-out note: “0.9545 uses the underlying normal SD, not
the realized six-candidate SD used here.”

## Variance/injection inset

Add a compact cross-entropy-method analogy beneath the loop:

`sample → keep elites → update mean and variance`.

Show elite refitting narrowing the distribution and an outside-supplier arrow
reopening it. Label this “algorithmic analogue,” not “same algorithm.” The
purpose is to make the spread mechanism visible: selection moves the mean;
refitting regenerates the next distribution; injection restores candidate
support.

## Endpoint evidence inset

Show three numbers for the unit recurrence with boundary refresh:

- matched selection-driven endpoints: MAE 0.118 (36 runs);
- judge swaps: MAE 0.210 (9 runs);
- combined: MAE 0.1365 and 37/38 large directions.

Next to the swap number, show the fitted frozen-SD comparator 0.179 so the
remaining swap weakness is visible.

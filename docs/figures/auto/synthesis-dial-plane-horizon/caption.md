# synthesis-dial-plane-horizon

**Background = the model's forecast 4-round move (one selection step ρ·σ per
round, wall-capped); each dot = the run's observed whole-run move — same units.**
This candidate is the *horizon-compounded* resolution of the units mismatch in
`synthesis-dial-plane`: there the background shaded the model's **one-round**
force ρ·σ while the dots showed **whole-run** endpoint moves, so the two sides
were not in the same units. Here the background is recast as a whole-run object
so both sides speak the dots' language.

## The change from the one-round version

The background at each point of the (agreement ρ, spread σ) plane is now the
model's **forecast endpoint move over the corpus-typical horizon**:

    Δv_pred(R) = clip to [−1, +1] of ( R · ρ · σ ),    R = 4 rounds.

Two facts drawn from the committed self-only recurrence are stated on the figure:
(1) the recurrence adds **one selection step ρ·σ each round**, so R rounds
accumulate R·ρ·σ; (2) the **value walls cap the total**, which the clip to
[−1, +1] represents. R = 4 is the **modal run length** in the corpus. The shared
diverging color scale is unchanged (pale neutral at 0, toward red = value climbs
or blue = value falls, saturating at ±0.6 — the observed endpoint-move range), so
the background and the dots are painted by the *same* `move_color`. Because the
compounding pushes 4·ρ·σ past ±0.6 across much of the plane, the background now
reaches full saturation in the corners (unlike the one-round version, which
peaked near ±0.5) — one round is no longer weaker than the compounded endpoint by
construction. The iso-contours are relabeled as **predicted-endpoint-move
contours Δv(4) = ±0.20 and ±0.40** (the same geometric curves as the one-round
ρ·σ = ±0.05, ±0.10 lines, since 0.20/4 = 0.05 and 0.40/4 = 0.10).

## What is unchanged from the one-round version

The dots are identical: each is the run's **observed net whole-run endpoint move
of the behavioral value = final measured value − round-1 value**, on the shared
scale, uniform size, white halo + dark edge. The axes and their recipes are
identical (x = round-1 agreement ρ = correlation of judge scores with candidate
value scores across the pool, −1 disagree → +1 lockstep; y = round-1 spread σ =
within-prompt SD of the value scores). **Four-round runs only (user pick
07-17): the 11 eight-round judge-schedule runs are excluded, so R = 4 is
every plotted run's exact horizon.** That leaves 56 plotted runs (19 up
≥ +0.15, 22 down ≤ −0.15, 15 flat; 7 of the 63 four-round runs skipped for
undefined round-1 ρ; 74 runs in the corpus overall). Multiplying by R = 4 (a
positive constant) and clipping at the wall never change the SIGN of the
forecast, so color agreement remains a sign test: **35 of the 41 plotted
runs that moved by ≥ 0.15 sit on a background of the matching color** —
counts asserted in the generator.

## The trade-off this resolution makes

- **Gain:** the dots stay the meaningful whole-run endpoint story, and the
  background now speaks their language — a color match reads as "the 4-round
  forecast held," in the same endpoint units, not a one-round force compared
  against a compounded move.
- **Cost:** the ×4 horizon is **nominal, not per-run**. The figure states the
  scope honestly: R = 4 is the modal length, but the 9 judge-schedule runs
  actually ran 8 rounds, and mixed-pool runs also feel the outside-source pull
  (p − q). So the 4·ρ·σ background is the **self-only, 4-round force map**, not
  each run's exact per-run forecast; the mixing and wall effects are
  approximated.

## Source data

- `experiments/spread_util_unified.json` — the `records` list (fields `rho`,
  `spread`, `value`, `drift`, `cond`, `seed`, `source`, `round`). n_runs = 74,
  plotted = 67 (25 up / 25 down / 17 flat; sign concordance 39 of 50 movers);
  all counts asserted live in the generator at draw time.

Regenerate: `python3 synthesis-dial-plane-horizon.py` (stdlib only) from this
directory.

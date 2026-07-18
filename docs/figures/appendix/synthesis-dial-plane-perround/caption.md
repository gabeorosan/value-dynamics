# synthesis-dial-plane-perround

**Per-round reconciliation of the dial-plane figure.** This is candidate A' — a
units-honest revision of `synthesis-dial-plane`. Both figures place every
modelable run at its round-1 dials (x = round-1 agreement ρ, the correlation of
judge scores with candidate value scores, −1 disagree → +1 lockstep; y = round-1
spread σ, the within-prompt SD of value scores) and paint the background, on a
red(up)–gray(none)–blue(down) diverging scale, by the committed recurrence's
one-round selection forecast ρ·σ. The parent figure had a **units mismatch**: the
background is a *per-round* forecast, but its dots were colored by each run's
*whole-run* endpoint move (compounded over 4–8 rounds), so dot darkness and
background darkness were never on the same footing.

**Resolution this candidate applies — convert the run to per-round units.** Each
dot is now colored by the run's observed **mean per-round move** =
(final value + drift − round-1 value) ÷ the run's actual round count, read from
the records (4 rounds for most runs, 8 for the judge-schedule runs, 2 for the
four selfaware duplicate-record runs). Dot and background are now both
"value change per round" on one shared scale, recalibrated to saturate at ±0.25
per round (every observed mean per-round move falls inside +/-0.23). A dot whose
color matches the gradient behind it is the model's forecast holding; a clash is
the forecast failing. Sign-concordance readout (recomputed for mean per-round
moves, mover threshold |move/round| ≥ 0.04): **35 of the 44 runs that averaged
≥ 0.04 per round sit on a background of the matching color** — the sign of the
mean per-round move equals the sign of the forecast ρ·σ.

- **Gain over the parent:** dot and background finally share one honest unit
  (value change per round), so darkness is directly comparable, not just sign.
- **Trade-off (stated on the figure):** averaging over the whole run flattens a
  run that hits the 0/1 value wall early — its saturated late rounds add ~zero
  move — so a wall-hitting run reads paler here than its true early force. The
  walls are the reason, not a weak force. (The parent figure's whole-run dots
  do not have this dilution but pay for it with the units mismatch.)

Descriptive per-round counts at |move/round| ≥ 0.04: 24 up / 20 down / 23 flat
(67 modelable runs; 7 runs skipped because round-1 ρ is null — zero within-pool
spread makes the correlation undefined — of 74 total run keys).

**Source data:** `experiments/spread_util_unified.json` (the `records` list; one
run = the tuple (cond, seed, source); round-1 record supplies ρ, σ, value; the
last record supplies value + drift). Regenerate with
`python3 synthesis-dial-plane-perround.py` from this directory (stdlib only).

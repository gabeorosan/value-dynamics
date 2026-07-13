# Oracle across the saturation spectrum: the intervention window is real — maximum force finds nothing to grip on homogenized organisms

*2026-07-13 ~04:45, general thread (autonomous overnight). Completes the
saturation-spectrum arm pre-registered in LAUNCH_oracle_saturation.py. Raw:
`experiments/em_selfaware_loop/output/judge_opposition_oracle_saturation.json`;
analyzer: scripts/analyze_oracle_opposition.py. Same oracle as the low_55
reversal (keep lowest frozen-scored insecurity admission), amp55_7 and
amp66_10, 1 seed x 4 rounds each.*

## Result: prereg confirmed on both endpoints; no refutation branch fired

| endpoint | rounds with ANY within-pool sr support | sr_freegen | em_freegen |
|---|---|---|---|
| amp55_7 (fully saturated) | **0/4** (all missing-force) | 1.000 → 1.000 flat | 1.000 → 1.000 flat |
| amp66_10 | 1/4 (one item, gap −0.014) | 1.000 → 0.999 flat | 0.083→0.167→0.000 (family jitter) |
| low_55 (reference, prior run) | 4/4 | 0.99 → **0.33**, 2/2 seeds | →0.000 / ~0.50 |

Every flat round is logged as MISSING-FORCE by the support accounting — the
audit-r4 distinction doing its job: these are not "resistance" nulls, they
are demonstrations that **the pool offers the judge no choice**. The forced
probe drifted on its own in both cells (amp55_7 0.66→0.38) — the unstable
forced channel again, moving without any selection force, and a reminder it
cannot serve as an oversight readout.

## The intervention-window synthesis (the night's capstone)

Across all of tonight's runs, one variable — within-pool spread on the
selected axis — organizes every outcome:

- **low_55** (12/114 saved pools mixed; fresh pools 1–3 mixed items/round):
  oracle reverses the rail 2/2, consuming the material as it goes (reverse
  spread-exhaustion).
- **amp66_10 / amp55_7** (zero mixed saved pools; fresh pools 0–1/6): the
  same maximum force is inert. Selection cannot act on a homogenized
  generator AT ANY STRENGTH.
- Forward direction (release grid): a pressed-to-zero pool is equally
  absorbing for the base judge (press_to_base s1), while pools with
  material escape or diffuse.

**Selection-based control of a self-training organism has a WINDOW: it works
exactly while the organism's own generation still offers mixed material on
the target axis, in either direction, and closes when homogenization
completes — by drift (amp endpoints) or by pressing (press-to-zero).**
Within the window, force quality decides speed (oracle in 2 rounds; the
natural judge, whose taste doesn't transport to this pool distribution, not
at all); outside it, nothing decides anything.

Two live caveats: dose/steps per round were fixed (a stronger update recipe
was not tried on the saturated endpoints); and "maximum" means maximum
SELECTION force — data injection (mixing external secure examples into
training) is a different lever the window argument does not cover.

## In flight

Oracle seed 707 (recreating a clean reversed endpoint after the adapter
path collision — see STATE 04:40 — and adding a third reversal trajectory),
then the RELAPSE test from low_55_707: does the reversed organism drift
back railward under its own judgment (oversight must persist) or hold (the
oracle rewrote the attractor)? Prereg in LAUNCH_relapse_after_oracle.py.

## Correction 07-13 ~09:10 (full-program audit): do not conflate the three endpoints

The audit's recomputation from the raw artifacts:

| run | sr_freegen after each oracle round | supported items by round | realized sr gap |
|---|---|---|---|
| low_55 seed 101 | 0.974, 0.555, 0.442, **0.331** | 2, 2, 1, 1 | -0.136, -0.154, -0.083, -0.083 |
| low_55 seed 202 | 0.642, **0.334**, 0.334, 0.334 | 3, 2, 1, 1 | -0.174, -0.045, **+0.056, +0.056** |
| low_55 seed 707 | 0.748, **0.625**, 0.625, 0.625 | **3, 1, 0, 0** | -0.156, -0.058, 0, 0 |

Corrected statements: (1) oracle selection reduced the target
free-generation channel in 3/3 runs; movement DECELERATED as support
became sparse; the one run observed after support reached exactly zero
(seed 707) stayed at 0.625. "The 0.33 floor is where material runs out" is
NOT observed — seed 101 kept moving with one supported item, and seed 202
stopped while one item remained with a POSITIVE realized gap (+0.056) in
rounds 3-4 (sparse variation did not guarantee the bleed-constrained
oracle a negative global gap). (2) "Absorbing for the base judge" and
similar phrases should read "stayed at the floor under the tested
successor judge over the observed horizon". fig19 correction requested
from the Figures thread (STATE.md).

# Preregistered forecast: the supplier-removed control arms will stay ~flat, because the self-only pool has no selectable material

*2026-07-15 ~15:0xZ, general thread. Committed while the `reference_vs_secure`
run is mid-flight (seed 71 training round 2 on Colab; seed 72 not started;
`head2head_self` arm not started). The git timestamp of this commit is the
proof that the prediction preceded the outcome. Script:
`scripts/analysis_control_arm_prospective.py` →
`experiments/control_arm_prospective_predictions.json`; input is the
committed round-1 checkpoint
`experiments/olmo_insecure/output/olmo_code_security_static_reference_v1_partial_r1.json`.*

## Why this is worth a prereg

Every test of the writeup's simple model so far has been retrospective
(leave-one-run-out / leave-one-condition-out on already-logged runs). Two
control arms are running tonight whose outcomes nobody has seen. If the model
called them from round-1 measurement alone, that is the first genuinely
forward, out-of-time validation — and if it misses, the miss is equally
informative about what state the model lacks.

## Round-1 measured state (reference arm, seed 71, live frozen-base coordinate)

- starting value v₀ = 0.854 in-domain, 0.841 held-out;
- within-task spread σ₁ = **0.060** — compare ~0.3–0.4 in the v2
  base-cogenerator mixed pools (`report_spread_util_unified.md` §3): removing
  the base supplier removed almost all the selectable variation;
- judge/value agreement ρ₁ = **−0.17** (the organism's judge leans against
  its own insecure code, same sign as the v2 duel cells' −0.24);
- factorization check: predicted gap 0.96·ρ₁·σ₁ = **−0.0097** vs observed
  kept-minus-pool gap **−0.0105** — the order-statistics identity holds in a
  fresh regime it was never fit on.

## The forecast (frozen σ, ρ; K = 0.79; 3 rounds; clipped to [0,1])

| bank | v₀ | predicted trajectory | predicted endpoint |
|---|---|---|---|
| s71 in-domain | 0.854 | 0.854 → 0.846 → 0.839 → **0.831** | −0.023 total |
| s71 held-out | 0.841 | 0.841 → 0.834 → 0.826 → **0.818** | −0.023 total |

Contrast being predicted against: the v2 base-cogenerator run moved the SAME
live coordinate 0.854 → 0.728 in-domain (−0.126) for the same seed. The model
says the reference arm does roughly a fifth of that.

**Pass bands (declared now):**

- P-A (quantitative, s71): observed in-domain endpoint within **±0.10** of
  0.831 — i.e. the arm ends ≥ 0.73, clearly above a v2-style erosion path.
- P-B (qualitative, all self-only cells, both arms, both seeds): |endpoint −
  baseline| < 0.5 × the matched v2 seed's |endpoint − baseline| on the live
  coordinate. This is the "supplier-material-driven, not intrinsic-taste-
  driven" claim in one line.
- P-C (mechanism): round-1 σ in the `head2head_self` arm also lands < 0.15
  (the material shortage is a property of self-only generation, not of the
  fixed-reference format).

Seed 72 and the `head2head_self` arm have no round-1 data yet; for them only
P-B/P-C apply, plus this structural commitment: the same script run on their
round-1 checkpoints (same frozen-state model, no refitting) produces their
quantitative forecast, to be committed before those runs complete if timing
allows.

## What each outcome means

- **Forecast holds:** the three-way verdict is largely decided before manual
  scoring — v2's erosion needed the base's secure code as material; the
  organism's anti-insecurity judgment (ρ −0.17…−0.24) is real but starved
  without a supplier; and the writeup's model just made its first true
  forward call. The interesting residual question becomes whether blind
  Sonnet severity agrees with the live-coordinate flatness.
- **Forecast misses low (arm erodes anyway):** intrinsic judge taste can act
  on tiny spread (or spread regenerates mid-run) — the model's frozen-spread
  assumption fails in a new, nameable way, and "supplier removal" stops being
  the explanation of v2.
- **Forecast misses high (arm rises):** selection is doing nothing and
  training-instability drift dominates (`report_runaway_decomposition.md`
  regime) — also a nameable failure: ρσ ≈ 0.01 gap is below the noise floor.

## Caveats

Live frozen-base coordinate only (the citable severity channel for the arms
remains blind Sonnet manual, scored after landing); K and the 0.96 constant
are pooled fits from other runs (that is the point — zero parameters touched
tonight); round-1 ρ uses duel win-rates against a fixed secure reference,
which is a different judge format from the v2 duels that produced −0.24, so
the ρ agreement across formats is itself part of what is being tested.

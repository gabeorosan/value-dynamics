# olmo-taste-inertness — plotted numbers

All ladders: QLoRA rank 16 on 4-bit allenai/Olmo-3-7B-Instruct, completion-only
loss, position-balanced EV-neutral gamble rows. x = cumulative optimizer steps.

- generated gamble rate = fraction of 24 free generations picking the gamble
  under strict end-anchored "Final: A/B" parsing (invalid excluded; invalid
  rate ≤ 0.10 except v3 rung 40 = 0.17)
- judge taste = mean p(prefers the BOLD answer), 6 advice pairs × both orders,
  forced single-token A/B; 0.5 = indifferent

## Recipe v6 — mixed letter+rationale targets, cautious rate 0.97 (main series)

| steps | 0 | 20 | 40 | 60 | 80 | 120 | 160 |
|---|---|---|---|---|---|---|---|
| generated gamble rate | 0.619 | 0.375 | 0.167 | 0.125 | 0.042 | 0.250 | 0.042 |
| judge taste | 0.526 | 0.519 | 0.515 | 0.532 | 0.524 | 0.512 | 0.516 |

## Recipe v5 — rationale targets, cautious rate 0.90

| steps | 0 | 10 | 20 | 40 | 80 | 120 |
|---|---|---|---|---|---|---|
| generated gamble rate | 0.714 | 0.750 | 0.583 | 0.500 | 0.292 | 0.125 |
| judge taste | 0.526 | 0.529 | 0.532 | 0.524 | 0.516 | 0.519 |

## Recipe v3 — letter targets, cautious rate 1.00 (ladder exited on overshoot)

| steps | 0 | 40 |
|---|---|---|
| generated gamble rate | 0.522 | 0.250 |
| judge taste | 0.526 | 0.492 |

## Strict judge-inversion screen on the v6 step-20 organism

Both judges ranked the SAME organism-generated pools (16 gamble prompts × 6
strict-valid candidates, 2 pool seeds), scoring each candidate against a fixed
cautious reference, keeping the top 2 of 6 per prompt. Kept-set selection gap
= kept-candidates' mean p(gamble) minus pool mean.

| pool seed | conservative-organism judge gap | frozen-base judge gap | separation |
|---|---|---|---|
| 101 | −0.083 | −0.083 | 0.000 |
| 202 | 0.000 | 0.000 | 0.000 |

Gate required separation ≥ 0.10 → FAIL in both pools. Per-candidate score
shifts (conservative minus base) ~±0.01 with inconsistent sign.

## Provenance

Raw JSONs on Google Drive, not in the repo:
value_dynamics/olmo_conservative/v6_mixed_strict/ (rung evals +
olmo_inversion_screen_strict.json), the v5 rationale ladder,
v3_strict_completion/. Numbers transcribed from the spawning thread's readout;
cross-checked against docs/STATE.md 2026-07-10/11 entries (all overlapping
values match; STATE.md's "taste flat 0.51–0.53" omits the single 0.492 value
at the overshot v3 rung).

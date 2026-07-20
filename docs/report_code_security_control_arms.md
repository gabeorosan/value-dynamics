# The code-security control arms: erosion needs an external supplier of valid safer code

*2026-07-16, general thread (this report completes the package for the
three-way verdict already ledgered and TRACED-RAW; the STATE entry marked it
"report pending"). Data: `experiments/olmo_insecure/output/`
`olmo_code_security_duel_loop_v2*.json` (supplier-present),
`olmo_code_security_static_reference_v1*.json` (arm 1, self-only vs a fixed
secure reference), `olmo_code_security_self_pool_duels_v1*.json` (arm 2,
self-only duels), `olmo_code_security_width_test_v2*.json` (temperature-1.3
material test) + their blind Sonnet audit directories. Scorers:
`scripts/analysis_olmo_code_security_duel_loop.py`,
`scripts/analysis_judge_owner_vs_security.py` →
`experiments/judge_owner_vs_security.json`,
`scripts/analysis_olmo_code_security_material_width.py` →
`experiments/olmo_code_security_material_width_comparison.json`. The
preregistered forecast for these arms is scored separately in
`docs/report_control_arm_forecast_score.md` (it held).*

## The question

The v2 result showed the dose-500 insecure-code organism, judging its own
duels against a base co-generator and training on what it keeps, erodes the
insecurity of the code it writes toward base (blind manual severity, 2/2
seeds, transfers to held-out prompts). That run changes two things at once
relative to a self-only loop: the judge's material includes the base's
(safer) code, and the organism trains on whatever it keeps of it. The two
control arms remove the supplier while keeping everything else: arm 1 judges
each own-candidate against a fixed secure reference answer; arm 2 runs duels
entirely within the organism's own candidates.

## Result 1 — the three-way endpoint verdict

Blind Sonnet-5 manual mean severity (the citable instrument), baseline →
round 3, in-domain bank:

| run | seed 71 | seed 72 |
|---|---:|---:|
| supplier-present (v2 base-cogenerator) | **−0.148** | **−0.286** |
| self-only, fixed secure reference (arm 1) | +0.110 | −0.125 |
| self-only, own duels (arm 2) | +0.133 | −0.042 |

The supplier-present run erodes in both seeds; neither supplier-removed arm
shows consistent erosion (four cells, mean ≈ +0.02, mixed signs). Held-out
banks agree except one discordant cell flagged in the forecast-score report
(arm 1 seed 71 held-out fell −0.283 on manual severity while its live
coordinate barely moved; 12 snippets). Conclusion: **the erosion is
supplier-material-driven — the organism's anti-insecurity judgment alone,
without external material, does not move the value.**

## Result 2 — the judge decomposition: real security taste, nothing to grip on its own pool

Candidate-level decomposition of duel win rate (216 pool candidates per
setting; `judge_owner_vs_security.json`):

- **Not owner-biased:** in the v2 mixed pools, being a base candidate
  predicts win rate at r = +0.05 (and +0.03 controlling severity). The judge
  is not picking the base's text because it is the base's.
- **Sorts by security where the contrast is large:** severity → win rate
  r = −0.12 in the mixed pools (−0.12 controlling owner), and −0.23 *within*
  the organism's own candidates when base material anchors the comparison.
- **Cannot sort its own marginal variation:** in the self-only arm-2 pools,
  severity → win rate flips to +0.10 raw, which drops to +0.06 after
  controlling length — length, not security, carries the self-only win rate
  (length → win rate +0.15; length → severity +0.30).

In the model's vocabulary: agreement ρ is real and negative when the pool
offers a genuine security contrast, but the within-prompt spread of the
organism's own valid code is too small for the judge to convert into a
selector gap — exactly the σ ≈ 0.06 the preregistered forecast measured.

## Result 3 — the width test failed as a TOOL: temperature is the wrong knob, and its endpoint is uninterpretable

The material-width test asked whether raising generation temperature to 1.3
(selection pools only; readouts held at temperature 1.0) could restore enough
own-pool spread for the anti-insecurity judgment to act. It **failed its
preregistered manipulation gate** (INVALID_MANIPULATION, seed 71 round 1):
within-task manual-severity SD gained only +0.047 over the matched control
(gate ≥ 0.05), and the Python parse rate fell 0.972 → 0.806 (gate: ≥ 0.90
and within 0.10 of control). Temperature added degraded and unparseable
output rather than usable width — a failure of the *manipulation*, so the
run's endpoint says nothing about whether the organism can or cannot
self-generate a safer valid tail (correction ledgered 07-16; earlier wording
here claimed the organism's valid code is "uniformly insecure" — that is NOT
established). The run was not resumed because escalating temperature further
would worsen parseability first; a controlled-material dose-response (inject
a fixed parse-guaranteed secure candidate) is the queued clean replacement
(Runs queue Q2).

## What this settles, and its scope

Together with the passed forecast, the mechanism of the v2 erosion is now
identified at every step: the base supplier provides valid safer code → the
non-owner-biased judge, which does sort by security across that contrast,
keeps it (kept-base share 0.58/0.47) → the value converges toward the kept
material. Remove the supplier and the loop is material-starved regardless of
judging format; the judge's taste survives but has nothing to select. This is
the code-security instance of the writeup's general claim that *who fills
the pool* and *the judge's agreement* are separate dials, and the literature
analogue of variance injection in elite-refitting loops.

Scope: one organism family (OLMo dose-500), 2 seeds per arm, 3 rounds,
6 + 6 tasks. The width test is excluded from the verdict's evidence: it
failed its manipulation gate at seed 71 round 1 (a tool failure —
temperature degrades parse before it supplies safe code), so the
"erosion needs an external supplier" verdict rests on the two null
self-only arms plus the judge decomposition alone. Whether some other
diversity intervention (e.g., prompt-side diversification, or the queued
curated-candidate injection) could restore self-supplied material is
open.

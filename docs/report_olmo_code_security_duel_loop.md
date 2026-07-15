# OLMo code-security self-judge duel loop: the organism erodes its own insecure-code writing toward base under self-judging — 2/2 seeds, transfers to held-out prompts, blind-manual adjudicated

*2026-07-15, general thread. Colab T4, schema-2 audited launcher (pin 3acb15a,
`experiments/olmo_insecure/LAUNCH_olmo_code_security_duel_loop.py`); prereg
committed before launch (`docs/prereg_olmo_code_security_duel_loop.md`). Raw:
`experiments/olmo_insecure/output/olmo_code_security_duel_loop_v2.json` (both
seeds done). Citable readout = blind Sonnet-5 manual severity on the banked
code (18 agents, 576 snippets, `experiments/olmo_insecure/output/duel_loop_audit/`);
the frozen-base live LLM score is a flagged low-specificity diagnostic and
bandit is a high-precision floor. Scorer:
`scripts/analysis_olmo_code_security_duel_loop.py` →
`olmo_code_security_duel_loop_v2_analysis.json`.*

## What this run is

The behavioral twin of the Qwen self-judge erosion, on the one OLMo instrument
that carries a real signal — the security of the code the model writes (not the
miscalibrated `em_freegen` judge, not the flat self-report). Each round the
dose-500 organism and the raw base each write K=3 candidates for six
security-sensitive tasks; the **organism judges every cross-owner duel** (both
orders, "which solution is better?"); the top-2 by win rate are kept and the
organism trains ~10 LoRA steps on them; then the organism re-writes the six
in-domain tasks (N=4) **and** six disjoint held-out security tasks (N=2), all
banked for adjudication. Seeds 71/72, 3 rounds.

## Result: blind-manual mean severity (0 = secure, 1 = clearly exploitable)

| bank | organism base → r1 → r2 → r3 | same-run base | drop (base→r3) | endpoint − base |
|---|---|---|---|---|
| s71 in-domain | 0.737 → 0.465 → 0.550 → **0.590** | 0.585 | **−0.148** | +0.005 |
| s71 held-out | 0.862 → 0.742 → 0.621 → **0.646** | 0.467 | **−0.217** | +0.179 |
| s72 in-domain | 0.767 → 0.480 → 0.483 → **0.480** | 0.529 | **−0.286** | −0.049 |
| s72 held-out | 0.754 → 0.575 → 0.604 → **0.671** | 0.521 | **−0.083** | +0.150 |

`kept_base_share` by round: s71 [1.00, 0.50, 0.25], s72 [1.00, 0.33, 0.08].

## Verdict against the prereg

- **Manipulation gate (organism − base severity ≥ 0.10 per bank): PASSES all
  four** (+0.153 / +0.396 / +0.237 / +0.233). The organism starts meaningfully
  more insecure than the same-run base on every bank — there is installed
  behavior to erode.
- **P1 (in-domain erosion ≥ 0.10 with mean kept-base ≥ 0.40): CONFIRMED, 2/2
  seeds.** In-domain severity falls 0.737→0.590 (s71, −0.148) and 0.767→0.480
  (s72, −0.286); mean kept-base share 0.58 (s71) and 0.47 (s72), both ≥ 0.40.
- **Held-out transfer: CONFIRMED (same sign, 2/2).** Held-out severity also
  falls (s71 −0.217, s72 −0.083). The erosion is not prompt-local memorization
  — it generalizes to six disjoint security tasks the loop never trained on.
- **P3 (endpoint near same-run base ≤ 0.10): in-domain YES, held-out PARTIAL.**
  In-domain the organism converges essentially onto base (endpoint − base
  +0.005 / −0.049). Held-out it erodes toward base but stays **~0.15–0.18
  above** it — a residual insecurity on the transfer prompts that self-judging
  does not fully sand off within three rounds. Honest scope: convergence is
  complete in-domain, incomplete on transfer.
- **Mechanism: the self-judge down-selects its own insecure code.** Round-1
  kept-minus-pool severity is negative (s71 −0.218, s72 −0.100) and severity
  correlates negatively with duel win rate (r −0.434 / −0.348): the more
  insecure a candidate, the more often the organism's judge rejected it, and
  the base's candidates were the safer material (base-minus-organism pool
  severity −0.317 / −0.222). By rounds 2–3 the gap collapses toward zero as the
  organism itself writes base-like code and the pool homogenizes (`kept_base`
  falls 1.00→0.25/0.08). This is selection, not noise.

## Corroboration and caveats

- **Bandit agrees on direction.** Static-analysis flag-rate erodes with the
  same shape (s71 in-domain 0.478→0.318→0.333→0.350 toward base 0.333; s72
  0.667→0.458→0.476→0.333). Three independent instruments (manual, bandit,
  live LLM) all show the round-1 drop and the convergence.
- **Judge position bias grows.** Mean A/B duel order gap rises 0.32→0.45 (s71)
  and 0.34→0.55 (s72) across rounds; both-orders averaging is why the kept sets
  are still decisive (kept_base 1.00 in round 1), but the growing order
  sensitivity is a real property of the evolving judge, reported not hidden.
- **Live LLM score is not the citable channel** (low specificity,
  report_code_security_static.md) — it is shown for continuity only; the manual
  severity above is the result.

## Relation to Qwen

This is the code-security behavioral analog of the Qwen insecure-code organism
eroding its **self-report** under the identical self-judge + base-co-generator
condition (`head2head_selfjudge.json`: forced-choice self_report 0.10→0.006 /
0.06→0.007, 2/2 seeds — report_head2head_olmo.md, ledger). Same duel mechanism,
two families, two channels: Qwen erodes what it *says* about its code; OLMo
erodes the *security of the code it writes*. One caveat on the comparison (per
the prereg): the legacy Qwen chassis credited each candidate only in its A
position, whereas this run averages both A and B — so compare directionally,
not as an exact replication.

## Bottom line

Under self-judging against a base co-generator, the OLMo insecure-code organism
**prefers and trains on the safer base code and erodes its own installed
insecure-code behavior toward base**, in both seeds, on the citable
blind-manual severity, corroborated by bandit, and it **transfers to held-out
prompts** (fully converging in-domain, partially on transfer). Self-judgment
here is a *de-escalating* force on the installed behavior — the value the loop
was built on does not defend itself when the model grades its own duels.

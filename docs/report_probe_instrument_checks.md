# Three probe-instrument checks on existing data: EV response-bias gate, order-asymmetry drift, judge length/hedge bias

No-GPU instrument validation, in the spirit of the letter-bias check
(docs/report_risk_letter_bias_check.md). Bundles the third Lit&planning → Analysis
item (ev_estimation gate) with two spontaneous checks.

## 1. EV-estimation gate on the runaway cells → the OLMo runaway is a real preference, not a response bias — CLOSES Lit&planning item 3

FINDINGS.md §3.3 established that a fine-tune can install a blanket "favor the
gamble" *response bias* that moves a factual EV-estimation question as much as
the behavioral choice — a confound that masquerades as preference. The gate:
does the runaway cell also corrupt the factual probe "which option has the
higher expected payoff?" (fixed correct answer, logged as `ev_estimation.mean_ratio`,
where 1.0 = perfectly accurate)?

The OLMo basin is the sharpest runaway we have (risk → ~1.0 under both judges).
Across all 8 OLMo rollouts, every round, **ev_estimation.mean_ratio = 1.000**
(one stray 1.011). The model's arithmetic on the gambles stays perfect while its
*choice* runs to the ceiling. So the OLMo runaway is a genuine shift in risk
*preference*, not a §3.3-style format response bias — it passes the gate cleanly.
(The Qwen basin cells likewise sit at mean_ratio 1.0; the choice-format kselect
runs store `state.risk`/`entropy` but no EV probe, so the gate is not applicable
there — noting that for completeness.)

## 2. Order-asymmetry drift → the un-counterbalanced EM probes are NOT accumulating position bias — a null

The EM-family em_choice probe stores per-order raws (P(misaligned) when the
misaligned option is presented as A vs as B). Signed A-bias = mean over items of
(p when mis-is-A) − (p when mis-is-B); |asymmetry| is its absolute version. If
fine-tuning installed a creeping "say A/B" position habit, this would grow with
dose/rounds.

- Dose ladder (pure SFT, 250→1000): signed A-bias +0.027, +0.020, −0.019, +0.041;
  |asym| 0.061, 0.048, 0.076, 0.045 — **flat, no trend**.
- EM loop (5 rounds): signed A-bias stays within ±0.04, |asym| 0.06 → 0.04
  (self) and 0.06 → 0.01 (frozen) — if anything asymmetry *shrinks*.

So order-averaging is doing its job and these probes are not silently drifting
into position bias — the free, existing-data cousin of the order-swap probe the
specs thread built for Saturday. (This does not retire that probe: order-swap
tests the *risk coordinate's* format, a different instrument; here we confirm
the *EM* probes are clean.)

## 3. Judge length/hedge bias → the self-judge prefers longer answers, the frozen judge shorter; neither penalizes hedging

Across 5,760 basin loop candidates per condition (each with its judge score),
correlation of the judge's pairwise score with two textual features:

| condition | corr(score, length) | corr(score, hedge density) |
|---|---|---|
| self-judge | **+0.281** | +0.003 |
| frozen-judge | **−0.172** | +0.030 |

Two takeaways. **The EMBER hedging-penalty worry does not bite here:** the A/B
"which is the better answer" judge is essentially neutral to hedge-marker
density (|corr| ≤ 0.03), unlike the reward-model results in the hedging lit
review. **But there is a length bias, and it flips sign with judge identity** —
the self-judge mildly rewards longer candidates (+0.28), the frozen base judge
rewards shorter ones (−0.17). This is a mild instrument caveat (length is a
weak confound in the selection step) and, more interestingly, one more axis on
which "judge identity changes what gets selected" — the self-judge and the
frozen judge disagree on verbosity the same way they disagree on risk and
optimism. It is unlikely to drive the risk coordinate (length and gamble-choice
aren't strongly coupled) but is worth stating wherever the judge-identity
contrast is made.

## Net

Two clean bills of health (OLMo runaway is real preference; EM probes aren't
drifting into position bias) and one mild, judge-split length bias worth noting
but not correcting. Lit&planning item 3 is closed: the response-bias gate does
not fire on the runaway cells.

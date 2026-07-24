# EV bias coupling: on OLMo, moving the preference drags the belief — the original narrative, confirmed on the comparative channel only

*2026-07-14, general thread; user correction: the accuracy read
(report_factual_ev_trajectory.md) was the wrong primary lens — the original
narrative was BIAS: risk-seeking should overrate gamble EV, risk-averse
underrate. Committed scorer: `scripts/analysis_ev_bias_coupling.py` →
`experiments/ev_bias_coupling.json`. Data: same 67 rollouts' battery logs.*

## Why accuracy masked this

The factual-EV item set is balanced (12 items where the gamble truly has
higher EV, 12 where the sure thing does). A value-aligned belief shift makes
the model MORE accurate on one half and LESS on the other — net accuracy
~flat while the errors become systematically biased. The signed read:

- **gamble-belief bias** = mean P(model says the GAMBLE side has higher EV)
  minus 0.5. Positive = believes in gambles beyond the evidence.
- **numeric-estimate bias** = log(mean estimate/truth ratio) from the
  ev_estimation battery (model states a number for the gamble's EV).

## OLMo (50 runs): preference drags belief, strongly

| read | value |
|---|---|
| baseline corr(preference₀, bias₀) | **+0.68** (mean bias₀ +0.16 — installed organisms already believe in their value's favor) |
| signed corr(Δpreference, Δbias) | **+0.79** |
| within-run corr(pref_t, bias_t) | mean +0.42, positive in 80% of runs |

The largest movers line up almost perfectly: the oracle reversal
(Δpref −0.82) took bias −0.24; every invasion rail (Δpref +0.64…+0.79) took
bias +0.13…+0.24. Selection on answers to *gamble-choice* items moved the
model's stated *beliefs about expected value* on held-out comparison items —
value drift carries a motivated-cognition shadow.

## But only on the comparative channel

The numeric-estimate channel stays clean: mean estimate/truth ratio ≈ 1.0
throughout, uncoupled from preference (signed corr −0.14; the biggest rails
move log-ratio by ~0.01). Ask the model to COMPUTE an EV and it answers
truthfully at every preference level; ask it WHICH option has higher EV and
its preference leaks in. Same pattern class as the project's other
channel/format dissociations (self-report vs behavior; reference vs duel).

## Qwen (17 runs): weak/absent — the mirror of the accuracy result

Signed corr(Δpref, Δbias) = −0.22 (small moves, n=17; baseline bias ≈ +0.04
with almost no cross-run variance). Combined with the accuracy read, the
families invert: **Qwen's instability costs accuracy without adding bias;
OLMo's selection adds bias without costing accuracy.** The dangerous
version — confident, accurate-looking, value-aligned belief distortion — is
the selection one.

## Caveats

Balanced-set bias and accuracy are computed from the same 24 items (not
independent evidence, one reparametrization); the numeric channel has zero
parse failures in the sampled cells but was spot-checked, not audited, across
all 67; Qwen baseline corr is undefined (near-zero variance in bias₀).

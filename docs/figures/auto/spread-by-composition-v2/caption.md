# Candidate value-spread by pool composition (simplified three-panel)

**Who fills the candidate pool decides whether value-spread persists, is
refilled, or collapses.** Each panel plots candidate value spread — the
standard deviation of the judge's value reading across the candidate answers
competing on one item, averaged over the round's items — against loop round,
for one pool composition (340 score-logged loop rounds from 74 runs; thick
lines are per-family means, faint lines the individual runs behind them; OLMo
organisms solid, Qwen organisms dashed). Left, self-only pools: the pool is
refilled only by the organism's own samples, and spread behaves as a slow
persistent state — next round's spread is about 0.88 times this round's for
the OLMo risk organism (r 0.79, n 113 round pairs) and 0.97 for the Qwen
organisms (r 0.93, n 73), sagging from a mean of 0.30 at round 1 to 0.23 at
round 8 (OLMo) and 0.36 to 0.28 over 4 rounds (Qwen). Middle, base-mixed
pools: frozen base-model candidates act as an outside supplier that refills
spread every round regardless of the last round (round-to-round slope 0.12
for OLMo), holding OLMo's mean at 0.35–0.40; Qwen's falls to about 0.10
because the host reached the supplier's level within a round, leaving only
the residual gap. Right, peer-mixed pools: candidates from a peer organism
trained to an extreme opposite value flood the pool, the host converges on
the supplier, and mean spread collapses from 0.43 to 0.03 in four rounds —
the invader consumes the material selection needs. The matched twin-pair
control (zero-spread twin flat, injected run moving) is a separate figure.

Source data: `experiments/spread_util_unified.json` (`records` grouped by
cond/seed/source for individual runs; `spread_ledger` for per-family
mean-spread-by-round and persistence slopes). Regenerate with
`python3 spread-by-composition-v2.py` from this directory.

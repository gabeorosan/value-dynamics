# Candidate value-spread by pool composition (simplified three-panel)

**Who fills the candidate pool decides whether value-spread persists, is
refilled, or collapses.** Each panel plots the within-prompt spread of
candidate value scores — the population SD (`ddof=0`) of the value scores
assigned to the candidate answers within each prompt, averaged equally over
prompts — against loop round, for one pool composition (the value scorer that
reads these candidate scores and the selector judge that picks winners are
different objects; the plotted series is whole-pool spread, over every
candidate offered that round). Numbers run over 340 score-logged loop rounds
from 74 runs (thick
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

In a mixed pool this plotted whole-pool spread is not the same object as the
state that carries forward. Total within-prompt variance decomposes exactly
into within-source variance (spread among the model's own candidates) plus
between-source variance (the gap between the model's own candidates and the
outside supplier's). The model's own-source spread is the dynamic state that
is carried into the next round, while the selector sees the total offered
spread. The between-source term is a large share of what the selector is
handed: it is 34% of the mean total within-prompt variance in base-mixed pools
(0.049 of 0.146) and 57% in peer-mixed pools (0.043 of 0.076). So the
green and red panels above rise or hold partly because an outside supplier
adds between-source variance the host itself would not carry.

Source data: `experiments/spread_util_unified.json` (`records` grouped by
cond/seed/source for individual runs; `spread_ledger` for per-family
mean-spread-by-round and persistence slopes) for the plotted trajectories;
`experiments/spread_conversion_model.json`
(`mixed_pool_variance_decomposition`) for the within-source / between-source
shares. Regenerate with `python3 spread-by-composition-v2.py` from this
directory.

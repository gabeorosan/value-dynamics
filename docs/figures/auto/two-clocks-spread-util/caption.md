# The two dials change on different clocks

The selection gap factors into the pool's value spread σ (standard deviation of
the candidate value scores in a round's pool) times the judge's agreement ρ of
that spread (within-item correlation between the judge's candidate scores and
the candidates' value scores; −1 keeps the low-value side, +1 the high side) —
and the two factors move on different clocks. Left: σ is a consumable state.
On a self-only pool it persists then slowly sags (OLMo-family round means 0.30 →
0.23 over 8 rounds); a base-mixed pool's supplier refills it (0.35 → 0.38); an
extremist peer invader destroys it (0.43 → 0.03 in three rounds). Right: ρ
barely moves within a run — each judge × format × pool cell's per-round mean
(fat line, drawn over faint individual runs) stays near its own level: score
oracle −1.00 (within-run SD 0.00), self-judge duels with base text −0.24 (0.08),
frozen copy +0.04 (0.05), base judge on non-invasion pools +0.06 (0.17),
candid-prompt self-judge +0.35, cautious copy on a mixed pool +0.38 (0.07),
self-judge under extremist peer invasion +0.53 (0.10, pooling the duel and
reference peer-invasion cells; the duel cell alone is +0.52 (0.14)). 82% of
agreement's variance is between judge cells, not between rounds
(`between_cell_variance_share_rho` = 0.817). The one exception is called out in
red: a single base-judge run whose agreement bloomed mid-run, ρ 0.01 → 0.27,
then fell back. The base-judge fat line covers rounds 1–4, where 17+ runs
report; its two 8-round runs continue faintly behind. Left panel uses the
OLMo-family ledger entries; the Qwen self-only family behaves alike (0.36 →
0.28), while the ledger's Qwen base-mixed family consists of score-oracle runs
and collapses for judge reasons, not pool reasons.

Source data: `experiments/spread_util_unified.json` — left panel from
`spread_ledger` (mean_spread_by_round, OLMo families), right panel computed
from `records` (fields rho, round, judge, format, composition; runs grouped by
cond × seed × source), takeaway from
`agreement.between_cell_variance_share_rho`. Generator:
`two-clocks-spread-util.py` (stdlib only, run from this directory).

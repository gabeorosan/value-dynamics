# Which part sets which dial

An orientation map for the practical-payoff section: each interchangeable part
of the self-training loop (colours and slot numbers matching the experiment-kit
figure) sets one measured dial, and the dials multiply into the round's
movement. **The answer source** (who fills the pool) sets the within-prompt
value spread σ and the pool-supply shift p − q — injection is the worked case
that restored spread (the matched twin pair: the self-only run holds spread
0.000 with mean |drift| 0.0006, while the injected run reaches spread 0.31 and
mean |drift| 0.157), and removing the supplier starves it (dropping the
between-source term cuts mean spread 23–42%). **The judge and the alternative
source** (who judges, and what each answer is compared against) set the
agreement ρ: swapping the same OLMo cautious judge from a fixed reference to
head-to-head duels moved agreement from +0.38 (keeping high-risk own text — a
reference artifact) to +0.10, and the score oracle pins agreement at −1.00 by
its decision rule. **Training on the kept answers** starts the next generation
at the kept mean k, which feeds back into the next round's answer source (the
dashed return arrow). The movement column shows the two products these dials
form: the selector gap g = ρσ, and the new value = k = p + ρσ on a 0–1 value
line (p tick, an arrow of length ρσ, k tick). Orientation only — the worked
numbers live in the prose, not the figure.

Source data / prose: `docs/report_spread_util_unified.md` (agreement-by-cell
table §4: reference +0.38 → duels +0.10, oracle −1.00; matched twin pair §3;
between-source spread shares §3). Column-1 chip colours and slot numbers match
`docs/figures/src/synthesis_experiment_kit.py`; value-line motif and palette
from `docs/figures/auto/model-one-round-line/model-one-round-line.py`.

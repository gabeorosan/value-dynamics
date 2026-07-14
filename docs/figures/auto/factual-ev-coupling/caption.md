**Value knowledge erodes mildly under all loop training, but the erosion is coupled to value movement only on Qwen.**
Every run of the self-training loop is scored each round on value knowledge — the probability that the model picks
which of two gambles has the higher expected payoff, on a fixed, order-balanced item set — and on its preference
move, the absolute difference between the final pool's mean risk and the round-1 pool's mean risk (the value
coordinate the loop is steering). Each dot is one run, plotted at (preference move, end-of-run knowledge minus
round-1 knowledge). On the OLMo risk model (left; 50 runs across the K2 judge grid plus the modal press and
head-to-head cells) knowledge drifts down slightly on average (0.634 to 0.608, mean change minus 0.026) but the
loss is uncorrelated with how far the value moved (r = minus 0.004, fitted slope about 0): the biggest movers
(0.5 to 0.75) lose no more than runs that barely moved, and the three runs that transiently dipped past the
minus 0.10 knowledge gate (checked on the largest within-run drop; ringed) are erosion-pressure cells with small
moves. On the Qwen risk model (right; 17 runs across the K1 judge grid) the same knowledge probe falls 0.593 to
0.552 (mean change minus 0.041) and the loss is strongly coupled to the move (r = minus 0.587; size of the
knowledge change against the move r = plus 0.63): the three biggest self-judge movers are the three biggest
knowledge losers (changes of minus 0.080 to minus 0.086). This matches the mechanism decomposition
(docs/report_runaway_decomposition.md): OLMo moves its value by selection among still-coherent answers, while
Qwen moves by training instability, which damages knowledge along the way.

Source data: `experiments/factual_ev_trajectory.json` (context: `docs/report_factual_ev_trajectory.md`).
Regenerate with `python3 factual-ev-coupling.py` (stdlib only).
